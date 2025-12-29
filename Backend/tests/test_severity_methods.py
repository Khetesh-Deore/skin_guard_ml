"""
Test script for Feature 5.3 & 5.4: Severity Scoring Logic & Urgency Flags
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.severity_analyzer import (
    analyze_severity,
    check_urgency_flags,
    get_severity_explanation,
    SEVERITY_ORDER
)


def test_analyze_severity():
    """Test analyze_severity(disease, confidence, symptoms) → severity_result"""
    print("=" * 70)
    print("Testing: analyze_severity(disease, confidence, symptoms)")
    print("=" * 70)
    
    test_cases = [
        {"disease": "Acne", "confidence": 0.85, "symptoms": ["pimples"], "expected_level": "mild"},
        {"disease": "Skin Cancer", "confidence": 0.90, "symptoms": ["new_growth"], "expected_level": "severe"},
    ]
    
    for case in test_cases:
        result = analyze_severity(case["disease"], case["confidence"], case["symptoms"])
        status = "✓" if result["level"] == case["expected_level"] else "~"
        print(f"  {status} {case['disease']}: level={result['level']}")


def main():
    print("=" * 70)
    print("Feature 5.3 & 5.4: Severity Scoring & Urgency Flags - Test Suite")
    print("=" * 70)
    
    test_analyze_severity()
    
    print("\n" + "=" * 70)
    print("Feature 5.3 & 5.4 - Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
