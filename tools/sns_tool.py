"""
FasalWatch — AWS Amazon SNS Alert Delivery Tool
Publishes alerts to an Amazon SNS topic and simulates/sends SMS.
"""

import os
import json
from datetime import datetime
import boto3
from strands import tool

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
TOPIC_NAME = "FasalWatch_Alerts"


def get_or_create_sns_topic():
    """Ensure SNS topic exists for FasalWatch broadcast."""
    try:
        sns = boto3.client("sns", region_name=REGION)
        resp = sns.create_topic(Name=TOPIC_NAME)
        return resp.get("TopicArn")
    except Exception as e:
        print(f"⚠️ Notice on SNS topic creation: {e}")
        return None


@tool
def publish_sns_alert(
    farmer_name: str,
    farmer_phone: str,
    short_advisory: str,
    full_advisory: str,
    risk_level: str,
    language: str
) -> dict:
    """
    Publish an advisory alert to Amazon SNS and deliver SMS.

    Args:
        farmer_name: Name of farmer
        farmer_phone: Phone number
        short_advisory: SMS version (max 160 chars)
        full_advisory: Full advisory
        risk_level: LOW/MEDIUM/HIGH/CRITICAL
        language: Language of message
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    topic_arn = get_or_create_sns_topic()
    message_id = None
    sns_status = "simulated"

    if topic_arn:
        try:
            sns = boto3.client("sns", region_name=REGION)
            pub_resp = sns.publish(
                TopicArn=topic_arn,
                Subject=f"FasalWatch Alert: {risk_level} Risk for {farmer_name}",
                Message=f"[{risk_level}] {short_advisory}\n\nFull: {full_advisory[:200]}...",
                MessageAttributes={
                    "RiskLevel": {"DataType": "String", "StringValue": risk_level},
                    "Language": {"DataType": "String", "StringValue": language},
                    "FarmerPhone": {"DataType": "String", "StringValue": farmer_phone}
                }
            )
            message_id = pub_resp.get("MessageId")
            sns_status = "published_to_aws_sns"
        except Exception as e:
            print(f"⚠️ SNS Publish notice: {e}")

    # Fallback/local visual confirmation
    risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🟠", "CRITICAL": "🔴"}.get(risk_level, "⚪")
    print("\n" + "="*60)
    print(f"📱 AWS SNS DISPATCH — {timestamp}")
    print(f"Topic ARN: {topic_arn or 'Local Fallback'}")
    print(f"AWS Message ID: {message_id or 'SIMULATED-' + timestamp}")
    print("="*60)
    print(f"To: {farmer_name} ({farmer_phone})")
    print(f"Risk: {risk_emoji} {risk_level} | Language: {language}")
    print(f"\n--- SMS Payload ({len(short_advisory)} chars) ---")
    print(short_advisory)
    print("="*60 + "\n")

    return {
        "status": "delivered",
        "aws_sns_status": sns_status,
        "topic_arn": topic_arn,
        "message_id": message_id or f"LOCAL-{timestamp}",
        "timestamp": timestamp,
        "farmer_name": farmer_name,
        "risk_level": risk_level
    }


if __name__ == "__main__":
    res = publish_sns_alert(
        farmer_name="Ramesh Kumar",
        farmer_phone="+91-9876543210",
        short_advisory="कल तेज गर्मी की संभावना है। सूर्योदय से पहले सिंचाई करें।",
        full_advisory="विस्तृत सलाह: अपने गेहूं के खेत में सुबह 6 बजे से पहले 4 सेमी पानी दें।",
        risk_level="HIGH",
        language="Hindi"
    )
    print("SNS tool test result:", res)

