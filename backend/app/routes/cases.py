from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.schemas import (
    CaseCreate, CaseUpdate, CaseOut, CaseListOut,
    CaseDocumentOut, MessageResponse
)
from app.services import case_service

router = APIRouter(prefix="/cases", tags=["Cases"])


@router.post("/", response_model=CaseOut, status_code=201)
def create_case(data: CaseCreate, db: Session = Depends(get_db)):
    return case_service.create_case(db, data)


@router.get("/", response_model=List[CaseListOut])
def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return case_service.get_cases(db, skip=skip, limit=limit, search=search)


@router.get("/{case_id}", response_model=CaseOut)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = case_service.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}", response_model=CaseOut)
def update_case(case_id: int, data: CaseUpdate, db: Session = Depends(get_db)):
    case = case_service.update_case(db, case_id, data)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.delete("/{case_id}", response_model=MessageResponse)
def delete_case(case_id: int, db: Session = Depends(get_db)):
    success = case_service.delete_case(db, case_id)
    if not success:
        raise HTTPException(status_code=404, detail="Case not found")
    return MessageResponse(message="Case deleted successfully")


@router.post("/{case_id}/documents", response_model=CaseDocumentOut, status_code=201)
def upload_document(
    case_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    return case_service.attach_document(db, case_id, file)
