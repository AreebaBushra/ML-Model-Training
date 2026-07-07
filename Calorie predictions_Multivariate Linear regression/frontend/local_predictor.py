from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.model_loader import ModelBundle, load_model_bundle
from backend.predictor import predict_calories
from backend.schemas import Gender, PredictionRequest


@st.cache_resource(show_spinner=False)
def get_model_bundle() -> ModelBundle:
    return load_model_bundle()


def is_model_ready() -> tuple[bool, str]:
    try:
        get_model_bundle()
        return True, "Model Loaded • Ready"
    except Exception as exc:
        return False, f"Model Error: {exc}"


def predict_locally(payload: Dict[str, Any]) -> Dict[str, Any]:
    bundle = get_model_bundle()
    request = PredictionRequest(
        gender=Gender(payload["gender"]),
        age=int(payload["age"]),
        height=float(payload["height"]),
        weight=float(payload["weight"]),
        duration=float(payload["duration"]),
        heart_rate=float(payload["heart_rate"]),
        body_temp=float(payload["body_temp"]),
    )
    response = predict_calories(request, bundle)
    return response.model_dump()
