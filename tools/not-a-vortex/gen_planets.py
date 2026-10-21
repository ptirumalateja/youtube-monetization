# Procedural planet maps (ours, no external imagery), equirectangular, x = longitude, y = latitude (north up).
# Colours follow true-colour spacecraft imagery (Juno/Cassini/Voyager re-processed, MESSENGER, Viking);
# features are placed where the real ones are (Great Red Spot at 22 S, Saturn's hexagon at 78 N,
# Valles Marineris, Syrtis Major, polar caps, Neptune's dark spot). Saturn's rings use the measured ring radii.
# Run: python3 gen_planets.py   (writes assets/*.jpg|png, about 1 minute)
import numpy as np
from PIL import Image

OUT = 'assets/'

def grid(W, H):
    lon = (np.arange(W, dtype=np.float32) + 0.5) / W * 2 * np.pi - np.pi
    lat = np.pi / 2 - (np.arange(H, dtype=np.float32) + 0.5) / H * np.pi
    LON, LAT = np.meshgrid(lon, lat)
    P = np.stack([np.cos(LAT) * np.cos(LON), np.cos(LAT) * np.sin(LON), np.sin(LAT)], -1).astype(np.float32)
    return LON, LAT, P

def vnoise(p, f, seed):  # 3D value noise, smooth trilinear on a 96^3 lattice
    r = np.random.default_rng(seed); n = 96; g = r.random((n, n, n), dtype=np.float32)
    q = (p * f + 1000.0) % n; i = np.floor(q).astype(np.int32); t = q - i; t = t * t * (3 - 2 * t)
    i1 = (i + 1) % n; out = np.zeros(p.shape[:-1], np.float32)
    for dx in (0, 1):
        ix = i1[..., 0] if dx else i[..., 0]; wx = t[..., 0] if dx else 1 - t[..., 0]
        for dy in (0, 1):
            iy = i1[..., 1] if dy else i[..., 1]; wy = t[..., 1] if dy else 1 - t[..., 1]
            for dz in (0, 1):
                iz = i1[..., 2] if dz else i[..., 2]; wz = t[..., 2] if dz else 1 - t[..., 2]
                out += wx * wy * wz * g[ix, iy, iz]
    return out

def fbm(p, f, oct, seed, gain=0.5):
    s, a, tot = 0, 1.0, 0
    for k in range(oct): s = s + a * vnoise(p + 17.3 * k, f * 2 ** k, seed + k); tot += a; a *= gain
    return s / tot

def ss(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1); return t * t * (3 - 2 * t)

def save(rgb, name, q=93):
    Image.fromarray((np.clip(rgb, 0, 1) * 255 + 0.5).astype(np.uint8)).save(OUT + name, quality=q)
    print('wrote', name)

def band_colour(latdeg, table):
    """table: list of (lat_from, lat_to, rgb) north to south; smooth 1.2 deg blends."""
    col = np.zeros(latdeg.shape + (3,), np.float32); wsum = np.zeros(latdeg.shape, np.float32)
    for a, b, c in table:
        lo, hi = min(a, b), max(a, b); w = ss(lo - 0.8, lo + 0.8, latdeg) * (1 - ss(hi - 0.8, hi + 0.8, latdeg)) + 1e-6
        col += w[..., None] * np.array(c, np.float32); wsum += w
    return col / wsum[..., None]

def gas_giant(W, H, table, seed, stretch, turb, warp, LON=None, LAT=None, P=None):
    if P is None: LON, LAT, P = grid(W, H)
    latd = np.degrees(LAT)
    # zonal jets: alternate eastward/westward shear, so eddies are smeared into streaks along each band
    q = P * np.array([1, 1, stretch], np.float32)
    w1 = fbm(q, 3.0, 5, seed) - 0.5
    shear = np.sin(np.radians(latd) * 9.0)
    lat_w = latd + warp * w1 * 6.0
    col = band_colour(lat_w, table)
    # longitude-warped turbulence for festoons and eddies
    LON2 = LON + shear * 0.35 + w1 * 0.9
    q2 = np.stack([np.cos(LAT) * np.cos(LON2), np.cos(LAT) * np.sin(LON2), np.sin(LAT) * stretch], -1).astype(np.float32)
    t = fbm(q2, 6.0, 6, seed + 50) - 0.5
    col = col * (1 + turb * t[..., None] * np.array([1.0, 0.95, 0.85], np.float32))
    return col, LON, LAT, P, latd

