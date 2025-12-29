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
        "Warts": "Warts"
    }
    
    label_to_idx = {name: idx for idx, name in labels.items()}
    folder_to_idx = {}
    
    for folder, label_name in folder_mapping.items():
        if label_name in label_to_idx:
            folder_to_idx[folder] = label_to_idx[label_name]
    
    return folder_to_idx


def preprocess_image(image_path, target_size=IMG_SIZE):
    """Preprocess image for model inference."""
    img = Image.open(image_path)
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    size = (target_size, target_size)
    img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    
    image_array = np.asarray(img)
    normalized = (image_array.astype(np.float32) / 127.5) - 1.0
    
    data = np.ndarray(shape=(1, target_size, target_size, 3), dtype=np.float32)
    data[0] = normalized
    
    return data


def load_test_data(test_path, folder_to_idx, max_per_class=None):
    """Load all test images and their labels"""
    images = []
    labels = []
    
    if not test_path.exists():
        return images, labels
    
    for folder_name in os.listdir(test_path):
        folder_path = test_path / folder_name
        if not folder_path.is_dir() or folder_name not in folder_to_idx:
            continue
        
        label_idx = folder_to_idx[folder_name]
        image_files = [f for f in os.listdir(folder_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if max_per_class:
            image_files = image_files[:max_per_class]
        
        for img_file in image_files:
            images.append(str(folder_path / img_file))
            labels.append(label_idx)
    
    return images, labels


def load_onnx_model(model_path):
    """Load ONNX model for inference"""
    try:
        import onnxruntime as ort
        session = ort.InferenceSession(str(model_path), providers=['CPUExecutionProvider'])
        input_name = session.get_inputs()[0].name
        return session, input_name
    except ImportError:
        print("onnxruntime not installed")
        return None, None


def load_keras_model(model_path):
    """Load Keras model for inference"""
    try:
        # Try tf-keras first for Teachable Machine compatibility
        try:
            import tf_keras
            model = tf_keras.models.load_model(str(model_path), compile=False)
            print("    Loaded with tf-keras")
            return model
        except ImportError:
            pass
        
        # Fallback to tensorflow.keras
        import tensorflow as tf
        model = tf.keras.models.load_model(str(model_path), compile=False)
        print("    Loaded with tensorflow.keras")
        return model
    except Exception as e:
        print(f"    Error loading Keras model: {e}")
        return None


def evaluate_with_keras(model, images, true_labels, labels_dict):
    """Evaluate model accuracy using Keras"""
    total = len(images)
    correct = 0
    class_correct = defaultdict(int)
    class_total = defaultdict(int)
    
    print(f"\nEvaluating {total} images with Keras...")
    
    for i, (img_path, true_label) in enumerate(zip(images, true_labels)):
        try:
            img_array = preprocess_image(img_path)
            outputs = model.predict(img_array, verbose=0)
            pred_class = np.argmax(outputs[0])
            
            class_total[true_label] += 1
            if pred_class == true_label:
                correct += 1
                class_correct[true_label] += 1
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{total}...", end='\r')
        except Exception as e:
            print(f"\nError processing {img_path}: {e}")
    
    print()
    
    class_accuracy = {}
    for class_idx in sorted(class_total.keys()):
        class_name = labels_dict.get(class_idx, f"Unknown_{class_idx}")
        acc = class_correct[class_idx] / class_total[class_idx] if class_total[class_idx] > 0 else 0
        class_accuracy[class_name] = {
            'accuracy': acc,
            'correct': class_correct[class_idx],
            'total': class_total[class_idx]
        }
    
    return {
        'overall_accuracy': correct / total if total > 0 else 0,
        'correct': correct,
        'total': total,
        'class_accuracy': class_accuracy
    }


def evaluate_with_onnx(session, input_name, images, true_labels, labels_dict):
    """Evaluate model accuracy using ONNX Runtime"""
    total = len(images)
    correct = 0
    class_correct = defaultdict(int)
    class_total = defaultdict(int)
    
    print(f"\nEvaluating {total} images...")
    
    for i, (img_path, true_label) in enumerate(zip(images, true_labels)):
        try:
            img_array = preprocess_image(img_path)
            outputs = session.run(None, {input_name: img_array})
            pred_class = np.argmax(outputs[0][0])
            
            class_total[true_label] += 1
            if pred_class == true_label:
                correct += 1
                class_correct[true_label] += 1
            
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{total}...", end='\r')
        except Exception as e:
            print(f"\nError: {e}")
    
    print()
    
    class_accuracy = {}
    for class_idx in sorted(class_total.keys()):
        class_name = labels_dict.get(class_idx, f"Unknown_{class_idx}")
        acc = class_correct[class_idx] / class_total[class_idx] if class_total[class_idx] > 0 else 0
        class_accuracy[class_name] = {
            'accuracy': acc,
            'correct': class_correct[class_idx],
            'total': class_total[class_idx]
        }
    
    return {
        'overall_accuracy': correct / total if total > 0 else 0,
        'correct': correct,
        'total': total,
        'class_accuracy': class_accuracy
    }


def main():
    print("=" * 70)
    print("Model Accuracy Test")
    print("=" * 70)
    
    if not LABELS_PATH.exists():
        print(f"ERROR: Labels not found at {LABELS_PATH}")
        return
    
    use_onnx = ONNX_MODEL_PATH.exists()
    if not use_onnx and not MODEL_PATH.exists():
        print(f"ERROR: No model found")
        return
    
    if not TEST_DATA_PATH.exists():
        print(f"ERROR: Test data not found at {TEST_DATA_PATH}")
        return
    
    print(f"\nModel: {'ONNX' if use_onnx else 'Keras'}")
    
    # Load labels
    labels = load_labels(LABELS_PATH)
    print(f"Loaded {len(labels)} classes")
    
    # Create mapping
    folder_to_idx = get_folder_to_label_mapping(labels)
    
    # Load test data
    images, true_labels = load_test_data(TEST_DATA_PATH, folder_to_idx, max_per_class=20)
    print(f"Loaded {len(images)} test images")
    
    if len(images) == 0:
        print("ERROR: No test images found!")
        return
    
    # Evaluate
    if use_onnx:
        session, input_name = load_onnx_model(ONNX_MODEL_PATH)
        if session is None:
            return
        results = evaluate_with_onnx(session, input_name, images, true_labels, labels)
    else:
        print("\nLoading Keras model...")
        model = load_keras_model(MODEL_PATH)
        if model is None:
            print("ERROR: Failed to load model")
            return
        results = evaluate_with_keras(model, images, true_labels, labels)
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"\nOverall Accuracy: {results['overall_accuracy']*100:.2f}%")
    print(f"Correct: {results['correct']} / {results['total']}")
    
    print("\nPer-Class Accuracy:")
    print("-" * 50)
    for class_name, metrics in sorted(results['class_accuracy'].items()):
        print(f"  {class_name:<25} {metrics['accuracy']*100:5.1f}% ({metrics['correct']}/{metrics['total']})")
    
    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)


if __name__ == "__main__":
    main()
