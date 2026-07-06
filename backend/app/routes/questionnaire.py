from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import Question, QuestionnaireResponse, QuestionResponseOut, MessageResponse
from app.models.models import Case, QuestionResponse as QRModel
from app.utils.knowledge_loader import get_questions_for_category

router = APIRouter(prefix="/questionnaire", tags=["Questionnaire"])


@router.get("/{case_id}/questions", response_model=List[Question])
def get_questions(case_id: int, db: Session = Depends(get_db)):
    """Get category-specific questions for the case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    category = case.category.value if case.category else None
    if not category or category == "unknown":
        raise HTTPException(
            status_code=400,
            detail="Case must be classified before generating questionnaire. Run /analysis/{case_id}/classify first.",
        )

    raw_questions = get_questions_for_category(category)
    questions = []
    for q in raw_questions:
        options = None
        if "options" in q:
            options = [{"value": opt.lower().replace(" ", "_"), "label": opt} for opt in q["options"]]
        questions.append(Question(
            id=q["id"],
            text=q["text"],
            question_type=q.get("type", "text"),
            options=options,
            required=True,
            help_text=q.get("help_text"),
        ))
    return questions


@router.post("/{case_id}/responses", response_model=List[QuestionResponseOut], status_code=201)
def submit_responses(
    case_id: int,
    data: QuestionnaireResponse,
    db: Session = Depends(get_db),
):
    """Submit questionnaire responses for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    saved = []
    for resp in data.responses:
        question_id = resp.get("question_id")
        if not question_id:
            continue

        # Upsert: update if already answered, insert otherwise
        existing = db.query(QRModel).filter(
            QRModel.case_id == case_id,
            QRModel.question_id == question_id,
        ).first()

        if existing:
            existing.answer = resp.get("answer")
            db.commit()
            db.refresh(existing)
            saved.append(existing)
        else:
            qr = QRModel(
                case_id=case_id,
                question_id=question_id,
                question_text=resp.get("question_text", ""),
                question_type=resp.get("question_type", "text"),
                answer=resp.get("answer"),
            )
            db.add(qr)
            db.commit()
            db.refresh(qr)
            saved.append(qr)

    return saved


@router.get("/{case_id}/responses", response_model=List[QuestionResponseOut])
def get_responses(case_id: int, db: Session = Depends(get_db)):
    """Get all submitted questionnaire responses for a case."""
    case = db.query(Case).filter(Case.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return db.query(QRModel).filter(QRModel.case_id == case_id).all()
