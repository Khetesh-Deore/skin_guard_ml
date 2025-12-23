"""
Test script for Feature 5: Severity Analysis Module
Tests the multi-factor severity assessment (Feature 5.1)
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules.severity_analyzer import (
    analyze_severity,
    assess_factor_1_baseline_severity,
    assess_factor_2_confidence_score,
    assess_factor_3_symptom_intensity,
    assess_factor_4_symptom_count,
    assess_factor_5_severe_indicators,
    assess_area_spread,
    assess_duration,
    get_urgency_level,
    get_severity_explanation,
    get_disease_risk_level,
    get_severity_recommendations,
    compare_severity_factors,
    calculate_risk_score,
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
        ("Melanoma", "critical"),
        ("Eczema", "mild"),
        ("Psoriasis", "moderate"),
    ]
    
    for disease, expected in test_diseases:
        score, explanation = assess_factor_1_baseline_severity(disease)
        status = "✓" if expected in explanation.lower() else "✗"
        print(f"  {status} {disease}: score={score}, {explanation}")


def test_factor_2_confidence():
    """Test Factor 2: Model Confidence Score"""
    print("\n" + "=" * 60)
    print("Testing Factor 2: Model Confidence Score")
    print("=" * 60)
    
    test_cases = [
        (0.95, "severe", "High confidence"),
        (0.75, "moderate", "Good confidence"),
        (0.50, "mild", "Moderate confidence"),
        (0.30, "severe", "Low confidence"),
    ]
    
    for confidence, baseline, expected_keyword in test_cases:
        adjustment, explanation = assess_factor_2_confidence_score(confidence, baseline)
        status = "✓" if expected_keyword.lower() in explanation.lower() else "✗"
        print(f"  {status} Confidence={confidence}, Baseline={baseline}: adj={adjustment}, {explanation}")


def test_factor_3_intensity():
    """Test Factor 3: Symptom Intensity Keywords"""
    print("\n" + "=" * 60)
    print("Testing Factor 3: Symptom Intensity Keywords")
    print("=" * 60)
    
    test_cases = [
        (["very itchy", "extremely painful"], "high"),
        (["moderate redness", "noticeable swelling"], "moderate"),
        (["slight discomfort", "mild rash"], "low"),
        (["rash", "bumps"], "normal"),
    ]
    
    for symptoms, expected_level in test_cases:
        score, level, explanation = assess_factor_3_symptom_intensity(symptoms)
        status = "✓" if level == expected_level else "✗"
        print(f"  {status} {symptoms[:2]}: score={score}, level={level}")


def test_factor_4_count():
    """Test Factor 4: Symptom Count"""
    print("\n" + "=" * 60)
    print("Testing Factor 4: Symptom Count")
    print("=" * 60)
    
    test_cases = [
        ([], 0),
        (["rash"], 0),
        (["rash", "itching", "redness"], 0.5),
        (["rash", "itching", "redness", "pain", "swelling"], 1.0),
        (["a", "b", "c", "d", "e", "f", "g", "h"], 1.5),
    ]
    
    for symptoms, expected_score in test_cases:
        score, explanation = assess_factor_4_symptom_count(symptoms)
        status = "✓" if score == expected_score else "✗"
        print(f"  {status} Count={len(symptoms)}: score={score}, {explanation}")


def test_factor_5_indicators():
    """Test Factor 5: Severe Indicators"""
    print("\n" + "=" * 60)
    print("Testing Factor 5: Severe Indicators")
    print("=" * 60)
    
    test_cases = [
        ("Acne", ["cysts", "nodules", "widespread"], True),
        ("Skin Cancer", ["rapid_growth", "bleeding", "ulceration"], True),
        ("Eczema", ["redness", "itching"], False),
    ]
    
    for disease, symptoms, should_have_indicators in test_cases:
        score, matched, explanation = assess_factor_5_severe_indicators(disease, symptoms)
        has_indicators = len(matched) > 0
        status = "✓" if has_indicators == should_have_indicators else "✗"
        print(f"  {status} {disease}: score={score}, matched={matched}")


def test_full_severity_analysis():
    """Test complete severity analysis"""
    print("\n" + "=" * 60)
    print("Testing Full Multi-Factor Severity Analysis")
    print("=" * 60)
    
    test_cases = [
        {
            "disease": "Acne",
            "confidence": 0.95,
            "symptoms": ["pimples", "oily_skin"],
            "expected_severity": "mild"
        },
        {
            "disease": "Acne",
            "confidence": 0.90,
            "symptoms": ["cysts", "nodules", "widespread", "very painful", "severe scarring"],
            "expected_severity": "moderate"  # Capped at moderate for Acne
        },
        {
            "disease": "Skin Cancer",
            "confidence": 0.85,
            "symptoms": ["rapid_growth", "bleeding", "ulceration"],
            "expected_severity": "critical"
        },
        {
            "disease": "Eczema",
            "confidence": 0.80,
            "symptoms": ["itching", "redness", "dry_skin"],
            "expected_severity": "mild"
        },
    ]
    
    for case in test_cases:
        result = analyze_severity(
            case["disease"],
            case["confidence"],
            case["symptoms"]
        )
        
        status = "✓" if result["level"] == case["expected_severity"] else "✗"
        print(f"\n  {status} {case['disease']} (confidence={case['confidence']}):")
        print(f"      Symptoms: {case['symptoms'][:3]}...")
        print(f"      Severity: {result['level']} (expected: {case['expected_severity']})")
        print(f"      Score: {result['score']}")
        print(f"      Urgency: {result['urgency']}")
        print(f"      Factors: {len(result['factors'])} assessed")


def test_risk_score():
    """Test risk score calculation"""
    print("\n" + "=" * 60)
    print("Testing Risk Score Calculation")
    print("=" * 60)
    
    test_cases = [
        ("Acne", 0.90, ["pimples"], "Low"),
        ("Skin Cancer", 0.85, ["rapid_growth", "bleeding"], "Very High"),
        ("Eczema", 0.75, ["itching", "very dry", "widespread"], "Moderate"),
    ]
    
    for disease, confidence, symptoms, expected_category in test_cases:
        result = calculate_risk_score(disease, confidence, symptoms)
        status = "✓" if result["risk_category"] == expected_category else "~"
        print(f"  {status} {disease}: score={result['risk_score']}, category={result['risk_category']}")


def test_urgency_levels():
    """Test urgency level determination"""
    print("\n" + "=" * 60)
    print("Testing Urgency Levels")
    print("=" * 60)
    
    test_cases = [
        ("Melanoma", "critical", ["rapid_growth"], "immediate"),
        ("Skin Cancer", "severe", ["bleeding"], "immediate"),
        ("Eczema", "mild", ["itching"], "routine"),
        ("Psoriasis", "moderate", ["scaling"], "consult_doctor"),
    ]
    
    for disease, severity, symptoms, expected_urgency in test_cases:
        urgency, warning = get_urgency_level(disease, severity, symptoms)
        status = "✓" if urgency == expected_urgency else "✗"
        print(f"  {status} {disease} ({severity}): urgency={urgency}")


def test_factor_weights():
    """Test that factor weights sum to 1.0"""
    print("\n" + "=" * 60)
    print("Testing Factor Weights")
    print("=" * 60)
    
    total = sum(FACTOR_WEIGHTS.values())
    status = "✓" if abs(total - 1.0) < 0.01 else "✗"
    print(f"  {status} Factor weights sum: {total} (should be 1.0)")
    
    for factor, weight in FACTOR_WEIGHTS.items():
        print(f"      {factor}: {weight:.0%}")


def main():
    print("=" * 60)
    print("Feature 5: Severity Analysis Module - Test Suite")
    print("Feature 5.1: Multi-Factor Severity Assessment")
    print("=" * 60)
    
    # Test individual factors
    test_factor_1_baseline()
    test_factor_2_confidence()
    test_factor_3_intensity()
    test_factor_4_count()
    test_factor_5_indicators()
    
    # Test full analysis
    test_full_severity_analysis()
    
    # Test additional functions
    test_risk_score()
    test_urgency_levels()
    test_factor_weights()
    
    print("\n" + "=" * 60)
    print("All Feature 5.1 tests completed!")
    print("=" * 60)
    print("\nMulti-Factor Assessment Factors:")
    print("  1. Disease Baseline Severity (25%)")
    print("  2. Model Confidence Score (15%)")
    print("  3. Symptom Intensity Keywords (20%)")
    print("  4. Symptom Count (15%)")
    print("  5. Severe Indicators (25%)")


if __name__ == "__main__":
    main()
