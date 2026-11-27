import numpy as np

from fourier_name.fourier import fourier_series


def test_circle_is_one_term():
    t = np.linspace(0, 2 * np.pi, 400, endpoint=False)
    circle = np.c_[np.cos(t), np.sin(t)]
    s = fourier_series(np.vstack([circle, circle[:1]]), samples=400, terms=5)
    assert abs(s.c[0]) > 0.99
    assert np.all(np.abs(s.c[1:]) < 1e-3)


def test_square_reconstructs():
    corners = np.array([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]], float)
    s = fourier_series(corners, samples=1000, terms=1000)
    z = s(np.linspace(0, 2 * np.pi, 1000, endpoint=False))
    assert np.allclose(np.abs(z.real).max(), 1 / np.sqrt(2), atol=0.02)
