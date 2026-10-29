"""
llm.py - one small wrapper so the rest of the app doesn't care which AI provider you use.

Supported providers (set LLM_PROVIDER in your .env file):
    gemini  -> Google Gemini (has a free API key option: https://aistudio.google.com/apikey)
    claude  -> Anthropic Claude (https://console.anthropic.com)

If no API key is set, is_configured() returns False and the app runs in
"offline mode" (it still finds the best matching passages, it just can't
write a natural-language answer).
"""

import os

from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "gemini").strip().lower()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-haiku-5-5")


def _api_key() -> str:
    if PROVIDER == "claude":
        return os.getenv("ANTHROPIC_API_KEY", "").strip()
    return os.getenv("GEMINI_API_KEY", "").strip()


def is_configured() -> bool:
    """True when an API key for the chosen provider is present."""
    return bool(_api_key())


def provider_label() -> str:
    model = CLAUDE_MODEL if PROVIDER == "claude" else GEMINI_MODEL
    return f"{PROVIDER} ({model})"


def generate(prompt: str, system: str = "", temperature: float = 0.2,
             images: list[bytes] | None = None, max_tokens: int = 4096) -> str:
    """
    Send one prompt to the chosen LLM and return its text reply.
    images - optional list of JPEG bytes (for reading photos / handwritten notes)
    """
    if not is_configured():
        raise RuntimeError(
            "No API key found. Copy .env.example to .env and add your key."
        )

    if PROVIDER == "claude":
        import anthropic

        import base64

        content = [
            {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg",
                                         "data": base64.b64encode(img).decode()}}
            for img in (images or [])
        ] + [{"type": "text", "text": prompt}]
        client = anthropic.Anthropic(api_key=_api_key())
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=max_tokens,
            temperature=temperature,
            system=system or "You are a helpful assistant.",
            messages=[{"role": "user", "content": content}],
        )
        return "".join(
            block.text for block in response.content if block.type == "text"
        ).strip()

    # default: Gemini
    from google import genai
    from google.genai import types

    contents = [types.Part.from_bytes(data=img, mime_type="image/jpeg")
                for img in (images or [])] + [prompt]
    client = genai.Client(api_key=_api_key())
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system or None,
            temperature=temperature,
        ),
    )
    return (response.text or "").strip()


def parse_json(text: str):
    """LLMs sometimes wrap JSON in ```json fences or add extra words. Pull the JSON out."""
    import json
    import re

    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"[\[{].*[\]}]", text, flags=re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                return None
    return None


LANGUAGES = {
    "English": "Reply in simple, clear English.",
    "ಕನ್ನಡ Kannada": (
        "Reply in simple Kannada using Kannada script. Keep technical terms in "
        "English inside brackets, e.g. ತೇವಾಂಶ ಸಂವೇದಕ (moisture sensor)."
    ),
    "Kannada + English mix": (
        "Reply in a friendly mix of Kannada and English (Kanglish) written in "
        "English letters, the way students talk, e.g. 'Hysteresis andre two thresholds use maadodu'."
    ),
}
