"""
Feature 7: API Routes & Request Handling
Module: routes/predict_routes.py

Main Prediction Endpoint: POST /api/predict

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
10. Clean up temporary files
11. Return JSON response
"""

from __future__ import annotations

import os
import tempfile
import logging
from typing import Dict, List, Optional, Tuple

from flask import Blueprint, current_app, jsonify, request
from werkzeug.utils import secure_filename

from modules.image_processor import process_image, validate_image
from modules import predictor
from modules.symptom_matcher import match_symptoms, get_all_symptoms
from modules.severity_analyzer import analyze_severity, check_urgency_flags
from modules.recommendation_engine import (
    generate_recommendations, 
    get_disclaimer,
    format_recommendations
)
from modules.disease_descriptions import get_disease_description

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
predict_bp = Blueprint("predict", __name__)

# =============================================================================
# Feature 7.3: Error Handling Strategy
# =============================================================================

# Error Types:
# 1. Validation Errors (400) - No image, invalid file type, file too large, corrupted
# 2. Processing Errors (500) - Preprocessing failed, model error, unexpected exception
# 3. Rate Limiting (429) - Too many requests from same IP

ERROR_CODES = {
    # ==========================================================================
    # 1. Validation Errors (400)
    # ==========================================================================
    "MISSING_IMAGE": {
        "code": "MISSING_IMAGE",
        "message": "No image file provided",
        "details": "Request must include an 'image' field with a file",
        "status_code": 400,
        "category": "validation"
    },
    "NO_FILE_SELECTED": {
        "code": "NO_FILE_SELECTED",
        "message": "No file was selected",
        "details": "Please select an image file to upload",
        "status_code": 400,
        "category": "validation"
    },
    "INVALID_FILE_TYPE": {
        "code": "INVALID_FILE_TYPE",
        "message": "Unsupported file type",
        "details": "File type must be jpg, jpeg, or png",
        "status_code": 400,
        "category": "validation"
    },
    "INVALID_IMAGE": {
        "code": "INVALID_IMAGE",
        "message": "Uploaded file is not a valid image",
        "details": "The file could not be processed as an image",
        "status_code": 400,
        "category": "validation"
    },
    "IMAGE_TOO_LARGE": {
        "code": "IMAGE_TOO_LARGE",
        "message": "Image file is too large",
        "details": "Maximum file size is 10MB",
        "status_code": 413,
        "category": "validation"
    },
    "CORRUPTED_IMAGE": {
        "code": "CORRUPTED_IMAGE",
        "message": "Image file appears to be corrupted",
        "details": "The image file could not be read. Please try a different image.",
        "status_code": 400,
        "category": "validation"
    },
    "INVALID_SYMPTOMS": {
        "code": "INVALID_SYMPTOMS",
        "message": "Invalid symptoms format",
        "details": "Symptoms should be a comma-separated string",
        "status_code": 400,
        "category": "validation"
    },
    
    # ==========================================================================
    # 2. Processing Errors (500)
    # ==========================================================================
    "MODEL_NOT_LOADED": {
        "code": "MODEL_NOT_LOADED",
        "message": "Prediction model is not available",
        "details": "The ML model is not loaded. Please try again later.",
        "status_code": 503,
        "category": "processing"
    },
    "PROCESSING_ERROR": {
        "code": "PROCESSING_ERROR",
        "message": "Image processing failed",
        "details": "Unable to process the uploaded image",
        "status_code": 500,
        "category": "processing"
    },
    "PREDICTION_ERROR": {
        "code": "PREDICTION_ERROR",
        "message": "Prediction failed",
        "details": "An error occurred during analysis",
        "status_code": 500,
        "category": "processing"
    },
    "INTERNAL_ERROR": {
        "code": "INTERNAL_ERROR",
        "message": "Internal server error",
        "details": "An unexpected error occurred. Please try again.",
        "status_code": 500,
        "category": "processing"
    },
    
    # ==========================================================================
    # 3. Rate Limiting (429)
    # ==========================================================================
    "RATE_LIMIT_EXCEEDED": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Too many requests",
        "details": "You have exceeded the rate limit. Please wait before making more requests.",
        "status_code": 429,
        "category": "rate_limit"
    },
}

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    "enabled": True,
    "requests_per_minute": 30,
    "requests_per_hour": 200,
    "burst_limit": 10
}

