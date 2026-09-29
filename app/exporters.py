import uuid
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .config import (
    EXPORTS_DIR,
    STATIC_DIR,
)


# =========================================================
# Convert URL to local file
# =========================================================

def image_url_to_path(
    image_url: str
) -> Path:

    relative = image_url.replace(
        "/static/",
        "",
        1
    )

    return STATIC_DIR / relative


# =========================================================
# Export comic to PDF
# =========================================================

def export_pdf(
    comic
):

    filename = (
        f"comic_"
        f"{uuid.uuid4().hex[:12]}"
        f".pdf"
    )

    output_path = (
        EXPORTS_DIR /
        filename
    )

    pdf = canvas.Canvas(
        str(output_path),
        pagesize=A4
    )

    page_width, page_height = A4

    pdf.setTitle(
        comic.title
    )

    pdf.setAuthor(
        "ComicCraft"
    )

    for panel in comic.panels:

        # -------------------------------------------------
        # Header
        # -------------------------------------------------

        pdf.setFont(
            "Helvetica-Bold",
            18
        )

        pdf.drawString(
            36,
            page_height - 42,
            comic.title[:90]
        )

        pdf.setFont(
            "Helvetica",
            10
        )

        pdf.drawRightString(
            page_width - 36,
            page_height - 42,
            f"Panel {panel.panel_number}"
        )

        # -------------------------------------------------
        # Image
        # -------------------------------------------------

        image_path = (
            image_url_to_path(
                panel.image_url
            )
        )

        if image_path.exists():

            image = ImageReader(
                str(image_path)
            )

            image_width, image_height = (
                image.getSize()
            )

            margin = 36

            max_width = (
                page_width
                - 2 * margin
            )

            max_height = (
                page_height
                - 150
            )

            scale = min(
                max_width / image_width,
                max_height / image_height
            )

            display_width = (
                image_width * scale
            )

            display_height = (
                image_height * scale
            )

            x = (
                page_width
                - display_width
            ) / 2

            y = (
                page_height
                - 75
                - display_height
            )

            pdf.drawImage(
                image,
                x,
                y,
                width=display_width,
                height=display_height,
                preserveAspectRatio=True,
                mask="auto"
            )

        # -------------------------------------------------
        # Panel information
        # -------------------------------------------------

        text_y = 48

        pdf.setFont(
            "Helvetica-Bold",
            11
        )

        pdf.drawString(
            36,
            text_y + 25,
            panel.title[:100]
        )

        pdf.setFont(
            "Helvetica",
            9
        )

        dialogue = (
            panel.dialogue
            or "—"
        )

        caption = (
            panel.caption
            or "—"
        )

        pdf.drawString(
            36,
            text_y + 10,
            (
                "Dialogue: "
                + dialogue[:150]
            )
        )

        pdf.drawString(
            36,
            text_y - 4,
            (
                "Caption: "
                + caption[:150]
            )
        )

        pdf.showPage()

    pdf.save()

    return (
        f"/static/exports/{filename}"
    )