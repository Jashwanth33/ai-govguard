from typing import Dict, List, Any, Tuple


DIMENSION_WEIGHTS = {
    "data": 0.10,
    "privacy": 0.10,
    "fairness": 0.12,
    "human_oversight": 0.12,
    "explainability": 0.08,
    "security": 0.10,
    "decision_impact": 0.15,
    "regulatory": 0.12,
    "model_risk": 0.06,
    "monitoring": 0.05,
}

DECISION_IMPACT_MAP = {
    "informational": 1,
    "advisory": 2,
    "decision_support": 3,
    "automated": 4,
    "high_impact_automated": 5,
}

SENSITIVE_INDUSTRIES = [
    "healthcare", "insurance", "banking", "financial_services",
    "human_resources", "education", "law_enforcement", "government"
]


def calculate_data_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    data_types = use_case.get("data_types", [])

    if "personal_data" in data_types:
        score += 2
        reasons.append("System processes personal data")
        recommendations.append("Implement data minimization principles")

    if "sensitive_data" in data_types:
        score += 3
        reasons.append("System processes sensitive data categories")
        recommendations.append("Apply enhanced data protection controls")

    if "financial_data" in data_types:
        score += 2
        reasons.append("Financial data processing identified")
        recommendations.append("Ensure financial data encryption at rest and in transit")

    if "health_data" in data_types:
        score += 3
        reasons.append("Health data processing identified")
        recommendations.append("Apply HIPAA-level data protection controls")

    if "biometric_data" in data_types:
        score += 3
        reasons.append("Biometric data processing identified")
        recommendations.append("Implement strict biometric data retention limits")

    affected = use_case.get("affected_population", 0)
    if affected > 10000:
        score += 2
        reasons.append(f"Large affected population: {affected}")
    elif affected > 1000:
        score += 1
        reasons.append(f"Moderate affected population: {affected}")

    if not reasons:
        score = 1
        reasons.append("Limited data risk indicators identified")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_privacy_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    data_types = use_case.get("data_types", [])

    if "personal_data" in data_types:
        score += 3
        reasons.append("Personal data processing requires privacy controls")
        recommendations.append("Establish lawful basis for processing")

    if "sensitive_data" in data_types:
        score += 3
        reasons.append("Sensitive data triggers enhanced privacy requirements")
        recommendations.append("Implement data protection impact assessment")

    if "health_data" in data_types or "biometric_data" in data_types:
        score += 2
        reasons.append("Special category data requires additional safeguards")
        recommendations.append("Apply purpose limitation and storage limitation")

    industry = use_case.get("industry", "").lower()
    if industry in ["insurance", "healthcare", "banking"]:
        score += 1
        reasons.append(f"Industry '{industry}' has heightened privacy expectations")

    if score == 0:
        score = 1
        reasons.append("Basic privacy controls recommended")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_fairness_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    data_types = use_case.get("data_types", [])
    decision_type = use_case.get("decision_type", "")
    industry = use_case.get("industry", "").lower()

    if decision_type in ["automated", "high_impact_automated"]:
        score += 3
        reasons.append("Automated decision-making increases fairness risk")

    if industry in ["human_resources", "insurance", "banking", "financial_services", "education"]:
        score += 3
        reasons.append(f"Industry '{industry}' is high-risk for algorithmic bias")

    if "personal_data" in data_types or "sensitive_data" in data_types:
        score += 2
        reasons.append("Personal/sensitive data may contain protected attributes")

    affected = use_case.get("affected_population", 0)
    if affected > 1000:
        score += 1
        reasons.append("Large population increases potential disparate impact")

    purpose = use_case.get("purpose", "").lower()
    bias_keywords = ["hiring", "recruitment", "lending", "loan", "insurance", "claim", "scoring", "ranking"]
    for keyword in bias_keywords:
        if keyword in purpose:
            score += 1
            reasons.append(f"Purpose contains bias-sensitive keyword: '{keyword}'")
            break

    if score == 0:
        score = 1
        reasons.append("Baseline fairness monitoring recommended")

    recommendations.append("Conduct group-level fairness testing")
    recommendations.append("Monitor for disparate impact across protected groups")
    recommendations.append("Document fairness metrics and thresholds")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_human_oversight_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    decision_type = use_case.get("decision_type", "")
    human_oversight = use_case.get("human_oversight", "")

    if decision_type in ["automated", "high_impact_automated"]:
        score += 3
        reasons.append("Automated decision-making identified")

    if human_oversight == "none":
        score += 4
        reasons.append("No human oversight mechanism exists")
        recommendations.append("IMMEDIATE: Implement human review before adverse decisions")
    elif human_oversight == "optional":
        score += 2
        reasons.append("Human oversight is optional, not mandatory")
        recommendations.append("Make human review mandatory for high-impact decisions")
    else:
        score += 1
        reasons.append("Human oversight exists but effectiveness should be validated")

    if decision_type == "high_impact_automated" and human_oversight != "required":
        score += 2
        reasons.append("High-impact automated decisions without mandatory human review")

    if score == 0:
        score = 1
        reasons.append("Human oversight controls appear adequate")

    recommendations.append("Ensure reviewers have authority to override AI decisions")
    recommendations.append("Implement escalation procedures for edge cases")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_explainability_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    decision_type = use_case.get("decision_type", "")
    model_type = use_case.get("model_type", "")

    if decision_type in ["automated", "high_impact_automated", "decision_support"]:
        score += 3
        reasons.append("Decision-making system requires explainability")

    if model_type in ["classification", "regression"]:
        score += 2
        reasons.append("Traditional ML models should provide feature importance")
    elif model_type == "generative_ai":
        score += 3
        reasons.append("Generative AI models have inherent explainability challenges")

    industry = use_case.get("industry", "").lower()
    if industry in ["insurance", "banking", "healthcare"]:
        score += 2
        reasons.append(f"Industry '{industry}' may require regulatory explainability")

    if score == 0:
        score = 1
        reasons.append("Basic explainability documentation recommended")

    recommendations.append("Document model decision logic and key features")
    recommendations.append("Provide user-facing explanations for decisions")
    recommendations.append("Maintain decision audit trail")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_security_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    data_types = use_case.get("data_types", [])
    model_type = use_case.get("model_type", "")

    if "personal_data" in data_types or "sensitive_data" in data_types:
        score += 2
        reasons.append("Sensitive data requires security controls")

    if "financial_data" in data_types or "health_data" in data_types:
        score += 2
        reasons.append("High-value data targets require enhanced security")

    if model_type == "generative_ai":
        score += 2
        reasons.append("Generative AI introduces prompt injection and jailbreaking risks")
        recommendations.append("Implement input validation and prompt filtering")

    if model_type in ["classification", "regression", "recommendation"]:
        score += 1
        reasons.append("ML models require adversarial attack protection")

    affected = use_case.get("affected_population", 0)
    if affected > 5000:
        score += 1
        reasons.append("Large-scale system increases attack surface")

    if score == 0:
        score = 1
        reasons.append("Baseline security controls recommended")

    recommendations.append("Implement authentication and authorization")
    recommendations.append("Encrypt data at rest and in transit")
    recommendations.append("Enable audit logging for all model interactions")
    recommendations.append("Conduct regular security assessments")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_decision_impact_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    decision_type = use_case.get("decision_type", "")
    industry = use_case.get("industry", "").lower()
    purpose = use_case.get("purpose", "").lower()

    base_impact = DECISION_IMPACT_MAP.get(decision_type, 1)
    score = base_impact * 2

    if decision_type in ["automated", "high_impact_automated"]:
        reasons.append(f"Decision type '{decision_type}' has significant individual impact")

    high_impact_keywords = [
        "approval", "rejection", "denial", "eligibility", "claim",
        "hiring", "termination", "loan", "credit", "insurance",
        "admission", "diagnosis", "treatment"
    ]
    for keyword in high_impact_keywords:
        if keyword in purpose:
            score = min(score + 1, 10)
            reasons.append(f"Purpose contains high-impact keyword: '{keyword}'")
            break

    if industry in SENSITIVE_INDUSTRIES:
        score = min(score + 1, 10)
        reasons.append(f"Industry '{industry}' involves high-stakes decisions")

    if score == 0:
        score = 1
        reasons.append("Decision impact assessment requires review")

    recommendations.append("Document decision impact on affected individuals")
    recommendations.append("Implement appeal and contest mechanisms")
    recommendations.append("Ensure decision transparency")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_regulatory_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    industry = use_case.get("industry", "").lower()
    decision_type = use_case.get("decision_type", "")
    data_types = use_case.get("data_types", [])

    if industry in ["insurance", "banking", "healthcare"]:
        score += 3
        reasons.append(f"Industry '{industry}' is heavily regulated")

    if decision_type in ["automated", "high_impact_automated"]:
        score += 2
        reasons.append("Automated decisions may trigger regulatory scrutiny")

    if "personal_data" in data_types:
        score += 2
        reasons.append("Personal data processing may require GDPR/privacy compliance")

    if "sensitive_data" in data_types:
        score += 1
        reasons.append("Sensitive data may trigger additional regulatory requirements")

    if industry == "insurance" and decision_type in ["automated", "high_impact_automated"]:
        score += 1
        reasons.append("Insurance automated decisions face specific regulatory attention")

    if score == 0:
        score = 1
        reasons.append("General regulatory landscape should be assessed")

    recommendations.append("Conduct regulatory mapping for applicable jurisdictions")
    recommendations.append("Document compliance with applicable AI regulations")
    recommendations.append("Monitor regulatory changes affecting AI deployment")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_model_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    model_type = use_case.get("model_type", "")
    decision_type = use_case.get("decision_type", "")

    if model_type == "generative_ai":
        score += 3
        reasons.append("Generative AI models have higher uncertainty and hallucination risk")
        recommendations.append("Implement output validation and fact-checking")
    elif model_type in ["classification", "regression"]:
        score += 2
        reasons.append("Traditional ML models require validation and monitoring")
    elif model_type == "recommendation":
        score += 2
        reasons.append("Recommendation systems may amplify existing biases")

    if decision_type in ["automated", "high_impact_automated"]:
        score += 2
        reasons.append("Model errors in automated decisions have higher consequences")

    if score == 0:
        score = 1
        reasons.append("Model risk baseline assessment recommended")

    recommendations.append("Implement model validation and testing")
    recommendations.append("Monitor model performance and drift")
    recommendations.append("Maintain model documentation and versioning")
    recommendations.append("Establish model approval process")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_monitoring_risk(use_case: Dict) -> Tuple[float, str, str, List[str]]:
    score = 0
    reasons = []
    recommendations = []
    deployment_status = use_case.get("deployment_status", "").lower()

    score += 2
    reasons.append("All AI systems require monitoring controls")

    if deployment_status in ["production", "deployed"]:
        score += 2
        reasons.append("Production systems require active monitoring")
    elif deployment_status in ["planning", "development"]:
        score += 1
        reasons.append("Monitoring plans should be established before deployment")

    decision_type = use_case.get("decision_type", "")
    if decision_type in ["automated", "high_impact_automated"]:
        score += 2
        reasons.append("Automated decision systems require comprehensive monitoring")

    if score == 0:
        score = 1
        reasons.append("Monitoring framework should be established")

    recommendations.append("Implement accuracy and performance monitoring")
    recommendations.append("Monitor for data and concept drift")
    recommendations.append("Track fairness metrics over time")
    recommendations.append("Log and monitor human override rates")
    recommendations.append("Establish incident response procedures")

    score = min(score, 10)
    return score, "; ".join(reasons), "; ".join(recommendations), recommendations


