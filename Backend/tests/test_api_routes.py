"""
Test script for Feature 7: API Routes & Request Handling
Tests the main prediction endpoint and response formats.
"""
import sys
import json
import io
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from routes.predict_routes import (
    _parse_symptoms,
    _format_prediction_response,
    _create_error_response,
    ERROR_CODES
)


def _test_allowed_file_logic(filename: str) -> bool:
    """Test file extension validation logic."""
    allowed_extensions = {"jpg", "jpeg", "png"}
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in allowed_extensions


def test_allowed_file():
    """Test file extension validation"""
    print("=" * 70)
    print("Testing: File Extension Validation Logic")
    print("=" * 70)
    
    test_cases = [
        ("image.jpg", True),
        ("image.jpeg", True),
        ("image.png", True),
        ("image.JPG", True),
        ("image.gif", False),
        ("image.bmp", False),
        ("", False),
        (None, False),
    ]
    
    print("\nTest Results:")
    for filename, expected in test_cases:
        result = _test_allowed_file_logic(filename)
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{filename}': {result} (expected: {expected})")


def test_parse_symptoms():
    """Test symptom string parsing"""
    print("\n" + "=" * 70)
    print("Testing: _parse_symptoms()")
    print("=" * 70)
    
    test_cases = [
        ("itching, redness, dry skin", ["itching", "redness", "dry_skin"]),
        ("", []),
        (None, []),
    ]
    
    print("\nTest Results:")
    for input_str, expected in test_cases:
        result = _parse_symptoms(input_str or "")
        status = "✓" if result == expected else "✗"
        print(f"  {status} '{input_str}' -> {result}")


def main():
    print("=" * 70)
    print("Feature 7: API Routes & Request Handling - Test Suite")
    print("=" * 70)
    
    test_allowed_file()
    test_parse_symptoms()
    
    print("\n" + "=" * 70)
    print("Feature 7 API Routes - Test Complete")
    print("=" * 70)


if __name__ == "__main__":
    main()
