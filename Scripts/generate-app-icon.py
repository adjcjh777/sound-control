#!/usr/bin/env python3
from __future__ import annotations

import math
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / "Resources"
DOC_IMAGES = ROOT / "docs" / "images"
ICONSET = RESOURCES / "AppIcon.iconset"
SOURCE_PNG = RESOURCES / "AppIcon.png"
DOC_PREVIEW = DOC_IMAGES / "app-icon.png"
ICNS = RESOURCES / "AppIcon.icns"


SCALE = 3
SIZE = 1024
CANVAS = SIZE * SCALE


def sc(value: float) -> int:
    return int(round(value * SCALE))


def rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = hex_color.strip("#")
    return (
        int(value[0:2], 16),
        int(value[2:4], 16),
        int(value[4:6], 16),
        alpha,
    )


def blend(
    a: tuple[int, int, int, int],
    b: tuple[int, int, int, int],
    t: float,
) -> tuple[int, int, int, int]:
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def draw_shadow(
    image: Image.Image,
    bbox: tuple[int, int, int, int],
    radius: int,
    blur: int,
    offset_y: int,
    color: tuple[int, int, int, int],
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    shifted = (bbox[0], bbox[1] + offset_y, bbox[2], bbox[3] + offset_y)
    draw.rounded_rectangle(shifted, radius=radius, fill=color)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    image.alpha_composite(layer)


def rounded_gradient(
    size: tuple[int, int],
    radius: int,
    top: tuple[int, int, int, int],
    bottom: tuple[int, int, int, int],
) -> Image.Image:
    width, height = size
    gradient = Image.new("RGBA", size)
    pixels = gradient.load()
    for y in range(height):
        t = y / max(1, height - 1)
        color = blend(top, bottom, t)
        for x in range(width):
            pixels[x, y] = color

    mask = Image.new("L", size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width, height), radius=radius, fill=255)
    gradient.putalpha(mask)
    return gradient


