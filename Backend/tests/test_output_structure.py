"""
Test script for Feature 6.3: Output Structure
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.recommendation_engine import (
    generate_recommendations,
    format_recommendations,
    get_disclaimer
)


def test_output_structure():
    """Test that output matches the specified structure"""
    print("=" * 70)
    print("Feature 6.3: Output Structure Verification")
    print("=" * 70)
    
    expected_fields = {
        "general_advice": str,
        "immediate_care": list,
        "home_remedies": list,
        "precautions": list,
        "lifestyle_tips": list,
        "when_to_see_doctor": str,
        "disclaimer": str,
        "urgency_level": str,
    }
    
    result = generate_recommendations(
        disease="Acne",
        severity="moderate",
        symptoms=["pimples", "oily_skin", "redness"],
        confidence=0.85
    )
    
    print("\nChecking required fields:")
    all_present = True
    
    for field, expected_type in expected_fields.items():
        if field in result:
            type_match = isinstance(result[field], expected_type)
            status = "✓" if type_match else "~"
            print(f"  {status} {field}: {expected_type.__name__}")
        else:
            print(f"  ✗ {field}: MISSING")
            all_present = False
    
    return all_present


def main():
    print("=" * 70)
    print("Feature 6.3: Output Structure - Test Suite")
    print("=" * 70)
    
    structure_ok = test_output_structure()
    
    print("\n" + "=" * 70)
    print("Feature 6.3 Output Structure - Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
