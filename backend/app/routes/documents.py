import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.schemas import DocumentGenerationRequest, GeneratedDocumentOut
from app.models.models import GeneratedDocument
from app.services.document_service import generate_document

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/generate", response_model=GeneratedDocumentOut, status_code=201)
def generate_doc(data: DocumentGenerationRequest, db: Session = Depends(get_db)):
    """Generate a PDF or DOCX document for a case."""
    return generate_document(db, data.case_id, data.document_type, data.document_format)


@router.get("/case/{case_id}", response_model=List[GeneratedDocumentOut])
def list_documents(case_id: int, db: Session = Depends(get_db)):
    """List all generated documents for a case."""
    return db.query(GeneratedDocument).filter(GeneratedDocument.case_id == case_id).all()


@router.get("/download/{document_id}")
def download_document(document_id: int, db: Session = Depends(get_db)):
    """Download a generated document file."""
    doc = db.query(GeneratedDocument).filter(GeneratedDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Document file not found on disk")

    media_type = "application/pdf" if doc.document_format.value == "pdf" else \
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return FileResponse(
        path=doc.file_path,
        filename=doc.filename,
        media_type=media_type,
    )
