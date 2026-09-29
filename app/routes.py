from fastapi import (
    APIRouter,
    HTTPException,
)

from .schemas import (
    OutlineRequest,
    OutlineOperationRequest,
    ComicResponse,
    GeneratedPanel,
    ExportRequest,
)

from .gemini_flash import (
    generate_outline,
)

from .gemini_pro import (
    polish_outline,
)

from .image_generator import (
    generate_panel_image,
)

from .exporters import (
    export_pdf,
)


router = APIRouter(
    prefix="/api",
    tags=["ComicCraft API"]
)


# =========================================================
# Health
# =========================================================

@router.get("/health")
def health():

    return {
        "status": "ok",
        "service": "ComicCraft",
        "version": "1.0.0"
    }


# =========================================================
# Generate outline
# =========================================================

@router.post("/outline")
def create_outline(
    request: OutlineRequest
):

    try:

        outline = generate_outline(
            request
        )

        return outline

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


# =========================================================
# Polish outline
# =========================================================

@router.post("/polish")
def polish(
    request: OutlineOperationRequest
):

    try:

        result = polish_outline(
            request.outline
        )

        return result

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


# =========================================================
# Generate all comic images
# =========================================================

@router.post(
    "/generate",
    response_model=ComicResponse
)
def generate_comic(
    request: OutlineOperationRequest
):

    try:

        outline = request.outline

        generated_panels = []

        for panel in outline.panels:

            image_url = (
                generate_panel_image(
                    panel,
                    outline
                )
            )

            generated_panels.append(
                GeneratedPanel(
                    panel_number=(
                        panel.panel_number
                    ),
                    title=panel.title,
                    dialogue=(
                        panel.dialogue
                        or ""
                    ),
                    caption=(
                        panel.caption
                        or ""
                    ),
                    image_url=image_url,
                    scene_description=(
                        panel.scene_description
                    )
                )
            )

        return ComicResponse(
            title=outline.title,
            logline=outline.logline,
            visual_style=outline.visual_style,
            characters=outline.characters,
            panels=generated_panels
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc


# =========================================================
# Export PDF
# =========================================================

@router.post("/export/pdf")
def export_comic_pdf(
    request: ExportRequest
):

    try:

        pdf_url = export_pdf(
            request.comic
        )

        return {
            "success": True,
            "pdf_url": pdf_url
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc)
        ) from exc