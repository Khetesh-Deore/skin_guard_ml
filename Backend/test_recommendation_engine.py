"""
Test script for Feature 6: Recommendation Engine
Verifies Feature 6.1: Recommendation Database Structure for all 22 disease classes.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
    
    # Expected 22 classes from Teachable Machine
    expected_classes = [
        "Acne", "Actinic Keratosis", "Benign Tumors", "Bullous", "Candidiasis",
        "Drug Eruption", "Eczema", "Infestations/Bites", "Lichen", "Lupus",
        "Moles", "Psoriasis", "Rosacea", "Seborrheic Keratoses", "Skin Cancer",
        "Sun/Sunlight Damage", "Tinea", "Unknown/Normal", "Vascular Tumors",
        "Vasculitis", "Vitiligo", "Warts"
    ]
    
    # Required recommendation fields per spec
    required_fields = [
        "general_advice",
        "home_remedies",
        "precautions",
        "when_to_see_doctor"
    ]
    
    # Additional fields in implementation
    additional_fields = ["immediate_care", "lifestyle_tips"]
    
    print(f"\nChecking {len(expected_classes)} disease classes...")
    print(f"Required fields: {required_fields}")
    print(f"Additional fields: {additional_fields}")
    
    missing_diseases = []
    incomplete_diseases = []
    complete_count = 0
    
    for disease in expected_classes:
        if disease not in RECOMMENDATIONS:
            missing_diseases.append(disease)
            print(f"  ✗ {disease}: MISSING")
            continue
        
        disease_recs = RECOMMENDATIONS[disease]
        
        # Check for mild severity level (minimum requirement)
        if "mild" not in disease_recs:
            incomplete_diseases.append(f"{disease} (no mild level)")
            print(f"  ~ {disease}: Missing 'mild' severity level")
            continue
        
        # Check required fields in mild level
        mild_recs = disease_recs["mild"]
        missing_fields = [f for f in required_fields if f not in mild_recs]
        
        if missing_fields:
            incomplete_diseases.append(f"{disease} (missing: {missing_fields})")
            print(f"  ~ {disease}: Missing fields {missing_fields}")
        else:
            # Check severity levels
            severities = list(disease_recs.keys())
            complete_count += 1
            print(f"  ✓ {disease}: Complete ({', '.join(severities)})")
    
    print(f"\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total diseases in database: {len(RECOMMENDATIONS)}")
    print(f"Expected classes: {len(expected_classes)}")
    print(f"Complete diseases: {complete_count}/{len(expected_classes)}")
    print(f"Missing diseases: {len(missing_diseases)}")
    print(f"Incomplete diseases: {len(incomplete_diseases)}")
    
    return len(missing_diseases) == 0


def test_severity_levels():
    """Test that all severity levels have proper recommendations"""
    print("\n" + "=" * 70)
    print("Testing Severity Levels (mild/moderate/severe)")
    print("=" * 70)
    
    test_diseases = ["Acne", "Skin Cancer", "Eczema", "Psoriasis", "Drug Eruption"]
    severity_levels = ["mild", "moderate", "severe"]
    
    for disease in test_diseases:
        if disease not in RECOMMENDATIONS:
            print(f"  ✗ {disease}: Not found")
            continue
            
        print(f"\n  {disease}:")
        disease_recs = RECOMMENDATIONS[disease]
        
        for severity in severity_levels:
            if severity in disease_recs:
                recs = disease_recs[severity]
                home_remedies_count = len(recs.get("home_remedies", []))
                precautions_count = len(recs.get("precautions", []))
                print(f"    ✓ {severity}: {home_remedies_count} remedies, {precautions_count} precautions")
            else:
                print(f"    ~ {severity}: Not defined")


def test_recommendation_content():
    """Test the content quality of recommendations"""
    print("\n" + "=" * 70)
    print("Testing Recommendation Content Quality")
    print("=" * 70)
    
    # Test Acne as specified in requirements
    print("\n  Testing Acne (as per spec):")
    acne_mild = RECOMMENDATIONS.get("Acne", {}).get("mild", {})
    
    # Check general_advice
    general = acne_mild.get("general_advice", "")
    print(f"    general_advice: {general[:60]}...")
    
    # Check home_remedies
    remedies = acne_mild.get("home_remedies", [])
    print(f"    home_remedies ({len(remedies)}):")
    for r in remedies[:3]:
        print(f"      - {r}")
    
    # Check precautions
    precautions = acne_mild.get("precautions", [])
    print(f"    precautions ({len(precautions)}):")
    for p in precautions[:3]:
        print(f"      - {p}")
    
    # Check when_to_see_doctor
    when_doc = acne_mild.get("when_to_see_doctor", "")
    print(f"    when_to_see_doctor: {when_doc}")


def test_generate_recommendations():
    """Test the generate_recommendations function"""
    print("\n" + "=" * 70)
    print("Testing generate_recommendations() Function")
    print("=" * 70)
    
    test_cases = [
        {"disease": "Acne", "severity": "mild", "symptoms": ["pimples"], "confidence": 0.9},
        {"disease": "Skin Cancer", "severity": "severe", "symptoms": ["new_growth"], "confidence": 0.85},
        {"disease": "Eczema", "severity": "moderate", "symptoms": ["itching", "redness"], "confidence": 0.7},
        {"disease": "Unknown Disease", "severity": "mild", "symptoms": [], "confidence": 0.5},
    ]
    
    for case in test_cases:
        print(f"\n  {case['disease']} ({case['severity']}):")
        
        result = generate_recommendations(
            case["disease"],
            case["severity"],
            case["symptoms"],
            case["confidence"]
        )
        
        print(f"    general_advice: {result.get('general_advice', 'N/A')[:50]}...")
        print(f"    home_remedies: {len(result.get('home_remedies', []))} items")
        print(f"    precautions: {len(result.get('precautions', []))} items")
        print(f"    when_to_see_doctor: {result.get('when_to_see_doctor', 'N/A')[:40]}...")
        
        if "warning" in result:
            print(f"    ⚠️ Warning: {result['warning']}")


def test_low_confidence_handling():
    """Test that low confidence adds appropriate warnings"""
    print("\n" + "=" * 70)
    print("Testing Low Confidence Handling")
    print("=" * 70)
    
    # High confidence
    high_conf = generate_recommendations("Acne", "mild", [], confidence=0.9)
    print(f"\n  High confidence (0.9):")
    print(f"    Contains 'low' warning: {'low' in high_conf.get('general_advice', '').lower()}")
    
    # Low confidence
    low_conf = generate_recommendations("Acne", "mild", [], confidence=0.4)
    print(f"\n  Low confidence (0.4):")
    print(f"    Contains 'low' warning: {'low' in low_conf.get('general_advice', '').lower()}")
    print(f"    Advice: {low_conf.get('general_advice', '')[:80]}...")


def test_severity_warnings():
    """Test that severe conditions get appropriate warnings"""
    print("\n" + "=" * 70)
    print("Testing Severity Warnings")
    print("=" * 70)
    
    for severity in ["mild", "moderate", "severe"]:
        result = generate_recommendations("Skin Cancer", severity, [], confidence=0.9)
        has_warning = "warning" in result
        print(f"  {severity}: Has warning = {has_warning}")
        if has_warning:
            print(f"    Warning: {result['warning']}")


def test_disclaimer():
    """Test the medical disclaimer"""
    print("\n" + "=" * 70)
    print("Testing Medical Disclaimer")
    print("=" * 70)
    
    disclaimer = get_disclaimer()
    print(f"\n  Disclaimer ({len(disclaimer)} chars):")
    print(f"    {disclaimer[:100]}...")
    
    # Check for required elements
    required_terms = ["informational", "NOT", "medical", "diagnosis", "professional"]
    for term in required_terms:
        found = term.lower() in disclaimer.lower()
        status = "✓" if found else "✗"
        print(f"    {status} Contains '{term}': {found}")


def test_all_diseases_have_recommendations():
    """Comprehensive test of all diseases"""
    print("\n" + "=" * 70)
    print("Testing All Diseases Have Valid Recommendations")
    print("=" * 70)
    
    all_diseases = list(RECOMMENDATIONS.keys())
    print(f"\n  Total diseases in database: {len(all_diseases)}")
    
    valid_count = 0
    for disease in all_diseases:
        recs = RECOMMENDATIONS[disease]
        has_mild = "mild" in recs
        has_advice = bool(recs.get("mild", {}).get("general_advice"))
        
        if has_mild and has_advice:
            valid_count += 1
        else:
            print(f"    ✗ {disease}: Invalid structure")
    
    print(f"\n  Valid diseases: {valid_count}/{len(all_diseases)}")
    return valid_count == len(all_diseases)


def main():
    print("=" * 70)
    print("Feature 6: Recommendation Engine - Complete Test Suite")
    print("=" * 70)
    
    # Test database structure
    structure_ok = test_recommendation_database_structure()
    
    # Test severity levels
    test_severity_levels()
    
    # Test content quality
    test_recommendation_content()
    
    # Test generation function
    test_generate_recommendations()
    
    # Test low confidence handling
    test_low_confidence_handling()
    
    # Test severity warnings
    test_severity_warnings()
    
    # Test disclaimer
    test_disclaimer()
    
    # Test all diseases
    all_valid = test_all_diseases_have_recommendations()
    
    print("\n" + "=" * 70)
    print("Feature 6 Recommendation Engine - Test Results")
    print("=" * 70)
    
    if structure_ok and all_valid:
        print("✅ All tests passed!")
    else:
        print("⚠️ Some tests need attention")
    
    print("\nRecommendation Structure (per spec):")
    print("  - general_advice: Clear explanation of condition")
    print("  - home_remedies: Safe home treatments")
    print("  - precautions: Things to avoid")
    print("  - when_to_see_doctor: Medical consultation criteria")
    print("\nAdditional fields implemented:")
    print("  - immediate_care: Immediate steps to take")
    print("  - lifestyle_tips: Long-term management")


if __name__ == "__main__":
    main()
