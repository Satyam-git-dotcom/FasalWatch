"""
FasalWatch — Alert Delivery Tool
Simulates SMS/SNS delivery (prints to console; swapped for Amazon SNS on AWS).
"""

import json
from datetime import datetime
from typing import Any
from strands import tool


@tool
def send_alert(
    farmer_name: str,
    farmer_phone: str,
    short_advisory: str,
    full_advisory: str,
    risk_level: str,
    language: str
) -> dict[str, Any]:
    """
    Send an advisory alert to a farmer via SMS (simulated locally, Amazon SNS on AWS).

    Args:
        farmer_name: Name of the farmer receiving the alert
        farmer_phone: Phone number of the farmer
        short_advisory: SMS-length advisory (max 160 characters)
        full_advisory: Full detailed advisory text
        risk_level: Risk level string (LOW, MEDIUM, HIGH, CRITICAL)
        language: Language of the advisory (e.g., 'Hindi', 'English')

    Returns:
        Delivery confirmation with timestamp and message ID
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message_id = f"MSG-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    risk_emoji = {
        "LOW": "🟢",
        "MEDIUM": "🟡",
        "HIGH": "🟠",
        "CRITICAL": "🔴"
    }.get(risk_level, "⚪")

    print("\n" + "="*60)
    print(f"📱 ALERT DELIVERY — {timestamp}")
    print("="*60)
    print(f"To: {farmer_name} ({farmer_phone})")
    print(f"Risk Level: {risk_emoji} {risk_level}")
    print(f"Language: {language}")
    print(f"\n--- SMS Message ({len(short_advisory)} chars) ---")
    print(short_advisory)
    print(f"\n--- Full Advisory ---")
    print(full_advisory)
    print("="*60)

    # Log the alert to a file
    log_entry = {
        "message_id": message_id,
        "timestamp": timestamp,
        "farmer_name": farmer_name,
        "farmer_phone": farmer_phone,
        "risk_level": risk_level,
        "language": language,
        "short_advisory": short_advisory,
        "full_advisory": full_advisory,
        "delivery_status": "simulated_success"
    }

    try:
        import os
        log_dir = os.path.join(os.path.dirname(__file__), "..", "data")
        log_path = os.path.join(log_dir, "alert_log.jsonl")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Don't fail on logging errors

    return {
        "status": "delivered",
        "message_id": message_id,
        "timestamp": timestamp,
        "channel": "SMS (simulated) — Amazon SNS in production",
        "characters": len(short_advisory)
    }

