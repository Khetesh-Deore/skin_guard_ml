"""
Feature 7: API Routes & Request Handling
Module: routes/predict_routes.py

Main Prediction Endpoint: POST /api/predict
"""

from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from modules.image_processor import process_image, validate_image
from modules import predictor
from modules.symptom_matcher import match_symptoms, get_all_symptoms
from modules.severity_analyzer import analyze_severity
from modules.recommendation_engine import generate_recommendations, get_disclaimer


predict_bp = Blueprint("predict", __name__)


def _allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", set())


def _parse_symptoms(symptoms_str: str) -> list:
    """Parse comma-separated symptoms string into list"""
    if not symptoms_str:
        return []
    return [s.strip().lower().replace(" ", "_") for s in symptoms_str.split(",") if s.strip()]


@predict_bp.post("/predict")
def predict():
    """
    Main Prediction Endpoint
    
    Route: POST /api/predict
    
    Request Format:
        Content-Type: multipart/form-data
        Fields:
        - image: file (required)
        - symptoms: string (optional, comma-separated)
    
    Processing Flow:
        1. Validate request
        2. Validate & extract image file
        3. Parse symptoms (if provided)
        4. Image preprocessing
        5. ML prediction
        6. Symptom matching (if symptoms provided)
        7. Severity analysis
        8. Generate recommendations
        9. Format response
        10. Return JSON response
    """
    
    # Step 1 & 2: Validate request and extract image
    if "image" not in request.files:
        return jsonify({"success": False, "error": "Missing file field 'image'"}), 400

    file = request.files["image"]
    if not file or not file.filename:
        return jsonify({"success": False, "error": "No file selected"}), 400

    if not _allowed_file(file.filename):
        return jsonify({"success": False, "error": "Unsupported file type. Use jpg, jpeg, or png."}), 400

    # Validate image
    ok, err = validate_image(file)
    if not ok:
        return jsonify({"success": False, "error": err or "Invalid image"}), 400

    # Step 3: Parse symptoms (if provided)
    symptoms_str = request.form.get("symptoms", "")
    user_symptoms = _parse_symptoms(symptoms_str)

    try:
        # Step 4: Image preprocessing
        image_array = process_image(file)
        
        # Step 5: ML prediction
        if not predictor.is_model_loaded():
            return jsonify({
                "success": False, 
                "error": "Model not loaded. Please try again later."
            }), 503
        
        prediction_result = predictor.predict_disease(image_array)
        
        predicted_disease = prediction_result["predicted_disease"]
        confidence = prediction_result["confidence"]
        confidence_level = prediction_result["confidence_level"]
        
        # Step 6: Symptom matching (if symptoms provided)
        symptom_analysis = None
        if user_symptoms:
            symptom_analysis = match_symptoms(predicted_disease, user_symptoms)
        
        # Step 7: Severity analysis
        severity_result = analyze_severity(
            disease=predicted_disease,
            confidence=confidence,
            symptoms=user_symptoms
        )
        
        # Step 8: Generate recommendations
        recommendations = generate_recommendations(
            disease=predicted_disease,
            severity=severity_result["level"],
            symptoms=user_symptoms,
            confidence=confidence
        )
        
        # Step 9 & 10: Format and return response
        response = {
            "success": True,
            "prediction": {
                "disease": predicted_disease,
                "confidence": confidence,
                "confidence_level": confidence_level,
                "alternative_possibilities": prediction_result.get("top_predictions", [])[1:],
                "needs_review": prediction_result.get("needs_review", False),
                "review_reason": prediction_result.get("review_reason")
            },
            "symptom_analysis": symptom_analysis,
            "severity": severity_result,
            "recommendations": recommendations,
            "disclaimer": get_disclaimer()
        }
        
        return jsonify(response), 200
        
    except predictor.ModelNotLoadedError as e:
        current_app.logger.error(f"Model not loaded: {str(e)}")
        return jsonify({"success": False, "error": "Model not available. Please try again later."}), 503
    except ValueError as e:
        current_app.logger.error(f"Validation error: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Prediction failed: {str(e)}")
        return jsonify({"success": False, "error": "Analysis failed. Please try again."}), 500


@predict_bp.get("/diseases")
def get_diseases():
    """
    Get list of supported diseases
    
    Route: GET /api/diseases
    """
    model_info = predictor.get_model_info()
    diseases = model_info.get("diseases", [])
    
    return jsonify({
        "diseases": diseases,
        "count": len(diseases)
    })


@predict_bp.get("/symptoms")
def get_symptoms():
    """
    Get list of available symptoms
    
    Route: GET /api/symptoms
    """
    symptoms = get_all_symptoms()
    
    return jsonify({
        "symptoms": symptoms,
        "count": len(symptoms)
    })

