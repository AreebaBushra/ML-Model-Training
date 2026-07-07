from __future__ import annotations

import logging

import pandas as pd

from backend.model_loader import ModelBundle
from backend.schemas import EquivalentActivity, PredictionRequest, PredictionResponse
from backend.utils import (
    bmi_category,
    build_summary,
    calculate_bmi,
    equivalent_activities,
    personalized_suggestions,
    workout_intensity,
)

logger = logging.getLogger(__name__)


def encode_gender(gender: str, sex_encoding: dict) -> int:
    return int(sex_encoding[gender])


def build_feature_row(request: PredictionRequest, bundle: ModelBundle) -> pd.DataFrame:
    sex_enc = encode_gender(request.gender.value, bundle.sex_encoding)
    row = {
        "Sex_enc": sex_enc,
        "Age": request.age,
        "Height": request.height,
        "Weight": request.weight,
        "Duration": request.duration,
        "Heart_Rate": request.heart_rate,
        "Body_Temp": request.body_temp,
    }
    return pd.DataFrame([row])[bundle.features]


def predict_calories(request: PredictionRequest, bundle: ModelBundle) -> PredictionResponse:
    features = build_feature_row(request, bundle)
    raw_prediction = float(bundle.model.predict(features)[0])

    # Notebook note: negative predictions clipped to 1
    predicted_calories = max(round(raw_prediction, 2), 1.0)
    if raw_prediction < 0:
        logger.warning("Negative prediction clipped: raw=%.2f", raw_prediction)

    bmi = calculate_bmi(request.weight, request.height)
    category = bmi_category(bmi)
    intensity, intensity_score = workout_intensity(request.heart_rate, request.age)
    suggestions = personalized_suggestions(bmi, intensity, request.duration, predicted_calories)
    equivalents = [
        EquivalentActivity(**item) for item in equivalent_activities(predicted_calories)
    ]
    summary = build_summary(predicted_calories, bmi, intensity, request.duration)

    return PredictionResponse(
        predicted_calories=predicted_calories,
        bmi=bmi,
        bmi_category=category,
        workout_intensity=intensity,
        intensity_score=intensity_score,
        suggestions=suggestions,
        equivalent_activities=equivalents,
        summary=summary,
    )
