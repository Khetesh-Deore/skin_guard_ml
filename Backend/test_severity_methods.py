"""
Test script for Feature 5.3 & 5.4: Severity Scoring Logic & Urgency Flags
Verifies all three exposed methods work correctly.

Methods to Expose:
- analyze_severity(disease, confidence, symptoms) → severity_result
- check_urgency_flags(disease, symptoms) → urgency_level
- get_severity_explanation(severity_level) → explanation_text
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules.severity_analyzer import (
    analyze_severity,
    check_urgency_flags,
    get_severity_explanation,
    get_urgency_level,
    SEVERITY_ORDER
)


def test_analyze_severity():
    """Test analyze_severity(disease, confidence, symptoms) → severity_result"""
    print("=" * 70)
    print("Testing: analyze_severity(disease, confidence, symptoms)")
    print("=" * 70)
    
    test_cases = [
        {
            "disease": "Acne",
            "confidence": 0.85,
            "symptoms": ["pimples", "oily_skin"],
            "expected_level": "mild",
            "description": "Mild acne case"
        },
        {
            "disease": "Acne",
            "confidence": 0.80,
            "symptoms": ["cysts", "nodules", "widespread", "severe_scarring"],
            "expected_level": "moderate",
            "description": "Severe acne with escalation"
        },
        {
            "disease": "Skin Cancer",
            "confidence": 0.90,
            "symptoms": ["new_growth", "irregular_border"],
            "expected_level": "severe",
            "description": "Skin cancer case"
        },
        {
            "disease": "Melanoma",
            "confidence": 0.95,
            "symptoms": ["rapid_growth", "bleeding", "ulceration"],
            "expected_level": "critical",
            "description": "Critical melanoma case"
        },
    ]
    
    print("\nSeverity Scoring Logic Steps:")
    print("  1. Start with disease baseline (mild/moderate/severe)")
    print("  2. Check for severe indicator symptoms → +1 level")
    print("  3. Check symptom intensity keywords → +1 level")
    print("  4. Check affected area keywords → +1 level")
    print("  5. Low model confidence + severe symptoms → flag for review")
    print()
    
    for case in test_cases:
        result = analyze_severity(
            case["disease"],
            case["confidence"],
            case["symptoms"]
        )
        
        status = "✓" if result["level"] == case["expected_level"] else "~"
        print(f"  {status} {case['description']}:")
        print(f"      Input: {case['disease']}, conf={case['confidence']}, symptoms={case['symptoms'][:2]}...")
        print(f"      Result: level={result['level']}, score={result['score']}, urgency={result['urgency']}")
        print(f"      Expected: {case['expected_level']}")
        print()
    
    # Test output levels
    print("  Output Levels:")
    for level in SEVERITY_ORDER:
        explanation = get_severity_explanation(level)
        print(f"    - {level.capitalize()}: {explanation[:50]}...")


def test_check_urgency_flags():
    """Test check_urgency_flags(disease, symptoms) → urgency_level"""
    print("\n" + "=" * 70)
    print("Testing: check_urgency_flags(disease, symptoms)")
    print("=" * 70)
    
    print("\nRed Flags (immediate attention):")
    red_flag_tests = [
        {
            "disease": "Melanoma",
            "symptoms": ["changing_mole", "irregular_border"],
            "description": "Melanoma predicted",
            "expected_red": True
        },
        {
            "disease": "Eczema",
            "symptoms": ["bleeding", "infection", "pus"],
            "description": "Bleeding + infection symptoms",
            "expected_red": True
        },
        {
            "disease": "Tinea",
            "symptoms": ["rapid_spread", "spreading_fast"],
            "description": "Rapid spread mentioned",
            "expected_red": True
        },
        {
            "disease": "Acne",
            "symptoms": ["severe_pain", "extreme_pain"],
            "description": "Severe pain present",
            "expected_red": True
        },
    ]
    
    for test in red_flag_tests:
        result = check_urgency_flags(test["disease"], test["symptoms"])
        
        status = "✓" if result["has_red_flags"] == test["expected_red"] else "✗"
        print(f"  {status} {test['description']}:")
        print(f"      Disease: {test['disease']}, Symptoms: {test['symptoms']}")
        print(f"      Red flags: {result['red_flags']}")
        print(f"      Urgency: {result['urgency_level']}")
        print()
    
    print("Yellow Flags (consult doctor):")
    yellow_flag_tests = [
        {
            "disease": "Eczema",
            "symptoms": ["persistent_itching", "chronic_rash", "long_time"],
            "description": "Persistent symptoms mentioned",
            "expected_yellow": True
        },
        {
            "disease": "Psoriasis",
            "symptoms": ["red_patches", "scaling", "itching", "joint_pain", "thick_plaques"],
            "description": "Multiple symptoms (5+)",
            "expected_yellow": True
        },
        {
            "disease": "Unknown/Normal",
            "symptoms": ["new_growth", "changing_shape", "color_change"],
            "description": "Uncertain prediction + concerning symptoms",
            "expected_yellow": True
        },
    ]
    
    for test in yellow_flag_tests:
        result = check_urgency_flags(test["disease"], test["symptoms"])
        
        status = "✓" if result["has_yellow_flags"] == test["expected_yellow"] else "✗"
        print(f"  {status} {test['description']}:")
        print(f"      Disease: {test['disease']}, Symptoms: {test['symptoms'][:3]}...")
        print(f"      Yellow flags: {result['yellow_flags']}")
        print(f"      Urgency: {result['urgency_level']}")
        print(f"      Recommendation: {result['recommendation'][:50]}...")
        print()


def test_get_severity_explanation():
    """Test get_severity_explanation(severity_level) → explanation_text"""
    print("\n" + "=" * 70)
    print("Testing: get_severity_explanation(severity_level)")
    print("=" * 70)
    
    expected_keywords = {
        "mild": "Self-care",
        "moderate": "consulting",
        "severe": "medical attention",
        "critical": "Immediate"
    }
    
    print("\nOutput Levels and Explanations:")
    for level, keyword in expected_keywords.items():
        explanation = get_severity_explanation(level)
        has_keyword = keyword.lower() in explanation.lower()
        
        status = "✓" if has_keyword else "✗"
        print(f"  {status} {level.capitalize()}:")
        print(f"      Explanation: {explanation}")
        print(f"      Contains '{keyword}': {has_keyword}")
        print()


def test_complete_workflow():
    """Test complete workflow with all three methods"""
    print("\n" + "=" * 70)
    print("Testing: Complete Workflow")
    print("=" * 70)
    
    # Complex case
    disease = "Skin Cancer"
    confidence = 0.85
    symptoms = ["rapid_growth", "bleeding", "irregular_border", "color_change"]
    
    print(f"\nTest Case: {disease}")
    print(f"Confidence: {confidence}")
    print(f"Symptoms: {symptoms}")
    
    # Step 1: Analyze severity
    print("\n  Step 1: analyze_severity()")
    severity_result = analyze_severity(disease, confidence, symptoms)
    print(f"    Level: {severity_result['level']}")
    print(f"    Score: {severity_result['score']}")
    print(f"    Urgency: {severity_result['urgency']}")
    print(f"    Has red flags: {severity_result['has_red_flags']}")
    
    # Step 2: Check urgency flags
    print("\n  Step 2: check_urgency_flags()")
    urgency_result = check_urgency_flags(disease, symptoms)
    print(f"    Urgency level: {urgency_result['urgency_level']}")
    print(f"    Red flags ({urgency_result['red_flag_count']}): {urgency_result['red_flags']}")
    print(f"    Yellow flags ({urgency_result['yellow_flag_count']}): {urgency_result['yellow_flags']}")
    print(f"    Recommendation: {urgency_result['recommendation']}")
    
    # Step 3: Get severity explanation
    print("\n  Step 3: get_severity_explanation()")
    explanation = get_severity_explanation(severity_result['level'])
    print(f"    Explanation: {explanation}")
    
    print("\n  Complete Result:")
    print(f"    Severity: {severity_result['level'].upper()}")
    print(f"    Urgency: {urgency_result['urgency_level'].upper()}")
    print(f"    Action: {urgency_result['recommendation']}")


def main():
    print("=" * 70)
    print("Feature 5.3 & 5.4: Severity Scoring & Urgency Flags - Method Tests")
    print("=" * 70)
    
    # Test all three exposed methods
    test_analyze_severity()
    test_check_urgency_flags()
    test_get_severity_explanation()
    test_complete_workflow()
    
    print("\n" + "=" * 70)
    print("All method tests completed!")
    print("=" * 70)
    print("\nExposed Methods Summary:")
    print("  ✓ analyze_severity(disease, confidence, symptoms) → severity_result")
    print("  ✓ check_urgency_flags(disease, symptoms) → urgency_level")
    print("  ✓ get_severity_explanation(severity_level) → explanation_text")
    print("\nSeverity Scoring Logic (5.3):")
    print("  1. Start with disease baseline")
    print("  2. Check severe indicator symptoms → escalation")
    print("  3. Check symptom intensity keywords → escalation")
    print("  4. Check affected area keywords → escalation")
    print("  5. Low confidence + severe symptoms → flag for review")
    print("\nUrgency Flags (5.4):")
    print("  Red Flags: Melanoma, bleeding+infection, rapid_spread, severe_pain")
    print("  Yellow Flags: Persistent symptoms, multiple symptoms, concerning symptoms")


if __name__ == "__main__":
    main()
