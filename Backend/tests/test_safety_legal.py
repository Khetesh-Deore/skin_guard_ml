"""
Test script for Feature 6.4: Safety & Legal Considerations
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.recommendation_engine import (
    generate_recommendations,
    generate_safe_recommendations,
    validate_safety_compliance,
    add_safety_elements,
    get_disclaimer,
    get_safety_messages,
    format_recommendations,
    PROHIBITED_PATTERNS,
    SAFETY_MESSAGES,
    RECOMMENDATIONS
)


def test_always_include():
    """Test that required elements are ALWAYS included"""
    print("=" * 70)
    print("Testing: Always Include Elements")
    print("=" * 70)
    
    test_cases = [
        ("Acne", "mild", []),
        ("Eczema", "moderate", ["itching"]),
        ("Skin Cancer", "severe", ["bleeding"]),
    ]
    
    print("\nTest Results:")
    for disease, severity, symptoms in test_cases:
        result = generate_safe_recommendations(disease, severity, symptoms, confidence=0.8)
        
        print(f"\n  {disease} ({severity}):")
        has_disclaimer = "disclaimer" in result and len(result["disclaimer"]) > 50
        print(f"    ✓ Medical disclaimer: {has_disclaimer}")


def test_disclaimer():
    """Test the medical disclaimer"""
    print("\n" + "=" * 70)
    print("Testing: Medical Disclaimer")
    print("=" * 70)
    
    disclaimer = get_disclaimer()
    print(f"\n  Disclaimer text ({len(disclaimer)} chars):")
    print(f"    \"{disclaimer[:100]}...\"")


def main():
    print("=" * 70)
    print("Feature 6.4: Safety & Legal Considerations - Test Suite")
    print("=" * 70)
    
    test_always_include()
    test_disclaimer()
    
    print("\n" + "=" * 70)
    print("Feature 6.4 Safety & Legal - Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
