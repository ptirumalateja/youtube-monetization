#!/usr/bin/env python3
"""Thumbnails for the Slow Light aliens film and its two Shorts (eerie palette, few words, one red mark)."""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx_aliens import font, IVORY, RED, AMBER, TEAL

ST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "stories", "aliens_wrong_place")
OUT = os.path.join(ST, "thumbnails")


def load(path, size, bright=1.0, contrast=1.1):
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    tw, th = size
    s = max(tw / sw, th / sh)
    im = im.resize((round(sw * s), round(sh * s)), Image.LANCZOS)
    l, t = (im.width - tw) // 2, (im.height - th) // 2
    im = im.crop((l, t, l + tw, t + th))
    im = ImageEnhance.Contrast(ImageEnhance.Brightness(im).enhance(bright)).enhance(contrast)
    return im


def shade(im, top=0.0, bottom=0.0, vignette=0.45, band=None):
    """Darken top/bottom gradients plus vignette so text sits on near-black."""
    w, h = im.size
    y = np.linspace(0, 1, h)[:, None]
    x = np.linspace(-1, 1, w)[None, :]
    m = np.ones((h, w))
    if top:
        m *= 1 - top * np.clip(1 - y / 0.45, 0, 1) ** 1.5
    if bottom:
        m *= 1 - bottom * np.clip((y - 0.6) / 0.4, 0, 1) ** 1.5
    if band:
        c, hw, amt = band
        m *= 1 - amt * np.clip(1 - np.abs(y - c) / hw, 0, 1)
    r = np.sqrt(x ** 2 + ((y - 0.5) * 2) ** 2)
    m *= 1 - vignette * np.clip(r - 0.55, 0, 1)
    a = np.asarray(im).astype(np.float32) * m[..., None]
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def text(im, xy, s, size, fill, weight=800, anchor="mm", spacing=0, glow=True):
    f = font("Montserrat.ttf", size, weight)
    if spacing:
        s = (" " * 0).join(s)
    if glow:
        g = Image.new("L", im.size, 0)
        ImageDraw.Draw(g).text(xy, s, font=f, fill=255, anchor=anchor)
        g = g.filter(ImageFilter.GaussianBlur(size // 6))
        im.paste(Image.new("RGB", im.size, (0, 0, 0)), (0, 0), g.point(lambda v: int(v * 0.85)))
    ImageDraw.Draw(im).text(xy, s, font=f, fill=fill, anchor=anchor)


def ring(im, box, width=7, color=RED):
    """Hand-drawn-ish red ellipse, the same mark as the 6EQUJ5 circle in the film."""
    ov = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    x0, y0, x1, y1 = box
    d.ellipse(box, outline=color + (255,), width=width)
    d.ellipse((x0 + 6, y0 - 4, x1 - 2, y1 + 3), outline=color + (150,), width=max(2, width // 3))
    im.paste(ov, (0, 0), ov)


def grain(im, amt=6, seed=3):
    a = np.asarray(im).astype(np.int16)
    n = np.random.default_rng(seed).normal(0, amt, a.shape[:2])[..., None]
    return Image.fromarray((a + n).clip(0, 255).astype(np.uint8))


def save(im, name):
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, name)
    im.convert("RGB").save(p, quality=92, optimize=True)
    print(p, os.path.getsize(p) // 1024, "KB")


# 1. Long-form, 1920x1080: the hot tub alone on the ocean, circled.
W, H = 1920, 1080
im = load(os.path.join(ST, "stills", "A16_hottub.png"), (W, H), bright=1.05)
im = shade(im, top=0.55, bottom=0.35, vignette=0.5)
cx, cy = 960, 768
ring(im, (cx - 175, cy - 95, cx + 175, cy + 85), width=8)
text(im, (W // 2, 150), "WE'VE SEARCHED", 92, IVORY, 700)
text(im, (W // 2, 285), "THIS MUCH.", 168, IVORY, 900)
save(grain(im), "long_thumbnail_1920x1080.jpg")

# 2. Short 1, 1080x1920: the Wow! printout.
W, H = 1080, 1920
im = Image.open(os.path.join(ST, "out", "thumb", "g02v_10.5.png")).convert("RGB")
im = im.resize((W, H), Image.LANCZOS)
im = shade(im, top=0.0, bottom=0.0, vignette=0.55, band=(0.17, 0.12, 0.0))
top = Image.new("RGB", (W, 520), (6, 9, 13))
mask = Image.fromarray((255 * np.clip(1 - (np.linspace(0, 1, 520) - 0.75) / 0.25, 0, 1)[:, None] * np.ones((1, W))).astype(np.uint8))
im.paste(top, (0, 0), mask)
text(im, (W // 2, 190), "72 SECONDS.", 128, IVORY, 900)
text(im, (W // 2, 335), "THEN NOTHING.", 96, RED, 800)
save(grain(im, 5), "short1_thumbnail_1080x1920.jpg")

# 3. Short 2, 1080x1920: the hot tub, vertical.
im = load(os.path.join(ST, "stills_v", "A16_hottub.png"), (W, H), bright=1.05)
im = shade(im, top=0.6, bottom=0.55, vignette=0.45)
cx, cy = 535, 1150
ring(im, (cx - 160, cy - 85, cx + 160, cy + 80), width=8)
text(im, (W // 2, 230), "EVERYTHING", 112, IVORY, 900)
text(im, (W // 2, 350), "WE'VE SEARCHED", 84, IVORY, 700)
text(im, (W // 2, 470), "FOR ALIENS", 84, IVORY, 700)
text(im, (W // 2, 1340), "= ONE HOT TUB", 88, AMBER, 800)
save(grain(im), "short2_thumbnail_1080x1920.jpg")

# 4. Long-form alternative for YouTube "Test & compare": the Wow! printout.
W, H = 1920, 1080
src = Image.open(os.path.join(ST, "out", "thumb", "g02h.png")).convert("RGB").resize((W, H), Image.LANCZOS)
im = Image.new("RGB", (W, H), (6, 9, 13))
im.paste(src.crop((0, 0, W - 470, H)), (470, 0))
im = shade(im, vignette=0.6)
left = Image.new("RGB", (900, H), (6, 9, 13))
mask = Image.fromarray((255 * np.clip(1 - (np.linspace(0, 1, 900) - 0.8) / 0.2, 0, 1)[None, :] * np.ones((H, 1))).astype(np.uint8))
im.paste(left, (0, 0), mask)
text(im, (430, 400), "72 SECONDS.", 108, IVORY, 900)
text(im, (430, 555), "NEVER", 120, RED, 900)
text(im, (430, 690), "HEARD AGAIN.", 86, RED, 800)
save(grain(im, 5), "long_thumbnail_alt_wow_1920x1080.jpg")
