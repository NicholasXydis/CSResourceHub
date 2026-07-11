from pathlib import Path

import matplotlib
from PIL import Image, ImageDraw, ImageFont
from utils import (
    CATEGORY_GROUPS,
    CATEGORY_LABELS,
    PUBLIC_DIR,
    SITE_NAME,
    SITE_TAGLINE,
    load_all_resources,
    log,
)

OG_FILE = PUBLIC_DIR / "og.png"
FLAG_FILE = PUBLIC_DIR / "ca-flag.png"
FLAG_SIZE = (44, 29)
WIDTH, HEIGHT = 1200, 630
BACKGROUND = (6, 11, 20)
GRADIENT_START = (79, 124, 255)
GRADIENT_END = (138, 92, 246)
TITLE_COLOR = (246, 248, 252)
BODY_COLOR = (174, 183, 200)
STAT_COLOR = (230, 236, 247)
WHITE = (255, 255, 255)

SUPERSAMPLE = 4
LOGO_SIZE = 96
LOGO_RADIUS = 22
GLYPH_SCALE = LOGO_SIZE / 64

HEX_VERTICES = [
    (32, 10.5),
    (44.6, 17.8),
    (44.6, 32.2),
    (32, 39.5),
    (19.4, 32.2),
    (19.4, 17.8),
]
HEX_CENTRE = (32, 25)
LEFT_PAGE = [
    (30.6, 51.9),
    ("c", (23.6, 45.7), (14.4, 43.6), (6.2, 46.1)),
    (4.4, 51.7),
    ("c", (13, 49.2), (22.6, 51.4), (29.8, 57.8)),
    (30.6, 58.5),
]

FONT_DIR = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
BOLD_FONT = FONT_DIR / "DejaVuSans-Bold.ttf"
REGULAR_FONT = FONT_DIR / "DejaVuSans.ttf"


def load_font(path: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(path), size)


def gradient_bar(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    span = max(x1 - x0, 1)
    for offset in range(span):
        ratio = offset / span
        colour = tuple(
            round(start + (end - start) * ratio)
            for start, end in zip(GRADIENT_START, GRADIENT_END)
        )
        draw.line([(x0 + offset, y0), (x0 + offset, y1)], fill=colour)


def bezier(start, control_a, control_b, end, steps=24):
    points = []
    for step in range(1, steps + 1):
        t = step / steps
        u = 1 - t
        x = (
            u**3 * start[0]
            + 3 * u**2 * t * control_a[0]
            + 3 * u * t**2 * control_b[0]
            + t**3 * end[0]
        )
        y = (
            u**3 * start[1]
            + 3 * u**2 * t * control_a[1]
            + 3 * u * t**2 * control_b[1]
            + t**3 * end[1]
        )
        points.append((x, y))
    return points


def page_polygon(mirror: bool) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    cursor = LEFT_PAGE[0]
    points.append(cursor)
    for step in LEFT_PAGE[1:]:
        if step[0] == "c":
            _, control_a, control_b, end = step
            points += bezier(cursor, control_a, control_b, end)
            cursor = end
        else:
            points.append(step)
            cursor = step
    if mirror:
        points = [(64 - x, y) for x, y in points]
    return points


def draw_logo(image: Image.Image, left: int, top: int) -> None:
    size = LOGO_SIZE * SUPERSAMPLE
    tile = Image.new("RGB", (size, size), BACKGROUND)
    tile_draw = ImageDraw.Draw(tile)
    gradient_bar(tile_draw, (0, 0, size, size))

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=LOGO_RADIUS * SUPERSAMPLE, fill=255
    )

    glyph = ImageDraw.Draw(tile)
    unit = GLYPH_SCALE * SUPERSAMPLE
    stroke = max(1, round(2.1 * unit))

    hexagon = [(x * unit, y * unit) for x, y in HEX_VERTICES]
    glyph.line(hexagon + [hexagon[0]], fill=WHITE, width=stroke, joint="curve")
    centre = (HEX_CENTRE[0] * unit, HEX_CENTRE[1] * unit)
    for vertex in hexagon:
        glyph.line([centre, vertex], fill=WHITE, width=stroke)

    for x, y in HEX_VERTICES:
        radius = 3.2 * unit
        glyph.ellipse(
            (
                x * unit - radius,
                y * unit - radius,
                x * unit + radius,
                y * unit + radius,
            ),
            fill=WHITE,
        )
    radius = 5.2 * unit
    glyph.ellipse(
        (
            centre[0] - radius,
            centre[1] - radius,
            centre[0] + radius,
            centre[1] + radius,
        ),
        fill=WHITE,
    )

    for mirror in (False, True):
        page = [(x * unit, y * unit) for x, y in page_polygon(mirror)]
        glyph.polygon(page, fill=WHITE)

    tile.putalpha(mask)
    image.paste(
        tile.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS),
        (left, top),
        tile.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS),
    )


def generate_og_image() -> None:
    resources = load_all_resources()
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    gradient_bar(draw, (0, 0, WIDTH, 12))

    title_font = load_font(BOLD_FONT, 74)
    body_font = load_font(REGULAR_FONT, 26)
    stat_font = load_font(BOLD_FONT, 54)
    badge_font = load_font(BOLD_FONT, 38)
    label_font = load_font(REGULAR_FONT, 24)

    logo_left = 80
    text_gap = 26
    title_left = logo_left + LOGO_SIZE + text_gap

    draw_logo(image, logo_left, 100)
    draw.text((title_left, 110), SITE_NAME, font=title_font, fill=TITLE_COLOR)

    flag = Image.open(FLAG_FILE).convert("RGBA").resize(FLAG_SIZE, Image.LANCZOS)
    flag_left = logo_left + (LOGO_SIZE - FLAG_SIZE[0]) // 2
    image.paste(flag, (flag_left, 215), flag)
    draw.text(
        (flag_left + FLAG_SIZE[0] + text_gap, 214),
        SITE_TAGLINE,
        font=body_font,
        fill=BODY_COLOR,
    )

    stats = [
        (str(len(resources)), "Resources"),
        (str(len(CATEGORY_LABELS)), "Categories"),
        (str(len(CATEGORY_GROUPS)), "Collections"),
    ]
    for index, (value, label) in enumerate(stats):
        x = 116 + index * 230
        draw.text((x, 360), value, font=stat_font, fill=STAT_COLOR)
        draw.text((x, 430), label, font=label_font, fill=BODY_COLOR)

    open_source_x = 116 + len(stats) * 230
    draw.text((open_source_x, 372), "Open Source", font=badge_font, fill=STAT_COLOR)
    draw.text((open_source_x, 430), "100% Free", font=label_font, fill=BODY_COLOR)

    gradient_bar(draw, (80, 348, 86, 476))
    gradient_bar(draw, (0, HEIGHT - 12, WIDTH, HEIGHT))

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    image.save(OG_FILE, "PNG", optimize=True)
    log(f"✅ Generated og.png ({len(resources)} resources)")


if __name__ == "__main__":
    generate_og_image()
