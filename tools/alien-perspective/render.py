"""Alien Perspective reel (Slow Light, 12 s loop). CPU renderer: numpy + PIL, ink-wash look, no plates.

python3 render.py OUTDIR [frame ...]     renders PNG frames (all 360 if none given, 4 processes)

Shot plan (video seconds):
  0.0-2.3   PAYOFF   early hominin under a huge Andromeda: "ALIENS IN ANDROMEDA SEE EARTH LIKE THIS."
  2.3-4.6   WHY      alien eye, Earth reflected in the slit pupil, push in to the dot
  4.6-8.6   HOW LONG ride the light beam out from Earth; era panes fly past, odometer only goes up
                     (NOW city -> 4,500 pyramids -> 300,000 first modern humans -> 2,500,000)
  8.0-8.3   held breath, last pane (the opening shot) approaches, then fills the frame
  8.6-10.0  REVEAL   same shot as frame 0, bigger: "NO MODERN HUMANS YET."
  10.0-12.0 FLIP     the ancestor becomes a modern stargazer (city glow on the horizon):
                     "TODAY'S LIGHT GETS THERE IN 2.5 MILLION YEARS.", then back to the ancestor = frame 0
"""
import math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter
from scipy.interpolate import PchipInterpolator

W, H, FPS, DUR = 1080, 1920, 30, 12.0
NF = int(DUR * FPS)
M = 140                      # canvas margin for parallax layers
CW, CH = W + 2 * M, H + 2 * M
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.environ.get('AP_CACHE', '/tmp/ap_cache')
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'

INK = np.array([0.025, 0.03, 0.06])
CREAM = np.array([0.97, 0.92, 0.80])
GOLD = np.array([0.98, 0.74, 0.36])
TEAL = np.array([0.22, 0.52, 0.62])
VIOLET = np.array([0.60, 0.56, 0.92])
RED = (214, 62, 48)

T_EYE, T_BEAM, T_REVEAL, T_FLIP = 2.3, 4.6, 8.6, 10.0


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def fbm(h, w, seed, sig=(90, 30, 10, 3), wt=(1, .55, .3, .15)):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    for s, k in zip(sig, wt):
        out += k * gaussian_filter(r.standard_normal((h, w)).astype(np.float32), s) * (2 * math.sqrt(math.pi) * s)
    return out / sum(wt)


def to8(a):
    return (np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8)


# ----------------------------------------------------------------------------------- figure rig
# units: 1.0 = modern standing height. x forward is -x (figure faces left, toward the galaxy)
HOM = dict(hip=(.02, -.42), kf=(-.07, -.235), af=(-.04, -.035), tf=(-.14, 0), kb=(.07, -.22), ab=(.10, -.035), tb=(.02, 0),
           neck=(-.125, -.665), head=(-.165, -.725), sh=(-.10, -.645), ef=(-.17, -.50), hf=(-.19, -.33),
           eb=(-.04, -.50), hb=(-.035, -.34), gaze=(-.72, -.70))
MOD = dict(hip=(0, -.50), kf=(-.03, -.265), af=(-.035, -.035), tf=(-.135, 0), kb=(.04, -.265), ab=(.06, -.035), tb=(-.035, 0),
           neck=(.0, -.84), head=(.012, -.912), sh=(.012, -.81), ef=(.10, -.665), hf=(-.045, -.56),
           eb=(.085, -.66), hb=(-.03, -.565), gaze=(-.78, -.63))


def ell_poly(c, rx, ry, ang, n=40):
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    x, y = rx * np.cos(a), ry * np.sin(a)
    ca, sa = math.cos(ang), math.sin(ang)
    return [(c[0] + ca * xx - sa * yy, c[1] + sa * xx + ca * yy) for xx, yy in zip(x, y)]


def draw_figure(dr, ox, oy, s, m, hood=None, stone=None, spear=False):
    """Silhouette into ImageDraw dr (fill 255). origin = feet, s = px per unit, m = morph 0 hominin -> 1 modern."""
    hood = m if hood is None else hood
    stone = (1 - m) if stone is None else stone
    P = {k: (ox + s * lerp(HOM[k][0], MOD[k][0], m), oy + s * lerp(HOM[k][1], MOD[k][1], m)) for k in HOM if k != 'gaze'}
    g = np.array([lerp(HOM['gaze'][0], MOD['gaze'][0], m), lerp(HOM['gaze'][1], MOD['gaze'][1], m)])
    g /= np.linalg.norm(g)
    dn = np.array([g[1], -g[0]])              # toward the chin
    W_ = lambda a, b: s * lerp(a, b, m)

    def cap(a, b, w):
        dr.line([a, b], fill=255, width=int(w))
        for p in (a, b):
            dr.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=255)
    # legs
    for k, a, f in (('b', 'kb', 'ab'), ('f', 'kf', 'af')):
        cap(P['hip'], P[a], W_(.072, .078)); cap(P[a], P[f], W_(.046, .056)); cap(P[f], P['t' + k], W_(.032, .036))
    # torso: tapered quad hip -> neck
    hp_, nk = np.array(P['hip']), np.array(P['neck'])
    ax = nk - hp_; L = np.linalg.norm(ax); ax /= L; pr = np.array([-ax[1], ax[0]])
    wh, wc = W_(.105, .10) / 2, W_(.13, .14) / 2
    quad = [tuple(hp_ + pr * wh), tuple(hp_ - pr * wh), tuple(hp_ + ax * L * .7 - pr * wc), tuple(nk - pr * wc * .7),
            tuple(nk + pr * wc * .7), tuple(hp_ + ax * L * .7 + pr * wc)]
    dr.polygon(quad, fill=255)
    # belly / chest mass (hominin barrel chest)
    mid = hp_ + ax * L * .45
    dr.polygon(ell_poly(tuple(mid - pr * s * .01 * (1 - m)), W_(.085, .06), L * .32, math.atan2(ax[1], ax[0]) + math.pi / 2), fill=255)
    cap(P['hip'], tuple(hp_ + ax * L * .2), W_(.11, .10))
    # neck + head
    hc = np.array(P['head'])
    cap(P['neck'], tuple(hc - g * s * .01), W_(.055, .05))
    ang = math.atan2(g[1], g[0])
    dr.polygon(ell_poly(tuple(hc), s * lerp(.07, .060, m), s * lerp(.05, .068, m), ang), fill=255)
    # face: hominin muzzle + brow ridge, modern nose + chin
    dr.polygon(ell_poly(tuple(hc + g * s * .045 + dn * s * .022), s * .046 * (1 - m) + 1, s * .034 * (1 - m) + 1, ang), fill=255)
    dr.polygon(ell_poly(tuple(hc + g * s * .052 - dn * s * .022), s * .022 * (1 - m) + 1, s * .012 * (1 - m) + 1, ang), fill=255)
    dr.polygon(ell_poly(tuple(hc + g * s * .062 - dn * s * .004), s * .016 * m + 1, s * .009 * m + 1, ang), fill=255)
    dr.polygon(ell_poly(tuple(hc + g * s * .035 + dn * s * .048), s * .022 * m + 1, s * .018 * m + 1, ang), fill=255)
    # hominin: low skull vault with hair at the back, heavy brow
    if m < 0.99:
        dr.polygon(ell_poly(tuple(hc - g * s * .03 - dn * s * .012), s * .05 * (1 - m) + 1, s * .045 * (1 - m) + 1, ang), fill=255)
    # hood (modern)
    if hood > 0.01:
        dr.polygon(ell_poly(tuple(hc - g * s * .03 + dn * s * .02), s * .075 * hood, s * .07 * hood, ang), fill=255)
    # arms
    for e, h in (('eb', 'hb'), ('ef', 'hf')):
        cap(P['sh'], P[e], W_(.05, .06)); cap(P[e], P[h], W_(.04, .052))
        hr = s * lerp(.034, .028, m)
        dr.ellipse([P[h][0] - hr, P[h][1] - hr, P[h][0] + hr, P[h][1] + hr], fill=255)
    if stone > 0.01:   # Oldowan-style hand stone
        hf = P['hf']
        dr.polygon(ell_poly((hf[0] - s * .012, hf[1] + s * .022), s * .04 * stone, s * .03 * stone, .5, 9), fill=255)
    if spear:
        hf = P['hf']
        dr.line([(hf[0] - s * .05, hf[1] + s * .45), (hf[0] + s * .08, hf[1] - s * .62)], fill=255, width=max(2, int(s * .018)))
    return P


