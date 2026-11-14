"""Assets for the Kepler-vs-Earth cut: alien planet map, moon maps, nebula backdrops, fonts."""
import os, sys
import numpy as np
import cv2
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from assets import load_all, TEX  # noqa: E402

TEX2 = os.environ.get("JB_TEX2", os.path.join(os.path.dirname(TEX), "tex2"))
Image.MAX_IMAGE_PIXELS = None


def _kepler_maps(base):
    """Kepler-452b: an ocean world with its own golden continents (grown from a shifted cloud field)."""
    cl = base["earth_cloud"][..., 0].astype(np.float32) / 255
    cl = np.roll(cl[::-1, ::-1], cl.shape[1] // 3, axis=1)
    big = cv2.GaussianBlur(cl, (0, 0), 18)
    fine = cl - cv2.GaussianBlur(cl, (0, 0), 4)
    landf = big + 0.25 * fine
    land = np.clip((landf - 0.355) * 9, 0, 1)
    coast = np.clip(1 - np.abs(landf - 0.355) * 18, 0, 1)
    h, w = land.shape
    lat = np.abs(np.linspace(-1, 1, h))[:, None]
    depth = np.clip((0.355 - landf) * 4, 0, 1)
    sea = (np.array([0.22, 0.80, 0.82]) * (1 - depth[..., None]) + np.array([0.06, 0.52, 0.66]) * depth[..., None])
    sea = sea + np.array([0.35, 0.30, 0.10]) * coast[..., None] * 0.5
    tex = np.clip(fine * 3 + 0.5, 0, 1)
    landc = (np.array([0.78, 0.70, 0.40]) * (0.75 + 0.35 * tex[..., None])
             + np.array([-0.25, -0.05, -0.12]) * np.clip(big - 0.5, 0, 1)[..., None] * 2)
    col = sea * (1 - land[..., None]) + landc * land[..., None]
    ice = np.clip((lat - 0.86) * 12, 0, 1)
    col = col * (1 - ice[..., None]) + np.array([0.92, 0.95, 0.96]) * ice[..., None]
    return (np.clip(col, 0, 1) * 255).astype(np.uint8), None, None


def load():
    base = load_all()
    kc = os.path.join(TEX2, "kepler_day3.png")
    if not os.path.exists(kc):
        d, _, _ = _kepler_maps(base)
        Image.fromarray(d).save(kc)
    kday = np.ascontiguousarray(np.asarray(Image.open(kc).convert("RGB")))
    kcloud = np.ascontiguousarray(np.roll(base["earth_cloud"][:, ::-1], base["earth_cloud"].shape[1] // 2, axis=1))
    knight = np.zeros_like(base["earth_night"])
    moon = np.ascontiguousarray(np.asarray(Image.open(os.path.join(TEX2, "2k_moon.jpg")).convert("RGB")))
    io = moon.astype(np.float32) / 255
    io = io.mean(2, keepdims=True) * np.array([1.25, 1.05, 0.55]) + 0.08
    io = (np.clip(io, 0, 1) * 255).astype(np.uint8)
    neb = {}
    for k, f in (("pillars", "pillars.jpg"), ("orion", "neb5.jpg"), ("carina", "neb2.jpg")):
        p = os.path.join(TEX2, f)
        if os.path.exists(p):
            neb[k] = cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    base.update(kday=kday, knight=knight, kcloud=kcloud, moon=moon, io=np.ascontiguousarray(io), nebimg=neb,
                font_it=os.path.join(TEX2, "Merriweather-Italic.ttf"))
    return base
