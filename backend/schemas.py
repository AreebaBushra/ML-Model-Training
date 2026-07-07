from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field, field_validator


class Gender(str, Enum):
    male = "male"
    female = "female"


class PredictionRequest(BaseModel):
    gender: Gender
    age: int = Field(..., ge=10, le=100)
    height: float = Field(..., ge=100.0, le=250.0, description="Height in cm")
    weight: float = Field(..., ge=30.0, le=200.0, description="Weight in kg")
    duration: float = Field(..., ge=1.0, le=300.0, description="Workout duration in minutes")
    heart_rate: float = Field(..., ge=50.0, le=220.0)
    body_temp: float = Field(..., ge=35.0, le=42.0)

    @field_validator("height", "weight", "duration", "heart_rate", "body_temp")
    @classmethod
    def must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Value must be greater than zero")
        return value


class EquivalentActivity(BaseModel):
    activity: str
    duration_minutes: float


class PredictionResponse(BaseModel):
    predicted_calories: float
    bmi: float
    bmi_category: str
    workout_intensity: str
    intensity_score: float
    suggestions: List[str]
    equivalent_activities: List[EquivalentActivity]
    summary: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class ErrorResponse(BaseModel):
    detail: str