def figure_layer(m, s=820, rough=None, ss=3):
    """RGBA (premultiplied float) silhouette with rim light, on a local box; returns (rgb, a, x0, y0) in ridge-canvas px."""
    bw, bh = int(s * .62), int(s * 1.12)
    img = Image.new('L', (bw * ss, bh * ss), 0)
    dr = ImageDraw.Draw(img)
    fx, fy = bw * .55, bh * .97
    draw_figure(dr, fx * ss, fy * ss, s * ss, m)
    a = np.asarray(img.resize((bw, bh), Image.LANCZOS), np.float32) / 255
    rough = (1 - m) if rough is None else rough
    if rough > 0.01:   # hair / fur on the hominin edge
        n = FUR[:bh, :bw]
        ab = gaussian_filter(a, 1.6)
        fur = np.maximum(np.clip((ab - 0.5 + 0.30 * n) * 3.2 + 0.5, 0, 1) * (gaussian_filter(a, 3) > 0.08), (ab > 0.85).astype(np.float32))
        a = fur * rough + a * (1 - rough)
    sh = np.zeros_like(a); dx, dy = 3, 4
    sh[dy:, dx:] = a[:-dy, :-dx]
    rim = gaussian_filter(np.clip(a - sh, 0, 1), 1.0) * a
    rgb = INK[None, None, :] * a[..., None] + rim[..., None] * (0.75 * CREAM + 0.25 * VIOLET)[None, None, :] * 0.6
    return rgb, a, 700 + M - fx, 1478 + M - fy


# ----------------------------------------------------------------------------------- assets
def galaxy_tex(S=1500, seed=11):
    y, x = np.mgrid[-1:1:S * 1j, -1:1:S * 1j].astype(np.float32)
    rot = math.radians(-33)
    xr = x * math.cos(rot) + y * math.sin(rot)
    yr = -x * math.sin(rot) + y * math.cos(rot)
    u, v = xr, yr / 0.30
    r = np.sqrt(u * u + v * v) + 1e-4
    th = np.arctan2(v, u)
    n = fbm(S, S, seed, (40, 12, 4), (1, .6, .3))
    arms = 0.55 + 0.45 * np.cos(2 * (th - 3.4 * np.log(r + 0.06)) + n * 0.9)
    disk = np.exp(-r / 0.21) * arms * (1 + 0.25 * n)
    dust = 1 - 0.75 * np.exp(-((r - 0.40) / 0.035) ** 2) * (yr > -0.01) - 0.55 * np.exp(-((r - 0.56) / 0.03) ** 2) * (yr > 0)
    disk *= np.clip(dust, 0.15, 1) * (r < 0.98)
    rb = np.sqrt(xr ** 2 + (yr / 0.62) ** 2)
    bulge = 1.6 * np.exp(-(rb / 0.055) ** 2) + 0.55 * np.exp(-rb / 0.11)
    col = bulge[..., None] * (0.6 * CREAM + 0.4 * GOLD) + disk[..., None] * (0.55 * VIOLET + 0.35 * TEAL + 0.25 * CREAM)
    # star-forming knots along the arms
    rr = np.random.default_rng(seed + 1)
    knots = np.zeros((S, S), np.float32)
    k = rr.integers(0, S, (9000, 2))
    keep = arms[k[:, 0], k[:, 1]] * np.exp(-r[k[:, 0], k[:, 1]] / 0.35) > rr.random(9000) * 0.9
    knots[k[keep, 0], k[keep, 1]] = rr.random(keep.sum()) * 3
    knots = gaussian_filter(knots, 1.2)
    col += knots[..., None] * np.array([0.75, 0.82, 1.0])
    # satellites (M32 tight, M110 elongated)
    for cx, cy, sx, sy, b in ((0.10, -0.26, .018, .016, 0.8),):
        col += (b * np.exp(-((x - cx) / sx) ** 2 - ((y - cy) / sy) ** 2))[..., None] * CREAM
    lum = col.mean(-1)
    col += gaussian_filter(lum, S * 0.03)[..., None] * np.array([0.35, 0.33, 0.55]) * 1.4
    return np.clip(col * 0.85, 0, 1.4)


def star_layer(h, w, seed, n, bright=1.0):
    r = np.random.default_rng(seed)
    a = np.zeros((h, w), np.float32)
    ys, xs = r.integers(0, h, n), r.integers(0, w, n)
    b = r.pareto(2.2, n) * 0.25 + 0.02
    np.add.at(a, (ys, xs), b)
    a = gaussian_filter(a, 0.9) * 6
    big = b > 1.2
    for y0, x0, bb in zip(ys[big], xs[big], b[big]):   # a few cross glints
        L = int(min(30, 8 + bb * 6))
        y1, y2, x1, x2 = max(0, y0 - L), min(h, y0 + L), max(0, x0 - L), min(w, x0 + L)
        a[y1:y2, x0] += np.exp(-np.abs(np.arange(y1, y2) - y0) / (L / 3)) * 0.25 * bb
        a[y0, x1:x2] += np.exp(-np.abs(np.arange(x1, x2) - x0) / (L / 3)) * 0.25 * bb
    return a * bright


