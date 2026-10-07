#!/usr/bin/env python3
"""Instagram/Facebook carousel (4:5): everything in the night sky is the past. Explains the name Slow Light."""
import os, sys
sys.argv = sys.argv[:1]
import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx_aliens import font, mono, IVORY, AMBER, TEAL, DIM, BG
from teaser_wow import fade_band, para, wrap
from thumbs_aliens import load, shade, text, grain, ST

W, H = 1080, 1350
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "release", "posts", "old_light")
os.makedirs(OUT, exist_ok=True)


def save(im, name):
    p = os.path.join(OUT, name)
    im.convert("RGB").save(p, quality=93, optimize=True)
    print(p)


def starfield(seed, n=420):
    im = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(im)
    rng = np.random.default_rng(seed)
    for _ in range(n):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        b = int(rng.uniform(40, 150))
        r = rng.choice([0.6, 0.8, 1.0, 1.5], p=[0.5, 0.3, 0.15, 0.05])
        d.ellipse((x - r, y - r, x + r, y + r), fill=(b, b + 10, b + 14))
    return im


# 1. Hook: the night sky is the past.
im = load(os.path.join(ST, "stills_v", "A02_emptysky.png"), (W, H), bright=1.05, contrast=1.1)
im = shade(im, vignette=0.4)
fade_band(im, 0, 260)
text(im, (W // 2, 330), "NOTHING YOU SEE", 76, IVORY, 800)
text(im, (W // 2, 425), "IN THE NIGHT SKY", 76, IVORY, 800)
text(im, (W // 2, 545), "IS HAPPENING NOW.", 80, AMBER, 900)
text(im, (W // 2, H - 110), "Swipe →", 42, IVORY, 700)
save(grain(im, 5), "01_hook.jpg")

# 2. The ladder: how old the light is.
im = starfield(1)
d = ImageDraw.Draw(im)
text(im, (W // 2, 120), "HOW OLD IS THE LIGHT", 56, IVORY, 800, glow=False)
text(im, (W // 2, 190), "REACHING YOUR EYES?", 56, IVORY, 800, glow=False)
rows = [("THE MOON", "1.3 seconds ago", 10),
        ("THE SUN", "8 minutes 20 seconds ago", 22),
        ("SIRIUS", "the brightest star at night", 14, "8.6 years ago"),
        ("ANDROMEDA", "one of the farthest things your eyes can see", 18, "2.5 million years ago")]
y, x_line = 320, 190
d.line((x_line, y + 20, x_line, y + 3 * 220 + 20), fill=(60, 80, 84), width=3)
for k, row in enumerate(rows):
    name, sub, r = row[0], row[1], row[2]
    age = row[3] if len(row) > 3 else sub
    yy = y + k * 220
    col = AMBER if k in (1, 3) else TEAL
    for g in range(4, 0, -1):  # soft glow
        a = 40 * g
        d.ellipse((x_line - r - g * 6, yy + 20 - r - g * 6, x_line + r + g * 6, yy + 20 + r + g * 6), outline=None,
                  fill=tuple(int(c * 0.12 * (5 - g) / 4) for c in col))
    d.ellipse((x_line - r, yy + 20 - r, x_line + r, yy + 20 + r), fill=col)
    d.text((290, yy - 14), name, font=font("Montserrat.ttf", 46, 800), fill=IVORY)
    d.text((290, yy + 44), age, font=font("Montserrat.ttf", 56 if k == 3 else 50, 700), fill=col)
    if len(row) > 3:
        d.text((290, yy + 112), sub, font=font("Montserrat.ttf", 32, 500), fill=DIM)
para(im, H - 160, "You are always seeing the past. The farther you look, the older it gets.", 38, IVORY, 500, 900)
save(grain(im, 4), "02_ladder.jpg")

# 3. Andromeda: the light left before us.
src = Image.open(os.path.join(ST, "stills_v", "A09_deepfield.png")).convert("RGB").crop((153, 480, 713, 1180))
im = src.resize((W, H), Image.LANCZOS)
im = shade(im, vignette=0.4)
fade_band(im, H - 620, H, top=False)
y = H - 520
y = para(im, y, "On a dark night, you can see Andromeda with your own eyes.", 42, IVORY, 600, 920)
y = para(im, y + 30, "The light reaching you tonight left it 2.5 million years ago, when our ancestors were just learning to make stone tools.", 40, IVORY, 500, 920)
para(im, y + 30, "It has been travelling ever since. Just to reach you.", 42, AMBER, 700, 920)
save(grain(im, 5), "03_andromeda.jpg")

# 4. Brand: why Slow Light.
im = starfield(7, 300)
im = shade(im, vignette=0.5)
text(im, (W // 2, 470), "This is why we're called", 46, DIM, 500, glow=False)
text(im, (W // 2, 590), "SLOW LIGHT", 128, IVORY, 900)
d = ImageDraw.Draw(im)
d.line((W // 2 - 200, 690, W // 2 + 200, 690), fill=AMBER, width=3)
para(im, 740, "Stories that took a long time to reach us. And are worth slowing down for.", 42, IVORY, 500, 860)
text(im, (W // 2, H - 140), "Ancient epics · Space · Real people · Strange history", 30, DIM, 600, glow=False)
save(grain(im, 4), "04_slowlight.jpg")
