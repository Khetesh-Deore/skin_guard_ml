# SkinGuard ML - Complete Setup Guide

This guide provides step-by-step instructions to set up and run the SkinGuard ML project.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/)
- **pip** - Usually comes with Python

### Verify Installation

```bash
python --version    # Should be 3.9 or higher
node --version      # Should be 16 or higher
npm --version       # Should be 8 or higher
git --version
```

## Step 1: Clone the Repository

```bash
git clone https://github.com/khetesh-deore/skin_guard_ml.git
cd skin_guard_ml
```

## Step 2: Backend Setup

### 2.1 Create Virtual Environment

**Windows (Command Prompt):**
```cmd
cd Backend
python -m venv venv
venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
cd Backend
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
cd Backend
python3 -m venv venv
source venv/bin/activate
```

### 2.2 Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 2.3 Download/Setup the Model

The trained model should be placed in `Backend/models/skin_model/`.

**Option A: Use pre-trained model**
```bash
# If you have a pre-trained model, copy it to:
# Backend/models/skin_model/
```

**Option B: Train your own model**
```bash
cd ../notebooks
python train_efficientnet.py --data_dir /path/to/dataset
```

### 2.4 Configure Environment Variables

Create a `.env` file in the Backend directory:

```bash
# Backend/.env
FLASK_ENV=development
FLASK_DEBUG=1
MODEL_PATH=models/skin_model
MAX_CONTENT_LENGTH=10485760
SECRET_KEY=your-secret-key-here
```

### 2.5 Create Required Directories

```bash
mkdir -p uploads
mkdir -p models/skin_model
```

### 2.6 Run the Backend Server

```bash
python app.py
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Model loaded successfully
 * 22 disease classes available
```

### 2.7 Verify Backend is Running

Open a new terminal and test:

```bash
curl http://localhost:5000/api/health
```

Expected response:
```json
{"status": "healthy", "model_loaded": true, "version": "1.0.0"}
```

## Step 3: Frontend Setup

### 3.1 Navigate to Frontend Directory

```bash
cd ../Frontend
```

### 3.2 Install Node.js Dependencies

```bash
npm install
```

### 3.3 Configure Environment Variables

Create a `.env` file in the Frontend directory:

```bash
# Frontend/.env
VITE_API_URL=http://localhost:5000/api
VITE_MAX_FILE_SIZE_MB=5
```

### 3.4 Run the Frontend Development Server

```bash
npm run dev
```

You should see:
```
  VITE v4.4.5  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3.5 Access the Application

Open your browser and navigate to:
```
http://localhost:5173
```

## Step 4: Running Both Services

### Option A: Two Terminal Windows

**Terminal 1 (Backend):**
```bash
cd Backend
source venv/bin/activate  # or venv\Scripts\activate on Windows
python app.py
```

**Terminal 2 (Frontend):**
```bash
cd Frontend
npm run dev
```

### Option B: Using a Process Manager (Optional)

Install `concurrently` for running both:

```bash
npm install -g concurrently
```

Create a script in the root directory:
```bash
# start.sh (Linux/Mac)
#!/bin/bash
cd Backend && source venv/bin/activate && python app.py &
cd Frontend && npm run dev
```

## Step 5: Testing the Application

### Test Backend API

```bash
cd Backend

# Run all tests
python -m pytest

# Run specific test files
python test_predictor.py
python test_api_routes.py
python test_severity_methods.py
```

### Test Frontend

```bash
cd Frontend
npm run test
```

### Manual API Test

```bash
# Test prediction endpoint with a sample image
curl -X POST http://localhost:5000/api/predict \
  -F "image=@/path/to/skin_image.jpg" \
  -F "symptoms=itching,redness"
```

## Troubleshooting

### Common Issues

#### 1. "Model not loaded" error
- Ensure the model file exists in `Backend/models/skin_model/`
- Check the model format (should be TensorFlow SavedModel or .h5)

#### 2. CORS errors in browser
- Ensure Flask-CORS is installed: `pip install flask-cors`
- Check that CORS is enabled in `app.py`

#### 3. "Module not found" errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

#### 4. Port already in use
- Backend: Change port in `app.py` or kill process on port 5000
- Frontend: Vite will automatically use next available port

#### 5. TensorFlow GPU issues
- For CPU-only: `pip install tensorflow-cpu`
- For GPU: Ensure CUDA and cuDNN are properly installed

### Getting Help

1. Check the [Issues](https://github.com/khetesh-deore/skin_guard_ml/issues) page
2. Review error logs in the terminal
3. Enable debug mode for more detailed errors

## Production Deployment

### Backend (Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Frontend (Build)

```bash
npm run build
# Serve the dist/ folder with nginx or similar
```

### Docker (Optional)

```dockerfile
# Backend Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Quick Reference Commands

| Task | Command |
|------|---------|
| Start Backend | `cd Backend && python app.py` |
| Start Frontend | `cd Frontend && npm run dev` |
| Run Backend Tests | `cd Backend && python -m pytest` |
| Run Frontend Tests | `cd Frontend && npm test` |
| Build Frontend | `cd Frontend && npm run build` |
| Install Backend Deps | `pip install -r requirements.txt` |
| Install Frontend Deps | `npm install` |

## Environment Variables Summary

### Backend (.env)
```
FLASK_ENV=development
FLASK_DEBUG=1
MODEL_PATH=models/skin_model
MAX_CONTENT_LENGTH=10485760
SECRET_KEY=your-secret-key
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:5000/api
VITE_MAX_FILE_SIZE_MB=5
```

---

For more information, see the main [README.md](README.md).
