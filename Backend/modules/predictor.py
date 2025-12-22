"""
ML Prediction Module
Handles model loading, inference, and prediction result formatting
"""

import os
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to cache the model (singleton pattern)
_model = None
_disease_mapping = None


class ModelNotLoadedError(Exception):
    """Raised when attempting to predict without loading the model first"""
    pass


def load_model(model_path: str) -> None:
    """
    Load the trained model from disk and cache it in memory.
    Should be called once at application startup.
    
    Args:
        model_path: Path to the saved model file (.h5 or .keras)
    
    Raises:
        FileNotFoundError: If model file doesn't exist
        Exception: If model loading fails
    """
    global _model
    
    if _model is not None:
        logger.info("Model already loaded, skipping reload")
        return
    
    try:
        # Check if model file exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found at: {model_path}")
        
        logger.info(f"Loading model from: {model_path}")
        
        # Import TensorFlow here to avoid loading if not needed
        import tensorflow as tf
        from tensorflow import keras
        
        # Set TensorFlow to inference mode for better performance
        tf.config.optimizer.set_jit(False)  # Disable XLA for compatibility
        
        # Workaround for TensorFlow 2.20+ quantization_mode issue
        # This is a known bug in TF 2.20 with certain saved models
        try:
            # Try loading with custom_objects to handle quantization issues
            _model = keras.models.load_model(
                model_path,
                compile=False,
                custom_objects=None
            )
        except (TypeError, AttributeError) as e:
            # If that fails, try with safe_mode disabled
            logger.warning(f"First load attempt failed: {e}. Trying alternative method...")
            try:
                import h5py
                # Load weights manually if direct loading fails
                with h5py.File(model_path, 'r') as f:
                    # Check if it's a full model or just weights
                    if 'model_config' in f.attrs or 'layer_names' in f.attrs:
                        # Try loading as SavedModel format
                        _model = keras.models.load_model(model_path, compile=False)
                    else:
                        raise ValueError("Unable to load model with current method")
            except Exception as e2:
                logger.error(f"Alternative load method also failed: {e2}")
                raise Exception(f"Could not load model. Original error: {e}")
        
        # Compile for inference (no training needed)
        _model.compile()
        
        logger.info(f"Model loaded successfully. Input shape: {_model.input_shape}")
        
        # Warm up the model with a dummy prediction
        _warmup_model()
        
        logger.info("Model warmed up and ready for predictions")
        
    except Exception as e:
        logger.error(f"Failed to load model: {str(e)}")
        raise


def _warmup_model() -> None:
    """
    Perform a dummy prediction to warm up the model.
    This reduces latency on the first real prediction.
    """
    global _model
    
    if _model is None:
        return
    
    try:
        # Get input shape from model
        input_shape = _model.input_shape
        # Create dummy input (batch_size, height, width, channels)
        dummy_input = np.random.rand(1, input_shape[1], input_shape[2], input_shape[3]).astype(np.float32)
        
        # Run dummy prediction
        _ = _model.predict(dummy_input, verbose=0)
        logger.info("Model warmup completed")
        
    except Exception as e:
        logger.warning(f"Model warmup failed: {str(e)}")


