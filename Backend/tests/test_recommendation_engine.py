"""
Test script for Feature 6: Recommendation Engine
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.recommendation_engine import (
    generate_recommendations,
    get_disclaimer,
    format_recommendations,
    RECOMMENDATIONS,
    DEFAULT_RECOMMENDATIONS
)


def test_recommendation_database_structure():
    """Test Feature 6.1: Recommendation Database Structure"""
    print("=" * 70)
    print("Feature 6.1: Recommendation Database Structure - Verification")
    print("=" * 70)
    
    expected_classes = [
        "Acne", "Actinic Keratosis", "Benign Tumors", "Bullous", "Candidiasis",
        "Drug Eruption", "Eczema", "Infestations/Bites", "Lichen", "Lupus",
        "Moles", "Psoriasis", "Rosacea", "Seborrheic Keratoses", "Skin Cancer",
        "Sun/Sunlight Damage", "Tinea", "Unknown/Normal", "Vascular Tumors",
        "Vasculitis", "Vitiligo", "Warts"
    ]
    
    required_fields = ["general_advice", "home_remedies", "precautions", "when_to_see_doctor"]
    
    print(f"\nChecking {len(expected_classes)} disease classes...")
    
    missing_diseases = []
    complete_count = 0
    
    for disease in expected_classes:
        if disease not in RECOMMENDATIONS:
            missing_diseases.append(disease)
            print(f"  ✗ {disease}: MISSING")
            continue
        
        disease_recs = RECOMMENDATIONS[disease]
        if "mild" in disease_recs:
            complete_count += 1
            print(f"  ✓ {disease}: Complete")
    
    print(f"\nComplete diseases: {complete_count}/{len(expected_classes)}")
    return len(missing_diseases) == 0


def main():
    print("=" * 70)
    print("Feature 6: Recommendation Engine - Test Suite")
    print("=" * 70)
    
    test_recommendation_database_structure()
    
    print("\n" + "=" * 70)
    print("Feature 6 Recommendation Engine - Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