# In-memory rate limit tracking (for simple implementation)
# In production, use Redis or similar
_rate_limit_store: Dict[str, Dict] = {}


def _get_client_ip() -> str:
    """Get client IP address from request."""
    # Check for forwarded IP (behind proxy)
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr or 'unknown'


def _check_rate_limit() -> Tuple[bool, Optional[Dict]]:
    """
    Check if the current request exceeds rate limits.
    
    Returns:
        Tuple of (is_allowed, error_response_if_not_allowed)
    """
    if not RATE_LIMIT_CONFIG.get("enabled", False):
        return True, None
    
    import time
    
    client_ip = _get_client_ip()
    current_time = time.time()
    
    # Initialize or get client's rate limit data
    if client_ip not in _rate_limit_store:
        _rate_limit_store[client_ip] = {
            "minute_requests": [],
            "hour_requests": []
        }
    
    client_data = _rate_limit_store[client_ip]
    
    # Clean old entries
    minute_ago = current_time - 60
    hour_ago = current_time - 3600
    
    client_data["minute_requests"] = [
        t for t in client_data["minute_requests"] if t > minute_ago
    ]
    client_data["hour_requests"] = [
        t for t in client_data["hour_requests"] if t > hour_ago
    ]
    
    # Check limits
    if len(client_data["minute_requests"]) >= RATE_LIMIT_CONFIG["requests_per_minute"]:
        logger.warning(f"Rate limit exceeded for IP: {client_ip} (per minute)")
        return False, _create_error_response("RATE_LIMIT_EXCEEDED", 
            f"Rate limit exceeded. Max {RATE_LIMIT_CONFIG['requests_per_minute']} requests per minute.")
    
    if len(client_data["hour_requests"]) >= RATE_LIMIT_CONFIG["requests_per_hour"]:
        logger.warning(f"Rate limit exceeded for IP: {client_ip} (per hour)")
        return False, _create_error_response("RATE_LIMIT_EXCEEDED",
            f"Rate limit exceeded. Max {RATE_LIMIT_CONFIG['requests_per_hour']} requests per hour.")
    
    # Record this request
    client_data["minute_requests"].append(current_time)
    client_data["hour_requests"].append(current_time)
    
    return True, None


def _create_error_response(error_key: str, custom_details: str = None) -> Tuple[Dict, int]:
    """
    Create a standardized error response.
    
    Feature 7.3: Error Handling Strategy
    
    Response Structure:
    - Always return JSON
    - Include error code for client handling
    - Provide user-friendly message
    - Log detailed error server-side
    
    Args:
        error_key: Key from ERROR_CODES
        custom_details: Optional custom details message
    
    Returns:
        Tuple of (response_dict, status_code)
    """
    error_info = ERROR_CODES.get(error_key, ERROR_CODES["INTERNAL_ERROR"])
    
    response = {
        "success": False,
        "error": {
            "code": error_info["code"],
            "message": error_info["message"],
            "details": custom_details or error_info["details"],
            "category": error_info.get("category", "unknown")
        }
    }
    
    status_code = error_info.get("status_code", 500)
    
    # Log the error server-side with details
    log_message = f"Error {error_info['code']}: {error_info['message']}"
    if custom_details:
        log_message += f" - {custom_details}"
    
    if status_code >= 500:
        logger.error(log_message)
    elif status_code == 429:
        logger.warning(log_message)
    else:
        logger.info(log_message)
    
    return response, status_code


def _log_error(error_key: str, exception: Exception = None, context: Dict = None):
    """
    Log error with full details server-side.
    
    Args:
        error_key: Error code key
        exception: Optional exception object
        context: Optional context dictionary
    """
    error_info = ERROR_CODES.get(error_key, {})
    
    log_data = {
        "error_code": error_key,
        "category": error_info.get("category", "unknown"),
        "client_ip": _get_client_ip() if request else "unknown",
    }
    
    if context:
        log_data.update(context)
    
    if exception:
        log_data["exception_type"] = type(exception).__name__
        log_data["exception_message"] = str(exception)
        logger.error(f"Error occurred: {log_data}", exc_info=True)
    else:
        logger.warning(f"Error occurred: {log_data}")


