"""
FasalWatch — Risk Calculator (Deterministic Python)
Calculates risk level by directly comparing weather data against crop thresholds.
This is deterministic — no LLM involved, no hallucinations possible.
The Risk Agent LLM then writes a human-readable explanation of the Python result.
"""

import json
import os

THRESHOLDS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crop_thresholds.json")


def calculate_risk(crop: str, stage: str, forecast_days: list, total_rain_mm: float) -> dict:
    """
    Deterministically calculate risk level by comparing forecast vs thresholds.

    Args:
        crop: Crop name (e.g., 'wheat')
        stage: Growth stage (e.g., 'grain_fill')
        forecast_days: List of dicts with 'max_temp_c' and 'precipitation_mm'
        total_rain_mm: Total 7-day rainfall in mm

    Returns:
        dict with risk_level, heat_triggered, drought_triggered, details
    """
    with open(THRESHOLDS_PATH) as f:
        thresholds = json.load(f)

    crop_lower = crop.lower()
    stage_lower = stage.lower().replace(" ", "_")

    if crop_lower not in thresholds or stage_lower not in thresholds[crop_lower]:
        return {"risk_level": "MEDIUM", "error": "Crop/stage not found in thresholds"}

    t = thresholds[crop_lower][stage_lower]
    heat_temp = t["heat_stress_temp_c"]
    heat_days_needed = t["heat_stress_consecutive_days"]
    drought_rain_limit = t["drought_rain_7day_mm"]

    # Count days above heat threshold
    max_temps = [d.get("max_temp_c", 0) for d in forecast_days if d.get("max_temp_c") is not None]
    days_above = [temp >= heat_temp for temp in max_temps]
    total_days_above = sum(days_above)

    # Find maximum consecutive days above threshold
    max_consecutive = 0
    current_streak = 0
    for above in days_above:
        if above:
            current_streak += 1
            max_consecutive = max(max_consecutive, current_streak)
        else:
            current_streak = 0

    heat_triggered = max_consecutive >= heat_days_needed
    drought_triggered = total_rain_mm < drought_rain_limit

    # Determine risk level
    if heat_triggered and drought_triggered:
        risk_level = "CRITICAL"
    elif heat_triggered or (drought_triggered and total_days_above >= heat_days_needed):
        risk_level = "HIGH"
    elif drought_triggered or total_days_above > 0:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    return {
        "risk_level": risk_level,
        "heat_triggered": heat_triggered,
        "drought_triggered": drought_triggered,
        "max_consecutive_heat_days": max_consecutive,
        "heat_days_needed": heat_days_needed,
        "heat_threshold_c": heat_temp,
        "total_days_above_threshold": total_days_above,
        "total_rain_mm": total_rain_mm,
        "drought_threshold_mm": drought_rain_limit,
        "peak_temp_c": max(max_temps) if max_temps else 0,
    }

