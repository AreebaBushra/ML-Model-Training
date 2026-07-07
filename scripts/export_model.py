"""One-time export of the notebook-trained Linear Regression model to backend artifacts."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "Calorie Expenditure.csv"
BACKEND_DIR = ROOT / "backend"

FEATURES = [
    "Sex_enc",
    "Age",
    "Height",
    "Weight",
    "Duration",
    "Heart_Rate",
    "Body_Temp",
]


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    df["Sex_enc"] = (df["Sex"] == "male").astype(int)

    x = df[FEATURES]
    y = df["Calories"]
    x_train, x_test, y_train, y_test = train_test_split(
        x, y, test_size=0.2, random_state=3
    )

    model = LinearRegression()
    model.fit(x_train, y_train)
    predictions = model.predict(x_test)

    metadata = {
        "algorithm": "Multivariate Linear Regression",
        "features": [
            "Gender (Sex_enc)",
            "Age",
            "Height",
            "Weight",
            "Duration",
            "Heart_Rate",
            "Body_Temp",
        ],
        "feature_order": FEATURES,
        "dataset": "Calorie Expenditure (750,000 training rows)",
        "train_test_split": {"test_size": 0.2, "random_state": 3},
        "sex_encoding": {"male": 1, "female": 0},
        "metrics": {
            "r2_score": float(r2_score(y_test, predictions)),
            "rmse": float(mean_squared_error(y_test, predictions) ** 0.5),
            "mae": float(mean_absolute_error(y_test, predictions)),
        },
        "author": "Areeba Bushra",
    }

    BACKEND_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, BACKEND_DIR / "model.pkl")
    joblib.dump(
        {"features": FEATURES, "sex_encoding": metadata["sex_encoding"]},
        BACKEND_DIR / "preprocessing.pkl",
    )
    with open(BACKEND_DIR / "model_metadata.json", "w", encoding="utf-8") as file:
        json.dump(metadata, file, indent=2)

    print("Model exported to backend/model.pkl")
    print(f"R²: {metadata['metrics']['r2_score']:.4f}")
    print(f"RMSE: {metadata['metrics']['rmse']:.4f}")
    print(f"MAE: {metadata['metrics']['mae']:.4f}")


if __name__ == "__main__":
    main()
