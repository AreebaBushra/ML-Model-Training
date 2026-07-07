from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
from sklearn.linear_model import LinearRegression

logger = logging.getLogger(__name__)

BACKEND_DIR = Path(__file__).resolve().parent
MODEL_PATH = BACKEND_DIR / "model.pkl"
PREPROCESSING_PATH = BACKEND_DIR / "preprocessing.pkl"
METADATA_PATH = BACKEND_DIR / "model_metadata.json"


class ModelBundle:
    def __init__(
        self,
        model: LinearRegression,
        features: List[str],
        sex_encoding: Dict[str, int],
        metadata: Dict[str, Any],
    ) -> None:
        self.model = model
        self.features = features
        self.sex_encoding = sex_encoding
        self.metadata = metadata


_bundle: Optional[ModelBundle] = None


def load_model_bundle() -> ModelBundle:
    global _bundle
    if _bundle is not None:
        return _bundle

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")

    logger.info("Loading model from %s", MODEL_PATH)
    model = joblib.load(MODEL_PATH)
    preprocessing = joblib.load(PREPROCESSING_PATH)
    metadata: Dict[str, Any] = {}
    if METADATA_PATH.exists():
        with open(METADATA_PATH, encoding="utf-8") as file:
            metadata = json.load(file)

    _bundle = ModelBundle(
        model=model,
        features=preprocessing["features"],
        sex_encoding=preprocessing["sex_encoding"],
        metadata=metadata,
    )
    logger.info("Model loaded successfully")
    return _bundle


def get_model_bundle() -> Optional[ModelBundle]:
    return _bundle
