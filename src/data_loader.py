import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for saving plots
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import yaml


def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def load_metadata(data_dir):
    metadata_path = os.path.join(data_dir, 'HAM10000_metadata.csv')
    df = pd.read_csv(metadata_path)

    print(f"Dataset shape: {df.shape}")
    print(df['dx'].value_counts())

    return df


def prepare_data(df, data_dir, img_size, batch_size):
    cfg = load_config()

    # Map label strings → numeric indices
    class_map = {v: k for k, v in cfg['class_names'].items()}
    df['label'] = df['dx'].map(class_map)

    # Remove rows where label doesn't exist
    df = df.dropna(subset=['label'])

    # 🔥 FIX: Keras requires labels to be strings even for class_mode="sparse"
    df['label'] = df['label'].astype(str)

    # Build full image path
    df['image_path'] = df['image_id'].apply(
        lambda x: os.path.join(data_dir, 'HAM10000_images', f"{x}.jpg")
    )

    # ---------------------------
    # Save ONE SAMPLE IMAGE
    # ---------------------------
    sample_img_path = df.iloc[0]['image_path']

    if os.path.exists(sample_img_path):
        sample_img = plt.imread(sample_img_path)

        # Normalize uint8 → float32 for imshow stability
        if sample_img.dtype == 'uint8':
            sample_img = sample_img.astype('float32') / 255.0

        plt.figure(figsize=(6, 6))
        plt.imshow(sample_img)
        plt.title(f"Sample: {df.iloc[0]['dx']}")
        plt.axis('off')

        save_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', 'outputs', 'sample_image.png')
        )
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()

        print(f"Sample image saved to: {save_path}")
    else:
        print("⚠ Warning: Sample image missing!")

    # ---------------------------
    # Check missing images
    # ---------------------------
    missing = df[~df['image_path'].apply(os.path.exists)]
    print(f"Missing images: {len(missing)}")

    # ---------------------------
    # Train/Val/Test Split
    # ---------------------------
    train_df, temp_df = train_test_split(
        df, test_size=0.2, stratify=df['label'], random_state=42
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.5, stratify=temp_df['label'], random_state=42
    )

    print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    # ---------------------------
    # IMAGE GENERATORS
    # ---------------------------
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        fill_mode='nearest'
    )
    val_datagen = ImageDataGenerator(rescale=1./255)
    test_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_dataframe(
        train_df,
        x_col='image_path',
        y_col='label',
        target_size=img_size,
        batch_size=batch_size,
        class_mode='sparse',
        shuffle=True
    )

    val_generator = val_datagen.flow_from_dataframe(
        val_df,
        x_col='image_path',
        y_col='label',
        target_size=img_size,
        batch_size=batch_size,
        class_mode='sparse',
        shuffle=False
    )

    test_generator = test_datagen.flow_from_dataframe(
        test_df,
        x_col='image_path',
        y_col='label',
        target_size=img_size,
        batch_size=batch_size,
        class_mode='sparse',
        shuffle=False
    )

    return train_generator, val_generator, test_generator


# ---------------------------
# MAIN EXECUTION
# ---------------------------
if __name__ == '__main__':
    cfg = load_config()
    df = load_metadata(cfg['data']['dir'])

    prepare_data(
        df,
        cfg['data']['dir'],
        tuple(cfg['data']['img_size']),
        cfg['data']['batch_size']
    )