def ridge_y(x):
    return 1478 + 0.0016 * (x - 700) ** 2 * (1 + 0.35 * np.sign(x - 700)) * 0.12 + 18 * np.sin(x / 61) + 9 * np.sin(x / 23 + 1)


def build_assets():
    os.makedirs(CACHE, exist_ok=True)
    f = CACHE + '/assets.npz'
    if os.path.exists(f):
        return dict(np.load(f))
    A = {}
    yy = np.arange(CH)[:, None] / CH
    xx = np.arange(CW)[None, :]
    # sky: navy ink wash, teal toward the horizon
    w = fbm(CH, CW, 1)
    g = np.clip((yy - 0.15) / 0.62, 0, 1) ** 1.6
    sky = (np.array([0.020, 0.028, 0.065]) * (1 - g[..., None]) + np.array([0.10, 0.16, 0.24]) * g[..., None])
    sky = sky * (1 + 0.28 * w[..., None]) + 0.02 * np.clip(w, 0, None)[..., None] * VIOLET
    sky += star_layer(CH, CW, 2, 1400)[..., None] * CREAM * (1 - 0.7 * g[..., None])
    A['sky'] = sky.astype(np.float32)
    # galaxy, placed upper left, huge (artistic; tagged NOT TO SCALE)
    A['gal'] = galaxy_tex().astype(np.float32)
    # far hills (savanna plain + distant acacias)
    xq = xx[0].astype(np.float32)
    hz = 1335 + M + 16 * np.sin(xq / 97 + 1) + 9 * np.sin(xq / 41 + 2) + 4 * np.sin(xq / 13) + 24 * np.sin(xq / 260)
    ys = np.arange(CH)[:, None]
    a = np.clip(ys - hz[None, :] + 0.5, 0, 1).astype(np.float32)
    im = Image.fromarray(to8(a)); dr = ImageDraw.Draw(im)
    r = np.random.default_rng(4)
    for _ in range(7):
        x0 = r.uniform(0, CW); y0 = hz[int(min(CW - 1, x0))]; s = r.uniform(18, 34)
        dr.line([(x0, y0), (x0 + s * .1, y0 - s * 1.1)], fill=255, width=3)
        dr.ellipse([x0 - s * 1.1, y0 - s * 1.35, x0 + s * 1.2, y0 - s * .95], fill=255)
    a = np.asarray(im, np.float32) / 255
    haze = np.exp(-np.clip(ys - hz[None, :], 0, None) / 60)
    col = np.array([0.035, 0.045, 0.075]) * (1 + 0.25 * fbm(CH, CW, 5)[..., None]) + haze[..., None] * np.array([0.05, 0.08, 0.11])
    A['far'] = np.dstack([col * a[..., None], a]).astype(np.float32)
    # city glow for "today" (additive, fades in with the morph)
    cg = np.exp(-((ys - hz[None, :] + 10) / 55) ** 2) * np.exp(-((xx - 260 - M) / 330) ** 2)
    lights = np.zeros((CH, CW), np.float32)
    for _ in range(420):
        x0 = int(r.normal(260 + M, 220)) % CW; y0 = int(hz[x0] + r.uniform(1, 26))
        if 0 <= y0 < CH: lights[y0, x0] += r.uniform(.5, 2)
    lights = gaussian_filter(lights, 0.8) * 4
    A['city'] = (cg[..., None] * GOLD * 0.30 + lights[..., None] * GOLD).astype(np.float32)
    # ridge + acacia (mid layer)
    xs = np.arange(CW) - M
    ry = ridge_y(xs) + M
    a = np.clip(ys - ry[None, :] + 0.5, 0, 1).astype(np.float32)
    im = Image.fromarray(to8(a)); dr = ImageDraw.Draw(im)
    tx, ty = 1075 + M, ridge_y(np.array([1075.]))[0] + M + 8
    dr.polygon([(tx - 16, ty), (tx + 18, ty), (tx + 2, ty - 470), (tx - 12, ty - 470)], fill=255)
    for bx, by, ex, ey, wdt in ((tx - 5, ty - 450, tx - 120, ty - 640, 14), (tx - 5, ty - 450, tx + 90, ty - 670, 14),
                                (tx - 60, ty - 550, tx - 230, ty - 670, 9), (tx + 40, ty - 560, tx + 210, ty - 640, 9),
                                (tx - 120, ty - 640, tx - 160, ty - 690, 6), (tx + 90, ty - 670, tx + 60, ty - 715, 6)):
        dr.line([(bx, by), (ex, ey)], fill=255, width=wdt)
    for _ in range(140):   # flat umbrella canopy
        cx = r.uniform(tx - 270, tx + 270); cy = ty - 690 + r.normal(0, 14) + abs(cx - tx) * 0.06
        rx, ryy = r.uniform(30, 85), r.uniform(9, 22)
        dr.ellipse([cx - rx, cy - ryy, cx + rx, cy + ryy], fill=255)
    for _ in range(90):    # grass tufts on the ridge
        x0 = r.uniform(0, CW); y0 = ridge_y(np.array([x0 - M]))[0] + M + 4; hh = r.uniform(10, 34)
        dr.line([(x0, y0), (x0 + r.uniform(-8, 8), y0 - hh)], fill=255, width=2)
    a = np.asarray(im, np.float32) / 255
    a = np.clip((gaussian_filter(a, 1.0) - 0.5 + 0.35 * fbm(CH, CW, 6, (2, 1), (1, .5))) * 2.4 + 0.5, 0, 1) * (a > 0.02) + a * 0
    a = np.maximum(a, np.asarray(im, np.float32) / 255 * (np.asarray(im) > 250))
    sh = np.zeros_like(a); sh[3:, 3:] = a[:-3, :-3]
    rim = gaussian_filter(np.clip(a - sh, 0, 1), 1.2) * a
    col = INK * (1 + 0.6 * fbm(CH, CW, 7, (20, 4), (1, .5))[..., None] * 0.3) + rim[..., None] * (0.6 * CREAM + 0.4 * VIOLET) * 0.4
    A['ridge'] = np.dstack([col * a[..., None], a]).astype(np.float32)
    # foreground grass, swaying (drawn per frame from blade list)
    A['blades'] = np.stack([r.uniform(-60, W + 60, 70), r.uniform(1730, 1960, 70), r.uniform(120, 330, 70),
                            r.uniform(5, 13, 70), r.uniform(0, 6.28, 70), r.uniform(-.35, .35, 70)], 1).astype(np.float32)
    A['paper'] = (1 + 0.035 * fbm(H, W, 8, (40, 6, 1.2), (1, .6, .8))).astype(np.float32)
    A['fur'] = fbm(1100, 800, 9, (1.4, .8), (1, .6)).astype(np.float32)
    A['space'] = (fbm(H + 400, W + 400, 10, (160, 50, 14), (1, .6, .3))).astype(np.float32)
    np.savez(f, **A)
    return A


