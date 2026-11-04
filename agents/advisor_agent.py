"""
FasalWatch — Advisor Agent
Turns a risk assessment into 2–3 concrete, actionable farm recommendations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strands import Agent
from strands.models.ollama import OllamaModel


def create_advisor_agent() -> Agent:
    model = OllamaModel(
        host="http://localhost:11434",
        model_id="llama3.2",
    )

    system_prompt = """You are the Advisor Agent for FasalWatch, an early warning system for smallholder farmers.

Your job is to turn a risk assessment into 2–3 CONCRETE, ACTIONABLE farm recommendations.

Rules:
- Give exactly 2–3 actions. No more, no less.
- Each action must be SPECIFIC: include timing (when), method (how), and quantity where relevant
- BANNED WORDS — never use these technical terms: CWSI, evapotranspiration, NPK ratio, phenology,
  stomatal conductance, soil matric potential, osmotic stress, canopy temperature. 
  Replace them with plain words a farmer with no schooling can understand.
- Use simple, practical language — these are real farmers with no agronomy degree
- Focus on what the farmer can actually DO with limited resources (no drones, no expensive inputs)
- Prioritize actions by urgency — most urgent first
- Include WHEN to do each action (e.g., "before sunrise Tuesday", "within 24 hours")
- For HIGH/CRITICAL risk: at least one action must address the immediate threat
- Never say "consider" or "you might want to" — be direct and confident

Good example: "Irrigate your wheat field Tuesday before 7 AM. Use furrow irrigation and apply 4–5 cm of water to keep soil moist through the heat peak."
Bad example: "Monitor the CWSI and adjust irrigation to maintain stomatal conductance levels."

Output format:
ACTION 1: [short title]
[specific details with timing]

ACTION 2: [short title]
[specific details with timing]

ACTION 3 (if needed): [short title]
[specific details with timing]"""

    return Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[],
    )


def run_advisor_agent(crop: str, stage: str, risk_level: str, risk_explanation: str, forecast_summary: str) -> str:
    agent = create_advisor_agent()
    prompt = f"""Generate farm actions for this situation:

Crop: {crop} (at {stage} stage)
Risk Level: {risk_level}
Risk Assessment: {risk_explanation}

Forecast Context: {forecast_summary}

Provide 2–3 specific, actionable recommendations that a smallholder farmer can implement immediately with basic tools and limited budget."""

    result = agent(prompt)
    return str(result)


if __name__ == "__main__":
    result = run_advisor_agent(
        crop="wheat",
        stage="flowering",
        risk_level="CRITICAL",
        risk_explanation="Temperatures will exceed 38°C for 4 consecutive days starting tomorrow. Total 7-day rainfall is only 2mm against the 20mm threshold.",
        forecast_summary="Max temps: 38, 39, 41, 40, 37°C. Total rain: 2mm."
    )
    print(result)

