"""Command line interface: fourier-name "রিজাফুল" "RIZAFUL" -o rizaful.mp4"""
from __future__ import annotations

import argparse

from . import Style, __version__, build_series
from .render import Renderer, encode


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(
        prog="fourier-name",
        description="Draw one or more lines of text (Bangla or English) with a "
                    "Fourier series of rotating circles.")
    p.add_argument("lines", nargs="+", help='text to draw, one argument per line, e.g. "রিজাফুল" "RIZAFUL"')
    p.add_argument("-o", "--output", default="name.mp4", help="output .mp4 or .gif (default: name.mp4)")
    p.add_argument("-n", "--terms", type=int, default=800, help="number of Fourier terms (default: 800)")
    p.add_argument("--samples", type=int, default=3000, help="points sampled along the path (default: 3000)")
    p.add_argument("--duration", type=float, default=24, help="seconds spent drawing (default: 24)")
    p.add_argument("--hold", type=float, default=4, help="seconds the result stays on screen (default: 4)")
    p.add_argument("--size", default="1920x1080", help="video size WxH (default: 1920x1080)")
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--circles", type=int, default=150, help="circles shown on screen, 0 hides them (default: 150)")
    p.add_argument("--background", default="#ffffff")
    p.add_argument("--ink", default="#14161a")
    p.add_argument("--bangla-font", help="path to a .ttf/.otf/.ttc font for Bangla text")
    p.add_argument("--latin-font", help="path to a font for English text")
    p.add_argument("--preview", metavar="PNG", help="save only the finished drawing as an image and exit")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    a = p.parse_args(argv)

    try:
        w, h = (int(v) for v in a.size.lower().split("x"))
    except ValueError:
        p.error("--size must look like 1920x1080")

    series = build_series(a.lines, a.terms, a.samples, a.bangla_font, a.latin_font)
    style = Style(width=w, height=h, fps=a.fps, draw=a.duration, hold=a.hold,
                  circles=a.circles, background=a.background, ink=a.ink)
    renderer = Renderer(series, style)
    if a.preview:
        renderer.frame(renderer.frame_count - 1).save(a.preview)
        print(f"saved {a.preview}")
        return
    encode(renderer, a.output)


if __name__ == "__main__":
    main()
