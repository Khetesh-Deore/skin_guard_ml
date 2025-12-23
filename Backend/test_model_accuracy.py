"""
Test script to evaluate Teachable Machine model accuracy on SkinDisease test data.
Uses keras_model.h5 trained from Teachable Machine website.

NOTE: Teachable Machine models require tf-keras (legacy Keras 2.x) for compatibility.
Install with: pip install tf-keras
"""

import os
import sys
import json
import numpy as np
from pathlib import Path
from PIL import Image
from collections import defaultdict

# Add Backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Force TensorFlow to use legacy Keras
os.environ['TF_USE_LEGACY_KERAS'] = '1'

import tensorflow as tf

# Try to use tf-keras for legacy model compatibility
try:
    import tf_keras as keras
    print("Using tf-keras (legacy Keras 2.x)")
except ImportError:
    # Fallback to regular keras
    from tensorflow import keras
    print("Using tensorflow.keras")


# Configuration
MODEL_PATH = Path(__file__).resolve().parent / "models" / "keras_model.h5"
LABELS_PATH = Path(__file__).resolve().parent / "models" / "labels.txt"
TEST_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "SkinDisease" / "SkinDisease" / "test"

# Teachable Machine uses 224x224 input
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
    # Folder names in test data -> label names in labels.txt
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
    
    # Create reverse mapping: label name -> index
    label_to_idx = {name: idx for idx, name in labels.items()}
    
    # Create folder -> index mapping
    folder_to_idx = {}
    for folder, label_name in folder_mapping.items():
        if label_name in label_to_idx:
            folder_to_idx[folder] = label_to_idx[label_name]
        else:
            print(f"Warning: Label '{label_name}' not found in labels.txt")
    
    return folder_to_idx


def preprocess_image(image_path, target_size=IMG_SIZE):
    """
    Preprocess image for Teachable Machine model.
    Uses official Teachable Machine preprocessing:
    - Center crop with ImageOps.fit and LANCZOS resampling
    - Normalize to [-1, 1] range
    """
    from PIL import ImageOps
    
    img = Image.open(image_path)
    
    # Convert to RGB if needed
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Teachable Machine uses center crop with LANCZOS resampling
    size = (target_size, target_size)
    img = ImageOps.fit(img, size, Image.Resampling.LANCZOS)
    
    # Convert to numpy array
    image_array = np.asarray(img)
    
    # Teachable Machine normalization: (pixel / 127.5) - 1 -> range [-1, 1]
    normalized_image_array = (image_array.astype(np.float32) / 127.5) - 1.0
    
    # Create array with batch dimension
    data = np.ndarray(shape=(1, target_size, target_size, 3), dtype=np.float32)
    data[0] = normalized_image_array
    
    return data


def load_test_data(test_path, folder_to_idx, max_per_class=None):
    """Load all test images and their labels"""
    images = []
    labels = []
    filenames = []
    
    for folder_name in os.listdir(test_path):
        folder_path = test_path / folder_name
        if not folder_path.is_dir():
            continue
        
        if folder_name not in folder_to_idx:
            print(f"Skipping unknown folder: {folder_name}")
            continue
        
        label_idx = folder_to_idx[folder_name]
        
        # Get image files
        image_files = [f for f in os.listdir(folder_path) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if max_per_class:
            image_files = image_files[:max_per_class]
        
        for img_file in image_files:
            img_path = folder_path / img_file
            images.append(str(img_path))
            labels.append(label_idx)
            filenames.append(f"{folder_name}/{img_file}")
    
    return images, labels, filenames


def evaluate_model(model, images, true_labels, labels_dict, batch_size=32):
    """Evaluate model accuracy on test data"""
    
    total = len(images)
    correct = 0
    predictions = []
    
    # Per-class metrics
    class_correct = defaultdict(int)
    class_total = defaultdict(int)
    
    print(f"\nEvaluating {total} images...")
    
    for i in range(0, total, batch_size):
        batch_images = images[i:i+batch_size]
        batch_labels = true_labels[i:i+batch_size]
        
        # Process batch
        batch_arrays = []
        for img_path in batch_images:
            try:
                arr = preprocess_image(img_path)
                batch_arrays.append(arr[0])  # Remove batch dim for stacking
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                batch_arrays.append(np.zeros((IMG_SIZE, IMG_SIZE, 3), dtype=np.float32))
        
        batch_input = np.array(batch_arrays)
        
        # Predict
        batch_preds = model.predict(batch_input, verbose=0)
        batch_pred_classes = np.argmax(batch_preds, axis=1)
        
        # Calculate metrics
        for j, (pred_class, true_class) in enumerate(zip(batch_pred_classes, batch_labels)):
            predictions.append(pred_class)
            class_total[true_class] += 1
            
            if pred_class == true_class:
                correct += 1
                class_correct[true_class] += 1
        
        # Progress
        processed = min(i + batch_size, total)
        print(f"  Processed {processed}/{total} images...", end='\r')
    
    print()  # New line after progress
    
    # Calculate overall accuracy
    accuracy = correct / total if total > 0 else 0
    
    # Calculate per-class accuracy
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
        'overall_accuracy': accuracy,
        'correct': correct,
        'total': total,
        'class_accuracy': class_accuracy,
        'predictions': predictions
    }


