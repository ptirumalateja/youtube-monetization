"""Animate still 'premium' plates (ChatGPT images) for the lightning Short.

Everything that moves is drawn here, never by a video model: the bolt is gated
on/off so it strikes and flickers like real lightning, rings and arrows spread
from the strike point in the plate's perspective, water shimmers, rain and
bubbles drift, and the camera pushes/pans. Coordinates are normalised (0..1)
so higher-resolution originals can be swapped in without changes.
"""
import os, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
PW = 1600  # working width of every plate
FL = "/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf"
VOLT = np.array([0.55, 0.85, 1.0], np.float32)

# strike point (normalised) and the y of the water surface at the strike, per plate
STRIKE = {"p1_split": (0.70, 0.20), "p2_strike": (0.503, 0.357), "p3_nobolt": (0.503, 0.357),
          "p4_danger": (0.72, 0.265), "p5_fish_hit": (0.69, 0.25)}

class Plate:
    def __init__(s, folder, name):
        p = os.path.join(folder, name + "_up.png")
        if not os.path.exists(p): p = os.path.join(folder, name + ".png")
        im = Image.open(p).convert("RGB")
        im = im.resize((PW, round(PW * im.height / im.width)), Image.LANCZOS)
        s.name, s.h = name, im.height
        s.img = np.asarray(im, np.float32) / 255
        sx, sy = STRIKE[name]; s.sx, s.sy = sx, sy
        # bolt matte: thin, bright, blue-white structure above (and just below) the strike point
        L = s.img.mean(2)
        bl = np.asarray(im.convert("L").filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
        m = np.clip((L - bl - 0.08) * 6, 0, 1) * (s.img[..., 2] > 0.55)
        yy = np.arange(s.h)[:, None] / s.h
        m *= (yy < sy + 0.015)
        mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(4))
        s.bolt = np.clip(np.asarray(mi, np.float32)[..., None] / 255 * 1.5, 0, 1)
        # without its bolt: use a real no-bolt plate when we have one, otherwise just dim the bolt
        alt = {"p2_strike": "p3_nobolt"}.get(name)
        if alt:
            q = os.path.join(folder, alt + "_up.png")
            if not os.path.exists(q): q = os.path.join(folder, alt + ".png")
            ia = Image.open(q).convert("RGB").resize((PW, s.h), Image.LANCZOS)
            s.off = np.asarray(ia, np.float32) / 255
        else:
            s.off = s.img  # bolt stays; brightness flicker carries the strike
        # splash/glow around the strike point
        Y, X = np.mgrid[0:s.h, 0:PW]
        s.splash = np.exp(-(((X / PW - sx) * 1.0) ** 2 + ((Y / s.h - sy) * 0.56) ** 2) / 0.006)[..., None].astype(np.float32)

    def frame(s, bolt_k=1.0, splash_k=1.0, base_dark=1.0):
        """bolt_k 0..1 shows the bolt; splash_k scales the glow at the strike point."""
        f = s.off + (s.img - s.off) * min(bolt_k, 1.0)
        f = f + s.bolt * s.img * 0.9 * min(bolt_k, 1.5)  # the bolt itself flares
        # brightness of the whole scene follows the bolt (lightning lights everything)
        f = f * (base_dark * (0.55 + 0.45 * min(1, bolt_k)) + 0.35 * max(0, bolt_k - 1))
        f = f * (1 - s.splash * (1 - max(splash_k, 0.6)) * 0.5)
        return f

def view(img, cx, cy, zoom):
    """9:16 window of the plate centred at normalised (cx, cy); zoom 1 = full plate width."""
    h, w = img.shape[:2]
    cw = w / zoom; ch = cw * 16 / 9
    if ch > h: ch = h; cw = ch * 9 / 16
    x0 = min(max(cx * w - cw / 2, 0), w - cw); y0 = min(max(cy * h - ch / 2, 0), h - ch)
    im = Image.fromarray((np.clip(img[int(y0):int(y0 + ch), int(x0):int(x0 + cw)], 0, 1) * 255).astype(np.uint8))
    out = np.asarray(im.resize((W, H), Image.LANCZOS), np.float32) / 255
    to_screen = lambda nx, ny: ((nx * w - x0) / cw * W, (ny * h - y0) / ch * H)
    return out, to_screen, W / cw * w  # frame, mapping, output px per plate-width unit