def angdist(LON, LAT, lon0, lat0):  # great-circle angle in degrees
    return np.degrees(np.arccos(np.clip(np.sin(LAT) * np.sin(lat0) + np.cos(LAT) * np.cos(lat0) * np.cos(LON - lon0), -1, 1)))

def oval(LON, LAT, lon0, lat0, a_deg, b_deg):  # elliptical distance (1 = edge), a along longitude
    dl = (LON - lon0 + np.pi) % (2 * np.pi) - np.pi
    return np.sqrt((np.degrees(dl) * np.cos(lat0) / a_deg) ** 2 + (np.degrees(LAT - lat0) / b_deg) ** 2)

# ---------------- Jupiter ----------------
def jupiter():
    W, H = 4096, 2048
    C = lambda r, g, b: (r / 255, g / 255, b / 255)
    zone, belt, neb, polar = C(238, 226, 205), C(190, 150, 112), C(165, 112, 78), C(150, 145, 140)
    table = [(90, 66, C(130, 128, 128)), (66, 52, polar), (52, 47, C(182, 165, 145)), (47, 43, C(205, 192, 175)), (43, 38, C(176, 150, 122)),
             (38, 34, C(220, 205, 182)), (34, 30, C(170, 128, 96)), (30, 25, C(232, 218, 196)), (25, 22, C(160, 108, 80)),
             (22, 18, zone), (18, 7, neb), (7, -7, C(240, 228, 206)), (-7, -19, belt), (-19, -27, zone),
             (-27, -32, C(178, 140, 108)), (-32, -38, C(228, 214, 192)), (-38, -43, C(185, 160, 132)), (-43, -52, C(208, 195, 178)),
             (-52, -66, polar), (-66, -90, C(128, 126, 128))]
    col, LON, LAT, P, latd = gas_giant(W, H, table, 3, 5.0, 0.42, 1.0)
    # blue-grey festoons hanging from the NEB's southern edge into the equatorial zone
    fest = np.clip(np.sin(LON * 12 + 3 * (fbm(P, 4, 3, 77) - 0.5)) * 0.5 + 0.5, 0, 1) ** 6
    fest *= ss(1.5, 5.5, latd) * (1 - ss(6.5, 8.5, latd))
    col = col * (1 - 0.45 * fest[..., None]) + 0.45 * fest[..., None] * np.array([0.42, 0.45, 0.52], np.float32)
    # the Great Red Spot (22 S, ~16,000 km wide) with a pale collar (the "Red Spot Hollow") and an internal swirl
    lon0, lat0 = np.radians(25.0), np.radians(-22.5)
    d = oval(LON, LAT, lon0, lat0, 11.5, 6.6)
    ang = np.arctan2(np.degrees(LAT - lat0) / 6.6, np.degrees((LON - lon0 + np.pi) % (2 * np.pi) - np.pi) * np.cos(lat0) / 11.5)
    sw = fbm(np.stack([np.cos(ang + 5 * (1 - d)), np.sin(ang + 5 * (1 - d)), d * 3], -1).astype(np.float32), 2.5, 4, 91) - 0.5
    grs = (1 - ss(0.75, 1.0, d))
    red = np.array([0.78, 0.40, 0.26], np.float32) * (0.9 + 0.5 * sw[..., None]) * (1 - 0.18 * ss(0.5, 0.0, d)[..., None])
    collar = np.exp(-((d - 1.18) / 0.16) ** 2)
    col = col * (1 - grs[..., None]) + red * grs[..., None]
    col = col + 0.18 * collar[..., None] * (np.array([0.98, 0.95, 0.9], np.float32) - col)
    # Oval BA (33 S) and a string of small white ovals
    rng = np.random.default_rng(5)
    for lon_d, lat_d, a, b, c in [(-60, -33, 3.6, 2.6, (0.86, 0.62, 0.52))] + [(rng.uniform(-180, 180), rng.choice([-41, -36, 40, 45, -48]), 1.6, 1.1, (0.97, 0.95, 0.92)) for _ in range(14)]:
        dd = oval(LON, LAT, np.radians(lon_d), np.radians(lat_d), a, b); m = (1 - ss(0.7, 1.0, dd))[..., None]
        col = col * (1 - m) + m * np.array(c, np.float32) * (0.92 + 0.08 * (1 - dd[..., None]))
    # polar mottling: cyclone clusters
    pol = ss(58, 75, np.abs(latd)); cyc = fbm(P, 14, 4, 123)
    col = col * (1 - 0.25 * pol[..., None] * (cyc[..., None] - 0.4))
    save(col ** 1.05, 'jupiter.jpg')

