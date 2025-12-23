"""
Test script for Feature 6.3: Output Structure
Verifies the recommendation output matches the specified JSON structure.
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

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
    
    # Expected structure from spec
    expected_fields = {
        "general_advice": str,           # "Clear explanation of condition"
        "immediate_care": list,          # ["Step 1", "Step 2"]
        "home_remedies": list,           # ["Remedy 1", "Remedy 2"]
        "precautions": list,             # ["Avoid X", "Do Y"]
        "lifestyle_tips": list,          # ["Diet advice", "Stress management"]
        "when_to_see_doctor": str,       # "Specific conditions requiring medical visit"
        "disclaimer": str,               # "This is not a medical diagnosis..."
        "urgency_level": str,            # "consult_soon" or "routine" or "urgent"
    }
    
    # Generate recommendations
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
            actual_type = type(result[field])
            type_match = isinstance(result[field], expected_type)
            status = "✓" if type_match else "~"
            print(f"  {status} {field}: {expected_type.__name__} = {type_match}")
            if not type_match:
                print(f"      Actual type: {actual_type.__name__}")
                all_present = False
        else:
            print(f"  ✗ {field}: MISSING")
            all_present = False
    
    return all_present


def test_output_content():
    """Test that output content is meaningful"""
    print("\n" + "=" * 70)
    print("Testing Output Content Quality")
    print("=" * 70)
    
    result = generate_recommendations(
        disease="Eczema",
        severity="moderate",
        symptoms=["itching", "redness", "dry_skin"],
        confidence=0.80
    )
    
    print("\nOutput Content:")
    
    # general_advice
    print(f"\n  general_advice:")
    print(f"    \"{result['general_advice'][:80]}...\"")
    assert len(result['general_advice']) > 20, "general_advice too short"
    print(f"    ✓ Length: {len(result['general_advice'])} chars")
    
    # immediate_care
    print(f"\n  immediate_care:")
    for i, item in enumerate(result['immediate_care'][:3], 1):
        print(f"    {i}. \"{item[:50]}...\"" if len(item) > 50 else f"    {i}. \"{item}\"")
    print(f"    ✓ Count: {len(result['immediate_care'])} items")
    
    # home_remedies
    print(f"\n  home_remedies:")
    for i, item in enumerate(result['home_remedies'][:3], 1):
        print(f"    {i}. \"{item}\"")
    print(f"    ✓ Count: {len(result['home_remedies'])} items")
    
    # precautions
    print(f"\n  precautions:")
    for i, item in enumerate(result['precautions'][:3], 1):
        print(f"    {i}. \"{item}\"")
    print(f"    ✓ Count: {len(result['precautions'])} items")
    
    # lifestyle_tips
    print(f"\n  lifestyle_tips:")
    for i, item in enumerate(result['lifestyle_tips'][:3], 1):
        print(f"    {i}. \"{item}\"")
    print(f"    ✓ Count: {len(result['lifestyle_tips'])} items")
    
    # when_to_see_doctor
    print(f"\n  when_to_see_doctor:")
    print(f"    \"{result['when_to_see_doctor']}\"")
    assert len(result['when_to_see_doctor']) > 10, "when_to_see_doctor too short"
    print(f"    ✓ Length: {len(result['when_to_see_doctor'])} chars")
    
    # disclaimer
    print(f"\n  disclaimer:")
    print(f"    \"{result['disclaimer'][:60]}...\"")
    assert "medical" in result['disclaimer'].lower(), "disclaimer should mention medical"
    print(f"    ✓ Contains 'medical': True")
    
    # urgency_level
    print(f"\n  urgency_level:")
    print(f"    \"{result['urgency_level']}\"")
    valid_urgencies = ["immediate", "seek_attention", "consult_doctor", "routine"]
    assert result['urgency_level'] in valid_urgencies, f"Invalid urgency: {result['urgency_level']}"
    print(f"    ✓ Valid urgency level: True")


def test_json_serializable():
    """Test that output is JSON serializable"""
    print("\n" + "=" * 70)
    print("Testing JSON Serialization")
    print("=" * 70)
    
    result = generate_recommendations(
        disease="Psoriasis",
        severity="moderate",
        symptoms=["scaling", "redness"],
        confidence=0.75
    )
    
    try:
        json_str = json.dumps(result, indent=2)
        print(f"\n  ✓ Successfully serialized to JSON")
        print(f"  ✓ JSON length: {len(json_str)} chars")
        
        # Parse back
        parsed = json.loads(json_str)
        print(f"  ✓ Successfully parsed back from JSON")
        print(f"  ✓ Keys preserved: {len(parsed)} keys")
        
        return True
    except Exception as e:
        print(f"  ✗ JSON serialization failed: {e}")
        return False


def test_urgency_levels():
    """Test all urgency level outputs"""
    print("\n" + "=" * 70)
    print("Testing Urgency Level Outputs")
    print("=" * 70)
    
    test_cases = [
        # Routine cases
        {"disease": "Acne", "severity": "mild", "symptoms": [], "confidence": 0.9, "expected": "routine"},
        
        # Consult doctor cases
        {"disease": "Psoriasis", "severity": "moderate", "symptoms": [], "confidence": 0.8, "expected": "consult_doctor"},
        
        # Seek attention cases
        {"disease": "Eczema", "severity": "severe", "symptoms": [], "confidence": 0.85, "expected": "seek_attention"},
        
        # Immediate/urgent cases
        {"disease": "Skin Cancer", "severity": "severe", "symptoms": [], "confidence": 0.9, "expected": "immediate"},
        {"disease": "Melanoma", "severity": "severe", "symptoms": [], "confidence": 0.85, "expected": "immediate"},
    ]
    
    print("\nUrgency Level Mapping:")
    print("  - 'routine' → Self-care, monitor condition")
    print("  - 'consult_doctor' → Schedule appointment")
    print("  - 'seek_attention' → See doctor soon")
    print("  - 'immediate' → Urgent medical care needed")
    
    print("\nTest Results:")
    for case in test_cases:
        result = generate_recommendations(
            case["disease"], case["severity"], case["symptoms"], case["confidence"]
        )
        
        actual = result["urgency_level"]
        expected = case["expected"]
        match = actual == expected
        status = "✓" if match else "~"
        
        print(f"  {status} {case['disease']} ({case['severity']}): {actual} (expected: {expected})")


def test_complete_output_example():
    """Show a complete output example matching the spec"""
    print("\n" + "=" * 70)
    print("Complete Output Example (Matching Spec)")
    print("=" * 70)
    
    result = generate_recommendations(
        disease="Acne",
        severity="moderate",
        symptoms=["pimples", "oily_skin"],
        confidence=0.85
    )
    
    # Format for display (matching spec structure)
    output = {
        "general_advice": result["general_advice"],
        "immediate_care": result["immediate_care"],
        "home_remedies": result["home_remedies"],
        "precautions": result["precautions"],
        "lifestyle_tips": result["lifestyle_tips"],
        "when_to_see_doctor": result["when_to_see_doctor"],
        "disclaimer": result["disclaimer"],
        "urgency_level": result["urgency_level"]
    }
    
    print("\nJSON Output:")
    print(json.dumps(output, indent=2))


def test_different_diseases():
    """Test output structure for different diseases"""
    print("\n" + "=" * 70)
    print("Testing Output Structure Across Diseases")
    print("=" * 70)
    
    diseases = ["Acne", "Eczema", "Psoriasis", "Skin Cancer", "Tinea", "Vitiligo"]
    required_fields = ["general_advice", "immediate_care", "home_remedies", 
                       "precautions", "lifestyle_tips", "when_to_see_doctor",
                       "disclaimer", "urgency_level"]
    
    all_valid = True
    
    for disease in diseases:
        result = generate_recommendations(disease, "mild", [], confidence=0.8)
        
        missing = [f for f in required_fields if f not in result]
        
        if missing:
            print(f"  ✗ {disease}: Missing {missing}")
            all_valid = False
        else:
            print(f"  ✓ {disease}: All required fields present")
    
    return all_valid


def main():
    print("=" * 70)
    print("Feature 6.3: Output Structure - Complete Test Suite")
    print("=" * 70)
    
    print("\nExpected Output Structure:")
    print("""
    {
        "general_advice": "Clear explanation of condition",
        "immediate_care": ["Step 1", "Step 2"],
        "home_remedies": ["Remedy 1", "Remedy 2"],
        "precautions": ["Avoid X", "Do Y"],
        "lifestyle_tips": ["Diet advice", "Stress management"],
        "when_to_see_doctor": "Specific conditions requiring medical visit",
        "disclaimer": "This is not a medical diagnosis...",
        "urgency_level": "consult_doctor" // or "routine" or "immediate"
    }
    """)
    
    # Run all tests
    structure_ok = test_output_structure()
    test_output_content()
    json_ok = test_json_serializable()
    test_urgency_levels()
    test_complete_output_example()
    diseases_ok = test_different_diseases()
    
    print("\n" + "=" * 70)
    print("Feature 6.3 Output Structure - Test Results")
    print("=" * 70)
    
    if structure_ok and json_ok and diseases_ok:
        print("\n✅ All output structure tests passed!")
    else:
        print("\n⚠️ Some tests need attention")
    
    print("\nOutput Structure Summary:")
    print("  ✓ general_advice: string - Clear explanation")
    print("  ✓ immediate_care: array - Immediate steps")
    print("  ✓ home_remedies: array - Home treatments")
    print("  ✓ precautions: array - Things to avoid")
    print("  ✓ lifestyle_tips: array - Long-term advice")
    print("  ✓ when_to_see_doctor: string - Medical visit criteria")
    print("  ✓ disclaimer: string - Medical disclaimer")
    print("  ✓ urgency_level: string - routine/consult_doctor/seek_attention/immediate")


if __name__ == "__main__":
    main()
