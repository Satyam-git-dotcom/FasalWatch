"""
FasalWatch — Risk Agent
Provides a human-readable explanation of the risk level.
NOTE: The actual risk level is calculated deterministically by risk_calculator.py.
      This agent only writes the natural language explanation — no hallucinations possible.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strands import Agent
from strands.models.ollama import OllamaModel
from tools.crop_tool import get_crop_thresholds


def create_risk_agent() -> Agent:
    model = OllamaModel(
        host="http://localhost:11434",
        model_id="llama3.2",
    )

    system_prompt = """You are the Risk Agent for FasalWatch, an early warning system for smallholder farmers.

The risk level has already been calculated by a precise Python algorithm. Your ONLY job is to:
1. Call get_crop_thresholds to look up the danger limits for the crop and stage
2. Write a clear, factual explanation of WHY the given risk level applies
3. Name the specific dates, temperatures, and thresholds in your explanation
4. Keep it under 100 words — farmers and advisors need quick clarity

DO NOT recalculate or override the provided risk level. Just explain it clearly."""

    return Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[get_crop_thresholds],
    )


def run_risk_agent(crop: str, stage: str, forecast_summary: str,
                   forced_risk_level: str = None, calc_details: dict = None) -> str:
    agent = create_risk_agent()

    calc_context = ""
    if calc_details:
        calc_context = f"""
Python Risk Calculator Results (USE THESE — do not recalculate):
  - Risk Level: {forced_risk_level}
  - Peak temperature: {calc_details.get('peak_temp_c')}°C (threshold: {calc_details.get('heat_threshold_c')}°C)
  - Consecutive heat days: {calc_details.get('max_consecutive_heat_days')} (needed: {calc_details.get('heat_days_needed')})
  - Heat threshold triggered: {calc_details.get('heat_triggered')}
  - Total 7-day rain: {calc_details.get('total_rain_mm')}mm (threshold: {calc_details.get('drought_threshold_mm')}mm)
  - Drought threshold triggered: {calc_details.get('drought_triggered')}
"""

    prompt = f"""Explain the risk assessment for this farm situation:

Crop: {crop}
Growth Stage: {stage}
{calc_context}
Weather Forecast:
{forecast_summary}

Steps:
1. Call get_crop_thresholds for {crop} at {stage} stage
2. Write a brief explanation (under 100 words) of why the risk level is {forced_risk_level or 'as calculated'}
3. Be specific about which thresholds were exceeded and on which dates
4. End with: RISK_LEVEL: {forced_risk_level or '[calculated level]'}"""

    result = agent(prompt)
    return str(result)


if __name__ == "__main__":
    from tools.risk_calculator import calculate_risk
    sample_days = [
        {"max_temp_c": 41.2, "precipitation_mm": 0},
        {"max_temp_c": 41.5, "precipitation_mm": 0},
        {"max_temp_c": 42.2, "precipitation_mm": 0},
        {"max_temp_c": 43.0, "precipitation_mm": 0},
        {"max_temp_c": 41.8, "precipitation_mm": 0},
        {"max_temp_c": 40.5, "precipitation_mm": 0},
        {"max_temp_c": 42.3, "precipitation_mm": 0},
    ]
    calc = calculate_risk("wheat", "grain_fill", sample_days, 0.0)
    print("Python says:", calc["risk_level"])
    result = run_risk_agent("wheat", "grain_fill", "43°C for 7 days, 0mm rain",
                            forced_risk_level=calc["risk_level"], calc_details=calc)
    print(result)