def calculate_risk_level(score: float) -> str:
    if score <= 2.9:
        return "LOW"
    elif score <= 4.9:
        return "MODERATE"
    elif score <= 6.9:
        return "HIGH"
    elif score <= 8.4:
        return "VERY HIGH"
    else:
        return "CRITICAL"


def assess_use_case(use_case: Dict) -> Dict[str, Any]:
    dimensions = {}

    calculators = {
        "data": calculate_data_risk,
        "privacy": calculate_privacy_risk,
        "fairness": calculate_fairness_risk,
        "human_oversight": calculate_human_oversight_risk,
        "explainability": calculate_explainability_risk,
        "security": calculate_security_risk,
        "decision_impact": calculate_decision_impact_risk,
        "regulatory": calculate_regulatory_risk,
        "model_risk": calculate_model_risk,
        "monitoring": calculate_monitoring_risk,
    }

    for dim_name, calculator in calculators.items():
        score, reason, recommendation, controls = calculator(use_case)
        dimensions[dim_name] = {
            "score": score,
            "weight": DIMENSION_WEIGHTS[dim_name],
            "reason": reason,
            "recommendation": recommendation,
            "controls": controls,
        }

    overall_score = sum(
        dim["score"] * dim["weight"] for dim in dimensions.values()
    )

    risk_level = calculate_risk_level(overall_score)

    confidence = calculate_confidence(use_case)

    if risk_level == "CRITICAL" and overall_score < 8.5:
        risk_level = "VERY HIGH"

    return {
        "overall_score": round(overall_score, 1),
        "risk_level": risk_level,
        "confidence": confidence,
        "dimensions": dimensions,
    }


def calculate_confidence(use_case: Dict) -> float:
    total_fields = 9
    filled_fields = 0

    if use_case.get("name"):
        filled_fields += 1
    if use_case.get("industry"):
        filled_fields += 1
    if use_case.get("purpose"):
        filled_fields += 1
    if use_case.get("ai_capability"):
        filled_fields += 1
    if use_case.get("data_types") and len(use_case.get("data_types", [])) > 0:
        filled_fields += 1
    if use_case.get("decision_type"):
        filled_fields += 1
    if use_case.get("human_oversight"):
        filled_fields += 1
    if use_case.get("model_type"):
        filled_fields += 1
    if use_case.get("affected_population", 0) > 0:
        filled_fields += 1

    return round((filled_fields / total_fields) * 100, 1)