# ---------------- Saturn ----------------
def saturn():
    W, H = 4096, 2048
    C = lambda r, g, b: (r / 255, g / 255, b / 255)
    table = [(90, 74, C(120, 132, 150)), (74, 62, C(160, 158, 150)), (62, 50, C(196, 178, 140)), (50, 40, C(214, 192, 148)),
             (40, 30, C(205, 178, 128)), (30, 20, C(226, 204, 158)), (20, 12, C(212, 182, 128)), (12, -12, C(236, 214, 166)),
             (-12, -22, C(214, 186, 134)), (-22, -32, C(228, 206, 160)), (-32, -45, C(206, 180, 132)), (-45, -60, C(214, 196, 158)),
             (-60, -90, C(188, 176, 150))]
    col, LON, LAT, P, latd = gas_giant(W, H, table, 21, 7.0, 0.13, 0.5)
    # the north polar hexagon (78 N), a slightly darker blue-grey band with straight sides, and the polar vortex
    hexr = np.radians(90 - 78.0)
    colat = np.pi / 2 - LAT
    th = (LON % (np.pi / 3)) - np.pi / 6
    hexedge = hexr * np.cos(np.pi / 6) / np.cos(th)
    hx = np.exp(-((colat - hexedge) / np.radians(1.4)) ** 2) * (LAT > 0)
    col = col * (1 - 0.35 * hx[..., None]) + 0.35 * hx[..., None] * np.array([0.42, 0.5, 0.6], np.float32)
    inner = (colat < hexedge) & (LAT > 0)
    col[inner] = col[inner] * 0.85 + 0.15 * np.array([0.35, 0.45, 0.58], np.float32)
    vort = np.exp(-(colat / np.radians(2.2)) ** 2)[..., None]
    col = col * (1 - 0.5 * vort) + 0.5 * vort * np.array([0.25, 0.3, 0.38], np.float32)
    save(col, 'saturn.jpg')

def saturn_rings():
    # radial profile from 66,900 km (D ring) to 141,000 km (outside the F ring), 4096 samples; rgb + alpha
    N = 4096; r = np.linspace(66900, 141000, N)
    rng = np.random.default_rng(9)
    fine = np.zeros(N)
    for k in range(60):  # ringlets and density waves
        f = rng.uniform(0.002, 0.2); fine += rng.uniform(0.2, 1) / (1 + 60 * f) * np.sin(r * f + rng.uniform(0, 6.28))
    fine = (fine - fine.min()) / (fine.max() - fine.min())
    a = np.zeros(N); col = np.zeros((N, 3))
    def seg(lo, hi, alpha, c, jitter):
        m = (r >= lo) & (r < hi); a[m] = np.clip(alpha + jitter * (fine[m] - 0.5), 0, 1); col[m] = c
    seg(66900, 74510, 0.03, (0.55, 0.52, 0.5), 0.02)                    # D ring
    seg(74658, 92000, 0.16, (0.52, 0.47, 0.42), 0.14)                   # C ring (plateaus)
    seg(92000, 117580, 0.9, (0.88, 0.80, 0.67), 0.18)                   # B ring, nearly opaque
    seg(117580, 122170, 0.07, (0.5, 0.47, 0.44), 0.08)                  # Cassini Division
    seg(122170, 136775, 0.62, (0.80, 0.76, 0.70), 0.18)                 # A ring
    m = (r > 92000) & (r < 99000); a[m] *= 0.75 + 0.25 * ss(92000, 99000, r[m])  # B inner edge
    for lo, hi in [(117680, 118030), (133423, 133745), (136485, 136527)]:  # Huygens, Encke, Keeler gaps
        m = (r >= lo) & (r < hi); a[m] = 0.01
    m = np.abs(r - 140220) < 60; a[m] = 0.55; col[m] = (0.85, 0.82, 0.78)   # F ring core
    m = np.abs(r - 140220) < 600; a[m] = np.maximum(a[m], 0.06 * np.exp(-((r[m] - 140220) / 300) ** 2))
    col = col * (0.88 + 0.24 * fine[:, None])
    img = np.concatenate([np.clip(col, 0, 1), a[:, None]], 1)
    img = np.repeat(img[None], 8, 0)
    Image.fromarray((img * 255 + 0.5).astype(np.uint8), 'RGBA').save(OUT + 'saturn_rings.png'); print('wrote saturn_rings.png')

