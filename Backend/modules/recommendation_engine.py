"""
Feature 6: Recommendation Engine
Generates actionable advice based on prediction results
"""

from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Recommendation database by disease and severity
RECOMMENDATIONS = {
    "Actinic keratoses": {
        "mild": {
            "general_advice": "Actinic keratoses are rough, scaly patches caused by sun damage.",
            "immediate_care": ["Protect from sun", "Apply SPF 30+ sunscreen daily"],
            "home_remedies": ["Use fragrance-free moisturizers", "Apply aloe vera"],
            "precautions": ["Avoid peak sun hours", "Wear protective clothing"],
            "lifestyle_tips": ["Regular skin self-exams", "Healthy diet with antioxidants"],
            "when_to_see_doctor": "If patch grows, bleeds, or changes appearance"
        },
        "moderate": {
            "general_advice": "Multiple actinic keratoses require professional evaluation.",
            "immediate_care": ["Schedule dermatologist appointment", "Document changes"],
            "home_remedies": ["Continue sun protection", "Keep skin moisturized"],
            "precautions": ["Do not remove lesions yourself", "Avoid tanning beds"],
            "lifestyle_tips": ["Annual skin cancer screenings"],
            "when_to_see_doctor": "As soon as possible for evaluation"
        },
        "severe": {
            "general_advice": "Severe actinic keratoses increase skin cancer risk significantly.",
            "immediate_care": ["Seek dermatological care promptly"],
            "home_remedies": ["Gentle skin care only"],
            "precautions": ["Do not delay medical consultation"],
            "lifestyle_tips": ["Regular dermatology follow-ups"],
            "when_to_see_doctor": "Immediately - professional treatment needed"
        }
    },
    "Basal cell carcinoma": {
        "mild": {
            "general_advice": "Basal cell carcinoma is common skin cancer requiring treatment.",
            "immediate_care": ["Schedule dermatologist appointment", "Protect from sun"],
            "home_remedies": ["Keep area clean and dry"],
            "precautions": ["Do not pick or scratch", "Avoid sun exposure"],
            "lifestyle_tips": ["Learn skin self-exam techniques"],
            "when_to_see_doctor": "As soon as possible for diagnosis"
        },
        "severe": {
            "general_advice": "Advanced basal cell carcinoma requires immediate intervention.",
            "immediate_care": ["Seek immediate dermatological care"],
            "home_remedies": [],
            "precautions": ["Follow all medical advice"],
            "lifestyle_tips": ["Build support system"],
            "when_to_see_doctor": "Immediately - urgent care needed"
        }
    },
    "Melanoma": {
        "mild": {
            "general_advice": "Any melanoma suspicion requires immediate professional evaluation.",
            "immediate_care": ["See dermatologist immediately", "Photograph the lesion"],
            "home_remedies": [],
            "precautions": ["Do not delay care", "Do not irritate area"],
            "lifestyle_tips": ["Learn ABCDEs of melanoma", "Monthly skin self-exams"],
            "when_to_see_doctor": "Immediately - urgent evaluation required"
        },
        "severe": {
            "general_advice": "This requires immediate medical attention.",
            "immediate_care": ["Go to dermatologist or ER today"],
            "home_remedies": [],
            "precautions": ["Do not delay for any reason"],
            "lifestyle_tips": ["Connect with melanoma support resources"],
            "when_to_see_doctor": "Immediately - emergency care appropriate"
        }
    },
    "Benign keratosis-like lesions": {
        "mild": {
            "general_advice": "Benign keratoses are non-cancerous and usually harmless.",
            "immediate_care": ["No urgent care needed", "Monitor for changes"],
            "home_remedies": ["Keep area clean", "Avoid picking"],
            "precautions": ["Do not remove yourself", "Watch for changes"],
            "lifestyle_tips": ["Normal part of aging", "Good skin health"],
            "when_to_see_doctor": "If growth changes or becomes irritated"
        }
    },
    "Dermatofibroma": {
        "mild": {
            "general_advice": "Dermatofibromas are benign nodules, usually harmless.",
            "immediate_care": ["No urgent care needed"],
            "home_remedies": ["Leave area alone", "Keep skin moisturized"],
            "precautions": ["Avoid picking", "Protect from trauma"],
            "lifestyle_tips": ["Removal is optional and cosmetic"],
            "when_to_see_doctor": "If it grows rapidly or becomes painful"
        }
    },
    "Melanocytic nevi": {
        "mild": {
            "general_advice": "Moles are usually harmless. Monitor using ABCDE criteria.",
            "immediate_care": ["No urgent care for stable moles"],
            "home_remedies": ["Protect from sun", "Use sunscreen"],
            "precautions": ["Never remove moles yourself", "Monitor monthly"],
            "lifestyle_tips": ["Regular skin self-exams", "Track mole changes"],
            "when_to_see_doctor": "If mole changes in size, shape, or color"
        }
    },
    "Vascular lesions": {
        "mild": {
            "general_advice": "Vascular lesions are blood vessel conditions, usually benign.",
            "immediate_care": ["No urgent care typically needed"],
            "home_remedies": ["Protect from trauma"],
            "precautions": ["Avoid activities causing bleeding"],
            "lifestyle_tips": ["Treatment often cosmetic"],
            "when_to_see_doctor": "If it bleeds frequently or grows"
        }
    }
}

DEFAULT_RECOMMENDATIONS = {
    "general_advice": "This condition should be evaluated by a healthcare professional.",
    "immediate_care": ["Keep area clean", "Avoid irritation", "Protect from sun"],
    "home_remedies": ["Use gentle skincare", "Keep moisturized"],
    "precautions": ["Do not self-diagnose", "Monitor for changes"],
    "lifestyle_tips": ["Maintain skin health", "Stay hydrated"],
    "when_to_see_doctor": "If condition persists or worsens"
}


def get_disclaimer() -> str:
    """Get the standard medical disclaimer."""
    return (
        "IMPORTANT: This AI analysis is for informational purposes only and does NOT "
        "constitute medical diagnosis or advice. Always consult a qualified healthcare "
        "professional for proper diagnosis and treatment. Do not delay seeking medical "
        "care based on this analysis."
    )


def generate_recommendations(
    disease: str,
    severity: str,
    symptoms: List[str],
    confidence: float = 1.0
) -> Dict:
    """Generate personalized recommendations."""
    # Get base recommendations
    disease_recs = RECOMMENDATIONS.get(disease, {})
    if not disease_recs:
        for key in RECOMMENDATIONS:
            if key.lower() == disease.lower():
                disease_recs = RECOMMENDATIONS[key]
                break
    
    recs = disease_recs.get(severity, disease_recs.get("mild", DEFAULT_RECOMMENDATIONS))
    if not recs:
        recs = DEFAULT_RECOMMENDATIONS
    
    result = recs.copy()
    
    # Add low confidence warning
    if confidence < 0.6:
        result["general_advice"] = (
            result.get("general_advice", "") + 
            " Note: AI confidence is low - professional evaluation is especially important."
        )
    
    # Add severity warning
    if severity in ["severe", "critical"]:
        result["warning"] = "This condition appears serious. Seek professional care promptly."
    
    return result


def format_recommendations(raw_recommendations: Dict) -> Dict:
    """Format recommendations for display."""
    return {k: [i for i in v if i] if isinstance(v, list) else v 
            for k, v in raw_recommendations.items()}
