"""
Symptom Matching Module
Cross-validates AI predictions with user-reported symptoms
"""

import logging
from typing import Dict, List, Set, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 4.1 Symptom Database (In-Memory Dictionary)
# This knowledge base maps diseases to their characteristic symptoms
DISEASE_SYMPTOMS = {
    "Acne": {
        "common": {"pimples", "blackheads", "whiteheads", "oily_skin", "bumps"},
        "optional": {"redness", "inflammation", "scarring", "tenderness"},
        "severity_indicators": {"cysts", "nodules", "widespread", "painful"}
    },
    "Eczema": {
        "common": {"itching", "redness", "dry_skin", "patches", "rash"},
        "optional": {"oozing", "crusting", "thickened_skin", "scaling", "swelling"},
        "severity_indicators": {"bleeding", "infection_signs", "large_area", "sleep_disturbance"}
    },
    "Melanoma": {
        "common": {"mole_changes", "irregular_border", "asymmetry", "color_variation"},
        "optional": {"itching", "bleeding", "crusting", "growth"},
        "severity_indicators": {"large_diameter", "evolving", "ulceration"}
    },
    "Basal cell carcinoma": {
        "common": {"shiny_bump", "pearly_nodule", "pink_growth", "sore_that_wont_heal"},
        "optional": {"scaly_patch", "white_waxy_scar", "blood_vessels"},
        "severity_indicators": {"bleeding", "crusting", "ulceration", "growing"}
    },
    "Melanocytic nevi": { # Moles
        "common": {"brown_spot", "round_shape", "defined_border", "flat_or_raised"},
        "optional": {"hairs", "darkening"},
        "severity_indicators": {"itching", "pain", "bleeding"} # Usually indicates changes
    },
    "Benign keratosis-like lesions": { # Seborrheic keratoses, solar lentigines
        "common": {"waxy_growth", "stuck_on_appearance", "brown_or_black", "rough_surface"},
        "optional": {"itching", "flat_patch"},
        "severity_indicators": {"bleeding", "irritation", "rapid_growth"}
    },
    "Actinic keratoses": {
        "common": {"rough_patch", "scaly_skin", "sandpaper_texture", "sun_exposed_area"},
        "optional": {"itching", "burning", "redness"},
        "severity_indicators": {"pain", "bleeding", "thickened_patch"}
    },
    "Vascular lesions": { # Cherry angiomas, angiokeratomas, pyogenic granulomas
        "common": {"red_dots", "purple_spots", "blood_blisters"},
        "optional": {"bleeding_easily"},
        "severity_indicators": {"rapid_growth", "pain", "ulceration"}
    },
    "Dermatofibroma": {
        "common": {"firm_bump", "brownish_nodule", "dimple_sign"},
        "optional": {"itching", "tenderness"},
        "severity_indicators": {"rapid_growth", "pain"}
    }
}

# 4.3 Symptom Normalization
# Dictionary to map user variations to standard symptom terms
SYMPTOM_ALIASES = {
    # Itching related
    "itchy": "itching",
    "itch": "itching",
    "scratching": "itching",
    "pruritus": "itching",
    
    # Redness related
    "red": "redness",
    "red_spots": "redness",
    "erythema": "redness",
    
    # Texture related
    "dry": "dry_skin",
    "dryness": "dry_skin",
    "flaky": "scaling",
    "scales": "scaling",
    "rough": "rough_surface",
    
    # Lesion types
    "pimple": "pimples",
    "zit": "pimples",
    "spot": "spots",
    "lump": "nodules",
    "bump": "bumps",
    "blister": "blisters",
    "pus": "oozing",
    
    # Severity/Pain
    "pain": "painful",
    "hurts": "painful",
    "sore": "tenderness",
    "tender": "tenderness",
    "bleed": "bleeding",
    "bloody": "bleeding"
}

def normalize_symptom(raw_symptom: str) -> str:
    """
    Normalize user input symptom to standard terminology.
    
    Args:
        raw_symptom: The symptom string provided by the user
        
    Returns:
        Normalized symptom string
    """
    if not raw_symptom:
        return ""
        
    # Convert to lowercase and strip whitespace
    normalized = raw_symptom.lower().strip()
    
    # Replace spaces with underscores for consistency with database
    normalized = normalized.replace(" ", "_")
    
    # Check aliases
    if normalized in SYMPTOM_ALIASES:
        return SYMPTOM_ALIASES[normalized]
        
    # Check for partial matches in aliases (simple keyword extraction)
    for alias, standard in SYMPTOM_ALIASES.items():
        if alias in normalized:
            return standard
            
    return normalized

def calculate_alignment_score(disease: str, user_symptoms: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Calculate how well the user's symptoms match the predicted disease.
    
    Args:
        disease: The disease name to check against
        user_symptoms: List of symptoms reported by the user
        
    Returns:
        Tuple containing:
        - match_percentage (0.0 to 1.0)
        - matched_symptoms (list of symptoms that matched)
        - unmatched_symptoms (list of symptoms that didn't match)
    """
    if disease not in DISEASE_SYMPTOMS:
        logger.warning(f"Disease '{disease}' not found in symptom database")
        return 0.0, [], user_symptoms
        
    disease_profile = DISEASE_SYMPTOMS[disease]
    
    # Combine all characteristic symptoms for the disease
    all_disease_symptoms = (
        disease_profile["common"] | 
        disease_profile["optional"] | 
        disease_profile["severity_indicators"]
    )
    
    matched = []
    unmatched = []
    
    if not user_symptoms:
        return 0.0, [], []
        
    normalized_user_symptoms = [normalize_symptom(s) for s in user_symptoms]
    
    for symptom in normalized_user_symptoms:
        if symptom in all_disease_symptoms:
            matched.append(symptom)
        else:
            unmatched.append(symptom)
            
    # Calculate score
    # We weight matches against the total number of user reported symptoms
    # This answers: "Of the symptoms the user has, how many fit this disease?"
    if not normalized_user_symptoms:
        match_percentage = 0.0
    else:
        match_percentage = len(matched) / len(normalized_user_symptoms)
        
    return match_percentage, matched, unmatched

def match_symptoms(predicted_disease: str, user_symptoms: List[str]) -> Dict:
    """
    Main entry point for symptom matching.
    
    Args:
        predicted_disease: The disease predicted by the ML model
        user_symptoms: List of symptoms reported by the user
        
    Returns:
        Dictionary with matching results and analysis
    """
    if not user_symptoms:
        return {
            "match_status": "No symptoms provided",
            "match_percentage": 0.0,
            "matched_symptoms": [],
            "unmatched_symptoms": [],
            "feedback": "Please provide symptoms for better accuracy."
        }
        
    percentage, matched, unmatched = calculate_alignment_score(predicted_disease, user_symptoms)
    
    # Determine match status based on percentage
    if percentage >= 0.8:
        status = "Strong match"
        feedback = "The reported symptoms align strongly with the visual prediction."
    elif percentage >= 0.5:
        status = "Moderate match"
        feedback = "Some reported symptoms align with the prediction, but others may be atypical."
    elif percentage > 0:
        status = "Weak match"
        feedback = "The reported symptoms do not strongly align with the visual prediction. Consider consulting a specialist."
    else:
        status = "No match"
        feedback = "The reported symptoms do not match the predicted condition. This requires careful clinical evaluation."
        
    return {
        "match_status": status,
        "match_percentage": round(percentage * 100, 1),
        "matched_symptoms": matched,
        "unmatched_symptoms": unmatched,
        "feedback": feedback
    }