A = build_assets()
FUR = A['fur']
GAL = A['gal']


# ----------------------------------------------------------------------------------- compositing helpers
def warp(layer, zoom, pivot, shift, p, size=(W, H)):
    """Sample a canvas-space float layer into the frame. zoom about frame-space pivot, parallax factor p."""
    zf = 1 + (zoom - 1) * p
    a = 1 / zf
    cx = M + pivot[0] * (1 - a) - shift[0] * p
    cy = M + pivot[1] * (1 - a) - shift[1] * p
    return affine(layer, (a, 0, cx, 0, a, cy), size)


def affine(arr, data, size):
    chans = []
    for c in range(arr.shape[2]):
        ch = Image.fromarray(arr[..., c].astype(np.float32), 'F')
        chans.append(np.asarray(ch.transform(size, Image.AFFINE, data, resample=Image.BILINEAR), np.float32))
    return np.dstack(chans)


def over(dst, rgba):
    a = rgba[..., 3:4]
    return dst * (1 - a) + rgba[..., :3]


def paste_over(dst, rgb, a, x0, y0):
    """premultiplied rgb, alpha a at integer-ish pos (x0,y0) in dst coords (clipped)."""
    h, w = a.shape
    x0, y0 = int(round(x0)), int(round(y0))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if X1 <= X0 or Y1 <= Y0:
        return
    sa = a[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0, None]
    dst[Y0:Y1, X0:X1] = dst[Y0:Y1, X0:X1] * (1 - sa) + rgb[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]


# galaxy canvas (additive): place galaxy texture into a sky-sized canvas once
def galaxy_canvas():
    f = CACHE + '/galcanvas.npy'
    if os.path.exists(f):
        return np.load(f)
    g = np.zeros((CH, CW, 3), np.float32)
    S = 1350
    im = np.dstack([np.asarray(Image.fromarray(GAL[..., c], 'F').resize((S, S), Image.LANCZOS)) for c in range(3)])
    cx, cy = 400 + M, 640 + M
    x0, y0 = cx - S // 2, cy - S // 2
    X0, Y0 = max(0, x0), max(0, y0)
    X1, Y1 = min(CW, x0 + S), min(CH, y0 + S)
    g[Y0:Y1, X0:X1] = im[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]
    np.save(f, g)
    return g


GALC = galaxy_canvas()


def render_ridge(t, zoom, m, pivot=(640, 980), shift=(0, 0), city=0.0):
    sky = warp(A['sky'] + GALC, zoom, pivot, shift, 0.35)
    img = sky
    if city > 0.01:
        img = img + city * warp(A['city'], zoom, pivot, shift, 0.6)
    img = over(img, warp(A['far'], zoom, pivot, shift, 0.6))
    # mid: ridge + figure on one canvas
    mid = A['ridge'].copy()
    rgb, a, fx, fy = figure_layer(m)
    breathe = 1.5 * math.sin(t * 2 * math.pi / 3.0)
    tmp = mid[..., :3]
    paste_over(tmp, rgb, a, fx, fy + breathe * 0)
    ma = mid[..., 3]
    h, w = a.shape; x0, y0 = int(round(fx)), int(round(fy))
    ma[y0:y0 + h, x0:x0 + w] = np.maximum(ma[y0:y0 + h, x0:x0 + w], a)
    img = over(img, warp(mid, zoom, pivot, shift, 1.0))
    # foreground grass
    gi = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(gi)
    zf = 1 + (zoom - 1) * 1.35
    for bx, by, hh, ww, ph, lean in A['blades']:
        sway = 0.10 * math.sin(t * 2 * math.pi / 2.4 + ph) + lean
        px = pivot[0] + (bx - pivot[0]) * zf - shift[0] * 1.35
        py = pivot[1] + (by - pivot[1]) * zf - shift[1] * 1.35
        pts = []
        for k in range(7):
            u = k / 6
            pts.append((px + math.sin(sway * u * 1.4) * hh * zf * u, py - math.cos(sway * u) * hh * zf * u))
        for k in range(6):
            dr.line([pts[k], pts[k + 1]], fill=255, width=max(1, int(ww * zf * (1 - k / 6.5))))
    ga = np.asarray(gi, np.float32)[..., None] / 255
    img = img * (1 - ga) + ga * INK * 0.6
    return img


# ----------------------------------------------------------------------------------- alien eye
def vnoise(x, y, seed=0):
    xi, yi = np.floor(x), np.floor(y)
    xf, yf = x - xi, y - yi
    def h(i, j):
        v = np.sin(i * 127.1 + j * 311.7 + seed * 74.7) * 43758.5453
        return v - np.floor(v)
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    return lerp(lerp(h(xi, yi), h(xi + 1, yi), u), lerp(h(xi, yi + 1), h(xi + 1, yi + 1), u), v)


R_EARTH = np.array([0.03, -0.20])          # Earth's reflection, eye units (iris radius 1)
ER = 380.0
_r = np.random.default_rng(21)
IRIS_K = np.arange(3, 140)
IRIS_A = _r.random(len(IRIS_K)) / np.sqrt(IRIS_K)
IRIS_P = _r.random(len(IRIS_K)) * 6.28
_n = 500
EYE_STARS = np.stack([_r.normal(0, .5, _n), _r.normal(0, .5, _n), _r.pareto(2.5, _n) * .2 + .05], 1)
# reflected Milky Way band across the cornea
_band = _r.uniform(-1.4, 1.4, 700)
EYE_STARS = np.vstack([EYE_STARS, np.stack([_band, -0.35 * _band + _r.normal(0, .09, 700) + 0.05, _r.pareto(3, 700) * .12 + .03], 1)])


