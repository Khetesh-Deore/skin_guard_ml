"""
Script to retrain the skin disease classification model
with better parameters to avoid overfitting to one class.

Run this script to create a new model:
    python notebooks/retrain_model.py
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from sklearn.utils.class_weight import compute_class_weight

# Configuration
IMG_SIZE = 128  # Larger than 28x28 for better feature extraction
BATCH_SIZE = 32
EPOCHS = 50
NUM_CLASSES = 7

# Disease mapping
DISEASE_NAMES = {
    0: "Actinic keratoses",
    1: "Basal cell carcinoma", 
    2: "Benign keratosis-like lesions",
    3: "Dermatofibroma",
    4: "Melanoma",
    5: "Melanocytic nevi",
    6: "Vascular lesions"
}

def create_model(input_shape=(IMG_SIZE, IMG_SIZE, 3), num_classes=NUM_CLASSES):
    """Create a CNN model for skin disease classification"""
    
    # Use transfer learning with MobileNetV2 for better results
    base_model = keras.applications.MobileNetV2(
        input_shape=input_shape,
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model layers initially
    base_model.trainable = False
    
    model = keras.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.5),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


def create_simple_model(input_shape=(IMG_SIZE, IMG_SIZE, 3), num_classes=NUM_CLASSES):
    """Create a simple CNN model (if you don't want transfer learning)"""
    
    model = keras.Sequential([
        # Input
        layers.Input(shape=input_shape),
        
        # Block 1
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 2
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Block 3
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),
        
        # Dense layers
        layers.Flatten(),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    return model


def main():
    print("=" * 50)
    print("Skin Disease Classification Model Training")
    print("=" * 50)
    
    # Check for data directory
    data_dir = "data/HAM10000"  # Adjust this path to your dataset
    
    if not os.path.exists(data_dir):
        print(f"\nERROR: Data directory not found: {data_dir}")
        print("\nPlease download the HAM10000 dataset and organize it as:")
        print("data/HAM10000/")
        print("  ├── train/")
        print("  │   ├── akiec/  (Actinic keratoses)")
        print("  │   ├── bcc/    (Basal cell carcinoma)")
        print("  │   ├── bkl/    (Benign keratosis)")
        print("  │   ├── df/     (Dermatofibroma)")
        print("  │   ├── mel/    (Melanoma)")
        print("  │   ├── nv/     (Melanocytic nevi)")
        print("  │   └── vasc/   (Vascular lesions)")
        print("  └── test/")
        print("      └── (same structure)")
        return
    
    # Data augmentation for training
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        vertical_flip=True,
        fill_mode='nearest',
        validation_split=0.2
    )
    
    test_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load training data
    print("\nLoading training data...")
    train_generator = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )
    
    validation_generator = train_datagen.flow_from_directory(
        os.path.join(data_dir, 'train'),
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )
    
    # Compute class weights to handle imbalanced data
    print("\nComputing class weights...")
    class_weights = compute_class_weight(
        class_weight='balanced',
        classes=np.unique(train_generator.classes),
        y=train_generator.classes
    )
    class_weight_dict = dict(enumerate(class_weights))
    print(f"Class weights: {class_weight_dict}")
    
    # Create model
    print("\nCreating model...")
    model = create_simple_model()  # Use create_model() for transfer learning
    
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate=0.001),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    model.summary()
    
    # Callbacks
    callbacks = [
        keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=1e-7
        ),
        keras.callbacks.ModelCheckpoint(
            'Backend/models/best_model_new.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max'
        )
    ]
    
    # Train
    print("\nStarting training...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator,
        class_weight=class_weight_dict,
        callbacks=callbacks
    )
    
    # Save final model
    model.save('Backend/models/best_model_retrained.h5')
    print("\nModel saved to Backend/models/best_model_retrained.h5")
    
    # Update disease mapping with correct image size
    import json
    mapping = {str(i): name for i, name in DISEASE_NAMES.items()}
    with open('Backend/models/disease_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    print("Disease mapping updated")
    
    print("\n" + "=" * 50)
    print("Training complete!")
    print(f"Update MODEL_INPUT_SIZE environment variable to: {IMG_SIZE}x{IMG_SIZE}")
    print("Or update config.py to use the new model")
    print("=" * 50)


if __name__ == "__main__":
    main()
