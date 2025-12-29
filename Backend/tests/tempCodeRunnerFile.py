"""
Test script to evaluate model accuracy on SkinDisease test data.
Supports both ONNX and Keras models.
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from PIL import Image, ImageOps
from collections import defaultdict

# Add Backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "keras_model.h5"
ONNX_MODEL_PATH = BASE_DIR / "models" / "model.onnx"
LABELS_PATH = BASE_DIR / "models" / "labels.txt"
TEST_DATA_PATH = BASE_DIR.parent / "data" / "SkinDisease" / "SkinDisease" / "test"

IMG_SIZE = 224


def load_labels(labels_path):
    """Load labels from Teachable Machine labels.txt"""
    labels = {}
    with open(labels_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                parts = line.split(' ', 1)
                if len(parts) == 2:
                    idx, name = parts
                    labels[int(idx)] = name
    return labels


def get_folder_to_label_mapping(labels):
    """Map test folder names to label indices"""
    folder_mapping = {
        "Acne": "Acne",
        "Actinic_Keratosis": "Actinic Keratosis",
        "Benign_tumors": "Benign Tumors",
        "Bullous": "Bullous",
        "Candidiasis": "Candidiasis",
        "DrugEruption": "Drug Eruption",
        "Eczema": "Eczema",
        "Infestations_Bites": "Infestations/Bites",
        "Lichen": "Lichen",
        "Lupus": "Lupus",
        "Moles": "Moles",
        "Psoriasis": "Psoriasis",
        "Rosacea": "Rosacea",
        "Seborrh_Keratoses": "Seborrheic Keratoses",
        "SkinCancer": "Skin Cancer",
        "Sun_Sunlight_Damage": "Sun/Sunlight Damage",
        "Tinea": "Tinea",
        "Unknown_Normal": "Unknown/Normal",
        "Vascular_Tumors": "Vascular Tumors",
        "Vasculitis": "Vasculitis",
        "Vitiligo": "Vitiligo",
