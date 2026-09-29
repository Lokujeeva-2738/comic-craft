import json
import requests

from .config import GEMINI_API_KEY, GEMINI_TEXT_MODEL
from .schemas import ComicOutline, OutlineRequest


def get_client():
    from google import genai

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. Check your .env file."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


# =========================================================
# Dynamic Local Fallback
# =========================================================

def generate_local_outline(request: OutlineRequest) -> ComicOutline:
    """
    Dynamic fallback generator.

    IMPORTANT:
    This fallback never uses a fixed story.
    It always uses the user's actual story idea.
    """

    story = request.prompt.strip()
    style = request.visual_style.strip()
    panel_count = request.panel_count

    if not story:
        story = "A mysterious adventure begins."

    if not style:
        style = "Modern comic book"

    # -----------------------------------------------------
    # Create generic characters based on the actual story
    # -----------------------------------------------------

    story_words = story.replace(".", "").split()

    if story_words:
        main_subject = " ".join(story_words[:8])
    else:
        main_subject = "the mysterious adventure"

    characters = [
        {
            "name": "Hero",
            "description": (
                f"The main character of the story '{story}'. "
                "A determined and expressive protagonist who drives "
                "the story forward."
            ),
            "role": "Main Character",
        },
        {
            "name": "Companion",
            "description": (
                f"A helpful companion who supports the main character "
                f"through the events described in the story: {story}"
            ),
            "role": "Supporting Character",
        },
    ]

    # -----------------------------------------------------
    # Dynamic panel stages
    # -----------------------------------------------------

    stages = [
        "The story begins and the main situation is introduced.",
        "The main character discovers an important clue or problem.",
        "The main character faces a difficult challenge.",
        "The main character takes action to solve the problem.",
        "The situation becomes more intense and the goal is within reach.",
        "The main character overcomes the major challenge.",
        "The consequences of the adventure become clear.",
        "The story reaches its final turning point.",
        "The main problem is resolved.",
        "The story ends with a new beginning.",
    ]

    panels = []

    for index in range(panel_count):

        stage = stages[index % len(stages)]

        panel_number = index + 1

        title = f"Panel {panel_number}: {stage}"

        scene = (
            f"Story idea: {story}. "
            f"Panel {panel_number}: {stage} "
            f"The scene must directly represent the user's story "
            f"and must not introduce an unrelated setting or plot."
        )

        dialogue = (
            "We have to figure this out together!"
        )

        caption = (
            f"The next moment of the adventure unfolds."
        )

        image_prompt = (
            f"{style}, original comic-book illustration. "
            f"Create panel {panel_number} for this story: {story}. "
            f"Scene requirement: {stage} "
            f"Current scene: {scene} "
            f"Show the main character and supporting character "
            f"acting according to the story. "
            f"Use a background appropriate to the actual story. "
            f"Do not use an underwater library unless the user's "
            f"story specifically mentions one. "
            f"Do not add unrelated animals, locations, objects, "
            f"or characters. "
            f"Make this panel visually different from other panels "
            f"while keeping character appearance consistent. "
            f"Professional cinematic comic composition, "
            f"expressive faces, dynamic poses, detailed environment."
        )

        panels.append(
            {
                "panel_number": panel_number,
                "title": title,
                "scene_description": scene,
                "dialogue": dialogue,
                "caption": caption,
                "image_prompt": image_prompt,
            }
        )

    # -----------------------------------------------------
    # Dynamic title
    # -----------------------------------------------------

    words = story.replace(".", "").split()

    if len(words) >= 5:
        title = " ".join(words[:5]).title()
    elif words:
        title = " ".join(words).title()
    else:
        title = "A New Adventure"

    data = {
        "title": title,
        "logline": story,
        "visual_style": style,
        "characters": characters,
        "panels": panels,
    }

    return ComicOutline.model_validate(data)


# =========================================================
# Gemini Story Generator
# =========================================================

def generate_outline(request: OutlineRequest) -> ComicOutline:
    """
    Generate a comic outline using Gemini.

    If Gemini fails, use the dynamic local fallback.
    """

    if not GEMINI_API_KEY:
        return generate_local_outline(request)

    panel_count = request.panel_count

    prompt = f"""
Create a completely original comic story based ONLY on the
user's story idea.

USER STORY IDEA:
{request.prompt}

GENRE:
{request.genre}

VISUAL STYLE:
{request.visual_style}

Create exactly {panel_count} comic panels.

VERY IMPORTANT:

- The user's story idea is the source of truth.
- Do NOT replace the story with another story.
- Do NOT use a fixed template story.
- Do NOT use an underwater library unless the user explicitly
  mentions an underwater library.
- Do NOT add a sea turtle unless the user asks for one.
- Do NOT add unrelated characters.
- Do NOT add unrelated locations.
- Every panel must represent the user's actual story.
- Every panel must have a meaningfully different scene.
- Keep characters visually consistent between panels.
- Create detailed image prompts specifically for each panel.
- The image prompt must describe the exact action and environment
  of that panel.

Return ONLY valid JSON.

Required structure:

{{
  "title": "Original comic title",
  "logline": "Short summary based on the user's story",
  "visual_style": "{request.visual_style}",
  "characters": [
    {{
      "name": "Character name",
      "description": "Detailed visual description",
      "role": "Character role"
    }}
  ],
  "panels": [
    {{
      "panel_number": 1,
      "title": "Panel title",
      "scene_description": "Detailed scene based on user story",
      "dialogue": "Short dialogue",
      "caption": "Short caption",
      "image_prompt": "Detailed visual prompt for this exact panel"
    }}
  ]
}}
"""

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_TEXT_MODEL}:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_API_KEY,
    }

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=120,
        )

        if response.status_code != 200:
            return generate_local_outline(request)

        response_data = response.json()

        candidates = response_data.get(
            "candidates",
            []
        )

        if not candidates:
            return generate_local_outline(request)

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        if not parts:
            return generate_local_outline(request)

        text = parts[0].get(
            "text",
            ""
        ).strip()

        if not text:
            return generate_local_outline(request)

        # -------------------------------------------------
        # Remove Markdown JSON fences
        # -------------------------------------------------

        if text.startswith("```"):

            text = text.replace(
                "```json",
                "",
                1
            )

            text = text.replace(
                "```",
                ""
            )

            text = text.strip()

        # -------------------------------------------------
        # Parse JSON
        # -------------------------------------------------

        data = json.loads(text)

        outline = ComicOutline.model_validate(
            data
        )

        return outline

    except Exception:
        return generate_local_outline(request)