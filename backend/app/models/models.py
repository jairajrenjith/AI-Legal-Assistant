import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, ForeignKey, Enum as SAEnum, JSON
)
from sqlalchemy.orm import relationship
from app.database.database import Base


class CaseStatus(str, enum.Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CaseCategory(str, enum.Enum):
    CRIMINAL = "criminal"
    PROPERTY = "property"
    FAMILY = "family"
    CONSUMER = "consumer"
    LABOR = "labor"
    CYBER = "cyber"
    ADMINISTRATIVE = "administrative"
    UNKNOWN = "unknown"


class EvidenceStatus(str, enum.Enum):
    PENDING = "pending"
    COLLECTED = "collected"
    UNAVAILABLE = "unavailable"


class DocumentType(str, enum.Enum):
    COMPLAINT_DRAFT = "complaint_draft"
    FIR_DRAFT = "fir_draft"
    LEGAL_NOTICE = "legal_notice"
    CASE_SUMMARY = "case_summary"
    INVESTIGATION_REPORT = "investigation_report"


class DocumentFormat(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"


class Case(Base):
    __tablename__ = "cases"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(SAEnum(CaseStatus), default=CaseStatus.DRAFT, nullable=False)
    category = Column(SAEnum(CaseCategory), default=CaseCategory.UNKNOWN, nullable=True)
    subcategory = Column(String(200), nullable=True)
    classification_confidence = Column(Float, nullable=True)
    ai_summary = Column(Text, nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    documents = relationship("CaseDocument", back_populates="case", cascade="all, delete-orphan")
    responses = relationship("QuestionResponse", back_populates="case", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="case", cascade="all, delete-orphan")
    applicable_laws = relationship("ApplicableLaw", back_populates="case", cascade="all, delete-orphan")
    scores = relationship("CaseScore", back_populates="case", uselist=False, cascade="all, delete-orphan")
    timeline_events = relationship("TimelineEvent", back_populates="case", cascade="all, delete-orphan")
    recommendations = relationship("Recommendation", back_populates="case", cascade="all, delete-orphan")
    generated_documents = relationship("GeneratedDocument", back_populates="case", cascade="all, delete-orphan")
    gap_analyses = relationship("GapAnalysis", back_populates="case", cascade="all, delete-orphan")


class CaseDocument(Base):
    __tablename__ = "case_documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(500), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="documents")


class QuestionResponse(Base):
    __tablename__ = "question_responses"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String(200), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)
    answer = Column(JSON, nullable=False)
    answered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="responses")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    evidence_type = Column(String(200), nullable=False)
    importance = Column(String(50), default="important")
    status = Column(SAEnum(EvidenceStatus), default=EvidenceStatus.PENDING, nullable=False)
    ai_reasoning = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="evidence_items")


class ApplicableLaw(Base):
    __tablename__ = "applicable_laws"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    act_name = Column(String(500), nullable=False)
    section_number = Column(String(100), nullable=False)
    section_title = Column(String(500), nullable=False)
    section_meaning = Column(Text, nullable=False)
    reason_for_recommendation = Column(Text, nullable=False)
    punishment = Column(Text, nullable=True)
    nature_of_offence = Column(String(200), nullable=True)
    confidence_score = Column(Float, nullable=False, default=0.0)
    triggering_facts = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="applicable_laws")


class CaseScore(Base):
    __tablename__ = "case_scores"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False, unique=True)
    claim_strength_score = Column(Float, nullable=True)
    evidence_strength_score = Column(Float, nullable=True)
    case_completeness_score = Column(Float, nullable=True)
    counterargument_opportunity_score = Column(Float, nullable=True)
    claim_strength_explanation = Column(Text, nullable=True)
    evidence_strength_explanation = Column(Text, nullable=True)
    case_completeness_explanation = Column(Text, nullable=True)
    counterargument_explanation = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="scores")


class TimelineEvent(Base):
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    event_date = Column(String(100), nullable=True)
    event_description = Column(Text, nullable=False)
    event_type = Column(String(100), nullable=True)
    sequence_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="timeline_events")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    action = Column(Text, nullable=False)
    action_type = Column(String(200), nullable=True)
    priority = Column(String(50), default="medium")
    reasoning = Column(Text, nullable=True)
    triggering_facts = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="recommendations")


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    document_type = Column(SAEnum(DocumentType), nullable=False)
    document_format = Column(SAEnum(DocumentFormat), nullable=False)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="generated_documents")


class GapAnalysis(Base):
    __tablename__ = "gap_analyses"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    gap_type = Column(String(200), nullable=False)
    gap_description = Column(Text, nullable=False)
    severity = Column(String(50), default="medium")
    suggestion = Column(Text, nullable=True)
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="gap_analyses")


class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(200), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
