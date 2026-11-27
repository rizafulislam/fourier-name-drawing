# fourier-name-drawing

Draws a name, in Bangla, English or both, as a chain of rotating circles. Each circle is one term of a complex Fourier series, and the tip of the last circle traces the letters in a single unbroken line.

<p align="center"><img src="examples/rizaful.gif" width="720" alt="রিজাফুল and RIZAFUL drawn by rotating circles"></p>

<p align="center">
  <a href="https://colab.research.google.com/github/rizafulislam/fourier-name-drawing/blob/main/notebooks/fourier_name.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"></a>
  <img src="https://img.shields.io/badge/python-3.9%2B-blue" alt="Python 3.9+">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="MIT license"></a>
</p>

## Contents

- [Draw your own name](#draw-your-own-name)
- [How it works](#how-it-works)
- [Command-line options](#command-line-options)
- [Python API](#python-api)
- [Fonts](#fonts)
- [Limitations](#limitations)
- [Project layout](#project-layout)

## Draw your own name

Replace `আপনার নাম` and `YOUR NAME` below with your name. One line or two, Bangla or English.

### Option 1: Google Colab (nothing to install)

1. Click **Open in Colab** above.
2. In the second cell, change `lines = ["রিজাফুল", "RIZAFUL"]` to `lines = ["আপনার নাম", "YOUR NAME"]`.
3. Choose **Runtime → Run all**. The video plays in the notebook and downloads when it is ready, after about a minute.

### Option 2: On your computer

**Requirements:** [Python](https://www.python.org/downloads/) 3.9 or newer and [ffmpeg](https://ffmpeg.org/download.html). On Windows, install ffmpeg with `winget install ffmpeg`. On Ubuntu, use `sudo apt install ffmpeg`. Restart the terminal afterwards.

Get the code with **Code → Download ZIP** on this page and extract it, or clone it:

```bash
git clone https://github.com/rizafulislam/fourier-name-drawing.git
```

Open the folder in a terminal. In VS Code, use **File → Open Folder**, then **Terminal → New Terminal**. Then run:

```bash
pip install -r requirements.txt
python -m fourier_name "আপনার নাম" "YOUR NAME" -o myname.mp4
```

`myname.mp4` is written to the same folder. To see the finished drawing in a few seconds before rendering the whole video, run:

```bash
python -m fourier_name "আপনার নাম" "YOUR NAME" --preview check.png
```

To use an editor's **Run** button instead, create a `run.py` in the folder:

```python
from fourier_name import make_video

make_video(["আপনার নাম", "YOUR NAME"], "myname.mp4")
```

### Option 3: Install as a command

```bash
pip install git+https://github.com/rizafulislam/fourier-name-drawing.git
fourier-name "আপনার নাম" "YOUR NAME" -o myname.mp4
```

This makes `fourier-name` available from any folder. `fourier-name` and `python -m fourier_name` accept the same options.

## How it works

Any closed curve in the plane can be written as a complex function $z(t) = x(t) + i\,y(t)$ with period $2\pi$, and so as a Fourier series

$$z(t) = \sum_{n} c_n \, e^{int}.$$

Each term $c_n e^{int}$ is a vector of length $|c_n|$ turning $n$ times per cycle. Put the vectors tip to tail and the end of the chain follows the curve.

To get a curve from a name:

1. **Shaping.** The text is shaped with HarfBuzz, which places Bangla vowel signs correctly (ি is drawn before the consonant it follows) and forms conjuncts such as প্ত and ল্ল. The glyph outlines are read with fontTools.
2. **One loop.** A Fourier series needs a single closed path, but a word has many separate outlines: every letter, every hole in a letter, every dot. Each outline is spliced into the path at its closest point to what is already there, so the pen travels in, goes round it, and comes back out the same way.
3. **Sampling.** The loop is resampled at $M$ points evenly spaced along its length, $z_0, \dots, z_{M-1}$.
4. **Coefficients.** The FFT gives every $c_n$ at once (formula below), and only the $N$ largest $|c_n|$ are kept. The defaults are $M = 3000$ and $N = 800$.

$$c_n = \frac{1}{M} \sum_{m=0}^{M-1} z_m \, e^{-2\pi i n m / M}$$

With few terms the name is a smooth blob. Sharp corners need high frequencies, so the letters only become crisp after a few hundred terms.

## Command-line options

Each positional argument is one line of text, drawn top to bottom.

```bash
python -m fourier_name "রিজাফুল" "RIZAFUL" -o rizaful.mp4    # two lines
python -m fourier_name "রিজাফুল" -o rizaful_bangla.mp4       # one line
python -m fourier_name "RIZAFUL" -o rizaful.gif               # GIF output
python -m fourier_name "RIZAFUL" --size 1080x1920 --circles 0 # phone story, no circles
```

| Option | Default | Description |
|---|---|---|
| `-o, --output` | `name.mp4` | output file, `.mp4` or `.gif` |
| `-n, --terms` | 800 | number of Fourier terms. Use 1200 or more for long names |
| `--samples` | 3000 | points sampled along the path |
| `--duration` | 24 | seconds spent drawing |
| `--hold` | 4 | seconds the finished drawing stays on screen |
| `--size` | `1920x1080` | video size in pixels |
| `--fps` | 30 | frames per second |
| `--circles` | 150 | circles shown on screen. `0` hides them; all terms are still used |
| `--background`, `--ink` | `#ffffff`, `#14161a` | colours as hex codes |
| `--bangla-font`, `--latin-font` | automatic | path to a `.ttf`, `.otf` or `.ttc` file |
| `--preview PNG` | | save only the finished drawing as an image |

## Python API

```python
from fourier_name import build_series, make_video, Style

# Render a video with custom timing and colours
make_video(["রিজাফুল", "RIZAFUL"], "rizaful.mp4",
           terms=800, style=Style(draw=20, ink="#0b5d63"))

# Work with the series directly
series = build_series(["RIZAFUL"], terms=200)
print(series.n[:5])          # frequencies, largest coefficient first
print(abs(series.c[:5]))     # magnitudes |c_n|
z = series([0.0, 1.0])       # evaluate z(t) at t = 0 and t = 1
```

## Fonts

Bangla text uses the first font found among Nirmala UI and Vrinda (Windows), FreeSerif, Noto Sans Bengali and Lohit Bengali (Linux), and Kohinoor Bangla (macOS). If none is installed, Noto Sans Bengali is downloaded from Google Fonts. English text uses Poppins Bold, downloaded once if missing, with Arial or a similar system font as the fallback. Downloads are cached in `~/.cache/fourier_name`.

The font changes how the letters look, not how the method works. Use `--bangla-font` or `--latin-font` to choose your own.

## Limitations

- Every separate piece of a letter has to be joined to the rest, so thin connecting lines appear where the pen moves between pieces. Fonts with many small marks show more of them.
- The two lines are set at the same font size, so when one line is much longer than the other, the shorter one looks smaller in the frame.
- Scripts other than Bangla and Latin need a suitable font passed with `--latin-font`. Colour emoji have no outlines and cannot be drawn.

## Project layout

```
fourier_name/
  outlines.py   text shaping, glyph outlines, joining contours into one loop
  fourier.py    arc-length resampling and the FFT
  render.py     epicycle drawing and ffmpeg encoding
  fonts.py      font lookup and download
  cli.py        command-line interface
notebooks/      Colab notebook
examples/       demo animation
tests/          unit tests (run with: pip install pytest && pytest)
```

## License

Released under the [MIT License](LICENSE).

Made by [Rizaful](https://github.com/rizafulislam), Department of Electrical and Electronic Engineering, Jashore University of Science & Technology.
