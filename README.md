# AI-GovGuard

An AI governance assessment application that evaluates AI use cases across privacy, fairness, human oversight, explainability, security, regulatory exposure, model risk, and monitoring, while providing evidence-backed recommendations.

## Architecture

```
React UI (Dashboard / Forms)
        │
        ▼
FastAPI REST API
        │
   ┌────┴────┐
   ▼         ▼
Governance   AI Intelligence
Rules Engine  LLM / Templates
   └────┬────┘
        ▼
    SQLite DB
        │
        ▼
Evidence Repository
```

## Quick Start

### Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
```

Backend runs at: http://localhost:8000

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at: http://localhost:5173

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| /api/health | GET | Health check |
| /api/seed | POST | Seed database with sample data |
| /api/use-cases | GET | List all use cases |
| /api/use-cases | POST | Create new use case |
| /api/assessments/{id} | POST | Run assessment |
| /api/assessments | GET | List all assessments |
| /api/assessments/{id} | GET | Get assessment details |
| /api/sources | GET | List all sources |
| /api/dashboard | GET | Dashboard statistics |

## Governance Dimensions

The platform evaluates 10 risk dimensions:

1. **Data** - Data quality, sensitivity, provenance
2. **Privacy** - Personal data, consent, retention
3. **Fairness** - Bias, disparate impact, protected groups
4. **Human Oversight** - Override capability, review processes
5. **Explainability** - Decision transparency, interpretability
6. **Security** - Access control, encryption, threats
7. **Decision Impact** - Individual and societal impact
8. **Regulatory** - Compliance requirements
9. **Model Risk** - Validation, drift, accuracy
10. **Monitoring** - Performance tracking, incident response

## Risk Classification

| Score | Classification |
|-------|----------------|
| 0-2.9 | LOW |
| 3-4.9 | MODERATE |
| 5-6.9 | HIGH |
| 7-8.4 | VERY HIGH |
| 8.5-10 | CRITICAL |

## Sample Use Cases

- AI Recruitment Screening
- Bank Loan Risk Scoring
- Customer Support AI
- Healthcare Appointment Risk Prediction

## Source Types

The platform distinguishes between:

- Law / Regulation
- Regulatory Guidance
- Industry Standard / Framework
- Research
- Vendor Information
- General Web Content

## Disclaimer

This assessment is a governance decision-support tool and does not constitute legal advice or a formal regulatory determination.
