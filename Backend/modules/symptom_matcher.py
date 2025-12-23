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
# Complete database for all 22 Teachable Machine classes
DISEASE_SYMPTOMS = {
    # Class 0: Acne
    "Acne": {
        "common": ["pimples", "blackheads", "whiteheads", "oily_skin", "bumps"],
        "optional": ["redness", "inflammation", "scarring", "pustules", "papules"],
        "severity_indicators": ["cysts", "nodules", "widespread", "deep_lesions", "severe_scarring"]
    },
    
    # Class 1: Actinic Keratosis
    "Actinic Keratosis": {
        "common": ["rough_patches", "scaly_skin", "dry_skin", "crusty_patches", "sun_damaged_skin"],
        "optional": ["redness", "itching", "burning", "tenderness", "flat_lesion"],
        "severity_indicators": ["bleeding", "rapid_growth", "multiple_lesions", "large_area", "hardening"]
    },
    
    # Class 2: Benign Tumors
    "Benign Tumors": {
        "common": ["lump", "firm_bump", "slow_growing", "painless_mass", "round_shape"],
        "optional": ["skin_colored", "movable", "soft_texture", "smooth_surface"],
        "severity_indicators": ["rapid_growth", "pain", "size_increase", "skin_changes"]
    },
    
    # Class 3: Bullous (Blistering diseases)
    "Bullous": {
        "common": ["blisters", "fluid_filled_bumps", "skin_peeling", "raw_skin", "erosions"],
        "optional": ["itching", "burning", "pain", "redness", "crusting"],
        "severity_indicators": ["widespread_blisters", "mouth_sores", "infection_signs", "fever", "large_area"]
    },
    
    # Class 4: Candidiasis
    "Candidiasis": {
        "common": ["red_rash", "itching", "white_patches", "skin_folds_affected", "moist_areas"],
        "optional": ["burning", "soreness", "cracking", "scaling", "satellite_lesions"],
        "severity_indicators": ["spreading", "severe_itching", "infection_signs", "fever", "widespread"]
    },
    
    # Class 5: Drug Eruption
    "Drug Eruption": {
        "common": ["rash", "hives", "redness", "itching", "widespread_spots"],
        "optional": ["swelling", "blisters", "peeling", "fever", "joint_pain"],
        "severity_indicators": ["mouth_sores", "eye_involvement", "severe_peeling", "fever", "breathing_difficulty"]
    },
    
    # Class 6: Eczema
    "Eczema": {
        "common": ["itching", "redness", "dry_skin", "patches", "inflammation"],
        "optional": ["oozing", "crusting", "thickened_skin", "scaly_skin", "cracking"],
        "severity_indicators": ["bleeding", "infection_signs", "large_area", "sleep_disruption", "severe_itching"]
    },
    
    # Class 7: Infestations/Bites
    "Infestations/Bites": {
        "common": ["itching", "red_bumps", "bite_marks", "small_spots", "clustered_bumps"],
        "optional": ["swelling", "redness", "pain", "blisters", "hives"],
        "severity_indicators": ["severe_itching", "infection_signs", "spreading", "allergic_reaction", "fever"]
    },
    
    # Class 8: Lichen
    "Lichen": {
        "common": ["purple_bumps", "flat_topped_lesions", "itching", "shiny_surface", "white_lines"],
        "optional": ["scaly_skin", "mouth_sores", "nail_changes", "hair_loss", "redness"],
        "severity_indicators": ["widespread", "severe_itching", "scarring", "nail_damage", "mouth_ulcers"]
    },
    
    # Class 9: Lupus
    "Lupus": {
        "common": ["butterfly_rash", "facial_redness", "sun_sensitivity", "skin_lesions", "discoid_rash"],
        "optional": ["joint_pain", "fatigue", "fever", "hair_loss", "mouth_sores"],
        "severity_indicators": ["widespread_rash", "kidney_problems", "severe_fatigue", "chest_pain", "fever"]
    },
    
    # Class 10: Moles
    "Moles": {
        "common": ["round_mole", "uniform_color", "smooth_border", "flat_or_raised", "brown_color"],
        "optional": ["multiple_moles", "small_size", "symmetrical", "stable_appearance"],
        "severity_indicators": ["changing_shape", "irregular_border", "color_change", "bleeding", "itching"]
    },
    
    # Class 11: Psoriasis
    "Psoriasis": {
        "common": ["red_patches", "silvery_scales", "dry_skin", "itching", "thick_plaques"],
        "optional": ["burning", "soreness", "nail_changes", "joint_pain", "cracking"],
        "severity_indicators": ["widespread", "joint_swelling", "severe_scaling", "bleeding", "large_area"]
    },
    
    # Class 12: Rosacea
    "Rosacea": {
        "common": ["facial_redness", "flushing", "visible_blood_vessels", "bumps", "pimples"],
        "optional": ["burning", "stinging", "dry_skin", "eye_irritation", "swelling"],
        "severity_indicators": ["nose_enlargement", "severe_redness", "eye_problems", "thickened_skin", "persistent_flushing"]
    },
    
    # Class 13: Seborrheic Keratoses
    "Seborrheic Keratoses": {
        "common": ["waxy_growth", "brown_patches", "stuck_on_appearance", "rough_texture", "raised_lesion"],
        "optional": ["itching", "multiple_spots", "tan_color", "black_color", "scaly_surface"],
        "severity_indicators": ["rapid_change", "bleeding", "irregular_border", "pain", "inflammation"]
    },
    
    # Class 14: Skin Cancer
    "Skin Cancer": {
        "common": ["new_growth", "changing_mole", "sore_that_wont_heal", "irregular_border", "color_variation"],
        "optional": ["bleeding", "crusting", "itching", "pain", "ulceration"],
        "severity_indicators": ["rapid_growth", "spreading", "satellite_lesions", "lymph_node_swelling", "large_size"]
    },
    
    # Class 15: Sun/Sunlight Damage
    "Sun/Sunlight Damage": {
        "common": ["sunburn", "redness", "peeling", "dry_skin", "freckles"],
        "optional": ["blisters", "pain", "swelling", "itching", "skin_discoloration"],
        "severity_indicators": ["severe_blistering", "fever", "chills", "nausea", "widespread_damage"]
    },
    
    # Class 16: Tinea (Fungal infections)
    "Tinea": {
        "common": ["ring_shaped_rash", "itching", "scaly_skin", "red_border", "clear_center"],
        "optional": ["burning", "cracking", "blisters", "hair_loss", "nail_changes"],
        "severity_indicators": ["spreading", "severe_itching", "infection_signs", "widespread", "nail_involvement"]
    },
    
    # Class 17: Unknown/Normal
    "Unknown/Normal": {
        "common": ["normal_skin", "no_symptoms", "healthy_appearance"],
        "optional": ["minor_blemish", "temporary_redness"],
        "severity_indicators": []
    },
    
    # Class 18: Vascular Tumors
    "Vascular Tumors": {
        "common": ["red_spots", "purple_patches", "visible_blood_vessels", "birthmark", "hemangioma"],
        "optional": ["swelling", "warmth", "tenderness", "raised_lesion", "soft_texture"],
        "severity_indicators": ["rapid_growth", "bleeding", "pain", "ulceration", "large_size"]
    },
    
    # Class 19: Vasculitis
    "Vasculitis": {
        "common": ["purple_spots", "red_spots", "skin_ulcers", "rash", "palpable_purpura"],
        "optional": ["pain", "fever", "fatigue", "joint_pain", "numbness"],
        "severity_indicators": ["widespread", "organ_involvement", "severe_ulcers", "fever", "kidney_problems"]
    },
    
    # Class 20: Vitiligo
    "Vitiligo": {
        "common": ["white_patches", "loss_of_color", "depigmentation", "symmetrical_patches", "pale_skin"],
        "optional": ["premature_graying", "eye_color_change", "mouth_discoloration"],
        "severity_indicators": ["spreading", "widespread", "rapid_progression", "facial_involvement"]
    },
    
    # Class 21: Warts
    "Warts": {
        "common": ["rough_bump", "skin_colored_growth", "cauliflower_texture", "small_dots", "raised_lesion"],
        "optional": ["pain", "tenderness", "multiple_warts", "clustering", "itching"],
        "severity_indicators": ["spreading", "large_size", "bleeding", "rapid_growth", "genital_area"]
    },
    
    # Legacy mappings for HAM10000 dataset compatibility
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
    # Itching variations
    "itchy": "itching",
    "itchy_skin": "itching",
    "itch": "itching",
    "scratchy": "itching",
    
    # Redness variations
    "red": "redness",
    "red_skin": "redness",
    "red_spots": "redness",
    "reddish": "redness",
    "inflamed": "inflammation",
    
    # Dryness variations
    "dry": "dry_skin",
    "flaky": "scaly_skin",
    "flaking": "scaly_skin",
    "scales": "scaly_skin",
    "scaly": "scaly_skin",
    "peeling": "skin_peeling",
    "flakes": "scaly_skin",
    
    # Texture variations
    "rough": "rough_texture",
    "bumpy": "bumps",
    "bump": "bumps",
    "lump": "firm_bump",
    "lumpy": "firm_bump",
    "raised": "raised_lesion",
    "elevated": "raised_lesion",
    
    # Pain variations
    "sore": "pain",
    "painful": "pain",
    "hurts": "pain",
    "aching": "pain",
    "tender": "tenderness",
    "sensitive": "tenderness",
    
    # Burning variations
    "burning": "burning",
    "burns": "burning",
    "stinging": "stinging",
    "hot": "warmth",
    
    # Bleeding variations
    "bleeding": "bleeding",
    "bleeds": "bleeding",
    "blood": "bleeding",
    
    # Swelling variations
    "swollen": "swelling",
    "swelling": "swelling",
    "puffy": "swelling",
    "inflated": "swelling",
    
    # Change variations
    "changing": "evolving_shape",
    "growing": "rapid_growth",
    "spreading": "spreading",
    "getting_bigger": "rapid_growth",
    "enlarging": "rapid_growth",
    
    # Crust variations
    "crusty": "crusting",
    "crust": "crusting",
    "scab": "crusting",
    "scabby": "crusting",
    
    # Mole variations
    "mole": "round_mole",
    "spot": "spots",
    "patch": "patches",
    "patches": "patches",
    "mark": "spots",
    
    # Color variations
    "discolored": "discoloration",
    "dark_spot": "brown_patches",
    "brown_spot": "brown_patches",
    "white_spot": "white_patches",
    "purple": "purple_spots",
    "pink": "redness",
    
    # Blister variations
    "blister": "blisters",
    "blistering": "blisters",
    "water_blister": "fluid_filled_bumps",
    "bubble": "blisters",
    
    # Rash variations
    "rash": "rash",
    "breakout": "rash",
    "eruption": "rash",
    "outbreak": "rash",
    
    # Acne-specific
    "pimple": "pimples",
    "zit": "pimples",
    "acne": "pimples",
    "blackhead": "blackheads",
    "whitehead": "whiteheads",
    "cyst": "cysts",
    "nodule": "nodules",
    
    # Fungal-specific
    "ringworm": "ring_shaped_rash",
    "ring": "ring_shaped_rash",
    "athletes_foot": "tinea",
    "jock_itch": "tinea",
    
    # Sun-related
    "sunburn": "sunburn",
    "sun_damage": "sun_damaged_skin",
    "tan": "sun_damaged_skin",
    "freckle": "freckles",
    
    # Eczema-specific
    "eczema": "patches",
    "dermatitis": "inflammation",
    "atopic": "patches",
    
    # Psoriasis-specific
    "plaque": "thick_plaques",
    "silvery": "silvery_scales",
    "silver_scales": "silvery_scales",
    
    # Vitiligo-specific
    "depigmented": "depigmentation",
    "loss_of_pigment": "loss_of_color",
    "pale_patch": "white_patches",
    
    # Wart-specific
    "wart": "rough_bump",
    "verruca": "rough_bump",
    "plantar_wart": "rough_bump",
    
    # General
    "lesion": "skin_lesions",
    "wound": "sore_that_wont_heal",
    "ulcer": "skin_ulcers",
    "open_sore": "sore_that_wont_heal",
    "infection": "infection_signs",
    "infected": "infection_signs",
    "pus": "infection_signs",
    "oozing": "oozing",
    "weeping": "oozing",
    "discharge": "oozing",
}


