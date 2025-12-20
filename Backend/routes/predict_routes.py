from __future__ import annotations

import logging
import traceback
from flask import Blueprint, current_app, jsonify, request
from typing import Dict, Any, List

from modules.image_processor import process_image, validate_image
from modules import predictor
from modules import symptom_matcher
from modules import severity_analyzer
from modules import recommendation_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

predict_bp = Blueprint("predict", __name__)

# --- Helper Functions ---

def _allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", {"jpg", "jpeg", "png"})

def _extract_symptoms(symptoms_str: str | None) -> List[str]:
    if not symptoms_str:
        return []
    # Split by comma and strip whitespace
    return [s.strip() for s in symptoms_str.split(",") if s.strip()]

def _get_all_symptoms() -> List[str]:
    """Helper to collect all unique symptoms from the knowledge base."""
    all_symptoms = set()
    for disease_data in symptom_matcher.DISEASE_SYMPTOMS.values():
        all_symptoms.update(disease_data.get("common", set()))
        all_symptoms.update(disease_data.get("optional", set()))
        all_symptoms.update(disease_data.get("severity_indicators", set()))
    return sorted(list(all_symptoms))

# --- API Endpoints ---

@predict_bp.post("/predict")
def predict():
    """
    Main prediction endpoint.
    Handles image upload, prediction, symptom analysis, and recommendation generation.
    """
    try:
        # 1. Request Validation
        if "image" not in request.files:
            return jsonify({
                "success": False,
                "error": {
                    "code": "MISSING_FILE",
                    "message": "No image file provided in request"
                }
            }), 400

        file = request.files["image"]
        if not file or not file.filename:
            return jsonify({
                "success": False,
                "error": {
                    "code": "EMPTY_FILENAME",
                    "message": "No file selected"
                }
            }), 400

        if not _allowed_file(file.filename):
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": "Unsupported file type",
                    "details": "Allowed types: jpg, jpeg, png"
                }
            }), 400

        # Validate image content
        is_valid, error_msg = validate_image(file)
        if not is_valid:
            return jsonify({
                "success": False,
                "error": {
                    "code": "INVALID_IMAGE_CONTENT",
                    "message": error_msg or "File is not a valid image"
                }
            }), 400

        # Extract symptoms if provided
        symptoms_input = request.form.get("symptoms", "")
        user_symptoms = _extract_symptoms(symptoms_input)

        # 2. Image Preprocessing
        try:
            # Note: process_image might raise ValueError
            img_array = process_image(file)
        except Exception as e:
            logger.error(f"Preprocessing error: {e}")
            return jsonify({
                "success": False,
                "error": {
                    "code": "PREPROCESSING_FAILED",
                    "message": "Failed to process image",
                    "details": str(e)
                }
            }), 400 # Bad request if image is malformed

        # 3. ML Prediction
        try:
            if not predictor.is_model_loaded():
                # Attempt to auto-load if not loaded (or return 503)
                # For now, return error to ensure proper startup
                return jsonify({
                    "success": False,
                    "error": {
                        "code": "MODEL_NOT_READY",
                        "message": "Model is not loaded. Service unavailable."
                    }
                }), 503

            prediction_result = predictor.predict_disease(img_array)
            
            predicted_disease = prediction_result["predicted_disease"]
            confidence = prediction_result["confidence"]
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            logger.error(traceback.format_exc())
            return jsonify({
                "success": False,
                "error": {
                    "code": "PREDICTION_FAILED",
                    "message": "Internal error during model inference"
                }
            }), 500

        # 4. Symptom Matching
        symptom_analysis = symptom_matcher.match_symptoms(predicted_disease, user_symptoms)

        # 5. Severity Analysis
        severity_result = severity_analyzer.calculate_severity_score(
            predicted_disease,
            confidence,
            user_symptoms
        )
        severity_level = severity_result["severity_level"]

        # 6. Generate Recommendations
        recommendations = recommendation_engine.generate_recommendations(
            predicted_disease,
            severity_level
        )

        # 7. Construct Response
        response_data = {
            "success": True,
            "prediction": {
                "disease": predicted_disease,
                "confidence": confidence,
                "confidence_level": prediction_result["confidence_level"],
                "alternative_possibilities": prediction_result["top_predictions"][1:] # Exclude top 1
            },
            "symptom_analysis": {
                "match_percentage": symptom_analysis["match_percentage"],
                "alignment": symptom_analysis["match_status"],
                "matched_symptoms": symptom_analysis["matched_symptoms"],
                "message": symptom_analysis["feedback"]
            },
            "severity": {
                "level": severity_level,
                "score": severity_result["score"],
                "explanation": severity_result["reasoning"],
                "urgency": recommendations["when_to_see_doctor"] # Map urgency roughly to this field
            },
            "recommendations": recommendations,
            "disclaimer": "This is an AI-powered assessment and does not replace professional medical advice. Please consult a dermatologist for accurate diagnosis and treatment."
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Unexpected error in /predict: {e}")
        logger.error(traceback.format_exc())
        return jsonify({
            "success": False,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }), 500


@predict_bp.get("/health")
def health_check():
    """
    Service health check endpoint.
    """
    model_info = predictor.get_model_info()
    status = "healthy" if model_info.get("loaded") else "degraded"
    
    return jsonify({
        "status": status,
        "model_loaded": model_info.get("loaded", False),
        "version": "1.0.0"
    })


@predict_bp.get("/diseases")
def get_supported_diseases():
    """
    List all supported diseases.
    """
    class_names = predictor.get_class_names()
    return jsonify({
        "diseases": class_names,
        "count": len(class_names)
    })


@predict_bp.get("/symptoms")
def get_available_symptoms():
    """
    List all symptoms known to the system.
    """
    symptoms = _get_all_symptoms()
    return jsonify({
        "symptoms": symptoms,
        "count": len(symptoms)
    })
