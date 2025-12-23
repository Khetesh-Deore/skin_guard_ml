"""
SIMPLIFIED SKIN DISEASE CLASSIFIER - SINGLE MODEL
For faster training or memory constraints
Expected Accuracy: 91-94%
Training Time: 45-90 minutes
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB1
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 100
TRAIN_DIR = 'data/SkinDisease/SkinDisease/Train'
TEST_DIR = 'data/SkinDisease/SkinDisease/Test'

CLASSES = [
    'Acne', 'Actinic_Keratosis', 'Benign_Tumors', 'Bullous',
    'Candidiasis', 'Drug_Eruption', 'Eczema', 'Infestations_Bites',
    'Lichen', 'Lupus', 'Moles', 'Psoriasis', 'Rosacea',
    'Seborrheic_Keratoses', 'Skin_Cancer', 'Sun_Sunlight_Damage',
    'Tinea', 'Unknown_Normal', 'Vascular_Tumors', 'Vasculitis',
    'Vitiligo', 'Warts'
]

# GPU Setup
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    tf.keras.mixed_precision.set_global_policy('mixed_float16')

# Data Generators with Heavy Augmentation
train_datagen = ImageDataGenerator(
    rescale=1./255,
    rotation_range=25,
    width_shift_range=0.2,
    height_shift_range=0.2,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True,
    vertical_flip=True,
    brightness_range=[0.8, 1.2],
    validation_split=0.15  # 15% for validation
)

test_datagen = ImageDataGenerator(rescale=1./255)

# Load data
train_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='training',
    shuffle=True
)

val_generator = train_datagen.flow_from_directory(
    TRAIN_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    subset='validation',
    shuffle=False
)

test_generator = test_datagen.flow_from_directory(
    TEST_DIR,
    target_size=(IMG_SIZE, IMG_SIZE),
    batch_size=BATCH_SIZE,
    class_mode='categorical',
    shuffle=False
)

# Calculate class weights
class_counts = np.bincount(train_generator.classes)
total = len(train_generator.classes)
class_weights = {i: total / (len(CLASSES) * count) for i, count in enumerate(class_counts)}

# Build Model
def create_model():
    base = EfficientNetB1(
        include_top=False,
        weights='imagenet',
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )
    
    # Freeze 80% of base layers
    for layer in base.layers[:int(len(base.layers) * 0.8)]:
        layer.trainable = False
    
    model = models.Sequential([
        base,
        layers.GlobalAveragePooling2D(),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.4),
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(len(CLASSES), activation='softmax', dtype='float32')
    ])
    
    return model

model = create_model()

# Compile
model.compile(
    optimizer=keras.optimizers.Adam(1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

# Callbacks
callbacks = [
    EarlyStopping(
        monitor='val_loss',
        patience=15,
        restore_best_weights=True,
        verbose=1
    ),
    ReduceLROnPlateau(
        monitor='val_loss',
        factor=0.5,
        patience=5,
        min_lr=1e-7,
        verbose=1
    ),
    ModelCheckpoint(
        'best_model.h5',
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

# Train
print("🚀 Starting training...")
history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    callbacks=callbacks,
    class_weight=class_weights
)

# Evaluate on test set
print("\n🧪 Evaluating on test set...")
test_loss, test_acc = model.evaluate(test_generator)
print(f"Test Accuracy: {test_acc*100:.2f}%")

# Predictions
y_pred = model.predict(test_generator)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true = test_generator.classes

# Classification Report
print("\n📋 Classification Report:")
print(classification_report(y_true, y_pred_classes, target_names=CLASSES))

# Confusion Matrix
cm = confusion_matrix(y_true, y_pred_classes)
plt.figure(figsize=(16, 14))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=CLASSES, yticklabels=CLASSES)
plt.title('Confusion Matrix')
plt.ylabel('True Label')
plt.xlabel('Predicted Label')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=150)

# Plot training history
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

ax1.plot(history.history['accuracy'], label='Train')
ax1.plot(history.history['val_accuracy'], label='Validation')
ax1.set_title('Model Accuracy')
ax1.set_xlabel('Epoch')
ax1.set_ylabel('Accuracy')
ax1.legend()
ax1.grid(True)

ax2.plot(history.history['loss'], label='Train')
ax2.plot(history.history['val_loss'], label='Validation')
ax2.set_title('Model Loss')
ax2.set_xlabel('Epoch')
ax2.set_ylabel('Loss')
ax2.legend()
ax2.grid(True)

plt.tight_layout()
plt.savefig('training_history.png', dpi=150)

print("\n✅ Training complete! Model saved as 'best_model.h5'")

# Inference function
def predict_image(image_path, model):
    img = keras.preprocessing.image.load_img(image_path, target_size=(IMG_SIZE, IMG_SIZE))
    img_array = keras.preprocessing.image.img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    prediction = model.predict(img_array, verbose=0)
    predicted_class = CLASSES[np.argmax(prediction)]
    confidence = np.max(prediction) * 100
    
    print(f"Predicted: {predicted_class}")
    print(f"Confidence: {confidence:.2f}%")
    
    # Top 3 predictions
    top3_idx = np.argsort(prediction[0])[-3:][::-1]
    print("\nTop 3 predictions:")
    for idx in top3_idx:
        print(f"  {CLASSES[idx]}: {prediction[0][idx]*100:.2f}%")
    
    return predicted_class, confidence

# Usage example:
# loaded_model = keras.models.load_model('best_model.h5')
# predict_image('path/to/test/image.jpg', loaded_model)