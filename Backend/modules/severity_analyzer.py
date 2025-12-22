"""
Feature 5: Severity Analysis Module
Assesses how serious the skin condition appears

Purpose: Evaluate severity based on disease type, confidence, and symptoms
"""

from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disease severity profiles
# Baseline severity and escalation conditions for each disease
DISEASE_SEVERITY_BASE = {
    "Actinic keratoses": {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": ["bleeding", "rapid_growth", "multiple_lesions", "large_area"],
        "description": "Pre-cancerous skin condition that requires monitoring"
    },
    "Basal cell carcinoma": {
        "baseline": "severe",
        "can_escalate_to": "critical",
        "severe_if": ["rapid_growth", "large_size", "ulceration", "pain"],
        "description": "Skin cancer that requires medical treatment"
    },
    "Benign keratosis-like lesions": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["rapid_change", "bleeding", "irregular_border"],
        "description": "Non-cancerous growth, usually harmless"
    },
    "Dermatofibroma": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["rapid_growth", "pain", "bleeding"],
        "description": "Benign skin nodule, typically harmless"
    },
    "Melanoma": {
        "baseline": "critical",
        "can_escalate_to": "critical",
        "severe_if": ["rapid_growth", "ulceration", "satellite_lesions", "pain"],
        "description": "Serious skin cancer requiring immediate medical attention"
    },
    "Melanocytic nevi": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["changing_shape", "irregular_border", "color_change", "rapid_growth"],
        "description": "Common mole, usually benign"
    },
    "Vascular lesions": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["rapid_growth", "bleeding", "pain", "ulceration"],
        "description": "Blood vessel-related skin condition"
    }
}

# Severity level ordering (for escalation)
SEVERITY_ORDER = ["mild", "moderate", "severe", "critical"]

# Intensity keywords that indicate severity
INTENSITY_KEYWORDS = {
    "high": ["very", "extremely", "severe", "intense", "unbearable", "constant"],
    "moderate": ["moderate", "noticeable", "persistent", "frequent"],
    "low": ["mild", "slight", "occasional", "minor"]
}

# Area keywords that indicate spread
AREA_KEYWORDS = ["widespread", "large", "spreading", "multiple", "extensive", "whole", "entire"]


def _get_severity_index(level: str) -> int:
    """Get numerical index for severity level"""
    try:
        return SEVERITY_ORDER.index(level.lower())
    except ValueError:
        return 0


def _escalate_severity(current: str, steps: int = 1) -> str:
    """Escalate severity by given steps"""
    current_idx = _get_severity_index(current)
    new_idx = min(current_idx + steps, len(SEVERITY_ORDER) - 1)
    return SEVERITY_ORDER[new_idx]


def _check_intensity_keywords(symptoms: List[str]) -> int:
    """
    Check for intensity keywords in symptoms.
    Returns escalation steps (0-2)
    """
    symptom_text = " ".join(symptoms).lower()
    
    for keyword in INTENSITY_KEYWORDS["high"]:
        if keyword in symptom_text:
            return 2
    
    for keyword in INTENSITY_KEYWORDS["moderate"]:
        if keyword in symptom_text:
            return 1
    
    return 0


def _check_area_keywords(symptoms: List[str]) -> int:
    """
    Check for area/spread keywords in symptoms.
    Returns escalation steps (0-1)
    """
    symptom_text = " ".join(symptoms).lower()
    
    for keyword in AREA_KEYWORDS:
        if keyword in symptom_text:
            return 1
    
    return 0


def _check_severe_indicators(disease: str, symptoms: List[str]) -> int:
    """
    Check if symptoms contain severe indicators for the disease.
    Returns escalation steps (0-2)
    """
    profile = DISEASE_SEVERITY_BASE.get(disease, {})
    severe_indicators = profile.get("severe_if", [])
    
    if not severe_indicators or not symptoms:
        return 0
    
    # Normalize symptoms for comparison
    normalized_symptoms = [s.lower().replace(" ", "_") for s in symptoms]
    
    matches = 0
    for indicator in severe_indicators:
        indicator_lower = indicator.lower()
        for symptom in normalized_symptoms:
            if indicator_lower in symptom or symptom in indicator_lower:
                matches += 1
                break
    
    if matches >= 3:
        return 2
    elif matches >= 1:
        return 1
    
    return 0


