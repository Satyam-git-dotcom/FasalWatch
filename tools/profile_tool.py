"""
FasalWatch — Farmer Profile Tool
Reads farmer profiles from a local JSON file (swapped for DynamoDB on AWS).
"""

import json
import os
from typing import Any
from strands import tool


PROFILES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "farmer_profiles.json")


def _load_profiles() -> dict:
    with open(PROFILES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@tool
def get_farmer_profile(farmer_id: str) -> dict[str, Any]:
    """
    Retrieve a farmer's profile including their location, crop type, growth stage, and preferred language.

    Args:
        farmer_id: Unique farmer identifier (e.g., 'farmer_001')

    Returns:
        Dictionary with farmer details: name, location, lat/lon, crop, stage, language
    """
    profiles = _load_profiles()
    if farmer_id in profiles:
        return {"status": "found", "farmer": profiles[farmer_id]}
    return {
        "status": "not_found",
        "error": f"No profile found for farmer_id: {farmer_id}",
        "available_ids": list(profiles.keys())
    }


@tool
def list_all_farmers() -> dict[str, Any]:
    """
    List all registered farmer profiles.

    Returns:
        Dictionary with all farmer IDs and their basic info
    """
    profiles = _load_profiles()
    summary = {}
    for fid, fdata in profiles.items():
        summary[fid] = {
            "name": fdata["name"],
            "location": fdata["location"],
            "crop": fdata["crop"],
            "stage": fdata["stage"],
            "language": fdata["language_name"]
        }
    return {"status": "success", "farmers": summary, "total": len(summary)}

