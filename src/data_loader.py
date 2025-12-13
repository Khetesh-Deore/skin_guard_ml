# src/data_loader.py
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import yaml
import numpy as np

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_metadata(data_dir):
    metadata_path = os.path.join(data_dir, 'HAM10000_metadata.csv')
    df = pd.read_csv(metadata_path)
    print(f"Dataset shape: {df.shape}")
    print(df['dx'].value_counts())
    return df

def prepare_data(df, data_dir, img_size, batch_size, shuffle=True):
    """
    Returns: train_generator, val_generator, test_generator, class_weights
    NOTE: For compatibility with Keras' flow_from_dataframe + class_mode='sparse',
    we will create both an integer label column (label_int) and a string label column (label)
    and use the string one in the dataframe generator while computing class weights from integers.
    """
    cfg = load_config()
    class_map = {v: k for k, v in cfg['class_names'].items()}
    df['label_int'] = df['dx'].map(class_map)
    df = df.dropna(subset=['label_int'])
    # keep integer for class weight compute
    df['label_int'] = df['label_int'].astype(int)
    # For Keras flow_from_dataframe (sparse), convert to string labels (works reliably)
    df['label'] = df['label_int'].astype(str)

    df['image_path'] = df['image_id'].apply(lambda x: os.path.join(data_dir, 'HAM10000_images', f"{x}.jpg"))

    # Save one sample image for verification
    sample_img_path = df.iloc[0]['image_path']
    if os.path.exists(sample_img_path):
        sample_img = plt.imread(sample_img_path)
        if sample_img.dtype == 'uint8':
            sample_img = sample_img.astype('float32') / 255.0
        plt.figure(figsize=(6, 6))
        plt.imshow(sample_img)
        plt.title(f"Sample: {df.iloc[0]['dx']}")
        plt.axis('off')
        save_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'outputs', 'sample_image.png'))
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"Sample image saved to: {save_path}")
    else:
        print("Warning: Sample image missing - check data paths")

    # Check missing files
    missing = df[~df['image_path'].apply(os.path.exists)]
    print(f"Missing images: {len(missing)}")

    # Split with stratify on label_int
    train_df, temp_df = train_test_split(df, test_size=0.2, stratify=df['label_int'], random_state=42)
    val_df, test_df = train_test_split(temp_df, test_size=0.5, stratify=temp_df['label_int'], random_state=42)
    print(f"Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")

    # Data generators
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.15,
        height_shift_range=0.15,
        horizontal_flip=True,
        zoom_range=0.15,
        fill_mode='nearest'
    )
    val_datagen = ImageDataGenerator(rescale=1./255)
    test_datagen = ImageDataGenerator(rescale=1./255)

    target_size = tuple(img_size)

    train_generator = train_datagen.flow_from_dataframe(
        dataframe=train_df,
        x_col='image_path',
        y_col='label',           # string labels (works with class_mode='sparse')
        target_size=target_size,
        batch_size=batch_size,
        class_mode='sparse',
        shuffle=shuffle
    )

    val_generator = val_datagen.flow_from_dataframe(
        dataframe=val_df,
        x_col='image_path',
        y_col='label',
        target_size=target_size,
        batch_size=batch_size,
        class_mode='sparse',
        shuffle=False
    )

    test_generator = test_datagen.flow_from_dataframe(
        dataframe=test_df,
        x_col='image_path',
        y_col='label',
        target_size=target_size,
        batch_size=batch_size,
        class_mode='sparse',
        shuffle=False
    )

    # Compute class weights using the integer labels from train_df
    y_train = train_df['label_int'].values
    classes = np.unique(y_train)
    weights = compute_class_weight(class_weight='balanced', classes=classes, y=y_train)
    # compute_class_weight returns array aligned with classes array; create dict mapping class index -> weight
    class_weights = {int(c): float(w) for c, w in zip(classes, weights)}
    print("Class weights:", class_weights)

    return train_generator, val_generator, test_generator, class_weights
