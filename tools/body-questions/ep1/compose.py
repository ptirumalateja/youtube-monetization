#!/usr/bin/env python3
"""Compose Body Questions ep1 ("It's Not the Water") from rendered plates/sequences.
usage: compose.py FRAMES_DIR OUT_DIR [--only t0 t1] [--guides]"""
import sys, os, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

FR = sys.argv[1]; OUT = sys.argv[2]; os.makedirs(OUT, exist_ok=True)
GUIDES = '--guides' in sys.argv
W, H, FPS, DUR = 1080, 1920, 30, 23.0
B = '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf'
SB = '/usr/share/fonts/opentype/inter/Inter-SemiBold.otf'
INK = (28, 34, 52); ORANGE = (214, 104, 40); GOLD = (222, 150, 30); RED = (210, 60, 50)

def ease(x): x = max(0., min(1., x)); return x * x * (3 - 2 * x)
def eout(x): x = max(0., min(1., x)); return 1 - (1 - x) ** 3

_cache = {}
def img(name):
    if name not in _cache:
        if len(_cache) > 40: _cache.clear()
        _cache[name] = Image.open(f'{FR}/{name}.jpg').convert('RGB')
    return _cache[name]

def seq(prefix, t, t0, fps, n):
    x = (t - t0) * fps; i = int(math.floor(x)); f = x - i
    i = max(0, min(n - 1, i)); j = min(n - 1, i + 1)
    a = img(f'{prefix}{i:03d}')
    if j == i or f < 0.02: return a
    return Image.blend(a, img(f'{prefix}{j:03d}'), f)

def kb(im, z, cx=0.5, cy=0.5, dx=0., dy=0.):
    """zoom z>=1 about (cx,cy) in frame fractions, plus pixel shake."""
    if abs(z - 1) < 1e-4 and dx == 0 and dy == 0: return im
    w, h = W / z, H / z
    x0 = cx * W - w * cx + dx; y0 = cy * H - h * cy + dy
    x0 = max(0, min(W - w, x0)); y0 = max(0, min(H - h, y0))
    return im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h))

def bloom(im, thr=225, gain=0.35, rad=26):
    hi = im.point(lambda v: max(0, v - thr) * 4)
    return ImageChops.add(im, hi.filter(ImageFilter.GaussianBlur(rad)).point(lambda v: int(v * gain)))

def glowred(im, gain=0.5):
    r, g, b = im.split()
    m = ImageChops.subtract(r, g).point(lambda v: max(0, v - 30) * 3)
    gl = Image.merge('RGB', (m, m.point(lambda v: v // 4), m.point(lambda v: v // 5))).filter(ImageFilter.GaussianBlur(18))
    return ImageChops.add(im, gl.point(lambda v: int(v * gain)))

# ---------------- shots ----------------
def shot(t):
    if t < 1.52:  # hook macro, punch at 0.30
        p = eout((t - 0.30) / 0.14)
        z = 1.0 + 0.02 * t + 0.10 * p - 0.04 * ease((t - 0.45) / 1.0)
        return kb(img('H1'), z, 0.52, 0.62)
    if t < 2.92:
        f = (t - 1.52) / 1.40
        return kb(img('H2'), 1.0 + 0.10 * ease(f) + 0.05 * (1 - eout((t - 1.52) / 0.2)), 0.5, 0.6)
    if t < 7.36:
        im = seq('X', t, 2.92, 15, 67)
        z = 1.0 + 0.07 * (1 - eout((t - 2.92) / 0.25)) + 0.06 * (1 - eout((t - 3.78) / 0.25)) * (t > 3.78)
        return glowred(bloom(kb(im, z, 0.5, 0.55), 242, 0.25, 20), 0.9)
    if t < 11.02:
        im = seq('G', t, 7.36, 15, 56)
        return kb(im, 1.0 + 0.06 * ease((t - 7.36) / 3.66), 0.5, 0.55)
    if t < 13.88:
        hit = 1 - eout((t - 11.02) / 0.3)
        sh = 10 * hit * math.sin(t * 90)
        z = 1.0 + 0.06 * hit + 0.05 * ease((t - 11.3) / 2.6)
        return glowred(kb(img('P'), z, 0.5, 0.75, sh, sh * 0.6), 0.7)
    if t < 15.65:
        return kb(img('H3'), 1.0 + 0.10 * ease((t - 13.88) / 1.77) + 0.06 * (1 - eout((t - 13.88) / 0.2)), 0.5, 0.55)
    if t < 19.05:
        im = seq('D', t, 15.65, 15, 52)
        return kb(im, 1.0 + 0.05 * (1 - eout((t - 15.65) / 0.25)), 0.5, 0.55)
    f = (t - 19.05) / 3.95
    return kb(img('C'), 1.22 - 0.22 * eout(f), 0.5, 0.6)

# ---------------- text ----------------
_fonts = {}
def F(path, size):
    k = (path, size)
    if k not in _fonts: _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]

def text(im, lines, y, t0, t, size=128, path=B, halo=True, out=None):
    """lines: [(str, colour)], pop-in at t0 (and fade at out)."""
    if t < t0 or (out is not None and t >= out): return
    p = 1.0 if t0 <= 0 else eout((t - t0) / 0.14)
    s = 0.86 + 0.14 * p; a = 255 if t0 <= 0 else int(255 * min(1, (t - t0) / 0.06))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    hl = Image.new('L', (W, H), 0); dh = ImageDraw.Draw(hl)
    probe = ImageDraw.Draw(Image.new('L', (8, 8)))
    mw = max(probe.textlength(s_, font=F(path, size)) for s_, _ in lines)
    if mw > W - 220: size = int(size * (W - 220) / mw)
    yy = y; fnt = F(path, size)
    for s_, col in lines:
        w = d.textlength(s_, font=fnt)
        assert w <= W - 220, (s_, w)
        x = (W - w) / 2
        d.text((x, yy), s_, font=fnt, fill=col + (a,)); dh.text((x, yy), s_, font=fnt, fill=a)
        yy += int(size * 1.08)
    if s < 0.999:
        cx, cy = W / 2, (y + yy) / 2
        def sc(L):
            L2 = L.resize((int(W * s), int(H * s)), Image.BILINEAR)
            o = Image.new(L.mode, (W, H), 0 if L.mode == 'L' else (0, 0, 0, 0))
            o.paste(L2, (int(cx - cx * s), int(cy - cy * s))); return o
        layer = sc(layer); hl = sc(hl)
    if halo:
        g = hl.filter(ImageFilter.GaussianBlur(18)).point(lambda v: min(255, int(v * 1.1)))
        im.paste(Image.new('RGB', (W, H), (255, 250, 240)), (0, 0), g)
        g2 = hl.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.8))
        im.paste(Image.new('RGB', (W, H), (255, 251, 244)), (0, 0), g2)
    im.paste(layer, (0, 0), layer)
    return yy

