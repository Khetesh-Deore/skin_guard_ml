# SkinGuard ML - AI-Powered Skin Disease Detection

![SkinGuard ML](https://img.shields.io/badge/SkinGuard-ML-blue)
![Python](https://img.shields.io/badge/Python-3.9+-green)
![React](https://img.shields.io/badge/React-18+-61DAFB)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

An intelligent skin disease detection system that uses deep learning to analyze skin images and provide preliminary assessments. The system combines image analysis with symptom matching to deliver comprehensive results including severity assessment and personalized recommendations.

> ⚠️ **Disclaimer**: This tool is for educational and informational purposes only. It is NOT a substitute for professional medical diagnosis. Always consult a qualified healthcare provider for accurate diagnosis and treatment.

## 📋 Table of Contents

- [Features](#-features)
- [Disease Classes](#-disease-classes-22-categories)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Dataset Information](#-dataset-information)
- [Model Training](#-model-training)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### Core Features
- **Image-Based Disease Detection**: Upload skin images for AI-powered analysis
- **22 Disease Classification**: Comprehensive coverage of common skin conditions
- **Symptom Matching**: Optional symptom input for enhanced accuracy
- **Severity Assessment**: Multi-factor severity analysis with urgency indicators
- **Personalized Recommendations**: Tailored advice based on condition and severity
- **Confidence Visualization**: Clear display of prediction confidence levels

### Technical Features
- **Real-time Analysis**: Fast prediction using optimized TensorFlow model
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **RESTful API**: Well-documented API for integration
- **Safety Compliance**: Medical disclaimers and safety validations
- **Error Handling**: Comprehensive error handling with user-friendly messages

## 🏥 Disease Classes (22 Categories)

The model is trained to detect the following skin conditions:

| # | Disease | Description |
|---|---------|-------------|
| 1 | **Acne** | Common skin condition affecting hair follicles and oil glands |
| 2 | **Actinic Keratosis** | Pre-cancerous rough, scaly patches from sun damage |
| 3 | **Benign Tumors** | Non-cancerous skin growths |
| 4 | **Bullous** | Blistering skin conditions |
| 5 | **Candidiasis** | Fungal infection caused by Candida |
| 6 | **Drug Eruption** | Skin reactions to medications |
| 7 | **Eczema** | Chronic inflammatory skin condition |
| 8 | **Infestations/Bites** | Skin reactions from insects or parasites |
| 9 | **Lichen** | Inflammatory condition affecting skin/mucous membranes |
| 10 | **Lupus** | Autoimmune condition with skin manifestations |
| 11 | **Moles** | Common skin growths (melanocytic nevi) |
| 12 | **Psoriasis** | Chronic autoimmune condition causing rapid skin cell buildup |
| 13 | **Rosacea** | Chronic facial redness and visible blood vessels |
| 14 | **Seborrheic Keratoses** | Common benign skin growths |
| 15 | **Skin Cancer** | Malignant skin conditions requiring immediate attention |
| 16 | **Sun/Sunlight Damage** | UV-induced skin damage |
| 17 | **Tinea** | Fungal skin infections (ringworm) |
| 18 | **Unknown/Normal** | Normal skin or unidentified conditions |
| 19 | **Vascular Tumors** | Blood vessel-related growths |
| 20 | **Vasculitis** | Inflammation of blood vessels |
| 21 | **Vitiligo** | Loss of skin pigmentation |
| 22 | **Warts** | Viral skin growths caused by HPV |

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │  Image   │  │ Symptom  │  │ Loading  │  │     Result       │ │
│  │  Upload  │  │  Input   │  │ Spinner  │  │    Display       │ │
│  └────┬─────┘  └────┬─────┘  └──────────┘  └────────┬─────────┘ │
│       │             │                               │           │
│       └─────────────┴───────────────────────────────┘           │
│                             │                                    │
│                    ┌────────┴────────┐                          │
│                    │   API Service   │                          │
│                    └────────┬────────┘                          │
└─────────────────────────────┼───────────────────────────────────┘
                              │ HTTP/REST
┌─────────────────────────────┼───────────────────────────────────┐
│                        Backend (Flask)                           │
│                    ┌────────┴────────┐                          │
│                    │  API Routes     │                          │
│                    └────────┬────────┘                          │
│       ┌─────────────────────┼─────────────────────┐             │
│       │                     │                     │             │
│  ┌────┴─────┐    ┌─────────┴─────────┐    ┌─────┴──────┐       │
│  │  Image   │    │    Predictor      │    │  Symptom   │       │
│  │Processor │    │  (TensorFlow)     │    │  Matcher   │       │
│  └──────────┘    └───────────────────┘    └────────────┘       │
│                           │                                     │
│       ┌───────────────────┼───────────────────┐                │
│       │                   │                   │                │
│  ┌────┴─────┐    ┌───────┴───────┐    ┌─────┴──────┐          │
│  │ Severity │    │Recommendation │    │   Safety   │          │
│  │ Analyzer │    │    Engine     │    │ Validator  │          │
│  └──────────┘    └───────────────┘    └────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Python 3.9+** - Core programming language
- **Flask** - Web framework for REST API
- **TensorFlow/Keras** - Deep learning framework
- **Pillow** - Image processing
- **NumPy** - Numerical computations
- **Flask-CORS** - Cross-origin resource sharing

### Frontend
- **React 18** - UI framework
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **CSS3** - Styling with responsive design

### ML Model
- **Architecture**: EfficientNet / Custom CNN
- **Input Size**: 224x224 RGB images
- **Output**: 22 class probabilities
- **Format**: TensorFlow SavedModel / Keras H5

## 📁 Project Structure

```
skin_guard_ml/
├── Backend/
│   ├── app.py                    # Flask application entry point
│   ├── config.py                 # Configuration settings
│   ├── requirements.txt          # Python dependencies
│   ├── models/
│   │   └── skin_model/           # Trained TensorFlow model
│   ├── modules/
│   │   ├── predictor.py          # ML prediction module
│   │   ├── image_processor.py    # Image preprocessing
│   │   ├── symptom_matcher.py    # Symptom matching logic
│   │   ├── severity_analyzer.py  # Severity assessment
│   │   └── recommendation_engine.py  # Recommendations
│   ├── routes/
│   │   └── predict_routes.py     # API endpoints
│   └── uploads/                  # Temporary upload directory
│
├── Frontend/
│   ├── src/
│   │   ├── App.jsx               # Main application component
│   │   ├── components/
│   │   │   ├── ImageUpload.jsx   # Image upload component
│   │   │   ├── SymptomInput.jsx  # Symptom selection
│   │   │   ├── ResultDisplay.jsx # Results display
│   │   │   └── LoadingSpinner.jsx
│   │   └── services/
│   │       └── api.js            # API service layer
│   ├── package.json
│   └── vite.config.js
│
├── notebooks/
│   ├── train_efficientnet.py     # Model training script
│   └── retrain_model.py          # Model retraining script
│
├── README.md                     # This file
└── requirements.txt              # Root dependencies
```

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- npm or yarn
- Git

### Clone the Repository
```bash
git clone https://github.com/khetesh-deore/skin_guard_ml.git
cd skin_guard_ml
```

### Backend Setup

1. **Create and activate virtual environment**
```bash
# Windows
python -m venv venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

2. **Install Python dependencies**
```bash
cd Backend
pip install -r requirements.txt
```

3. **Download/Place the trained model**
```bash
# Place your trained model in Backend/models/skin_model/
# The model should be in TensorFlow SavedModel format or .h5 file
```

4. **Configure environment variables** (optional)
```bash
# Create .env file in Backend/
FLASK_ENV=development
FLASK_DEBUG=1
MODEL_PATH=models/skin_model
MAX_CONTENT_LENGTH=10485760
```

5. **Run the backend server**
```bash
python app.py
# Server runs on http://localhost:5000
```

### Frontend Setup

1. **Install Node.js dependencies**
```bash
cd Frontend
npm install
```

2. **Configure environment variables**
```bash
# Create .env file in Frontend/
VITE_API_URL=http://localhost:5000/api
VITE_MAX_FILE_SIZE_MB=5
```

3. **Run the development server**
```bash
npm run dev
# Frontend runs on http://localhost:5173
```

### Quick Start (Both Services)

**Terminal 1 - Backend:**
```bash
cd Backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd Frontend
npm run dev
```

Open your browser and navigate to `http://localhost:5173`

## 📖 Usage

### Web Interface

1. **Upload Image**: Click or drag-and-drop a skin image (JPG, PNG)
2. **Add Symptoms** (Optional): Select relevant symptoms from the list
3. **Analyze**: Click "Analyze Condition" button
4. **View Results**: Review prediction, severity, and recommendations

### API Usage

```python
import requests

# Predict disease from image
url = "http://localhost:5000/api/predict"
files = {"image": open("skin_image.jpg", "rb")}
data = {"symptoms": "itching,redness,dry_skin"}

response = requests.post(url, files=files, data=data)
result = response.json()

print(f"Disease: {result['prediction']['disease']}")
print(f"Confidence: {result['prediction']['confidence']:.2%}")
print(f"Severity: {result['severity']['level']}")
```

## 📚 API Documentation

### Endpoints

#### POST /api/predict
Main prediction endpoint for skin disease analysis.

**Request:**
```
Content-Type: multipart/form-data

Fields:
- image: file (required) - JPG, JPEG, or PNG image
- symptoms: string (optional) - Comma-separated symptoms
```

**Response:**
```json
{
  "success": true,
  "prediction": {
    "disease": "Eczema",
    "confidence": 0.87,
    "confidence_level": "high",
    "alternative_possibilities": [
      {"disease": "Dermatitis", "confidence": 0.08},
      {"disease": "Psoriasis", "confidence": 0.03}
    ]
  },
  "symptom_analysis": {
    "match_percentage": 85,
    "alignment": "strong",
    "matched_symptoms": ["itching", "redness", "dry_skin"]
  },
  "severity": {
    "level": "moderate",
    "urgency": "consult_doctor",
    "explanation": "Condition shows moderate severity..."
  },
  "recommendations": {
    "general_advice": "...",
    "immediate_care": ["..."],
    "home_remedies": ["..."],
    "precautions": ["..."],
    "when_to_see_doctor": "..."
  },
  "disclaimer": "This is an AI-powered assessment..."
}
```

#### GET /api/health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

#### GET /api/diseases
Get list of supported diseases.

**Response:**
```json
{
  "diseases": ["Acne", "Eczema", ...],
  "count": 22
}
```

#### GET /api/symptoms
Get list of available symptoms.

**Response:**
```json
{
  "symptoms": ["itching", "redness", ...],
  "count": 45
}
```

### Error Responses

```json
{
  "success": false,
  "error": {
    "code": "INVALID_IMAGE",
    "message": "Uploaded file is not a valid image",
    "details": "File type must be jpg, jpeg, or png"
  }
}
```

## 📊 Dataset Information

### Training Dataset
The model was trained on a comprehensive skin disease dataset combining multiple sources:

- **Primary Dataset**: Dermnet (23 classes, ~19,500 images)
- **Supplementary**: HAM10000 dataset for additional samples
- **Image Resolution**: Resized to 224x224 pixels
- **Augmentation**: Rotation, flip, zoom, brightness adjustment

### Data Distribution
```
Total Images: ~19,500
Training Set: 80%
Validation Set: 10%
Test Set: 10%
```

### Class Distribution
| Class | Training Samples |
|-------|-----------------|
| Acne | ~800 |
| Eczema | ~900 |
| Psoriasis | ~850 |
| Skin Cancer | ~750 |
| ... | ... |

## 🧠 Model Training

### Training Script
```bash
cd notebooks
python train_efficientnet.py
```

### Training Parameters
```python
# Model Configuration
BASE_MODEL = "EfficientNetB0"
INPUT_SHAPE = (224, 224, 3)
NUM_CLASSES = 22

# Training Parameters
BATCH_SIZE = 32
EPOCHS = 50
LEARNING_RATE = 0.001
OPTIMIZER = "Adam"

# Data Augmentation
ROTATION_RANGE = 20
ZOOM_RANGE = 0.15
HORIZONTAL_FLIP = True
```

### Retraining with New Data
```bash
python retrain_model.py --data_dir /path/to/new/data --epochs 20
```

## 🧪 Testing

### Backend Tests
```bash
cd Backend

# Run all tests
python -m pytest

# Run specific test files
python test_predictor.py
python test_symptom_matching.py
python test_severity_methods.py
python test_recommendation_engine.py
python test_api_routes.py
```

### Frontend Tests
```bash
cd Frontend

# Run tests
npm test

# Run with coverage
npm run test:coverage
```

### API Integration Test
```bash
cd Backend
python test_api_integration.py
```

## 🔧 Configuration

### Backend Configuration (config.py)
```python
# Model settings
MODEL_PATH = "models/skin_model"
INPUT_SIZE = (224, 224)

# API settings
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

# Rate limiting
RATE_LIMIT_PER_MINUTE = 30
RATE_LIMIT_PER_HOUR = 200
```

### Frontend Configuration (.env)
```env
VITE_API_URL=http://localhost:5000/api
VITE_MAX_FILE_SIZE_MB=5
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Dermnet dataset for training images
- HAM10000 dataset contributors
- TensorFlow and Keras teams
- React and Vite communities

## 📞 Support

For support, please open an issue on GitHub or contact the maintainers.

---

**Remember**: This tool is for educational purposes only. Always consult a healthcare professional for medical advice.