def load_disease_mapping(mapping_path: str) -> None:
    """
    Load disease class mapping from JSON file.
    Maps model output indices to disease names.
    
    Args:
        mapping_path: Path to disease_mapping.json file
    
    Raises:
        FileNotFoundError: If mapping file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    global _disease_mapping
    
    if _disease_mapping is not None:
        logger.info("Disease mapping already loaded, skipping reload")
        return
    
    try:
        if not os.path.exists(mapping_path):
            raise FileNotFoundError(f"Disease mapping file not found at: {mapping_path}")
        
        with open(mapping_path, 'r') as f:
            _disease_mapping = json.load(f)
        
        logger.info(f"Disease mapping loaded: {len(_disease_mapping)} classes")
        
    except Exception as e:
        logger.error(f"Failed to load disease mapping: {str(e)}")
        raise


def get_confidence_level(confidence_score: float) -> str:
    """
    Convert numerical confidence score to categorical level.
    
    Args:
        confidence_score: Float between 0 and 1
    
    Returns:
        String: "high", "medium", or "low"
    """
    if confidence_score >= 0.80:
        return "high"
    elif confidence_score >= 0.60:
        return "medium"
    else:
        return "low"


def predict_disease(image_array: np.ndarray, top_k: int = 3) -> Dict:
    """
    Predict disease from preprocessed image array.
    
    Args:
        image_array: Preprocessed image array (batch_size, height, width, channels)
        top_k: Number of top predictions to return (default: 3)
    
    Returns:
        Dictionary containing prediction results:
        {
            "predicted_disease": str,
            "confidence": float,
            "confidence_level": str,
            "top_predictions": List[Dict],
            "needs_review": bool,
            "review_reason": Optional[str]
        }
    
    Raises:
        ModelNotLoadedError: If model hasn't been loaded
        ValueError: If image_array has wrong shape
    """
    global _model, _disease_mapping
    
    # Validate model is loaded
    if _model is None:
        raise ModelNotLoadedError("Model not loaded. Call load_model() first.")
    
    if _disease_mapping is None:
        raise ModelNotLoadedError("Disease mapping not loaded. Call load_disease_mapping() first.")
    
    try:
        # Validate input shape
        expected_shape = _model.input_shape
        if len(image_array.shape) != 4:
            raise ValueError(f"Expected 4D array, got shape: {image_array.shape}")
        
        if image_array.shape[1:] != expected_shape[1:]:
            raise ValueError(
                f"Image shape mismatch. Expected {expected_shape[1:]}, got {image_array.shape[1:]}"
            )
        
        # Run prediction
        logger.info("Running model prediction...")
        predictions = _model.predict(image_array, verbose=0)
        
        # Get probability distribution (first batch item)
        probabilities = predictions[0]
        
        # Get top K predictions
        top_indices = np.argsort(probabilities)[::-1][:top_k]
        top_predictions = []
        
        for idx in top_indices:
            disease_name = _disease_mapping.get(str(idx), f"Unknown_{idx}")
            confidence = float(probabilities[idx])
            top_predictions.append({
                "disease": disease_name,
                "confidence": round(confidence, 4)
            })
        
        # Extract top prediction
        predicted_disease = top_predictions[0]["disease"]
        confidence = top_predictions[0]["confidence"]
        confidence_level = get_confidence_level(confidence)
        
        # Determine if expert review is needed
        needs_review, review_reason = _check_needs_review(probabilities, confidence)
        
        # Build result
        result = {
            "predicted_disease": predicted_disease,
            "confidence": round(confidence, 4),
            "confidence_level": confidence_level,
            "top_predictions": top_predictions,
            "needs_review": needs_review,
            "review_reason": review_reason
        }
        
        logger.info(f"Prediction complete: {predicted_disease} ({confidence_level} confidence)")
        
        return result
        
    except Exception as e:
        logger.error(f"Prediction failed: {str(e)}")
        raise


def _check_needs_review(probabilities: np.ndarray, top_confidence: float) -> Tuple[bool, Optional[str]]:
    """
    Determine if prediction needs expert review based on confidence patterns.
    
    Args:
        probabilities: Full probability distribution
        top_confidence: Confidence of top prediction
    
    Returns:
        Tuple of (needs_review: bool, reason: Optional[str])
    """
    # Low confidence threshold
    if top_confidence < 0.60:
        return True, "Low confidence prediction"
    
    # Check for multiple high probabilities (ambiguous case)
    sorted_probs = np.sort(probabilities)[::-1]
    if len(sorted_probs) >= 2:
        second_highest = sorted_probs[1]
        # If second prediction is also high, it's ambiguous
        if second_highest > 0.30 and (top_confidence - second_highest) < 0.20:
            return True, "Multiple possible conditions detected"
    
    return False, None


def get_model_info() -> Dict:
    """
    Get information about the loaded model.
    
    Returns:
        Dictionary with model metadata
    """
    global _model, _disease_mapping
    
    if _model is None:
        return {"loaded": False}
    
    return {
        "loaded": True,
        "input_shape": _model.input_shape,
        "output_shape": _model.output_shape,
        "num_classes": len(_disease_mapping) if _disease_mapping else 0,
        "diseases": list(_disease_mapping.values()) if _disease_mapping else []
    }


def is_model_loaded() -> bool:
    """
    Check if model is loaded and ready for predictions.
    
    Returns:
        bool: True if model is loaded, False otherwise
    """
    return _model is not None and _disease_mapping is not None
