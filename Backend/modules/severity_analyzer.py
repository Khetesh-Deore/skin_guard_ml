"""
Feature 5: Severity Analysis Module
Assesses how serious the skin condition appears

Purpose: Evaluate severity based on disease type, confidence, and symptoms

Feature 5.1: Multi-Factor Severity Assessment
Factors to Consider:
1. Model confidence score
2. Predicted disease baseline severity
3. User symptom intensity keywords
4. Symptom count
5. Presence of severe indicators
"""

from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disease severity profiles
# Baseline severity and escalation conditions for each disease
# Complete database for all 22 Teachable Machine classes
DISEASE_SEVERITY_BASE = {
    # Class 0: Acne
    "Acne": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["cysts", "nodules", "widespread", "severe_scarring", "deep_lesions"],
        "description": "Common skin condition affecting hair follicles and oil glands"
    },
    
    # Class 1: Actinic Keratosis
    "Actinic Keratosis": {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": ["bleeding", "rapid_growth", "multiple_lesions", "large_area", "hardening"],
        "description": "Pre-cancerous skin condition caused by sun damage that requires monitoring"
    },
    
    # Class 2: Benign Tumors
    "Benign Tumors": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["rapid_growth", "pain", "size_increase", "skin_changes"],
        "description": "Non-cancerous growth that is usually harmless but should be monitored"
    },
    
    # Class 3: Bullous (Blistering diseases)
    "Bullous": {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": ["widespread_blisters", "mouth_sores", "infection_signs", "fever", "large_area"],
        "description": "Blistering skin condition that may require medical treatment"
    },
    
    # Class 4: Candidiasis
    "Candidiasis": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["spreading", "severe_itching", "infection_signs", "fever", "widespread"],
        "description": "Fungal infection that typically responds well to treatment"
    },
    
    # Class 5: Drug Eruption
    "Drug Eruption": {
        "baseline": "moderate",
        "can_escalate_to": "critical",
        "severe_if": ["mouth_sores", "eye_involvement", "severe_peeling", "fever", "breathing_difficulty"],
        "description": "Skin reaction to medication - may require immediate medical attention"
    },
    
    # Class 6: Eczema
    "Eczema": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["bleeding", "infection_signs", "large_area", "sleep_disruption", "severe_itching"],
        "description": "Chronic inflammatory skin condition that can be managed with proper care"
    },
    
    # Class 7: Infestations/Bites
    "Infestations/Bites": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["severe_itching", "infection_signs", "spreading", "allergic_reaction", "fever"],
        "description": "Skin reaction to insect bites or infestations"
    },
    
    # Class 8: Lichen
    "Lichen": {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": ["widespread", "severe_itching", "scarring", "nail_damage", "mouth_ulcers"],
        "description": "Inflammatory condition affecting skin, nails, or mucous membranes"
    },
    
    # Class 9: Lupus
    "Lupus": {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": ["widespread_rash", "kidney_problems", "severe_fatigue", "chest_pain", "fever"],
        "description": "Autoimmune condition that can affect skin and other organs"
    },
    
    # Class 10: Moles
    "Moles": {
        "baseline": "mild",
        "can_escalate_to": "severe",
        "severe_if": ["changing_shape", "irregular_border", "color_change", "bleeding", "rapid_growth"],
        "description": "Common skin growth - monitor for changes using ABCDE criteria"
    },
    
    # Class 11: Psoriasis
    "Psoriasis": {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": ["widespread", "joint_swelling", "severe_scaling", "bleeding", "large_area"],
        "description": "Chronic autoimmune condition causing rapid skin cell buildup"
    },
    
    # Class 12: Rosacea
    "Rosacea": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["nose_enlargement", "severe_redness", "eye_problems", "thickened_skin", "persistent_flushing"],
        "description": "Chronic facial skin condition causing redness and visible blood vessels"
    },
    
    # Class 13: Seborrheic Keratoses
    "Seborrheic Keratoses": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["rapid_change", "bleeding", "irregular_border", "pain", "inflammation"],
        "description": "Common benign skin growth, typically harmless"
    },
    
    # Class 14: Skin Cancer
    "Skin Cancer": {
        "baseline": "severe",
        "can_escalate_to": "critical",
        "severe_if": ["rapid_growth", "spreading", "satellite_lesions", "lymph_node_swelling", "ulceration"],
        "description": "Malignant skin condition requiring immediate medical evaluation"
    },
    
    # Class 15: Sun/Sunlight Damage
    "Sun/Sunlight Damage": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["severe_blistering", "fever", "chills", "nausea", "widespread_damage"],
        "description": "Skin damage from UV exposure - protect from further sun exposure"
    },
    
    # Class 16: Tinea (Fungal infections)
    "Tinea": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["spreading", "severe_itching", "infection_signs", "widespread", "nail_involvement"],
        "description": "Fungal skin infection that responds well to antifungal treatment"
    },
    
    # Class 17: Unknown/Normal
    "Unknown/Normal": {
        "baseline": "mild",
        "can_escalate_to": "mild",
        "severe_if": [],
        "description": "Skin appears normal or condition is unidentified"
    },
    
    # Class 18: Vascular Tumors
    "Vascular Tumors": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["rapid_growth", "bleeding", "pain", "ulceration", "large_size"],
        "description": "Blood vessel-related growth, usually benign"
    },
    
    # Class 19: Vasculitis
    "Vasculitis": {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": ["widespread", "organ_involvement", "severe_ulcers", "fever", "kidney_problems"],
        "description": "Inflammation of blood vessels that may require medical treatment"
    },
    
    # Class 20: Vitiligo
    "Vitiligo": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["spreading", "widespread", "rapid_progression", "facial_involvement"],
        "description": "Autoimmune condition causing loss of skin pigmentation"
    },
    
    # Class 21: Warts
    "Warts": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": ["spreading", "large_size", "bleeding", "rapid_growth", "genital_area"],
        "description": "Viral skin growth caused by HPV, usually harmless"
    },
    
    # Legacy mappings for HAM10000 dataset compatibility
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

