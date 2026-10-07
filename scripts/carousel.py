#!/usr/bin/env python3
"""Build a Slow Light story carousel (4:5, 1080x1350) from 9:16 stills.

Usage: carousel.py SLIDES.json OUTDIR
SLIDES.json: list of {"image", "focus" (0-1, vertical centre of the crop), "kicker"?, "title"?, "text"}
"""
import json, os, sys, textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1350
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "edit_v7", "fonts")
AMBER = (232, 176, 84)
IVORY = (246, 240, 228)


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


def crop45(im, focus):
    s = W / im.width
    im = im.resize((W, round(im.height * s)), Image.LANCZOS)
    top = min(max(0, round(focus * im.height - H / 2)), im.height - H)
    return im.crop((0, top, W, top + H))


def shade(im, start=0.52):
    """Dark gradient over the lower part for text, plus a soft top vignette."""
    g = Image.new("L", (1, H))
    for y in range(H):
        t = (y / H - start) / (1 - start)
        a = 0 if t < 0 else min(1, t) ** 1.3 * 225
        top = max(0, (0.10 - y / H) / 0.10) * 90
        g.putpixel((0, y), int(max(a, top)))
    g = g.resize((W, H))
    black = Image.new("RGB", (W, H), (8, 6, 4))
    return Image.composite(black, im, g)


def draw_centered(d, y, text, f, fill, spacing=10, shadow=True):
    for line in text.split("\n"):
        w = d.textlength(line, font=f)
        x = (W - w) / 2
        if shadow:
            d.text((x + 2, y + 3), line, font=f, fill=(0, 0, 0))
        d.text((x, y), line, font=f, fill=fill)
        y += f.size + spacing
    return y


def build(slides, out):
    os.makedirs(out, exist_ok=True)
    n = len(slides)
    for i, s in enumerate(slides, 1):
        im = crop45(Image.open(s["image"]).convert("RGB"), s.get("focus", 0.5))
        im = shade(im, s.get("shade", 0.5))
        d = ImageDraw.Draw(im)
        body = font("Montserrat.ttf", 40, 600)
        lines = "\n".join(textwrap.fill(p, 36) for p in s["text"].split("\n"))
        nlines = lines.count("\n") + 1
        y = H - 120 - nlines * 52
        af = font("Cinzel.ttf", 50, 700)
        acc = "\n".join(textwrap.fill(p, 30) for p in s.get("accent", "").split("\n")) if s.get("accent") else ""
        if acc:
            y -= (acc.count("\n") + 1) * 62 + 24
        if s.get("title"):
            tf = font("Cinzel.ttf", 64, 700)
            th = (s["title"].count("\n") + 1) * 76
            y -= th + 26
            yt = draw_centered(d, y, s["title"], tf, AMBER, spacing=12)
            y = yt + 26
        if s.get("kicker"):
            kf = font("Montserrat.ttf", 28, 700)
            draw_centered(d, y - 52, s["kicker"].upper(), kf, AMBER, shadow=False)
        y = draw_centered(d, y, lines, body, IVORY, spacing=12)
        if acc:
            draw_centered(d, y + 24, acc, af, AMBER, spacing=12)
        # footer: brand + page count
        ff = font("Cinzel.ttf", 26, 600)
        d.text((48, H - 58), "SLOW LIGHT", font=ff, fill=(220, 210, 190))
        pf = font("Montserrat.ttf", 26, 600)
        p = f"{i}/{n}"
        d.text((W - 48 - d.textlength(p, font=pf), H - 58), p, font=pf, fill=(220, 210, 190))
        im.save(os.path.join(out, f"{i:02d}.jpg"), quality=94, subsampling=0)


if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
