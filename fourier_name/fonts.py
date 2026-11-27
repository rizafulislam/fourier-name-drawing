"""Locate fonts for Bangla and Latin text.

Order of preference: a path given by the user, a font already installed on
the system, then a copy downloaded once from the Google Fonts repository.
"""
from __future__ import annotations

import os
import sys
import urllib.request
from pathlib import Path

from fontTools.ttLib import TTFont

BANGLA_CANDIDATES = [
    r"C:\Windows\Fonts\Nirmala.ttc",
    r"C:\Windows\Fonts\vrinda.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerif.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansBengali-Regular.ttf",
    "/usr/share/fonts/truetype/lohit-bengali/Lohit-Bengali.ttf",
    "/System/Library/Fonts/KohinoorBangla.ttc",
]

LATIN_CANDIDATES = [
    "/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
]

# Used only when the preferred font is missing and cannot be downloaded.
LATIN_FALLBACKS = [
    r"C:\Windows\Fonts\arialbd.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]

_GF = "https://github.com/google/fonts/raw/main/ofl/"
DOWNLOADS = {
    "bangla": ("NotoSansBengali.ttf", _GF + "notosansbengali/NotoSansBengali%5Bwdth,wght%5D.ttf"),
    "latin": ("Poppins-Bold.ttf", _GF + "poppins/Poppins-Bold.ttf"),
}


def _cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME") or (Path.home() / ".cache")
    path = Path(base) / "fourier_name" / "fonts"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _download(kind: str) -> str:
    name, url = DOWNLOADS[kind]
    target = _cache_dir() / name
    if not target.exists():
        print(f"Downloading {name} ...", file=sys.stderr)
        tmp = target.with_suffix(".part")
        try:
            urllib.request.urlretrieve(url, tmp)
            TTFont(tmp).close()  # reject error pages saved instead of a font
        except Exception as err:
            tmp.unlink(missing_ok=True)
            raise OSError(f"could not download {name}: {err}") from err
        tmp.replace(target)
    return str(target)


def find_font(kind: str, user_path: str | None = None) -> str:
    """Return a usable font path for 'bangla' or 'latin' text."""
    if user_path:
        if not os.path.exists(user_path):
            raise FileNotFoundError(f"Font not found: {user_path}")
        return user_path
    preferred = BANGLA_CANDIDATES if kind == "bangla" else LATIN_CANDIDATES
    fallbacks = [] if kind == "bangla" else LATIN_FALLBACKS
    cached = _cache_dir() / DOWNLOADS[kind][0]
    for path in preferred + [str(cached)]:
        if os.path.exists(path):
            return path
    try:
        return _download(kind)
    except OSError as err:
        for path in fallbacks:
            if os.path.exists(path):
                return path
        raise FileNotFoundError(
            f"No {kind} font found and the download failed ({err}). "
            f"Pass one with --{kind}-font PATH."
        ) from err


def has_bangla(text: str) -> bool:
    return any("\u0980" <= ch <= "\u09ff" for ch in text)
