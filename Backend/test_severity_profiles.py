"""
Test script for Feature 5.2: Disease Severity Profiles
Verifies all 22 disease classes have complete severity profiles.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from modules.severity_analyzer import DISEASE_SEVERITY_BASE


def test_severity_profiles():
    """Verify all 22 disease classes have severity profiles"""
    
    # Expected 22 classes from Teachable Machine
    expected_classes = [
        "Acne", "Actinic Keratosis", "Benign Tumors", "Bullous", "Candidiasis",
        "Drug Eruption", "Eczema", "Infestations/Bites", "Lichen", "Lupus",
        "Moles", "Psoriasis", "Rosacea", "Seborrheic Keratoses", "Skin Cancer",
        "Sun/Sunlight Damage", "Tinea", "Unknown/Normal", "Vascular Tumors",
        "Vasculitis", "Vitiligo", "Warts"
    ]
    
    print("=" * 70)
    print("Feature 5.2: Disease Severity Profiles - Verification")
    print("=" * 70)
    
    # Check each class
    missing = []
    profiles_summary = []
    
    for cls in expected_classes:
        if cls in DISEASE_SEVERITY_BASE:
            profile = DISEASE_SEVERITY_BASE[cls]
            baseline = profile.get("baseline", "unknown")
            escalate = profile.get("can_escalate_to", "unknown")
            indicators = profile.get("severe_if", [])
            description = profile.get("description", "")
            
            profiles_summary.append({
                "disease": cls,
                "baseline": baseline,
                "escalate_to": escalate,
                "indicator_count": len(indicators),
                "indicators": indicators
            })
            
            print(f"\n  [OK] {cls}")
            print(f"       Baseline: {baseline} -> Can escalate to: {escalate}")
            print(f"       Severe indicators ({len(indicators)}): {indicators[:3]}{'...' if len(indicators) > 3 else ''}")
        else:
            missing.append(cls)
            print(f"\n  [MISSING] {cls}")
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    total_defined = len([c for c in expected_classes if c in DISEASE_SEVERITY_BASE])
    print(f"\nTotal classes defined: {total_defined}/22")
    
    if missing:
        print(f"Missing classes: {missing}")
    else:
        print("All 22 disease classes have severity profiles!")
    
    # Summary by baseline severity
    print("\n" + "-" * 40)
    print("Distribution by Baseline Severity:")
    print("-" * 40)
    
    for level in ["mild", "moderate", "severe", "critical"]:
        diseases = [p["disease"] for p in profiles_summary if p["baseline"] == level]
        print(f"\n  {level.upper()} ({len(diseases)} diseases):")
        for d in diseases:
            print(f"    - {d}")
    
    # Summary by escalation potential
    print("\n" + "-" * 40)
    print("Diseases that can escalate to CRITICAL:")
    print("-" * 40)
    
    critical_escalation = [p["disease"] for p in profiles_summary if p["escalate_to"] == "critical"]
    for d in critical_escalation:
        print(f"  ⚠️  {d}")
    
    print("\n" + "-" * 40)
    print("Diseases that can escalate to SEVERE:")
    print("-" * 40)
    
    severe_escalation = [p["disease"] for p in profiles_summary if p["escalate_to"] == "severe"]
    for d in severe_escalation:
        print(f"  ⚡ {d}")
    
    # Indicator statistics
    print("\n" + "-" * 40)
    print("Severe Indicator Statistics:")
    print("-" * 40)
    
    total_indicators = sum(p["indicator_count"] for p in profiles_summary)
    avg_indicators = total_indicators / len(profiles_summary) if profiles_summary else 0
    max_indicators = max(p["indicator_count"] for p in profiles_summary) if profiles_summary else 0
    min_indicators = min(p["indicator_count"] for p in profiles_summary) if profiles_summary else 0
    
    print(f"  Total indicators defined: {total_indicators}")
    print(f"  Average per disease: {avg_indicators:.1f}")
    print(f"  Range: {min_indicators} - {max_indicators}")
    
    print("\n" + "=" * 70)
    print("Feature 5.2 verification complete!")
    print("=" * 70)
    
    return len(missing) == 0


if __name__ == "__main__":
    success = test_severity_profiles()
    sys.exit(0 if success else 1)
