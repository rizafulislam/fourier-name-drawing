"""Draw the epicycle animation and encode it with ffmpeg."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageDraw

from .fourier import Series


def _rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


@dataclass
class Style:
    width: int = 1920
    height: int = 1080
    fps: int = 30
    intro: float = 1.5      # seconds of blank screen before drawing
    draw: float = 24.0      # seconds spent drawing
    hold: float = 4.0       # seconds the finished drawing stays on screen
    circles: int = 150      # circles drawn on screen (all terms are still summed)
    background: str = "#ffffff"
    ink: str = "#14161a"
    arm: str = "#0b5d63"
    ring: str = "#aacdd0"
    pen: str = "#e8251a"
    line_width: float = 4.0
    supersample: int = 2    # draw larger, then shrink, for smooth lines


class Renderer:
    def __init__(self, series: Series, style: Style, curve_points: int = 4000):
        self.s, self.st = series, style
        ss = style.supersample
        self.curve = series(np.linspace(0, 2 * np.pi, curve_points + 1))
        half_w = np.abs(self.curve.real).max()
        half_h = np.abs(self.curve.imag).max()
        self.scale = min(0.41 * style.width / half_w, 0.42 * style.height / half_h) * ss
        self.cx, self.cy = style.width * ss / 2, style.height * ss / 2
        self.colors = {k: _rgb(getattr(style, k)) for k in ("background", "ink", "arm", "ring", "pen")}

    def _xy(self, z):
        return self.cx + z.real * self.scale, self.cy + z.imag * self.scale

    @property
    def frame_count(self) -> int:
        st = self.st
        return int(round((st.intro + st.draw + st.hold) * st.fps))

    def frame(self, i: int) -> Image.Image:
        st, ss, col = self.st, self.st.supersample, self.colors
        im = Image.new("RGB", (st.width * ss, st.height * ss), col["background"])
        dr = ImageDraw.Draw(im)

        start = st.intro * st.fps
        progress = min(1.0, max(0.0, (i - start) / (st.draw * st.fps)))
        n = int(progress * (len(self.curve) - 1))
        if n > 1:
            dr.line([self._xy(z) for z in self.curve[: n + 1]], fill=col["ink"],
                    width=round(st.line_width * ss), joint="curve")

        if i >= start and progress < 1 and st.circles > 0:
            vec = self.s.c * np.exp(1j * self.s.n * 2 * np.pi * progress)
            tips = np.concatenate([[0], np.cumsum(vec)])
            shown = min(st.circles, len(vec))
            for j in range(shown):
                r = abs(vec[j]) * self.scale
                if r < 1.5 * ss:
                    break
                x, y = self._xy(tips[j])
                dr.ellipse([x - r, y - r, x + r, y + r], outline=col["ring"], width=2 * ss)
            dr.line([self._xy(z) for z in tips[: shown + 1]], fill=col["arm"], width=2 * ss)
            x, y = self._xy(tips[-1])
            dr.ellipse([x - 9 * ss, y - 9 * ss, x + 9 * ss, y + 9 * ss], fill=col["pen"])

        if ss > 1:
            im = im.resize((st.width, st.height), Image.LANCZOS)
        return im


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if exe is None:
        sys.exit("ffmpeg was not found on PATH. Install it first "
                 "(Windows: winget install ffmpeg, Ubuntu: sudo apt install ffmpeg).")
    return exe


def encode(renderer: Renderer, output: str, quiet: bool = False) -> str:
    """Render every frame and write an .mp4 or .gif file."""
    st, ffmpeg = renderer.st, _ffmpeg()
    gif = output.lower().endswith(".gif")
    fd, tmp = tempfile.mkstemp(suffix=".mp4", dir=os.path.dirname(os.path.abspath(output)))
    os.close(fd)

    cmd = [ffmpeg, "-y", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{st.width}x{st.height}",
           "-r", str(st.fps), "-i", "-",
           "-c:v", "libx264", "-crf", "18", "-preset", "veryfast",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    total = renderer.frame_count
    try:
        for i in range(total):
            proc.stdin.write(renderer.frame(i).tobytes())
            if not quiet and (i % st.fps == 0 or i == total - 1):
                print(f"\rframe {i + 1}/{total}", end="", file=sys.stderr, flush=True)
        proc.stdin.close()
        if proc.wait() != 0:
            raise RuntimeError("ffmpeg failed while encoding")
        if gif:
            subprocess.run([ffmpeg, "-y", "-loglevel", "error", "-i", tmp, "-vf",
                            "fps=12,scale=720:-1:flags=lanczos,split[a][b];"
                            "[a]palettegen=max_colors=32[p];[b][p]paletteuse=dither=none",
                            output], check=True)
            os.remove(tmp)
        else:
            os.replace(tmp, output)
        os.chmod(output, 0o644)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
    if not quiet:
        print(f"\nsaved {output}", file=sys.stderr)
    return output
