"""Shared Gemini API client: one place for key lookup, model name and HTTP call."""

import json
import logging
import re
from typing import Any, Dict, Optional

import httpx

from app import config

logger = logging.getLogger(__name__)

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"


def resolve_gemini_key(custom_api_key: Optional[str] = None) -> str:
    """Key priority: explicit key from the request > .env / environment > key saved from the UI."""
    key = (custom_api_key or "").strip()
    if key:
        return key
    if config.GEMINI_API_KEY:
        return config.GEMINI_API_KEY
    try:
        from app.notifications.notifier import AlertNotifier
        return (AlertNotifier().get_config().get("gemini_api_key") or "").strip()
    except Exception:
        return ""


def model_label() -> str:
    return config.GEMINI_MODEL


def generate_json(prompt: str, api_key: str, timeout: float = 25.0, temperature: float = 0.4) -> Optional[Dict[str, Any]]:
    """Calls Gemini and parses the response as JSON. Returns None on any failure.

    The key is sent in the x-goog-api-key header rather than the URL so it never
    ends up in access logs or exception messages.
    """
    if not api_key:
        return None
    url = f"{GEMINI_BASE_URL}/{config.GEMINI_MODEL}:generateContent"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "response_mime_type": "application/json"},
    }
    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(url, json=payload, headers={"x-goog-api-key": api_key})
        if resp.status_code != 200:
            logger.error("Gemini API (%s) returned %s: %s", config.GEMINI_MODEL, resp.status_code, resp.text[:500])
            return None
        text = resp.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-z]*\n", "", text)
            text = re.sub(r"\n```$", "", text)
        return json.loads(text)
    except Exception as e:
        logger.warning("Gemini call failed: %s", type(e).__name__)
        return None
