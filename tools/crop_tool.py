"""
FasalWatch — Crop Threshold Tool
Loads crop-stage heat and drought thresholds from data/crop_thresholds.json.
"""

import json
import os
from typing import Any
from strands import tool


THRESHOLDS_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "crop_thresholds.json")


def _load_thresholds() -> dict:
    with open(THRESHOLDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@tool
def get_crop_thresholds(crop: str, stage: str) -> dict[str, Any]:
    """
    Get the heat and drought stress thresholds for a specific crop at a specific growth stage.

    Args:
        crop: Crop name (e.g., 'wheat', 'rice', 'maize', 'cotton')
        stage: Growth stage (e.g., 'flowering', 'grain_fill', 'transplanting', 'tasseling')

    Returns:
        Dictionary with heat_stress_temp_c, heat_stress_consecutive_days,
        drought_rain_7day_mm, and a description of the stage sensitivity
    """
    thresholds = _load_thresholds()
    crop_lower = crop.lower().strip()
    stage_lower = stage.lower().strip().replace(" ", "_")

    if crop_lower not in thresholds:
        available = list(thresholds.keys())
        return {
            "status": "not_found",
            "error": f"Crop '{crop}' not in database. Available crops: {available}"
        }

    crop_data = thresholds[crop_lower]
    if stage_lower not in crop_data:
        available_stages = list(crop_data.keys())
        return {
            "status": "not_found",
            "error": f"Stage '{stage}' not found for {crop}. Available stages: {available_stages}"
        }

    threshold = crop_data[stage_lower]
    return {
        "status": "found",
        "crop": crop_lower,
        "stage": stage_lower,
        "thresholds": threshold
    }

