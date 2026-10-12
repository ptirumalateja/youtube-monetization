"""Designed cross-section of the sea for the lightning Short.

Side-on slice: storm sky, the water surface, a bolt landing at x=0, and the
electric potential V ~ 1/r spreading through the water as a half-dome.
Iso-voltage lines are spaced equally in V, so they crowd near the strike and
spread apart with distance: a fish far away sits between two lines (tiny
voltage across its body), a fish near the strike is crossed by many.

World units: surface at y=0 (up is +y), strike point at (0, 0).
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 1920
DV = 1 / 16          # potential step between iso-lines (V = 1/r)
RNG = np.random.default_rng(7)

# ---------- palette (matches the night grade used on footage) ----------
SKY_TOP, SKY_LOW = np.array([0.020, 0.035, 0.060]), np.array([0.060, 0.090, 0.130])
SEA_TOP, SEA_DEEP = np.array([0.030, 0.140, 0.180]), np.array([0.004, 0.018, 0.030])
VOLT = np.array([0.55, 0.85, 1.00])      # electric cyan-white
HOT = np.array([1.00, 0.30, 0.18])       # danger red

def smooth(x): x = np.clip(x, 0, 1); return x * x * (3 - 2 * x)

# fractal noise texture for clouds (tileable-ish, scrolled over time)
def _noise(shape, octaves=5):
    out = np.zeros(shape, np.float32)
    for o in range(octaves):
        s = 2 ** o * 4
        n = RNG.random((s, s * shape[1] // shape[0] + 1)).astype(np.float32)
        img = Image.fromarray((n * 255).astype(np.uint8)).resize((shape[1], shape[0]), Image.BICUBIC)
        out += np.asarray(img, np.float32) / 255 / 2 ** o
    return out / out.max()
CLOUD = _noise((960, 2400))
PART = RNG.random((420, 4)) * [40, 14, 1, 1] - [20, 13, 0, 0]  # marine snow: x, y, size, phase

def bolt_path(seed, top=8.0, x0=0.0):
    """Jagged polyline from the cloud base down to (x0, 0), in world units."""
    r = np.random.default_rng(seed)
    pts = [(x0 + r.normal(0, 0.35), top), (x0, 0.0)]
    for _ in range(6):  # midpoint displacement
        new = []
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            d = np.hypot(bx - ax, by - ay)
            new += [(ax, ay), ((ax + bx) / 2 + r.normal(0, d * 0.18), (ay + by) / 2)]
        pts = new + [pts[-1]]
    return pts

class Cam:
    def __init__(s, cx, cy, h): s.cx, s.cy, s.h = cx, cy, h; s.k = H / h
    def grid(s):
        xs = s.cx + (np.arange(W) - W / 2) / s.k
        ys = s.cy - (np.arange(H) - H / 2) / s.k
        return np.meshgrid(xs, ys)
    def px(s, x, y): return (W / 2 + (x - s.cx) * s.k, H / 2 - (y - s.cy) * s.k)

def fish_sprite(length_px, t, hot=0.0, seed=0):
    """Fish silhouette facing left, with a little tail beat. Returns RGBA float array."""
    L = int(length_px); Hh = int(L * 0.42); S = 2
    img = Image.new("RGBA", (L * S, Hh * S), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    beat = np.sin(t * 7 + seed) * 0.07
    xs = np.linspace(0, 0.80, 40)
    half = 0.30 * np.sin(np.pi * np.clip(xs / 0.80, 0, 1)) ** 0.65 * (1 - 0.35 * xs) + 0.035
    body = [(x, 0.5 - h) for x, h in zip(xs, half)] + [(x, 0.5 + h * 0.92) for x, h in zip(xs[::-1], half[::-1])]
    tail = [(0.74, 0.47), (0.99, 0.16 + beat), (0.92, 0.5 + beat / 2), (0.99, 0.84 + beat), (0.74, 0.53)]
    fin = [(0.30, 0.25), (0.42, 0.06), (0.55, 0.24)]
    col = tuple(int(c) for c in (np.array([14, 40, 50]) * (1 - hot) + np.array([150, 40, 25]) * hot)) + (255,)
    for poly in (body, tail, fin):
        d.polygon([(x * L * S, y * Hh * S) for x, y in poly], fill=col)
    a = np.asarray(img.resize((L, Hh), Image.LANCZOS), np.float32) / 255
    # rim light along the top edge
    alpha = a[..., 3]
    rim = np.clip(alpha - np.roll(alpha, 3, 0), 0, 1)
    a[..., :3] += rim[..., None] * (np.array([0.25, 0.55, 0.60]) * (1 - hot) + np.array([1.0, 0.5, 0.3]) * hot) * 0.8
    eye = (int(L * 0.13), int(Hh * 0.42))
    a[max(eye[1] - 2, 0):eye[1] + 3, eye[0] - 2:eye[0] + 3, :3] = 0.8
    return a

def paste(f, spr, cx, cy):
    h, w = spr.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
    xa, ya, xb, yb = max(x0, 0), max(y0, 0), min(x0 + w, W), min(y0 + h, H)
    if xa >= xb or ya >= yb: return
    s = spr[ya - y0:yb - y0, xa - x0:xb - x0]
    f[ya:yb, xa:xb] = f[ya:yb, xa:xb] * (1 - s[..., 3:]) + s[..., :3] * s[..., 3:]

def render(t, cam, field_t0=None, front_speed=2.2, show_lines=0.0, bolt=0.0, fishes=(), hot=0.0, glow=1.0):
    """One frame. t: scene time (s). field_t0: when the strike happened (None = no field yet).
    show_lines: 0..1 iso-line opacity. bolt: 0..1 bolt brightness. fishes: list of (x, y, len, seed)."""
    X, Y = cam.grid()
    water = Y < 0
    # surface waves
    surf = 0.06 * np.sin(X * 2.1 + t * 1.7) + 0.035 * np.sin(X * 4.7 - t * 2.3)
    water = Y < surf
    # sky
    u = np.clip((Y - 0) / 9, 0, 1)
    f = SKY_LOW * (1 - u[..., None]) + SKY_TOP * u[..., None]
    cy0 = ((Y * 60 + 400) % 960).astype(int); cx0 = ((X * 60 + t * 25 + 1200) % 2400).astype(int)
    cl = CLOUD[cy0, cx0]
    f = f + (cl[..., None] ** 2) * 0.10 * (~water)[..., None] * (1 + bolt * 6)
    # sea gradient
    dpt = np.clip(-Y / 9, 0, 1)
    sea = SEA_TOP * (1 - dpt[..., None]) ** 1.5 + SEA_DEEP * (1 - (1 - dpt[..., None]) ** 1.5)
    f = np.where(water[..., None], sea, f)
    # faint light shafts from the surface
    sh = (0.5 + 0.5 * np.sin(X * 1.3 + 0.4 * Y + t * 0.3)) ** 6 * np.exp(Y / 3) * 0.05
    f += (sh * water)[..., None] * np.array([0.4, 0.8, 0.9])
    # surface line highlight
    sl = np.exp(-((Y - surf) * cam.k / 2.5) ** 2)
    f += sl[..., None] * np.array([0.25, 0.45, 0.55]) * (0.6 + bolt * 2)

    # fish
    for fx, fy, flen, seed, fhot in fishes:
        px, py = cam.px(fx, fy)
        spr = fish_sprite(flen * cam.k, t, fhot, seed)
        paste(f, spr, px, py)
    # ---------- electric field ----------
    if field_t0 is not None and t >= field_t0:
        age = t - field_t0
        R = 0.25 + front_speed * age ** 1.15             # spreading front, all directions
        r = np.hypot(X, Y) + 1e-3
        front = smooth((R - r) / (0.25 * R + 0.2))
        inside = water * front
        # field strength E ~ 1/r^2: bright core fading fast with distance
        E = np.clip(0.06 / r ** 2, 0, 3)
        f += (inside * np.minimum(E, 1.5) * glow)[..., None] * VOLT * 0.55
        # leading pulse ring
        ring = np.exp(-((r - R) * cam.k / 18) ** 2) * water * np.clip(1.2 / (R + 0.5), 0, 1)
        f += ring[..., None] * VOLT * 0.9 * glow
        if show_lines > 0:
            V = 1 / r
            ph = V / DV
            spacing = r * r * DV * cam.k                    # px between neighbouring lines here
            dpx = np.abs(ph - np.round(ph)) * spacing
            line = np.exp(-(dpx / 1.6) ** 2)
            dense = smooth((10 - spacing) / 8)              # lines merge into a glow where crowded
            line = line * (1 - dense) + dense * 0.55
            line *= (ph >= 0.75)                             # nothing beyond r = 1/(0.75 dV)
            lcol = VOLT * (1 - hot) + HOT * hot
            f += (line * inside * show_lines * 0.65)[..., None] * lcol
    # marine snow (parallax with camera)
    for x, y, s, p in PART:
        px, py = cam.px(x + 0.08 * np.sin(t * 0.4 + p * 6), y + ((t * 0.05 + p) % 1) * 0.6)
        if 0 <= px < W - 3 and 0 <= py < H - 3 and y < 0:
            v = 0.10 + 0.25 * s
            f[int(py):int(py) + 2, int(px):int(px) + 2] += v
    # bolt
    if bolt > 0.01:
        lay = Image.new("L", (W, H), 0); d = ImageDraw.Draw(lay)
        for seed, wdt in ((3, 6), (5, 2)):
            pts = [cam.px(x, y) for x, y in bolt_path(seed)]
            d.line(pts, fill=255 if seed == 3 else 150, width=wdt)
        core = np.asarray(lay, np.float32) / 255
        glowl = np.asarray(lay.filter(ImageFilter.GaussianBlur(28)), np.float32) / 255
        f += (core * 1.4 + glowl * 3.0)[..., None] * np.array([0.75, 0.88, 1.0]) * bolt
        # contact flash on the surface
        r0 = np.hypot(X, Y)
        f += (np.exp(-(r0 * cam.k / 90) ** 2) * bolt * 1.5)[..., None] * np.array([0.8, 0.95, 1.0])
        f += bolt * 0.15
    return f
