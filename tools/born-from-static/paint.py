"""Paint the hidden picture for Born From Static (procedural, numpy).

A lone figure on a sea cliff watches a ringed planet rise over the ocean.
Writes a float32 linear-ish RGB array (H, W, 3) in [0, 1] to OUT.npy and a PNG preview.

    python3 paint.py OUT/painting
"""
import sys
import numpy as np
from scipy.ndimage import gaussian_filter, zoom
from PIL import Image

W, H = 1080, 1920
HORIZON = 1190
rng = np.random.default_rng(7)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)


def fbm(octaves=6, base=4, seed=0, aspect=1.0):
    """Fractal value noise on the full frame, roughly in [-1, 1]."""
    r = np.random.default_rng(seed)
    out = np.zeros((H, W), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        n = base * 2 ** o
        gh, gw = max(2, int(n * H / W / aspect)), max(2, n)
        g = r.standard_normal((gh + 1, gw + 1)).astype(np.float32)
        up = zoom(g, (H / gh, W / gw), order=3)[:H, :W]
        out += amp * up
        total += amp
        amp *= 0.55
    return out / total


def lerp(a, b, t):
    t = np.clip(t, 0, 1)[..., None]
    return a * (1 - t) + b * t


def col(*c):
    return np.array(c, np.float32) / 255.0


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


img = np.zeros((H, W, 3), np.float32)

# ---- sky -------------------------------------------------------------------
t = yy / HORIZON
sky = lerp(col(10, 8, 34), col(48, 22, 92), smooth(0.0, 0.55, t))
sky = lerp(sky, col(150, 48, 118), smooth(0.45, 0.85, t))
sky = lerp(sky, col(250, 128, 84), smooth(0.80, 1.0, t))
# painterly clouds: streaky low-frequency noise, stronger near the horizon
cl = fbm(6, 3, seed=1, aspect=3.5)
band = smooth(0.35, 0.95, t) * (1 - smooth(0.98, 1.0, t))
sky = sky * (1 + 0.22 * cl[..., None] * band[..., None])
sky += col(255, 150, 120) * (np.clip(cl, 0, 1) ** 2 * band * 0.25)[..., None]
img[:] = sky

# stars (fewer toward the horizon)
n = 2600
sx = rng.uniform(0, W, n)
sy = rng.uniform(0, HORIZON, n) ** 1.0
keep = rng.uniform(0, 1, n) > (sy / HORIZON) ** 0.7
sx, sy = sx[keep], sy[keep]
mag = rng.uniform(0.15, 1.0, sx.size) ** 3
stars = np.zeros((H, W), np.float32)
np.add.at(stars, (sy.astype(int), sx.astype(int)), mag * 3)
stars = gaussian_filter(stars, 0.8) + gaussian_filter(stars, 3) * 0.6
img += stars[..., None] * col(220, 225, 255)

# aurora ribbon (teal) high in the sky
ax = xx / W
curve = 360 + 120 * np.sin(ax * 5.0 + 0.6) + 50 * np.sin(ax * 13.0)
d = (yy - curve)
rib = np.exp(-(d / 60) ** 2) * (0.5 + 0.5 * fbm(5, 6, seed=3, aspect=0.25))
rays = np.clip(-d, 0, None)
rib += np.exp(-rays / 180) * (d < 0) * 0.35 * (0.5 + 0.5 * np.sin(xx * 0.09 + fbm(3, 8, seed=4) * 6))
rib *= smooth(0, 0.2, ax) * smooth(1.0, 0.75, ax)
img += (rib * 0.32)[..., None] * col(60, 255, 200)

# ---- planet ----------------------------------------------------------------
PX, PY, PR = 560.0, 820.0, 330.0
dx, dy = (xx - PX) / PR, (yy - PY) / PR
r2 = dx * dx + dy * dy
disc = r2 < 1
z = np.sqrt(np.clip(1 - r2, 0, 1))
# light from the lower right (setting sun behind the viewer, right side)
L = np.array([0.55, 0.35, 0.76]); L /= np.linalg.norm(L)
lam = np.clip(dx * L[0] + dy * L[1] + z * L[2], 0, 1)
ra = np.deg2rad(-14)  # shared with the rings so the bands line up with them
lat = -dx * np.sin(ra) + dy * np.cos(ra)
bands = np.sin(lat * 22 + 2.0 * fbm(5, 6, seed=5) ) * 0.5 + 0.5
bands2 = np.sin(lat * 57 + 3.0 * fbm(4, 10, seed=6)) * 0.5 + 0.5
pc = lerp(col(232, 170, 110), col(160, 90, 80), bands)
pc = lerp(pc, col(255, 225, 180), bands2 * 0.35)
# storm spot
spot = np.exp(-(((dx - 0.25) / 0.16) ** 2 + ((lat + 0.22) / 0.07) ** 2))
pc = lerp(pc, col(200, 80, 60), spot * 0.8)
shade = (0.06 + 0.94 * lam ** 0.8)[..., None]
limb = (1 - z) ** 3
planet = pc * shade + col(255, 140, 120) * (limb * 0.5 * lam)[..., None]
img = np.where(disc[..., None], planet, img)
# atmosphere glow around the planet
rr = np.sqrt(r2)
glow = np.exp(-np.clip(rr - 1, 0, None) / 0.10) * (rr >= 1) * 0.55
glow += np.exp(-np.clip(rr - 1, 0, None) / 0.6) * (rr >= 1) * 0.18
img += glow[..., None] * col(255, 160, 130)

# rings: tilted ellipse, back half hidden by the planet
rx = (xx - PX) * np.cos(ra) + (yy - PY) * np.sin(ra)
ry = -(xx - PX) * np.sin(ra) + (yy - PY) * np.cos(ra)
er = np.sqrt((rx / (PR * 2.05)) ** 2 + (ry / (PR * 0.42)) ** 2)
ring_band = smooth(0.66, 0.70, er) * (1 - smooth(0.97, 1.0, er))
ring_tex = 0.55 + 0.45 * np.sin(er * 140) * np.sin(er * 37 + 1)
gap = 1 - 0.85 * np.exp(-((er - 0.83) / 0.008) ** 2)
ring_a = ring_band * ring_tex * gap * np.where(disc, 0.95, 0.8)
front = ry > 0
ring_vis = np.where(disc & ~front, 0, ring_a)
ring_col = col(250, 215, 175) * (0.4 + 0.6 * smooth(-1, 1, rx / (PR * 2)))[..., None]
img = lerp(img, ring_col, ring_vis)
# soft ring shadow on the planet, just above the front arc
sh = np.exp(-((ry / PR - 0.12) / 0.05) ** 2) * disc * (er < 0.66)
img *= (1 - 0.45 * sh)[..., None]

# ---- distant mountains ------------------------------------------------------
def ridge(seed, base, amp, rough):
    r = np.random.default_rng(seed)
    g = r.standard_normal(40)
    x = np.linspace(0, 39, W)
    h = np.interp(x, np.arange(40), g)
    g2 = r.standard_normal(200)
    h += rough * np.interp(np.linspace(0, 199, W), np.arange(200), g2)
    return base - amp * h


for seed, base, amp, c, haze, mask_fn in [
    (11, HORIZON - 30, 28, col(70, 40, 96), 0.55, lambda x: smooth(560, 860, x)),
    (12, HORIZON - 10, 22, col(46, 24, 70), 0.35, lambda x: smooth(620, 900, x)),
]:
    h = ridge(seed, base, amp, 0.25)
    m = (yy > h[None, :]) & (yy < HORIZON) & (mask_fn(xx) > 0.5)
    img = np.where(m[..., None], lerp(c * np.ones_like(img), col(240, 120, 100), np.full((H, W), haze * 0.3)), img)

# ---- sea --------------------------------------------------------------------
sea_t = (yy - HORIZON) / (H - HORIZON)
sea = lerp(col(120, 52, 100), col(14, 10, 36), smooth(0, 0.7, sea_t))
waves = fbm(6, 3, seed=20, aspect=0.2)
# broken glints: short horizontal dashes, denser and thinner toward the horizon
gl = fbm(6, 6, seed=21, aspect=0.08)
fine = np.clip(gl * 2.2 + 0.1 * np.sin(yy * 0.6), 0, 1) ** 1.5
sea *= (0.85 + 0.25 * waves)[..., None]
# reflection column of the planet and its glow
col_w = 120 + 260 * sea_t
refl = np.exp(-((xx - PX - 20 * waves) / col_w) ** 2)
streak = np.clip(fine * 1.6 - 0.6, 0, 1) * refl * (1 - 0.6 * sea_t)
sea += streak[..., None] * col(255, 175, 120) * 0.9
sea += (refl * 0.18 * (1 - sea_t))[..., None] * col(255, 120, 110)
# horizon glow
sea += (np.exp(-np.clip(yy - HORIZON, 0, None) / 30))[..., None] * col(255, 140, 100) * 0.35
img = np.where((yy >= HORIZON)[..., None], sea, img)

# ---- foreground cliff + figure ----------------------------------------------
cx = xx / W
edge_x = 600 + 30 * fbm(4, 12, seed=30)[:, 0:1]
top = 1460 + 160 * smooth(0.25, 0.62, cx) ** 1.5 * 0 + 0
cliff_top = 1450 - 90 * (1 - smooth(0.0, 0.55, cx)) + 18 * fbm(5, 10, seed=31)[1450:1451, :]
cliff_top = np.broadcast_to(cliff_top, (H, W))
# cliff face drops away to the right of edge_x
face = (xx < edge_x + (yy - 1450) * 0.35)
cliff = (yy > cliff_top) & face
rock = lerp(col(18, 10, 26) * np.ones_like(img), col(60, 28, 52), (0.5 + 0.5 * fbm(6, 10, seed=32)) * smooth(1500, 1450, yy))
# warm rim light on the cliff top
rim = np.exp(-np.clip(yy - cliff_top, 0, None) / 6) * smooth(0.1, 0.55, cx)
rock += rim[..., None] * col(255, 140, 100) * 0.6
img = np.where(cliff[..., None], rock, img)

# figure standing near the cliff edge, back to us
FX, FY = 520.0, float(cliff_top[0, 520]) + 2
fig = np.zeros((H, W), bool)
# cloak (trapezoid)
h_c = 118
cy = (FY - yy) / h_c
half = 13 + 25 * (1 - cy)
fig |= (cy >= 0) & (cy <= 0.82) & (np.abs(xx - FX - 3 * (1 - cy)) < half)
# head
fig |= ((xx - FX) ** 2 + (yy - (FY - h_c * 0.9)) ** 2) < 14 ** 2
# cloak tail blowing right
tail = (yy > FY - 60) & (yy < FY - 6) & (xx > FX + 20) & (xx < FX + 20 + (yy - (FY - 60)) * 0.9)
fig |= tail
img = np.where(fig[..., None], col(8, 4, 14), img)
# rim light on the figure's right edge
fe = gaussian_filter(fig.astype(np.float32), 2) * (~fig)
img += (fe * (xx > FX))[..., None] * col(255, 150, 110) * 0.8

# ---- finishing ----------------------------------------------------------------
# soft bloom on the bright parts
lum = img.mean(-1)
bright = np.clip(img - 0.65, 0, None)
img += gaussian_filter(bright, (18, 18, 0)) * 0.9 + gaussian_filter(bright, (60, 60, 0)) * 0.5
# painterly: tiny directional smear + canvas texture
img = gaussian_filter(img, (1.2, 0.6, 0))
canvas = fbm(4, 120, seed=40) * 0.035
img *= (1 + canvas)[..., None]
# vignette
v = ((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2
img *= (1 - 0.7 * v)[..., None]
img = np.clip(img, 0, 1)

out = sys.argv[1] if len(sys.argv) > 1 else "painting"
np.save(out + ".npy", img.astype(np.float32))
Image.fromarray((img * 255 + 0.5).astype(np.uint8)).save(out + ".png")
print("wrote", out)
