import os
import uuid
import shutil
from datetime import datetime
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException

from app.models.models import (
    Case, CaseDocument, Evidence, ApplicableLaw, CaseScore,
    TimelineEvent, Recommendation, GapAnalysis,
    CaseStatus, CaseCategory, EvidenceStatus
)
from app.schemas.schemas import CaseCreate, CaseUpdate
from app.config import settings
from app.utils.knowledge_loader import (
    get_evidence_list_for_category,
    keyword_match_laws,
    get_recommended_actions_for_category,
)
from app.services.ai_service import classify_case_with_ai, generate_ai_analysis


def create_case(db: Session, data: CaseCreate) -> Case:
    case = Case(
        title=data.title,
        description=data.description,
        status=CaseStatus.DRAFT,
    )
    db.add(case)
    db.commit()
    db.refresh(case)
    return case


def get_case(db: Session, case_id: int) -> Optional[Case]:
    return db.query(Case).filter(Case.id == case_id).first()


def get_cases(db: Session, skip: int = 0, limit: int = 100, search: Optional[str] = None) -> List[Case]:
    q = db.query(Case)
    if search:
        q = q.filter(Case.title.ilike(f"%{search}%"))
    return q.order_by(Case.updated_at.desc()).offset(skip).limit(limit).all()


def update_case(db: Session, case_id: int, data: CaseUpdate) -> Optional[Case]:
    case = get_case(db, case_id)
    if not case:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(case, field, value)
    case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    return case


def delete_case(db: Session, case_id: int) -> bool:
    case = get_case(db, case_id)
    if not case:
        return False
    db.delete(case)
    db.commit()
    return True


def save_uploaded_file(case_id: int, file: UploadFile) -> Tuple[str, str]:
    """Save an uploaded file and return (stored_filename, file_path)."""
    upload_dir = os.path.join(settings.UPLOAD_DIR, str(case_id))
    os.makedirs(upload_dir, exist_ok=True)
    ext = os.path.splitext(file.filename)[1]
    stored_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, stored_name)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return stored_name, file_path


