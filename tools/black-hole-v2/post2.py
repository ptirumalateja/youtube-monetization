"""Grade one HDR frame from bh.c: foreground dust, bloom, filmic tone map, grain.

usage: post.py in.raw out.png W H frame_index [exposure]
"""
import os
import sys
import numpy as np
from PIL import Image

src, dst, W, H, fi = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
EXPO = float(sys.argv[6]) if len(sys.argv) > 6 else 1.0
FPS = 30.0
img = np.fromfile(src, dtype=np.float32).reshape(H, W, 3)


def resize(a, w, h):
    return np.stack([np.asarray(Image.fromarray(a[..., c]).resize((w, h), Image.BILINEAR)) for c in range(a.shape[2])], -1)


def blur(a, levels):
    """Wide soft glow: downsample pyramid, then upsample and sum with weights."""
    h, w = a.shape[:2]
    out = np.zeros_like(a)
    cur = a
    for lv, wt in enumerate(levels):
        cw, ch = max(cur.shape[1] // 2, 1), max(cur.shape[0] // 2, 1)
        cur = resize(cur, cw, ch)
        cur = resize(resize(cur, max(cw // 2, 1), max(ch // 2, 1)), cw, ch) * 0.5 + cur * 0.5
        out += resize(cur, w, h) * wt
    return out


# ---- foreground dust: two slow, outward-drifting layers (parallax of falling past dust) ----
def dust_tex(seed, n=1024):
    """Periodic 1/f noise (spectral synthesis), so the drifting layer tiles without seams."""
    rng = np.random.default_rng(seed)
    f = np.fft.fftfreq(n)
    k = np.sqrt(f[:, None] ** 2 + f[None, :] ** 2)
    k[0, 0] = 1.0
    spec = np.fft.fft2(rng.standard_normal((n, n))) * k ** -1.6 * np.exp(-(k * n / 260.0) ** 2)
    spec[0, 0] = 0
    acc = np.real(np.fft.ifft2(spec)).astype(np.float32)
    return (acc - acc.mean()) / acc.std()


DUST = None


def dust_layer(tex, t, zoom0, zrate, rot, ox, oy):
    n = tex.shape[0]
    s = zoom0 * np.exp(zrate * t)                # grows: we fly toward/through it
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W * 0.5, H * 0.42
    x = (xx - cx) / H / s
    y = (yy - cy) / H / s
    ca, sa = np.cos(rot * t), np.sin(rot * t)
    u = (x * ca - y * sa + ox) * n
    v = (x * sa + y * ca + oy) * n
    iu = np.mod(u, n).astype(np.int32)
    iv = np.mod(v, n).astype(np.int32)
    return tex[iv, iu]


t = fi / FPS
try:
    texA = np.load(os.path.join(os.path.dirname(os.path.abspath(dst)), "dustA.npy"))
    texB = np.load(os.path.join(os.path.dirname(os.path.abspath(dst)), "dustB.npy"))
except FileNotFoundError:
    texA, texB = dust_tex(7), dust_tex(11)
    np.save(os.path.join(os.path.dirname(os.path.abspath(dst)), "dustA.npy"), texA)
    np.save(os.path.join(os.path.dirname(os.path.abspath(dst)), "dustB.npy"), texB)

yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
rr = np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.42) / H * 1.1) ** 2)
edge = np.clip((rr - 0.22) / 0.45, 0, 1) ** 1.3  # dust lives toward the frame edges, not on the hole
la = dust_layer(texA, t, 1.0, 0.040, 0.004, 0.13, 0.71)
lb = dust_layer(texB, t, 0.55, 0.065, -0.006, 0.52, 0.29)
dA = np.clip((la - 0.35) / 1.4, 0, 1) * edge
dB = np.clip((lb - 0.55) / 1.3, 0, 1) * edge
# dark silhouettes with a faint warm/blue rim lit by the disk
dark = 1 - 0.62 * dA - 0.45 * dB
img = img * dark[..., None]
rim = (dA * (1 - dA) * 4) * edge
img += rim[..., None] * np.array([0.020, 0.012, 0.007], np.float32) * 0.6
img += (dB * (1 - dB) * 4)[..., None] * np.array([0.004, 0.008, 0.020], np.float32)

img *= EXPO
# ---- bloom ----
bright = np.maximum(img - 0.55, 0)
glow = blur(bright, [0.30, 0.30, 0.26, 0.22, 0.18, 0.14])
halo = blur(img, [0.0, 0.0, 0.0, 0.05, 0.07, 0.08])
img = img + glow * 0.45 + halo * 0.12

# ---- filmic tone map (ACES fit) + gentle grade ----
a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
x = img * 0.85
tm = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
# lift blacks toward deep navy so nothing is flat black
tm = tm + np.array([0.002, 0.003, 0.006], np.float32) * (1 - tm)
# vignette
vig = 1 - 0.32 * np.clip((rr - 0.25) / 0.55, 0, 1) ** 1.6
tm *= vig[..., None]
out = np.power(np.clip(tm, 0, 1), 1 / 2.2)
# ---- grain (also dithers away banding) ----
rng = np.random.default_rng(1000 + fi)
g = rng.standard_normal((H, W)).astype(np.float32)
lum = out.mean(-1, keepdims=True)
out = out + g[..., None] * (0.010 + 0.018 * np.sqrt(np.clip(lum, 0, 1)) * (1 - lum)) + rng.uniform(-0.5, 0.5, (H, W, 3)) / 255.0
Image.fromarray((np.clip(out, 0, 1) * 255 + 0.5).astype(np.uint8)).save(dst)
