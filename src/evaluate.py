import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.models import load_model
import cv2
import yaml
from src.data_loader import load_config, load_metadata, prepare_data

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def evaluate_model(model_path, test_gen, cfg):
    model = load_model(model_path)
    test_loss, test_acc = model.evaluate(test_gen, steps=len(test_gen))
    print(f"Test Accuracy: {test_acc:.4f}")

    # Predictions
    y_pred = model.predict(test_gen, steps=len(test_gen))
    y_pred_classes = np.argmax(y_pred, axis=1)
    y_true = test_gen.classes

    # Report
    print(classification_report(y_true, y_pred_classes, target_names=list(cfg['class_names'].values())))

    # Confusion Matrix
    cm = confusion_matrix(y_true, y_pred_classes)
    plt.figure(figsize=(8, 6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion Matrix')
    plt.colorbar()
    tick_marks = np.arange(len(cfg['class_names']))
    plt.xticks(tick_marks, list(cfg['class_names'].values()), rotation=45)
    plt.yticks(tick_marks, list(cfg['class_names'].values()))
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.savefig('../outputs/confusion_matrix.png')
    plt.close()

def predict_single_image(image_path, model, img_size):
    img = cv2.imread(image_path)
    img = cv2.resize(img, img_size)
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)
    pred = model.predict(img)
    class_idx = np.argmax(pred)
    confidence = np.max(pred)
    cfg = load_config()
    return list(cfg['class_names'].values())[class_idx], confidence

if __name__ == '__main__':
    cfg = load_config()
    df = load_metadata(cfg['data']['dir'])
    _, _, test_gen = prepare_data(df, cfg['data']['dir'], tuple(cfg['data']['img_size']), cfg['data']['batch_size'])
    model_path = os.path.join(cfg['paths']['models_dir'], 'best_skin_model.h5')
    evaluate_model(model_path, test_gen, cfg)

    # Test single (use a path from test set)
    sample_path = '../data/HAM10000/HAM10000_images/ISIC_0024306.jpg'  # Example; replace with real
    if os.path.exists(sample_path):
        model = load_model(model_path)
        pred_class, conf = predict_single_image(sample_path, model, tuple(cfg['data']['img_size']))
        print(f"Predicted: {pred_class} (conf: {conf:.2f})")