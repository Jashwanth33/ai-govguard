from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class UseCase(Base):
    __tablename__ = "use_cases"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    purpose = Column(Text, nullable=False)
    ai_capability = Column(String, nullable=False)
    data_types = Column(JSON, nullable=False)
    decision_type = Column(String, nullable=False)
    human_oversight = Column(String, nullable=False)
    model_type = Column(String, nullable=False)
    deployment_status = Column(String, default="Planning")
    affected_population = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    assessments = relationship("Assessment", back_populates="use_case")


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    use_case_id = Column(Integer, ForeignKey("use_cases.id"), nullable=False)
    overall_score = Column(Float, nullable=False)
    risk_level = Column(String, nullable=False)
    confidence = Column(Float, default=0.0)
    executive_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    use_case = relationship("UseCase", back_populates="assessments")
    risk_scores = relationship("RiskScore", back_populates="assessment")
    evidence_items = relationship("Evidence", back_populates="assessment")


class RiskScore(Base):
    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    dimension = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)
    reason = Column(Text)
    recommendation = Column(Text)
    controls = Column(JSON)

    assessment = relationship("Assessment", back_populates="risk_scores")


class Source(Base):
    __tablename__ = "sources"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, unique=True, nullable=False)
    title = Column(String, nullable=False)
    organization = Column(String, nullable=False)
    source_type = Column(String, nullable=False)
    url = Column(String)
    topic = Column(String)
    summary = Column(Text)
    publication_date = Column(String)
    jurisdiction = Column(String)
    authority_level = Column(String)
    retrieved_date = Column(DateTime, default=datetime.utcnow)


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    source_id = Column(Integer, ForeignKey("sources.id"), nullable=False)
    dimension = Column(String, nullable=False)
    relevance = Column(Text)
    finding = Column(Text)

    assessment = relationship("Assessment", back_populates="evidence_items")
    source = relationship("Source")