def strike(im, t, t0, y, x0, x1, col=RED):
    if t < t0: return
    p = eout((t - t0) / 0.18)
    d = ImageDraw.Draw(im); d.line([(x0, y), (x0 + (x1 - x0) * p, y)], fill=col, width=14)

def overlay(im, t):
    q = (INK); o = ORANGE
    if t < 2.92:
        text(im, [("Why do fingers wrinkle in water?", INK)], 330, 0, t, 50, SB)
        text(im, [("IT'S NOT", INK), ("THE WATER.", ORANGE)], 420, 0, t)
        if t >= 2.16:
            fnt = F(B, 128); d = ImageDraw.Draw(im)
            w = d.textlength("THE WATER.", font=fnt); x = (W - w) / 2
            strike(im, t, 2.16, 420 + 138 + 70, x - 10, x + w + 10, INK)
    elif t < 3.78:
        text(im, [("IT'S YOUR", INK), ("NERVES.", GOLD)], 360, 2.94, t)
    elif t < 7.36:
        text(im, [("5 MINUTES IN", INK)], 340, 3.81, t, 64, B)
        if t >= 5.44:
            text(im, [("BLOOD VESSELS", INK)], 440, 5.44, t, 96)
        if t >= 6.87:
            text(im, [("NARROW.", RED)], 545, 6.87, t, 128)
    elif t < 11.02:
        text(im, [("THE TIP SHRINKS", INK)], 340, 7.55, t, 96)
        if t >= 9.9:
            text(im, [("SKIN BUCKLES.", ORANGE)], 450, 9.9, t, 112)
    elif t < 13.88:
        text(im, [("PROOF:", INK)], 330, 11.06, t, 80)
        if t >= 12.35:
            text(im, [("NERVE CUT =", INK), ("NO WRINKLES.", RED)], 425, 12.35, t, 118)
        if t >= 11.5:
            text(im, [("NERVE CUT", INK)], 1330, 11.5, t, 44, SB) if False else None
    elif t < 15.65:
        text(im, [("SO WHY", INK), ("DO IT?", INK)], 360, 13.91, t, 140)
    elif t < 19.05:
        text(im, [("GRIP.", ORANGE)], 360, 15.69, t, 170)
        if t >= 17.58:
            text(im, [("LIKE TYRE TREADS", INK), ("IN THE RAIN", INK)], 560, 17.58, t, 84)
    else:
        text(im, [("YOUR BODY BUILDS", INK), ("RAIN TYRES.", ORANGE)], 380, 19.08, t, 104)
        if t >= 20.62:
            text(im, [("ALL BY ITSELF.", INK)], 625, 20.62, t, 72)
        if t >= 21.75:
            text(im, [("Which body question next?", INK), ("Comment it below", ORANGE)], 1250, 21.75, t, 58, SB)

def side_labels(im, t):
    if 11.02 <= t < 13.88 and t >= 11.6:
        a = min(1, (t - 11.6) / 0.15)
        d = ImageDraw.Draw(im); f = F(SB, 46)
        for s_, cx, col in (("NERVE CUT", 300, RED), ("NORMAL", 780, INK)):
            w = d.textlength(s_, font=f)
            d.rounded_rectangle([cx - w / 2 - 22, 1352, cx + w / 2 + 22, 1420], 34, fill=(255, 250, 242))
            d.text((cx - w / 2, 1358), s_, font=f, fill=col)

def frame(t):
    im = shot(t).copy()
    side_labels(im, t)
    overlay(im, t)
    if GUIDES:
        d = ImageDraw.Draw(im)
        for y in (300, 1440): d.line([(0, y), (W, y)], fill=(0, 200, 255), width=3)
        for x in (110, W - 110): d.line([(x, 0), (x, H)], fill=(0, 200, 255), width=2)
    return im

if __name__ == '__main__':
    ts = None
    if '--only' in sys.argv:
        i = sys.argv.index('--only'); ts = [float(x) for x in sys.argv[i + 1:] if x[0].isdigit()]
    if ts:
        for t in ts: frame(t).save(f'{OUT}/t{t:05.2f}.jpg', quality=90)
    else:
        n = int(DUR * FPS)
        for k in range(n):
            frame(k / FPS).save(f'{OUT}/{k:04d}.jpg', quality=93)
            if k % 60 == 0: print(k, flush=True)
