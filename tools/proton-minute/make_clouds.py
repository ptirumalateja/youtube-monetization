# Procedural cloud layer (equirectangular, 2048x1024), written to tex/clouds.png.
# 3D value-noise fbm sampled on the unit sphere so there is no seam at the date line,
# domain-warped for swirls, with fewer clouds in the subtropics like the real planet.
import numpy as np
from PIL import Image
from pathlib import Path

W, H = 2048, 1024
rng = np.random.default_rng(7)
G = 64
grid = rng.random((G, G, G)).astype(np.float32)

def vnoise(p):
    p = p * 1.0
    i = np.floor(p).astype(np.int64)
    f = p - i
    f = f * f * (3 - 2 * f)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (f[..., 0] if dx else 1 - f[..., 0]) * (f[..., 1] if dy else 1 - f[..., 1]) * (f[..., 2] if dz else 1 - f[..., 2])
                out = out + w * grid[(i[..., 0] + dx) % G, (i[..., 1] + dy) % G, (i[..., 2] + dz) % G]
    return out

def fbm(p, oct=6):
    s, a, tot = 0, 0.5, 0
    for _ in range(oct):
        s = s + a * vnoise(p); tot += a; p = p * 2.03 + 3.1; a *= 0.5
    return s / tot

lon = (np.arange(W) + 0.5) / W * 2 * np.pi - np.pi
lat = np.pi / 2 - (np.arange(H) + 0.5) / H * np.pi
LON, LAT = np.meshgrid(lon, lat)
P = np.stack([np.cos(LAT) * np.cos(LON), np.cos(LAT) * np.sin(LON), np.sin(LAT)], -1).astype(np.float32) * 3.0 + 20
warp = np.stack([fbm(P * 0.8 + 1.7, 4), fbm(P * 0.8 + 9.2, 4), fbm(P * 0.8 + 4.4, 4)], -1)
c = fbm(P + 2.2 * (warp - 0.5) + np.stack([LAT * 1.5] * 3, -1) * [0, 0, 1], 6)
latd = np.degrees(np.abs(LAT))
band = 0.62 + 0.25 * np.exp(-((latd - 55) / 18) ** 2) + 0.18 * np.exp(-(latd / 8) ** 2) - 0.12 * np.exp(-((latd - 25) / 8) ** 2)
v = np.clip((c * band - 0.31) / 0.24, 0, 1) ** 1.4
Path(__file__).with_name('tex').mkdir(exist_ok=True)
Image.fromarray((v * 255).astype(np.uint8), 'L').save(Path(__file__).with_name('tex') / 'clouds.png')
print('clouds.png', v.mean())
