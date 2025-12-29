"""
Test script for Feature 4: Symptom Matching Module
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.symptom_matcher import (
    match_symptoms, 
    normalize_symptom,
    calculate_alignment_score,
    get_all_symptoms, 
    DISEASE_SYMPTOMS
)


def test_feature_4_2():
    """Test Feature 4.2: Matching Algorithm"""
    print("\n" + "=" * 70)
    print("Testing Feature 4.2: Symptom Matching Algorithm")
    print("=" * 70)
    
    # Test strong match
    print("\n[4.2.1] Testing STRONG match - Eczema...")
    eczema_symptoms = ["itching", "redness", "dry_skin"]
    result = match_symptoms("Eczema", eczema_symptoms, original_confidence=0.85)
    print(f"    Symptoms: {eczema_symptoms}")
    print(f"    Match: {result['match_percentage']}%")
    print(f"    Alignment: {result['alignment']}")


def test_feature_4_3():
    """Test Feature 4.3: Symptom Normalization"""
    print("\n" + "=" * 70)
    print("Testing Feature 4.3: Symptom Normalization")
    print("=" * 70)
    
    test_cases = [
        ("itchy skin", "itching"),
        ("red spots", "redness"),
    ]
    
    for raw, expected in test_cases:
        result = normalize_symptom(raw)
        status = "✓" if result == expected else "✗"
        print(f"    {status} '{raw}' -> '{result}' (expected: '{expected}')")


def main():
    print("=" * 70)
    print("Feature 4: Symptom Matching Module - Test Suite")
    print("=" * 70)
    
    test_feature_4_2()
    test_feature_4_3()
    
    print("\n" + "=" * 70)
    print("Feature 4 Symptom Matching - Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