def render_eye(t):
    u = (t - T_EYE) / (T_BEAM - T_EYE)
    Z = math.exp(lerp(0.0, math.log(48.0), u ** 3.2))
    C = np.array([W / 2, 1000.0])
    S0 = C + ER * R_EARTH
    Sp = S0 + (np.array([W / 2, 1000.0]) - S0) * ease(min(1, u * 1.6))
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    ex = R_EARTH[0] + (xs - Sp[0]) / (ER * Z)
    ey = R_EARTH[1] + (ys - Sp[1]) / (ER * Z)
    r = np.sqrt(ex * ex + ey * ey) + 1e-6
    th = np.arctan2(ey, ex)
    img = np.zeros((H, W, 3), np.float32)
    # iris: radial fibres, gold near pupil to teal outside
    fib = np.zeros_like(r)
    for k, a, p in zip(IRIS_K[::3], IRIS_A[::3], IRIS_P[::3]):
        fib += a * np.sin(k * th + p + 2.0 * r)
    fib = 0.5 + 0.5 * np.tanh(fib * 1.6)
    crypt = vnoise(th * 9, r * 7, 3)
    base = np.clip(1 - r, 0, 1)[..., None] * GOLD * 0.9 + np.clip(r, 0, 1)[..., None] * TEAL * 0.8
    iris = base * (0.35 + 0.75 * fib[..., None]) * (0.7 + 0.5 * crypt[..., None])
    iris *= (1 - 0.8 * np.exp(-((r - 1.0) / 0.06) ** 2))[..., None]          # limbal ring
    img += iris * (r < 1.04)[..., None]
    # outer: glossy dark sclera / skin with scales
    sc = np.abs(np.sin(9 * ex + 4.5 * ey)) * np.abs(np.sin(9 * ex - 4.5 * ey))
    skin = (0.05 + 0.10 * vnoise(ex * 6, ey * 6, 5) + 0.06 * sc)[..., None] * np.array([0.35, 0.55, 0.6])
    img = np.where((r < 1.04)[..., None], img, skin)
    # slit pupil, dilating as we push in
    pw = lerp(0.12, 0.22, ease(u * 1.2))
    pupil = np.clip((1 - (np.abs(ex) / (pw * np.sqrt(np.clip(1 - (ey / 0.98) ** 2, 1e-4, 1)))) ) * 30, 0, 1) * (np.abs(ey) < .98)
    img = img * (1 - pupil[..., None]) + pupil[..., None] * np.array([0.012, 0.016, 0.035])
    # eyelids (almond opening)
    open_ = 1.08 * np.clip(1 - (ex / 2.3) ** 2, 0, 1)
    lid = np.clip((np.abs(ey) - open_) * ER * Z / 8, 0, 1)
    lidedge = np.exp(-((np.abs(ey) - open_) * ER * Z / 10) ** 2)
    img = img * (1 - lid[..., None]) + lid[..., None] * skin * 0.8
    img += lidedge[..., None] * np.array([0.25, 0.32, 0.34]) * 0.5
    # reflections: Milky Way band + stars on the cornea, Earth dot in the pupil, window highlight
    st = np.zeros((H, W), np.float32)
    sx = Sp[0] + (EYE_STARS[:, 0] - R_EARTH[0]) * ER * Z
    sy = Sp[1] + (EYE_STARS[:, 1] - R_EARTH[1]) * ER * Z
    ok = (sx > 0) & (sx < W - 1) & (sy > 0) & (sy < H - 1)
    np.add.at(st, (sy[ok].astype(int), sx[ok].astype(int)), EYE_STARS[ok, 2])
    st = gaussian_filter(st, 1.0 + 0.04 * Z) * 5
    img += st[..., None] * CREAM * 0.8 * (lid < .5)[..., None]
    d = np.sqrt((xs - Sp[0]) ** 2 + (ys - Sp[1]) ** 2)
    er = 0.018 * ER * Z
    disc = np.clip((er - d) / 1.5 + 0.5, 0, 1)
    shade = np.clip(0.55 + 0.6 * ((xs - Sp[0]) * -0.6 + (ys - Sp[1]) * -0.8) / (er + 1e-3), 0.08, 1.2)
    clouds = vnoise((xs - Sp[0]) / (er * .35 + 1e-3), (ys - Sp[1]) / (er * .35 + 1e-3), 8)
    earth = np.array([0.25, 0.55, 0.95]) * (1 - 0.6 * clouds[..., None]) + clouds[..., None] * 0.6 * CREAM * (clouds > .55)[..., None]
    img = img * (1 - disc[..., None]) + disc[..., None] * earth * shade[..., None]
    img += np.exp(-(d / (er * 2.6 + 3)) ** 2)[..., None] * np.array([0.25, 0.45, 0.85]) * 0.55
    hl = np.exp(-(((ex + 0.45) / .16) ** 2 + ((ey + 0.42) / .09) ** 2))
    img += hl[..., None] * 0.55 * CREAM
    # flare into the beam
    if u > 0.85:
        img += ((u - 0.85) / 0.15) ** 2 * 0.15
    return img


# ----------------------------------------------------------------------------------- the light beam
F = 900.0
VP = np.array([W / 2, 780.0])
CAM = PchipInterpolator([4.6, 4.95, 5.5, 5.85, 6.4, 6.75, 7.3, 7.75, 8.3, 8.6],
                        [0.0, 0.75, 1.05, 2.75, 3.05, 4.75, 5.05, 7.2, 7.75, 8.583])
HOLDS = [(4.75, 5.55), (5.8, 6.45), (6.7, 7.35)]   # pane i is big and labelled
PANES = [  # world z, x, y, width, label
    dict(z=2.0, x=-0.13, y=-0.12, w=0.80, label='CITIES'),
    dict(z=4.0, x=0.13, y=-0.12, w=0.80, label='PYRAMIDS'),
    dict(z=6.0, x=-0.13, y=-0.12, w=0.80, label='FIRST MODERN HUMANS'),
    dict(z=9.0, x=0.0, y=180 * 0.41667 / F, w=0.50, label=None),
]
_r2 = np.random.default_rng(31)
STARS3 = np.stack([_r2.uniform(-6, 6, 900), _r2.uniform(-10, 10, 900), _r2.uniform(0.3, 14, 900), _r2.random(900)], 1)


