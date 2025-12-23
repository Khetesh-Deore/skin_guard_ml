"""
Test script to verify full API integration with Teachable Machine model.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app import app

def test_full_prediction():
    """Test the full prediction pipeline"""
    print("=" * 60)
    print("Testing Full API Integration")
    print("=" * 60)
    
    # Find a test image
    test_dir = Path(__file__).resolve().parent.parent / "data" / "SkinDisease" / "SkinDisease" / "test" / "Acne"
    test_images = list(test_dir.glob("*.jpeg"))[:1]
    if not test_images:
        test_images = list(test_dir.glob("*.jpg"))[:1]
    if not test_images:
        test_images = list(test_dir.glob("*.png"))[:1]
    
    if not test_images:
        print("No test images found!")
        return
    
    test_image = test_images[0]
    print(f"\nTest image: {test_image.name}")
    
    with app.test_client() as client:
        # Test health endpoint
        print("\n[1] Testing /api/health...")
        resp = client.get("/api/health")
        health = resp.get_json()
        print(f"    Status: {health.get('status')}")
        print(f"    Model loaded: {health.get('model_loaded')}")
        print(f"    Classes: {health.get('num_classes')}")
        
        # Test diseases endpoint
        print("\n[2] Testing /api/diseases...")
        resp = client.get("/api/diseases")
        diseases = resp.get_json()
        print(f"    Count: {diseases.get('count')}")
        
        # Test symptoms endpoint
        print("\n[3] Testing /api/symptoms...")
        resp = client.get("/api/symptoms")
        symptoms = resp.get_json()
        print(f"    Count: {symptoms.get('count')}")
        
        # Test prediction endpoint
        print("\n[4] Testing /api/predict...")
        with open(test_image, "rb") as f:
            data = {
                "image": (f, test_image.name),
            }
            resp = client.post("/api/predict", data=data, content_type="multipart/form-data")
        
        result = resp.get_json()
        print(f"    HTTP Status: {resp.status_code}")
        print(f"    Success: {result.get('success')}")
        
        if result.get("success"):
            pred = result.get("prediction", {})
            print(f"\n    Prediction Results:")
            print(f"    - Disease: {pred.get('disease')}")
            print(f"    - Confidence: {pred.get('confidence'):.2%}")
            print(f"    - Confidence Level: {pred.get('confidence_level')}")
            print(f"    - Needs Review: {pred.get('needs_review')}")
            
            severity = result.get("severity", {})
            print(f"\n    Severity Analysis:")
            print(f"    - Level: {severity.get('level')}")
            print(f"    - Urgency: {severity.get('urgency')}")
            
            recs = result.get("recommendations", {})
            print(f"\n    Recommendations:")
            print(f"    - General Advice: {recs.get('general_advice', 'N/A')[:80]}...")
            
            print(f"\n    Top 3 Predictions:")
            for i, alt in enumerate([pred] + pred.get("alternative_possibilities", [])[:2], 1):
                print(f"    {i}. {alt.get('disease')}: {alt.get('confidence'):.2%}")
        else:
            print(f"    Error: {result.get('error')}")
        
        # Test with symptoms
        print("\n[5] Testing /api/predict with symptoms...")
        with open(test_image, "rb") as f:
            data = {
                "image": (f, test_image.name),
                "symptoms": "redness,itching,bumps"
            }
            resp = client.post("/api/predict", data=data, content_type="multipart/form-data")
        
        result = resp.get_json()
        if result.get("success"):
            symptom_analysis = result.get("symptom_analysis", {})
            print(f"    Symptom Match: {symptom_analysis.get('match_percentage', 0):.0f}%")
            print(f"    Alignment: {symptom_analysis.get('alignment', 'N/A')}")
        
    print("\n" + "=" * 60)
    print("Integration test completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_full_prediction()