def get_urgency_level(disease: str, severity: str, symptoms: List[str]) -> Tuple[str, Optional[str]]:
    """
    Determine urgency level based on disease, severity, and symptoms.
    
    Returns:
        Tuple of (urgency_level, warning_message)
        
    Urgency levels:
    - "routine": Normal care, no rush
    - "consult_doctor": Should see a doctor soon
    - "seek_attention": Seek medical attention within days
    - "immediate": Immediate medical attention required
    """
    # Red flags - immediate attention
    red_flag_diseases = ["Melanoma", "Basal cell carcinoma"]
    red_flag_symptoms = ["bleeding", "infection", "rapid_spread", "severe_pain", "ulceration"]
    
    symptom_text = " ".join(symptoms).lower() if symptoms else ""
    
    # Check for critical conditions
    if disease in red_flag_diseases and severity in ["severe", "critical"]:
        return "immediate", "This condition requires immediate medical evaluation."
    
    # Check for red flag symptoms
    for flag in red_flag_symptoms:
        if flag in symptom_text:
            if severity in ["severe", "critical"]:
                return "immediate", f"Symptom '{flag}' detected. Seek immediate medical attention."
            else:
                return "seek_attention", f"Concerning symptom detected. Please consult a doctor soon."
    
    # Severity-based urgency
    if severity == "critical":
        return "immediate", "Critical condition detected. Seek immediate medical attention."
    elif severity == "severe":
        return "seek_attention", "Condition appears serious. Please see a doctor soon."
    elif severity == "moderate":
        return "consult_doctor", "Consider consulting a healthcare provider."
    else:
        return "routine", None


def analyze_severity(
    disease: str,
    confidence: float,
    symptoms: List[str]
) -> Dict:
    """
    Analyze severity of the predicted condition.
    
    Multi-Factor Assessment considers:
    1. Model confidence score
    2. Predicted disease baseline severity
    3. User symptom intensity keywords
    4. Symptom count
    5. Presence of severe indicators
    
    Args:
        disease: Predicted disease name
        confidence: Model confidence score (0-1)
        symptoms: List of user-reported symptoms
    
    Returns:
        Dictionary with severity assessment:
        {
            "level": str ("mild", "moderate", "severe", "critical"),
            "urgency": str,
            "explanation": str,
            "factors": List[str]
        }
    """
    factors = []
    
    # Get disease profile
    profile = DISEASE_SEVERITY_BASE.get(disease, {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": [],
        "description": "Unknown condition"
    })
    
    # Start with baseline severity
    current_severity = profile.get("baseline", "moderate")
    max_severity = profile.get("can_escalate_to", "severe")
    factors.append(f"Baseline severity for {disease}: {current_severity}")
    
    # Factor 1: Check severe indicator symptoms
    severe_escalation = _check_severe_indicators(disease, symptoms)
    if severe_escalation > 0:
        current_severity = _escalate_severity(current_severity, severe_escalation)
        factors.append(f"Severe symptoms detected (+{severe_escalation} level)")
    
    # Factor 2: Check intensity keywords
    intensity_escalation = _check_intensity_keywords(symptoms)
    if intensity_escalation > 0:
        current_severity = _escalate_severity(current_severity, intensity_escalation)
        factors.append(f"High intensity symptoms (+{intensity_escalation} level)")
    
    # Factor 3: Check area/spread keywords
    area_escalation = _check_area_keywords(symptoms)
    if area_escalation > 0:
        current_severity = _escalate_severity(current_severity, area_escalation)
        factors.append(f"Widespread condition (+{area_escalation} level)")
    
    # Factor 4: Symptom count
    if len(symptoms) >= 5:
        current_severity = _escalate_severity(current_severity, 1)
        factors.append(f"Multiple symptoms reported ({len(symptoms)})")
    
    # Factor 5: Low confidence with severe symptoms
    if confidence < 0.6 and _get_severity_index(current_severity) >= 2:
        factors.append("Low confidence with severe symptoms - expert review recommended")
    
    # Cap at maximum severity for this disease
    max_idx = _get_severity_index(max_severity)
    current_idx = _get_severity_index(current_severity)
    if current_idx > max_idx:
        current_severity = max_severity
    
    # Get urgency level
    urgency, warning = get_urgency_level(disease, current_severity, symptoms)
    
    # Build explanation
    explanation = profile.get("description", "")
    if current_severity == "critical":
        explanation += " Immediate medical attention is strongly recommended."
    elif current_severity == "severe":
        explanation += " Please consult a healthcare provider soon."
    elif current_severity == "moderate":
        explanation += " Consider scheduling a medical consultation."
    else:
        explanation += " Monitor the condition and seek help if it worsens."
    
    return {
        "level": current_severity,
        "urgency": urgency,
        "explanation": explanation,
        "factors": factors,
        "warning": warning
    }


def get_severity_explanation(severity_level: str) -> str:
    """
    Get explanation text for a severity level.
    
    Args:
        severity_level: One of "mild", "moderate", "severe", "critical"
    
    Returns:
        Explanation string
    """
    explanations = {
        "mild": "The condition appears mild. Self-care may be sufficient, but monitor for changes.",
        "moderate": "The condition shows moderate severity. Consider consulting a healthcare provider.",
        "severe": "The condition appears serious. Please seek medical attention soon.",
        "critical": "This is a critical condition. Immediate medical attention is required."
    }
    
    return explanations.get(severity_level.lower(), "Unable to determine severity.")