def pane_images():
    out = []
    def frame(img):
        a = np.ones(img.shape[:2], np.float32)
        h, w = a.shape; rr = 26
        yy, xx = np.mgrid[0:h, 0:w]
        for cx, cy in ((rr, rr), (w - rr, rr), (rr, h - rr), (w - rr, h - rr)):
            cor = ((xx < rr) if cx == rr else (xx > w - rr)) & ((yy < rr) if cy == rr else (yy > h - rr))
            a[cor & ((xx - cx) ** 2 + (yy - cy) ** 2 > rr * rr)] = 0
        b = np.zeros_like(a); b[6:-6, 6:-6] = 1
        border = np.clip(a - b, 0, 1)
        img = img * (1 - border[..., None]) + border[..., None] * CREAM
        return np.dstack([img * a[..., None], a]).astype(np.float32)
    r = np.random.default_rng(41)
    pw, ph = 620, 470
    yy = np.arange(ph)[:, None, None] / ph
    # 1 city at night
    img = (np.array([0.02, 0.03, 0.08]) * (1 - yy) + np.array([0.12, 0.10, 0.12]) * yy) * np.ones((ph, pw, 3))
    im = Image.new('L', (pw, ph), 0); dr = ImageDraw.Draw(im); win = np.zeros((ph, pw), np.float32)
    x = -10
    while x < pw:
        bw, bh = r.uniform(34, 80), r.uniform(90, 330)
        dr.rectangle([x, ph - bh, x + bw, ph], fill=255)
        if r.random() < .25: dr.line([(x + bw / 2, ph - bh), (x + bw / 2, ph - bh - 40)], fill=255, width=3)
        for wy in np.arange(ph - bh + 10, ph - 6, 13):
            for wx in np.arange(x + 6, x + bw - 6, 11):
                if r.random() < .42: win[int(wy):int(wy) + 5, int(wx):int(wx) + 4] = r.uniform(.5, 1)
        x += bw + r.uniform(-4, 6)
    a = np.asarray(im, np.float32)[..., None] / 255
    img = img * (1 - a) + a * INK + (win * (a[..., 0] > .5))[..., None] * GOLD
    img += np.exp(-((yy[..., 0] - 1) / .25) ** 2)[..., None] * GOLD * 0.25
    out.append(frame(img))
    # 2 pyramids at dusk
    img = (np.array([0.10, 0.10, 0.20]) * (1 - yy) + np.array([0.85, 0.55, 0.30]) * yy ** 2) * np.ones((ph, pw, 3))
    im = Image.new('L', (pw, ph), 0); dr = ImageDraw.Draw(im)
    lit = Image.new('L', (pw, ph), 0); dl = ImageDraw.Draw(lit)
    for cx, s in ((200, 190), (395, 150), (530, 80)):
        base = ph - 70
        dr.polygon([(cx - s, base), (cx + s, base), (cx, base - s * 0.95)], fill=255)
        dl.polygon([(cx - s, base), (cx, base), (cx, base - s * 0.95)], fill=255)
    dr.rectangle([0, ph - 75, pw, ph], fill=255)
    a = np.asarray(im, np.float32)[..., None] / 255; l = np.asarray(lit, np.float32)[..., None] / 255
    img = img * (1 - a) + a * (INK * 1.5 + l * np.array([0.35, 0.22, 0.12]))
    img += np.exp(-(((np.arange(pw)[None, :] - 470) / 60) ** 2 + ((np.arange(ph)[:, None] - 330) / 60) ** 2))[..., None] * GOLD * 0.7
    out.append(frame(img))
    # 3 first modern humans: campfire, upright figures with spears
    img = (np.array([0.02, 0.03, 0.07]) * (1 - yy) + np.array([0.08, 0.10, 0.14]) * yy) * np.ones((ph, pw, 3))
    img += star_layer(ph, pw, 42, 260)[..., None] * CREAM * 0.8
    im = Image.new('L', (pw * 2, ph * 2), 0); dr = ImageDraw.Draw(im)
    dr.rectangle([0, (ph - 60) * 2, pw * 2, ph * 2], fill=255)
    for fx, s in ((170, 300), (300, 330), (455, 280)):
        draw_figure(dr, fx * 2, (ph - 58) * 2, s * 2, 1.0, hood=0, stone=0, spear=(fx != 300))
    a = np.asarray(im.resize((pw, ph), Image.LANCZOS), np.float32)[..., None] / 255
    img = img * (1 - a) + a * INK
    fire = np.exp(-(((np.arange(pw)[None, :] - 380) / 22) ** 2 + ((np.arange(ph)[:, None] - (ph - 70)) / 30) ** 2))
    glow = np.exp(-(((np.arange(pw)[None, :] - 380) / 160) ** 2 + ((np.arange(ph)[:, None] - (ph - 70)) / 120) ** 2))
    img += fire[..., None] * np.array([1.0, 0.6, 0.2]) * 1.4 + glow[..., None] * np.array([0.5, 0.25, 0.08]) * 0.6
    out.append(frame(img))
    return out