def draw_soft_circle(
    image: Image.Image,
    center: tuple[int, int],
    radius: int,
    inner: tuple[int, int, int, int],
    outer: tuple[int, int, int, int],
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pixels = layer.load()
    cx, cy = center
    for y in range(cy - radius, cy + radius + 1):
        if y < 0 or y >= image.height:
            continue
        for x in range(cx - radius, cx + radius + 1):
            if x < 0 or x >= image.width:
                continue
            distance = math.hypot(x - cx, y - cy)
            if distance <= radius:
                t = distance / radius
                pixels[x, y] = blend(inner, outer, t)
    image.alpha_composite(layer)


def draw_fader(
    image: Image.Image,
    x: int,
    top: int,
    bottom: int,
    knob_y: int,
    accent: tuple[int, int, int, int],
) -> None:
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)

    track_width = sc(22)
    fill_width = sc(10)
    knob_w = sc(94)
    knob_h = sc(104)

    draw.rounded_rectangle(
        (x - track_width // 2, top, x + track_width // 2, bottom),
        radius=track_width // 2,
        fill=rgba("ffffff", 38),
    )
    draw.rounded_rectangle(
        (x - fill_width // 2, knob_y, x + fill_width // 2, bottom),
        radius=fill_width // 2,
        fill=accent,
    )

    shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        (x - knob_w // 2, knob_y - knob_h // 2 + sc(10), x + knob_w // 2, knob_y + knob_h // 2 + sc(10)),
        radius=sc(34),
        fill=rgba("000000", 90),
    )
    image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(sc(18))))

    draw.rounded_rectangle(
        (x - knob_w // 2, knob_y - knob_h // 2, x + knob_w // 2, knob_y + knob_h // 2),
        radius=sc(34),
        fill=rgba("f9fafb", 245),
    )
    draw.rounded_rectangle(
        (x - knob_w // 2 + sc(8), knob_y - knob_h // 2 + sc(8), x + knob_w // 2 - sc(8), knob_y + knob_h // 2 - sc(8)),
        radius=sc(28),
        outline=rgba("ffffff", 190),
        width=sc(2),
    )
    draw.rounded_rectangle(
        (x - sc(26), knob_y - sc(7), x + sc(26), knob_y + sc(7)),
        radius=sc(7),
        fill=rgba("18202b", 210),
    )

    image.alpha_composite(layer)


def render_icon() -> Image.Image:
    image = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))

    base_bbox = (sc(78), sc(58), sc(946), sc(966))
    base_radius = sc(188)
    draw_shadow(image, base_bbox, base_radius, sc(46), sc(34), rgba("000000", 110))

    base = rounded_gradient(
        (base_bbox[2] - base_bbox[0], base_bbox[3] - base_bbox[1]),
        base_radius,
        rgba("263141"),
        rgba("0a0d12"),
    )
    image.alpha_composite(base, dest=(base_bbox[0], base_bbox[1]))

    base_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(base_overlay)
    overlay_draw.rounded_rectangle(
        base_bbox,
        radius=base_radius,
        outline=rgba("ffffff", 34),
        width=sc(3),
    )
    overlay_draw.rounded_rectangle(
        (sc(106), sc(86), sc(918), sc(930)),
        radius=sc(160),
        outline=rgba("ffffff", 15),
        width=sc(2),
    )
    image.alpha_composite(base_overlay)

    glow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse((sc(254), sc(198), sc(820), sc(826)), fill=rgba("d9792b", 42))
    glow = glow.filter(ImageFilter.GaussianBlur(sc(96)))
    image.alpha_composite(glow)

    draw_fader(image, sc(330), sc(256), sc(758), sc(602), rgba("e88435", 230))
    draw_fader(image, sc(690), sc(256), sc(758), sc(418), rgba("55d5c7", 220))

    core_shadow = Image.new("RGBA", image.size, (0, 0, 0, 0))
    core_shadow_draw = ImageDraw.Draw(core_shadow)
    core_shadow_draw.ellipse((sc(344), sc(344), sc(680), sc(680)), fill=rgba("000000", 105))
    image.alpha_composite(core_shadow.filter(ImageFilter.GaussianBlur(sc(30))))

    draw_soft_circle(
        image,
        (sc(512), sc(512)),
        sc(166),
        rgba("ffb15e"),
        rgba("b9571f"),
    )

    core = Image.new("RGBA", image.size, (0, 0, 0, 0))
    core_draw = ImageDraw.Draw(core)
    core_draw.ellipse((sc(386), sc(386), sc(638), sc(638)), outline=rgba("fff4df", 170), width=sc(8))
    core_draw.ellipse((sc(438), sc(438), sc(586), sc(586)), fill=rgba("151b24", 235))
    core_draw.polygon(
        [
            (sc(474), sc(466)),
            (sc(474), sc(558)),
            (sc(536), sc(598)),
            (sc(536), sc(426)),
        ],
        fill=rgba("f9fafb", 238),
    )
    core_draw.rounded_rectangle((sc(424), sc(476), sc(482), sc(548)), radius=sc(16), fill=rgba("f9fafb", 238))

    for inset, alpha, width in [(0, 160, 12), (38, 105, 9), (78, 70, 7)]:
        box = (sc(372 + inset), sc(332 + inset), sc(760 - inset), sc(720 - inset))
        core_draw.arc(box, start=-42, end=42, fill=rgba("fff4df", alpha), width=sc(width))

    image.alpha_composite(core)

    highlight = Image.new("RGBA", image.size, (0, 0, 0, 0))
    highlight_draw = ImageDraw.Draw(highlight)
    highlight_draw.ellipse((sc(246), sc(116), sc(696), sc(416)), fill=rgba("ffffff", 26))
    highlight = highlight.filter(ImageFilter.GaussianBlur(sc(28)))
    image.alpha_composite(highlight)

    return image.resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def write_iconset(source: Image.Image) -> None:
    if ICONSET.exists():
        shutil.rmtree(ICONSET)
    ICONSET.mkdir(parents=True)

    sizes = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
        ("icon_512x512@2x.png", 1024),
    ]

    for filename, size in sizes:
        source.resize((size, size), Image.Resampling.LANCZOS).save(ICONSET / filename)


def main() -> None:
    RESOURCES.mkdir(parents=True, exist_ok=True)
    DOC_IMAGES.mkdir(parents=True, exist_ok=True)

    source = render_icon()
    source.save(SOURCE_PNG)
    source.save(DOC_PREVIEW)
    write_iconset(source)

    subprocess.run(["iconutil", "-c", "icns", str(ICONSET), "-o", str(ICNS)], check=True)


if __name__ == "__main__":
    main()