# Severity level scores for numerical calculations
SEVERITY_SCORES = {
    "mild": 1,
    "moderate": 2,
    "severe": 3,
    "critical": 4
}

# Intensity keywords that indicate severity
INTENSITY_KEYWORDS = {
    "high": ["very", "extremely", "severe", "intense", "unbearable", "constant", 
             "excruciating", "terrible", "awful", "worst", "agonizing"],
    "moderate": ["moderate", "noticeable", "persistent", "frequent", "considerable",
                 "significant", "bothersome", "uncomfortable"],
    "low": ["mild", "slight", "occasional", "minor", "barely", "little", "faint"]
}

# Area keywords that indicate spread
AREA_KEYWORDS = ["widespread", "large", "spreading", "multiple", "extensive", 
                 "whole", "entire", "all_over", "everywhere", "covering"]

# Duration keywords that indicate chronicity
DURATION_KEYWORDS = {
    "acute": ["sudden", "new", "recent", "just_started", "appeared_today"],
    "chronic": ["long_time", "months", "years", "persistent", "recurring", "chronic", "ongoing"]
}

# Red flag symptoms requiring immediate attention
RED_FLAG_SYMPTOMS = [
    "bleeding", "infection", "rapid_spread", "severe_pain", "ulceration",
    "breathing_difficulty", "fever", "mouth_sores", "eye_involvement",
    "swollen_lymph_nodes", "chest_pain", "difficulty_swallowing"
]

# Factor weights for multi-factor assessment
FACTOR_WEIGHTS = {
    "baseline_severity": 0.25,      # Disease baseline
    "confidence_score": 0.15,       # Model confidence
    "symptom_intensity": 0.20,      # Intensity keywords
    "symptom_count": 0.15,          # Number of symptoms
    "severe_indicators": 0.25       # Presence of severe indicators
}


def _get_severity_index(level: str) -> int:
    """Get numerical index for severity level"""
    try:
        return SEVERITY_ORDER.index(level.lower())
    except ValueError:
        return 0


def _get_severity_score(level: str) -> int:
    """Get numerical score for severity level"""
    return SEVERITY_SCORES.get(level.lower(), 1)


def _escalate_severity(current: str, steps: int = 1) -> str:
    """Escalate severity by given steps"""
    current_idx = _get_severity_index(current)
    new_idx = min(current_idx + steps, len(SEVERITY_ORDER) - 1)
    return SEVERITY_ORDER[new_idx]


def _score_to_severity(score: float) -> str:
    """Convert numerical score to severity level"""
    if score >= 3.5:
        return "critical"
    elif score >= 2.5:
        return "severe"
    elif score >= 1.5:
        return "moderate"
    else:
        return "mild"


# =============================================================================
# Feature 5.1: Multi-Factor Severity Assessment Functions
# =============================================================================

def assess_factor_1_baseline_severity(disease: str) -> Tuple[float, str]:
    """
    Factor 1: Predicted disease baseline severity
    
    Args:
        disease: Predicted disease name
    
    Returns:
        Tuple of (score 1-4, explanation)
    """
    profile = DISEASE_SEVERITY_BASE.get(disease, {"baseline": "moderate"})
    baseline = profile.get("baseline", "moderate")
    score = _get_severity_score(baseline)
    
    explanation = f"Disease baseline: {baseline} ({score}/4)"
    return score, explanation


