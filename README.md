# Skin Guard ML: Skin Disease Detection Model Training

## Overview
Trains a CNN from scratch on HAM10000 dataset for skin disease classification.

## Setup
1. Install deps: `pip install -r requirements.txt`
2. Download HAM10000 dataset to `data/HAM10000/` (images + metadata.csv)
3. Run: `python src/train.py`

## Usage
- Training: `python src/train.py`
- Evaluate: `python src/evaluate.py`
- TensorBoard: `tensorboard --logdir logs/`

## Structure
- `src/`: Core scripts
- `models/`: Saved .h5 files
- `notebooks/`: Jupyter prototyping

## Expected Output
- Test Accuracy: ~70-80%
- Model: `./models/best_skin_model.h5`