def shimmer(f, t, y_from=0, amp=2.0):
    """Cheap water movement: shift each row sideways by a slowly travelling wave."""
    out = f.copy()
    ys = np.arange(y_from, H)
    dx = (amp * np.sin(ys * 0.045 + t * 2.2) + amp * 0.6 * np.sin(ys * 0.11 - t * 3.1)).astype(int)
    for k in np.unique(dx):
        rows = ys[dx == k]
        out[rows] = np.roll(f[rows], k, axis=1)
    return out

RNG = np.random.default_rng(11)
RAIN = RNG.random((260, 3))
def rain(f, t, amount=1.0, angle=0.18):
    lay = Image.new("L", (W, H), 0); d = ImageDraw.Draw(lay)
    for x, y, s in RAIN:
        L = 40 + 70 * s; sp = 2600 + 1400 * s
        yy = (y * (H + 200) + t * sp) % (H + 200) - 100; xx = (x * W + yy * angle) % W
        d.line([xx, yy, xx - L * angle, yy - L], fill=int(60 + 90 * s), width=1 + int(s > 0.8))
    r = np.asarray(lay.filter(ImageFilter.GaussianBlur(0.8)), np.float32)[..., None] / 255
    return f + r * 0.35 * amount * np.array([0.8, 0.9, 1.0])

BUB = RNG.random((90, 4))
def bubbles(f, t, amount=1.0, y_min=0.0):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for x, y, s, p in BUB:
        r = 2 + 9 * s ** 2
        yy = H - ((y * H + t * (60 + 140 * s)) % H); xx = x * W + 8 * np.sin(t * 2 + p * 9)
        if yy < y_min * H: continue
        d.ellipse([xx - r, yy - r, xx + r, yy + r], outline=(200, 235, 255, int(150 * amount)), width=2)
        d.ellipse([xx - r * 0.35 - r * 0.3, yy - r * 0.6, xx - r * 0.3 + r * 0.1, yy - r * 0.2], fill=(255, 255, 255, int(120 * amount)))
    l = np.asarray(lay.filter(ImageFilter.GaussianBlur(0.6)), np.float32) / 255
    return f * (1 - l[..., 3:] * 0.6) + l[..., :3] * l[..., 3:] * 0.9

