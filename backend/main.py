from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import engine, get_db, Base
from models import UseCase, Assessment, RiskScore, Source, Evidence
from governance_engine import assess_use_case
from ai_layer import generate_executive_summary, generate_top_risks, generate_controls
from seed_data import SOURCES, SAMPLE_USE_CASES

app = FastAPI(title="AI-GovGuard API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


class UseCaseCreate(BaseModel):
    name: str
    industry: str
    purpose: str
    ai_capability: str
    data_types: List[str]
    decision_type: str
    human_oversight: str
    model_type: str
    deployment_status: str = "Planning"
    affected_population: int = 0


class UseCaseResponse(BaseModel):
    id: int
    name: str
    industry: str
    purpose: str
    ai_capability: str
    data_types: List[str]
    decision_type: str
    human_oversight: str
    model_type: str
    deployment_status: str
    affected_population: int
    created_at: datetime

    class Config:
        from_attributes = True


class RiskScoreResponse(BaseModel):
    id: int
    dimension: str
    score: float
    weight: float
    reason: Optional[str]
    recommendation: Optional[str]
    controls: Optional[list]

    class Config:
        from_attributes = True


class AssessmentResponse(BaseModel):
    id: int
    use_case_id: int
    overall_score: float
    risk_level: str
    confidence: float
    executive_summary: Optional[str]
    created_at: datetime
    risk_scores: List[RiskScoreResponse]

    class Config:
        from_attributes = True


class AssessmentDetailResponse(BaseModel):
    id: int
    use_case_id: int
    overall_score: float
    risk_level: str
    confidence: float
    executive_summary: Optional[str]
    created_at: datetime
    risk_scores: List[RiskScoreResponse]
    use_case: UseCaseResponse
    top_risks: list
    recommended_controls: list
    evidence: list

    class Config:
        from_attributes = True


class SourceResponse(BaseModel):
    id: int
    source_id: str
    title: str
    organization: str
    source_type: str
    url: Optional[str]
    topic: Optional[str]
    summary: Optional[str]
    publication_date: Optional[str]
    jurisdiction: Optional[str]
    authority_level: Optional[str]

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_use_cases: int
    total_assessments: int
    high_risk_count: int
    very_high_risk_count: int
    low_risk_count: int
    average_score: float
    risk_distribution: dict
    recent_assessments: list


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/use-cases", response_model=UseCaseResponse)
def create_use_case(use_case: UseCaseCreate, db: Session = Depends(get_db)):
    db_use_case = UseCase(**use_case.model_dump())
    db.add(db_use_case)
    db.commit()
    db.refresh(db_use_case)
    return db_use_case


@app.get("/api/use-cases", response_model=List[UseCaseResponse])
def list_use_cases(db: Session = Depends(get_db)):
    return db.query(UseCase).all()


@app.get("/api/use-cases/{use_case_id}", response_model=UseCaseResponse)
def get_use_case(use_case_id: int, db: Session = Depends(get_db)):
    use_case = db.query(UseCase).filter(UseCase.id == use_case_id).first()
    if not use_case:
        raise HTTPException(status_code=404, detail="Use case not found")
    return use_case


@app.put("/api/use-cases/{use_case_id}", response_model=UseCaseResponse)
def update_use_case(use_case_id: int, use_case: UseCaseCreate, db: Session = Depends(get_db)):
    db_use_case = db.query(UseCase).filter(UseCase.id == use_case_id).first()
    if not db_use_case:
        raise HTTPException(status_code=404, detail="Use case not found")
    for key, value in use_case.model_dump().items():
        setattr(db_use_case, key, value)
    db.commit()
    db.refresh(db_use_case)
    return db_use_case


@app.delete("/api/use-cases/{use_case_id}")
def delete_use_case(use_case_id: int, db: Session = Depends(get_db)):
    db_use_case = db.query(UseCase).filter(UseCase.id == use_case_id).first()
    if not db_use_case:
        raise HTTPException(status_code=404, detail="Use case not found")
    db.query(Evidence).filter(Evidence.assessment_id.in_(
        db.query(Assessment.id).filter(Assessment.use_case_id == use_case_id)
    )).delete(synchronize_session=False)
    db.query(RiskScore).filter(RiskScore.assessment_id.in_(
        db.query(Assessment.id).filter(Assessment.use_case_id == use_case_id)
    )).delete(synchronize_session=False)
    db.query(Assessment).filter(Assessment.use_case_id == use_case_id).delete(synchronize_session=False)
    db.delete(db_use_case)
    db.commit()
    return {"status": "deleted"}


@app.post("/api/assessments/{use_case_id}")
def run_assessment(use_case_id: int, db: Session = Depends(get_db)):
    use_case = db.query(UseCase).filter(UseCase.id == use_case_id).first()
    if not use_case:
        raise HTTPException(status_code=404, detail="Use case not found")

    use_case_dict = {
        "name": use_case.name,
        "industry": use_case.industry,
        "purpose": use_case.purpose,
        "ai_capability": use_case.ai_capability,
        "data_types": use_case.data_types,
        "decision_type": use_case.decision_type,
        "human_oversight": use_case.human_oversight,
        "model_type": use_case.model_type,
        "deployment_status": use_case.deployment_status,
        "affected_population": use_case.affected_population,
    }

    result = assess_use_case(use_case_dict)

    executive_summary = generate_executive_summary(use_case_dict, result)

    assessment = Assessment(
        use_case_id=use_case_id,
        overall_score=result["overall_score"],
        risk_level=result["risk_level"],
        confidence=result["confidence"],
        executive_summary=executive_summary,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)

    for dim_name, dim_data in result["dimensions"].items():
        risk_score = RiskScore(
            assessment_id=assessment.id,
            dimension=dim_name,
            score=dim_data["score"],
            weight=dim_data["weight"],
            reason=dim_data["reason"],
            recommendation=dim_data["recommendation"],
            controls=dim_data["controls"],
        )
        db.add(risk_score)

    db.commit()

    source_topic_map = {
        "data": ["AI Risk Management", "Data Protection", "Data Governance"],
        "privacy": ["Data Protection", "Privacy", "GDPR"],
        "fairness": ["Algorithmic Fairness", "Bias", "AI Ethics"],
        "human_oversight": ["AI Safety", "Human Oversight", "Accountability"],
        "explainability": ["AI Transparency", "Explainability", "Interpretability"],
        "security": ["AI Security", "Cybersecurity", "Adversarial Attacks"],
        "decision_impact": ["AI Risk Classification", "High-Risk AI Systems"],
        "regulatory": ["AI Regulation", "Compliance", "Legal Requirements"],
        "model_risk": ["Model Validation", "Model Risk", "AI Testing"],
        "monitoring": ["AI Monitoring", "Performance Tracking", "Incident Response"],
    }

    all_sources = db.query(Source).all()
    for dim_name, dim_data in result["dimensions"].items():
        if dim_data["score"] >= 5:
            relevant_topics = source_topic_map.get(dim_name, [])
            matched_sources = [
                s for s in all_sources
                if any(t.lower() in (s.topic or "").lower() for t in relevant_topics)
            ]
            if not matched_sources:
                matched_sources = all_sources[:2]

            for source in matched_sources[:2]:
                evidence = Evidence(
                    assessment_id=assessment.id,
                    source_id=source.id,
                    dimension=dim_name,
                    relevance=f"Applicable to {dim_name.replace('_', ' ')} assessment for {use_case.industry} industry",
                    finding=dim_data["reason"],
                )
                db.add(evidence)

    db.commit()

    return {"assessment_id": assessment.id, "status": "completed"}


@app.get("/api/assessments", response_model=List[AssessmentResponse])
def list_assessments(db: Session = Depends(get_db)):
    return db.query(Assessment).all()


@app.get("/api/assessments/{assessment_id}")
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    use_case = db.query(UseCase).filter(UseCase.id == assessment.use_case_id).first()
    risk_scores = db.query(RiskScore).filter(RiskScore.assessment_id == assessment.id).all()
    evidence_items = db.query(Evidence).filter(Evidence.assessment_id == assessment.id).all()

    use_case_dict = {
        "name": use_case.name,
        "industry": use_case.industry,
        "purpose": use_case.purpose,
        "ai_capability": use_case.ai_capability,
        "data_types": use_case.data_types,
        "decision_type": use_case.decision_type,
        "human_oversight": use_case.human_oversight,
        "model_type": use_case.model_type,
        "deployment_status": use_case.deployment_status,
        "affected_population": use_case.affected_population,
    }

    assessment_result = {
        "overall_score": assessment.overall_score,
        "risk_level": assessment.risk_level,
        "confidence": assessment.confidence,
        "dimensions": {
            rs.dimension: {"score": rs.score, "reason": rs.reason, "recommendation": rs.recommendation}
            for rs in risk_scores
        },
    }

    top_risks = generate_top_risks(assessment_result)
    recommended_controls = generate_controls(assessment_result)

    evidence_list = []
    for ev in evidence_items:
        source = db.query(Source).filter(Source.id == ev.source_id).first()
        if source:
            evidence_list.append({
                "id": ev.id,
                "dimension": ev.dimension,
                "finding": ev.finding,
                "relevance": ev.relevance,
                "source": {
                    "source_id": source.source_id,
                    "title": source.title,
                    "organization": source.organization,
                    "source_type": source.source_type,
                    "url": source.url,
                    "authority_level": source.authority_level,
                }
            })

    return {
        "id": assessment.id,
        "use_case_id": assessment.use_case_id,
        "overall_score": assessment.overall_score,
        "risk_level": assessment.risk_level,
        "confidence": assessment.confidence,
        "executive_summary": assessment.executive_summary,
        "created_at": assessment.created_at,
        "risk_scores": [
            {
                "id": rs.id,
                "dimension": rs.dimension,
                "score": rs.score,
                "weight": rs.weight,
                "reason": rs.reason,
                "recommendation": rs.recommendation,
                "controls": rs.controls,
            }
            for rs in risk_scores
        ],
        "use_case": {
            "id": use_case.id,
            "name": use_case.name,
            "industry": use_case.industry,
            "purpose": use_case.purpose,
            "ai_capability": use_case.ai_capability,
            "data_types": use_case.data_types,
            "decision_type": use_case.decision_type,
            "human_oversight": use_case.human_oversight,
            "model_type": use_case.model_type,
            "deployment_status": use_case.deployment_status,
            "affected_population": use_case.affected_population,
            "created_at": use_case.created_at,
        },
        "top_risks": top_risks,
        "recommended_controls": recommended_controls,
        "evidence": evidence_list,
    }


@app.get("/api/sources", response_model=List[SourceResponse])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()


@app.get("/api/dashboard", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db)):
    total_use_cases = db.query(UseCase).count()
    total_assessments = db.query(Assessment).count()

    risk_distribution = {
        "LOW": 0,
        "MODERATE": 0,
        "HIGH": 0,
        "VERY HIGH": 0,
        "CRITICAL": 0,
    }

    assessments = db.query(Assessment).all()
    total_score = 0
    for a in assessments:
        risk_distribution[a.risk_level] = risk_distribution.get(a.risk_level, 0) + 1
        total_score += a.overall_score

    average_score = round(total_score / total_assessments, 1) if total_assessments > 0 else 0

    recent = db.query(Assessment).order_by(Assessment.created_at.desc()).limit(5).all()
    recent_list = []
    for a in recent:
        uc = db.query(UseCase).filter(UseCase.id == a.use_case_id).first()
        recent_list.append({
            "id": a.id,
            "use_case_name": uc.name if uc else "Unknown",
            "overall_score": a.overall_score,
            "risk_level": a.risk_level,
            "created_at": a.created_at.isoformat() if a.created_at else "",
        })

    return DashboardStats(
        total_use_cases=total_use_cases,
        total_assessments=total_assessments,
        high_risk_count=risk_distribution.get("HIGH", 0),
        very_high_risk_count=risk_distribution.get("VERY HIGH", 0) + risk_distribution.get("CRITICAL", 0),
        low_risk_count=risk_distribution.get("LOW", 0) + risk_distribution.get("MODERATE", 0),
        average_score=average_score,
        risk_distribution=risk_distribution,
        recent_assessments=recent_list,
    )


@app.post("/api/seed")
def seed_database(db: Session = Depends(get_db)):
    existing_sources = db.query(Source).count()
    if existing_sources == 0:
        for source_data in SOURCES:
            source = Source(**source_data)
            db.add(source)
        db.commit()

    existing_cases = db.query(UseCase).count()
    if existing_cases == 0:
        for case_data in SAMPLE_USE_CASES:
            use_case = UseCase(**case_data)
            db.add(use_case)
        db.commit()

    return {"status": "seeded", "sources": len(SOURCES), "use_cases": len(SAMPLE_USE_CASES)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