# =============================================================================
# Feature 7.4: Request Validation
# =============================================================================

# Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/jpg"}


def _allowed_file(filename: str) -> bool:
    """
    Check if file extension is allowed.
    
    Args:
        filename: Name of the uploaded file
    
    Returns:
        True if file extension is allowed
    """
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    allowed = current_app.config.get("ALLOWED_EXTENSIONS", ALLOWED_EXTENSIONS)
    return ext in allowed


def _check_file_size(file) -> Tuple[bool, Optional[str]]:
    """
    Check if file size is within limits.
    
    Args:
        file: File object from request
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Get file size by seeking to end
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    
    max_size = current_app.config.get("MAX_CONTENT_LENGTH", MAX_FILE_SIZE)
    
    if size > max_size:
        size_mb = size / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        return False, f"File size ({size_mb:.1f}MB) exceeds maximum ({max_mb:.0f}MB)"
    
    return True, None


def validate_prediction_request(req) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate the prediction request.
    
    Feature 7.4: Request Validation
    
    Pre-Processing Checks:
    1. Request method is POST
    2. Content-Type is multipart/form-data
    3. 'image' field exists in request.files
    4. File has allowed extension
    5. File size < MAX_FILE_SIZE
    6. Optional: symptoms field is string (if present)
    
    Args:
        req: Flask request object
    
    Returns:
        Tuple of (is_valid, error_message, error_code)
    """
    # Check 1: Request method is POST
    if req.method != 'POST':
        return False, "Method not allowed. Use POST.", "METHOD_NOT_ALLOWED"
    
    # Check 2: Content-Type is multipart/form-data
    content_type = req.content_type or ""
    if not content_type.startswith('multipart/form-data'):
        return False, "Content-Type must be multipart/form-data", "INVALID_CONTENT_TYPE"
    
    # Check 3: 'image' field exists in request.files
    if 'image' not in req.files:
        return False, "No image uploaded", "MISSING_IMAGE"
    
    file = req.files['image']
    
    # Check 3b: File is not empty
    if not file or file.filename == '':
        return False, "Empty filename", "NO_FILE_SELECTED"
    
    # Check 4: File has allowed extension
    if not _allowed_file(file.filename):
        return False, "Invalid file type. Allowed: jpg, jpeg, png", "INVALID_FILE_TYPE"
    
    # Check 5: File size < MAX_FILE_SIZE
    size_valid, size_error = _check_file_size(file)
    if not size_valid:
        return False, size_error, "IMAGE_TOO_LARGE"
    
    # Check 6: Optional symptoms field is string (if present)
    if 'symptoms' in req.form:
        symptoms = req.form.get('symptoms')
        if symptoms is not None and not isinstance(symptoms, str):
            return False, "Symptoms must be a string", "INVALID_SYMPTOMS"
    
    return True, None, None


