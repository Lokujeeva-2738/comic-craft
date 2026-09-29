from .config import PANELS_DIR


def generate_panel_image(panel, outline):
    """
    Use local images from static/panels.
    No API key or token is required.
    """

    panel_number = int(panel.panel_number)

    possible_files = [
        PANELS_DIR / f"panel_{panel_number}.jpg",
        PANELS_DIR / f"panel_{panel_number}.jpeg",
        PANELS_DIR / f"panel_{panel_number}.png",
        PANELS_DIR / f"panel_{panel_number}.webp",
    ]

    for image_path in possible_files:
        if image_path.exists():
            return f"/static/panels/{image_path.name}"

    raise RuntimeError(
        f"Image not found for Panel {panel_number}. "
        f"Please check static/panels/panel_{panel_number}.*"
    )