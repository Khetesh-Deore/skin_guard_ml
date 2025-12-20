"""
Severity Analysis Module
Assess how serious the condition appears based on model confidence, disease baseline, and symptoms.
"""

import logging
from typing import Dict, List, Optional
from modules.symptom_matcher import normalize_symptom, DISEASE_SYMPTOMS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 5.2 Disease Severity Profiles
# Baseline severity and escalation rules for each disease
DISEASE_SEVERITY_BASE = {
    "Acne": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": {"nodules", "cysts", "scarring", "widespread", "painful"}
    },
    "Eczema": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": {"bleeding", "infection_signs", "large_area", "sleep_disturbance", "swelling"}
    },
    "Melanoma": {
        "baseline": "severe",
        "can_escalate_to": "severe",
        "severe_if": {"large_diameter", "evolving", "ulceration", "bleeding"}
    },
    "Basal cell carcinoma": {
        "baseline": "moderate",
        "can_escalate_to": "severe",
        "severe_if": {"bleeding", "ulceration", "growing", "large_size"}
    },
    "Melanocytic nevi": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": {"itching", "pain", "bleeding", "change_in_appearance"}
    },
    "Benign keratosis-like lesions": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": {"bleeding", "irritation", "rapid_growth"}
    },
    "Actinic keratoses": {
        "baseline": "moderate", # Pre-cancerous
        "can_escalate_to": "moderate",
        "severe_if": {"pain", "bleeding", "thickened_patch"}
    },
    "Vascular lesions": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": {"rapid_growth", "pain", "ulceration", "bleeding_easily"}
    },
    "Dermatofibroma": {
        "baseline": "mild",
        "can_escalate_to": "moderate",
        "severe_if": {"rapid_growth", "pain"}
    }
}

SEVERITY_LEVELS = {
    "mild": 1,
    "moderate": 2,
    "severe": 3,
    "critical": 4
}

LEVEL_TO_NAME = {v: k for k, v in SEVERITY_LEVELS.items()}

def calculate_severity_score(
    predicted_disease: str,
    confidence_score: float,
    user_symptoms: List[str]
) -> Dict:
    """
    Calculate the severity level of the condition.
    
    Args:
        predicted_disease: Name of the disease predicted by the model
        confidence_score: Confidence score from the model (0.0 to 1.0)
        user_symptoms: List of symptoms reported by the user
        
    Returns:
        Dictionary containing severity analysis
    """
    if predicted_disease not in DISEASE_SEVERITY_BASE:
        logger.warning(f"Disease '{predicted_disease}' not found in severity database. Defaulting to mild.")
        return {
            "severity_level": "mild",
            "score": 1,
            "reasoning": "Disease profile not found, defaulting to baseline."
        }
        
    profile = DISEASE_SEVERITY_BASE[predicted_disease]
    baseline_level = profile["baseline"]
    current_score = SEVERITY_LEVELS[baseline_level]
    reasoning = [f"Baseline severity for {predicted_disease} is {baseline_level}."]
    
    # Normalize user symptoms
    normalized_symptoms = {normalize_symptom(s) for s in user_symptoms}
    
    # Check for severe indicators
    severe_indicators = profile.get("severe_if", set())
    found_severe_indicators = []
    
    for symptom in normalized_symptoms:
        if symptom in severe_indicators:
            found_severe_indicators.append(symptom)
            
    if found_severe_indicators:
        current_score += 1
        reasoning.append(f"Presence of severe indicators ({', '.join(found_severe_indicators)}) increased severity.")
        
    # Check for high intensity keywords (generic)
    high_intensity_keywords = {"painful", "severe", "extreme", "bleeding", "spreading", "rapid"}
    intensity_matches = []
    for symptom in normalized_symptoms:
        for keyword in high_intensity_keywords:
            if keyword in symptom and symptom not in found_severe_indicators:
                intensity_matches.append(symptom)
                
    if intensity_matches:
        # Only add score if we haven't already maxed out based on "can_escalate_to" logic or if it's critical
        # But for simplicity, let's just add 0.5 or 1
        current_score += 0.5
        reasoning.append(f"High intensity symptoms reported: {', '.join(intensity_matches)}.")

    # Cap severity based on disease profile limits (optional logic, but good for safety)
    # Some diseases like Acne rarely become "critical" in the life-threatening sense
    # But Melanoma starts at "severe".
    
    # Ensure score doesn't exceed 3 (severe) unless specific conditions met, or cap at 4
    current_score = min(current_score, 4)
    
    # Convert back to string level
    # Round to nearest integer for the label
    final_level_idx = int(round(current_score))
    final_level_idx = max(1, min(4, final_level_idx)) # Clamp between 1 and 4
    final_level = LEVEL_TO_NAME[final_level_idx]
    
    return {
        "severity_level": final_level,
        "score": current_score,
        "reasoning": " ".join(reasoning)
    }

def get_severity_color(severity_level: str) -> str:
    """
    Get a color code for the severity level (UI helper).
    """
    colors = {
        "mild": "#28a745",      # Green
        "moderate": "#ffc107",  # Yellow/Orange
        "severe": "#dc3545",    # Red
        "critical": "#721c24"   # Dark Red
    }
    return colors.get(severity_level, "#6c757d") # Default gray
