import os
from google import genai


def is_strict_genai() -> bool:
    value = os.getenv("STRICT_GENAI", "1").strip().lower()
    return value in {"1", "true", "yes", "on"}


def get_genai_client():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)


def _iter_models(model_list):
    if hasattr(model_list, "page"):
        return model_list.page
    if hasattr(model_list, "models"):
        return model_list.models
    return model_list


def get_gemini_model_name(preferred=None) -> str:
    env_model = os.getenv("GEMINI_MODEL", "").strip()
    if env_model:
        return env_model

    preferred = preferred or [
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-flash-latest",
        "gemini-pro-latest"
    ]

    client = get_genai_client()
    try:
        model_list = client.models.list()
    except Exception as e:
        raise RuntimeError(f"Unable to list Gemini models: {e}")

    candidates = []
    for m in _iter_models(model_list):
        name = getattr(m, "name", "")
        if name.startswith("models/"):
            name = name.replace("models/", "", 1)
        methods = getattr(m, "supported_generation_methods", []) or []
        if not methods or "generateContent" in methods:
            if "gemini" in name:
                candidates.append(name)

    for p in preferred:
        if p in candidates:
            return p

    if candidates:
        return candidates[0]

    raise RuntimeError("No Gemini models available for generateContent. Check API key/project access.")
