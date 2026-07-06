from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import (
    CaseOut, ApplicableLawOut, EvidenceOut, EvidenceStatusUpdate,
    CaseScoreOut, RecommendationOut, GapAnalysisOut, TimelineEventOut,
    MessageResponse
)
from app.services import case_service
from app.models.models import Evidence, EvidenceStatus

router = APIRouter(prefix="/analysis", tags=["Analysis"])


@router.post("/{case_id}/classify", response_model=CaseOut)
def classify_case(case_id: int, db: Session = Depends(get_db)):
    """Run AI classification on the case description."""
    return case_service.classify_case(db, case_id)


@router.post("/{case_id}/laws", response_model=List[ApplicableLawOut])
def identify_laws(case_id: int, db: Session = Depends(get_db)):
    """Identify applicable laws for the case."""
    return case_service.identify_applicable_laws(db, case_id)


@router.post("/{case_id}/evidence", response_model=List[EvidenceOut])
def recommend_evidence(case_id: int, db: Session = Depends(get_db)):
    """Generate evidence recommendations."""
    return case_service.generate_evidence_recommendations(db, case_id)


@router.patch("/{case_id}/evidence/{evidence_id}", response_model=EvidenceOut)
def update_evidence_status(
    case_id: int,
    evidence_id: int,
    data: EvidenceStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update the collection status of an evidence item."""
    ev = db.query(Evidence).filter(
        Evidence.id == evidence_id,
        Evidence.case_id == case_id,
    ).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    ev.status = data.status
    db.commit()
    db.refresh(ev)
    return ev


@router.post("/{case_id}/scores", response_model=CaseScoreOut)
def compute_scores(case_id: int, db: Session = Depends(get_db)):
    """Compute claim strength and other scores."""
    return case_service.compute_case_scores(db, case_id)


@router.post("/{case_id}/recommendations", response_model=List[RecommendationOut])
def generate_recommendations(case_id: int, db: Session = Depends(get_db)):
    """Generate recommended next actions."""
    return case_service.generate_recommendations(db, case_id)


@router.post("/{case_id}/gaps", response_model=List[GapAnalysisOut])
def generate_gaps(case_id: int, db: Session = Depends(get_db)):
    """Generate gap analysis."""
    return case_service.generate_gap_analysis(db, case_id)


@router.post("/{case_id}/timeline", response_model=List[TimelineEventOut])
def generate_timeline(case_id: int, db: Session = Depends(get_db)):
    """Generate case timeline."""
    return case_service.generate_timeline(db, case_id)


@router.post("/{case_id}/full-analysis", response_model=CaseOut)
def run_full_analysis(case_id: int, db: Session = Depends(get_db)):
    """Run all analysis steps in sequence: classify → laws → evidence → scores → recommendations → gaps → timeline."""
    case_service.classify_case(db, case_id)
    case_service.identify_applicable_laws(db, case_id)
    case_service.generate_evidence_recommendations(db, case_id)
    case_service.generate_recommendations(db, case_id)
    case_service.compute_case_scores(db, case_id)
    case_service.generate_gap_analysis(db, case_id)
    case_service.generate_timeline(db, case_id)
    case = case_service.get_case(db, case_id)
    return case
