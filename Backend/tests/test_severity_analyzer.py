"""
Test script for Feature 5: Severity Analysis Module
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.severity_analyzer import (
    analyze_severity,
    assess_factor_1_baseline_severity,
    assess_factor_2_confidence_score,
    assess_factor_3_symptom_intensity,
    assess_factor_4_symptom_count,
    assess_factor_5_severe_indicators,
    get_urgency_level,
    get_severity_explanation,
    DISEASE_SEVERITY_BASE,
    FACTOR_WEIGHTS
)


def test_factor_1_baseline():
    """Test Factor 1: Disease Baseline Severity"""
    print("\n" + "=" * 60)
    print("Testing Factor 1: Disease Baseline Severity")
    print("=" * 60)
    
    test_diseases = [
        ("Acne", "mild"),
        ("Skin Cancer", "severe"),
        ("Eczema", "mild"),
    ]
    
    for disease, expected in test_diseases:
        score, explanation = assess_factor_1_baseline_severity(disease)
        status = "✓" if expected in explanation.lower() else "✗"
        print(f"  {status} {disease}: score={score}, {explanation}")


def test_full_severity_analysis():
    """Test complete severity analysis"""
    print("\n" + "=" * 60)
    print("Testing Full Multi-Factor Severity Analysis")
    print("=" * 60)
    
    test_cases = [
        {"disease": "Acne", "confidence": 0.95, "symptoms": ["pimples"], "expected_severity": "mild"},
        {"disease": "Skin Cancer", "confidence": 0.85, "symptoms": ["rapid_growth"], "expected_severity": "critical"},
    ]
    
    for case in test_cases:
        result = analyze_severity(case["disease"], case["confidence"], case["symptoms"])
        status = "✓" if result["level"] == case["expected_severity"] else "✗"
        print(f"\n  {status} {case['disease']}:")
        print(f"      Severity: {result['level']} (expected: {case['expected_severity']})")


def main():
    print("=" * 60)
    print("Feature 5: Severity Analysis Module - Test Suite")
    print("=" * 60)
    
    test_factor_1_baseline()
    test_full_severity_analysis()
    
    print("\n" + "=" * 60)
    print("Feature 5 Severity Analysis - Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
