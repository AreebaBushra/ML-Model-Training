# Calorie Expenditure Prediction API

Production FastAPI service for predicting calories burned during exercise using multivariate linear regression.

**Author:** Areeba Bushra

## Model

| Metric | Value |
|--------|-------|
| Algorithm | Multivariate Linear Regression |
| R² Score | 0.9685 |
| RMSE | 11.09 |
| MAE | 8.09 |
| Features | Gender, Age, Height, Weight, Duration, Heart Rate, Body Temperature |

Gender encoding: `male = 1`, `female = 0` (no scaling — matches the training notebook).

## Project structure

```
Calorie predictions_Multivariate Linear regression/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── model_loader.py     # Loads model.pkl at startup
│   ├── predictor.py        # Prediction logic (notebook-identical)
│   ├── schemas.py          # Pydantic request/response models
│   ├── utils.py            # BMI, intensity, suggestions
│   ├── model.pkl           # Trained model
│   ├── preprocessing.pkl   # Feature order + sex encoding
│   └── model_metadata.json # Model metrics
├── scripts/
│   └── export_model.py     # Re-export model from CSV (optional)
├── calorie_prediction_notebook.ipynb
├── requirements.txt
├── runtime.txt
└── README.md
```

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service info |
| GET | `/health` | Health check |
| GET | `/model-info` | Model metrics and feature list |
| POST | `/predict` | Predict calories burned |
| GET | `/docs` | Interactive Swagger UI |

### Example prediction request

```bash
curl -X POST https://YOUR-RENDER-URL.onrender.com/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "male",
    "age": 36,
    "height": 189.0,
    "weight": 82.0,
    "duration": 26.0,
    "heart_rate": 101.0,
    "body_temp": 41.0
  }'
```

## Run locally

```bash
cd "Calorie predictions_Multivariate Linear regression"
pip install -r requirements.txt
uvicorn backend.app:app --reload --host 127.0.0.1 --port 8000
```

Open **http://127.0.0.1:8000/docs** to test the API.

## Deploy on Render

### Option A — Blueprint (recommended)

1. Push this repo to GitHub: [AreebaBushra/ML-Model-Training](https://github.com/AreebaBushra/ML-Model-Training)
2. Log in to [dashboard.render.com](https://dashboard.render.com)
3. Click **New +** → **Blueprint**
4. Connect your GitHub account and select repository **ML-Model-Training**
5. Render detects `render.yaml` at the repo root and creates the **calorie-prediction-api** web service
6. Click **Apply** and wait for the deploy to finish (~3–5 minutes on free tier)

Your API will be live at: `https://calorie-prediction-api.onrender.com` (or similar)

### Option B — Manual web service

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New +** → **Web Service**
2. Connect **AreebaBushra/ML-Model-Training**
3. Configure:

| Setting | Value |
|---------|-------|
| **Name** | `calorie-prediction-api` |
| **Root Directory** | `Calorie predictions_Multivariate Linear regression` |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn backend.app:app --host 0.0.0.0 --port $PORT` |
| **Health Check Path** | `/health` |

4. Click **Create Web Service**

### After deploy

- Test health: `https://YOUR-URL.onrender.com/health`
- API docs: `https://YOUR-URL.onrender.com/docs`
- Model info: `https://YOUR-URL.onrender.com/model-info`

> **Note:** On Render's free tier, the service sleeps after inactivity. The first request may take 30–60 seconds to wake up.

## Re-export model (optional)

If you have the training CSV locally:

```bash
python scripts/export_model.py
```

This regenerates `backend/model.pkl` using the exact notebook pipeline (`random_state=3`, 80/20 split).

## Original notebook

See `calorie_prediction_notebook.ipynb` for the full ML training workflow (Colab / exploratory analysis).
