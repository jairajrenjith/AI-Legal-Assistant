from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Any, Dict
from datetime import datetime
from app.models.models import (
    CaseStatus, CaseCategory, EvidenceStatus,
    DocumentType, DocumentFormat
)


# ─── Case Schemas ────────────────────────────────────────────────────────────

class CaseCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: str = Field(..., min_length=10)


class CaseUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=500)
    description: Optional[str] = None
    status: Optional[CaseStatus] = None


class CaseDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    case_id: int
    filename: str
    original_filename: str
    file_type: str
    file_size: int
    uploaded_at: datetime


class CaseScoreOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    claim_strength_score: Optional[float]
    evidence_strength_score: Optional[float]
    case_completeness_score: Optional[float]
    counterargument_opportunity_score: Optional[float]
    claim_strength_explanation: Optional[str]
    evidence_strength_explanation: Optional[str]
    case_completeness_explanation: Optional[str]
    counterargument_explanation: Optional[str]
    updated_at: datetime


class TimelineEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    event_date: Optional[str]
    event_description: str
    event_type: Optional[str]
    sequence_order: int


class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    action: str
    action_type: Optional[str]
    priority: str
    reasoning: Optional[str]
    triggering_facts: Optional[List[str]]


class GapAnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    gap_type: str
    gap_description: str
    severity: str
    suggestion: Optional[str]
    resolved: bool


class ApplicableLawOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    act_name: str
    section_number: str
    section_title: str
    section_meaning: str
    reason_for_recommendation: str
    punishment: Optional[str]
    nature_of_offence: Optional[str]
    confidence_score: float
    triggering_facts: Optional[List[str]]


class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    description: Optional[str]
    evidence_type: str
    importance: str
    status: EvidenceStatus
    ai_reasoning: Optional[str]
    created_at: datetime


class GeneratedDocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    document_type: DocumentType
    document_format: DocumentFormat
    filename: str
    generated_at: datetime


class CaseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    status: CaseStatus
    category: Optional[CaseCategory]
    subcategory: Optional[str]
    classification_confidence: Optional[float]
    ai_summary: Optional[str]
    extracted_entities: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    documents: List[CaseDocumentOut] = []
    evidence_items: List[EvidenceOut] = []
    applicable_laws: List[ApplicableLawOut] = []
    scores: Optional[CaseScoreOut] = None
    timeline_events: List[TimelineEventOut] = []
    recommendations: List[RecommendationOut] = []
    generated_documents: List[GeneratedDocumentOut] = []
    gap_analyses: List[GapAnalysisOut] = []


class CaseListOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    status: CaseStatus
    category: Optional[CaseCategory]
    subcategory: Optional[str]
    classification_confidence: Optional[float]
    created_at: datetime
    updated_at: datetime


# ─── Classification Schemas ───────────────────────────────────────────────────

class ClassificationRequest(BaseModel):
    case_id: int
    description: str
    title: str


class ClassificationResult(BaseModel):
    category: CaseCategory
    subcategory: str
    confidence: float
    summary: str
    extracted_entities: Dict[str, Any]
    reasoning: str


# ─── Questionnaire Schemas ────────────────────────────────────────────────────

class QuestionOption(BaseModel):
    value: str
    label: str


class Question(BaseModel):
    id: str
    text: str
    question_type: str  # multiple_choice | checkbox | dropdown | text | date
    options: Optional[List[QuestionOption]] = None
    required: bool = True
    conditional_on: Optional[str] = None
    conditional_value: Optional[str] = None
    help_text: Optional[str] = None


class QuestionnaireResponse(BaseModel):
    case_id: int
    responses: List[Dict[str, Any]]


class QuestionResponseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question_id: str
    question_text: str
    question_type: str
    answer: Any
    answered_at: datetime


# ─── Evidence Schemas ─────────────────────────────────────────────────────────

class EvidenceStatusUpdate(BaseModel):
    status: EvidenceStatus


# ─── Document Generation Schemas ─────────────────────────────────────────────

class DocumentGenerationRequest(BaseModel):
    case_id: int
    document_type: DocumentType
    document_format: DocumentFormat


# ─── Settings Schemas ─────────────────────────────────────────────────────────

class SettingUpdate(BaseModel):
    key: str
    value: str


class SettingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    value: Optional[str]
    updated_at: datetime


# ─── Generic Response ─────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True