def assess_factor_2_confidence_score(confidence: float, baseline_severity: str) -> Tuple[float, str]:
    """
    Factor 2: Model confidence score impact
    
    High confidence with severe disease = higher severity
    Low confidence = uncertainty, may need review
    
    Args:
        confidence: Model confidence (0-1)
        baseline_severity: Disease baseline severity
    
    Returns:
        Tuple of (adjustment -1 to +1, explanation)
    """
    baseline_score = _get_severity_score(baseline_severity)
    
    if confidence >= 0.9:
        # Very high confidence - trust the baseline
        if baseline_score >= 3:
            adjustment = 0.5  # Increase severity for serious conditions
            explanation = f"High confidence ({confidence:.0%}) confirms serious condition"
        else:
            adjustment = 0
            explanation = f"High confidence ({confidence:.0%}) in diagnosis"
    elif confidence >= 0.7:
        adjustment = 0
        explanation = f"Good confidence ({confidence:.0%}) in diagnosis"
    elif confidence >= 0.5:
        adjustment = 0
        explanation = f"Moderate confidence ({confidence:.0%}) - consider professional evaluation"
    else:
        # Low confidence - recommend review regardless
        adjustment = 0.5  # Slight increase due to uncertainty
        explanation = f"Low confidence ({confidence:.0%}) - professional evaluation recommended"
    
    return adjustment, explanation


def assess_factor_3_symptom_intensity(symptoms: List[str]) -> Tuple[float, str, str]:
    """
    Factor 3: User symptom intensity keywords
    
    Detects intensity modifiers like "very", "extremely", "severe"
    
    Args:
        symptoms: List of user-reported symptoms
    
    Returns:
        Tuple of (score 0-2, intensity_level, explanation)
    """
    if not symptoms:
        return 0, "none", "No symptoms provided"
    
    symptom_text = " ".join(symptoms).lower()
    
    # Check for high intensity keywords
    high_count = sum(1 for kw in INTENSITY_KEYWORDS["high"] if kw in symptom_text)
    moderate_count = sum(1 for kw in INTENSITY_KEYWORDS["moderate"] if kw in symptom_text)
    low_count = sum(1 for kw in INTENSITY_KEYWORDS["low"] if kw in symptom_text)
    
    if high_count >= 2:
        return 2.0, "high", f"Multiple high-intensity descriptors detected ({high_count})"
    elif high_count >= 1:
        return 1.5, "high", "High-intensity symptoms reported"
    elif moderate_count >= 2:
        return 1.0, "moderate", f"Moderate intensity symptoms ({moderate_count} descriptors)"
    elif moderate_count >= 1:
        return 0.5, "moderate", "Moderate intensity symptoms"
    elif low_count >= 1:
        return 0, "low", "Mild intensity symptoms reported"
    else:
        return 0.5, "normal", "Normal symptom intensity"


def assess_factor_4_symptom_count(symptoms: List[str]) -> Tuple[float, str]:
    """
    Factor 4: Symptom count assessment
    
    More symptoms generally indicate more serious condition
    
    Args:
        symptoms: List of user-reported symptoms
    
    Returns:
        Tuple of (score 0-2, explanation)
    """
    count = len(symptoms) if symptoms else 0
    
    if count == 0:
        return 0, "No symptoms reported"
    elif count <= 2:
        return 0, f"Few symptoms ({count}) - likely localized condition"
    elif count <= 4:
        return 0.5, f"Several symptoms ({count}) - moderate involvement"
    elif count <= 6:
        return 1.0, f"Multiple symptoms ({count}) - significant involvement"
    else:
        return 1.5, f"Many symptoms ({count}) - extensive involvement"


def assess_factor_5_severe_indicators(disease: str, symptoms: List[str]) -> Tuple[float, List[str], str]:
    """
    Factor 5: Presence of severe indicators
    
    Checks for disease-specific severe indicators and red flag symptoms
    
    Args:
        disease: Predicted disease name
        symptoms: List of user-reported symptoms
    
    Returns:
        Tuple of (score 0-3, matched_indicators, explanation)
    """
    if not symptoms:
        return 0, [], "No symptoms to evaluate"
    
    profile = DISEASE_SEVERITY_BASE.get(disease, {})
    severe_indicators = profile.get("severe_if", [])
    
    # Normalize symptoms for comparison
    normalized_symptoms = [s.lower().replace(" ", "_") for s in symptoms]
    symptom_text = " ".join(normalized_symptoms)
    
    # Check disease-specific severe indicators
    matched_disease_indicators = []
    for indicator in severe_indicators:
        indicator_lower = indicator.lower()
        if indicator_lower in symptom_text:
            matched_disease_indicators.append(indicator)
    
    # Check red flag symptoms
    matched_red_flags = []
    for flag in RED_FLAG_SYMPTOMS:
        if flag in symptom_text:
            matched_red_flags.append(flag)
    
    all_matched = list(set(matched_disease_indicators + matched_red_flags))
    
    # Calculate score
    if matched_red_flags:
        score = 2.5 + min(len(matched_red_flags) * 0.5, 1.5)  # Max 4
        explanation = f"RED FLAG symptoms detected: {', '.join(matched_red_flags)}"
    elif len(matched_disease_indicators) >= 3:
        score = 2.0
        explanation = f"Multiple severe indicators ({len(matched_disease_indicators)})"
    elif len(matched_disease_indicators) >= 2:
        score = 1.5
        explanation = f"Several severe indicators detected"
    elif len(matched_disease_indicators) >= 1:
        score = 1.0
        explanation = f"Severe indicator present: {matched_disease_indicators[0]}"
    else:
        score = 0
        explanation = "No severe indicators detected"
    
    return score, all_matched, explanation


