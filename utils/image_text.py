"""
Utility para agregar texto sobre imágenes generadas por Flux.
Flux genera imágenes con errores de texto, así que separamos:
  1. Flux genera la imagen de fondo (sin texto)
  2. Pillow agrega el texto con fuente Inter, idioma correcto, colores de marca
"""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Brand colors
BRAND_BLUE = "#667eea"
BRAND_PURPLE = "#764ba2"
BRAND_PINK = "#f093fb"
WHITE = "#FFFFFF"
DARK_BG = "#1a1a2e"
TEXT_DARK = "#333333"

# Font paths (Inter) — fallback to system fonts
_FONT_CACHE: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _get_font(size: int, weight: str = "Bold") -> ImageFont.FreeTypeFont:
    """Get Inter font at given size, with fallbacks."""
    key = (weight, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    project_root = Path(__file__).parent.parent
    fonts_dir = project_root / "data" / "brand_assets" / "fonts"

    # Try Inter font files
    font_files = [
        fonts_dir / f"Inter-{weight}.ttf",
        fonts_dir / f"Inter-{weight}.otf",
        fonts_dir / "Inter-Bold.ttf",
        fonts_dir / "Inter-Regular.ttf",
    ]

    for font_path in font_files:
        if font_path.exists():
            try:
                font = ImageFont.truetype(str(font_path), size)
                _FONT_CACHE[key] = font
                return font
            except Exception:
                continue

    # Fallback: try system Arial/Helvetica
    for fallback in ["arial.ttf", "Arial.ttf", "Helvetica.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
        try:
            font = ImageFont.truetype(fallback, size)
            _FONT_CACHE[key] = font
            return font
        except Exception:
            continue

    # Last resort: default font
    font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font


def add_text_overlay(
    image_path: str | Path,
    texts: list[dict],
    output_path: str | Path | None = None,
) -> Path:
    """
    Add text overlays to an image.

    Args:
        image_path: Path to the base image (from Flux)
        texts: List of text configs, each with:
            - text: str — the text to render
            - position: str — "top", "center", "bottom", or (x, y) tuple
            - font_size: int — font size (default 48)
            - font_weight: str — "Bold", "Regular", "Medium" (default "Bold")
            - color: str — hex color (default white)
            - shadow: bool — add drop shadow (default True)
            - max_width_pct: float — max text width as % of image width (default 0.85)
            - align: str — "center", "left", "right" (default "center")
            - bg_color: str | None — background color behind text (default None)
            - bg_padding: int — padding for background (default 12)
        output_path: Where to save. If None, overwrites the input.

    Returns:
        Path to saved image.
    """
    img_path = Path(image_path)
    img = Image.open(img_path).convert("RGBA")
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = img.size

    for txt_cfg in texts:
        text = txt_cfg.get("text", "")
        if not text:
            continue

        font_size = txt_cfg.get("font_size", 48)
        font_weight = txt_cfg.get("font_weight", "Bold")
        color = txt_cfg.get("color", WHITE)
        shadow = txt_cfg.get("shadow", True)
        max_width_pct = txt_cfg.get("max_width_pct", 0.85)
        align = txt_cfg.get("align", "center")
        bg_color = txt_cfg.get("bg_color")
        bg_padding = txt_cfg.get("bg_padding", 12)
        position = txt_cfg.get("position", "center")

        font = _get_font(font_size, font_weight)

        # Word wrap
        max_px = int(w * max_width_pct)
        wrapped = _wrap_text(draw, text, font, max_px)

        # Calculate text bounding box
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, align=align)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]

        # Position
        if isinstance(position, (list, tuple)):
            x, y = int(position[0]), int(position[1])
        elif position == "top":
            x = (w - tw) // 2
            y = int(h * 0.08)
        elif position == "bottom":
            x = (w - tw) // 2
            y = int(h - th - h * 0.08)
        else:  # center
            x = (w - tw) // 2
            y = (h - th) // 2

        # Background rectangle
        if bg_color:
            r = (
                x - bg_padding,
                y - bg_padding,
                x + tw + bg_padding,
                y + th + bg_padding,
            )
            # Semi-transparent background
            bg_rgba = _hex_to_rgba(bg_color, alpha=200)
            draw.rounded_rectangle(r, radius=8, fill=bg_rgba)

        # Drop shadow
        if shadow:
            shadow_color = (0, 0, 0, 160)
            draw.multiline_text((x + 2, y + 2), wrapped, font=font, fill=shadow_color, align=align)

        # Main text
        draw.multiline_text((x, y), wrapped, font=font, fill=color, align=align)

    # Composite
    result = Image.alpha_composite(img, overlay).convert("RGB")
    out = Path(output_path) if output_path else img_path
    result.save(str(out), "PNG", quality=95)
    return out


def add_brand_bar(
    image_path: str | Path,
    logo_path: str | Path | None = None,
    bar_color: str = BRAND_BLUE,
    position: str = "bottom",
    bar_height_pct: float = 0.06,
    output_path: str | Path | None = None,
) -> Path:
    """Add a brand color bar (optionally with logo) to the image."""
    img_path = Path(image_path)
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size
    bar_h = max(int(h * bar_height_pct), 30)

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    y0 = h - bar_h if position == "bottom" else 0
    draw.rectangle([0, y0, w, y0 + bar_h], fill=_hex_to_rgba(bar_color, 220))

    # Logo
    if logo_path and Path(logo_path).exists():
        try:
            logo = Image.open(logo_path).convert("RGBA")
            logo_h = bar_h - 10
            ratio = logo_h / logo.height
            logo_w = int(logo.width * ratio)
            logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
            lx = w - logo_w - 15
            ly = y0 + 5
            overlay.paste(logo, (lx, ly), logo)
        except Exception:
            pass

    result = Image.alpha_composite(img, overlay).convert("RGB")
    out = Path(output_path) if output_path else img_path
    result.save(str(out), "PNG", quality=95)
    return out


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test = f"{current_line} {word}".strip() if current_line else word
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test
        else:
            if current_line:
                lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines) if lines else text


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple[int, int, int, int]:
    """Convert hex color to RGBA tuple."""
    hex_color = hex_color.lstrip("#")
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return (r, g, b, alpha)
