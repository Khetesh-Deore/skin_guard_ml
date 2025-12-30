---
title: SkinGuard ML API
emoji: 🏥
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# SkinGuard ML Backend API

Flask API for skin disease prediction using TensorFlow.

## Endpoints

- `GET /api/health` - Health check
- `POST /api/predict` - Predict skin condition from image
- `GET /api/diseases` - List supported diseases
- `GET /api/symptoms` - List available symptoms