def validate_image_content(file) -> Tuple[bool, Optional[str]]:
    """
    Validate that the file contains valid image data.
    
    Args:
        file: File object from request
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Read first few bytes to check magic numbers
        file.seek(0)
        header = file.read(16)
        file.seek(0)
        
        # Check for JPEG magic number (FFD8FF)
        if header[:3] == b'\xff\xd8\xff':
            return True, None
        
        # Check for PNG magic number (89504E47)
        if header[:8] == b'\x89PNG\r\n\x1a\n':
            return True, None
        
        return False, "File does not appear to be a valid image"
        
    except Exception as e:
        return False, f"Error reading file: {str(e)}"


def get_validation_summary() -> Dict:
    """
    Get a summary of validation rules for documentation.
    
    Returns:
        Dictionary with validation rules
    """
    return {
        "allowed_extensions": list(ALLOWED_EXTENSIONS),
        "max_file_size_mb": MAX_FILE_SIZE / (1024 * 1024),
        "content_type": "multipart/form-data",
        "required_fields": ["image"],
        "optional_fields": ["symptoms"],
        "checks": [
            "Request method is POST",
            "Content-Type is multipart/form-data",
            "'image' field exists in request.files",
            "File has allowed extension (jpg, jpeg, png)",
            "File size < 10MB",
            "Symptoms field is string (if present)"
        ]
    }


def _parse_symptoms(symptoms_str: str) -> List[str]:
    """
    Parse comma-separated symptoms string into list.
    
    Args:
        symptoms_str: Comma-separated symptoms string
    
    Returns:
        List of normalized symptom strings
    """
    if not symptoms_str:
        return []
    
    symptoms = []
    for s in symptoms_str.split(","):
        s = s.strip()
        if s:
            # Normalize: lowercase and replace spaces with underscores
            normalized = s.lower().replace(" ", "_")
            symptoms.append(normalized)
    
    return symptoms


def _format_prediction_response(
    prediction_result: Dict,
    symptom_analysis: Optional[Dict],
    severity_result: Dict,
    recommendations: Dict
) -> Dict:
    """
    Format the complete prediction response according to spec.
    
    Response Format:
    {
        "success": true,
        "prediction": {...},
        "symptom_analysis": {...},
        "severity": {...},
        "recommendations": {...},
        "disclaimer": "..."
    }
    """
    # Get disease name and description
    disease_name = prediction_result["predicted_disease"]
    disease_info = get_disease_description(disease_name)
    
    # Format prediction section
    prediction = {
        "disease": disease_name,
        "confidence": round(prediction_result["confidence"], 4),
        "confidence_level": prediction_result["confidence_level"],
        "description": disease_info.get("description", ""),
        "causes": disease_info.get("causes", ""),
        "common_in": disease_info.get("common_in", ""),
        "alternative_possibilities": []
    }
    
    # Add alternative possibilities (top predictions excluding the main one)
    top_predictions = prediction_result.get("top_predictions", [])
    if len(top_predictions) > 1:
        prediction["alternative_possibilities"] = [
            {
                "disease": p["disease"],
                "confidence": round(p["confidence"], 4),
                "description": get_disease_description(p["disease"]).get("description", "")
            }
            for p in top_predictions[1:4]  # Top 3 alternatives
        ]
    
    # Format symptom analysis section
    formatted_symptom_analysis = None
    if symptom_analysis:
        formatted_symptom_analysis = {
            "match_percentage": symptom_analysis.get("match_percentage", 0),
            "alignment": symptom_analysis.get("alignment", "unknown"),
            "matched_symptoms": symptom_analysis.get("matched_symptoms", []),
            "message": symptom_analysis.get("message", "")
        }
    
    # Format severity section
    severity = {
        "level": severity_result.get("level", "moderate"),
        "urgency": severity_result.get("urgency", "consult_doctor"),
        "explanation": severity_result.get("explanation", ""),
        "score": severity_result.get("score", 0),
        "has_red_flags": severity_result.get("has_red_flags", False)
    }
    
    # Format recommendations section
    formatted_recommendations = {
        "general_advice": recommendations.get("general_advice", ""),
        "immediate_care": recommendations.get("immediate_care", []),
        "home_remedies": recommendations.get("home_remedies", []),
        "precautions": recommendations.get("precautions", []),
        "lifestyle_tips": recommendations.get("lifestyle_tips", []),
        "when_to_see_doctor": recommendations.get("when_to_see_doctor", "")
    }
    
    # Build complete response
    response = {
        "success": True,
        "prediction": prediction,
        "symptom_analysis": formatted_symptom_analysis,
        "severity": severity,
        "recommendations": formatted_recommendations,
        "disclaimer": get_disclaimer()
    }
    
    return response


def _cleanup_temp_file(filepath: str):
    """
    Clean up temporary file if it exists.
    
    Args:
        filepath: Path to temporary file
    """
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"Cleaned up temp file: {filepath}")
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file {filepath}: {e}")


# =============================================================================
# Main Prediction Endpoint
# =============================================================================

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
        10. Clean up temporary files
        11. Return JSON response
    
    Returns:
        JSON response with prediction results or error
    """
    temp_filepath = None
    
    try:
        # =====================================================================
        # Step 0: Check rate limit
        # =====================================================================
        is_allowed, rate_limit_error = _check_rate_limit()
        if not is_allowed:
            return jsonify(rate_limit_error[0]), rate_limit_error[1]
        
        # =====================================================================
        # Step 1: Validate request using validation helper
        # =====================================================================
        is_valid, error_msg, error_code = validate_prediction_request(request)
        if not is_valid:
            logger.warning(f"Request validation failed: {error_msg}")
            return jsonify(*_create_error_response(error_code, error_msg))
        
        # =====================================================================
        # Step 2: Extract and validate image file
        # =====================================================================
        file = request.files["image"]
        
        # Check file size
        size_valid, size_error = _check_file_size(file)
        if not size_valid:
            logger.warning(f"File too large: {size_error}")
            return jsonify(*_create_error_response("IMAGE_TOO_LARGE", size_error))
        
        # Validate image content (magic bytes)
        content_valid, content_error = validate_image_content(file)
        if not content_valid:
            logger.warning(f"Invalid image content: {content_error}")
            return jsonify(*_create_error_response("CORRUPTED_IMAGE", content_error))
        
        # Validate image using image_processor module
        is_valid, error_msg = validate_image(file)
        if not is_valid:
            logger.warning(f"Invalid image: {error_msg}")
            return jsonify(*_create_error_response("INVALID_IMAGE", error_msg))
        
        # Reset file pointer after validation
        file.seek(0)
        
        # =====================================================================
        # Step 3: Parse symptoms (if provided)
        # =====================================================================
        symptoms_str = request.form.get("symptoms", "")
        user_symptoms = _parse_symptoms(symptoms_str)
        logger.info(f"Parsed symptoms: {user_symptoms}")
        
        # =====================================================================
        # Step 4: Image preprocessing
        # =====================================================================
        try:
            image_array = process_image(file)
            logger.info("Image preprocessing completed")
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return jsonify(*_create_error_response("PROCESSING_ERROR", str(e)))
        
        # =====================================================================
        # Step 5: ML prediction
        # =====================================================================
        if not predictor.is_model_loaded():
            logger.error("Model not loaded")
            return jsonify(*_create_error_response("MODEL_NOT_LOADED"))
        
        try:
            prediction_result = predictor.predict_disease(image_array)
            logger.info(f"Prediction: {prediction_result['predicted_disease']} "
                       f"({prediction_result['confidence']:.2%})")
        except predictor.ModelNotLoadedError as e:
            logger.error(f"Model error: {e}")
            return jsonify(*_create_error_response("MODEL_NOT_LOADED"))
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return jsonify(*_create_error_response("PREDICTION_ERROR", str(e)))
        
        predicted_disease = prediction_result["predicted_disease"]
        confidence = prediction_result["confidence"]
        
        # =====================================================================
        # Step 6: Symptom matching (if symptoms provided)
        # =====================================================================
        symptom_analysis = None
        if user_symptoms:
            try:
                symptom_analysis = match_symptoms(predicted_disease, user_symptoms)
                logger.info(f"Symptom match: {symptom_analysis.get('match_percentage', 0)}%")
            except Exception as e:
                logger.warning(f"Symptom matching failed: {e}")
                # Continue without symptom analysis
        
        # =====================================================================
        # Step 7: Severity analysis
        # =====================================================================
        try:
            severity_result = analyze_severity(
                disease=predicted_disease,
                confidence=confidence,
                symptoms=user_symptoms
            )
            logger.info(f"Severity: {severity_result['level']}")
        except Exception as e:
            logger.warning(f"Severity analysis failed: {e}")
            severity_result = {
                "level": "moderate",
                "urgency": "consult_doctor",
                "explanation": "Unable to determine severity. Please consult a healthcare provider."
            }
        
        # =====================================================================
        # Step 8: Generate recommendations
        # =====================================================================
        try:
            recommendations = generate_recommendations(
                disease=predicted_disease,
                severity=severity_result["level"],
                symptoms=user_symptoms,
                confidence=confidence
            )
            logger.info("Recommendations generated")
        except Exception as e:
            logger.warning(f"Recommendation generation failed: {e}")
            recommendations = {
                "general_advice": "Please consult a healthcare provider for proper evaluation.",
                "immediate_care": ["Keep the affected area clean"],
                "home_remedies": [],
                "precautions": ["Avoid irritating the area"],
                "lifestyle_tips": [],
                "when_to_see_doctor": "If symptoms persist or worsen"
            }
        
        # =====================================================================
        # Step 9: Format response
        # =====================================================================
        response = _format_prediction_response(
            prediction_result=prediction_result,
            symptom_analysis=symptom_analysis,
            severity_result=severity_result,
            recommendations=recommendations
        )
        
        # =====================================================================
        # Step 10: Clean up temporary files
        # =====================================================================
        _cleanup_temp_file(temp_filepath)
        
        # =====================================================================
        # Step 11: Return JSON response
        # =====================================================================
        logger.info("Prediction request completed successfully")
        return jsonify(response), 200
        
    except Exception as e:
        # Clean up on error
        _cleanup_temp_file(temp_filepath)
        
        logger.error(f"Unexpected error in predict endpoint: {e}", exc_info=True)
        return jsonify(*_create_error_response("INTERNAL_ERROR", str(e)))


