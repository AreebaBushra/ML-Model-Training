from __future__ import annotations

from typing import List, Tuple


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100.0
    return round(weight_kg / (height_m**2), 2)


def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    if bmi < 25:
        return "Normal"
    if bmi < 30:
        return "Overweight"
    return "Obese"


def workout_intensity(heart_rate: float, age: int) -> Tuple[str, float]:
    max_hr = 220 - age
    reserve = max(max_hr - 60, 1)
    intensity_pct = ((heart_rate - 60) / reserve) * 100
    intensity_pct = max(0.0, min(intensity_pct, 100.0))

    if intensity_pct < 50:
        label = "Light"
    elif intensity_pct < 70:
        label = "Moderate"
    elif intensity_pct < 85:
        label = "Vigorous"
    else:
        label = "Maximum"

    return label, round(intensity_pct, 1)


def personalized_suggestions(
    bmi: float,
    intensity: str,
    duration: float,
    predicted_calories: float,
) -> List[str]:
    suggestions: List[str] = []

    if bmi >= 30:
        suggestions.append(
            "Focus on longer moderate sessions (30–45 min) to build endurance safely."
        )
    elif bmi < 18.5:
        suggestions.append(
            "Pair workouts with adequate nutrition to support recovery and energy."
        )
    else:
        suggestions.append(
            "Your BMI is in a healthy range — maintain consistency with 3–5 sessions per week."
        )

    if intensity == "Light":
        suggestions.append(
            "Increase pace or duration gradually to raise heart rate into the moderate zone."
        )
    elif intensity in {"Vigorous", "Maximum"}:
        suggestions.append(
            "Include recovery days and hydration — high-intensity sessions need adequate rest."
        )
    else:
        suggestions.append(
            "Moderate intensity is ideal for fat burning and cardiovascular health."
        )

    if duration < 15:
        suggestions.append("Try extending sessions beyond 20 minutes for greater calorie burn.")
    elif predicted_calories > 200:
        suggestions.append("Excellent session! Log this workout to track progress over time.")

    return suggestions


def equivalent_activities(calories: float) -> List[dict]:
    # Approximate MET-based equivalents (calories for a 70 kg person scaled to prediction)
    activities = [
        ("Walking (brisk)", 4.0),
        ("Cycling (leisure)", 6.0),
        ("Swimming", 7.0),
        ("Running (moderate)", 9.0),
        ("Jump Rope", 11.0),
    ]
    reference_weight = 70.0
    results = []
    for name, met in activities:
        # calories ≈ MET * weight(kg) * hours; solve for minutes at same calories
        hours = calories / (met * reference_weight)
        minutes = round(max(hours * 60, 1), 1)
        results.append({"activity": name, "duration_minutes": minutes})
    return results


def build_summary(
    predicted_calories: float,
    bmi: float,
    intensity: str,
    duration: float,
) -> str:
    return (
        f"You burned approximately {predicted_calories:.0f} kcal in {duration:.0f} minutes "
        f"at {intensity.lower()} intensity. BMI: {bmi:.1f}."
    )
