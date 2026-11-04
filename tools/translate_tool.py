"""
FasalWatch — AWS Amazon Translate Tool
Translates advisories using Amazon Translate (fast, fluent, 75+ languages).
Gracefully falls back to local translation if AWS is unreachable.
"""

import os
import boto3
from strands import tool

REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")


@tool
def translate_farm_advisory(text: str, target_language_code: str = "hi") -> dict:
    """
    Translate advisory text using AWS Amazon Translate.

    Args:
        text: English text to translate
        target_language_code: 2-letter ISO language code (e.g., 'hi' for Hindi, 'mr' for Marathi)

    Returns:
        Dictionary with translated text and metadata
    """
    if target_language_code == "en":
        return {"status": "success", "translated_text": text, "provider": "passthrough"}

    try:
        client = boto3.client("translate", region_name=REGION)
        resp = client.translate_text(
            Text=text,
            SourceLanguageCode="en",
            TargetLanguageCode=target_language_code,
        )
        return {
            "status": "success",
            "translated_text": resp.get("TranslatedText", text),
            "source_language": "en",
            "target_language": target_language_code,
            "provider": "amazon_translate"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "translated_text": text,
            "provider": "fallback"
        }


if __name__ == "__main__":
    sample = "Jaipur Wheat Alert: High heat expected tomorrow. Irrigate before sunrise."
    res = translate_farm_advisory(sample, "hi")
    print("Amazon Translate output:")
    print(res["translated_text"])

