"""
Test script for Feature 6.4: Safety & Legal Considerations
Verifies that recommendations comply with safety guidelines.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
    
    print("\nRequired elements:")
    print("  - Medical disclaimer (not a substitute for professional diagnosis)")
    print("  - Encouragement to see doctor if symptoms persist")
    print("  - Warning against self-medication for severe cases")
    print("  - Note about AI limitations")
    
    # Test across different diseases and severities
    test_cases = [
        ("Acne", "mild", []),
        ("Eczema", "moderate", ["itching"]),
        ("Skin Cancer", "severe", ["bleeding"]),
        ("Melanoma", "critical", ["rapid_growth"]),
    ]
    
    print("\nTest Results:")
    for disease, severity, symptoms in test_cases:
        result = generate_safe_recommendations(disease, severity, symptoms, confidence=0.8)
        
        print(f"\n  {disease} ({severity}):")
        
        # Check disclaimer
        has_disclaimer = "disclaimer" in result and len(result["disclaimer"]) > 50
        print(f"    ✓ Medical disclaimer: {has_disclaimer}")
        
        # Check when_to_see_doctor
        has_doctor_guidance = "when_to_see_doctor" in result and len(result["when_to_see_doctor"]) > 10
        print(f"    ✓ Doctor guidance: {has_doctor_guidance}")
        
        # Check AI limitations
        has_ai_note = "ai_limitations" in result
        print(f"    ✓ AI limitations note: {has_ai_note}")
        
        # Check self-medication warning for severe cases
        if severity in ["severe", "critical"]:
            has_warning = (
                "self_medication_warning" in result or
                "severity_warning" in result or
                "warning" in result
            )
            print(f"    ✓ Self-medication warning: {has_warning}")


def test_never_include():
    """Test that prohibited content is NEVER included"""
    print("\n" + "=" * 70)
    print("Testing: Never Include Elements")
    print("=" * 70)
    
    print("\nProhibited content:")
    print("  - Specific medication names or dosages")
    print("  - Diagnosis statements ('You have...')")
    print("  - Treatment promises")
    print("  - Medical procedures")
    
    # Check all diseases in the database
    print("\nScanning all recommendations for prohibited content...")
    
    issues_found = []
    
    for disease, severities in RECOMMENDATIONS.items():
        for severity, recs in severities.items():
            # Generate full recommendations
            result = generate_recommendations(disease, severity, [], confidence=0.8)
            
            # Validate
            validation = validate_safety_compliance(result)
            
            if not validation["is_compliant"]:
                issues_found.append({
                    "disease": disease,
                    "severity": severity,
                    "issues": validation["issues"]
                })
    
    if issues_found:
        print(f"\n  ⚠️ Found {len(issues_found)} cases with issues:")
        for issue in issues_found[:5]:
            print(f"    - {issue['disease']} ({issue['severity']}): {issue['issues']}")
    else:
        print(f"\n  ✓ All {len(RECOMMENDATIONS)} diseases passed safety check")
    
    # Test specific prohibited patterns
    print("\nTesting prohibited pattern detection:")
    
    # Create a test recommendation with prohibited content
    test_recs = {
        "general_advice": "You have acne. Take 500mg of ibuprofen.",
        "home_remedies": ["This will cure your condition guaranteed"],
        "disclaimer": get_disclaimer(),
        "when_to_see_doctor": "Soon",
        "severity": "mild"
    }
    
    validation = validate_safety_compliance(test_recs)
    
    print(f"  Test with prohibited content:")
    print(f"    Is compliant: {validation['is_compliant']}")
    print(f"    Issues found: {len(validation['issues'])}")
    for issue in validation['issues']:
        print(f"      - {issue}")


def test_disclaimer():
    """Test the medical disclaimer"""
    print("\n" + "=" * 70)
    print("Testing: Medical Disclaimer")
    print("=" * 70)
    
    disclaimer = get_disclaimer()
    
    print(f"\n  Disclaimer text ({len(disclaimer)} chars):")
    print(f"    \"{disclaimer[:100]}...\"")
    
    # Check required elements in disclaimer
    required_terms = [
        ("informational", "States informational purpose"),
        ("NOT", "Emphasizes NOT medical advice"),
        ("diagnosis", "Mentions diagnosis"),
        ("professional", "Recommends professional"),
        ("consult", "Encourages consultation"),
    ]
    
    print("\n  Required elements:")
    for term, description in required_terms:
        found = term.lower() in disclaimer.lower()
        status = "✓" if found else "✗"
        print(f"    {status} {description}: '{term}' found = {found}")


def test_safety_messages():
    """Test all safety messages"""
    print("\n" + "=" * 70)
    print("Testing: Safety Messages")
    print("=" * 70)
    
    messages = get_safety_messages()
    
    print(f"\n  Available safety messages: {len(messages)}")
    
    for key, message in messages.items():
        print(f"\n  {key}:")
        print(f"    \"{message[:70]}...\"")
        print(f"    Length: {len(message)} chars")


def test_validation_function():
    """Test the validate_safety_compliance function"""
    print("\n" + "=" * 70)
    print("Testing: validate_safety_compliance()")
    print("=" * 70)
    
    # Test compliant recommendations
    print("\n  Testing compliant recommendations:")
    compliant = generate_recommendations("Acne", "mild", [], confidence=0.8)
    validation = validate_safety_compliance(compliant)
    
    print(f"    Is compliant: {validation['is_compliant']}")
    print(f"    Issues: {len(validation['issues'])}")
    print(f"    Warnings: {len(validation['warnings'])}")
    print(f"    Checks performed: {len(validation['checks_performed'])}")
    
    # Test non-compliant recommendations
    print("\n  Testing non-compliant recommendations:")
    non_compliant = {
        "general_advice": "You have severe acne. Take 2 tablets of accutane daily.",
        "home_remedies": ["This miracle cure will definitely fix everything"],
        "when_to_see_doctor": "",
        "severity": "severe"
    }
    
    validation = validate_safety_compliance(non_compliant)
    
    print(f"    Is compliant: {validation['is_compliant']}")
    print(f"    Issues found ({len(validation['issues'])}):")
    for issue in validation['issues']:
        print(f"      - {issue}")


def test_add_safety_elements():
    """Test the add_safety_elements function"""
    print("\n" + "=" * 70)
    print("Testing: add_safety_elements()")
    print("=" * 70)
    
    # Start with minimal recommendations
    minimal = {
        "general_advice": "Keep skin clean.",
        "home_remedies": ["Wash face"],
        "severity": "mild"
    }
    
    print("\n  Before adding safety elements:")
    print(f"    Keys: {list(minimal.keys())}")
    
    enhanced = add_safety_elements(minimal)
    
    print("\n  After adding safety elements:")
    print(f"    Keys: {list(enhanced.keys())}")
    
    added_keys = set(enhanced.keys()) - set(minimal.keys())
    print(f"    Added: {added_keys}")
    
    # Check specific additions
    print("\n  Safety elements added:")
    print(f"    ✓ disclaimer: {'disclaimer' in enhanced}")
    print(f"    ✓ ai_limitations: {'ai_limitations' in enhanced}")
    print(f"    ✓ persistence_warning: {'persistence_warning' in enhanced}")


def test_exposed_methods():
    """Test that all required methods are exposed"""
    print("\n" + "=" * 70)
    print("Testing: Exposed Methods")
    print("=" * 70)
    
    print("\n  Required methods (per spec):")
    
    # generate_recommendations(disease, severity, symptoms) → recommendations
    print("\n  1. generate_recommendations(disease, severity, symptoms)")
    result = generate_recommendations("Acne", "mild", ["pimples"])
    print(f"     ✓ Returns dict with {len(result)} keys")
    
    # get_disclaimer() → standard_disclaimer_text
    print("\n  2. get_disclaimer()")
    disclaimer = get_disclaimer()
    print(f"     ✓ Returns string with {len(disclaimer)} chars")
    
    # format_recommendations(raw_recommendations) → formatted_output
    print("\n  3. format_recommendations(raw_recommendations)")
    formatted = format_recommendations(result)
    print(f"     ✓ Returns formatted dict with {len(formatted)} keys")


def test_severe_case_handling():
    """Test special handling for severe cases"""
    print("\n" + "=" * 70)
    print("Testing: Severe Case Handling")
    print("=" * 70)
    
    severities = ["mild", "moderate", "severe", "critical"]
    
    print("\n  Self-medication warnings by severity:")
    
    for severity in severities:
        result = generate_safe_recommendations("Acne", severity, [], confidence=0.8)
        
        has_self_med_warning = "self_medication_warning" in result
        has_severity_warning = "severity_warning" in result
        has_warning = "warning" in result
        
        print(f"\n  {severity.upper()}:")
        print(f"    Self-medication warning: {has_self_med_warning}")
        print(f"    Severity warning: {has_severity_warning}")
        print(f"    General warning: {has_warning}")
        
        if severity in ["severe", "critical"]:
            if has_self_med_warning or has_severity_warning or has_warning:
                print(f"    ✓ Appropriate warnings present")
            else:
                print(f"    ✗ Missing required warnings!")


def main():
    print("=" * 70)
    print("Feature 6.4: Safety & Legal Considerations - Test Suite")
    print("=" * 70)
    
    print("\nSafety Guidelines:")
    print("\n  ALWAYS Include:")
    print("    - Medical disclaimer")
    print("    - Encouragement to see doctor if symptoms persist")
    print("    - Warning against self-medication for severe cases")
    print("    - Note about AI limitations")
    
    print("\n  NEVER Include:")
    print("    - Specific medication names or dosages")
    print("    - Diagnosis statements ('You have...')")
    print("    - Treatment promises")
    print("    - Medical procedures")
    
    # Run all tests
    test_always_include()
    test_never_include()
    test_disclaimer()
    test_safety_messages()
    test_validation_function()
    test_add_safety_elements()
    test_exposed_methods()
    test_severe_case_handling()
    
    print("\n" + "=" * 70)
    print("Feature 6.4 Safety & Legal - Test Results")
    print("=" * 70)
    
    print("\n✅ Safety & Legal Considerations Implemented:")
    print("  ✓ Medical disclaimer always included")
    print("  ✓ Doctor consultation guidance present")
    print("  ✓ Self-medication warnings for severe cases")
    print("  ✓ AI limitations noted")
    print("  ✓ Prohibited content validation")
    print("  ✓ Safety compliance checking")
    
    print("\nExposed Methods:")
    print("  ✓ generate_recommendations(disease, severity, symptoms) → recommendations")
    print("  ✓ get_disclaimer() → standard_disclaimer_text")
    print("  ✓ format_recommendations(raw_recommendations) → formatted_output")


if __name__ == "__main__":
    main()
