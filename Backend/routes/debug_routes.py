"""
Debug routes for model diagnostics
WARNING: Remove or protect these endpoints in production
"""
from flask import Blueprint, request, jsonify
import numpy as np
from modules.image_processor import process_image
from modules import predictor
import traceback
from PIL import Image
import io

debug_bp = Blueprint('debug', __name__)


def interpret_statistics(stats):
    """
    Generate human-readable interpretation of prediction statistics
    """
    interpretations = []
    
    max_prob = stats.get("max_probability", 0)
    entropy = stats.get("entropy", 0)
    
    if max_prob > 0.9:
        interpretations.append("Model is very confident in its top prediction.")
    elif max_prob > 0.7:
        interpretations.append("Model is moderately confident.")
    else:
        interpretations.append("Model is uncertain (low top probability).")
        
    if entropy > 2.0:
        interpretations.append("High entropy indicates the model is 'confused' across many classes.")
    elif entropy < 0.5:
        interpretations.append("Low entropy indicates a sharp, focused prediction.")
        
    return interpretations


def generate_preprocessing_warnings(info):
    """
    Generate warnings if preprocessing looks suspicious
    """
    warnings_list = []
    processed = info.get("processed_array", {})
    min_val = processed.get("min_value", 0)
    max_val = processed.get("max_value", 0)
    
    # Check for likely normalization issues
    if max_val > 1.0:
        warnings_list.append("Processed image values > 1.0. Is the image normalized to [0,1] or [-1,1]?")
    
    if min_val < 0 and max_val > 0:
        if min_val < -1:
             warnings_list.append("Values < -1 detected. Standard scaling usually stays within [-1, 1] or similar.")
    
    if min_val >= 0 and max_val <= 1.0:
        # Looks like [0, 1]
        pass
    elif min_val >= -1.0 and max_val <= 1.0:
        # Looks like [-1, 1]
        pass
    else:
        warnings_list.append(f"Unusual value range: [{min_val:.2f}, {max_val:.2f}]")

    return warnings_list


@debug_bp.route('/debug/prediction-distribution', methods=['POST'])
def check_prediction_distribution():
    """
    Shows probability distribution across ALL classes
    Use this to understand what the model is "thinking"
    """
    try:
        # Validate request
        if 'image' not in request.files:
            return jsonify({
                "error": "No image file provided",
                "hint": "Send image using form-data with key 'image'"
            }), 400
        
        image_file = request.files['image']
        
        # Preprocess image
        try:
            img_array = process_image(image_file)
        except Exception as e:
            return jsonify({"error": f"Preprocessing failed: {str(e)}"}), 400
        
        # Get model and classes
        model = predictor.get_internal_model()
        class_names = predictor.get_class_names()
        
        if model is None:
             return jsonify({"error": "Model not loaded"}), 503

        # Get raw predictions
        raw_predictions = model.predict(img_array, verbose=0)[0]
        
        # Create distribution map
        distribution = []
        for idx, prob in enumerate(raw_predictions):
            disease_name = class_names[idx] if idx < len(class_names) else f"Class {idx}"
            distribution.append({
                "class_index": idx,
                "disease_name": disease_name,
                "probability": float(prob),
                "percentage": float(prob * 100)
            })
        
        # Sort by probability (highest first)
        distribution.sort(key=lambda x: x['probability'], reverse=True)
        
        # Calculate statistics
        probabilities = raw_predictions
        stats = {
            "max_probability": float(np.max(probabilities)),
            "min_probability": float(np.min(probabilities)),
            "mean_probability": float(np.mean(probabilities)),
            "std_probability": float(np.std(probabilities)),
            "median_probability": float(np.median(probabilities)),
            "sum_of_probabilities": float(np.sum(probabilities)),
            "entropy": float(-np.sum(probabilities * np.log(probabilities + 1e-10))),
            "top_5_cumulative": float(np.sum(sorted(probabilities, reverse=True)[:5]))
        }
        
        return jsonify({
            "success": True,
            "statistics": stats,
            "full_distribution": distribution,
            "top_10": distribution[:10],
            "interpretation": interpret_statistics(stats)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@debug_bp.route('/debug/preprocessing-info', methods=['POST'])
def check_preprocessing():
    """
    Shows detailed preprocessing information
    Use this to verify preprocessing matches training
    """
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        image_file = request.files['image']
        
        # Read original image
        image_bytes = image_file.read()
        image_file.seek(0)  # Reset file pointer
        
        original_img = Image.open(io.BytesIO(image_bytes))
        
        # Get preprocessing output
        # process_image reads from the file object, so we need to ensure it's at start
        image_file.seek(0)
        processed_array = process_image(image_file)
        
        info = {
            "original_image": {
                "size": original_img.size,  # (width, height)
                "mode": original_img.mode,  # RGB, RGBA, L, etc.
                "format": original_img.format
            },
            "processed_array": {
                "shape": list(processed_array.shape),
                "dtype": str(processed_array.dtype),
                "min_value": float(np.min(processed_array)),
                "max_value": float(np.max(processed_array)),
                "mean_value": float(np.mean(processed_array)),
                "std_value": float(np.std(processed_array)),
                "median_value": float(np.median(processed_array))
            },
            "expected_preprocessing": {
                "note": "Compare these values with your training preprocessing",
                "common_ranges": {
                    "ImageNet_normalized": "mean near 0, std near 1",
                    "0_to_1_range": "min=0, max=1",
                    "minus1_to_1_range": "min=-1, max=1",
                    "0_to_255_range": "min=0, max=255"
                }
            }
        }
        
        return jsonify({
            "success": True,
            "preprocessing_info": info,
            "warnings": generate_preprocessing_warnings(info)
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


@debug_bp.route('/debug/model-info', methods=['GET'])
def get_model_info_route():
    """
    Shows model architecture and configuration
    """
    try:
        model = predictor.get_internal_model()
        class_names = predictor.get_class_names()
        
        info = {
            "model_loaded": model is not None,
            "number_of_classes": len(class_names),
            "class_names": class_names,
            "model_input_shape": list(model.input_shape) if model else None,
            "model_output_shape": list(model.output_shape) if model else None,
            "total_parameters": int(model.count_params()) if model else 0
        }
        return jsonify(info)
    except Exception as e:
         return jsonify({
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500
