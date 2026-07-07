# Calorie Expenditure Prediction

A machine learning project that predicts calories burned during exercise using multivariate linear regression — trained, evaluated, and deployed as a production FastAPI service with a web interface.

**Live app:** https://calories-expenditure-prediction.onrender.com

**Author:** Areeba Bushra

---

## Overview

This project takes a calorie-expenditure dataset through the full pipeline: exploratory analysis, feature encoding, model training and evaluation, then packaging the trained model behind a REST API with a browser-based UI for real-time predictions.

- **Model:** Multivariate Linear Regression, R² = 0.968
- **Backend:** FastAPI, serving predictions via a validated JSON API
- **Frontend:** Static HTML/CSS/JS interface served directly by the API
- **Deployment:** Live on Render, auto-deployed from `main`

---

## Dataset

- Source: [Calorie Expenditure Dataset (Google Drive)](https://drive.google.com/file/d/1tj_WGyspImVxlpzL1KSzu2fzLsTxPKWN/view?usp=sharing)
- 750,000 training rows / 250,000 test rows
- Target column: `Calories`

| Column       | Description |
|--------------|-------------|
| `id`         | Unique identifier for each sample (used for aligning predictions in the submission file). |
| `Sex`        | Biological sex of the individual (`male` / `female`). Affects calorie expenditure due to physiological differences. |
| `Age`        | Age of the individual in years. Influences metabolism and energy consumption. |
| `Height`     | Height in centimeters. Affects BMI and indirectly influences energy needs. |
| `Weight`     | Weight in kilograms. A key factor in energy burned during activity. |
| `Duration`   | Duration of physical activity in minutes. Direct measure of exercise volume. |
| `Heart_Rate` | Heart rate during activity (in beats per minute). Reflects intensity of the physical effort. |
| `Body_Temp`  | Body temperature during activity (°C). Indicates metabolic response to exertion. |
| `Calories`   | **Target variable** — total calories burned during the activity session. |

---

## Model

Trained and evaluated in `calorie_prediction_notebook.ipynb`:

1. Load and explore the data (stats, missing values, boxplots).
2. Encode `Sex` (male = 1, female = 0).
3. Check per-feature correlation with `Calories`.
4. Split into train/validation sets (80/20).
5. Train single-feature regressions to compare individual predictive power.
6. Train the final multivariate linear regression on all features.
7. Visualize Duration vs. Calories and Actual vs. Predicted results.
8. Evaluate with R², RMSE, and MAE.

| Metric | Value |
|--------|-------|
| Algorithm | Multivariate Linear Regression |
| R² Score | 0.9685 |
| RMSE | 11.09 |
| MAE | 8.09 |
| Features | Sex, Age, Height, Weight, Duration, Heart Rate, Body Temperature |

**Key findings:**
- Duration is the strongest single predictor (R² = 0.922 alone).
- Heart Rate and Body Temperature add meaningful extra predictive value.
- Multicollinearity between Duration, Heart Rate, and Body Temp makes individual coefficients hard to interpret directly.
- A handful of predictions came out negative (no domain constraints in linear regression); these are clipped to a minimum of 1.

**Libraries used:** pandas, numpy, matplotlib, seaborn, scikit-learn

---

## Architecture

```
├── backend/                    
│   ├── app.py                  
│   ├── model_loader.py         
│   ├── predictor.py           
│   ├── schemas.py              
│   ├── utils.py
│   ├── model.pkl
│   └── preprocessing.pkl
├── static/
│   └── index.html             
├── scripts/
│   └── export_model.py         
├── calorie_prediction_notebook.ipynb
├── render.yaml                  
└── requirements.txt
```

---

## API

| Method | Path          | Description                              |
|--------|---------------|-------------------------------------------|
| GET    | `/`           | Web UI for entering session data and viewing predictions |
| POST   | `/predict`    | Predict calories burned from input features |
| GET    | `/health`     | Health check + model load status          |
| GET    | `/model-info` | Model metadata and evaluation metrics      |
| GET    | `/api`        | API service info (JSON)                   |
| GET    | `/docs`       | Interactive Swagger documentation          |

**Example request** to `/predict`:
```json
{
  "gender": "male",
  "age": 30,
  "height": 175,
  "weight": 75,
  "duration": 30,
  "heart_rate": 120,
  "body_temp": 39.5
}
```

**Response** includes predicted calories, BMI and category, workout intensity score, personalized suggestions, and equivalent activities.

---

## Running locally

```bash
pip install -r requirements.txt
uvicorn backend.app:app --reload
```
Then open `http://127.0.0.1:8000` in your browser.

---

## Deployment

Deployed on [Render](https://render.com) via `render.yaml` (Infrastructure as Code / Blueprint). Every push to `main` triggers an automatic build and redeploy.

---
