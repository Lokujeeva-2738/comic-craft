from typing import List, Optional

from pydantic import BaseModel, Field


# =========================================================
# Character
# =========================================================

class Character(BaseModel):
    name: str
    description: str = ""


# =========================================================
# Panel
# =========================================================

class Panel(BaseModel):
    panel_number: int = Field(..., ge=1)
    title: str = ""
    scene_description: str = ""
    dialogue: Optional[str] = ""
    caption: Optional[str] = ""
    image_prompt: str = ""


# =========================================================
# Comic Outline
# =========================================================

class ComicOutline(BaseModel):
    title: str
    logline: str
    visual_style: str
    characters: List[Character] = []
    panels: List[Panel] = []


# =========================================================
# Outline Request
# =========================================================

class OutlineRequest(BaseModel):
    prompt: str
    genre: str = "Superhero"
    visual_style: str = "Modern comic book"
    panel_count: int = Field(default=6, ge=1, le=20)


# =========================================================
# Outline Operation Request
# =========================================================

class OutlineOperationRequest(BaseModel):
    outline: ComicOutline


# =========================================================
# Generated Panel
# =========================================================

class GeneratedPanel(BaseModel):
    panel_number: int
    title: str = ""
    dialogue: str = ""
    caption: str = ""
    image_url: str = ""
    scene_description: str = ""


# =========================================================
# Comic Response
# =========================================================

class ComicResponse(BaseModel):
    title: str
    logline: str
    visual_style: str
    characters: List[Character] = []
    panels: List[GeneratedPanel] = []


# =========================================================
# Export Request
# =========================================================

class ExportRequest(BaseModel):
    comic: ComicResponse

