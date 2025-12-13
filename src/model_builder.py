# src/model_builder.py
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, Dropout, GlobalAveragePooling2D, BatchNormalization
from tensorflow.keras.optimizers import Adam
import yaml
import os

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def build_efficientnetb3(img_size, num_classes, learning_rate, fine_tune_at=200, pretrained=True):
    """
    Build an EfficientNetB3 model.
    If pretrained=True, use ImageNet weights and fine-tune last layers.
    """
    base_weights = 'imagenet' if pretrained else None

    base_model = tf.keras.applications.EfficientNetB3(
        include_top=False,
        weights=base_weights,
        input_shape=(*img_size, 3)
    )

    # Freeze the base
    base_model.trainable = True  # set True so we can selectively unfreeze
    # Freeze all layers except last `fine_tune_at` layers
    for layer in base_model.layers[:-fine_tune_at]:
        layer.trainable = False

    x = base_model.output
    x = GlobalAveragePooling2D(name='avg_pool')(x)
    x = BatchNormalization(name='bn')(x)
    x = Dropout(0.3)(x)
    x = Dense(512, activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.3)(x)
    outputs = Dense(num_classes, activation='softmax', name='predictions')(x)

    model = Model(inputs=base_model.input, outputs=outputs, name='efficientnetb3')

    # Compile with sparse loss (we use integer labels)
    model.compile(
        optimizer=Adam(learning_rate=learning_rate),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

if __name__ == '__main__':
    cfg = load_config()
    model = build_efficientnetb3(tuple(cfg['data']['img_size']), cfg['model']['num_classes'],
                                 cfg['model']['learning_rate'], cfg['model']['fine_tune_at'], cfg['model']['pretrained'])
    model.summary()
