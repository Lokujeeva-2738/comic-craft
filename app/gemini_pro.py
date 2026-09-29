import json

from google import genai
from google.genai import types

from .config import (
    GEMINI_API_KEY,
    GEMINI_PRO_MODEL,
)

from .schemas import ComicOutline


# =========================================================
# Gemini client
# =========================================================

def get_client():

    if not GEMINI_API_KEY:

        raise RuntimeError(
            "GEMINI_API_KEY is missing."
        )

    return genai.Client(
        api_key=GEMINI_API_KEY
    )


# =========================================================
# Improve an existing outline
# =========================================================

def polish_outline(
    outline: ComicOutline
) -> ComicOutline:

    client = get_client()

    prompt = f"""
You are a professional comic story editor.

Improve the following ComicCraft outline.

Improve:

- story clarity
- pacing
- character consistency
- visual continuity
- dialogue
- scene descriptions
- image prompts
- panel-to-panel storytelling

IMPORTANT:

- Keep exactly five panels.
- Do not change the central story.
- Do not add extra panels.
- Keep the characters consistent.
- Keep the story original.
- Do not use copyrighted characters.
- Do not imitate a specific living artist.
- Return JSON matching the ComicOutline schema.

CURRENT OUTLINE:

{outline.model_dump_json(indent=2)}
"""

    response = client.models.generate_content(
        model=GEMINI_PRO_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ComicOutline,
        ),
    )

    parsed = getattr(
        response,
        "parsed",
        None
    )

    if parsed is not None:

        if isinstance(
            parsed,
            ComicOutline
        ):
            return parsed

        return ComicOutline.model_validate(
            parsed
        )

    text = (
        response.text
        or ""
    ).strip()

    if not text:

        raise RuntimeError(
            "Gemini Pro returned an empty response."
        )

    try:

        data = json.loads(text)

    except json.JSONDecodeError as exc:

        raise RuntimeError(
            "Gemini Pro returned invalid JSON."
        ) from exc

    return ComicOutline.model_validate(
        data
    )