# src/train.py
import os
import yaml
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

# Set threading to reduce spikes on CPU
tf.config.threading.set_inter_op_parallelism_threads(1)
tf.config.threading.set_intra_op_parallelism_threads(1)

from src.data_loader import load_config, load_metadata, prepare_data
from src.model_builder import build_efficientnetb3
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau, TensorBoard

def train():
    cfg = load_config()
    data_dir = cfg['data']['dir']
    img_size = tuple(cfg['data']['img_size'])
    batch_size = cfg['data']['batch_size']
    epochs = cfg['model']['epochs']
    num_classes = cfg['model']['num_classes']
    lr = cfg['model']['learning_rate']
    fine_tune_at = cfg['model'].get('fine_tune_at', 200)

    os.makedirs(cfg['paths']['models_dir'], exist_ok=True)
    os.makedirs(cfg['paths']['logs_dir'], exist_ok=True)
    os.makedirs(cfg['paths']['outputs_dir'], exist_ok=True)

    # Load and prepare data
    df = load_metadata(data_dir)
    train_gen, val_gen, test_gen, class_weights = prepare_data(df, data_dir, img_size, batch_size, shuffle=True)

    # Build model
    model = build_efficientnetb3(img_size, num_classes, lr, fine_tune_at=fine_tune_at, pretrained=cfg['model'].get('pretrained', True))
    model.summary()

    # Callbacks
    callbacks = [
        EarlyStopping(monitor='val_loss', patience=8, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, min_lr=1e-7, verbose=1),
        ModelCheckpoint(os.path.join(cfg['paths']['models_dir'], 'best_efficientnetb3.keras'),
                        monitor='val_accuracy', save_best_only=True, save_format='keras'),
        TensorBoard(log_dir=cfg['paths']['logs_dir'])
    ]

    # Train
    try:
        history = model.fit(
            train_gen,
            steps_per_epoch=len(train_gen),
            epochs=epochs,
            validation_data=val_gen,
            validation_steps=len(val_gen),
            callbacks=callbacks,
            class_weight=class_weights,
            verbose=1
        )
    except tf.errors.ResourceExhaustedError as e:
        print("ResourceExhaustedError during training. Try reducing batch_size or img_size or use GPU.")
        print(e)
        return

    # Save training curves
    out_png = os.path.join(cfg['paths']['outputs_dir'], 'training_curves_efficientnetb3.png')
    plt.figure(figsize=(12, 4))
    plt.subplot(1,2,1)
    plt.plot(history.history.get('accuracy', []), label='train_acc')
    plt.plot(history.history.get('val_accuracy', []), label='val_acc')
    plt.legend(); plt.title('Accuracy')

    plt.subplot(1,2,2)
    plt.plot(history.history.get('loss', []), label='train_loss')
    plt.plot(history.history.get('val_loss', []), label='val_loss')
    plt.legend(); plt.title('Loss')

    plt.savefig(out_png)
    plt.close()
    print("Training curves saved to:", out_png)
    print("Best model saved to:", os.path.join(cfg['paths']['models_dir'], 'best_efficientnetb3.keras'))

if __name__ == '__main__':
    train()
