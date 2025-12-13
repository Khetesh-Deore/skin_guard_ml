# src/evaluate.py
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import yaml
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow.keras.models import load_model
from src.data_loader import load_config, load_metadata, prepare_data

def evaluate():
    cfg = load_config()
    data_dir = cfg['data']['dir']
    img_size = tuple(cfg['data']['img_size'])
    batch_size = cfg['data']['batch_size']

    # prepare data (use same pipeline)
    df = load_metadata(data_dir)
    _, _, test_gen, _ = prepare_data(df, data_dir, img_size, batch_size, shuffle=False)

    model_path = os.path.join(cfg['paths']['models_dir'], 'best_efficientnetb3.keras')
    if not os.path.exists(model_path):
        print("Model not found at", model_path)
        return

    model = load_model(model_path)
    print("Loaded model:", model_path)

    # Evaluate
    loss, acc = model.evaluate(test_gen, steps=len(test_gen))
    print(f"Test loss: {loss:.4f}, Test accuracy: {acc:.4f}")

    preds = model.predict(test_gen, steps=len(test_gen))
    y_pred = np.argmax(preds, axis=1)
    y_true = test_gen.classes  # flow_from_dataframe stores class indices

    # Classification report
    cfg_all = load_config()
    class_names = list(cfg_all['class_names'].values())
    print(classification_report(y_true, y_pred, target_names=class_names))

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(8,6))
    plt.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    plt.title('Confusion matrix')
    plt.colorbar()
    tick_marks = np.arange(len(class_names))
    plt.xticks(tick_marks, class_names, rotation=45)
    plt.yticks(tick_marks, class_names)
    plt.ylabel('True label')
    plt.xlabel('Predicted label')
    out_cm = os.path.join(cfg['paths']['outputs_dir'], 'confusion_matrix_efficientnetb3.png')
    plt.savefig(out_cm, bbox_inches='tight')
    plt.close()
    print("Confusion matrix saved to:", out_cm)

if __name__ == '__main__':
    evaluate()