# Contradictory symptoms mapping
# Symptoms that typically don't occur together or indicate different conditions
CONTRADICTORY_SYMPTOMS = {
    # Acne contradictions
    "Acne": ["white_patches", "depigmentation", "ring_shaped_rash", "butterfly_rash"],
    
    # Vitiligo contradictions (pigment loss vs pigment increase)
    "Vitiligo": ["brown_patches", "hyperpigmentation", "pimples", "oily_skin"],
    
    # Psoriasis vs Eczema distinctions
    "Psoriasis": ["oozing", "weeping", "moist_areas"],  # Psoriasis is typically dry
    "Eczema": ["silvery_scales", "thick_plaques"],  # More psoriasis-specific
    
    # Fungal vs bacterial
    "Tinea": ["pus", "yellow_discharge"],  # Fungal typically doesn't have pus
    "Candidiasis": ["silvery_scales", "thick_plaques"],
    
    # Cancer warning signs contradictions
    "Moles": ["rapid_growth", "irregular_border", "color_variation", "ulceration"],  # These suggest malignancy
    
    # Rosacea vs Acne
    "Rosacea": ["blackheads", "whiteheads"],  # Rosacea doesn't have comedones
    
    # Sun damage contradictions
    "Sun/Sunlight Damage": ["white_patches", "depigmentation"],  # Sun causes hyperpigmentation
    
    # Vascular vs pigmented
    "Vascular Tumors": ["brown_patches", "hyperpigmentation"],
    "Vasculitis": ["oily_skin", "blackheads", "whiteheads"],
}

