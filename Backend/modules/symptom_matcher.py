"""
Feature 4: Symptom Matching Module
Cross-validates AI predictions with user-reported symptoms

Purpose: Match user-reported symptoms with predicted disease to validate AI prediction
"""

import re
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Symptom database for skin diseases
# Maps disease names to their associated symptoms
DISEASE_SYMPTOMS = {
    "Actinic keratoses": {
        "common": ["rough_patches", "scaly_skin", "dry_skin", "crusty_patches"],
        "optional": ["redness", "itching", "burning", "tenderness"],
        "severity_indicators": ["bleeding", "rapid_growth", "multiple_lesions", "large_area"]
    },
    "Basal cell carcinoma": {
        "common": ["pearly_bump", "flat_lesion", "sore_that_wont_heal", "bleeding"],
        "optional": ["itching", "crusting", "shiny_appearance", "visible_blood_vessels"],
        "severity_indicators": ["rapid_growth", "large_size", "ulceration", "pain"]
    },
    "Benign keratosis-like lesions": {
        "common": ["waxy_growth", "brown_patches", "stuck_on_appearance", "rough_texture"],
        "optional": ["itching", "multiple_spots", "raised_surface"],
        "severity_indicators": ["rapid_change", "bleeding", "irregular_border"]
    },
    "Dermatofibroma": {
        "common": ["firm_bump", "brown_color", "dimpling_when_pinched", "small_nodule"],
        "optional": ["itching", "tenderness", "pink_color"],
        "severity_indicators": ["rapid_growth", "pain", "bleeding"]
    },
    "Melanoma": {
        "common": ["asymmetric_mole", "irregular_border", "color_variation", "large_diameter"],
        "optional": ["itching", "bleeding", "evolving_shape", "new_mole"],
        "severity_indicators": ["rapid_growth", "ulceration", "satellite_lesions", "pain"]
    },
    "Melanocytic nevi": {
        "common": ["round_mole", "uniform_color", "smooth_border", "flat_or_raised"],
        "optional": ["brown_color", "multiple_moles", "small_size"],
        "severity_indicators": ["changing_shape", "irregular_border", "color_change"]
    },
    "Vascular lesions": {
        "common": ["red_spots", "purple_patches", "visible_blood_vessels", "birthmark"],
        "optional": ["swelling", "warmth", "tenderness"],
        "severity_indicators": ["rapid_growth", "bleeding", "pain", "ulceration"]
    },
    # Generic fallback for unknown diseases
    "Unknown": {
        "common": ["rash", "spots", "discoloration", "bumps"],
        "optional": ["itching", "pain", "swelling", "redness"],
        "severity_indicators": ["bleeding", "rapid_spread", "infection_signs"]
    }
}

# Symptom normalization mapping
# Maps common user input variations to standardized symptom names
SYMPTOM_ALIASES = {
    "itchy": "itching",
    "itchy_skin": "itching",
    "itch": "itching",
    "red": "redness",
    "red_skin": "redness",
    "red_spots": "redness",
    "dry": "dry_skin",
    "flaky": "scaly_skin",
    "flaking": "scaly_skin",
    "scales": "scaly_skin",
    "scaly": "scaly_skin",
    "rough": "rough_texture",
    "bumpy": "bumps",
    "bump": "bumps",
    "lump": "firm_bump",
    "sore": "pain",
    "painful": "pain",
    "hurts": "pain",
    "burning": "burning",
    "burns": "burning",
    "bleeding": "bleeding",
    "bleeds": "bleeding",
    "swollen": "swelling",
    "swelling": "swelling",
    "changing": "evolving_shape",
    "growing": "rapid_growth",
    "spreading": "rapid_spread",
    "crusty": "crusting",
    "crust": "crusting",
    "peeling": "scaly_skin",
    "tender": "tenderness",
    "sensitive": "tenderness",
    "mole": "round_mole",
    "spot": "spots",
    "patch": "patches",
    "patches": "patches",
    "discolored": "discoloration",
    "dark_spot": "brown_patches",
    "brown_spot": "brown_patches",
}


def normalize_symptom(raw_symptom: str) -> str:
    """
    Normalize user input symptom to standardized form.
    
    Handles variations like:
    - "itchy skin" → "itching"
    - "red spots" → "redness"
    - "very itchy" → "itching"
    
    Args:
        raw_symptom: Raw user input symptom string
    
    Returns:
        Normalized symptom string
    """
    # Clean and lowercase
    symptom = raw_symptom.strip().lower()
    
    # Remove intensity modifiers
    intensity_words = ["very", "extremely", "slightly", "mild", "severe", "intense"]
    for word in intensity_words:
        symptom = symptom.replace(word, "").strip()
    
    # Replace spaces with underscores
    symptom = symptom.replace(" ", "_")
    
    # Remove extra underscores
    symptom = re.sub(r'_+', '_', symptom).strip('_')
    
    # Check alias mapping
    if symptom in SYMPTOM_ALIASES:
        return SYMPTOM_ALIASES[symptom]
    
    return symptom


