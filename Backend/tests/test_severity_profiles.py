"""
Test script for Feature 5.2: Disease Severity Profiles
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modules.severity_analyzer import DISEASE_SEVERITY_BASE


def test_severity_profiles():
    """Verify all 22 disease classes have severity profiles"""
    
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
    
    missing = []
    
    for cls in expected_classes:
        if cls in DISEASE_SEVERITY_BASE:
            profile = DISEASE_SEVERITY_BASE[cls]
            baseline = profile.get("baseline", "unknown")
            print(f"  [OK] {cls}: baseline={baseline}")
        else:
            missing.append(cls)
            print(f"  [MISSING] {cls}")
    
    print(f"\nTotal defined: {len(expected_classes) - len(missing)}/22")
    return len(missing) == 0


if __name__ == "__main__":
    success = test_severity_profiles()
    sys.exit(0 if success else 1)
