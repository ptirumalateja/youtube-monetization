# Procedural Moon textures (ours, no external imagery): albedo with maria and ray-free craters, and an
# object-space normal map from the crater height field. Equirectangular 2048x1024. Run: python3 gen_moon.py
import numpy as np
from PIL import Image
W, H = 2048, 1024
rng = np.random.default_rng(7)
lon = (np.arange(W) + 0.5) / W * 2 * np.pi - np.pi
lat = np.pi / 2 - (np.arange(H) + 0.5) / H * np.pi
LON, LAT = np.meshgrid(lon, lat)
P = np.stack([np.cos(LAT) * np.cos(LON), np.cos(LAT) * np.sin(LON), np.sin(LAT)], -1)

def vnoise(p, f, seed):  # 3D value noise, trilinear
    r = np.random.default_rng(seed); n = 64; g = r.random((n, n, n))
    q = (p * f) % n; i = np.floor(q).astype(int); t = q - i; t = t * t * (3 - 2 * t)
    out = 0
    for dx in (0, 1):
        for dy in (0, 1):
            for dz in (0, 1):
                w = (t[..., 0] if dx else 1 - t[..., 0]) * (t[..., 1] if dy else 1 - t[..., 1]) * (t[..., 2] if dz else 1 - t[..., 2])
                out = out + w * g[(i[..., 0] + dx) % n, (i[..., 1] + dy) % n, (i[..., 2] + dz) % n]
    return out
def fbm(p, f, oct, seed):
    s, a, tot = 0, 1, 0
    for k in range(oct): s += a * vnoise(p + 17.3 * k, f * 2 ** k, seed + k); tot += a; a *= 0.5
    return s / tot

maria = fbm(P, 1.6, 4, 1)
maria = np.clip((maria - 0.52) / 0.12, 0, 1); maria = maria * maria * (3 - 2 * maria)
# keep most maria on the near side (+x hemisphere), like the real Moon
maria *= np.clip(0.35 + 0.9 * P[..., 0], 0, 1)
fine = fbm(P, 9, 5, 11)
height = 0.15 * fine
alb = 0.62 + 0.3 * (fine - 0.5) - 0.3 * maria * (0.8 + 0.4 * fbm(P, 5, 3, 21))

# craters: power-law radii, bowl + raised rim + a little ejecta brightening
N = 2600
for k in range(N):
    r = 0.012 * (1 - rng.random()) ** (-0.55); r = min(r, 0.22)
    u = rng.normal(size=3); c = u / np.linalg.norm(u)
    clat, clon = np.arcsin(c[2]), np.arctan2(c[1], c[0])
    dlat = r * 2.2; y0 = max(0, int((np.pi / 2 - (clat + dlat)) / np.pi * H)); y1 = min(H, int((np.pi / 2 - (clat - dlat)) / np.pi * H) + 1)
    sub = P[y0:y1]; d = np.arccos(np.clip(sub @ c, -1, 1)) / r
    m = d < 2.2
    if not m.any(): continue
    bowl = np.where(d < 1, (d * d - 1) * 0.9, 0)
    rim = 0.35 * np.exp(-((d - 1) / 0.18) ** 2)
    ej = np.where(d > 1, 0.25 * np.exp(-(d - 1) * 2.2), 0)
    age = rng.random() ** 2  # most craters are old and soft
    height[y0:y1] += (bowl + rim) * r * 6 * (0.4 + 0.6 * age)
    alb[y0:y1] += ej * 0.35 * age ** 3 * (1 - 0.6 * maria[y0:y1])

alb = np.clip(alb, 0.12, 1)
Image.fromarray((np.clip(alb, 0, 1) ** 0.9 * 255).astype(np.uint8)).save('assets/moon_albedo.jpg', quality=92)
# object-space normal from the height gradient
gy, gx = np.gradient(height)
gx = gx / (2 * np.pi / W) / np.maximum(np.cos(LAT), 0.05); gy = -gy / (np.pi / H)
east = np.stack([-np.sin(LON), np.cos(LON), np.zeros_like(LON)], -1)
north = np.stack([-np.sin(LAT) * np.cos(LON), -np.sin(LAT) * np.sin(LON), np.cos(LAT)], -1)
k = 0.9
n = P - k * (gx[..., None] * east + gy[..., None] * north)
n /= np.linalg.norm(n, axis=-1, keepdims=True)
Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save('assets/moon_normal.png')
print('moon textures written')