def rings(f, t0, t, to_screen, ppu, sx, sy, persp=0.42, speed=0.16, every=0.55, n=10, life=3.6, strength=1.0):
    """Current spreading across the surface: rings born every `every` s at the strike point,
    radius in plate-width units, drawn as perspective ellipses, fading with distance (1/r)."""
    if t < t0: return f
    lay = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, cy = to_screen(sx, sy)
    for k in range(n):
        age = t - t0 - k * every
        if age < 0 or age > life: continue
        r = 0.02 + speed * age ** 0.9                  # plate-width units
        a = r * ppu; b = a * persp; yc = cy + b * 0.25  # nearer half sits lower
        inten = min(1, 0.11 / (r + 0.02)) * (1 - age / life) ** 0.7 * strength
        if inten < 0.02: continue
        c = tuple(int(255 * inten * v) for v in VOLT)
        d.ellipse([cx - a, yc - b, cx + a, yc + b], outline=c, width=max(3, int(12 * inten)))
    core = np.asarray(lay, np.float32) / 255
    glow = np.asarray(lay.filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    return f + core * 0.9 + glow * 1.6

def arrows(f, t0, t, to_screen, ppu, sx, sy, persp=0.42, n=10, dur=1.4, strength=1.0):
    """Arrows bursting outward from the strike point in every direction, in perspective."""
    if t < t0: return f
    u = min(1, (t - t0) / dur); fade = 1 - max(0, (t - t0 - dur - 0.8) / 0.6)
    if fade <= 0: return f
    lay = Image.new("RGB", (W, H), (0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, cy = to_screen(sx, sy)
    for k in range(n):
        ang = 2 * np.pi * (k + 0.5) / n + 0.15
        r0, r1 = 0.16, 0.16 + 0.40 * (1 - (1 - u) ** 3)
        pt = lambda r: (cx + np.cos(ang) * r * ppu, cy + np.sin(ang) * r * ppu * persp + r * ppu * persp * 0.25)
        near = 0.55 + 0.45 * (np.sin(ang) + 1) / 2          # arrows toward the camera are bigger
        inten = fade * strength * 0.6
        c = tuple(int(255 * inten * v) for v in (0.6, 0.85, 1.0))
        steps = 14                                           # tapered shaft: thin at the start
        for j in range(steps):
            q0, q1 = pt(r0 + (r1 - r0) * j / steps), pt(r0 + (r1 - r0) * (j + 1) / steps)
            d.line([q0, q1], fill=c, width=max(1, int((2 + 5 * j / steps) * near)))
        p0, p1 = pt(r1 - 0.02), pt(r1)
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = np.hypot(dx, dy) + 1e-6; ux, uy = dx / L, dy / L
        hs = 34 * near
        d.polygon([(p1[0] + ux * hs * 0.3, p1[1] + uy * hs * 0.3), (p1[0] - ux * hs - uy * hs * 0.5, p1[1] - uy * hs + ux * hs * 0.5),
                   (p1[0] - ux * hs + uy * hs * 0.5, p1[1] - uy * hs - ux * hs * 0.5)], fill=c)
    core = np.asarray(lay, np.float32) / 255
    glow = np.asarray(lay.filter(ImageFilter.GaussianBlur(8)), np.float32) / 255
    return f + core * 0.7 + glow * 1.8

def wave_glow(f, t0, t, center, speed=900, width=140, strength=0.9):
    """A pulse of brightness travelling outward from the strike through the water:
    lights up the existing bright (electric-blue) detail as it passes."""
    if t < t0: return f
    Y, X = np.mgrid[0:H, 0:W]
    r = np.hypot(X - center[0], Y - center[1])
    out = f
    for k in range(3):
        age = t - t0 - k * 0.7
        if age < 0: continue
        R = age * speed
        band = np.exp(-((r - R) / width) ** 2) * (300 / (300 + R))
        lum = f.mean(2, keepdims=True)
        out = out + band[..., None] * np.clip(lum - 0.25, 0, 1) * strength * VOLT * 2.0
    return out

def red_pulse(f, t, center, radius, k):
    Y, X = np.mgrid[0:H, 0:W]
    g = np.exp(-((X - center[0]) ** 2 + (Y - center[1]) ** 2) / (2 * radius ** 2))
    p = k * (0.75 + 0.25 * np.sin(t * 18))
    return f + g[..., None] * p * np.array([0.55, 0.12, 0.05])

def label(f, xy, anchor_xy, text, a=1.0, size=40):
    """Thin leader line from a dot to a small spaced-caps label (documentary style)."""
    if a <= 0: return f
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    fnt = ImageFont.truetype(FL, size)
    spaced = " ".join(text)
    tx, ty = xy; ax, ay = anchor_xy
    c = (235, 245, 255, int(255 * a))
    d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], fill=c)
    elbow = (tx - 30 if tx > ax else tx + 30, ty + 26)
    d.line([(ax, ay), elbow], fill=c, width=3)
    tw = d.textlength(spaced, font=fnt)
    x_text = tx if tx > ax else tx - tw
    d.line([elbow, (x_text + tw if tx > ax else x_text, ty + 26)], fill=c, width=3)
    sh = lay.filter(ImageFilter.GaussianBlur(6))
    d.text((x_text, ty), spaced, font=fnt, fill=c, anchor="ls")
    lay = Image.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, 0)), lay)
    l = np.asarray(lay, np.float32) / 255
    return f * (1 - l[..., 3:]) + l[..., :3] * l[..., 3:]