# =============================================================================
# Feature 7.2: Additional Support Endpoints
# =============================================================================

# API Version
API_VERSION = "1.0.0"


@predict_bp.get("/health")
def health_check():
    """
    Health Check Endpoint.
    
    Route: GET /api/health
    
    Response Format:
    {
        "status": "healthy",
        "model_loaded": true,
        "version": "1.0.0"
    }
    
    Returns:
        JSON with service health status
    """
    model_loaded = predictor.is_model_loaded()
    
    response = {
        "status": "healthy" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "version": API_VERSION
    }
    
    status_code = 200 if model_loaded else 503
    return jsonify(response), status_code


@predict_bp.get("/diseases")
def get_diseases():
    """
    Get list of supported diseases.
    
    Route: GET /api/diseases
    
    Response Format:
    {
        "diseases": ["Acne", "Eczema", ...],
        "count": 22
    }
    
    Returns:
        JSON with list of diseases and count
    """
    try:
        model_info = predictor.get_model_info()
        diseases = model_info.get("diseases", [])
        
        return jsonify({
            "diseases": diseases,
            "count": len(diseases)
        }), 200
    except Exception as e:
        logger.error(f"Failed to get diseases: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve disease list"
        }), 500


@predict_bp.get("/symptoms")
def get_symptoms():
    """
    Get list of available symptoms for input.
    
    Route: GET /api/symptoms
    
    Response Format:
    {
        "symptoms": ["itching", "redness", ...],
        "count": 45
    }
    
    Returns:
        JSON with list of symptoms and count
    """
    try:
        symptoms = get_all_symptoms()
        
        return jsonify({
            "symptoms": symptoms,
            "count": len(symptoms)
        }), 200
    except Exception as e:
        logger.error(f"Failed to get symptoms: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve symptom list"
        }), 500


@predict_bp.get("/model-info")
def get_model_info_endpoint():
    """
    Get information about the loaded model.
    
    Route: GET /api/model-info
    
    Returns:
        JSON with model information
    """
    try:
        model_info = predictor.get_model_info()
        
        return jsonify({
            "success": True,
            "model": model_info,
            "version": API_VERSION
        }), 200
    except Exception as e:
        logger.error(f"Failed to get model info: {e}")
        return jsonify({
            "success": False,
            "error": "Failed to retrieve model information"
        }), 500


# =============================================================================
# Error Handlers
# =============================================================================

@predict_bp.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify(*_create_error_response("IMAGE_TOO_LARGE"))


@predict_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request error"""
    return jsonify({
        "success": False,
        "error": {
            "code": "BAD_REQUEST",
            "message": "Bad request",
            "details": str(error)
        }
    }), 400


@predict_bp.errorhandler(500)
def internal_error(error):
    """Handle internal server error"""
    return jsonify(*_create_error_response("INTERNAL_ERROR"))
