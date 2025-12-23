"""
High-Accuracy Skin Disease Classification Training Script
Using EfficientNetB0 with Transfer Learning

Expected accuracy: 85-95% on HAM10000 dataset

Usage:
    python notebooks/train_efficientnet.py

Requirements:
    - TensorFlow 2.x
    - HAM10000 dataset organized in folders
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import (
    EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TensorBoard
)
from sklearn.utils.class_weight import compute_class_weight
from datetime import datetime

# ============================================
# CONFIGURATION
# ============================================
IMG_SIZE = 224  # EfficientNet optimal size
BATCH_SIZE = 32
EPOCHS = 100
NUM_CLASSES = 7
LEARNING_RATE = 0.001
FINE_TUNE_LEARNING_RATE = 0.0001

# Paths
DATA_DIR = "data/images"  # Update this to your dataset path
MODEL_SAVE_PATH = "Backend/models/skin_efficientnet_best.h5"
MAPPING_PATH = "Backend/models/disease_mapping.json"

# Disease mapping (HAM10000 classes)
CLASS_NAMES = {
    'akiec': 'Actinic keratoses',
    'bcc': 'Basal cell carcinoma',
    'bkl': 'Benign keratosis-like lesions',
    'df': 'Dermatofibroma',
    'mel': 'Melanoma',
    'nv': 'Melanocytic nevi',
    'vasc': 'Vascular lesions'
}

# ============================================
# GPU CONFIGURATION
# ============================================
def setup_gpu():
    """Configure GPU for optimal training"""
    gpus = tf.config.list_physical_devices('GPU')
    if gpus:
        try:
            for gpu in gpus:
                tf.config.experimental.set_memory_growth(gpu, True)
            print(f"✓ Found {len(gpus)} GPU(s)")
        except RuntimeError as e:
            print(f"GPU setup error: {e}")
    else:
        print("⚠ No GPU found, using CPU (training will be slower)")


# ============================================
# DATA PREPARATION
# ============================================
def create_data_generators(data_dir, img_size, batch_size):
    """Create training and validation data generators with augmentation"""
    
    # Strong augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=360,  # Full rotation for skin lesions
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.8, 1.2],
        fill_mode='reflect',
        validation_split=0.2
    )
    
    # No augmentation for validation
    val_datagen = ImageDataGenerator(
        rescale=1./255,
        validation_split=0.2
    )
    
    print(f"\nLoading data from: {data_dir}")
    
    train_generator = train_datagen.flow_from_directory(
        data_dir,
        target_size=(img_size, img_size),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training',
        shuffle=True
    )
    
    val_generator = val_datagen.flow_from_directory(
        data_dir,
        target_size=(img_size, img_size),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation',
        shuffle=False
    )
    
    print(f"✓ Training samples: {train_generator.samples}")
    print(f"✓ Validation samples: {val_generator.samples}")
    print(f"✓ Classes: {train_generator.class_indices}")
    
    return train_generator, val_generator


def compute_class_weights(generator):
    """Compute class weights to handle imbalanced dataset"""
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(generator.classes),
        y=generator.classes
    )
    class_weight_dict = dict(enumerate(class_weights))
    print(f"\n✓ Class weights computed: {class_weight_dict}")
    return class_weight_dict


# ============================================
# MODEL ARCHITECTURE
# ============================================
def create_efficientnet_model(input_shape=(IMG_SIZE, IMG_SIZE, 3), num_classes=NUM_CLASSES):
    """
    Create EfficientNetB0 model with custom classification head
    
    Architecture:
    - EfficientNetB0 backbone (pretrained on ImageNet)
    - Global Average Pooling
    - Dense layers with dropout for regularization
    - Softmax output for multi-class classification
    """
    
    # Load pretrained EfficientNetB0
    base_model = keras.applications.EfficientNetB0(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model initially
    base_model.trainable = False
    
    # Build model
    inputs = keras.Input(shape=input_shape)
    
    # Preprocessing for EfficientNet
    x = keras.applications.efficientnet.preprocess_input(inputs)
    
    # Base model
    x = base_model(x, training=False)
    
    # Custom classification head
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)
    x = layers.Dense(256, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01))(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation='relu', kernel_regularizer=keras.regularizers.l2(0.01))(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation='softmax')(x)
    
    model = Model(inputs, outputs)
    
    return model, base_model


def unfreeze_model(model, base_model, num_layers_to_unfreeze=20):
    """Unfreeze top layers of base model for fine-tuning"""
    base_model.trainable = True
    
    # Freeze all layers except the last num_layers_to_unfreeze
    for layer in base_model.layers[:-num_layers_to_unfreeze]:
        layer.trainable = False
    
    trainable_count = sum([1 for layer in base_model.layers if layer.trainable])
    print(f"✓ Unfroze {trainable_count} layers for fine-tuning")
    
    return model


# ============================================
# TRAINING CALLBACKS
# ============================================
def create_callbacks(model_path):
    """Create training callbacks"""
    
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_dir = f"logs/fit/{timestamp}"
    
    callbacks = [
        # Save best model
        ModelCheckpoint(
            model_path,
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        
        # Early stopping
        EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        ),
        
        # Reduce learning rate on plateau
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7,
            verbose=1
        ),
        
        # TensorBoard logging
        TensorBoard(
            log_dir=log_dir,
            histogram_freq=1
        )
    ]
    
    return callbacks


# ============================================
# TRAINING FUNCTIONS
# ============================================
def train_phase1(model, train_gen, val_gen, class_weights, callbacks, epochs=20):
    """Phase 1: Train only the classification head (frozen backbone)"""
    
    print("\n" + "="*60)
    print("PHASE 1: Training Classification Head (Backbone Frozen)")
    print("="*60)
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history1 = model.fit(
        train_gen,
        epochs=epochs,
        validation_data=val_gen,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    
    return history1


def train_phase2(model, base_model, train_gen, val_gen, class_weights, callbacks, epochs=50):
    """Phase 2: Fine-tune the entire model"""
    
    print("\n" + "="*60)
    print("PHASE 2: Fine-Tuning (Unfreezing Top Layers)")
    print("="*60)
    
    # Unfreeze top layers
    model = unfreeze_model(model, base_model, num_layers_to_unfreeze=30)
    
    # Recompile with lower learning rate
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=FINE_TUNE_LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    history2 = model.fit(
        train_gen,
        epochs=epochs,
        validation_data=val_gen,
        class_weight=class_weights,
        callbacks=callbacks,
        verbose=1
    )
    
    return history2


# ============================================
# SAVE MODEL AND MAPPING
# ============================================
def save_disease_mapping(generator, mapping_path):
    """Save disease mapping JSON file"""
    
    # Get class indices from generator
    class_indices = generator.class_indices
    
    # Create mapping: index -> disease name
    mapping = {}
    for folder_name, idx in class_indices.items():
        disease_name = CLASS_NAMES.get(folder_name, folder_name)
        mapping[str(idx)] = disease_name
    
    # Save to JSON
    os.makedirs(os.path.dirname(mapping_path), exist_ok=True)
    with open(mapping_path, 'w') as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✓ Disease mapping saved to: {mapping_path}")
    print(f"  Mapping: {mapping}")


# ============================================
# MAIN TRAINING SCRIPT
# ============================================
def main():
    print("\n" + "="*60)
    print("  SKIN DISEASE CLASSIFICATION - EFFICIENTNET TRAINING")
    print("="*60)
    
    # Setup
    setup_gpu()
    
    # Check data directory
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ ERROR: Data directory not found: {DATA_DIR}")
        print("\nPlease organize your HAM10000 dataset as follows:")
        print(f"{DATA_DIR}/")
        print("  ├── akiec/  (Actinic keratoses images)")
        print("  ├── bcc/    (Basal cell carcinoma images)")
        print("  ├── bkl/    (Benign keratosis images)")
        print("  ├── df/     (Dermatofibroma images)")
        print("  ├── mel/    (Melanoma images)")
        print("  ├── nv/     (Melanocytic nevi images)")
        print("  └── vasc/   (Vascular lesions images)")
        print("\nYou can download HAM10000 from:")
        print("https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-ham10000")
        return
    
    # Create data generators
    train_gen, val_gen = create_data_generators(DATA_DIR, IMG_SIZE, BATCH_SIZE)
    
    # Compute class weights
    class_weights = compute_class_weights(train_gen)
    
    # Create model
    print("\n✓ Creating EfficientNetB0 model...")
    model, base_model = create_efficientnet_model()
    model.summary()
    
    # Create callbacks
    callbacks = create_callbacks(MODEL_SAVE_PATH)
    
    # Phase 1: Train classification head
    history1 = train_phase1(
        model, train_gen, val_gen, class_weights, callbacks, epochs=20
    )
    
    # Phase 2: Fine-tune
    history2 = train_phase2(
        model, base_model, train_gen, val_gen, class_weights, callbacks, epochs=EPOCHS-20
    )
    
    # Save disease mapping
    save_disease_mapping(train_gen, MAPPING_PATH)
    
    # Final evaluation
    print("\n" + "="*60)
    print("  TRAINING COMPLETE")
    print("="*60)
    
    val_loss, val_acc = model.evaluate(val_gen)
    print(f"\n✓ Final Validation Accuracy: {val_acc*100:.2f}%")
    print(f"✓ Final Validation Loss: {val_loss:.4f}")
    print(f"\n✓ Model saved to: {MODEL_SAVE_PATH}")
    
    # Instructions
    print("\n" + "="*60)
    print("  NEXT STEPS")
    print("="*60)
    print(f"""
1. Update Backend/config.py:
   MODEL_PATH = "{MODEL_SAVE_PATH}"

2. Set environment variable (or update image_processor.py):
   MODEL_INPUT_SIZE=224x224

3. Restart the backend:
   python Backend/app.py

4. Test with different skin images!
""")


if __name__ == "__main__":
    main()
