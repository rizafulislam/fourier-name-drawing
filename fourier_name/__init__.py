"""Draw names with a Fourier series of rotating circles."""
from __future__ import annotations

from .fonts import find_font, has_bangla
from .fourier import Series, fourier_series
from .outlines import join_contours, layout
from .render import Renderer, Style, encode

__version__ = "1.0.0"
__all__ = ["build_series", "make_video", "Series", "Style"]


def build_series(lines: list[str], terms: int = 800, samples: int = 3000,
                 bangla_font: str | None = None, latin_font: str | None = None) -> Series:
    """Fourier series for one or more lines of text, top to bottom."""
    lines = [t.strip() for t in lines if t and t.strip()]
    if not lines:
        raise ValueError("Give at least one line of text.")
    items = []
    for text in lines:
        bangla = has_bangla(text)
        font = find_font("bangla", bangla_font) if bangla else find_font("latin", latin_font)
        items.append((font, text, bangla))
    placed = layout(items)
    return fourier_series(join_contours(placed), samples=samples, terms=terms)


def make_video(lines: list[str], output: str = "name.mp4", terms: int = 800,
               samples: int = 3000, style: Style | None = None,
               bangla_font: str | None = None, latin_font: str | None = None,
               quiet: bool = False) -> str:
    """Render the drawing of `lines` to an .mp4 or .gif file."""
    series = build_series(lines, terms, samples, bangla_font, latin_font)
    return encode(Renderer(series, style or Style()), output, quiet=quiet)
