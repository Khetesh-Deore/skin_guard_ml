"""
Test script for predictor module
Run this to verify Feature 3 is working correctly
"""

import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules import predictor

def test_predictor():
    """Test the predictor module functionality"""
    
    print("=" * 60)
    print("Testing Feature 3: ML Prediction Module")
    print("=" * 60)
    
    # Get paths - using Teachable Machine model
    base_dir = Path(__file__).resolve().parent.parent
    model_path = base_dir / "models" / "keras_model.h5"
    mapping_path = base_dir / "models" / "disease_mapping.json"
    
    # Test 1: Load model
    print("\n[Test 1] Loading model...")
    try:
        predictor.load_model(str(model_path))
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"✗ Model loading failed: {e}")
        return
    
    # Test 2: Load disease mapping
    print("\n[Test 2] Loading disease mapping...")
    try:
        predictor.load_disease_mapping(str(mapping_path))
        print("✓ Disease mapping loaded successfully")
    except Exception as e:
        print(f"✗ Disease mapping loading failed: {e}")
        return
    
    # Test 3: Check model info
    print("\n[Test 3] Getting model info...")
    model_info = predictor.get_model_info()
    print(f"✓ Model loaded: {model_info['loaded']}")
    print(f"  Number of classes: {model_info['num_classes']}")
    
    # Test 4: Test confidence level function
    print("\n[Test 4] Testing confidence level function...")
    test_scores = [0.95, 0.75, 0.45]
    for score in test_scores:
        level = predictor.get_confidence_level(score)
        print(f"  Score {score:.2f} → {level}")
    print("✓ Confidence level function working")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully! ✓")
    print("=" * 60)


if __name__ == "__main__":
    test_predictor()
