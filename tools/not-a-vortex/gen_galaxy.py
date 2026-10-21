# Procedural Milky Way plate (face-on, ours): bar + bulge, four log-spiral arms (two major), warm gold star
# light with blue-white young clusters, pink H II knots, dark dust lanes on the arms' inner edges, a faint disc. North-up view (galaxy rotates
# clockwise, arms trail). The Sun sits at (-26,700, 0) ly in the Orion Spur between the Sagittarius and Perseus arms.
# Plate spans 110,000 ly. Run: python3 gen_galaxy.py  (writes assets/galaxy_plate.jpg)
import numpy as np
from PIL import Image, ImageFilter

N = 3072; SPAN = 110000.0
rng = np.random.default_rng(42)
xs = (np.arange(N, dtype=np.float32) + 0.5) / N * SPAN - SPAN / 2
X, Y = np.meshgrid(xs, -xs)                      # image up = +y
R = np.hypot(X, Y) + 1.0; TH = np.arctan2(Y, X)

def noise(res, sigma, seed):
    r = np.random.default_rng(seed); a = r.random((res, res)).astype(np.float32)
    im = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(sigma)).resize((N, N), Image.BICUBIC)
    v = np.asarray(im, np.float32) / 255; return (v - v.mean()) / (v.std() + 1e-6)
n1, n2, n3 = noise(384, 2, 1), noise(1024, 1.5, 2), noise(2048, 1.0, 3)

def arm(theta0, pitch_deg, w0, r0=11000):
    k = 1 / np.tan(np.radians(pitch_deg))
    th_arm = theta0 + np.log(np.maximum(R, 1) / r0) * k       # trailing for clockwise rotation
    d = np.angle(np.exp(1j * (TH - th_arm)))                  # wrapped angular offset
    perp = d * R / np.sqrt(1 + k * k)                         # distance across the arm (ly)
    w = w0 + 0.03 * R
    return perp, w

BAR = np.radians(27) + np.pi
col = np.zeros((N, N, 3), np.float32)
# disc and bulge
disc = np.exp(-R / 12000) * 0.22 * (1 + 0.3 * n1)
xb = X * np.cos(BAR) + Y * np.sin(BAR); yb = -X * np.sin(BAR) + Y * np.cos(BAR)
bar = np.exp(-(xb / 15000) ** 2 - (yb / 4200) ** 2) * 0.9
bulge = np.exp(-R / 2200) * 1.6 + np.exp(-R / 900) * 1.4
warm = np.array([1.0, 0.8, 0.56], np.float32); col += (disc + bar * (1 + 0.15 * n2) + bulge)[..., None] * warm
# arms: two major (Scutum-Centaurus, Perseus), two minor (Norma-Outer, Sagittarius-Carina)
young = np.array([1.0, 0.82, 0.55], np.float32); blue = np.array([0.62, 0.76, 1.0], np.float32); pink = np.array([1.0, 0.45, 0.62], np.float32)
dust = np.zeros((N, N), np.float32)
start = (R > 9000).astype(np.float32) * np.clip((R - 9000) / 4000, 0, 1) * np.exp(-np.maximum(R - 42000, 0) / 7000)
for th0, strength in [(BAR, 1.0), (BAR + np.pi, 1.0), (BAR + np.pi / 2, 0.38), (BAR + 3 * np.pi / 2, 0.38)]:
    perp, w = arm(th0, 13.5, 650)
    perp = perp + 500 * n1
    clump = 0.55 + 0.45 * (1 / (1 + np.exp(-(0.9 * n2 + 0.5 * n3)))) * 1.6
    clump *= np.clip(0.75 + 0.35 * n1, 0.2, 1.4) if strength < 1 else 1
    a = np.exp(-(perp / w) ** 2) * strength * start * clump
    col += a[..., None] * young * 0.7
    col += (a * np.clip(0.9 * n3 + 0.6 * n2 - 0.4, 0, None))[..., None] * blue * 0.55
    col += (np.exp(-(perp / (w * 2.6)) ** 2) * strength * start * 0.12)[..., None] * np.array([1.0, 0.85, 0.65], np.float32)
    dust = np.maximum(dust, np.exp(-((perp + 0.95 * w) / (0.6 * w)) ** 2) * strength * start * np.clip(0.75 + 0.35 * n1, 0, 1))
# Orion Spur: a short segment near the Sun
spur_r = 26700 + (TH - np.pi) * 0  # placeholder for shape below
ang = np.angle(np.exp(1j * (TH - np.pi)))
spur = np.exp(-((R - (26700 + ang * 26700 * 0.35) + 600 * n1) / 1100) ** 2) * np.exp(-(ang / 0.3) ** 2) * 0.4 * np.clip(0.4 + 0.8 * (0.6 * n2 + 0.4 * n3), 0, None)
col += (spur * np.clip(1 + 0.3 * n1, 0, None))[..., None] * (0.5 * young + 0.5 * blue)
# H II regions: pink knots strewn along the arms
knots = np.zeros((N, N), np.float32)
armmask = col.sum(-1) > 1.5
ys, xs_ = np.nonzero(armmask); pick = rng.choice(len(ys), size=min(2600, len(ys)), replace=False)
for y, x in zip(ys[pick], xs_[pick]): knots[y, x] += rng.uniform(1.0, 2.5)
knots = np.asarray(Image.fromarray(np.clip(knots * 120, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(2.2)), np.float32) / 255 * 5
col += knots[..., None] * pink * 3.0
# dust lanes darken the arms' inner edges and cross the bar's leading sides
col *= (1 - 0.5 * dust)[..., None]
col *= (1 - 0.35 * np.exp(-(yb / 1500 - 2.2) ** 2) * np.exp(-(xb / 12000) ** 2))[..., None]
col *= (1 - 0.35 * np.exp(-(yb / 1500 + 2.2) ** 2) * np.exp(-(xb / 12000) ** 2))[..., None]
# field stars (fine speckle)
sp = (rng.random((N, N)) > 0.9965).astype(np.float32) * rng.random((N, N)).astype(np.float32) * np.exp(-R / 30000)
col += sp[..., None] * 0.8
col = 1 - np.exp(-col * 1.0)                      # soft clamp
lum = col.mean(-1, keepdims=True); col = np.clip(lum + (col - lum) * 1.7, 0, None)   # restore saturation lost in the clamp
col *= np.clip((55000 - R) / 6000, 0, 1)[..., None]
Image.fromarray((np.clip(col, 0, 1) ** 0.95 * 255 + 0.5).astype(np.uint8)).save('assets/galaxy_plate.jpg', quality=93)
print('wrote assets/galaxy_plate.jpg')
