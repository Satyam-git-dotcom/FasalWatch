"""
FasalWatch — Weather Tool
Fetches 7-day forecast from Open-Meteo (free, no API key required).
"""

import requests
from typing import Any
from strands import tool


@tool
def get_weather_forecast(latitude: float, longitude: float, location_name: str = "the farm") -> dict[str, Any]:
    """
    Fetch a 7-day hourly weather forecast for a given location using the Open-Meteo API.
    Returns temperature, precipitation, humidity, and wind speed data.

    Args:
        latitude: Latitude of the farm location (decimal degrees)
        longitude: Longitude of the farm location (decimal degrees)
        location_name: Human-readable name of the location (for display purposes)

    Returns:
        Dictionary containing forecast data with daily summaries and raw hourly data
    """
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m,precipitation,relative_humidity_2m,wind_speed_10m",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "forecast_days": 7,
        "timezone": "auto",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Build clean daily summary
        daily = data.get("daily", {})
        dates = daily.get("time", [])
        max_temps = daily.get("temperature_2m_max", [])
        min_temps = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind = daily.get("wind_speed_10m_max", [])

        daily_summary = []
        for i, date in enumerate(dates):
            daily_summary.append({
                "date": date,
                "max_temp_c": max_temps[i] if i < len(max_temps) else None,
                "min_temp_c": min_temps[i] if i < len(min_temps) else None,
                "precipitation_mm": precip[i] if i < len(precip) else None,
                "max_wind_kmh": wind[i] if i < len(wind) else None,
            })

        total_rain_7day = sum(p for p in precip if p is not None)
        days_above_35 = sum(1 for t in max_temps if t is not None and t >= 35)
        days_above_38 = sum(1 for t in max_temps if t is not None and t >= 38)
        max_temp_week = max((t for t in max_temps if t is not None), default=0)

        return {
            "location": location_name,
            "latitude": latitude,
            "longitude": longitude,
            "timezone": data.get("timezone", "unknown"),
            "forecast_days": daily_summary,
            "summary": {
                "total_rainfall_7day_mm": round(total_rain_7day, 1),
                "max_temperature_7day_c": max_temp_week,
                "days_above_35c": days_above_35,
                "days_above_38c": days_above_38,
            },
            "status": "success"
        }

    except requests.exceptions.ConnectionError:
        return {
            "status": "error",
            "error": "Could not connect to weather service. Check internet connection.",
            "location": location_name
        }
    except requests.exceptions.Timeout:
        return {
            "status": "error",
            "error": "Weather service timed out. Try again.",
            "location": location_name
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "location": location_name
        }

