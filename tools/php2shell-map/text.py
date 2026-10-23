"""On-screen text for the PHP2Shell reel: HUD, typed headlines, counters (asserted monotonic)."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from timeline import *

INTER = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
INTER_B = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-ExtraBold.ttf"
MONO_M = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"
_fc = {}
_bc = {}


def _band(a):
    k = round(a, 2)
    if k not in _bc:
        import numpy as np
        y = np.arange(H, dtype=np.float32)
        m = np.exp(-((y - 1470) / 170.0) ** 2) * 0.62 * k
        arr = np.zeros((H, W, 4), np.uint8)
        arr[..., 0] = 6; arr[..., 1] = 1; arr[..., 2] = 2
        arr[..., 3] = (m[:, None] * 255).astype(np.uint8)
        _bc[k] = Image.fromarray(arr, "RGBA")
    return _bc[k]


def font(p, s):
    k = (p, s)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(p, s)
    return _fc[k]


CREAM = (246, 236, 226)
RED = (255, 52, 46)
DIM = (196, 150, 146)
GLYPH = "#%&@$<>/\\01=+*"


def typed(s, t, t0, cps=26.0, seed=0):
    n = int((t - t0) * cps)
    if n < 1:
        return ""
    if n >= len(s):
        return s
    r = random.Random(seed * 1000 + n)
    junk = "".join(r.choice(GLYPH) if c != " " else " " for c in s[n:n + 2])
    return s[:n] + junk


def alpha(t, t0, t1, fin=0.08, fout=0.18):
    if t < t0 or t > t1:
        return 0.0
    return min(1.0, (t - t0) / fin if fin else 1.0, (t1 - t) / fout if fout else 1.0)


def text_c(layer, glow, y, s, f, col, a, glow_a=0.0, spacing=0):
    if a <= 0 or not s:
        return
    d = ImageDraw.Draw(layer)
    w = d.textlength(s, font=f) + spacing * (len(s) - 1)
    x = (W - w) / 2
    c = (*col, int(255 * a))
    if spacing:
        for ch in s:
            d.text((x, y), ch, font=f, fill=c, stroke_width=3, stroke_fill=(10, 2, 3, int(220 * a)))
            if glow_a:
                ImageDraw.Draw(glow).text((x, y), ch, font=f, fill=(*col, int(255 * a * glow_a)))
            x += d.textlength(ch, font=f) + spacing
    else:
        d.text((x, y), s, font=f, fill=c, stroke_width=4, stroke_fill=(10, 2, 3, int(220 * a)))
        if glow_a:
            ImageDraw.Draw(glow).text((x, y), s, font=f, fill=(*col, int(255 * a * glow_a)))


LOG = None  # set to a dict by qa.py to record counter values in time order


def counter(name, v):
    if LOG is not None:
        LOG.setdefault(name, []).append(v)
    return v


def reticle(d, t, xy):
    """target brackets on the first ping (hook and the loop tail)"""
    a = max(alpha(t, 0.0, 2.25, fin=0.0, fout=0.25), alpha(t, 14.35, 15.1, fin=0.3, fout=0.0))
    if a <= 0:
        return
    x, y = xy
    pulse = 1 + 0.06 * math.sin(t * 2 * math.pi / 1.5)
    r = 78 * pulse
    L = 26
    c = (255, 70, 60, int(235 * a))
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = x + sx * r, y + sy * r
            d.line([(cx, cy), (cx - sx * L, cy)], fill=c, width=4)
            d.line([(cx, cy), (cx, cy - sy * L)], fill=c, width=4)
    d.line([(x - r - 40, y), (x - r - 8, y)], fill=c, width=2)
    d.line([(x + r + 8, y), (x + r + 40, y)], fill=c, width=2)
    f = font(MONO, 26)
    lab = "ATTACK #1"
    d.text((x + r + 14, y - r - 10), lab, font=f, fill=(*CREAM, int(240 * a)), stroke_width=3, stroke_fill=(10, 2, 3, int(220 * a)))
    d.text((x + r + 14, y - r + 22), "17 OCT 2026", font=font(MONO_M, 22), fill=(*DIM, int(230 * a)), stroke_width=2, stroke_fill=(10, 2, 3, int(200 * a)))


def draw(img, t, seed_xy=None):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    if seed_xy:
        reticle(d, t, seed_xy)

    # ---- HUD (always on) ----
    f = font(MONO, 30)
    chip = "PHP2SHELL"
    cw = d.textlength(chip, font=f)
    d.rounded_rectangle((64, 132, 64 + cw + 36, 180), 8, fill=(200, 30, 28, 235))
    d.text((82, 136), chip, font=f, fill=CREAM)
    blink = 1.0 if (t * 2) % 2 < 1.4 else 0.25
    d.ellipse((64 + cw + 56, 147, 64 + cw + 74, 165), fill=(255, 60, 50, int(255 * blink)))
    d.text((64 + cw + 84, 137), "LIVE", font=font(MONO_M, 28), fill=(*CREAM, 230))
    # date ticker 17 -> 22 Oct (monotonic until the loop wraps)
    day = 17 + min(5, int(max(0.0, t - 1.2) / 1.25)) if t < WHO else 22
    ds = f"{day} OCT 2026"
    fd = font(MONO, 30)
    d.text((W - 64 - d.textlength(ds, font=fd), 136), ds, font=fd, fill=CREAM, stroke_width=2, stroke_fill=(10, 2, 3))
    tag = "ILLUSTRATIVE MAP"
    ft = font(MONO_M, 20)
    d.text((W - 64 - d.textlength(tag, font=ft), 184), tag, font=ft, fill=(*DIM, 200))

    H1 = font(INTER, 108)
    H1b = font(INTER, 124)
    SUBF = font(MONO_M, 31)
    CNT = font(MONO, 150)
    LBL = font(INTER_B, 40)
    SRC = font(MONO_M, 22)
    Y1, Y2 = 300, 420

    # ---- A: hook ----
    a = alpha(t, 0.0, 2.3, fin=0.0)
    text_c(layer, glow, Y1, typed("SOMEONE KNEW", t, 0.0, 30, 1), H1, CREAM, a)
    text_c(layer, glow, Y2, typed("4 DAYS EARLY.", t, 0.40, 30, 2), H1, RED, a, glow_a=0.9)
    text_c(layer, glow, 570, typed("FIRST ATTACK SEEN   17 OCT", t, 0.95, 48, 3), SUBF, CREAM, a)
    text_c(layer, glow, 616, typed("BUG MADE PUBLIC     21 OCT", t, 1.15, 48, 4), SUBF, DIM, a)

    # ---- B: PHP + 69.3% ----
    a = alpha(t, PHP, 5.05)
    text_c(layer, glow, Y1, typed("THE HOLE IS IN", t, PHP, 34, 5), H1, CREAM, a)
    text_c(layer, glow, Y2 - 6, typed("PHP.", t, PHP + 0.35, 20, 6), H1b, RED, a, glow_a=1.0)
    if t >= PHP + 0.3:
        x = smooth((t - (PHP + 0.3)) / 1.7)
        v = counter("pct", round(69.3 * x, 1))
        text_c(layer, glow, 1340, f"{v:.1f}%", CNT, RED, a, glow_a=1.0)
        text_c(layer, glow, 1510, "OF WEBSITES RUN ON IT", LBL, CREAM, a)
        text_c(layer, glow, 1564, "W3TECHS · SITES WITH A KNOWN SERVER LANGUAGE", SRC, DIM, a * 0.9)

    # ---- C: hosts ----
    a = alpha(t, HOSTS, BREATH - 0.02)
    text_c(layer, glow, Y1, typed("ATTACKS ARE", t, HOSTS, 34, 7), H1, CREAM, a)
    text_c(layer, glow, Y2, typed("SPREADING.", t, HOSTS + 0.3, 30, 8), H1, RED, a, glow_a=0.9)
    if t >= HOSTS + 0.2:
        x = smooth((t - (HOSTS + 0.2)) / 2.5) ** 0.8
        v = counter("hosts", int(round(1886612 * x)))
        text_c(layer, glow, 1340, f"{v:,}", font(MONO, 132), RED, a, glow_a=1.0)
        text_c(layer, glow, 1510, "PHP SERVERS FACING THE INTERNET", LBL, CREAM, a)
        text_c(layer, glow, 1564, "MODAT SCAN · VIA RECORDED FUTURE · 21 OCT", SRC, DIM, a * 0.9)

    # ---- D: no password ----
    a = alpha(t, HIT, SINCE - 0.05, fin=0.0)
    text_c(layer, glow, Y1, "NO PASSWORD.", H1, CREAM, a)
    text_c(layer, glow, Y2, "ONE REQUEST." if t >= HIT2 else "", H1, RED, a, glow_a=0.9)
    text_c(layer, glow, 1420, typed("CRITICAL · CVSS 9.2", t, HIT + 0.9, 40, 9), font(MONO, 44), CREAM, a)
    text_c(layer, glow, 1480, typed("REMOTE CODE EXECUTION", t, HIT + 1.1, 40, 10), SUBF, DIM, a)

    # ---- E: since 2012 ----
    a = alpha(t, SINCE, WHO - 0.05)
    text_c(layer, glow, Y1, typed("HIDDEN IN PHP", t, SINCE, 34, 11), H1, CREAM, a)
    text_c(layer, glow, Y2, typed("SINCE 2012.", t, SINCE + 0.3, 30, 12), H1, RED, a, glow_a=0.9)
    text_c(layer, glow, 1420, typed("FIXED: 8.2.35  8.3.36  8.4.27  8.5.12", t, SINCE + 0.5, 60, 13), font(MONO, 34), CREAM, a)
    text_c(layer, glow, 1476, typed("UPDATE PHP NOW", t, SINCE + 0.9, 40, 14), font(MONO, 34), RED, a, glow_a=0.6)

    # ---- F: who knew ----
    a = alpha(t, WHO, 14.82, fout=0.3)
    text_c(layer, glow, Y1, typed("SO WHO", t, WHO + 0.05, 24, 15), H1b, CREAM, a)
    text_c(layer, glow, Y2 + 20, typed("KNEW?", t, WHO + 0.35, 20, 16), H1b, RED, a, glow_a=1.0)

    band = max(alpha(t, PHP + 0.2, BREATH - 0.02, fin=0.3, fout=0.3), alpha(t, HIT + 0.8, WHO - 0.05, fin=0.3, fout=0.2))
    out = img.convert("RGBA")
    if band > 0:
        out = Image.alpha_composite(out, _band(band))
    g = glow.filter(ImageFilter.GaussianBlur(18))
    # additive-ish glow
    out = Image.alpha_composite(out, g)
    out = Image.alpha_composite(out, layer)
    return out.convert("RGB")