def render_beam(t, panes, last_img):
    c = float(CAM(t))
    # background: ink-wash space, drifting outward
    s = 1 + 0.03 * (t - T_BEAM)
    sp = A['space']
    img = np.zeros((H, W, 3), np.float32)
    ys, xs = np.mgrid[0:H, 0:W].astype(np.float32)
    wash = np.asarray(Image.fromarray(sp, 'F').transform((W, H), Image.AFFINE,
                      (1 / s, 0, 200 + VP[0] * (1 - 1 / s), 0, 1 / s, 200 + VP[1] * (1 - 1 / s)), Image.BILINEAR))
    img += np.array([0.02, 0.03, 0.07]) + np.clip(wash, -1, 2)[..., None] * np.array([0.02, 0.025, 0.06])
    # star streaks (world-fixed points, camera flies +z)
    st = Image.new('F', (W, H), 0.0); dr = ImageDraw.Draw(st)
    dz = 0.16 + 0.5 * max(0, t - 7.0)
    for x, y, z, b in STARS3:
        zr = (z - c) % 14 + 0.05
        z2 = zr + dz
        p1 = (VP[0] + F * x / zr, VP[1] + F * y / zr)
        p2 = (VP[0] + F * x / z2, VP[1] + F * y / z2)
        if -50 < p1[0] < W + 50 and -50 < p1[1] < H + 50:
            dr.line([p2, p1], fill=float(0.25 + 0.75 * b) * min(1, 2.5 / zr), width=2 if zr < 2 else 1)
    st = gaussian_filter(np.asarray(st), 0.8)
    img += st[..., None] * (0.7 * CREAM + 0.3 * TEAL)
    # the beam: a ribbon below the camera from here to the vanishing point
    dy = np.clip(ys[:, :1] - VP[1], 1e-3, None)
    zrow = F * 0.45 / dy
    wid = F * 0.035 / zrow
    prof = np.exp(-((xs - VP[0]) / (wid + 0.6)) ** 2)
    halo = np.exp(-((xs - VP[0]) / (wid * 6 + 3)) ** 2)
    pulse = 0.75 + 0.25 * np.sin(2 * np.pi * ((zrow + c) * 1.3 - 0.0))
    below = (ys > VP[1]).astype(np.float32)
    img += (prof * pulse * 0.8 * np.clip(F * 0.45 / dy / 0.6, 0.35, 1))[..., None] * below[..., None] * CREAM + (halo * 0.35)[..., None] * below[..., None] * TEAL
    # Andromeda ahead at the vanishing point, growing
    gs = int(90 + 260 * ((t - T_BEAM) / 4.0) ** 1.5)
    g = np.dstack([np.asarray(Image.fromarray(GAL[..., k], 'F').resize((gs, gs), Image.BILINEAR)) for k in range(3)])
    paste_add(img, g * 0.9, VP[0] - gs / 2, VP[1] - gs / 2)
    img += np.exp(-(((xs - VP[0]) ** 2 + (ys - VP[1]) ** 2) / (2 * 30 ** 2)))[..., None] * CREAM * 0.35
    # panes, far to near
    chips = []
    for i in (3, 2, 1, 0):
        P = PANES[i]
        zr = P['z'] - c
        if zr < 0.18 or zr > 7.5:
            continue
        pw = F * P['w'] / zr
        src = panes[i] if i < 3 else last_img
        ph = pw * src.shape[0] / src.shape[1]
        cx, cy = VP[0] + F * P['x'] / zr, VP[1] + F * P['y'] / zr
        if pw < 4 or pw > 4 * W:
            continue
        fade = min(1, (7.5 - zr) / 2.0)
        if i < 3:
            fade *= min(1, (zr - 0.18) / 0.35)
        q = resize_rgba(src, int(pw), int(ph), (cx - pw / 2, cy - ph / 2))
        if q is None:
            continue
        rgb, a, x0, y0 = q
        paste_over(img, rgb * fade, a * fade, x0, y0)
        if P['label']:
            h0, h1 = HOLDS[i]
            al = min(1, (t - h0) / 0.1, (h1 - t) / 0.1)
            if al > 0:
                chips.append((P['label'], cx, cy + ph / 2 + 22, al))
    return img, chips


def paste_add(dst, rgb, x0, y0):
    h, w = rgb.shape[:2]; x0, y0 = int(round(x0)), int(round(y0))
    X0, Y0, X1, Y1 = max(0, x0), max(0, y0), min(dst.shape[1], x0 + w), min(dst.shape[0], y0 + h)
    if X1 > X0 and Y1 > Y0:
        dst[Y0:Y1, X0:X1] += rgb[Y0 - y0:Y1 - y0, X0 - x0:X1 - x0]


def resize_rgba(src, w, h, pos):
    """crop-aware resize: only produce the visible part of a (possibly huge) pane."""
    x0, y0 = pos
    X0, Y0, X1, Y1 = max(0, int(x0)), max(0, int(y0)), min(W, int(x0 + w) + 1), min(H, int(y0 + h) + 1)
    if X1 <= X0 or Y1 <= Y0:
        return None
    sx, sy = src.shape[1] / w, src.shape[0] / h
    data = (sx, 0, (X0 - x0) * sx, 0, sy, (Y0 - y0) * sy)
    out = affine(src, data, (X1 - X0, Y1 - Y0))
    return out[..., :3], np.clip(out[..., 3], 0, 1), X0, Y0


# ----------------------------------------------------------------------------------- grade + text
YY, XX = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.42 * (((XX - W / 2) / (W * .75)) ** 2 + ((YY - H * .48) / (H * .62)) ** 2))[..., None]


