"""
SIMPLIFIED SKIN DISEASE CLASSIFIER - SINGLE MODEL (UPDATED & FIXED)
Expected Accuracy: 91–94%
GPU: RTX 2050 (Mixed Precision Enabled)
TensorFlow: 2.13 (Windows-safe)
"""

import os
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import EfficientNetB1
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns

# ===============================
# CONFIGURATION
# ===============================
IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 100

TRAIN_DIR = 'data/SkinDisease/SkinDisease/Train'
TEST_DIR  = 'data/SkinDisease/SkinDisease/Test'

CLASSES = [
    'Acne', 'Actinic_Keratosis', 'Benign_Tumors', 'Bullous',
    'Candidiasis', 'Drug_Eruption', 'Eczema', 'Infestations_Bites',
    'Lichen', 'Lupus', 'Moles', 'Psoriasis', 'Rosacea',
    'Seborrheic_Keratoses', 'Skin_Cancer', 'Sun_Sunlight_Damage',
    'Tinea', 'Unknown_Normal', 'Vascular_Tumors', 'Vasculitis',
    'Vitiligo', 'Warts'
]

NUM_CLASSES = len(CLASSES)

# ===============================
# GPU & MIXED PRECISION SETUP
# ===============================
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
    tf.keras.mixed_precision.set_global_policy('mixed_float16')

print("✅ GPU Enabled:", bool(gpus))
print("✅ Mixed Precision:", tf.keras.mixed_precision.global_policy())

# ===============================
# DATA GENERATORS
# ===============================
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
    validation_split=0.15
)

test_datagen = ImageDataGenerator(rescale=1./255)

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

# ===============================
# CLASS WEIGHTS (FIXED)
# ===============================
class_counts = np.bincount(train_generator.classes)
total_samples = np.sum(class_counts)

class_weights = {
    i: float(total_samples / (NUM_CLASSES * class_counts[i]))
    for i in range(NUM_CLASSES)
}

# ===============================
# MODEL DEFINITION
# ===============================
def create_model():
    base_model = EfficientNetB1(
        include_top=False,
        weights='imagenet',
        input_shape=(IMG_SIZE, IMG_SIZE, 3)
    )

    # Freeze first 80%
    for layer in base_model.layers[:int(0.8 * len(base_model.layers))]:
        layer.trainable = False

    x = base_model.output
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.5)(x)

    x = layers.Dense(512, activation='relu')(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dropout(0.4)(x)

    x = layers.Dense(256, activation='relu')(x)
    x = layers.Dropout(0.3)(x)

    outputs = layers.Dense(
        NUM_CLASSES,
        activation='softmax',
        dtype='float32'   # IMPORTANT for mixed precision
    )(x)

    return models.Model(inputs=base_model.input, outputs=outputs)

model = create_model()

# ===============================
# COMPILE
# ===============================
model.compile(
    optimizer=keras.optimizers.Adam(learning_rate=1e-4),
    loss='categorical_crossentropy',
    metrics=['accuracy']
)

model.summary()

# ===============================
# CALLBACKS (JSON BUG FIXED)
# ===============================
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
        filepath='best_model.keras',   # ✅ FIX
        monitor='val_accuracy',
        save_best_only=True,
        verbose=1
    )
]

# ===============================
# TRAINING
# ===============================
print("\n🚀 Starting Training...\n")

history = model.fit(
    train_generator,
    validation_data=val_generator,
    epochs=EPOCHS,
    class_weight=class_weights,
    callbacks=callbacks
)

# ===============================
# EVALUATION
# ===============================
print("\n🧪 Evaluating on Test Set...")
test_loss, test_acc = model.evaluate(test_generator)
print(f"✅ Test Accuracy: {test_acc * 100:.2f}%")

# ===============================
# REPORTS
# ===============================
y_pred = model.predict(test_generator)
y_pred_classes = np.argmax(y_pred, axis=1)
y_true = test_generator.classes

print("\n📋 Classification Report:\n")
print(classification_report(y_true, y_pred_classes, target_names=CLASSES))

cm = confusion_matrix(y_true, y_pred_classes)

plt.figure(figsize=(16, 14))
sns.heatmap(
    cm,
    annot=True,
    fmt='d',
    cmap='Blues',
    xticklabels=CLASSES,
    yticklabels=CLASSES
)
plt.title("Confusion Matrix")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig("confusion_matrix.png", dpi=150)
plt.close()

# ===============================
# TRAINING CURVES
# ===============================
plt.figure(figsize=(14, 5))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train')
plt.plot(history.history['val_accuracy'], label='Validation')
plt.title("Accuracy")
plt.legend()
plt.grid(True)

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train')
plt.plot(history.history['val_loss'], label='Validation')
plt.title("Loss")
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.savefig("training_history.png", dpi=150)
plt.close()

print("\n✅ Training Complete! Model saved as best_model.keras")

# ===============================
# INFERENCE FUNCTION
# ===============================
def predict_image(image_path, model):
    img = keras.preprocessing.image.load_img(
        image_path,
        target_size=(IMG_SIZE, IMG_SIZE)
    )
    img = keras.preprocessing.image.img_to_array(img) / 255.0
    img = np.expand_dims(img, axis=0)

    preds = model.predict(img, verbose=0)[0]
    top3 = preds.argsort()[-3:][::-1]

    print("\n🔍 Prediction Result:")
    for i in top3:
        print(f"{CLASSES[i]}: {preds[i] * 100:.2f}%")

    return CLASSES[top3[0]], preds[top3[0]]
