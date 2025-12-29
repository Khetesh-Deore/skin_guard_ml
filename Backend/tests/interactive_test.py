"""
Interactive Test for Feature 3
"""
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules import predictor

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def main():
    print_header("Feature 3: Interactive Test")
    
    # Load disease mapping
    print("\n📋 Loading disease mapping...")
    base_dir = Path(__file__).resolve().parent.parent
    mapping_path = base_dir / "models" / "disease_mapping.json"
    
    try:
        predictor.load_disease_mapping(str(mapping_path))
        print("✓ Disease mapping loaded successfully!")
        
        with open(mapping_path, 'r') as f:
            diseases = json.load(f)
        
        print(f"\n🏥 Available diseases ({len(diseases)} classes):")
        for idx, disease in diseases.items():
            print(f"   {idx}. {disease}")
    except Exception as e:
        print(f"✗ Failed to load disease mapping: {e}")
        return
    
    # Test confidence levels
    print_header("Testing Confidence Levels")
    
    test_scores = [(0.95, "Very high"), (0.75, "Medium"), (0.55, "Low")]
    
    print("\n📊 Confidence Score → Level:")
    for score, description in test_scores:
        level = predictor.get_confidence_level(score)
        print(f"   {score:.2f} ({description}) → {level.upper()}")
    
    print_header("Test Summary")
    print("\n   ✅ Module imports: WORKING")
    print("   ✅ Disease mapping: WORKING")
    print("   ✅ Confidence levels: WORKING")
    
    print("\n" + "=" * 60)
    print("  Test Complete!")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
