"""
FasalWatch — AWS Configuration
Central place to switch between LOCAL (Ollama) and AWS (Bedrock) modes.
Change USE_AWS = True once Bedrock access is confirmed.
"""

import os

# ── Toggle here ────────────────────────────────────────────────
USE_AWS = False   # Set to True after Bedrock access is confirmed

# ── AWS Settings ───────────────────────────────────────────────
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
BEDROCK_MODEL_ID = "us.anthropic.claude-3-5-haiku-20241022-v1:0"

# ── Ollama Settings (local fallback) ───────────────────────────
OLLAMA_HOST = "http://localhost:11434"
OLLAMA_ADVISOR_MODEL = "llama3.2"    # Fast agents
OLLAMA_TRANSLATE_MODEL = "gemma4"    # Better Hindi

# ── Translation backend ────────────────────────────────────────
# "aws"   → Amazon Translate (accurate, 75+ languages)
# "llm"   → LLM-based translation (less accurate)
TRANSLATION_BACKEND = "llm"  # switches to "aws" when USE_AWS = True


def get_llm_model(role: str = "general"):
    """
    Returns the appropriate Strands model based on USE_AWS flag.
    role: "general" | "translate"
    """
    if USE_AWS:
        from strands.models.bedrock import BedrockModel
        return BedrockModel(
            model_id=BEDROCK_MODEL_ID,
            region_name=AWS_REGION,
        )
    else:
        from strands.models.ollama import OllamaModel
        model_id = OLLAMA_TRANSLATE_MODEL if role == "translate" else OLLAMA_ADVISOR_MODEL
        return OllamaModel(
            host=OLLAMA_HOST,
            model_id=model_id,
        )


def get_translation_backend():
    """Returns 'aws' or 'llm' based on current config."""
    return "aws" if USE_AWS else TRANSLATION_BACKEND

