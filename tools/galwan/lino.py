# Linocut print engine: paper + ink plates with rough edges and boil.
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import math, os

W, H = 1080, 1920
HERE = os.path.dirname(os.path.abspath(__file__))
FONT_TE = os.path.join(HERE, "fonts/NotoSansTelugu-800.ttf")
FONT_DISP = os.path.join(HERE, "fonts/Ramaraja.ttf")
FONT_NUM = os.path.join(HERE, "fonts/Anton.ttf")

PAPER = np.array([238, 228, 206], np.float32)
BRIGHT = (255, 255, 255)
INK = np.array([27, 36, 68], np.float32)
SAFF = np.array([228, 126, 34], np.float32)
GREEN = np.array([30, 118, 64], np.float32)
COLS = {"ink": INK, "saff": SAFF, "paper": np.array([246, 240, 224], np.float32), "green": GREEN,
        "deep": np.array([18, 24, 48], np.float32)}

_rng = np.random.default_rng(7)


def _noise(scale, seed):
    r = np.random.default_rng(seed)
    small = r.random((H // scale + 2, W // scale + 2)).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((W + scale * 2, H + scale * 2), Image.BICUBIC)
    return np.asarray(im, np.float32)[:H, :W] / 255.0


# paper texture
_grain = _noise(2, 1) * 0.5 + _noise(9, 2) * 0.35 + _noise(40, 3) * 0.15
PAPER_IMG = PAPER[None, None, :] * (0.93 + 0.1 * _grain[..., None])
# boil noises (cycle) for edge roughness and ink speckle
BOIL = [(_noise(3, 10 + i) * 0.6 + _noise(11, 20 + i) * 0.4) for i in range(4)]
SPECK = [np.clip((_noise(5, 40 + i) - 0.62) * 4, 0, 1) * 0.35 + np.clip((_noise(2, 60 + i) - 0.8) * 5, 0, 1) * 0.4
         for i in range(4)]


class Canvas:
    def __init__(self, t):
        self.img = PAPER_IMG.copy()
        self.k = int(t * 12) % 4  # 12 fps boil
        self.cur = None

    def L(self, col="ink", rough=1.0, speck=True, alpha=1.0):
        self.flush()
        m = Image.new("L", (W, H), 0)
        self.cur = (m, col, rough, speck, alpha)
        return ImageDraw.Draw(m)

    def flush(self):
        if self.cur is None:
            return
        m, col, rough, speck, alpha = self.cur
        self.cur = None
        a = np.asarray(m, np.float32) / 255.0
        if not a.any():
            return
        if rough > 0:
            b = np.asarray(m.filter(ImageFilter.GaussianBlur(1.6 * rough)), np.float32) / 255.0
            a = np.clip((b + (BOIL[self.k] - 0.5) * 0.55 * rough - 0.5) * 6 + 0.5, 0, 1)
        if speck:
            a = a * (1 - SPECK[self.k])
        a = a * alpha
        c = COLS[col] if isinstance(col, str) else np.array(col, np.float32)
        if isinstance(col, str) and col == "paper":
            c = PAPER_IMG * 1.04
            self.img = self.img * (1 - a[..., None]) + c * a[..., None]
        else:
            self.img = self.img * (1 - a[..., None]) + c[None, None, :] * a[..., None]

    def paste_rgba(self, im, xy=(0, 0)):
        self.flush()
        a = np.asarray(im, np.float32) / 255.0
        x, y = xy
        h, w = a.shape[:2]
        x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + w), min(H, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        sub = a[y0 - y:y1 - y, x0 - x:x1 - x]
        al = sub[..., 3:4]
        self.img[y0:y1, x0:x1] = self.img[y0:y1, x0:x1] * (1 - al) + sub[..., :3] * 255 * al

    def out(self):
        self.flush()
        return np.clip(self.img, 0, 255).astype(np.uint8)


# ---- camera helpers ----
PUNCH = [1.0]


class Cam:
    def __init__(self, cx=540, cy=960, s=1.0, rot=0.0, sx=0, sy=0):
        self.cx, self.cy, self.s, self.sx, self.sy = cx, cy, s * PUNCH[0], sx, sy

    def off(self, dx, dy=0):
        c = Cam.__new__(Cam)
        c.cx, c.cy, c.s, c.sx, c.sy = self.cx + dx, self.cy + dy, self.s, self.sx, self.sy
        return c

    def p(self, x, y):
        return (540 + (x - self.cx) * self.s + self.sx, 960 + (y - self.cy) * self.s + self.sy)

    def pts(self, P):
        return [self.p(x, y) for x, y in P]


def poly(d, cam, P, fill=255):
    d.polygon(cam.pts(P), fill=fill)


def line(d, cam, P, w, fill=255):
    q = cam.pts(P)
    ww = max(1, int(w * cam.s))
    d.line(q, fill=fill, width=ww, joint="curve")
    r = ww / 2
    for x, y in (q[0], q[-1]):
        d.ellipse((x - r, y - r, x + r, y + r), fill=fill)


def circ(d, cam, x, y, r, fill=255, outline=None, width=0):
    X, Y = cam.p(x, y)
    R = r * cam.s
    d.ellipse((X - R, Y - R, X + R, Y + R), fill=fill, outline=outline, width=int(width * cam.s) if width else 0)


def ease(u):
    u = min(1, max(0, u))
    return u * u * (3 - 2 * u)


def eout(u):
    u = min(1, max(0, u))
    return 1 - (1 - u) ** 3


# ---- figures ----
def soldier(d, cam, x, yf, h, pose=None, facing=1, club=False, helmet=True, rifle=False, pack=True):
    """Side/back silhouette soldier. pose: dict of angles in degrees (0 = straight down)."""
    P = dict(lt=8, ls=0, rt=-8, rs=0, la=10, le=10, ra=-10, re=-10, lean=0)
    if pose:
        P.update(pose)
    f = facing
    lw = 0.085 * h
    hip = (x, yf - 0.5 * h)
    lean = math.radians(P["lean"]) * f
    sh = (hip[0] + math.sin(lean) * 0.33 * h, hip[1] - math.cos(lean) * 0.33 * h)
    head = (sh[0] + math.sin(lean) * 0.12 * h, sh[1] - math.cos(lean) * 0.12 * h)

    def limb(o, a1, a2, L1, L2, w):
        a1r, a2r = math.radians(a1) * f, math.radians(a1 + a2) * f
        k = (o[0] + math.sin(a1r) * L1, o[1] + math.cos(a1r) * L1)
        e = (k[0] + math.sin(a2r) * L2, k[1] + math.cos(a2r) * L2)
        taper(d, cam, [o, k, e], w * 1.15, w * 0.8)
        return e

    limb(hip, P["lt"], P["ls"] - P["lt"] * 0 , 0.26 * h, 0.25 * h, lw * 1.05)
    limb(hip, P["rt"], P["rs"], 0.26 * h, 0.25 * h, lw * 1.05)
    # torso
    tw = 0.15 * h
    poly(d, cam, [(hip[0] - tw * 0.8, hip[1]), (hip[0] + tw * 0.8, hip[1]),
                  (sh[0] + tw, sh[1] + 0.02 * h), (sh[0] - tw, sh[1] + 0.02 * h)])
    if pack:
        bx = -f * tw * 0.9
        poly(d, cam, [(sh[0] + bx - 0.03 * h * f, sh[1] + 0.03 * h), (sh[0] + bx - 0.11 * h * f, sh[1] + 0.06 * h),
                      (hip[0] + bx - 0.1 * h * f, hip[1] - 0.05 * h), (hip[0] + bx, hip[1] - 0.02 * h)])
    line(d, cam, [(sh[0], sh[1] + 0.01 * h), head], lw * 0.9)
    circ(d, cam, head[0], head[1] - 0.02 * h, 0.06 * h)
    if helmet:
        X, Y = head[0], head[1] - 0.04 * h
        r = 0.078 * h
        q = [cam.p(X + r * math.cos(a), Y - r * 0.85 * math.sin(a)) for a in np.linspace(0, math.pi, 14)]
        q += [cam.p(X - r * 1.12, Y + 0.012 * h), cam.p(X + r * 1.12, Y + 0.012 * h)]
        d.polygon(q, fill=255)
    hand_r = limb((sh[0], sh[1] + 0.02 * h), P["ra"], P["re"], 0.17 * h, 0.17 * h, lw * 0.85)
    hand_l = limb((sh[0], sh[1] + 0.02 * h), P["la"], P["le"], 0.17 * h, 0.17 * h, lw * 0.85)
    if rifle:
        line(d, cam, [(sh[0] - f * 0.1 * h, sh[1] - 0.04 * h), (hip[0] + f * 0.12 * h, hip[1] + 0.06 * h)], lw * 0.4)
    if club:
        a = math.radians(P.get("club", 160)) * f
        e = (hand_r[0] + math.sin(a) * 0.32 * h, hand_r[1] + math.cos(a) * 0.32 * h)
        line(d, cam, [hand_r, e], lw * 0.55)
    return dict(head=head, sh=sh, hip=hip, hand_r=hand_r, hand_l=hand_l)


def taper(d, cam, P, w1, w2, fill=255):
    """tapered limb through points P, width w1 -> w2"""
    n = len(P)
    L, R = [], []
    for i in range(n):
        a = P[max(i - 1, 0)]; b = P[min(i + 1, n - 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        nx, ny = -dy / ln, dx / ln
        w = (w1 + (w2 - w1) * i / max(1, n - 1)) / 2
        L.append((P[i][0] + nx * w, P[i][1] + ny * w)); R.append((P[i][0] - nx * w, P[i][1] - ny * w))
    poly(d, cam, L + R[::-1], fill)
    for (x, y), w in ((P[0], w1), (P[-1], w2)):
        circ(d, cam, x, y, w / 2, fill)


def figure_front(d, cam, x, yf, h, arms=None, legs=6, helmet=True, rim=0):
    """front/back view soldier in winter kit. arms: (left_deg, right_deg, elbow) from vertical, outward positive."""
    al, ar, el = arms or (8, 8, 6)
    hw = 0.135 * h
    sy = yf - 0.80 * h
    wy = yf - 0.47 * h
    # torso (puffy jacket)
    poly(d, cam, [(x - hw, sy + 0.02 * h), (x - hw * 0.62, sy - 0.035 * h), (x + hw * 0.62, sy - 0.035 * h), (x + hw, sy + 0.02 * h),
                  (x + hw * 0.92, wy), (x + hw * 0.98, wy + 0.06 * h), (x - hw * 0.98, wy + 0.06 * h), (x - hw * 0.92, wy)])
    # legs
    for sgn in (-1, 1):
        spread = math.radians(legs)
        hx = x + sgn * 0.055 * h
        kx = hx + sgn * math.sin(spread) * 0.24 * h
        fx = kx + sgn * math.sin(spread) * 0.22 * h
        taper(d, cam, [(hx, wy + 0.03 * h), (kx, yf - 0.24 * h), (fx, yf - 0.03 * h)], 0.11 * h, 0.07 * h)
        poly(d, cam, [(fx - 0.045 * h, yf - 0.05 * h), (fx + 0.045 * h, yf - 0.05 * h), (fx + 0.055 * h + sgn * 0.01 * h, yf), (fx - 0.055 * h + sgn * 0.01 * h, yf)])
    # arms
    for sgn, a in ((-1, al), (1, ar)):
        ox, oy = x + sgn * hw * 0.9, sy + 0.03 * h
        ar1 = math.radians(a)
        ex, ey = ox + sgn * math.sin(ar1) * 0.17 * h, oy + math.cos(ar1) * 0.17 * h
        ar2 = math.radians(a + el)
        hx2, hy2 = ex + sgn * math.sin(ar2) * 0.17 * h, ey + math.cos(ar2) * 0.17 * h
        taper(d, cam, [(ox, oy), (ex, ey), (hx2, hy2)], 0.085 * h, 0.06 * h)
        circ(d, cam, hx2, hy2, 0.035 * h)
    # neck/head/helmet
    poly(d, cam, [(x - 0.035 * h, sy - 0.02 * h), (x + 0.035 * h, sy - 0.02 * h), (x + 0.03 * h, sy - 0.07 * h), (x - 0.03 * h, sy - 0.07 * h)])
    circ(d, cam, x, yf - 0.905 * h, 0.058 * h)
    if helmet:
        X, Y, r = x, yf - 0.925 * h, 0.08 * h
        q = [cam.p(X + r * math.cos(a), Y - r * 0.9 * math.sin(a)) for a in np.linspace(0, math.pi, 18)]
        q += [cam.p(X - r * 1.1, Y + 0.018 * h), cam.p(X + r * 1.1, Y + 0.018 * h)]
        d.polygon(q, fill=255)


def ridge(seed, base, amp, n=7, x0=-400, x1=1480, step=12):
    r = np.random.default_rng(seed)
    ph = r.random(n) * 6.28
    fr = (np.arange(n) + 1) ** 1.25 * 0.0018
    am = amp / (np.arange(n) + 1) ** 1.1
    xs = np.arange(x0, x1 + step, step)
    ys = base - np.abs(sum(am[i] * np.sin(xs * fr[i] + ph[i]) for i in range(n)))
    return list(zip(xs.tolist(), ys.tolist()))


def mountains(C, cam, seed, base, amp, col="ink", snow=True, t=0, speck=True):
    R = ridge(seed, base, amp)
    d = C.L(col, speck=speck)
    poly(d, cam, R + [(1480, 4000), (-400, 4000)])
    if snow:
        d = C.L("paper", rough=0.9)
        r = np.random.default_rng(seed + 99)
        top = min(y for _, y in R)
        bot = []
        for i, (x, y) in enumerate(R):
            hgt = (base - y) / amp
            dep = max(0.0, hgt - 0.55) * amp * 0.45 * (0.7 + 0.5 * r.random())
            bot.append((x, y + dep))
        poly(d, cam, R + bot[::-1])
        d = C.L("ink", rough=0.6, alpha=0.8)
        for i in range(2, len(R) - 2, 3):
            x, y = bot[i]
            if bot[i][1] - R[i][1] > 12:
                line(d, cam, [(x, R[i][1] + 6), (x + 6, y - 4)], 3)
    return R


def sky(C, cam, t, gouge=True, col="ink", density=1.0):
    d = C.L(col, rough=0, speck=True)
    d.rectangle((0, 0, W, H), fill=255)
    if gouge:
        d = C.L("paper", rough=0.7, speck=False, alpha=0.55)
        r = np.random.default_rng(5)
        y = -300.0
        i = 0
        while y < 2300:
            i += 1
            th = 2 + 5 * r.random() * density
            ph = r.random() * 6
            xs = np.arange(-300, 1400, 30)
            P = [(x, y + 10 * math.sin(x * 0.006 + ph + t * 0.6)) for x in xs]
            # broken gouge strokes
            segs = r.integers(2, 5)
            for s in range(segs):
                a = r.integers(0, len(P) - 8)
                b = min(len(P), a + r.integers(6, 30))
                line(d, cam, P[a:b], th)
            y += 26 + 30 * r.random() / density


def moon(C, cam, x, y, r, t, ring=1.0, glow=1.0):
    d = C.L("saff", rough=0.6, alpha=0.9 * glow)
    for k in range(3):
        rr = r + 30 + k * 34 * ring
        circ(d, cam, x, y, rr, fill=None, outline=255, width=10 - k * 2)
    d = C.L("paper", rough=0.5)
    circ(d, cam, x, y, r)
    d = C.L("ink", rough=0.5, alpha=0.18)
    circ(d, cam, x - r * 0.3, y + r * 0.2, r * 0.25)
    circ(d, cam, x + r * 0.35, y - r * 0.3, r * 0.15)


def snow(C, cam, t, n=140, speed=1.0, seed=3, wind=1.0, size=1.0, col="paper"):
    d = C.L(col, rough=0.3, speck=False)
    r = np.random.default_rng(seed)
    X = r.random(n) * 1300 - 100
    Y = r.random(n) * 2100
    S = (0.5 + r.random(n)) * size
    for i in range(n):
        y = (Y[i] + t * 260 * speed * S[i]) % 2100 - 100
        x = (X[i] + t * 380 * wind * S[i] + 40 * math.sin(t * 2 + i)) % 1300 - 100
        rr = 3 + 5 * S[i]
        d.ellipse((x - rr, y - rr * 0.7, x + rr * 2.2 * wind, y + rr * 0.7), fill=255)


_fc = {}


def font(path, size):
    k = (path, size)
    if k not in _fc:
        _fc[k] = ImageFont.truetype(path, size, layout_engine=ImageFont.Layout.RAQM)
    return _fc[k]


def text_layer(C, txt, cx, cy, size, col="paper", path=FONT_TE, scale=1.0, maxw=860, stroke=0, rough=0.4, alpha=1.0, outline=None):
    if outline:
        text_layer(C, txt, cx + size * 0.03, cy + size * 0.04, size, col=outline, path=path, scale=scale, maxw=maxw, stroke=max(4, int(size * scale / 9)), rough=rough, alpha=alpha)
    f = font(path, int(size * scale))
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    bb = d0.textbbox((0, 0), txt, font=f, stroke_width=stroke)
    w = bb[2] - bb[0]
    if w > maxw * scale:
        return text_layer(C, txt, cx, cy, size * maxw / w * 0.98, col, path, scale, maxw, stroke, rough, alpha, outline)
    d = C.L(col, rough=rough, speck=True, alpha=alpha)
    d.text((cx - w / 2 - bb[0], cy - (bb[3] + bb[1]) / 2), txt, font=f, fill=255, stroke_width=stroke, stroke_fill=255)
    return (cx - w / 2, cy - (bb[3] - bb[1]) / 2, cx + w / 2, cy + (bb[3] - bb[1]) / 2)


def label(C, lines, cy, size=74, t=0, tin=0.0, bg="paper", fg="ink", hl="saff"):
    """Printed paper label strip caption. lines: list of (text, highlight bool)."""
    u = eout((t - tin) / 0.12) if t >= tin else 0
    if u <= 0:
        return
    f = font(FONT_TE, size)
    d0 = ImageDraw.Draw(Image.new("L", (1, 1)))
    lh = int(size * 1.42)
    ws = []
    for s, _ in lines:
        bb = d0.textbbox((0, 0), s, font=f)
        ws.append((bb[2] - bb[0], bb))
    wmax = max(w for w, _ in ws)
    if wmax > 820:
        return label(C, lines, cy, int(size * 820 / wmax), t, tin, bg, fg, hl)
    tot = lh * len(lines)
    y0 = cy - tot / 2
    sc = 0.85 + 0.15 * u
    d = C.L(bg, rough=0.9, speck=False)
    for i, (w, bb) in enumerate(ws):
        yy = y0 + i * lh
        pad = 34
        x0 = 540 - (w / 2 + pad) * sc
        x1 = 540 + (w / 2 + pad) * sc
        d.polygon([(x0, yy + 6), (x1, yy), (x1 + 4, yy + lh - 4), (x0 - 3, yy + lh + 2)], fill=255)
    for i, ((s, h_), (w, bb)) in enumerate(zip(lines, ws)):
        yy = y0 + i * lh + lh / 2
        d = C.L(hl if h_ else fg, rough=0.35)
        ff = font(FONT_TE, int(size * sc))
        b2 = d0.textbbox((0, 0), s, font=ff)
        d.text((540 - (b2[2] - b2[0]) / 2 - b2[0], yy - (b2[3] + b2[1]) / 2), s, font=ff, fill=255)