def grade(img, f):
    img = np.maximum(img, 0)
    small = img[::2, ::2]
    bright = np.clip(small - 0.55, 0, None)
    bl = gaussian_filter(bright, (14, 14, 0)) * 0.9 + gaussian_filter(bright, (40, 40, 0)) * 0.6
    img = img + np.repeat(np.repeat(bl, 2, 0), 2, 1)[:H, :W]
    img = 1 - np.exp(-1.25 * img)                  # soft clamp (no white-outs)
    img = img * VIG * A['paper'][..., None]
    gr = np.random.default_rng(1000 + f).standard_normal((H // 2, W // 2)).astype(np.float32)
    img += np.repeat(np.repeat(gr, 2, 0), 2, 1)[..., None] * 0.012
    return img


def font(px, f=MONO):
    return ImageFont.truetype(f, px)


def text_block(dr, lines, y, px, alpha=1.0, n=None, col=(246, 236, 214)):
    fnt = font(px)
    used = 0
    for i, ln in enumerate(lines):
        s = ln
        if n is not None:
            k = max(0, min(len(ln), n - used)); used += len(ln); s = ln[:k]
            if k <= 0:
                continue
        w = dr.textlength(ln, font=fnt)
        dr.text(((W - w) / 2, y + i * px * 1.18), s, font=fnt, fill=col + (int(255 * alpha),),
                stroke_width=max(3, px // 11), stroke_fill=(0, 0, 0, int(255 * alpha)))


def chip(dr, s, cx, cy, px, alpha=1.0):
    fnt = font(px)
    w = dr.textlength(s, font=fnt)
    pad = px * 0.4
    dr.rounded_rectangle([cx - w / 2 - pad, cy - pad * .6, cx + w / 2 + pad, cy + px + pad * .5], radius=8,
                         fill=RED + (int(235 * alpha),))
    dr.text((cx - w / 2, cy - px * 0.08), s, font=fnt, fill=(250, 244, 230, int(255 * alpha)))


YEAR_T = [4.6, 5.5, 5.85, 6.4, 6.75, 7.3, 7.75]
YEAR_V = [0, 0, 4500, 4500, 300000, 300000, 2500000]


def years(t):
    if t <= YEAR_T[0]:
        return 0
    if t >= YEAR_T[-1]:
        return 2500000
    for i in range(len(YEAR_T) - 1):
        if YEAR_T[i] <= t <= YEAR_T[i + 1]:
            u = ease((t - YEAR_T[i]) / (YEAR_T[i + 1] - YEAR_T[i]))
            a, b = math.log10(1 + YEAR_V[i]), math.log10(1 + YEAR_V[i + 1])
            return int(round(10 ** lerp(a, b, u) - 1))


def fmt_years(v):
    if v < 1:
        return 'NOW'
    if v >= 10000:
        v = int(round(v / 1000.0) * 1000) if v < 2500000 else 2500000
    elif v >= 100:
        v = int(round(v / 10.0) * 10)
    return f'{v:,} YEARS AGO'


def overlay(t, chips):
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(ov)
    tag = 'THOUGHT EXPERIMENT · NOT TO SCALE'
    fnt = font(24, SANS)
    dr.text(((W - dr.textlength(tag, font=fnt)) / 2, 168), tag, font=fnt, fill=(246, 236, 214, 150),
            stroke_width=2, stroke_fill=(0, 0, 0, 150))
    if t < T_EYE:                                  # payoff hook
        n = 1 + int(t * 95)
        a = 1.0 if t < T_EYE - 0.12 else (T_EYE - t) / 0.12
        text_block(dr, ['ALIENS IN ANDROMEDA', 'SEE EARTH LIKE THIS.'], 250, 64, a, n)
        if t > 0.55:
            chip(dr, 'RIGHT NOW', W / 2, 420, 40, min(1, (t - 0.55) / 0.12) * a)
    elif t < T_BEAM:                               # the eye
        n = 1 + int((t - T_EYE) * 60)
        a = 1.0 if t < T_BEAM - 0.15 else max(0, (T_BEAM - t) / 0.15)
        text_block(dr, ['THE LIGHT IN THEIR EYE', 'LEFT EARTH LONG AGO.'], 260, 60, a, n)
    elif t < T_REVEAL:                             # odometer
        a = min(1, (t - T_BEAM) / 0.15)
        fnt = font(32)
        s = 'THIS LIGHT LEFT EARTH'
        dr.text(((W - dr.textlength(s, font=fnt)) / 2, 240), s, font=fnt, fill=(246, 236, 214, int(255 * a)),
                stroke_width=4, stroke_fill=(0, 0, 0, int(255 * a)))
        text_block(dr, [fmt_years(years(t))], 292, 84, a)
        for s, cx, cy, al in chips:
            chip(dr, s, cx, cy, 30, max(0, al))
    elif t < T_FLIP:                               # reveal
        u = t - T_REVEAL
        fnt = font(32)
        s = '2,500,000 YEARS AGO'
        dr.text(((W - dr.textlength(s, font=fnt)) / 2, 250), s, font=fnt, fill=(246, 236, 214, 235),
                stroke_width=4, stroke_fill=(0, 0, 0, 235))
        sc = 1 + 0.25 * math.exp(-u / 0.08)
        a = 1.0 if t < T_FLIP - 0.12 else (T_FLIP - t) / 0.12
        text_block(dr, ['NO MODERN', 'HUMANS YET.'], 310, int(84 * sc), a)
    else:                                          # flip to today
        u = t - T_FLIP
        a = min(1, max(0, (u - 0.15) / 0.15)) * (1 if t < 11.55 else max(0, (11.85 - t) / 0.3))
        if a > 0:
            n = 1 + int((u - 0.15) * 70)
            text_block(dr, ["TODAY'S LIGHT GETS THERE", 'IN 2.5 MILLION YEARS.'], 255, 56, a, n)
    return ov


# ----------------------------------------------------------------------------------- timeline
def ridge_zoom(t):
    """one continuous push across the loop: reveal 1.00 -> flip 1.06 -> end 1.10 = frame 0 -> 1.18 at 2.3,
    zoomed about the top edge so the push drops the ground out of frame (tight framing)"""
    if t < T_EYE:
        z = lerp(1.10, 1.19, t / T_EYE)
    elif t < T_FLIP:
        z = lerp(1.00, 1.06, ease((t - T_REVEAL) / 1.4) * 0.6 + 0.4 * (t - T_REVEAL) / 1.4)
    else:
        z = lerp(1.06, 1.10, (t - T_FLIP) / 2.0)
    return z


PIVOT = (600, 0)


def morph(t):
    if T_FLIP <= t < 12.0:
        u = t - T_FLIP
        if u < 0.75:
            return ease(u / 0.75)
        if u < 1.55:
            return 1.0
        return 1 - ease((u - 1.55) / 0.45)
    return 0.0


def shake(t):
    s = np.zeros(2)
    for th, amp in ((0.0, 7.0), (T_REVEAL, 14.0)):
        if th <= t < th + 0.35:
            k = (t - th)
            s += amp * math.exp(-k / 0.09) * np.array([math.sin(k * 97), math.cos(k * 83)])
    return s


LAST = None


def last_pane():
    global LAST
    if LAST is None:
        f = CACHE + '/lastpane.npy'
        if os.path.exists(f):
            LAST = np.load(f)
        else:
            img = render_ridge(T_REVEAL, ridge_zoom(T_REVEAL), 0.0, pivot=PIVOT)
            LAST = np.dstack([img, np.ones(img.shape[:2], np.float32)]).astype(np.float32)
            np.save(f, LAST)
    return LAST


PANE_IMGS = None


def render_frame(f):
    global PANE_IMGS
    t = f / FPS
    chips = []
    if t < T_EYE or t >= T_REVEAL:
        m = morph(t)
        img = render_ridge(t, ridge_zoom(t), m, pivot=PIVOT, shift=tuple(shake(t)), city=m)
        if t >= T_REVEAL and t < T_REVEAL + 0.12:
            img = img + (1 - (t - T_REVEAL) / 0.12) * 0.14
        if t < 0.1:
            img = img + (1 - t / 0.1) * 0.12
    elif t < T_BEAM:
        img = render_eye(t)
    else:
        if PANE_IMGS is None:
            PANE_IMGS = pane_images()
        img, chips = render_beam(t, PANE_IMGS, last_pane())
        if t < T_BEAM + 0.15:
            img = img + (1 - (t - T_BEAM) / 0.15) * 0.15
        if 8.0 <= t < 8.3:
            img = img * 0.85
    img = grade(img, f)
    out = Image.fromarray(to8(img)).convert('RGBA')
    out = Image.alpha_composite(out, overlay(t, chips)).convert('RGB')
    return out


def work(args):
    outdir, frames = args
    for f in frames:
        p = f'{outdir}/f{f:04d}.png'
        if not os.path.exists(p):
            render_frame(f).save(p)
    return len(frames)


if __name__ == '__main__':
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    frames = [int(x) for x in sys.argv[2:]] or list(range(NF))
    last_pane()
    if len(frames) <= 4:
        work((outdir, frames))
    else:
        from multiprocessing import Pool
        with Pool(4) as p:
            p.map(work, [(outdir, frames[i::4]) for i in range(4)])
    # monotonic odometer check
    v = [years(f / FPS) for f in range(NF)]
    assert all(b >= a for a, b in zip(v[:int(T_REVEAL * FPS)], v[1:int(T_REVEAL * FPS)])), 'odometer went backwards'