# ---------------- Uranus and Neptune ----------------
def uranus():
    W, H = 2048, 1024
    C = lambda r, g, b: (r / 255, g / 255, b / 255)
    table = [(90, 60, C(196, 228, 230)), (60, 40, C(176, 218, 224)), (40, 10, C(166, 210, 220)), (10, -20, C(160, 204, 216)),
             (-20, -45, C(168, 210, 220)), (-45, -90, C(176, 214, 222))]
    col, *_ = gas_giant(W, H, table, 41, 6.0, 0.035, 0.3)
    save(col, 'uranus.jpg')

def neptune():
    W, H = 2048, 1024
    C = lambda r, g, b: (r / 255, g / 255, b / 255)
    # re-processed true colour: a paler azure than the famous saturated Voyager prints, a little bluer than Uranus
    table = [(90, 60, C(120, 160, 205)), (60, 35, C(100, 145, 200)), (35, 10, C(92, 138, 198)), (10, -15, C(88, 134, 196)),
             (-15, -30, C(80, 124, 190)), (-30, -50, C(96, 142, 200)), (-50, -70, C(84, 128, 190)), (-70, -90, C(110, 150, 200))]
    col, LON, LAT, P, latd = gas_giant(W, H, table, 61, 6.0, 0.12, 0.6)
    d = oval(LON, LAT, np.radians(-40), np.radians(-20), 15, 6.5); m = (1 - ss(0.6, 1.0, d))[..., None]
    col = col * (1 - 0.5 * m) + 0.5 * m * np.array([0.12, 0.2, 0.42], np.float32)        # Great Dark Spot
    for lon0, lat0, a, b in [(-25, -15, 9, 1.4), (-55, -24, 7, 1.0), (60, -42, 22, 1.2), (130, 28, 30, 1.0), (-120, 35, 18, 0.9), (20, -55, 6, 1.6)]:
        d = oval(LON, LAT, np.radians(lon0), np.radians(lat0), a, b) + 0.6 * (fbm(P, 9, 3, int(lon0) + 500) - 0.5)
        m = (1 - ss(0.5, 1.0, d))[..., None]; col = col * (1 - 0.8 * m) + 0.8 * m * np.array([0.93, 0.96, 1.0], np.float32)  # methane cirrus
    save(col, 'neptune.jpg')

# ---------------- Mars ----------------
def mars():
    W, H = 4096, 2048
    LON, LAT, P = grid(W, H); latd, lond = np.degrees(LAT), np.degrees(LON)
    base = fbm(P, 2.2, 6, 301); det = fbm(P, 18, 5, 333)
    dark = ss(0.5, 0.62, base + 0.18 * (latd < 0) * ss(-60, -10, latd) * (1 - ss(-10, 10, latd)) - 0.1 * ss(10, 50, latd))
    # Syrtis Major (~290 E i.e. -70, 8 N) and Mare Acidalium (~-30, 45 N) darkened explicitly
    for lo, la, a, b in [(-70, 8, 9, 14), (-30, 46, 16, 8), (-160, -20, 26, 9), (-55, -22, 30, 7)]:
        dd = oval(LON, LAT, np.radians(lo), np.radians(la), a, b); dark = np.maximum(dark, (1 - ss(0.5, 1.15, dd + 0.5 * (det - 0.5))) * 0.85)
    bright = np.array([0.80, 0.52, 0.32], np.float32); ochre = np.array([0.70, 0.42, 0.25], np.float32); darkc = np.array([0.36, 0.24, 0.17], np.float32)
    col = bright * (1 - ss(0.3, 0.7, base))[..., None] + ochre * ss(0.3, 0.7, base)[..., None]
    col = col * (1 - dark[..., None]) + darkc * dark[..., None]
    col = col * (0.85 + 0.3 * det[..., None])
    # Valles Marineris: a 4,000 km canyon system just south of the equator
    vm = np.exp(-((latd + 8 + 0.9 * np.sin(np.radians(lond) * 5) + 0.6 * (det - 0.5)) / 1.5) ** 2) * ss(-112, -96, lond) * (1 - ss(-52, -40, lond))
    vm = np.maximum(vm, 0.6 * np.exp(-((latd + 12.5 + 0.5 * np.sin(np.radians(lond) * 7)) / 0.9) ** 2) * ss(-90, -80, lond) * (1 - ss(-60, -52, lond)))
    col = col * (1 - 0.33 * vm[..., None])
    # Tharsis volcanoes: Olympus Mons (18 N, -134) and the three Tharsis Montes, with summit calderas
    for lo, la, rr in [(-134, 18.6, 5.5), (-113, -0.8, 2.6), (-104, 11.8, 2.6), (-121, -8.8, 2.4)]:
        dd = angdist(LON, LAT, np.radians(lo), np.radians(la)) / rr
        col = col * (1 + 0.14 * np.exp(-dd ** 2)[..., None] - 0.35 * np.exp(-(dd / 0.18) ** 2)[..., None])
    # polar caps: a ragged residual north cap, and a small offset south cap
    ncap = ss(78, 83, latd + 3 * (fbm(P, 10, 4, 404) - 0.5) * 2)
    sd = angdist(LON, LAT, np.radians(-40), np.radians(-87)); scap = 1 - ss(4, 6.5, sd + 2 * (fbm(P, 12, 3, 505) - 0.5))
    cap = np.maximum(ncap, scap)[..., None]
    col = col * (1 - cap) + cap * np.array([0.96, 0.94, 0.92], np.float32)
    save(col, 'mars.jpg')