def main():
    print("=" * 70)
    print("Teachable Machine Model Accuracy Test")
    print("Model: keras_model.h5 (trained on SkinDisease dataset)")
    print("=" * 70)
    
    # Check paths
    if not MODEL_PATH.exists():
        print(f"ERROR: Model not found at {MODEL_PATH}")
        return
    
    if not LABELS_PATH.exists():
        print(f"ERROR: Labels not found at {LABELS_PATH}")
        return
    
    if not TEST_DATA_PATH.exists():
        print(f"ERROR: Test data not found at {TEST_DATA_PATH}")
        return
    
    print(f"\nModel path: {MODEL_PATH}")
    print(f"Labels path: {LABELS_PATH}")
    print(f"Test data path: {TEST_DATA_PATH}")
    
    # Load labels
    print("\n[1] Loading labels...")
    labels = load_labels(LABELS_PATH)
    print(f"    Loaded {len(labels)} classes")
    
    # Create folder mapping
    print("\n[2] Creating folder to label mapping...")
    folder_to_idx = get_folder_to_label_mapping(labels)
    print(f"    Mapped {len(folder_to_idx)} folders")
    
    # Load model
    print("\n[3] Loading Teachable Machine model...")
    try:
        # Try loading with tf-keras first (legacy Keras 2.x compatible)
        try:
            import tf_keras
            model = tf_keras.models.load_model(str(MODEL_PATH), compile=False)
            print(f"    Loaded with tf-keras")
        except ImportError:
            # Fallback: try with tensorflow.keras
            model = tf.keras.models.load_model(str(MODEL_PATH), compile=False)
            print(f"    Loaded with tf.keras")
        
        print(f"    Model loaded successfully")
        print(f"    Input shape: {model.input_shape}")
        print(f"    Output shape: {model.output_shape}")
    except Exception as e:
        print(f"    ERROR loading model: {e}")
        print("\n    The Teachable Machine model requires tf-keras for compatibility.")
        print("    Install it with: pip install tf-keras")
        import traceback
        traceback.print_exc()
        return
    
    # Load test data
    print("\n[4] Loading test images...")
    images, true_labels, filenames = load_test_data(TEST_DATA_PATH, folder_to_idx)
    print(f"    Loaded {len(images)} test images")
    
    if len(images) == 0:
        print("    ERROR: No test images found!")
        return
    
    # Evaluate
    print("\n[5] Evaluating model...")
    results = evaluate_model(model, images, true_labels, labels)
    
    # Print results
    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    
    print(f"\nOverall Accuracy: {results['overall_accuracy']*100:.2f}%")
    print(f"Correct: {results['correct']} / {results['total']}")
    
    print("\n" + "-" * 70)
    print("Per-Class Accuracy:")
    print("-" * 70)
    print(f"{'Class':<30} {'Accuracy':>10} {'Correct':>10} {'Total':>10}")
    print("-" * 70)
    
    for class_name, metrics in sorted(results['class_accuracy'].items()):
        acc_str = f"{metrics['accuracy']*100:.1f}%"
        print(f"{class_name:<30} {acc_str:>10} {metrics['correct']:>10} {metrics['total']:>10}")
    
    print("-" * 70)
    
    # Summary statistics
    accuracies = [m['accuracy'] for m in results['class_accuracy'].values()]
    if accuracies:
        print(f"\nMean per-class accuracy: {np.mean(accuracies)*100:.2f}%")
        print(f"Min class accuracy: {np.min(accuracies)*100:.2f}%")
        print(f"Max class accuracy: {np.max(accuracies)*100:.2f}%")
    
    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    main()
