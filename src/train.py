import os
import matplotlib.pyplot as plt
from src.data_loader import load_config, load_metadata, prepare_data
from src.model_builder import build_model
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard


def train():
    # Load config
    cfg = load_config()

    data_dir = cfg['data']['dir']
    img_size = tuple(cfg['data']['img_size'])
    batch_size = cfg['data']['batch_size']
    epochs = cfg['model']['epochs']
    num_classes = cfg['model']['num_classes']

    # Load dataset
    df = load_metadata(data_dir)

    # Prepare generators
    train_gen, val_gen, _ = prepare_data(df, data_dir, img_size, batch_size)

    # Build model
    model = build_model(img_size, num_classes, cfg['model']['learning_rate'])

    # Output directories from config
    models_dir = cfg['paths']['models_dir']
    logs_dir = cfg['paths']['logs_dir']
    outputs_dir = cfg['paths']['outputs_dir']

    # Ensure directories exist
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)
    os.makedirs(outputs_dir, exist_ok=True)

    # Callbacks
    callbacks = [
        EarlyStopping(
            monitor='val_loss',
            patience=10,
            restore_best_weights=True
        ),
        ModelCheckpoint(
            os.path.join(models_dir, 'best_skin_model.h5'),
            monitor='val_accuracy',
            save_best_only=True
        ),
        TensorBoard(log_dir=logs_dir)
    ]

    # Train model
    history = model.fit(
        train_gen,
        steps_per_epoch=len(train_gen),
        epochs=epochs,
        validation_data=val_gen,
        validation_steps=len(val_gen),
        callbacks=callbacks,
        verbose=1
    )

    # Plot accuracy/loss curves
    plt.figure(figsize=(12, 4))

    # Accuracy plot
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Train Accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
    plt.title('Accuracy Progress')
    plt.legend()

    # Loss plot
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Train Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.title('Loss Progress')
    plt.legend()

    # Save training curve
    plot_path = os.path.join(outputs_dir, 'training_curves.png')
    plt.savefig(plot_path)
    plt.close()

    print(f"Training curves saved at: {plot_path}")
    print(f"Best model saved at: {os.path.join(models_dir, 'best_skin_model.h5')}")


if __name__ == '__main__':
    train()