# ---------------- Mercury (cratered, with young bright ray craters) ----------------
def cratered(W, H, seed, base_col, n_crater, rays, name, nrm_name, maria_amt=0.0):
    LON, LAT, P = grid(W, H)
    rng = np.random.default_rng(seed)
    fine = fbm(P, 9, 5, seed + 11); height = 0.15 * fine
    maria = ss(0.55, 0.68, fbm(P, 1.6, 4, seed + 1)) * maria_amt
    alb = 0.62 + 0.3 * (fine - 0.5) - 0.3 * maria
    for k in range(n_crater):
        r = 0.010 * (1 - rng.random()) ** (-0.55); r = min(r, 0.2)
        u = rng.normal(size=3); c = (u / np.linalg.norm(u)).astype(np.float32)
        clat = np.arcsin(c[2]); dlat = r * 2.2
        y0 = max(0, int((np.pi / 2 - (clat + dlat)) / np.pi * H)); y1 = min(H, int((np.pi / 2 - (clat - dlat)) / np.pi * H) + 1)
        sub = P[y0:y1]; d = np.arccos(np.clip(sub @ c, -1, 1)) / r
        bowl = np.where(d < 1, (d * d - 1) * 0.9, 0); rim = 0.35 * np.exp(-((d - 1) / 0.18) ** 2)
        ej = np.where(d > 1, 0.25 * np.exp(-(d - 1) * 2.2), 0); age = rng.random() ** 2
        height[y0:y1] += (bowl + rim) * r * 6 * (0.4 + 0.6 * age)
        alb[y0:y1] += ej * 0.35 * age ** 3
    for k in range(rays):  # young craters with long bright ray systems
        u = rng.normal(size=3); c = (u / np.linalg.norm(u)).astype(np.float32)
        d = np.arccos(np.clip(P @ c, -1, 1)); east = np.cross(c, [0, 0, 1]); east /= np.linalg.norm(east) + 1e-9; north = np.cross(east, c)
        az = np.arctan2(P @ north, P @ east)
        spokes = np.clip(np.sin(az * rng.integers(9, 17) + 4 * (vnoise(P, 3, seed + k) - 0.5)), 0, 1) ** 8
        alb += 0.35 * spokes * np.exp(-d / rng.uniform(0.15, 0.35)) * (d > 0.012) + 0.5 * np.exp(-(d / 0.012) ** 2)
    alb = np.clip(alb, 0.1, 1.2)
    rgb = (alb[..., None] * np.array(base_col, np.float32)) ** 0.95
    save(rgb, name)
    gy, gx = np.gradient(height)
    gx = gx / (2 * np.pi / W) / np.maximum(np.cos(LAT), 0.05); gy = -gy / (np.pi / H)
    east = np.stack([-np.sin(LON), np.cos(LON), np.zeros_like(LON)], -1)
    north = np.stack([-np.sin(LAT) * np.cos(LON), -np.sin(LAT) * np.sin(LON), np.cos(LAT)], -1)
    n = P - 0.9 * (gx[..., None] * east + gy[..., None] * north); n /= np.linalg.norm(n, axis=-1, keepdims=True)
    Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8)).save(OUT + nrm_name); print('wrote', nrm_name)

