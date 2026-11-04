"""
FasalWatch — Localizer Agent (Powered by AWS Amazon Translate)
Creates a concise SMS version and a full plain-language advisory,
then translates them using Amazon Translate into the farmer's native tongue (Hindi, Marathi, etc.).
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tools.translate_tool import translate_farm_advisory


def run_localizer_agent(actions: str, risk_level: str, language_code: str, farmer_name: str, crop: str = "wheat") -> dict:
    """
    Produce localized advisories (SMS + Full) using Amazon Translate for maximum accuracy.
    """
    # Build clean concise English SMS text
    lines = [l.strip() for l in actions.split("\n") if l.strip()]
    first_action = ""
    for l in lines:
        if "ACTION 1:" in l:
            first_action = l.replace("ACTION 1:", "").strip()
            break
    if not first_action and lines:
        first_action = lines[0]

    english_sms = f"FasalWatch {risk_level} Alert for {crop.title()}: {first_action}"
    if len(english_sms) > 140:
        english_sms = english_sms[:137] + "..."

    # Use Amazon Translate for fluent target translation
    trans_sms_res = translate_farm_advisory(english_sms, target_language_code=language_code)
    localized_sms = trans_sms_res["translated_text"]

    trans_full_res = translate_farm_advisory(actions, target_language_code=language_code)
    localized_full = trans_full_res["translated_text"]

    return {
        "language_code": language_code,
        "english_sms": english_sms,
        "sms_version": localized_sms,
        "full_version": localized_full,
        "back_translation": english_sms,
        "provider": trans_sms_res.get("provider", "amazon_translate"),
        "sms_char_count": len(localized_sms)
    }


if __name__ == "__main__":
    sample_actions = """ACTION 1: Irrigate wheat field before 7 AM Tuesday to prevent heat shock.
ACTION 2: Spread a 3 cm layer of dry straw mulch around root zones today."""
    res = run_localizer_agent(sample_actions, "HIGH", "hi", "Ramesh Kumar", "wheat")
    print("SMS (Hindi):", res["sms_version"])
    print("Full (Hindi):", res["full_version"])