def get_disease_symptoms(disease: str) -> Dict:
    """
    Get symptom profile for a disease.
    
    Args:
        disease: Disease name
    
    Returns:
        Dictionary with common, optional, and severity_indicators lists
    """
    # Try exact match first
    if disease in DISEASE_SYMPTOMS:
        return DISEASE_SYMPTOMS[disease]
    
    # Try case-insensitive match
    disease_lower = disease.lower()
    for key in DISEASE_SYMPTOMS:
        if key.lower() == disease_lower:
            return DISEASE_SYMPTOMS[key]
    
    # Return generic symptoms for unknown diseases
    return DISEASE_SYMPTOMS.get("Unknown", {
        "common": [],
        "optional": [],
        "severity_indicators": []
    })


def calculate_alignment_score(disease: str, symptoms: List[str]) -> Tuple[int, List[str]]:
    """
    Calculate how well user symptoms align with disease profile.
    
    Args:
        disease: Predicted disease name
        symptoms: List of user-reported symptoms (normalized)
    
    Returns:
        Tuple of (match_percentage, matched_symptoms_list)
    """
    if not symptoms:
        return 0, []
    
    disease_profile = get_disease_symptoms(disease)
    
    # Combine all possible symptoms for the disease
    all_disease_symptoms = set(
        disease_profile.get("common", []) +
        disease_profile.get("optional", []) +
        disease_profile.get("severity_indicators", [])
    )
    
    if not all_disease_symptoms:
        return 0, []
    
    # Normalize user symptoms
    normalized_symptoms = [normalize_symptom(s) for s in symptoms]
    
    # Find matches
    matched = []
    for symptom in normalized_symptoms:
        if symptom in all_disease_symptoms:
            matched.append(symptom)
        else:
            # Try partial matching
            for disease_symptom in all_disease_symptoms:
                if symptom in disease_symptom or disease_symptom in symptom:
                    matched.append(disease_symptom)
                    break
    
    # Calculate percentage based on common symptoms matched
    common_symptoms = set(disease_profile.get("common", []))
    common_matched = len(set(matched) & common_symptoms)
    
    if common_symptoms:
        # Weight common symptoms more heavily
        match_percentage = int((common_matched / len(common_symptoms)) * 100)
    else:
        match_percentage = int((len(matched) / len(all_disease_symptoms)) * 100) if all_disease_symptoms else 0
    
    # Cap at 100%
    match_percentage = min(match_percentage, 100)
    
    return match_percentage, list(set(matched))


def match_symptoms(disease: str, symptoms: List[str]) -> Dict:
    """
    Match user symptoms with predicted disease.
    
    Args:
        disease: Predicted disease name
        symptoms: List of user-reported symptoms
    
    Returns:
        Dictionary with match analysis:
        {
            "match_percentage": int,
            "alignment": str ("strong", "moderate", "weak"),
            "matched_symptoms": List[str],
            "message": str
        }
    """
    if not symptoms:
        return {
            "match_percentage": 0,
            "alignment": "none",
            "matched_symptoms": [],
            "message": "No symptoms provided for matching."
        }
    
    match_percentage, matched_symptoms = calculate_alignment_score(disease, symptoms)
    
    # Determine alignment level
    if match_percentage >= 80:
        alignment = "strong"
        message = "Your symptoms strongly align with the prediction."
    elif match_percentage >= 50:
        alignment = "moderate"
        message = "Some of your symptoms align with the prediction."
    elif match_percentage > 0:
        alignment = "weak"
        message = "Few symptoms match. Consider consulting a doctor for accurate diagnosis."
    else:
        alignment = "none"
        message = "Symptoms don't match the prediction. Professional evaluation recommended."
    
    return {
        "match_percentage": match_percentage,
        "alignment": alignment,
        "matched_symptoms": matched_symptoms,
        "message": message
    }


def get_all_symptoms() -> List[str]:
    """
    Get list of all available symptoms for user selection.
    
    Returns:
        List of all unique symptom names
    """
    all_symptoms = set()
    
    for disease_data in DISEASE_SYMPTOMS.values():
        all_symptoms.update(disease_data.get("common", []))
        all_symptoms.update(disease_data.get("optional", []))
        all_symptoms.update(disease_data.get("severity_indicators", []))
    
    # Add common aliases
    all_symptoms.update(SYMPTOM_ALIASES.keys())
    
    return sorted(list(all_symptoms))


def get_symptoms_by_category() -> Dict[str, List[str]]:
    """
    Get symptoms organized by category.
    
    Returns:
        Dictionary with categorized symptoms
    """
    return {
        "Skin Appearance": [
            "redness", "patches", "spots", "bumps", "scaly_skin",
            "discoloration", "brown_patches", "pearly_bump", "flat_lesion"
        ],
        "Sensations": [
            "itching", "burning", "pain", "tenderness"
        ],
        "Texture": [
            "dry_skin", "rough_texture", "waxy_growth", "firm_bump",
            "raised_surface", "smooth_border"
        ],
        "Changes": [
            "rapid_growth", "evolving_shape", "color_variation",
            "irregular_border", "changing_shape"
        ],
        "Other": [
            "bleeding", "crusting", "swelling", "ulceration",
            "sore_that_wont_heal", "visible_blood_vessels"
        ]
    }
