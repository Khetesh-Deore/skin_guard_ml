"""
Test script for Feature 6.2: Personalization Logic
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.recommendation_engine import (
    generate_recommendations,
    format_recommendations,
    get_disclaimer,
    get_urgency_recommendations,
    SYMPTOM_SPECIFIC_ADVICE
)


def test_step1_base_recommendations():
    """Test Step 1: Get base recommendations for disease + severity"""
    print("=" * 70)
    print("Step 1: Get Base Recommendations for Disease + Severity")
    print("=" * 70)
    
    test_cases = [
        ("Acne", "mild"),
        ("Acne", "moderate"),
        ("Skin Cancer", "severe"),
    ]
    
    for disease, severity in test_cases:
        result = generate_recommendations(disease, severity, [], confidence=0.9)
        print(f"\n  {disease} ({severity}):")
        print(f"    ✓ general_advice: {result['general_advice'][:50]}...")


def main():
    print("=" * 70)
    print("Feature 6.2: Personalization Logic - Test Suite")
    print("=" * 70)
    
    test_step1_base_recommendations()
    
    print("\n" + "=" * 70)
    print("Feature 6.2 Personalization Logic - Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