# ---------------- Venus (the cloud deck in visible light: cream, soft streaks, the faint Y) ----------------
def venus():
    W, H = 2048, 1024
    LON, LAT, P = grid(W, H); latd = np.degrees(LAT)
    q = P * np.array([1, 1, 3], np.float32)
    w = fbm(q, 2.5, 5, 701) - 0.5
    y = np.exp(-((latd - 18 * np.abs(np.sin((LON + w * 1.5) * 0.5)) * np.sign(np.sin(LON + 0.6))) / 9) ** 2) * ss(-35, 0, -np.abs(latd) + 35)
    col = np.array([0.93, 0.86, 0.68], np.float32) * (1 - 0.07 * y[..., None] + 0.1 * w[..., None])
    col = col * (1 - 0.06 * ss(50, 80, np.abs(latd))[..., None])
    save(col, 'venus.jpg')

# ---------------- Galilean moons, Titan, Triton (small in frame: 1024 maps) ----------------
def small_moons():
    W, H = 1024, 512
    LON, LAT, P = grid(W, H)
    n = fbm(P, 5, 5, 801); n2 = fbm(P, 16, 4, 802)
    io = np.array([0.92, 0.84, 0.45], np.float32) * (0.85 + 0.3 * n[..., None])
    for k in range(40):  # volcanic patera: dark spots with red/orange haloes
        rng = np.random.default_rng(900 + k); lo, la = rng.uniform(-np.pi, np.pi), rng.uniform(-1.2, 1.2)
        d = angdist(LON, LAT, lo, la); io = io * (1 - 0.6 * np.exp(-(d / 1.5) ** 2)[..., None]) + 0.25 * np.exp(-(d / 5) ** 2)[..., None] * np.array([0.6, 0.2, 0.05], np.float32)
    save(io, 'io.jpg')
    lin = np.clip(np.abs(np.sin(LON * 7 + 9 * (n - 0.5)) * np.sin(LAT * 5 + 7 * (n2 - 0.5))), 0, 1)
    eu = np.array([0.88, 0.85, 0.80], np.float32) * (1 - 0.35 * (lin < 0.08)[..., None] * np.array([0.6, 0.9, 1.1], np.float32)) * (0.9 + 0.15 * n2[..., None])
    save(eu, 'europa.jpg')
    ga = np.array([0.55, 0.5, 0.45], np.float32) * (0.75 + 0.5 * ss(0.4, 0.6, n)[..., None]) * (0.9 + 0.2 * n2[..., None])
    save(ga, 'ganymede.jpg')
    ca = np.array([0.36, 0.32, 0.28], np.float32) * (0.85 + 0.3 * n2[..., None]) + 0.4 * (n2 > 0.72)[..., None]
    save(ca, 'callisto.jpg')
    ti = np.array([0.85, 0.6, 0.3], np.float32) * (0.95 + 0.08 * n[..., None])
    save(ti, 'titan.jpg')
    tr = np.array([0.8, 0.74, 0.72], np.float32) * (0.85 + 0.25 * n2[..., None]); tr[LAT < -0.3] *= np.array([1.05, 0.95, 0.9], np.float32)
    save(tr, 'triton.jpg')

if __name__ == '__main__':
    import sys
    which = sys.argv[1:] or ['jupiter', 'saturn', 'rings', 'uranus', 'neptune', 'mars', 'mercury', 'moon', 'venus', 'moons']
    for w in which:
        if w == 'jupiter': jupiter()
        if w == 'saturn': saturn()
        if w == 'rings': saturn_rings()
        if w == 'uranus': uranus()
        if w == 'neptune': neptune()
        if w == 'mars': mars()
        if w == 'mercury': cratered(4096, 2048, 31, (0.62, 0.58, 0.54), 5200, 7, 'mercury.jpg', 'mercury_normal.png')
        if w == 'moon': cratered(2048, 1024, 7, (0.66, 0.65, 0.63), 2600, 2, 'moon.jpg', 'moon_normal.png', maria_amt=1.0)
        if w == 'venus': venus()
        if w == 'moons': small_moons()
