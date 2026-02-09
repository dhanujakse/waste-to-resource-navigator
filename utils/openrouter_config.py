import os
from typing import Optional
from openai import OpenAI


def get_openrouter_client() -> OpenAI:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")

    base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    return OpenAI(base_url=base_url, api_key=api_key)


def get_openrouter_headers() -> dict:
    headers = {}
    app_url = os.getenv("OPENROUTER_APP_URL")
    app_name = os.getenv("OPENROUTER_APP_NAME")
    if app_url:
        headers["HTTP-Referer"] = app_url
    if app_name:
        headers["X-Title"] = app_name
    return headers


def get_openrouter_model_text() -> str:
    return os.getenv("OPENROUTER_MODEL_TEXT", "openai/gpt-4o-mini")


def get_openrouter_model_vision() -> str:
    return os.getenv("OPENROUTER_MODEL_VISION", "openai/gpt-4o-mini")


def get_openrouter_embedding_model() -> Optional[str]:
    value = os.getenv("OPENROUTER_EMBEDDING_MODEL", "").strip()
    return value or None


def is_strict_genai() -> bool:
    value = os.getenv("STRICT_GENAI", "1").strip().lower()
    return value in {"1", "true", "yes", "on"}
