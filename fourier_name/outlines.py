"""Turn text into glyph contours and join them into one closed path."""
from __future__ import annotations

import numpy as np
import uharfbuzz as hb
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.ttLib import TTFont

# Spacing between points on straight segments, in font units.
_LINE_STEP = 15


def _flatten(pen_value, dx, dy):
    """Convert recorded pen operations into a list of point arrays."""
    contours, cur, last = [], [], None
    for op, args in pen_value:
        if op == "moveTo":
            cur, last = [args[0]], args[0]
        elif op == "lineTo":
            a, b = np.array(last), np.array(args[0])
            n = max(2, int(np.linalg.norm(b - a) / _LINE_STEP))
            cur += [tuple(a + (b - a) * t) for t in np.linspace(0, 1, n)[1:]]
            last = args[0]
        elif op == "qCurveTo":
            # TrueType quadratic: consecutive off-curve points have an
            # implied on-curve point halfway between them.
            offs, end, p0 = list(args[:-1]), args[-1], last
            if not offs:
                cur.append(end)
            for i, c in enumerate(offs):
                nxt = end if i == len(offs) - 1 else tuple((np.array(c) + np.array(offs[i + 1])) / 2)
                p, q, r = np.array(p0), np.array(c), np.array(nxt)
                for t in np.linspace(0, 1, 10)[1:]:
                    cur.append(tuple((1 - t) ** 2 * p + 2 * (1 - t) * t * q + t * t * r))
                p0 = nxt
            last = end
        elif op == "curveTo":
            p0 = np.array(last)
            c1, c2, e = map(np.array, args)
            for t in np.linspace(0, 1, 12)[1:]:
                cur.append(tuple((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1
                                 + 3 * (1 - t) * t * t * c2 + t ** 3 * e))
            last = args[-1]
        elif op in ("closePath", "endPath"):
            if len(cur) > 2:
                contours.append(np.array(cur) + (dx, dy))
            cur = []
    return contours


def text_contours(font_path: str, text: str) -> list[np.ndarray]:
    """Shape `text` with HarfBuzz and return its outline contours.

    Shaping matters for Bangla: vowel signs such as ি are reordered and
    conjuncts are formed, which a plain character-to-glyph lookup misses.
    """
    face = hb.Face(hb.Blob.from_file_path(font_path), 0)
    font = hb.Font(face)
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(font, buf, {})

    tt = TTFont(font_path, fontNumber=0)
    glyphs, order = tt.getGlyphSet(), tt.getGlyphOrder()
    contours, x = [], 0
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        pen = DecomposingRecordingPen(glyphs)
        glyphs[order[info.codepoint]].draw(pen)
        contours += _flatten(pen.value, x + pos.x_offset, pos.y_offset)
        x += pos.x_advance
    if not contours:
        raise ValueError(f"The font {font_path} has no visible glyphs for {text!r}")
    return contours


def place(contours, scale: float, top: float) -> list[np.ndarray]:
    """Scale contours, centre them on x = 0 and put their top edge at `top`."""
    pts = np.vstack(contours) * scale
    x_mid = (pts[:, 0].min() + pts[:, 0].max()) / 2
    y_max = pts[:, 1].max()
    return [np.c_[c[:, 0] * scale - x_mid, c[:, 1] * scale - y_max + top] for c in contours]


def join_contours(contours) -> np.ndarray:
    """Join contours into a single closed path.

    Each contour is spliced into the path at the pair of points that are
    closest, so the path visits every contour and returns along the same
    bridge. The result is one loop, which is what a Fourier series needs.
    """
    path = list(contours[0]) + [contours[0][0]]
    remaining = list(range(1, len(contours)))
    while remaining:
        p = np.array(path)
        best = None
        for j in remaining:
            d = np.linalg.norm(p[:, None, :] - contours[j][None, ::2, :], axis=2)
            i, k = np.unravel_index(d.argmin(), d.shape)
            if best is None or d[i, k] < best[0]:
                best = (d[i, k], i, j, 2 * k)
        _, i, j, k = best
        c = np.roll(contours[j], -k, axis=0)
        path = path[: i + 1] + list(c) + [c[0]] + path[i:]
        remaining.remove(j)
    return np.array(path)


# Bangla glyphs look smaller than Latin capitals at the same point size,
# so Bangla lines are set a little larger to balance the two scripts.
BANGLA_SIZE = 1.35


def layout(lines: list[tuple[str, str, bool]], gap: float = 0.18) -> list[np.ndarray]:
    """Stack lines of text vertically, all at the same point size.

    `lines` is a list of (font_path, text, is_bangla). Coordinates are in
    ems; the final drawing is rescaled to fit the screen anyway.
    """
    out, top = [], 0.0
    for font, text, bangla in lines:
        upm = TTFont(font, fontNumber=0)["head"].unitsPerEm
        scale = (BANGLA_SIZE if bangla else 1.0) / upm
        placed = place(text_contours(font, text), scale, top)
        out += sorted(placed, key=lambda c: c[:, 0].min())
        top = np.vstack(placed)[:, 1].min() - gap
    return out
