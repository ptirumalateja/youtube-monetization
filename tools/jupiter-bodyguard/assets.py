"""Texture loading + procedural nebula for the Jupiter bodyguard reel."""
import os
import numpy as np
from PIL import Image
import cv2

TEX = os.environ.get("JB_TEX", "/tmp/claude-0/-home-user/be075317-9b13-5dc2-bdf1-585b08c9f335/scratchpad/tex")
Image.MAX_IMAGE_PIXELS = None


def _load(name, mode="RGB"):
    return np.ascontiguousarray(np.asarray(Image.open(os.path.join(TEX, name)).convert(mode)))


def nebula(w=4096, h=2048, seed=7):
    """Soft coloured nebula clouds in equirect space (uint8)."""
    rng = np.random.default_rng(seed)

    def fbm(oct0=3, n=7, pers=0.55):
        acc = np.zeros((h, w), np.float32)
        amp, tot = 1.0, 0.0
        for o in range(n):
            s = 2 ** (o + oct0)
            g = rng.random((s // 2 + 1, s + 1)).astype(np.float32)
            g[:, -1] = g[:, 0]
            acc += cv2.resize(g, (w, h), interpolation=cv2.INTER_CUBIC) * amp
            tot += amp
            amp *= pers
        return acc / tot

    a = fbm(); b = fbm(); c = fbm(2, 6, 0.6)
    band = np.exp(-((np.linspace(-1, 1, h)[:, None] - 0.08 * np.sin(np.linspace(0, 6.283, w))[None]) / 0.35) ** 2)
    m1 = np.clip((a - 0.48) * 3.2, 0, 1) ** 2 * (0.35 + 0.65 * band)
    m2 = np.clip((b - 0.50) * 3.0, 0, 1) ** 2 * (0.25 + 0.75 * band)
    m3 = np.clip((c - 0.52) * 3.5, 0, 1) ** 2.5
    col = (m1[..., None] * np.array([0.35, 0.10, 0.55]) +   # violet
           m2[..., None] * np.array([0.05, 0.30, 0.45]) +   # teal
           m3[..., None] * np.array([0.50, 0.16, 0.38]))    # rose
    col = np.clip(col, 0, 1)
    return (col * 255).astype(np.uint8)


def sky_color(w=8192, h=4096):
    """Colourised Milky Way: smooth the 8-bit map, lift it, tint core gold and arms violet/blue."""
    a = np.asarray(Image.open(os.path.join(TEX, "8k_stars_milky_way.jpg")).convert("RGB")).astype(np.float32) / 255
    a = cv2.resize(a, (w, h), interpolation=cv2.INTER_AREA)
    lum = a.mean(2)
    diffuse = cv2.GaussianBlur(lum, (0, 0), 22)
    diffuse = np.clip((diffuse - 0.003) * 9.0, 0, 1) ** 1.1
    core = cv2.GaussianBlur(lum, (0, 0), 60)
    core = np.clip(core / core.max(), 0, 1) ** 1.5
    neb = nebula(w, h).astype(np.float32) / 255
    band = np.clip(cv2.GaussianBlur(lum, (0, 0), 120) * 25, 0, 1)
    col = (diffuse[..., None] * (core[..., None] * np.array([1.0, 0.72, 0.45]) +
                                 (1 - core[..., None]) * np.array([0.55, 0.55, 1.0])) * 0.55
           + neb * (0.03 + 0.97 * band[..., None] ** 1.5) * 0.55)
    pts = np.clip(lum - cv2.GaussianBlur(lum, (0, 0), 3) - 0.02, 0, 1) * 6
    col += pts[..., None] * np.array([0.9, 0.95, 1.0])
    return (np.clip(col, 0, 1) ** (1 / 2.2) * 255).astype(np.uint8)


def load_all():
    cache = os.path.join(TEX, "nebula.png")
    if not os.path.exists(cache):
        Image.fromarray(nebula()).save(cache)
    sc = os.path.join(TEX, "sky_color.png")
    if not os.path.exists(sc):
        Image.fromarray(sky_color()).save(sc)
    ring = np.ascontiguousarray(np.asarray(Image.open(os.path.join(TEX, "8k_saturn_ring_alpha.png")).convert("RGBA")))
    return dict(
        earth_day=_load("8k_earth_daymap.jpg"),
        earth_night=_load("8k_earth_nightmap.jpg"),
        earth_cloud=_load("8k_earth_clouds.jpg", "L")[..., None].copy(),
        jup=_load("8k_jupiter.jpg"),
        sat=_load("8k_saturn.jpg"),
        ring=ring,
        sky=_load("sky_color.png"),
        neb=_load("nebula.png"),
    )
