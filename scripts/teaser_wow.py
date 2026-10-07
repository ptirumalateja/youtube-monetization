#!/usr/bin/env python3
"""Instagram/Facebook teaser carousel (4:5, 1080x1350) for the Wow! signal, the night before the aliens reels."""
import os, sys
sys.argv = sys.argv[:1]
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx_aliens import font, mono, IVORY, RED, AMBER, TEAL, GREEN, DIM, BG
from thumbs_aliens import load, shade, text, grain, ST

W, H = 1080, 1350
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "release", "aliens_wrong_place", "teaser_carousel")
os.makedirs(OUT, exist_ok=True)


def fade_band(im, y0, y1, top=True):
    """Solid dark band fading into the picture."""
    h = y1 - y0
    a = np.linspace(1, 0, h) if top else np.linspace(0, 1, h)
    a = np.clip(a * 4.0, 0, 1)   # solid for most of the band, short fade at the edge
    mask = Image.fromarray((255 * a[:, None] * np.ones((1, W))).astype(np.uint8))
    im.paste(Image.new("RGB", (W, h), BG), (0, y0), mask)


def save(im, name):
    p = os.path.join(OUT, name)
    im.convert("RGB").save(p, quality=93, optimize=True)
    print(p)


def wrap(d, s, f, maxw):
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def para(im, y, s, size, fill, weight=500, maxw=900, lh=1.35):
    d = ImageDraw.Draw(im)
    f = font("Montserrat.ttf", size, weight)
    for line in wrap(d, s, f, maxw):
        d.text((W // 2, y), line, font=f, fill=fill, anchor="ma")
        y += int(size * lh)
    return y


# 1. The printout: what is this?
src = Image.open(os.path.join(ST, "out", "thumb", "g02v_10.5.png")).convert("RGB")
im = src.crop((0, 200, 1080, 200 + H))
im = shade(im, vignette=0.5)
fade_band(im, 0, 560)
fade_band(im, H - 260, H, top=False)
text(im, (W // 2, 120), "IN 1977, A TELESCOPE", 62, IVORY, 800)
text(im, (W // 2, 205), "PRINTED THIS.", 92, IVORY, 900)
text(im, (W // 2, 300), "The astronomer who found it", 42, AMBER, 600)
text(im, (W // 2, 360), "could only write one word.", 42, AMBER, 600)
text(im, (W // 2, H - 110), "Swipe →", 44, IVORY, 700)
save(grain(im, 5), "01_printout.jpg")

# 2. Decoder: what the six characters mean.
im = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(im)
text(im, (W // 2, 110), "WHAT “6EQUJ5” MEANS", 60, IVORY, 800, glow=False)
y = para(im, 180, "Each character is how loud the signal was, measured every 12 seconds.", 36, DIM, 500, 900)
chars, vals = "6EQUJ5", [6, 14, 26, 30, 19, 5]
x0, step, base, scale = 165, 150, 930, 17
pts = []
for i, (c, v) in enumerate(zip(chars, vals)):
    x = x0 + i * step
    top = base - v * scale
    col = RED if c == "U" else TEAL
    d.rectangle((x - 38, top, x + 38, base), fill=col)
    d.text((x, top - 18), str(v) + "×", font=font("Montserrat.ttf", 34, 700), fill=IVORY, anchor="mb")
    d.text((x, base + 24), c, font=mono(78), fill=IVORY, anchor="ma")
    pts.append((x, top))
d.line((70, base, W - 70, base), fill=DIM, width=2)
para(im, base + 130, "“U” = about 30 times louder than the background hiss of space.", 38, IVORY, 600, 920)
para(im, base + 250, "It rose and fell just like a point in the sky drifting through the telescope’s view.", 34, AMBER, 500, 940)
save(grain(im, 4), "02_decoded.jpg")

# 3. Big Ear: then nothing.
im = load(os.path.join(ST, "stills", "A01_bigear.png"), (W, H), bright=1.0, contrast=1.12)
im = shade(im, vignette=0.45)
fade_band(im, 0, 560)
fade_band(im, H - 330, H, top=False)
text(im, (W // 2, 130), "IT LASTED", 60, IVORY, 700)
text(im, (W // 2, 250), "72 SECONDS.", 120, IVORY, 900)
para(im, 345, "Telescopes have pointed back at that patch of sky many times since.", 38, IVORY, 500, 900)
para(im, 450, "It has never been heard again.", 42, IVORY, 700, 900)
text(im, (W // 2, H - 150), "The full story · tomorrow", 46, AMBER, 700)
text(im, (W // 2, H - 80), "SLOW LIGHT", 34, DIM, 600)
save(grain(im, 5), "03_bigear.jpg")