# Disease-specific symptom weights for more accurate matching
SYMPTOM_WEIGHTS = {
    "common": 3,      # Common symptoms are most important
    "optional": 1,    # Optional symptoms add some weight
    "severity_indicators": 2  # Severity indicators are important for assessment
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


def check_contradictory_symptoms(disease: str, symptoms: List[str]) -> Tuple[bool, List[str]]:
    """
    Check if user symptoms contain contradictory indicators for the predicted disease.
    
    Args:
        disease: Predicted disease name
        symptoms: List of user-reported symptoms (normalized)
    
    Returns:
        Tuple of (has_contradictions: bool, contradictory_symptoms: List[str])
    """
    contradictions = CONTRADICTORY_SYMPTOMS.get(disease, [])
    if not contradictions:
        return False, []
    
    # Normalize user symptoms
    normalized_symptoms = [normalize_symptom(s) for s in symptoms]
    
    # Find contradictory symptoms
    found_contradictions = []
    for symptom in normalized_symptoms:
        for contradiction in contradictions:
            if symptom == contradiction or symptom in contradiction or contradiction in symptom:
                found_contradictions.append(symptom)
                break
    
    return len(found_contradictions) > 0, found_contradictions


def calculate_alignment_score(disease: str, symptoms: List[str]) -> Tuple[int, List[str], Dict]:
    """
    Calculate how well user symptoms align with disease profile.
    
    Feature 4.2 Matching Algorithm:
    1. Get symptom profile for predicted disease
    2. Count matches with user symptoms
    3. Calculate match percentage
    4. Check for contradictory symptoms
    5. Adjust confidence based on match rate
    
    Args:
        disease: Predicted disease name
        symptoms: List of user-reported symptoms
    
    Returns:
        Tuple of (match_percentage, matched_symptoms_list, details_dict)
    """
    if not symptoms:
        return 0, [], {"common_matched": 0, "optional_matched": 0, "severity_matched": 0}
    
    disease_profile = get_disease_symptoms(disease)
    
    # Get symptom categories
    common_symptoms = set(disease_profile.get("common", []))
    optional_symptoms = set(disease_profile.get("optional", []))
    severity_symptoms = set(disease_profile.get("severity_indicators", []))
    
    # Combine all possible symptoms for the disease
    all_disease_symptoms = common_symptoms | optional_symptoms | severity_symptoms
    
    if not all_disease_symptoms:
        return 0, [], {"common_matched": 0, "optional_matched": 0, "severity_matched": 0}
    
    # Normalize user symptoms
    normalized_symptoms = [normalize_symptom(s) for s in symptoms]
    
    # Find matches by category
    common_matched = []
    optional_matched = []
    severity_matched = []
    all_matched = []
    
    for symptom in normalized_symptoms:
        matched = False
        
        # Check common symptoms
        for disease_symptom in common_symptoms:
            if symptom == disease_symptom or symptom in disease_symptom or disease_symptom in symptom:
                common_matched.append(disease_symptom)
                all_matched.append(disease_symptom)
                matched = True
                break
        
        if matched:
            continue
            
        # Check optional symptoms
        for disease_symptom in optional_symptoms:
            if symptom == disease_symptom or symptom in disease_symptom or disease_symptom in symptom:
                optional_matched.append(disease_symptom)
                all_matched.append(disease_symptom)
                matched = True
                break
        
        if matched:
            continue
            
        # Check severity symptoms
        for disease_symptom in severity_symptoms:
            if symptom == disease_symptom or symptom in disease_symptom or disease_symptom in symptom:
                severity_matched.append(disease_symptom)
                all_matched.append(disease_symptom)
                break
    
    # Calculate weighted score
    common_score = len(set(common_matched)) * SYMPTOM_WEIGHTS["common"]
    optional_score = len(set(optional_matched)) * SYMPTOM_WEIGHTS["optional"]
    severity_score = len(set(severity_matched)) * SYMPTOM_WEIGHTS["severity_indicators"]
    
    total_score = common_score + optional_score + severity_score
    
    # Calculate max possible score
    max_common = len(common_symptoms) * SYMPTOM_WEIGHTS["common"]
    max_optional = len(optional_symptoms) * SYMPTOM_WEIGHTS["optional"]
    max_severity = len(severity_symptoms) * SYMPTOM_WEIGHTS["severity_indicators"]
    max_score = max_common + max_optional + max_severity
    
    # Calculate percentage (weighted towards common symptoms)
    if max_score > 0:
        # Primary: based on common symptoms (most important)
        if common_symptoms:
            common_percentage = (len(set(common_matched)) / len(common_symptoms)) * 100
        else:
            common_percentage = 0
        
        # Secondary: overall weighted score
        weighted_percentage = (total_score / max_score) * 100
        
        # Combine: 70% common, 30% overall
        match_percentage = int(common_percentage * 0.7 + weighted_percentage * 0.3)
    else:
        match_percentage = 0
    
    # Cap at 100%
    match_percentage = min(match_percentage, 100)
    
    details = {
        "common_matched": len(set(common_matched)),
        "common_total": len(common_symptoms),
        "optional_matched": len(set(optional_matched)),
        "optional_total": len(optional_symptoms),
        "severity_matched": len(set(severity_matched)),
        "severity_total": len(severity_symptoms),
        "weighted_score": total_score,
        "max_score": max_score
    }
    
    return match_percentage, list(set(all_matched)), details


def adjust_confidence_based_on_symptoms(
    original_confidence: float,
    match_percentage: int,
    has_contradictions: bool
) -> Tuple[float, str]:
    """
    Adjust AI confidence based on symptom matching results.
    
    Args:
        original_confidence: Original AI model confidence (0-1)
        match_percentage: Symptom match percentage (0-100)
        has_contradictions: Whether contradictory symptoms were found
    
    Returns:
        Tuple of (adjusted_confidence, adjustment_reason)
    """
    adjusted = original_confidence
    reason = None
    
    # Strong symptom match increases confidence
    if match_percentage >= 80:
        adjustment = min(0.1, (1.0 - original_confidence) * 0.3)
        adjusted = min(1.0, original_confidence + adjustment)
        reason = "Confidence increased due to strong symptom alignment"
    
    # Moderate match - slight increase
    elif match_percentage >= 50:
        adjustment = min(0.05, (1.0 - original_confidence) * 0.15)
        adjusted = min(1.0, original_confidence + adjustment)
        reason = "Confidence slightly increased due to moderate symptom alignment"
    
    # Weak match - slight decrease
    elif match_percentage < 30 and match_percentage > 0:
        adjusted = max(0.1, original_confidence * 0.9)
        reason = "Confidence slightly decreased due to weak symptom alignment"
    
    # No match - decrease confidence
    elif match_percentage == 0:
        adjusted = max(0.1, original_confidence * 0.8)
        reason = "Confidence decreased - no symptom matches found"
    
    # Contradictory symptoms - significant decrease
    if has_contradictions:
        adjusted = max(0.1, adjusted * 0.7)
        reason = "Confidence significantly decreased due to contradictory symptoms"
    
    return round(adjusted, 4), reason


def match_symptoms(disease: str, symptoms: List[str], original_confidence: float = None) -> Dict:
    """
    Match user symptoms with predicted disease.
    
    Feature 4.2 Complete Matching Algorithm:
    Input:
    - predicted_disease
    - user_symptoms (list of strings)
    
    Process:
    1. Get symptom profile for predicted disease
    2. Count matches with user symptoms
    3. Calculate match percentage
    4. Check for contradictory symptoms
    5. Adjust confidence based on match rate
    
    Scoring:
    - 80%+ match → "Strong match - symptoms align with prediction"
    - 50-79% match → "Moderate match - some symptoms align"
    - <50% match → "Weak match - consider other conditions"
    - Contradictory symptoms → "Warning: symptoms don't match prediction"
    
    Args:
        disease: Predicted disease name
        symptoms: List of user-reported symptoms
        original_confidence: Optional original AI confidence for adjustment
    
    Returns:
        Dictionary with match analysis:
        {
            "match_percentage": int,
            "alignment": str ("strong", "moderate", "weak", "none"),
            "matched_symptoms": List[str],
            "message": str,
            "has_contradictions": bool,
            "contradictory_symptoms": List[str],
            "confidence_adjustment": Optional[Dict],
            "details": Dict
        }
    """
    if not symptoms:
        return {
            "match_percentage": 0,
            "alignment": "none",
            "matched_symptoms": [],
            "message": "No symptoms provided for matching.",
            "has_contradictions": False,
            "contradictory_symptoms": [],
            "confidence_adjustment": None,
            "details": {}
        }
    
    # Step 1-3: Calculate alignment score
    match_percentage, matched_symptoms, details = calculate_alignment_score(disease, symptoms)
    
    # Step 4: Check for contradictory symptoms
    has_contradictions, contradictory_symptoms = check_contradictory_symptoms(disease, symptoms)
    
    # Step 5: Adjust confidence if provided
    confidence_adjustment = None
    if original_confidence is not None:
        adjusted_confidence, adjustment_reason = adjust_confidence_based_on_symptoms(
            original_confidence, match_percentage, has_contradictions
        )
        confidence_adjustment = {
            "original": original_confidence,
            "adjusted": adjusted_confidence,
            "reason": adjustment_reason
        }
    
    # Determine alignment level and message based on scoring rules
    if has_contradictions:
        alignment = "contradictory"
        message = f"Warning: Some symptoms ({', '.join(contradictory_symptoms)}) don't typically match {disease}. Professional evaluation strongly recommended."
    elif match_percentage >= 80:
        alignment = "strong"
        message = f"Strong match - your symptoms strongly align with {disease} prediction."
    elif match_percentage >= 50:
        alignment = "moderate"
        message = f"Moderate match - some of your symptoms align with {disease}."
    elif match_percentage > 0:
        alignment = "weak"
        message = f"Weak match - few symptoms match {disease}. Consider consulting a doctor for accurate diagnosis."
    else:
        alignment = "none"
        message = f"No symptom matches found for {disease}. Professional evaluation recommended."
    
    return {
        "match_percentage": match_percentage,
        "alignment": alignment,
        "matched_symptoms": matched_symptoms,
        "message": message,
        "has_contradictions": has_contradictions,
        "contradictory_symptoms": contradictory_symptoms,
        "confidence_adjustment": confidence_adjustment,
        "details": details
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
    Get symptoms organized by category for UI display.
    
    Returns:
        Dictionary with categorized symptoms
    """
    return {
        "Skin Appearance": [
            "redness", "patches", "spots", "bumps", "scaly_skin",
            "discoloration", "brown_patches", "white_patches", "purple_spots",
            "pearly_bump", "flat_lesion", "raised_lesion", "rash", "hives"
        ],
        "Sensations": [
            "itching", "burning", "pain", "tenderness", "stinging",
            "numbness", "tingling", "warmth", "soreness"
        ],
        "Texture Changes": [
            "dry_skin", "rough_texture", "waxy_growth", "firm_bump",
            "raised_surface", "smooth_border", "thick_plaques", "scaly_skin",
            "thickened_skin", "soft_texture"
        ],
        "Lesion Changes": [
            "rapid_growth", "evolving_shape", "color_variation",
            "irregular_border", "changing_shape", "spreading", "new_growth",
            "size_increase"
        ],
        "Surface Issues": [
            "bleeding", "crusting", "oozing", "ulceration", "peeling",
            "cracking", "blisters", "erosions", "skin_peeling"
        ],
        "Acne Symptoms": [
            "pimples", "blackheads", "whiteheads", "oily_skin",
            "cysts", "nodules", "pustules", "papules", "inflammation"
        ],
        "Fungal Signs": [
            "ring_shaped_rash", "red_border", "clear_center",
            "nail_changes", "hair_loss", "athlete_foot"
        ],
        "Vascular Signs": [
            "visible_blood_vessels", "spider_veins", "flushing",
            "facial_redness", "birthmark", "hemangioma"
        ],
        "Systemic Symptoms": [
            "fever", "fatigue", "joint_pain", "swelling",
            "mouth_sores", "eye_irritation"
        ],
        "Warning Signs": [
            "sore_that_wont_heal", "rapid_growth", "bleeding",
            "infection_signs", "satellite_lesions", "lymph_node_swelling"
        ]
    }


def find_best_matching_diseases(symptoms: List[str], top_n: int = 3) -> List[Dict]:
    """
    Find diseases that best match the given symptoms.
    Useful when AI prediction doesn't align well with symptoms.
    
    Args:
        symptoms: List of user-reported symptoms
        top_n: Number of top matches to return
    
    Returns:
        List of dictionaries with disease name and match score
    """
    if not symptoms:
        return []
    
    matches = []
    
    # Check each disease
    for disease in DISEASE_SYMPTOMS.keys():
        if disease in ["Unknown", "Unknown/Normal"]:
            continue
            
        match_percentage, matched_symptoms, details = calculate_alignment_score(disease, symptoms)
        
        if match_percentage > 0:
            matches.append({
                "disease": disease,
                "match_percentage": match_percentage,
                "matched_symptoms": matched_symptoms,
                "common_matched": details.get("common_matched", 0),
                "common_total": details.get("common_total", 0)
            })
    
    # Sort by match percentage (descending)
    matches.sort(key=lambda x: x["match_percentage"], reverse=True)
    
    return matches[:top_n]


def get_symptom_severity_indicators(disease: str, symptoms: List[str]) -> Dict:
    """
    Check if user symptoms include severity indicators for the disease.
    
    Args:
        disease: Disease name
        symptoms: List of user-reported symptoms
    
    Returns:
        Dictionary with severity indicator analysis
    """
    disease_profile = get_disease_symptoms(disease)
    severity_indicators = set(disease_profile.get("severity_indicators", []))
    
    if not severity_indicators:
        return {
            "has_severity_indicators": False,
            "matched_indicators": [],
            "severity_level": "unknown"
        }
    
    # Normalize user symptoms
    normalized_symptoms = [normalize_symptom(s) for s in symptoms]
    
    # Find matched severity indicators
    matched_indicators = []
    for symptom in normalized_symptoms:
        for indicator in severity_indicators:
            if symptom == indicator or symptom in indicator or indicator in symptom:
                matched_indicators.append(indicator)
                break
    
    matched_indicators = list(set(matched_indicators))
    
    # Determine severity level based on indicator count
    indicator_count = len(matched_indicators)
    total_indicators = len(severity_indicators)
    
    if indicator_count == 0:
        severity_level = "mild"
    elif indicator_count <= total_indicators * 0.3:
        severity_level = "moderate"
    elif indicator_count <= total_indicators * 0.6:
        severity_level = "severe"
    else:
        severity_level = "critical"
    
    return {
        "has_severity_indicators": indicator_count > 0,
        "matched_indicators": matched_indicators,
        "indicator_count": indicator_count,
        "total_indicators": total_indicators,
        "severity_level": severity_level
    }


# =============================================================================
# Feature 4.3: Enhanced Symptom Normalization
# =============================================================================

# Severity modifiers that indicate intensity level
SEVERITY_MODIFIERS = {
    "high": ["very", "extremely", "severely", "intensely", "unbearably", "terribly", 
             "really", "super", "incredibly", "excruciating", "constant", "persistent"],
    "moderate": ["moderately", "somewhat", "fairly", "quite", "noticeably", "frequently"],
    "low": ["slightly", "mildly", "a_little", "barely", "occasionally", "sometimes", "minor"]
}

# Keyword extraction patterns for common symptom phrases
KEYWORD_PATTERNS = {
    # Itching patterns
    r"itchy?\s*skin": "itching",
    r"skin\s*itch": "itching",
    r"scratching": "itching",
    r"want\s*to\s*scratch": "itching",
    
    # Redness patterns
    r"red\s*spot": "redness",
    r"red\s*area": "redness",
    r"red\s*skin": "redness",
    r"looks?\s*red": "redness",
    r"turned?\s*red": "redness",
    
    # Pain patterns
    r"hurts?\s*a?\s*lot": "pain",
    r"painful\s*area": "pain",
    r"sore\s*spot": "pain",
    r"tender\s*to\s*touch": "tenderness",
    
    # Dryness patterns
    r"dry\s*skin": "dry_skin",
    r"skin\s*dry": "dry_skin",
    r"flaky\s*skin": "scaly_skin",
    r"peeling\s*skin": "skin_peeling",
    
    # Growth patterns
    r"getting\s*bigger": "rapid_growth",
    r"growing\s*fast": "rapid_growth",
    r"spreading\s*fast": "spreading",
    r"new\s*spot": "new_growth",
    
    # Bleeding patterns
    r"bleeds?\s*easily": "bleeding",
    r"won'?t\s*stop\s*bleeding": "bleeding",
    r"blood\s*coming": "bleeding",
    
    # Texture patterns
    r"rough\s*texture": "rough_texture",
    r"bumpy\s*skin": "bumps",
    r"raised\s*area": "raised_lesion",
    r"flat\s*spot": "flat_lesion",
    
    # Color patterns
    r"dark\s*spot": "brown_patches",
    r"brown\s*spot": "brown_patches",
    r"white\s*spot": "white_patches",
    r"purple\s*spot": "purple_spots",
    r"discolored?\s*area": "discoloration",
    
    # Acne patterns
    r"pimple": "pimples",
    r"zit": "pimples",
    r"blackhead": "blackheads",
    r"whitehead": "whiteheads",
    r"oily\s*skin": "oily_skin",
    
    # Fungal patterns
    r"ring\s*shape": "ring_shaped_rash",
    r"circular\s*rash": "ring_shaped_rash",
    r"athlete'?s?\s*foot": "tinea",
}


def extract_severity_flag(raw_symptom: str) -> Tuple[str, str, bool]:
    """
    Extract severity information from symptom description.
    
    Feature 4.3: Handle user input variations like "very itchy" → "itching" + severity flag
    
    Args:
        raw_symptom: Raw user input symptom string
    
    Returns:
        Tuple of (normalized_symptom, severity_level, has_severity_modifier)
        severity_level: "high", "moderate", "low", or "normal"
    """
    symptom_lower = raw_symptom.strip().lower()
    severity_level = "normal"
    has_modifier = False
    
    # Check for high severity modifiers
    for modifier in SEVERITY_MODIFIERS["high"]:
        if modifier in symptom_lower:
            severity_level = "high"
            has_modifier = True
            # Remove the modifier from symptom
            symptom_lower = symptom_lower.replace(modifier, "").strip()
            break
    
    # Check for moderate severity modifiers
    if not has_modifier:
        for modifier in SEVERITY_MODIFIERS["moderate"]:
            if modifier in symptom_lower:
                severity_level = "moderate"
                has_modifier = True
                symptom_lower = symptom_lower.replace(modifier, "").strip()
                break
    
    # Check for low severity modifiers
    if not has_modifier:
        for modifier in SEVERITY_MODIFIERS["low"]:
            if modifier in symptom_lower:
                severity_level = "low"
                has_modifier = True
                symptom_lower = symptom_lower.replace(modifier, "").strip()
                break
    
    # Normalize the remaining symptom
    normalized = normalize_symptom(symptom_lower)
    
    return normalized, severity_level, has_modifier


def fuzzy_match_symptom(user_input: str, threshold: float = 0.6) -> Tuple[Optional[str], float]:
    """
    Use fuzzy matching to find the best matching symptom.
    
    Feature 4.3: Fuzzy matching for symptom normalization
    
    Args:
        user_input: User's symptom description
        threshold: Minimum similarity score (0-1) to consider a match
    
    Returns:
        Tuple of (matched_symptom or None, similarity_score)
    """
    # First try exact normalization
    normalized = normalize_symptom(user_input)
    
    # Get all known symptoms
    all_symptoms = get_all_symptoms()
    
    # Check if normalized is already a known symptom
    if normalized in all_symptoms:
        return normalized, 1.0
    
    # Simple fuzzy matching using character overlap
    best_match = None
    best_score = 0.0
    
    user_clean = normalized.replace("_", "").lower()
    
    for symptom in all_symptoms:
        symptom_clean = symptom.replace("_", "").lower()
        
        # Calculate similarity using longest common subsequence ratio
        score = _calculate_similarity(user_clean, symptom_clean)
        
        if score > best_score and score >= threshold:
            best_score = score
            best_match = symptom
    
    return best_match, best_score


def _calculate_similarity(s1: str, s2: str) -> float:
    """
    Calculate similarity between two strings using multiple methods.
    
    Args:
        s1: First string
        s2: Second string
    
    Returns:
        Similarity score between 0 and 1
    """
    if not s1 or not s2:
        return 0.0
    
    # Method 1: Substring match
    if s1 in s2 or s2 in s1:
        shorter = min(len(s1), len(s2))
        longer = max(len(s1), len(s2))
        return shorter / longer
    
    # Method 2: Character overlap (Jaccard-like)
    set1 = set(s1)
    set2 = set(s2)
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    char_similarity = intersection / union if union > 0 else 0
    
    # Method 3: Common prefix/suffix
    common_prefix = 0
    for i in range(min(len(s1), len(s2))):
        if s1[i] == s2[i]:
            common_prefix += 1
        else:
            break
    prefix_score = common_prefix / max(len(s1), len(s2))
    
    # Combine scores
    return (char_similarity * 0.6 + prefix_score * 0.4)


def extract_keywords(text: str) -> List[str]:
    """
    Extract symptom keywords from free-form text description.
    
    Feature 4.3: Keyword extraction for symptom normalization
    
    Args:
        text: Free-form text description of symptoms
    
    Returns:
        List of extracted and normalized symptom keywords
    """
    text_lower = text.lower().strip()
    extracted = []
    
    # Apply keyword patterns
    for pattern, symptom in KEYWORD_PATTERNS.items():
        if re.search(pattern, text_lower):
            if symptom not in extracted:
                extracted.append(symptom)
    
    # Also try to extract individual words and normalize them
    words = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        if len(word) >= 3:  # Skip very short words
            normalized = normalize_symptom(word)
            # Check if it's a known symptom
            if normalized in get_all_symptoms() and normalized not in extracted:
                extracted.append(normalized)
    
    return extracted


def normalize_symptom_with_details(raw_symptom: str) -> Dict:
    """
    Enhanced symptom normalization with full details.
    
    Feature 4.3 Complete Implementation:
    - Handles variations like "itchy skin" → "itching"
    - Handles "red spots" → "redness"
    - Handles "very itchy" → "itching" + severity flag
    - Uses fuzzy matching for unknown inputs
    - Extracts keywords from descriptions
    
    Args:
        raw_symptom: Raw user input symptom string
    
    Returns:
        Dictionary with normalization details:
        {
            "original": str,
            "normalized": str,
            "severity": str ("high", "moderate", "low", "normal"),
            "has_severity_modifier": bool,
            "fuzzy_match_score": float,
            "extracted_keywords": List[str],
            "confidence": str ("exact", "alias", "fuzzy", "keyword", "unknown")
        }
    """
    original = raw_symptom.strip()
    
    # Step 1: Extract severity flag
    normalized, severity, has_modifier = extract_severity_flag(original)
    
    # Step 2: Check if it's an exact match or alias
    if normalized in get_all_symptoms():
        return {
            "original": original,
            "normalized": normalized,
            "severity": severity,
            "has_severity_modifier": has_modifier,
            "fuzzy_match_score": 1.0,
            "extracted_keywords": [normalized],
            "confidence": "exact" if normalized == original.lower().replace(" ", "_") else "alias"
        }
    
    # Step 3: Try fuzzy matching
    fuzzy_match, fuzzy_score = fuzzy_match_symptom(original)
    if fuzzy_match and fuzzy_score >= 0.6:
        return {
            "original": original,
            "normalized": fuzzy_match,
            "severity": severity,
            "has_severity_modifier": has_modifier,
            "fuzzy_match_score": fuzzy_score,
            "extracted_keywords": [fuzzy_match],
            "confidence": "fuzzy"
        }
    
    # Step 4: Try keyword extraction
    keywords = extract_keywords(original)
    if keywords:
        return {
            "original": original,
            "normalized": keywords[0],  # Primary keyword
            "severity": severity,
            "has_severity_modifier": has_modifier,
            "fuzzy_match_score": 0.0,
            "extracted_keywords": keywords,
            "confidence": "keyword"
        }
    
    # Step 5: Return as unknown
    return {
        "original": original,
        "normalized": normalized,
        "severity": severity,
        "has_severity_modifier": has_modifier,
        "fuzzy_match_score": 0.0,
        "extracted_keywords": [],
        "confidence": "unknown"
    }


def normalize_symptoms_batch(raw_symptoms: List[str]) -> List[Dict]:
    """
    Normalize a batch of symptoms with full details.
    
    Args:
        raw_symptoms: List of raw symptom strings
    
    Returns:
        List of normalization result dictionaries
    """
    return [normalize_symptom_with_details(s) for s in raw_symptoms]


def get_severity_summary(symptoms: List[str]) -> Dict:
    """
    Get a summary of severity levels from a list of symptoms.
    
    Args:
        symptoms: List of raw symptom strings
    
    Returns:
        Dictionary with severity summary:
        {
            "overall_severity": str,
            "high_severity_symptoms": List[str],
            "moderate_severity_symptoms": List[str],
            "low_severity_symptoms": List[str],
            "normal_symptoms": List[str]
        }
    """
    high = []
    moderate = []
    low = []
    normal = []
    
    for symptom in symptoms:
        result = normalize_symptom_with_details(symptom)
        severity = result["severity"]
        normalized = result["normalized"]
        
        if severity == "high":
            high.append(normalized)
        elif severity == "moderate":
            moderate.append(normalized)
        elif severity == "low":
            low.append(normalized)
        else:
            normal.append(normalized)
    
    # Determine overall severity
    if high:
        overall = "high"
    elif moderate:
        overall = "moderate"
    elif low:
        overall = "low"
    else:
        overall = "normal"
    
    return {
        "overall_severity": overall,
        "high_severity_symptoms": high,
        "moderate_severity_symptoms": moderate,
        "low_severity_symptoms": low,
        "normal_symptoms": normal,
        "total_symptoms": len(symptoms)
    }


# =============================================================================
# Exposed Methods (Feature 4.3)
# =============================================================================

__all__ = [
    # Core matching functions
    "match_symptoms",
    "normalize_symptom",
    "calculate_alignment_score",
    
    # Enhanced normalization (Feature 4.3)
    "normalize_symptom_with_details",
    "normalize_symptoms_batch",
    "extract_severity_flag",
    "fuzzy_match_symptom",
    "extract_keywords",
    "get_severity_summary",
    
    # Helper functions
    "get_disease_symptoms",
    "get_all_symptoms",
    "get_symptoms_by_category",
    "check_contradictory_symptoms",
    "adjust_confidence_based_on_symptoms",
    "find_best_matching_diseases",
    "get_symptom_severity_indicators",
    
    # Data exports
    "DISEASE_SYMPTOMS",
    "SYMPTOM_ALIASES",
    "CONTRADICTORY_SYMPTOMS",
    "SEVERITY_MODIFIERS",
]
