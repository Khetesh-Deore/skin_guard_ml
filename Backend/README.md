# SkinGuard ML - Backend API

Flask-based REST API for skin disease prediction using deep learning.

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
python app.py
```

Server runs at `http://localhost:5000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict` | Analyze skin image |
| GET | `/api/health` | Health check |
| GET | `/api/diseases` | List supported diseases |
| GET | `/api/symptoms` | List available symptoms |

## Project Structure

```
Backend/
├── app.py                 # Flask application
├── config.py              # Configuration
├── requirements.txt       # Dependencies
├── models/
│   └── skin_model/        # TensorFlow model
├── modules/
│   ├── predictor.py       # ML prediction
│   ├── image_processor.py # Image preprocessing
│   ├── symptom_matcher.py # Symptom matching
│   ├── severity_analyzer.py
│   └── recommendation_engine.py
├── routes/
│   └── predict_routes.py  # API routes
└── uploads/               # Temp uploads
```

## Modules

### 1. Predictor (`modules/predictor.py`)
- Loads TensorFlow model
- Processes images through CNN
- Returns top-k predictions with confidence

### 2. Image Processor (`modules/image_processor.py`)
- Validates uploaded images
- Resizes to 224x224
- Normalizes pixel values

### 3. Symptom Matcher (`modules/symptom_matcher.py`)
- Matches user symptoms to disease profiles
- Calculates alignment percentage
- Supports 22 disease classes

### 4. Severity Analyzer (`modules/severity_analyzer.py`)
- Multi-factor severity assessment
- Urgency flag detection
- Red/yellow flag warnings

### 5. Recommendation Engine (`modules/recommendation_engine.py`)
- Disease-specific recommendations
- Severity-based advice
- Safety compliance validation

## Configuration

Create `.env` file:
```env
FLASK_ENV=development
FLASK_DEBUG=1
MODEL_PATH=models/skin_model
MAX_CONTENT_LENGTH=10485760
```

## Testing

```bash
# Run all tests
python -m pytest

# Run specific tests
python test_predictor.py
python test_api_routes.py
python test_severity_methods.py
```

## API Usage Example

```python
import requests

response = requests.post(
    "http://localhost:5000/api/predict",
    files={"image": open("skin.jpg", "rb")},
    data={"symptoms": "itching,redness"}
)

result = response.json()
print(result["prediction"]["disease"])
```

## Supported Diseases (22 Classes)

1. Acne
2. Actinic Keratosis
3. Benign Tumors
4. Bullous
5. Candidiasis
6. Drug Eruption
7. Eczema
8. Infestations/Bites
9. Lichen
10. Lupus
11. Moles
12. Psoriasis
13. Rosacea
14. Seborrheic Keratoses
15. Skin Cancer
16. Sun/Sunlight Damage
17. Tinea
18. Unknown/Normal
19. Vascular Tumors
20. Vasculitis
21. Vitiligo
22. Warts

## Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| MISSING_IMAGE | 400 | No image provided |
| INVALID_FILE_TYPE | 400 | Wrong file format |
| INVALID_IMAGE | 400 | Corrupted image |
| IMAGE_TOO_LARGE | 413 | File > 10MB |
| MODEL_NOT_LOADED | 503 | Model unavailable |
| RATE_LIMIT_EXCEEDED | 429 | Too many requests |

## License

MIT License
