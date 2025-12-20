"""
Recommendation Engine
Generates personalized health recommendations based on disease prediction and severity.
"""

from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Knowledge Base for Recommendations
RECOMMENDATION_DB = {
    "Acne": {
        "general_advice": "Acne is a common skin condition that happens when hair follicles become plugged with oil and dead skin cells.",
        "mild": {
            "immediate_care": ["Wash affected area gently twice a day", "Avoid touching or picking at the face"],
            "home_remedies": ["Over-the-counter benzoyl peroxide or salicylic acid", "Tea tree oil"],
            "when_to_see_doctor": "If over-the-counter products don't work after a few months."
        },
        "moderate": {
            "immediate_care": ["Maintain a strict skincare routine", "Use non-comedogenic products"],
            "home_remedies": ["Warm compresses for cysts"],
            "when_to_see_doctor": "If you have painful cysts or nodules."
        },
        "severe": {
            "immediate_care": ["Do not squeeze or pop cysts (causes scarring)", "Keep hair clean and off the face"],
            "home_remedies": ["Cold compresses to reduce pain/swelling"],
            "when_to_see_doctor": "Immediately. Prescription medication (retinoids, antibiotics) is likely needed to prevent scarring."
        }
    },
    "Eczema": {
        "general_advice": "Eczema (atopic dermatitis) causes dry, itchy, and inflamed skin. It's common in children but can occur at any age.",
        "mild": {
            "immediate_care": ["Moisturize immediately after bathing", "Wear soft, breathable fabrics like cotton"],
            "home_remedies": ["Coconut oil", "Colloidal oatmeal baths"],
            "when_to_see_doctor": "If itching is mild but persistent."
        },
        "moderate": {
            "immediate_care": ["Avoid known triggers (soaps, detergents, stress)", "Take short, lukewarm showers"],
            "home_remedies": ["Wet wrap therapy"],
            "when_to_see_doctor": "If sleep is disturbed by itching or if signs of infection appear."
        },
        "severe": {
            "immediate_care": ["Cover affected areas to prevent scratching", "Use prescribed topical creams"],
            "home_remedies": ["Bleach baths (consult doctor first)"],
            "when_to_see_doctor": "Immediately. You may need systemic treatments or phototherapy."
        }
    },
    "Melanoma": {
        "general_advice": "Melanoma is the most serious type of skin cancer. Early detection is critical.",
        "mild": { # Early stage
            "immediate_care": ["Protect skin from sun exposure", "Monitor the lesion for changes"],
            "home_remedies": ["None - Medical evaluation is required"],
            "when_to_see_doctor": "Immediately. All suspected melanomas require professional biopsy."
        },
        "moderate": {
            "immediate_care": ["Avoid sun exposure entirely on the area", "Document changes with photos"],
            "home_remedies": ["None - Medical evaluation is required"],
            "when_to_see_doctor": "URGENT. See a dermatologist or oncologist immediately."
        },
        "severe": {
            "immediate_care": ["Seek emergency care if bleeding or ulcerated"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "EMERGENCY. Immediate specialist intervention is required."
        }
    },
    "Basal cell carcinoma": {
        "general_advice": "Basal cell carcinoma is a type of skin cancer. It usually occurs on sun-exposed areas.",
        "mild": {
            "immediate_care": ["Protect from sun", "Cover with bandage if bleeding"],
            "home_remedies": ["None - Requires removal"],
            "when_to_see_doctor": "Schedule an appointment soon for evaluation."
        },
        "moderate": {
            "immediate_care": ["Avoid trauma to the area"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Promptly. Surgical removal is typically required."
        },
        "severe": {
            "immediate_care": ["Keep clean and covered"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Immediately, especially if the lesion is growing rapidly or bleeding heavily."
        }
    },
    "Melanocytic nevi": { # Moles
        "general_advice": "Moles are common skin growths. Most are harmless, but changes can indicate cancer.",
        "mild": {
            "immediate_care": ["Monitor for ABCDE changes (Asymmetry, Border, Color, Diameter, Evolving)"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Routine check-ups are sufficient."
        },
        "moderate": {
            "immediate_care": ["Photograph the mole to track changes"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "If you notice itching, bleeding, or changes in size/color."
        },
        "severe": {
            "immediate_care": ["Do not scratch or irritate"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Immediately. Significant changes require biopsy."
        }
    },
    "Benign keratosis-like lesions": {
        "general_advice": "These include seborrheic keratoses (barnacles of aging) and solar lentigines (sun spots). They are non-cancerous.",
        "mild": {
            "immediate_care": ["Sun protection"],
            "home_remedies": ["None required"],
            "when_to_see_doctor": "For cosmetic removal if desired."
        },
        "moderate": {
            "immediate_care": ["Avoid picking at the lesion"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "If it becomes irritated by clothing or bleeds."
        },
        "severe": {
            "immediate_care": ["Keep clean if irritated"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "If rapid growth occurs (to rule out other conditions)."
        }
    },
    "Actinic keratoses": {
        "general_advice": "Rough, scaly patches on the skin caused by years of sun exposure. They are precancerous.",
        "mild": {
            "immediate_care": ["Strict sun protection (SPF 30+)", "Wear protective clothing"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Schedule a dermatological exam."
        },
        "moderate": {
            "immediate_care": ["Avoid further sun damage"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Promptly. Treatment (freezing, creams) is needed to prevent progression to cancer."
        },
        "severe": {
            "immediate_care": ["Protect from all UV exposure"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Immediately. High risk of developing into squamous cell carcinoma."
        }
    },
    "Vascular lesions": {
        "general_advice": "Common abnormalities of the skin and underlying tissues, typically involving blood vessels.",
        "mild": {
            "immediate_care": ["Avoid trauma"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "If you want cosmetic removal or if it bleeds often."
        },
        "moderate": {
            "immediate_care": ["Apply pressure if bleeding occurs"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "If the lesion is painful or changing rapidly."
        },
        "severe": {
            "immediate_care": ["Protect area from injury"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Immediately if there is ulceration or uncontrollable bleeding."
        }
    },
    "Dermatofibroma": {
        "general_advice": "Small, non-cancerous (benign) skin growths that can appear anywhere on the body.",
        "mild": {
            "immediate_care": ["None specific"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "Not usually necessary unless diagnosis is uncertain."
        },
        "moderate": {
            "immediate_care": ["Avoid shaving over the area"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "If it becomes tender or changes appearance."
        },
        "severe": {
            "immediate_care": ["Monitor for rapid growth"],
            "home_remedies": ["None"],
            "when_to_see_doctor": "If it is painful or growing quickly."
        }
    }
}

# Fallback for unknown diseases
DEFAULT_RECOMMENDATION = {
    "general_advice": "Please consult a healthcare professional for an accurate diagnosis.",
    "immediate_care": ["Keep the area clean and dry", "Monitor for changes"],
    "home_remedies": [],
    "when_to_see_doctor": "If you are concerned about the appearance or symptoms of your skin condition."
}

def generate_recommendations(disease: str, severity_level: str) -> Dict:
    """
    Generate tailored recommendations based on disease and severity.
    
    Args:
        disease: Predicted disease name
        severity_level: 'mild', 'moderate', 'severe', or 'critical'
        
    Returns:
        Dictionary containing recommendations
    """
    # Normalize severity for lookup (critical maps to severe in our DB for now)
    lookup_severity = severity_level.lower()
    if lookup_severity == "critical":
        lookup_severity = "severe"
    elif lookup_severity not in ["mild", "moderate", "severe"]:
        lookup_severity = "mild" # Default fallback
        
    if disease not in RECOMMENDATION_DB:
        logger.warning(f"Disease '{disease}' not found in recommendation DB. Using default.")
        rec = DEFAULT_RECOMMENDATION.copy()
        # Add a severity note
        rec["note"] = f"Severity assessed as {severity_level}."
        return rec
        
    disease_info = RECOMMENDATION_DB[disease]
    severity_info = disease_info.get(lookup_severity, disease_info["mild"])
    
    return {
        "general_advice": disease_info["general_advice"],
        "immediate_care": severity_info["immediate_care"],
        "home_remedies": severity_info["home_remedies"],
        "precautions": ["Avoid picking or scratching", "Protect from direct sunlight"],
        "when_to_see_doctor": severity_info["when_to_see_doctor"]
    }
