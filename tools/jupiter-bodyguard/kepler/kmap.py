"""Build the Kepler-452b day map: alien continents (from the cloud-grown kepler_day3 mask) filled with
Earth's real terrain detail (high-pass of the day map) over a green/gold palette, turquoise seas with shallows."""
import os, sys
import numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, HERE)
from assets import load_all
from kassets import TEX2


def build(out, preview=None):
    b = load_all()
    w, h = 4096, 2048
    k3 = np.asarray(Image.open(os.path.join(TEX2, "kepler_day3.png")).convert("RGB")).astype(np.float32) / 255
    k3 = cv2.resize(k3, (w, h), interpolation=cv2.INTER_AREA)
    land = np.clip((k3[..., 0] - 0.40) * 4, 0, 1)
    land = cv2.GaussianBlur(land, (0, 0), 0.8)
    d = b["earth_day"].astype(np.float32) / 255
    d = cv2.resize(d, (w, h), interpolation=cv2.INTER_AREA)
    d = np.roll(d, 1700, axis=1)
    lum = d.mean(2)
    hp = lum - cv2.GaussianBlur(lum, (0, 0), 6)
    cl = cv2.resize(b["earth_cloud"][..., 0].astype(np.float32) / 255, (w, h), interpolation=cv2.INTER_AREA)
    cl = np.roll(cl[::-1], 900, axis=1)
    hp2 = cl - cv2.GaussianBlur(cl, (0, 0), 4)
    rng = np.random.default_rng(452)
    def fbm(scale):
        n = rng.random((h // scale + 2, w // scale + 2)).astype(np.float32)
        return cv2.resize(n, (w + scale * 2, h + scale * 2), interpolation=cv2.INTER_CUBIC)[:h, :w]
    veg = np.clip(fbm(96) * 0.7 + fbm(24) * 0.3, 0, 1)
    green = np.array([0.20, 0.36, 0.12]); gold = np.array([0.66, 0.58, 0.30]); pale = np.array([0.80, 0.78, 0.55])
    t = veg[..., None]
    base = green * (1 - t) + gold * t
    base = base * (1 - np.clip((t - 0.7) * 3, 0, 1)) + pale * np.clip((t - 0.7) * 3, 0, 1)
    # inland is greener, coasts get a pale beach rim
    inl = cv2.GaussianBlur(land, (0, 0), 14)
    base = base * (0.85 + 0.25 * inl[..., None])
    det = 1 + hp[..., None] * 3.0 + hp2[..., None] * 0.8
    landc = np.clip(base * det, 0, 1)
    depth = np.clip(1 - cv2.GaussianBlur(land, (0, 0), 40) * 2.5, 0, 1)
    sea = np.array([0.16, 0.66, 0.76]) * (1 - depth[..., None] * 0.6) + np.array([0.03, 0.28, 0.44]) * depth[..., None] * 0.6
    shallow = np.clip(cv2.GaussianBlur(land, (0, 0), 6) * 2.2, 0, 1) * (1 - land)
    sea = sea + np.array([0.22, 0.30, 0.14]) * shallow[..., None]
    sea = sea * (1 + hp2[..., None] * 0.25)
    col = sea * (1 - land[..., None]) + landc * land[..., None]
    lat = np.abs(np.linspace(-1, 1, h))[:, None]
    ice = np.clip((lat - 0.88 + fbm(64) * 0.05) * 14, 0, 1)[..., None]
    col = col * (1 - ice) + np.array([0.90, 0.94, 0.96]) * ice
    Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8)).save(out)
    if preview:
        cv2.imwrite(preview, (np.clip(col[700:1300, 1500:2700][..., ::-1], 0, 1) * 255).astype(np.uint8))


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
