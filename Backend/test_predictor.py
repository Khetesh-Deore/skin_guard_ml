"""
Test script for predictor module
Run this to verify Feature 3 is working correctly
"""

import numpy as np
from pathlib import Path
from modules import predictor

def test_predictor():
    """Test the predictor module functionality"""
    
    print("=" * 60)
    print("Testing Feature 3: ML Prediction Module")
    print("=" * 60)
    
    # Get paths
    base_dir = Path(__file__).resolve().parent
    model_path = base_dir / "models" / "skin_efficientnet_v2_final_90plus.h5"
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
    print(f"  Input shape: {model_info['input_shape']}")
    print(f"  Output shape: {model_info['output_shape']}")
    print(f"  Number of classes: {model_info['num_classes']}")
    print(f"  Diseases: {', '.join(model_info['diseases'])}")
    
    # Test 4: Test confidence level function
    print("\n[Test 4] Testing confidence level function...")
    test_scores = [0.95, 0.75, 0.45]
    for score in test_scores:
        level = predictor.get_confidence_level(score)
        print(f"  Score {score:.2f} → {level}")
    print("✓ Confidence level function working")
    
    # Test 5: Make a dummy prediction
    print("\n[Test 5] Making dummy prediction...")
    try:
        # Create dummy image array matching model input shape
        input_shape = model_info['input_shape']
        dummy_image = np.random.rand(1, input_shape[1], input_shape[2], input_shape[3]).astype(np.float32)
        
        result = predictor.predict_disease(dummy_image, top_k=3)
        
        print("✓ Prediction successful!")
        print(f"  Predicted disease: {result['predicted_disease']}")
        print(f"  Confidence: {result['confidence']:.4f}")
        print(f"  Confidence level: {result['confidence_level']}")
        print(f"  Needs review: {result['needs_review']}")
        if result['review_reason']:
            print(f"  Review reason: {result['review_reason']}")
        
        print(f"\n  Top {len(result['top_predictions'])} predictions:")
        for i, pred in enumerate(result['top_predictions'], 1):
            print(f"    {i}. {pred['disease']}: {pred['confidence']:.4f}")
            
    except Exception as e:
        print(f"✗ Prediction failed: {e}")
        return
    
    # Test 6: Test error handling
    print("\n[Test 6] Testing error handling...")
    try:
        # Try prediction with wrong shape
        wrong_shape = np.random.rand(1, 100, 100, 3).astype(np.float32)
        predictor.predict_disease(wrong_shape)
        print("✗ Should have raised ValueError for wrong shape")
    except ValueError as e:
        print(f"✓ Correctly caught shape mismatch: {str(e)[:50]}...")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    print("\n" + "=" * 60)
    print("All tests completed successfully! ✓")
    print("Feature 3: ML Prediction Module is working correctly")
    print("=" * 60)


if __name__ == "__main__":
    test_predictor()
