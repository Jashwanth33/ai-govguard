from typing import Dict, Any


def generate_executive_summary(use_case: Dict, assessment: Dict) -> str:
    risk_level = assessment["risk_level"]
    overall_score = assessment["overall_score"]

    high_risk_dims = []
    for dim_name, dim_data in assessment["dimensions"].items():
        if dim_data["score"] >= 7:
            high_risk_dims.append(dim_name.replace("_", " ").title())

    name = use_case.get("name", "This AI system")
    industry = use_case.get("industry", "the target industry")
    purpose = use_case.get("purpose", "its intended purpose")

    summary = f"{name} has been assessed as {risk_level} risk with an overall score of {overall_score}/10. "

    if high_risk_dims:
        summary += f"The primary areas of concern are: {', '.join(high_risk_dims[:3])}. "

    decision_type = use_case.get("decision_type", "")
    if decision_type in ["automated", "high_impact_automated"]:
        summary += "This system makes automated decisions that affect individuals, requiring strong governance controls. "

    data_types = use_case.get("data_types", [])
    if "sensitive_data" in data_types or "health_data" in data_types:
        summary += "The processing of sensitive data categories necessitates enhanced privacy and security measures. "

    summary += "This assessment is based on deterministic governance rules and should be reviewed by the organization's governance and compliance functions."

    return summary


def generate_top_risks(assessment: Dict) -> list:
    risks = []
    risk_priority = {
        "decision_impact": "High decision impact on affected individuals",
        "fairness": "Potential fairness and bias concerns",
        "regulatory": "Significant regulatory exposure",
        "privacy": "Privacy risks from data processing",
        "human_oversight": "Insufficient human oversight mechanisms",
        "explainability": "Limited model explainability",
        "security": "Security vulnerabilities identified",
        "data": "Data quality and governance concerns",
        "model_risk": "Model reliability and validation gaps",
        "monitoring": "Insufficient monitoring controls",
    }

    sorted_dims = sorted(
        assessment["dimensions"].items(),
        key=lambda x: x[1]["score"],
        reverse=True
    )

    for dim_name, dim_data in sorted_dims[:4]:
        if dim_data["score"] >= 5:
            risks.append({
                "dimension": dim_name.replace("_", " ").title(),
                "risk": risk_priority.get(dim_name, "Risk identified"),
                "score": dim_data["score"],
            })

    return risks


def generate_controls(assessment: Dict) -> list:
    controls = []
    seen = set()

    for dim_name, dim_data in assessment["dimensions"].items():
        if dim_data["score"] >= 5:
            rec_text = dim_data.get("recommendation", "")
            if isinstance(rec_text, str):
                recs = [r.strip() for r in rec_text.split(";") if r.strip()]
            else:
                recs = rec_text if isinstance(rec_text, list) else []
            for rec in recs:
                if rec not in seen:
                    seen.add(rec)
                    controls.append({
                        "dimension": dim_name.replace("_", " ").title(),
                        "control": rec,
                        "priority": "High" if dim_data["score"] >= 7 else "Medium",
                    })

    return controls[:8]


def generate_fallback_explanation(dimension: str, score: float, reason: str) -> str:
    level = "minimal" if score <= 3 else "moderate" if score <= 6 else "significant" if score <= 8 else "critical"

    explanations = {
        "data": f"The data risk is {level} ({score}/10). {reason}",
        "privacy": f"The privacy risk is {level} ({score}/10). {reason}",
        "fairness": f"The fairness risk is {level} ({score}/10). {reason}",
        "human_oversight": f"The human oversight risk is {level} ({score}/10). {reason}",
        "explainability": f"The explainability risk is {level} ({score}/10). {reason}",
        "security": f"The security risk is {level} ({score}/10). {reason}",
        "decision_impact": f"The decision impact risk is {level} ({score}/10). {reason}",
        "regulatory": f"The regulatory exposure is {level} ({score}/10). {reason}",
        "model_risk": f"The model risk is {level} ({score}/10). {reason}",
        "monitoring": f"The monitoring risk is {level} ({score}/10). {reason}",
    }

    return explanations.get(dimension, f"The {dimension} risk is {level} ({score}/10). {reason}")
