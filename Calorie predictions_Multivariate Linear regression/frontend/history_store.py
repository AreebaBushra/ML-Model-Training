from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
HISTORY_PATH = ROOT / "data" / "predictions_history.csv"
SESSION_KEY = "prediction_history_rows"

COLUMNS = [
    "timestamp",
    "gender",
    "age",
    "height",
    "weight",
    "duration",
    "heart_rate",
    "body_temp",
    "predicted_calories",
    "bmi",
    "workout_intensity",
    "intensity_score",
    "summary",
]


def ensure_history_file() -> None:
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not HISTORY_PATH.exists():
        with open(HISTORY_PATH, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()


def _build_row(inputs: Dict[str, Any], result: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "gender": inputs["gender"],
        "age": inputs["age"],
        "height": inputs["height"],
        "weight": inputs["weight"],
        "duration": inputs["duration"],
        "heart_rate": inputs["heart_rate"],
        "body_temp": inputs["body_temp"],
        "predicted_calories": result["predicted_calories"],
        "bmi": result["bmi"],
        "workout_intensity": result["workout_intensity"],
        "intensity_score": result["intensity_score"],
        "summary": result["summary"],
    }


def save_prediction(inputs: Dict[str, Any], result: Dict[str, Any]) -> None:
    row = _build_row(inputs, result)

    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = []
    st.session_state[SESSION_KEY].insert(0, row)

    try:
        ensure_history_file()
        with open(HISTORY_PATH, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writerow(row)
    except OSError:
        pass


def load_history() -> pd.DataFrame:
    session_rows = st.session_state.get(SESSION_KEY, [])
    if session_rows:
        df = pd.DataFrame(session_rows)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp", ascending=False)

    try:
        ensure_history_file()
        df = pd.read_csv(HISTORY_PATH)
        if df.empty:
            return df
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df.sort_values("timestamp", ascending=False)
    except (OSError, pd.errors.EmptyDataError):
        return pd.DataFrame(columns=COLUMNS)


def delete_history() -> None:
    st.session_state[SESSION_KEY] = []
    try:
        ensure_history_file()
        with open(HISTORY_PATH, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=COLUMNS)
            writer.writeheader()
    except OSError:
        pass


def history_stats(df: pd.DataFrame) -> Dict[str, Any]:
    if df.empty:
        return {
            "total_predictions": 0,
            "avg_calories": 0.0,
            "avg_duration": 0.0,
            "avg_bmi": 0.0,
        }
    return {
        "total_predictions": len(df),
        "avg_calories": round(df["predicted_calories"].mean(), 1),
        "avg_duration": round(df["duration"].mean(), 1),
        "avg_bmi": round(df["bmi"].mean(), 1),
    }
