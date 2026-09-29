from pathlib import Path

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)

from .config import (
    STATIC_DIR,
)


# =========================================================
# Font helper
# =========================================================

def get_font(
    size=28,
    bold=False
):

    candidates = []

    if bold:

        candidates.extend([
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ])

    else:

        candidates.extend([
            "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ])

    for path in candidates:

        if Path(path).exists():

            return ImageFont.truetype(
                path,
                size
            )

    return ImageFont.load_default()


# =========================================================
# Build contact sheet
# =========================================================

def build_contact_sheet(
    panel_paths,
    title
):

    if not panel_paths:

        raise ValueError(
            "No panel images supplied."
        )

    images = []

    for path in panel_paths:

        image = Image.open(
            path
        ).convert("RGB")

        images.append(
            image
        )

    thumbnail_width = 600

    thumbnails = []

    for image in images:

        ratio = (
            thumbnail_width /
            image.width
        )

        thumbnail_height = int(
            image.height *
            ratio
        )

        thumbnail = image.resize(
            (
                thumbnail_width,
                thumbnail_height
            )
        )

        thumbnails.append(
            thumbnail
        )

    gap = 20

    header_height = 90

    sheet_width = (
        thumbnail_width * 2
        + gap * 3
    )

    row_heights = []

    for index in range(
        0,
        len(thumbnails),
        2
    ):

        row = thumbnails[
            index:index + 2
        ]

        row_heights.append(
            max(
                image.height
                for image in row
            )
        )

    sheet_height = (
        header_height
        + gap
        + sum(row_heights)
        + gap * len(row_heights)
    )

    sheet = Image.new(
        "RGB",
        (
            sheet_width,
            sheet_height
        ),
        "white"
    )

    draw = ImageDraw.Draw(
        sheet
    )

    draw.text(
        (
            gap,
            25
        ),
        title,
        fill="black",
        font=get_font(
            36,
            True
        )
    )

    y = (
        header_height
        + gap
    )

    for row_index, row_height in enumerate(
        row_heights
    ):

        for column in range(2):

            image_index = (
                row_index * 2
                + column
            )

            if image_index >= len(
                thumbnails
            ):
                continue

            x = (
                gap
                + column *
                (
                    thumbnail_width
                    + gap
                )
            )

            sheet.paste(
                thumbnails[image_index],
                (
                    x,
                    y
                )
            )

        y += (
            row_height
            + gap
        )

    output_path = (
        STATIC_DIR /
        "comic_contact_sheet.jpg"
    )

    sheet.save(
        output_path,
        quality=92
    )

    return (
        "/static/comic_contact_sheet.jpg"
    )