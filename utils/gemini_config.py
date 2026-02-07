import os
import google.generativeai as genai


def is_strict_genai() -> bool:
    value = os.getenv("STRICT_GENAI", "1").strip().lower()
    return value in {"1", "true", "yes", "on"}


def get_gemini_model_name(preferred=None) -> str:
    env_model = os.getenv("GEMINI_MODEL", "").strip()
    if env_model:
        return env_model

    preferred = preferred or [
        "gemini-1.5-flash-002",
        "gemini-1.5-flash-001",
        "gemini-1.5-pro-002",
        "gemini-1.5-pro-001",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "gemini-2.0-flash"
    ]

    try:
        models = genai.list_models()
    except Exception as e:
        raise RuntimeError(f"Unable to list Gemini models: {e}")

    candidates = []
    for m in models:
        name = getattr(m, "name", "")
        if name.startswith("models/"):
            name = name.replace("models/", "", 1)
        methods = getattr(m, "supported_generation_methods", []) or []
        if "generateContent" in methods and "gemini" in name:
            candidates.append(name)

    for p in preferred:
        if p in candidates:
            return p

    if candidates:
        return candidates[0]

    raise RuntimeError("No Gemini models available for generateContent. Check API key/project access.")