def attach_document(db: Session, case_id: int, file: UploadFile) -> CaseDocument:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    file_content = file.file.read()
    file_size = len(file_content)
    file.file.seek(0)

    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if file_size > max_bytes:
        raise HTTPException(status_code=400, detail=f"File too large. Max {settings.MAX_FILE_SIZE_MB}MB.")

    stored_name, file_path = save_uploaded_file(case_id, file)
    file_type = file.content_type or "application/octet-stream"

    doc = CaseDocument(
        case_id=case_id,
        filename=stored_name,
        original_filename=file.filename,
        file_path=file_path,
        file_type=file_type,
        file_size=file_size,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


def classify_case(db: Session, case_id: int) -> Case:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    result = classify_case_with_ai(case.title, case.description)

    category_str = result.get("category", "unknown")
    try:
        case.category = CaseCategory(category_str)
    except ValueError:
        case.category = CaseCategory.UNKNOWN

    case.subcategory = result.get("subcategory", "")
    case.classification_confidence = result.get("confidence", 0.0)
    case.ai_summary = result.get("summary", "")
    case.extracted_entities = result.get("extracted_entities", {})
    case.status = CaseStatus.IN_PROGRESS
    case.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(case)
    return case


def generate_evidence_recommendations(db: Session, case_id: int) -> List[Evidence]:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    category = case.category.value if case.category else "criminal"
    evidence_list = get_evidence_list_for_category(category)

    # Remove existing AI-generated evidence to avoid duplicates
    db.query(Evidence).filter(Evidence.case_id == case_id).delete()

    new_items = []
    for item in evidence_list:
        ev = Evidence(
            case_id=case_id,
            name=item["name"],
            description=None,
            evidence_type=item.get("type", "documentary"),
            importance=item.get("importance", "medium"),
            status=EvidenceStatus.PENDING,
            ai_reasoning=f"Recommended based on {category} case classification.",
        )
        db.add(ev)
        new_items.append(ev)

    db.commit()
    for ev in new_items:
        db.refresh(ev)
    return new_items


def identify_applicable_laws(db: Session, case_id: int) -> List[ApplicableLaw]:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    category = case.category.value if case.category else "criminal"
    combined_text = f"{case.title} {case.description}"

    matched_laws = keyword_match_laws(combined_text, category)
    if not matched_laws and case.category:
        from app.utils.knowledge_loader import get_laws_for_category
        matched_laws = get_laws_for_category(category)[:5]

    # Remove old
    db.query(ApplicableLaw).filter(ApplicableLaw.case_id == case_id).delete()

    new_laws = []
    for law in matched_laws[:8]:
        match_count = law.get("_match_count", 1)
        total_keywords = len(law.get("keywords", [1]))
        confidence = min(round(match_count / max(total_keywords, 1), 2), 0.95)

        triggering_keywords = [kw for kw in law.get("keywords", []) if kw.lower() in combined_text.lower()]

        al = ApplicableLaw(
            case_id=case_id,
            act_name=law["act"],
            section_number=law["section"],
            section_title=law["title"],
            section_meaning=law["meaning"],
            reason_for_recommendation=f"Case description contains relevant terms: {', '.join(triggering_keywords[:3])}.",
            punishment=law.get("punishment"),
            nature_of_offence=law.get("nature_of_offence"),
            confidence_score=confidence,
            triggering_facts=triggering_keywords[:5],
        )
        db.add(al)
        new_laws.append(al)

    db.commit()
    for al in new_laws:
        db.refresh(al)
    return new_laws


def compute_case_scores(db: Session, case_id: int) -> CaseScore:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    # Evidence scoring
    total_ev = db.query(Evidence).filter(Evidence.case_id == case_id).count()
    collected_ev = db.query(Evidence).filter(
        Evidence.case_id == case_id,
        Evidence.status == EvidenceStatus.COLLECTED
    ).count()
    evidence_score = round((collected_ev / max(total_ev, 1)) * 100, 1)
    evidence_explanation = (
        f"{collected_ev} of {total_ev} recommended evidence items collected ({evidence_score}%). "
        + ("Strong evidentiary base." if evidence_score >= 70 else "More evidence collection needed.")
    )

    # Law identification scoring
    laws_count = db.query(ApplicableLaw).filter(ApplicableLaw.case_id == case_id).count()
    avg_confidence = 0.0
    if laws_count > 0:
        from sqlalchemy import func
        result = db.query(func.avg(ApplicableLaw.confidence_score)).filter(
            ApplicableLaw.case_id == case_id
        ).scalar()
        avg_confidence = float(result or 0.0)

    claim_score = round(min((laws_count * 10) + (avg_confidence * 40), 100), 1)
    claim_explanation = (
        f"{laws_count} applicable laws identified with average confidence {round(avg_confidence*100,1)}%. "
        + ("Legal basis is well-established." if claim_score >= 60 else "More legal analysis recommended.")
    )

    # Completeness scoring
    has_description = bool(case.description and len(case.description) > 50)
    has_classification = case.category not in (None, CaseCategory.UNKNOWN)
    has_responses = db.query(
        __import__("app.models.models", fromlist=["QuestionResponse"]).QuestionResponse
    ).filter(
        __import__("app.models.models", fromlist=["QuestionResponse"]).QuestionResponse.case_id == case_id
    ).count() > 0
    has_laws = laws_count > 0

    completeness_factors = [has_description, has_classification, has_responses, has_laws, total_ev > 0]
    completeness_score = round((sum(completeness_factors) / len(completeness_factors)) * 100, 1)
    completeness_explanation = (
        f"Case completeness: {sum(completeness_factors)}/{len(completeness_factors)} key elements present. "
        + ("Case well-documented." if completeness_score >= 80 else "Additional information needed.")
    )

    # Counterargument score (inverse of claim strength — higher means more vulnerability)
    counterarg_score = round(100 - claim_score, 1)
    counterarg_explanation = (
        "Potential counterargument exposure is "
        + ("low" if counterarg_score < 30 else "moderate" if counterarg_score < 60 else "high")
        + f" ({counterarg_score}%). "
        + ("Case has solid legal standing." if counterarg_score < 40 else "Consider addressing potential weaknesses.")
    )

    existing = db.query(CaseScore).filter(CaseScore.case_id == case_id).first()
    if existing:
        existing.claim_strength_score = claim_score
        existing.evidence_strength_score = evidence_score
        existing.case_completeness_score = completeness_score
        existing.counterargument_opportunity_score = counterarg_score
        existing.claim_strength_explanation = claim_explanation
        existing.evidence_strength_explanation = evidence_explanation
        existing.case_completeness_explanation = completeness_explanation
        existing.counterargument_explanation = counterarg_explanation
        existing.updated_at = datetime.utcnow()
        score_obj = existing
    else:
        score_obj = CaseScore(
            case_id=case_id,
            claim_strength_score=claim_score,
            evidence_strength_score=evidence_score,
            case_completeness_score=completeness_score,
            counterargument_opportunity_score=counterarg_score,
            claim_strength_explanation=claim_explanation,
            evidence_strength_explanation=evidence_explanation,
            case_completeness_explanation=completeness_explanation,
            counterargument_explanation=counterarg_explanation,
        )
        db.add(score_obj)

    db.commit()
    db.refresh(score_obj)
    return score_obj


def generate_recommendations(db: Session, case_id: int) -> List[Recommendation]:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    category = case.category.value if case.category else "criminal"
    actions = get_recommended_actions_for_category(category)

    db.query(Recommendation).filter(Recommendation.case_id == case_id).delete()

    priorities = ["high", "high", "medium", "medium", "medium", "low", "low", "low"]
    new_recs = []
    for i, action in enumerate(actions):
        rec = Recommendation(
            case_id=case_id,
            action=action,
            action_type=category,
            priority=priorities[i] if i < len(priorities) else "low",
            reasoning=f"Standard recommended action for {category} cases.",
            triggering_facts=[case.category.value if case.category else "general"],
        )
        db.add(rec)
        new_recs.append(rec)

    db.commit()
    for rec in new_recs:
        db.refresh(rec)
    return new_recs


def generate_gap_analysis(db: Session, case_id: int) -> List[GapAnalysis]:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    db.query(GapAnalysis).filter(GapAnalysis.case_id == case_id).delete()

    gaps = []

    # Check description length
    if not case.description or len(case.description) < 100:
        gaps.append(GapAnalysis(
            case_id=case_id,
            gap_type="missing_information",
            gap_description="Case description is too brief. More details are needed for accurate analysis.",
            severity="high",
            suggestion="Expand the case description with specific dates, locations, persons involved, and sequence of events.",
        ))

    # Check classification
    if case.category in (None, CaseCategory.UNKNOWN):
        gaps.append(GapAnalysis(
            case_id=case_id,
            gap_type="missing_classification",
            gap_description="Case has not been classified. Run AI classification first.",
            severity="high",
            suggestion="Click 'Classify Case' to run AI classification.",
        ))

    # Check evidence
    from app.models.models import QuestionResponse
    total_ev = db.query(Evidence).filter(Evidence.case_id == case_id).count()
    if total_ev == 0:
        gaps.append(GapAnalysis(
            case_id=case_id,
            gap_type="missing_evidence",
            gap_description="No evidence items have been identified yet.",
            severity="high",
            suggestion="Run evidence recommendation after classifying the case.",
        ))
    else:
        pending_ev = db.query(Evidence).filter(
            Evidence.case_id == case_id,
            Evidence.status == EvidenceStatus.PENDING
        ).count()
        if pending_ev > 0:
            gaps.append(GapAnalysis(
                case_id=case_id,
                gap_type="pending_evidence",
                gap_description=f"{pending_ev} evidence item(s) are still pending collection.",
                severity="medium",
                suggestion="Collect or mark all pending evidence items before proceeding to court.",
            ))

    # Check questionnaire responses
    response_count = db.query(QuestionResponse).filter(
        QuestionResponse.case_id == case_id
    ).count()
    if response_count == 0:
        gaps.append(GapAnalysis(
            case_id=case_id,
            gap_type="missing_questionnaire",
            gap_description="Case questionnaire has not been completed.",
            severity="medium",
            suggestion="Complete the dynamic questionnaire to provide structured case details.",
        ))

    # Check laws
    laws_count = db.query(ApplicableLaw).filter(ApplicableLaw.case_id == case_id).count()
    if laws_count == 0:
        gaps.append(GapAnalysis(
            case_id=case_id,
            gap_type="missing_laws",
            gap_description="No applicable laws have been identified for this case.",
            severity="high",
            suggestion="Run law identification after classifying the case.",
        ))

    for gap in gaps:
        db.add(gap)

    db.commit()
    for gap in gaps:
        db.refresh(gap)
    return gaps


def generate_timeline(db: Session, case_id: int) -> List[TimelineEvent]:
    case = get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    db.query(TimelineEvent).filter(TimelineEvent.case_id == case_id).delete()

    events = []

    events.append(TimelineEvent(
        case_id=case_id,
        event_date=case.created_at.strftime("%Y-%m-%d"),
        event_description=f"Case '{case.title}' created in the legal assistant system.",
        event_type="system",
        sequence_order=1,
    ))

    if case.category and case.category != CaseCategory.UNKNOWN:
        events.append(TimelineEvent(
            case_id=case_id,
            event_date=case.updated_at.strftime("%Y-%m-%d"),
            event_description=f"Case classified as {case.category.value.title()} — {case.subcategory or ''}.",
            event_type="classification",
            sequence_order=2,
        ))

    # Add events from questionnaire responses (dates given by user)
    from app.models.models import QuestionResponse
    date_responses = db.query(QuestionResponse).filter(
        QuestionResponse.case_id == case_id,
        QuestionResponse.question_type == "date"
    ).all()

    for i, resp in enumerate(date_responses):
        events.append(TimelineEvent(
            case_id=case_id,
            event_date=str(resp.answer),
            event_description=f"{resp.question_text}: {resp.answer}",
            event_type="user_provided",
            sequence_order=10 + i,
        ))

    for ev in events:
        db.add(ev)

    db.commit()
    for ev in events:
        db.refresh(ev)
    return events
