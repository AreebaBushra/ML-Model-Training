from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.model_loader import get_model_bundle, load_model_bundle
from backend.predictor import predict_calories
from backend.schemas import ErrorResponse, HealthResponse, PredictionRequest, PredictionResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        load_model_bundle()
        logger.info("Application startup complete")
    except Exception as exc:
        logger.exception("Failed to load model on startup: %s", exc)
        raise
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="Calorie Prediction API",
    description="Production API for multivariate linear regression calorie expenditure prediction.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(detail="Internal server error").model_dump(),
    )


@app.get("/", tags=["System"])
async def root() -> dict:
    return {
        "service": "Calorie Prediction API",
        "docs": "/docs",
        "health": "/health",
        "predict": "POST /predict",
        "model_info": "/model-info",
    }


@app.get("/model-info", tags=["System"])
async def model_info() -> dict:
    bundle = get_model_bundle()
    if bundle is None:
        raise HTTPException(status_code=503, detail="Model is not loaded")
    return bundle.metadata


@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    bundle = get_model_bundle()
    return HealthResponse(status="ok", model_loaded=bundle is not None)


@app.post("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict(request: PredictionRequest) -> PredictionResponse:
    bundle = get_model_bundle()
    if bundle is None:
        logger.error("Prediction requested before model was loaded")
        raise HTTPException(status_code=503, detail="Model is not loaded")

    try:
        result = predict_calories(request, bundle)
        logger.info(
            "Prediction success | calories=%.2f | duration=%.1f | hr=%.1f",
            result.predicted_calories,
            request.duration,
            request.heart_rate,
        )
        return result
    except ValueError as exc:
        logger.warning("Validation error during prediction: %s", exc)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Prediction failed: %s", exc)
        raise HTTPException(status_code=500, detail="Prediction failed") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
