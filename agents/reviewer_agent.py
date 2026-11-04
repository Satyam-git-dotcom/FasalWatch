"""
FasalWatch — Reviewer Agent
Quality-gates the advisory before delivery:
- Checks for contradictions between actions
- Flags overconfident or alarming language
- Verifies the SMS is within 160 characters
- Approves or sends back for revision
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from strands import Agent
from strands.models.ollama import OllamaModel


def create_reviewer_agent() -> Agent:
    model = OllamaModel(
        host="http://localhost:11434",
        model_id="llama3.2",
    )

    system_prompt = """You are the Reviewer Agent for FasalWatch. You are the final quality gate before an advisory is sent to a farmer.

Your job is to check the advisory and either APPROVE it or REQUEST REVISION.

Check for these issues:
1. CONTRADICTIONS: Do any actions contradict each other? (e.g., "irrigate more" and "reduce water" in the same advisory)
2. OVERCONFIDENCE: Does the advisory make promises it cannot keep? (e.g., "this will definitely save your crop")
3. ALARM: Is the tone unnecessarily scary? Farm advisories should be urgent but calm.
4. SMS LENGTH: Is the SMS version within 160 characters? Count carefully.
5. ACTIONABILITY: Are all actions specific enough for a farmer to follow immediately?
6. MISSING URGENCY: For HIGH/CRITICAL risk, is there at least one action to take TODAY or TOMORROW?

Output format (use EXACTLY these headers):
REVIEW_RESULT: [APPROVED / REVISION_NEEDED]

ISSUES_FOUND:
[List any issues, or write "None" if approved]

SUGGESTED_FIXES:
[List specific fixes for each issue, or write "None" if approved]

FINAL_VERDICT:
[One sentence summary explaining your decision]"""

    return Agent(
        model=model,
        system_prompt=system_prompt,
        tools=[],
    )


def run_reviewer_agent(
    risk_level: str,
    english_actions: str,
    sms_version: str,
    full_version: str,
    back_translation: str
) -> dict:
    agent = create_reviewer_agent()

    sms_char_count = len(sms_version)

    prompt = f"""Review this farm advisory before it is sent to a farmer:

Risk Level: {risk_level}

Original English Actions:
{english_actions}

SMS Version ({sms_char_count} characters):
{sms_version}

Full Localized Advisory:
{full_version}

English Back-Translation (for accuracy check):
{back_translation}

Check for: contradictions, overconfidence, unnecessary alarm, SMS length (must be ≤ 160 chars), 
actionability, and appropriate urgency for the risk level. Then give your REVIEW_RESULT."""

    result = agent(prompt)
    result_text = str(result)

    # Parse result
    approved = "APPROVED" in result_text.upper() and "REVISION_NEEDED" not in result_text.upper()

    return {
        "approved": approved,
        "review_result": "APPROVED" if approved else "REVISION_NEEDED",
        "sms_char_count": sms_char_count,
        "sms_within_limit": sms_char_count <= 160,
        "raw_review": result_text
    }


if __name__ == "__main__":
    result = run_reviewer_agent(
        risk_level="CRITICAL",
        english_actions="ACTION 1: Irrigate before 7 AM Tuesday\nACTION 2: Apply mulch today",
        sms_version="Jaipur wheat alert: Heat 41°C next 4 days. Water before 7AM Tue+Wed. Add mulch today. Save crop!",
        full_version="आपके गेहूं के खेत में खतरा है। अगले 4 दिन बहुत गर्म रहेंगे।",
        back_translation="Your wheat field is in danger. The next 4 days will be very hot."
    )
    print("Approved:", result["approved"])
    print("Review:", result["raw_review"])

