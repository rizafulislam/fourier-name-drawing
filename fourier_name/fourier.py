"""Complex Fourier series of a closed 2-D path."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Series:
    """z(t) = sum_k c[k] * exp(i * n[k] * t), terms sorted by |c|."""

    n: np.ndarray
    c: np.ndarray

    def __call__(self, t) -> np.ndarray:
        t = np.atleast_1d(t)
        return (self.c[None, :] * np.exp(1j * np.outer(t, self.n))).sum(axis=1)

    def truncate(self, terms: int) -> "Series":
        return Series(self.n[:terms], self.c[:terms])


def resample(path: np.ndarray, samples: int) -> np.ndarray:
    """Return `samples` points spaced evenly along the path's arc length."""
    seg = np.linalg.norm(np.diff(path, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    u = np.linspace(0, s[-1], samples, endpoint=False)
    return np.c_[np.interp(u, s, path[:, 0]), np.interp(u, s, path[:, 1])]


def fourier_series(path: np.ndarray, samples: int = 3000, terms: int = 800) -> Series:
    """Fit a Fourier series to a closed path.

    The path is centred and scaled so its farthest point lies on the unit
    circle. The y axis is flipped to screen orientation (down is positive).
    """
    pts = resample(path, samples)
    x, y = pts[:, 0], pts[:, 1]
    z = (x - (x.min() + x.max()) / 2) - 1j * (y - (y.min() + y.max()) / 2)
    z /= np.abs(z).max()

    c = np.fft.fft(z) / samples
    n = np.fft.fftfreq(samples, 1 / samples).astype(int)
    order = np.argsort(-np.abs(c))[:terms]
    return Series(n[order], c[order])
