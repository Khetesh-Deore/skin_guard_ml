"""
Manual Test for Feature 3 - Works around TensorFlow 2.20 model loading bug
"""

import numpy as np
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

print("=" * 60)
print("Manual Test: Feature 3 Logic Verification")
print("=" * 60)

# Test 1: Import the module
print("\n[Test 1] Importing predictor module...")
try:
    from modules import predictor
    print("✓ Module imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    exit(1)

# Test 2: Check disease mapping file
print("\n[Test 2] Checking disease mapping file...")
try:
    base_dir = Path(__file__).resolve().parent.parent
    mapping_path = base_dir / "models" / "disease_mapping.json"
    
    with open(mapping_path, 'r') as f:
        disease_mapping = json.load(f)
    
    print(f"✓ Disease mapping loaded: {len(disease_mapping)} classes")
except Exception as e:
    print(f"✗ Failed: {e}")

# Test 3: Test confidence level function
print("\n[Test 3] Testing confidence level function...")
try:
    test_cases = [
        (0.95, "high"),
        (0.85, "high"),
        (0.75, "medium"),
        (0.55, "low"),
    ]
    
    for score, expected in test_cases:
        result = predictor.get_confidence_level(score)
        status = "✓" if result == expected else "✗"
        print(f"  {status} Score {score:.2f} → {result} (expected: {expected})")
        
except Exception as e:
    print(f"✗ Test failed: {e}")

print("\n" + "=" * 60)
print("Logic Tests Complete!")
print("=" * 60)
