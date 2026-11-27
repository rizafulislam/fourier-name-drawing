# fourier-name-drawing

Draws a name, in Bangla, English or both, as a chain of rotating circles. Each circle is one term of a complex Fourier series, and the tip of the last circle traces the letters in a single unbroken line.

<p align="center"><img src="examples/rizaful.gif" width="720" alt="রিজাফুল and RIZAFUL drawn by rotating circles"></p>

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rizafulislam/fourier-name-drawing/blob/main/notebooks/fourier_name.ipynb)

## The idea

Any closed curve in the plane can be written as a complex function $z(t) = x(t) + i\,y(t)$ with period $2\pi$, and so as a Fourier series

$$z(t) = \sum_{n} c_n \, e^{int}.$$

Each term $c_n e^{int}$ is a vector of length $|c_n|$ turning $n$ times per cycle. Put the vectors tip to tail and the end of the chain follows the curve.

To get a curve from a name:

1. The text is shaped with HarfBuzz, which handles Bangla vowel signs (ি is drawn before the consonant it follows) and conjuncts such as প্ত and ল্ল. The glyph outlines are read with fontTools.
2. A Fourier series needs one closed loop, but a word has many separate outlines (every letter, every hole in a letter, the dots). Each outline is spliced into the path at its closest point to what is already there, so the pen travels in, goes round it, and comes back out the same way.
3. The loop is resampled at $M$ evenly spaced points $z_0, \dots, z_{M-1}$, and the coefficients come from the FFT:

$$c_n = \frac{1}{M} \sum_{m=0}^{M-1} z_m \, e^{-2\pi i n m / M}.$$

4. Only the $N$ largest coefficients are kept. Defaults are $M = 3000$ and $N = 800$.

With few terms the name is a smooth blob. Sharp corners need high frequencies, so the letters only become crisp after a few hundred terms.

## Install

Python 3.9 or newer and [ffmpeg](https://ffmpeg.org/download.html) are needed.

```bash
pip install git+https://github.com/rizafulislam/fourier-name-drawing.git
```

or from a clone:

```bash
git clone https://github.com/rizafulislam/fourier-name-drawing.git
cd fourier-name-drawing
pip install .
```

On Windows, ffmpeg can be installed with `winget install ffmpeg`. On Ubuntu, use `sudo apt install ffmpeg`.

## Usage

Each argument is one line of text, drawn top to bottom.

```bash
fourier-name "রিজাফুল" "RIZAFUL" -o rizaful.mp4
fourier-name "রিজাফুল" -o rizaful_bangla.mp4
fourier-name "Rizaful" -o rizaful.gif
```

Check how the result will look before spending a minute on the video:

```bash
fourier-name "রিজাফুল" "Rizaful" --preview check.png
```

Useful options:

| Option | Default | |
|---|---|---|
| `-n, --terms` | 800 | number of Fourier terms. Use 1200 or more for long names |
| `--samples` | 3000 | points along the path |
| `--duration` | 24 | seconds spent drawing |
| `--hold` | 4 | seconds the finished drawing stays on screen |
| `--size` | 1920x1080 | e.g. `1080x1920` for a phone story |
| `--circles` | 150 | circles shown on screen. `0` hides them |
| `--background`, `--ink` | white, near black | hex colours |
| `--bangla-font`, `--latin-font` | auto | path to a .ttf, .otf or .ttc |

`python -m fourier_name --help` lists everything.

From Python:

```python
from fourier_name import build_series, make_video, Style

make_video(["রিজাফুল", "RIZAFUL"], "rizaful.mp4", terms=800, style=Style(draw=20))

series = build_series(["RIZAFUL"], terms=200)
print(series.n[:5], series.c[:5])   # frequencies and coefficients, largest first
```

## Fonts

Bangla text uses the first of these that exists: Nirmala UI or Vrinda (Windows), FreeSerif, Noto Sans Bengali, Lohit Bengali (Linux), Kohinoor Bangla (macOS). If none is installed, Noto Sans Bengali is downloaded from Google Fonts. English text uses Poppins Bold, which is downloaded once if missing. Fonts are cached in `~/.cache/fourier_name`. Different fonts change how the letters look, not how the method works.

## Limitations

- Every separate piece of a letter has to be joined to the rest, so thin connecting lines appear where the pen moves between letters. Fonts with many small dots and marks show more of them.
- Text in scripts other than Bangla and Latin needs a font passed with `--latin-font`. Colour emoji have no outlines and cannot be drawn.

## Tests

```bash
pip install pytest
pytest
```

## License

MIT. See [LICENSE](LICENSE).

Rizaful, Department of Electrical and Electronic Engineering, Jashore University of Science & Technology.