def assess_area_spread(symptoms: List[str]) -> Tuple[float, str]:
    """
    Additional factor: Area/spread assessment
    
    Args:
        symptoms: List of user-reported symptoms
    
    Returns:
        Tuple of (score 0-1, explanation)
    """
    if not symptoms:
        return 0, "No area information"
    
    symptom_text = " ".join(symptoms).lower()
    
    spread_count = sum(1 for kw in AREA_KEYWORDS if kw in symptom_text)
    
    if spread_count >= 2:
        return 1.0, "Widespread/extensive condition"
    elif spread_count >= 1:
        return 0.5, "Some spreading noted"
    else:
        return 0, "Localized condition"


def assess_duration(symptoms: List[str]) -> Tuple[str, str]:
    """
    Additional factor: Duration assessment
    
    Args:
        symptoms: List of user-reported symptoms
    
    Returns:
        Tuple of (duration_type, explanation)
    """
    if not symptoms:
        return "unknown", "Duration unknown"
    
    symptom_text = " ".join(symptoms).lower()
    
    for kw in DURATION_KEYWORDS["acute"]:
        if kw in symptom_text:
            return "acute", "Recent/sudden onset"
    
    for kw in DURATION_KEYWORDS["chronic"]:
        if kw in symptom_text:
            return "chronic", "Long-standing/chronic condition"
    
    return "unknown", "Duration not specified"


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
    # Red flags - immediate attention (cancer-related)
    red_flag_diseases = ["Melanoma", "Skin Cancer", "Basal cell carcinoma"]
    
    # Yellow flags - seek attention soon
    yellow_flag_diseases = ["Drug Eruption", "Bullous", "Vasculitis", "Lupus", "Actinic Keratosis"]
    
    # Red flag symptoms
    red_flag_symptoms = ["bleeding", "infection", "rapid_spread", "severe_pain", "ulceration", 
                         "breathing_difficulty", "fever", "mouth_sores", "eye_involvement"]
    
    symptom_text = " ".join(symptoms).lower() if symptoms else ""
    
    # Check for critical conditions (cancer)
    if disease in red_flag_diseases:
        if severity in ["severe", "critical"]:
            return "immediate", f"{disease} detected with high confidence. Seek immediate medical evaluation."
        else:
            return "seek_attention", f"{disease} suspected. Please consult a dermatologist promptly."
    
    # Check for yellow flag diseases
    if disease in yellow_flag_diseases and severity in ["moderate", "severe", "critical"]:
        return "seek_attention", f"{disease} may require medical treatment. Please see a doctor soon."
    
    # Check for red flag symptoms
    for flag in red_flag_symptoms:
        if flag in symptom_text:
            if severity in ["severe", "critical"]:
                return "immediate", f"Concerning symptom '{flag}' detected. Seek immediate medical attention."
            elif severity == "moderate":
                return "seek_attention", f"Symptom '{flag}' detected. Please consult a doctor soon."
            else:
                return "consult_doctor", f"Symptom '{flag}' noted. Consider consulting a healthcare provider."
    
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
    
    Feature 5.1: Multi-Factor Severity Assessment
    
    Factors Considered:
    1. Model confidence score (15% weight)
    2. Predicted disease baseline severity (25% weight)
    3. User symptom intensity keywords (20% weight)
    4. Symptom count (15% weight)
    5. Presence of severe indicators (25% weight)
    
    Args:
        disease: Predicted disease name
        confidence: Model confidence score (0-1)
        symptoms: List of user-reported symptoms
    
    Returns:
        Dictionary with comprehensive severity assessment:
        {
            "level": str ("mild", "moderate", "severe", "critical"),
            "urgency": str,
            "explanation": str,
            "factors": List[str],
            "warning": Optional[str],
            "score": float,
            "factor_breakdown": Dict
        }
    """
    factors = []
    factor_breakdown = {}
    
    # Get disease profile
    profile = DISEASE_SEVERITY_BASE.get(disease, {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": [],
        "description": "Unknown condition"
    })
    
    # ==========================================================================
    # Factor 1: Disease Baseline Severity (25% weight)
    # ==========================================================================
    baseline_score, baseline_explanation = assess_factor_1_baseline_severity(disease)
    factors.append(f"[Factor 1] {baseline_explanation}")
    factor_breakdown["baseline_severity"] = {
        "score": baseline_score,
        "max_score": 4,
        "weight": FACTOR_WEIGHTS["baseline_severity"],
        "weighted_score": baseline_score * FACTOR_WEIGHTS["baseline_severity"],
        "explanation": baseline_explanation
    }
    
    # ==========================================================================
    # Factor 2: Model Confidence Score (15% weight)
    # ==========================================================================
    baseline_level = profile.get("baseline", "moderate")
    confidence_adjustment, confidence_explanation = assess_factor_2_confidence_score(
        confidence, baseline_level
    )
    factors.append(f"[Factor 2] {confidence_explanation}")
    factor_breakdown["confidence_score"] = {
        "score": confidence,
        "adjustment": confidence_adjustment,
        "weight": FACTOR_WEIGHTS["confidence_score"],
        "explanation": confidence_explanation
    }
    
    # ==========================================================================
    # Factor 3: Symptom Intensity Keywords (20% weight)
    # ==========================================================================
    intensity_score, intensity_level, intensity_explanation = assess_factor_3_symptom_intensity(
        symptoms
    )
    factors.append(f"[Factor 3] {intensity_explanation}")
    factor_breakdown["symptom_intensity"] = {
        "score": intensity_score,
        "max_score": 2,
        "level": intensity_level,
        "weight": FACTOR_WEIGHTS["symptom_intensity"],
        "weighted_score": intensity_score * FACTOR_WEIGHTS["symptom_intensity"],
        "explanation": intensity_explanation
    }
    
    # ==========================================================================
    # Factor 4: Symptom Count (15% weight)
    # ==========================================================================
    count_score, count_explanation = assess_factor_4_symptom_count(symptoms)
    factors.append(f"[Factor 4] {count_explanation}")
    factor_breakdown["symptom_count"] = {
        "score": count_score,
        "max_score": 1.5,
        "count": len(symptoms) if symptoms else 0,
        "weight": FACTOR_WEIGHTS["symptom_count"],
        "weighted_score": count_score * FACTOR_WEIGHTS["symptom_count"],
        "explanation": count_explanation
    }
    
    # ==========================================================================
    # Factor 5: Severe Indicators (25% weight)
    # ==========================================================================
    indicator_score, matched_indicators, indicator_explanation = assess_factor_5_severe_indicators(
        disease, symptoms
    )
    factors.append(f"[Factor 5] {indicator_explanation}")
    factor_breakdown["severe_indicators"] = {
        "score": indicator_score,
        "max_score": 4,
        "matched": matched_indicators,
        "weight": FACTOR_WEIGHTS["severe_indicators"],
        "weighted_score": indicator_score * FACTOR_WEIGHTS["severe_indicators"],
        "explanation": indicator_explanation
    }
    
    # ==========================================================================
    # Additional Factors (informational)
    # ==========================================================================
    area_score, area_explanation = assess_area_spread(symptoms)
    duration_type, duration_explanation = assess_duration(symptoms)
    
    factor_breakdown["area_spread"] = {
        "score": area_score,
        "explanation": area_explanation
    }
    factor_breakdown["duration"] = {
        "type": duration_type,
        "explanation": duration_explanation
    }
    
    # ==========================================================================
    # Calculate Final Severity Score
    # ==========================================================================
    
    # Weighted score calculation
    weighted_total = (
        baseline_score * FACTOR_WEIGHTS["baseline_severity"] +
        intensity_score * FACTOR_WEIGHTS["symptom_intensity"] +
        count_score * FACTOR_WEIGHTS["symptom_count"] +
        indicator_score * FACTOR_WEIGHTS["severe_indicators"]
    )
    
    # Add confidence adjustment
    weighted_total += confidence_adjustment
    
    # Add area spread bonus
    weighted_total += area_score * 0.1
    
    # Normalize to 1-4 scale
    final_score = max(1, min(4, weighted_total + 1))
    
    # Convert score to severity level
    current_severity = _score_to_severity(final_score)
    
    # Cap at maximum severity for this disease (unless red flags present)
    max_severity = profile.get("can_escalate_to", "severe")
    has_red_flags = any(flag in " ".join(symptoms).lower() for flag in RED_FLAG_SYMPTOMS) if symptoms else False
    
    if not has_red_flags:
        max_idx = _get_severity_index(max_severity)
        current_idx = _get_severity_index(current_severity)
        if current_idx > max_idx:
            current_severity = max_severity
            factors.append(f"Severity capped at {max_severity} for {disease}")
    
    # ==========================================================================
    # Determine Urgency Level
    # ==========================================================================
    urgency, warning = get_urgency_level(disease, current_severity, symptoms)
    
    # ==========================================================================
    # Build Explanation
    # ==========================================================================
    explanation = profile.get("description", "")
    
    if current_severity == "critical":
        explanation += " Immediate medical attention is strongly recommended."
    elif current_severity == "severe":
        explanation += " Please consult a healthcare provider soon."
    elif current_severity == "moderate":
        explanation += " Consider scheduling a medical consultation."
    else:
        explanation += " Monitor the condition and seek help if it worsens."
    
    # Add duration context
    if duration_type == "chronic":
        explanation += " The chronic nature may require ongoing management."
    elif duration_type == "acute":
        explanation += " Recent onset - monitor for changes."
    
    return {
        "level": current_severity,
        "urgency": urgency,
        "explanation": explanation,
        "factors": factors,
        "warning": warning,
        "score": round(final_score, 2),
        "factor_breakdown": factor_breakdown,
        "has_red_flags": has_red_flags,
        "matched_severe_indicators": matched_indicators
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


# =============================================================================
# Additional Severity Analysis Functions
# =============================================================================

def get_disease_risk_level(disease: str) -> Dict:
    """
    Get the inherent risk level for a disease.
    
    Args:
        disease: Disease name
    
    Returns:
        Dictionary with risk information
    """
    profile = DISEASE_SEVERITY_BASE.get(disease, {})
    
    baseline = profile.get("baseline", "moderate")
    can_escalate = profile.get("can_escalate_to", "severe")
    severe_indicators = profile.get("severe_if", [])
    
    # Determine risk category
    if baseline == "critical" or can_escalate == "critical":
        risk_category = "high"
        risk_message = "This condition has high inherent risk and requires medical attention."
    elif baseline == "severe" or can_escalate == "severe":
        risk_category = "moderate-high"
        risk_message = "This condition can become serious and should be monitored closely."
    elif baseline == "moderate":
        risk_category = "moderate"
        risk_message = "This condition has moderate risk and may benefit from medical evaluation."
    else:
        risk_category = "low"
        risk_message = "This condition is generally low risk but should be monitored."
    
    return {
        "disease": disease,
        "baseline_severity": baseline,
        "max_severity": can_escalate,
        "risk_category": risk_category,
        "risk_message": risk_message,
        "severe_indicators": severe_indicators,
        "indicator_count": len(severe_indicators)
    }


def compare_severity_factors(
    disease: str,
    confidence: float,
    symptoms: List[str]
) -> Dict:
    """
    Get a detailed comparison of all severity factors.
    
    Args:
        disease: Predicted disease name
        confidence: Model confidence score
        symptoms: List of symptoms
    
    Returns:
        Dictionary with factor comparison
    """
    # Assess each factor
    f1_score, f1_exp = assess_factor_1_baseline_severity(disease)
    
    profile = DISEASE_SEVERITY_BASE.get(disease, {"baseline": "moderate"})
    f2_adj, f2_exp = assess_factor_2_confidence_score(confidence, profile.get("baseline", "moderate"))
    
    f3_score, f3_level, f3_exp = assess_factor_3_symptom_intensity(symptoms)
    f4_score, f4_exp = assess_factor_4_symptom_count(symptoms)
    f5_score, f5_matched, f5_exp = assess_factor_5_severe_indicators(disease, symptoms)
    
    area_score, area_exp = assess_area_spread(symptoms)
    duration_type, duration_exp = assess_duration(symptoms)
    
    return {
        "factors": {
            "baseline_severity": {"score": f1_score, "max": 4, "explanation": f1_exp},
            "confidence_impact": {"adjustment": f2_adj, "explanation": f2_exp},
            "symptom_intensity": {"score": f3_score, "max": 2, "level": f3_level, "explanation": f3_exp},
            "symptom_count": {"score": f4_score, "max": 1.5, "explanation": f4_exp},
            "severe_indicators": {"score": f5_score, "max": 4, "matched": f5_matched, "explanation": f5_exp},
        },
        "additional": {
            "area_spread": {"score": area_score, "explanation": area_exp},
            "duration": {"type": duration_type, "explanation": duration_exp}
        },
        "summary": {
            "highest_factor": max(
                [("baseline", f1_score), ("intensity", f3_score), 
                 ("count", f4_score), ("indicators", f5_score)],
                key=lambda x: x[1]
            )[0],
            "total_factors_elevated": sum([
                1 if f1_score >= 3 else 0,
                1 if f3_score >= 1.5 else 0,
                1 if f4_score >= 1 else 0,
                1 if f5_score >= 2 else 0
            ])
        }
    }


def get_severity_recommendations(severity_level: str, urgency: str) -> Dict:
    """
    Get specific recommendations based on severity and urgency.
    
    Args:
        severity_level: Current severity level
        urgency: Current urgency level
    
    Returns:
        Dictionary with recommendations
    """
    recommendations = {
        "critical": {
            "immediate_actions": [
                "Seek emergency medical care immediately",
                "Do not delay treatment",
                "Call emergency services if symptoms worsen"
            ],
            "timeframe": "Immediately (within hours)",
            "care_level": "Emergency/Urgent Care"
        },
        "severe": {
            "immediate_actions": [
                "Schedule urgent appointment with dermatologist",
                "Document symptoms and changes",
                "Avoid irritating the affected area"
            ],
            "timeframe": "Within 24-48 hours",
            "care_level": "Specialist Care"
        },
        "moderate": {
            "immediate_actions": [
                "Schedule appointment with healthcare provider",
                "Monitor for worsening symptoms",
                "Begin gentle skincare routine"
            ],
            "timeframe": "Within 1-2 weeks",
            "care_level": "Primary Care/Dermatologist"
        },
        "mild": {
            "immediate_actions": [
                "Monitor the condition",
                "Try over-the-counter treatments if appropriate",
                "Maintain good skincare hygiene"
            ],
            "timeframe": "As needed, or if condition worsens",
            "care_level": "Self-care with monitoring"
        }
    }
    
    urgency_additions = {
        "immediate": "⚠️ URGENT: Do not delay seeking medical attention.",
        "seek_attention": "Please see a healthcare provider soon.",
        "consult_doctor": "Consider scheduling a medical consultation.",
        "routine": "Continue monitoring and maintain good skincare."
    }
    
    base_recs = recommendations.get(severity_level, recommendations["moderate"])
    
    return {
        **base_recs,
        "urgency_note": urgency_additions.get(urgency, ""),
        "severity_level": severity_level,
        "urgency_level": urgency
    }


def calculate_risk_score(
    disease: str,
    confidence: float,
    symptoms: List[str]
) -> Dict:
    """
    Calculate an overall risk score (0-100) for the condition.
    
    Args:
        disease: Predicted disease name
        confidence: Model confidence score
        symptoms: List of symptoms
    
    Returns:
        Dictionary with risk score and breakdown
    """
    # Get full severity analysis
    severity_result = analyze_severity(disease, confidence, symptoms)
    
    # Convert severity to base score
    severity_scores = {"mild": 20, "moderate": 45, "severe": 70, "critical": 90}
    base_score = severity_scores.get(severity_result["level"], 45)
    
    # Adjust based on factors
    factor_breakdown = severity_result.get("factor_breakdown", {})
    
    # Add points for severe indicators
    indicator_score = factor_breakdown.get("severe_indicators", {}).get("score", 0)
    indicator_bonus = min(indicator_score * 5, 15)
    
    # Add points for high intensity
    intensity_score = factor_breakdown.get("symptom_intensity", {}).get("score", 0)
    intensity_bonus = min(intensity_score * 3, 10)
    
    # Adjust for confidence
    if confidence < 0.5:
        confidence_adjustment = 5  # Uncertainty adds risk
    elif confidence > 0.9:
        confidence_adjustment = 0
    else:
        confidence_adjustment = 0
    
    # Calculate final score
    final_score = min(100, base_score + indicator_bonus + intensity_bonus + confidence_adjustment)
    
    # Determine risk category
    if final_score >= 80:
        risk_category = "Very High"
        risk_color = "red"
    elif final_score >= 60:
        risk_category = "High"
        risk_color = "orange"
    elif final_score >= 40:
        risk_category = "Moderate"
        risk_color = "yellow"
    elif final_score >= 20:
        risk_category = "Low"
        risk_color = "green"
    else:
        risk_category = "Very Low"
        risk_color = "green"
    
    return {
        "risk_score": round(final_score),
        "risk_category": risk_category,
        "risk_color": risk_color,
        "severity_level": severity_result["level"],
        "urgency": severity_result["urgency"],
        "breakdown": {
            "base_score": base_score,
            "indicator_bonus": indicator_bonus,
            "intensity_bonus": intensity_bonus,
            "confidence_adjustment": confidence_adjustment
        }
    }


# =============================================================================
# Feature 5.4: Urgency Flags - check_urgency_flags Method
# =============================================================================

def check_urgency_flags(disease: str, symptoms: List[str]) -> Dict:
    """
    Check for urgency flags based on disease and symptoms.
    
    Feature 5.4: Urgency Flags
    
    Red Flags (immediate attention):
    - Melanoma predicted with high confidence
    - "bleeding" + "infection" symptoms
    - "rapid_spread" mentioned
    - "severe_pain" present
    
    Yellow Flags (consult doctor):
    - Persistent symptoms mentioned
    - Moderate severity + multiple symptoms
    - Uncertain prediction but concerning symptoms
    
    Args:
        disease: Predicted disease name
        symptoms: List of user-reported symptoms
    
    Returns:
        Dictionary with urgency flag information:
        {
            "urgency_level": str,
            "red_flags": List[str],
            "yellow_flags": List[str],
            "has_red_flags": bool,
            "has_yellow_flags": bool,
            "recommendation": str
        }
    """
    symptom_text = " ".join(symptoms).lower() if symptoms else ""
    
    red_flags_found = []
    yellow_flags_found = []
    
    # ==========================================================================
    # Red Flags (Immediate Attention)
    # ==========================================================================
    
    # 1. Melanoma predicted with high confidence
    if disease in ["Melanoma", "Skin Cancer", "Basal cell carcinoma"]:
        red_flags_found.append(f"{disease} detected - requires immediate evaluation")
    
    # 2. "bleeding" + "infection" symptoms
    has_bleeding = "bleeding" in symptom_text
    has_infection = any(word in symptom_text for word in ["infection", "pus", "infected", "oozing"])
    if has_bleeding and has_infection:
        red_flags_found.append("Bleeding with signs of infection")
    elif has_bleeding:
        red_flags_found.append("Bleeding present")
    elif has_infection:
        red_flags_found.append("Signs of infection")
    
    # 3. "rapid_spread" mentioned
    if any(word in symptom_text for word in ["rapid_spread", "spreading_fast", "rapid_growth", "growing_quickly"]):
        red_flags_found.append("Rapid spread/growth reported")
    
    # 4. "severe_pain" present
    if any(word in symptom_text for word in ["severe_pain", "extreme_pain", "unbearable_pain", "excruciating"]):
        red_flags_found.append("Severe pain reported")
    
    # Additional red flags
    additional_red_flags = [
        ("breathing_difficulty", "Breathing difficulty"),
        ("difficulty_breathing", "Breathing difficulty"),
        ("mouth_sores", "Mouth sores present"),
        ("eye_involvement", "Eye involvement"),
        ("swollen_lymph", "Swollen lymph nodes"),
        ("chest_pain", "Chest pain"),
        ("high_fever", "High fever"),
        ("ulceration", "Ulceration present")
    ]
    
    for keyword, description in additional_red_flags:
        if keyword in symptom_text:
            red_flags_found.append(description)
    
    # ==========================================================================
    # Yellow Flags (Consult Doctor)
    # ==========================================================================
    
    # 1. Persistent symptoms mentioned
    persistent_keywords = ["persistent", "chronic", "long_time", "months", "weeks", "recurring", "ongoing"]
    for keyword in persistent_keywords:
        if keyword in symptom_text:
            yellow_flags_found.append("Persistent/chronic symptoms")
            break
    
    # 2. Moderate severity + multiple symptoms
    if len(symptoms) >= 4:
        yellow_flags_found.append(f"Multiple symptoms reported ({len(symptoms)})")
    
    # 3. Uncertain prediction but concerning symptoms
    concerning_symptoms = ["new_growth", "changing_shape", "color_change", "irregular_border", "asymmetric"]
    concerning_found = [s for s in concerning_symptoms if s in symptom_text]
    if concerning_found:
        yellow_flags_found.append(f"Concerning symptoms: {', '.join(concerning_found)}")
    
    # Additional yellow flags
    if any(word in symptom_text for word in ["worsening", "getting_worse", "spreading"]):
        yellow_flags_found.append("Condition worsening")
    
    if any(word in symptom_text for word in ["not_healing", "slow_healing", "won't_heal"]):
        yellow_flags_found.append("Poor healing noted")
    
    # ==========================================================================
    # Determine Urgency Level
    # ==========================================================================
    has_red_flags = len(red_flags_found) > 0
    has_yellow_flags = len(yellow_flags_found) > 0
    
    if has_red_flags:
        if len(red_flags_found) >= 2:
            urgency_level = "immediate"
            recommendation = "URGENT: Multiple red flags detected. Seek immediate medical attention."
        else:
            urgency_level = "seek_attention"
            recommendation = "Red flag detected. Please see a healthcare provider as soon as possible."
    elif has_yellow_flags:
        if len(yellow_flags_found) >= 2:
            urgency_level = "consult_doctor"
            recommendation = "Multiple concerning factors. Please schedule a medical consultation."
        else:
            urgency_level = "consult_doctor"
            recommendation = "Consider consulting a healthcare provider for evaluation."
    else:
        urgency_level = "routine"
        recommendation = "No urgent flags detected. Monitor condition and seek help if it worsens."
    
    return {
        "urgency_level": urgency_level,
        "red_flags": red_flags_found,
        "yellow_flags": yellow_flags_found,
        "has_red_flags": has_red_flags,
        "has_yellow_flags": has_yellow_flags,
        "red_flag_count": len(red_flags_found),
        "yellow_flag_count": len(yellow_flags_found),
        "recommendation": recommendation
    }


# =============================================================================
# Exposed Methods (Feature 5)
# =============================================================================

__all__ = [
    # Main analysis function
    "analyze_severity",
    
    # Factor assessment functions
    "assess_factor_1_baseline_severity",
    "assess_factor_2_confidence_score",
    "assess_factor_3_symptom_intensity",
    "assess_factor_4_symptom_count",
    "assess_factor_5_severe_indicators",
    "assess_area_spread",
    "assess_duration",
    
    # Helper functions
    "get_urgency_level",
    "get_severity_explanation",
    "get_disease_risk_level",
    "get_severity_recommendations",
    "check_urgency_flags",
    
    # Comparison and scoring
    "compare_severity_factors",
    "calculate_risk_score",
    
    # Data exports
    "DISEASE_SEVERITY_BASE",
    "SEVERITY_ORDER",
    "INTENSITY_KEYWORDS",
    "RED_FLAG_SYMPTOMS",
    "FACTOR_WEIGHTS",
]
