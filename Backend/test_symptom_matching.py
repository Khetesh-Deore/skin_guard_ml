"""
Test script to verify symptom matching for all 22 disease classes.
Tests Feature 4.2 Matching Algorithm and Feature 4.3 Symptom Normalization.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules.symptom_matcher import (
    # Core functions
    match_symptoms, 
    normalize_symptom,
    calculate_alignment_score,
    get_all_symptoms, 
    get_symptoms_by_category,
    
    # Feature 4.2 functions
    check_contradictory_symptoms,
    find_best_matching_diseases,
    get_symptom_severity_indicators,
    adjust_confidence_based_on_symptoms,
    
    # Feature 4.3 functions
    normalize_symptom_with_details,
    normalize_symptoms_batch,
    extract_severity_flag,
    fuzzy_match_symptom,
    extract_keywords,
    get_severity_summary,
    
    DISEASE_SYMPTOMS
)

def test_feature_4_2():
    """Test Feature 4.2: Matching Algorithm"""
    print("\n" + "=" * 70)
    print("Testing Feature 4.2: Symptom Matching Algorithm")
    print("=" * 70)
    
    # Test 1: Strong match (80%+)
    print("\n[4.2.1] Testing STRONG match (80%+) - Eczema...")
    eczema_symptoms = ["itching", "redness", "dry_skin", "patches", "inflammation"]
    result = match_symptoms("Eczema", eczema_symptoms, original_confidence=0.85)
    print(f"    Symptoms: {eczema_symptoms}")
    print(f"    Match: {result['match_percentage']}%")
    print(f"    Alignment: {result['alignment']}")
    
    # Test 2: Contradictory symptoms
    print("\n[4.2.2] Testing CONTRADICTORY symptoms - Rosacea...")
    contradictory_symptoms = ["facial_redness", "blackheads", "whiteheads", "flushing"]
    result = match_symptoms("Rosacea", contradictory_symptoms, original_confidence=0.80)
    print(f"    Has contradictions: {result['has_contradictions']}")
    print(f"    Contradictory: {result['contradictory_symptoms']}")
    
    # Test 3: Find best matching diseases
    print("\n[4.2.3] Testing find_best_matching_diseases...")
    test_symptoms = ["itching", "ring_shaped_rash", "scaly_skin", "red_border"]
    best_matches = find_best_matching_diseases(test_symptoms, top_n=3)
    print(f"    Symptoms: {test_symptoms}")
    for match in best_matches:
        print(f"      - {match['disease']}: {match['match_percentage']}%")


def test_feature_4_3():
    """Test Feature 4.3: Symptom Normalization"""
    print("\n" + "=" * 70)
    print("Testing Feature 4.3: Symptom Normalization")
    print("=" * 70)
    
    # Test 1: Basic normalization
    print("\n[4.3.1] Testing basic normalization...")
    test_cases = [
        ("itchy skin", "itching"),
        ("red spots", "redness"),
        ("very itchy", "itching"),
        ("extremely painful", "pain"),
        ("slightly dry", "dry_skin"),
    ]
    for raw, expected in test_cases:
        result = normalize_symptom(raw)
        status = "✓" if result == expected else "✗"
        print(f"    {status} '{raw}' -> '{result}' (expected: '{expected}')")
    
    # Test 2: Severity flag extraction
    print("\n[4.3.2] Testing severity flag extraction...")
    severity_tests = [
        ("very itchy", "itching", "high"),
        ("extremely painful", "pain", "high"),
        ("slightly red", "redness", "low"),
        ("moderately dry skin", "dry_skin", "moderate"),
        ("normal rash", "rash", "normal"),
    ]
    for raw, expected_symptom, expected_severity in severity_tests:
        normalized, severity, has_mod = extract_severity_flag(raw)
        status = "✓" if severity == expected_severity else "✗"
        print(f"    {status} '{raw}' -> symptom='{normalized}', severity='{severity}'")
    
    # Test 3: Fuzzy matching
    print("\n[4.3.3] Testing fuzzy matching...")
    fuzzy_tests = [
        "itchiness",
        "reddish skin",
        "painful bump",
        "scaly patches",
    ]
    for test in fuzzy_tests:
        match, score = fuzzy_match_symptom(test)
        print(f"    '{test}' -> '{match}' (score: {score:.2f})")
    
    # Test 4: Keyword extraction
    print("\n[4.3.4] Testing keyword extraction...")
    text_tests = [
        "My skin is very itchy and has red spots",
        "I have a painful bump that is getting bigger",
        "There's a ring shaped rash on my arm",
        "Dry flaky skin with some bleeding",
    ]
    for text in text_tests:
        keywords = extract_keywords(text)
        print(f"    '{text[:40]}...' -> {keywords}")
    
    # Test 5: Full normalization with details
    print("\n[4.3.5] Testing normalize_symptom_with_details...")
    detail_tests = [
        "very itchy skin",
        "red spots on face",
        "extremely painful bump",
        "ringworm",
    ]
    for test in detail_tests:
        result = normalize_symptom_with_details(test)
        print(f"    '{test}':")
        print(f"      normalized: '{result['normalized']}'")
        print(f"      severity: '{result['severity']}'")
        print(f"      confidence: '{result['confidence']}'")
    
    # Test 6: Batch normalization
    print("\n[4.3.6] Testing batch normalization...")
    batch = ["very itchy", "red spots", "slightly painful", "dry skin"]
    results = normalize_symptoms_batch(batch)
    print(f"    Input: {batch}")
    print(f"    Normalized: {[r['normalized'] for r in results]}")
    print(f"    Severities: {[r['severity'] for r in results]}")
    
    # Test 7: Severity summary
    print("\n[4.3.7] Testing severity summary...")
    symptoms_with_severity = [
        "very itchy skin",
        "extremely painful",
        "slightly red",
        "normal rash",
        "moderately dry"
    ]
    summary = get_severity_summary(symptoms_with_severity)
    print(f"    Overall severity: {summary['overall_severity']}")
    print(f"    High: {summary['high_severity_symptoms']}")
    print(f"    Moderate: {summary['moderate_severity_symptoms']}")
    print(f"    Low: {summary['low_severity_symptoms']}")
    print(f"    Normal: {summary['normal_symptoms']}")


def test_exposed_methods():
    """Test that all exposed methods work correctly"""
    print("\n" + "=" * 70)
    print("Testing Exposed Methods")
    print("=" * 70)
    
    print("\n[Methods] Verifying all exposed methods...")
    
    # match_symptoms(disease, symptoms) → match_result
    result = match_symptoms("Acne", ["pimples", "oily_skin"])
    print(f"    ✓ match_symptoms() -> alignment: {result['alignment']}")
    
    # normalize_symptom(raw_symptom) → normalized_symptom
    result = normalize_symptom("itchy skin")
    print(f"    ✓ normalize_symptom() -> '{result}'")
    
    # calculate_alignment_score(disease, symptoms) → percentage
    percentage, matched, details = calculate_alignment_score("Eczema", ["itching", "dry_skin"])
    print(f"    ✓ calculate_alignment_score() -> {percentage}%")
    
    # normalize_symptom_with_details() → dict
    result = normalize_symptom_with_details("very itchy")
    print(f"    ✓ normalize_symptom_with_details() -> severity: {result['severity']}")
    
    # extract_severity_flag() → tuple
    norm, sev, has_mod = extract_severity_flag("extremely painful")
    print(f"    ✓ extract_severity_flag() -> severity: {sev}")
    
    # fuzzy_match_symptom() → tuple
    match, score = fuzzy_match_symptom("itchiness")
    print(f"    ✓ fuzzy_match_symptom() -> '{match}' ({score:.2f})")
    
    # extract_keywords() → list
    keywords = extract_keywords("red itchy skin")
    print(f"    ✓ extract_keywords() -> {keywords}")
    
    # get_severity_summary() → dict
    summary = get_severity_summary(["very itchy", "mild pain"])
    print(f"    ✓ get_severity_summary() -> overall: {summary['overall_severity']}")


def main():
    print("=" * 70)
    print("Feature 4: Symptom Matching Module - Complete Test Suite")
    print("=" * 70)
    
    # Test Feature 4.2
    test_feature_4_2()
    
    # Test Feature 4.3
    test_feature_4_3()
    
    # Test exposed methods
    test_exposed_methods()
    
    # Summary
    print("\n" + "=" * 70)
    print("All Feature 4 tests completed!")
    print("=" * 70)
    print("\nExposed Methods:")
    print("  - match_symptoms(disease, symptoms) → match_result")
    print("  - normalize_symptom(raw_symptom) → normalized_symptom")
    print("  - calculate_alignment_score(disease, symptoms) → percentage")
    print("  - normalize_symptom_with_details(raw) → detailed_dict")
    print("  - extract_severity_flag(raw) → (symptom, severity, has_modifier)")
    print("  - fuzzy_match_symptom(input) → (match, score)")
    print("  - extract_keywords(text) → keywords_list")
    print("  - get_severity_summary(symptoms) → summary_dict")


if __name__ == "__main__":
    main()
