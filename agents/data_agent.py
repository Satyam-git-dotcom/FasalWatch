"""
FasalWatch — Data Agent
Fetches weather forecast data for a farmer's location using Open-Meteo API.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strands import Agent
from strands.models.ollama import OllamaModel
from tools.weather_tool import get_weather_forecast
from tools.profile_tool import get_farmer_profile


def create_data_agent() -> Agent:
    model = OllamaModel(
        host="http://localhost:11434",
        model_id="llama3.2",
    )

    system_prompt = """You are the Data Agent for FasalWatch, an early warning system for smallholder farmers.

Your ONLY job is to:
1. Retrieve the farmer's profile using get_farmer_profile
2. Fetch a 7-day weather forecast for the farmer's location using get_weather_forecast
3. Return a clean structured summary of the forecast data

Always call the tools. Do not guess or fabricate weather data. 
Return the raw forecast data as-is so the Risk Agent can analyze it.
Keep your response focused and factual — no recommendations, just data."""

    return Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[get_farmer_profile, get_weather_forecast],
    )


def run_data_agent(farmer_id: str) -> str:
    agent = create_data_agent()
    prompt = f"""Retrieve the profile for farmer ID '{farmer_id}', then fetch a 7-day weather forecast 
for their farm location. Return all the forecast data including daily max temperatures, 
minimum temperatures, precipitation amounts, and the 7-day summary statistics."""
    result = agent(prompt)
    return str(result)


if __name__ == "__main__":
    result = run_data_agent("farmer_001")
    print(result)

