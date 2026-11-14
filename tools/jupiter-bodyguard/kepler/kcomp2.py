"""v2 compositor: replica look of the reference reel (soft planets, real backdrops, magnetosphere, film subs)."""
import math
import os
import sys
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from kernel import render  # noqa: E402
from scene import tonemap  # noqa: E402
import kshots2 as ks  # noqa: E402
from kassets import load, TEX2  # noqa: E402
from kcomp import planet_mask  # noqa: E402

W, H = ks.W, ks.H
T = load()
DL = os.environ.get("JB_DL", os.path.join(os.path.dirname(TEX2), "dl"))
_c = {}


def _lin(img):
    return np.power(np.clip(img, 0, 1), 2.2).astype(np.float32)


def asset(name):
    if name in _c:
        return _c[name]
    if name == "kday_soft":
        p = os.path.join(TEX2, "kepler_day5.png")
        if not os.path.exists(p):
            import kmap
            kmap.build(p)
        v = np.ascontiguousarray(np.asarray(Image.open(p).convert("RGB")))
    elif name == "kcloud_soft":
        v = np.ascontiguousarray((T["kcloud"][..., 0].astype(np.float32) * 0.7).astype(np.uint8)[..., None])
    elif name == "europa":
        m = T["moon"].astype(np.float32) / 255
        m = m.mean(2, keepdims=True) * np.array([1.12, 0.98, 0.82]) + np.array([0.10, 0.08, 0.05])
        v = np.ascontiguousarray((np.clip(m, 0, 1) * 255).astype(np.uint8))
    elif name == "m15":
        v = cv2.cvtColor(cv2.imread(os.path.join(DL, "Messier_15_HST.jpg")), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
    elif name == "juno":
        im = cv2.cvtColor(cv2.imread(os.path.join(DL, "PIA21775.jpg")), cv2.COLOR_BGR2RGB).astype(np.float32) / 255
        # richer, warmer, more contrast (the raw JunoCam frame is pale)
        g = im.mean(2, keepdims=True)
        im = g + (im - g) * 1.3
        im = np.clip((im - 0.06) * 1.12, 0, 1) ** 1.25
        im = im * np.array([1.06, 0.97, 0.88])
        v = np.clip(im, 0, 1).astype(np.float32)
    elif name == "noise":
        rng = np.random.default_rng(7)
        v = rng.random((256, 256)).astype(np.float32)
    else:
        raise KeyError(name)
    _c[name] = v
    return v


# ------------------------------------------------------------------ 3D render
def raw(st, ss=2):
    tex = st["tex"]
    if tex == "kepler":
        day, night, cloud = asset("kday_soft"), T["knight"], asset("kcloud_soft")
    else:
        day, night, cloud = T["earth_day"], T["earth_night"], T["earth_cloud"]
    sat = {"io": T["io"], "moon": T["moon"], "europa": asset("europa")}.get(tex, T["sat"])
    objs = np.array(st["objs"])
    return render(W, H, st["cam"], objs, len(objs), st["L"], day, night, cloud, T["jup"], sat, T["ring"],
                  T["sky"], T["neb"], st["prm"], ss).astype(np.float32)


# ------------------------------------------------------------------ backdrops
_yy, _xx = np.mgrid[0:H, 0:W].astype(np.float32)


def bg_navy():
    if "navy" not in _c:
        y = _yy / H
        top = np.array([0.010, 0.034, 0.095], np.float32)
        bot = np.array([0.0015, 0.004, 0.012], np.float32)
        k = np.clip(y * 1.25, 0, 1) ** 0.8
        _c["navy"] = top * (1 - k[..., None]) + bot * k[..., None]
    return _c["navy"]


def bg_redwisp():
    """Small red emission cloud top-right, like the ref's Kepler shots."""
    if "redwisp" not in _c:
        img = T["nebimg"]["carina"]
        c = img[200:900, 1100:1800]
        c = cv2.resize(c, (420, 420))
        r = c[..., 0:1] * np.array([1.0, 0.25, 0.18])
        yy, xx = np.mgrid[0:420, 0:420]
        a = np.clip(1 - np.sqrt((xx - 210) ** 2 + (yy - 210) ** 2) / 210, 0, 1) ** 1.5
        lay = np.zeros((H, W, 3), np.float32)
        lay[330:750, 760:1080] = (_lin(r) * a[..., None] * 0.9)[:, :320]
        _c["redwisp"] = lay
    return _c["redwisp"]


def bg_cluster(u):
    """Dense Hubble star cluster with the bright core peeking out under Jupiter + warm dust."""
    m = asset("m15")
    s = 1.55 + 0.05 * u
    im = cv2.resize(m, (int(1920 * s), int(1920 * s)), interpolation=cv2.INTER_AREA)
    cx, cy = im.shape[1] // 2, im.shape[0] // 2
    x0 = cx - 540; y0 = cy - 1400                     # core sits just below Jupiter's bottom limb
    pad = np.zeros((H, W, 3), np.float32)
    ys, ye = max(0, -y0), min(H, im.shape[0] - y0)
    pad[ys:ye] = im[y0 + ys:y0 + ye, x0:x0 + W]
    lin = _lin(pad) * 0.55
    lin = lin * np.array([0.92, 0.88, 1.15], np.float32)
    dust = T["nebimg"]["orion"]
    dd = cv2.resize(dust, (W + 200, int((W + 200) * dust.shape[0] / dust.shape[1])))[:H, 100:100 + W]
    if dd.shape[0] < H:
        dd = cv2.resize(dd, (W, H))
    g = dd.mean(2, keepdims=True)
    warm = g * np.array([1.0, 0.78, 0.55]) * 0.6 + dd * 0.4
    lin = lin + _lin(warm) * 0.45
    # glow from the core
    core = np.exp(-(((_xx - 540) / 420) ** 2 + ((_yy - 1400) / 300) ** 2))
    lin = lin + core[..., None] * np.array([0.40, 0.33, 0.24], np.float32)
    return lin.astype(np.float32)


def bg_magneto(t, u):
    """Jupiter's magnetosphere: dipole (axis horizontal, poles left/right) field lines in violet."""
    cx, cy, R = 540.0, 960.0, 250.0
    x = (_xx - cx) / R
    y = (_yy - cy) / R
    r = np.sqrt(x * x + y * y) + 1e-4
    s2 = (y / r) ** 2 + 1e-4                          # sin^2 from the horizontal (dipole) axis
    Lv = r / s2
    th = np.arctan2(np.abs(y), x)
    # streaky noise flowing along the lines
    nz = asset("noise")
    lnL = np.log(Lv)
    a = (lnL * 40.0) % 256
    b = (th * 30.0 - t * 18.0) % 256
    n1 = cv2.remap(cv2.GaussianBlur(nz, (0, 0), 1.2), a.astype(np.float32), b.astype(np.float32),
                   cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    n2 = cv2.remap(cv2.GaussianBlur(nz, (0, 0), 4.0), (a * 0.25).astype(np.float32), (b * 0.5).astype(np.float32),
                   cv2.INTER_LINEAR, borderMode=cv2.BORDER_WRAP)
    lines = np.zeros_like(x)
    for k, Lk in enumerate([1.6, 2.1, 2.8, 3.7, 4.9, 6.4, 8.5, 11.0]):
        w = 0.10 * Lk
        lines += np.exp(-((Lv - Lk) / w) ** 2) * (0.9 - 0.06 * k)
    fill = np.clip(1.0 / (1 + (Lv / 6.0) ** 2), 0, 1) * np.clip((r - 1.0) * 1.5, 0, 1)
    wisp = (0.15 + 1.2 * n1 ** 1.5) * (0.35 + 1.0 * n2)
    v = (lines * 0.75 + fill * 0.35) * wisp
    v = cv2.GaussianBlur(v.astype(np.float32), (0, 0), 2.0)
    col = v[..., None] * np.array([0.20, 0.09, 0.42], np.float32)
    col += (fill * 0.35)[..., None] * np.array([0.05, 0.05, 0.16], np.float32)
    # dark equatorial cavity on both sides of the planet
    eq = np.exp(-(y / 0.55) ** 2) * np.clip(np.abs(x) - 1.0, 0, 3) / 3
    col *= (1 - 0.55 * eq)[..., None]
    base = np.array([0.012, 0.012, 0.040], np.float32)
    col = col + base
    # aurora glow over the lobes, blooming in as the line lands
    k = np.clip((u - 0.25) / 0.45, 0, 1)
    k = k * k * (3 - 2 * k)
    if k > 0:
        for py in (cy - 600, cy + 600):
            d2 = ((_xx - cx) / 330) ** 2 + ((_yy - py) / 260) ** 2
            core = np.exp(-d2 * 1.6)
            halo = np.exp(-d2 * 0.45)
            col += 0.30 * k * (core[..., None] * np.array([1.05, 0.55, 0.38], np.float32)
                        + halo[..., None] * np.array([0.10, 0.32, 0.36], np.float32) * 0.8)
    stars = T.get("_mstars")
    return col.astype(np.float32)


# ------------------------------------------------------------------ Juno GRS shot
def flare(lay, x, y, s, rings=True):
    """Lens flare: hot core, anamorphic streak, soft glow and two big thin rings."""
    d2 = (_xx - x) ** 2 + (_yy - y) ** 2
    lay += (np.exp(-d2 / (2 * (9 * s) ** 2)) * 6.0)[..., None] * np.array([1.0, 0.95, 0.85], np.float32)
    lay += (np.exp(-d2 / (2 * (70 * s) ** 2)) * 0.6)[..., None] * np.array([1.0, 0.7, 0.4], np.float32)
    st = np.exp(-((_yy - y) / (3.0 * s)) ** 2 - ((_xx - x) / (420 * s)) ** 2) * 1.6
    lay += st[..., None] * np.array([0.55, 0.70, 1.0], np.float32)
    st2 = np.exp(-((_xx - x) / (3.0 * s)) ** 2 - ((_yy - y) / (160 * s)) ** 2) * 0.8
    lay += st2[..., None] * np.array([0.9, 0.85, 1.0], np.float32)
    if rings:
        dr = np.sqrt((_xx - 560) ** 2 + (_yy - 560) ** 2)
        for rr, c in ((420, (0.45, 0.10, 0.10)), (330, (0.20, 0.20, 0.45))):
            ring = np.exp(-((dr - rr) / 4.0) ** 2) * 0.55 * s
            lay += ring[..., None] * np.array(c, np.float32)
    return lay


def juno_shot(st):
    u, t = st["u"], st["t"]
    dur = ks.SHOTS[st["idx"]][1] - ks.SHOTS[st["idx"]][0]
    im = asset("juno")
    s = 1.25 * (1 + 0.04 * u)
    big = cv2.resize(im, (int(1280 * s), int(1138 * s)), interpolation=cv2.INTER_AREA)
    gx, gy = 660 * s, 523 * s
    hz = 88 * s
    oy = int(640 - hz)
    x0 = int(gx - 540)
    out = np.zeros((H, W, 3), np.float32)
    ys, ye = max(0, oy), min(H, oy + big.shape[0])
    out[ys:ye] = big[ys - oy:ye - oy, x0:x0 + W]
    out = _lin(out)
    # faint stars + haze above the horizon
    rng = np.random.default_rng(3)
    for _ in range(140):
        sx, sy = rng.integers(0, W), rng.integers(0, 640)
        if out[sy, sx].sum() < 0.01:
            b = rng.random() ** 3 * 0.8 + 0.05
            cv2.circle(out, (int(sx), int(sy)), 1, (b, b, b * 1.1), -1, cv2.LINE_AA)
    haze = np.exp(-((_yy - 640) / 110) ** 2)[..., None] * np.array([0.05, 0.035, 0.02], np.float32)
    out += haze
    lay = np.zeros((H, W, 3), np.float32)
    # asteroid streaking in from upper right toward the limb above the storm
    a0, a1 = 0.05, 0.62
    P0, P1, P2, P3 = (np.array(p, float) for p in ((1180, 120), (900, 420), (740, 560), (600, 650)))

    def at(q):
        m = 1 - q
        return m ** 3 * P0 + 3 * m * m * q * P1 + 3 * m * q * q * P2 + q ** 3 * P3
    if u >= a0:
        q = min((u - a0) / (a1 - a0), 1.0) ** 1.3
        if q < 1.0:
            qs = np.linspace(max(q - 0.4, 0), q, 50)
            pts = [at(v) for v in qs]
            for k in range(len(pts) - 1):
                f = (k + 1) / len(pts)
                cv2.line(lay, tuple(int(v) for v in pts[k]), tuple(int(v) for v in pts[k + 1]),
                         (2.6 * f, 1.2 * f, 0.35 * f), max(1, int(12 * f ** 1.5)), cv2.LINE_AA)
            lay = cv2.GaussianBlur(lay, (0, 0), 1.5)
            hx, hy = at(q)
            flare(lay, hx, hy, 0.8 + 0.4 * q)
        else:
            dt = (u - a1) * dur
            hx, hy = at(1.0)
            k = math.exp(-dt * 3.0)
            fl = math.exp(-dt * 10)
            d2 = ((_xx - hx) / 1.0) ** 2 + ((_yy - hy) / 0.35) ** 2
            lay += (np.exp(-d2 / (2 * (60 + 300 * (1 - math.exp(-dt * 3))) ** 2)) * 2.2 * k)[..., None] \
                * np.array([1.0, 0.55, 0.22], np.float32)
            lay += (np.exp(-((_xx - hx) ** 2 + (_yy - hy) ** 2) / (2 * (25 + 50 * fl) ** 2)) * 4 * fl)[..., None] \
                * np.array([1.0, 0.95, 0.85], np.float32)
            flare(lay, hx, hy, 1.0 * fl + 0.3 * k, rings=fl > 0.05)
    return out + lay


# ------------------------------------------------------------------ subtitles
_sub = {}


def font(size, var=b"Bold Italic"):
    k = (size, var)
    if k not in _c:
        f = ImageFont.truetype(T["font_it"], size)
        f.set_variation_by_name(var)
        _c[k] = f
    return _c[k]


def subtitle(who, text):
    key = (who, text)
    if key in _sub:
        return _sub[key]
    f = font(40)
    maxw = 960
    words = text.split(" ")
    lines, cur = [], (who + ": ") if who else ""
    for wd in words:
        trial = cur + wd + " "
        if f.getlength(trial) > maxw and cur.strip():
            lines.append(cur.rstrip()); cur = wd + " "
        else:
            cur = trial
    lines.append(cur.rstrip())
    lh = 54
    im = Image.new("RGBA", (W, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        y = 20 + i * lh
        x = (W - f.getlength(ln)) / 2
        if i == 0 and who:
            nm = who + ":"
            d.text((x, y), nm, font=f, fill=ks.COL[who] + (255,))
            x += f.getlength(nm + " ")
            ln = ln[len(nm) + 1:]
        d.text((x, y), ln, font=f, fill=(246, 246, 250, 255))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * 0.8)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 2))
    out.alpha_composite(im)
    _sub[key] = out
    return out


# ------------------------------------------------------------------ frame
_vig = None


def _ramp(u, a, b):
    x = min(max((u - a) / (b - a), 0.0), 1.0)
    return x * x * (3 - 2 * x)


def frame(t, ss=2):
    """Final frame with cinematic transitions: white-flash carry into M, dissolve M -> C."""
    i, s = ks.shot_at(t)
    if s[2] == "C" and t - s[0] < 0.6:
        k = _ramp(t - s[0], 0.0, 0.6)
        a = np.asarray(_frame(s[0] - 1e-3, ss), np.float32)
        b = np.asarray(_frame(t, ss), np.float32)
        return Image.fromarray((a * (1 - k) + b * k).astype(np.uint8))
    return _frame(t, ss)


def _frame(t, ss=2):
    global _vig
    st = ks.setup(t)
    kind = st["shot"]
    if kind == "G":
        img = juno_shot(st)
    else:
        img = raw(st, ss)
        bg = st["bg"]
        if bg in ("navy", "cluster", "magneto"):
            m = planet_mask(st["cam"], st["objs"])[..., None]
            b = {"navy": bg_navy, "cluster": lambda: bg_cluster(st["u"]) * _ramp(st["u"], 0.0, 0.22),
                 "magneto": lambda: bg_magneto(t, st["u"])}[bg]()
            img = img + b * (1 - m)
        if kind == "K":
            m = planet_mask(st["cam"], st["objs"])[..., None]
            img = img + bg_redwisp() * (1 - m)
    if kind == "J":
        img = img * _ramp(st["u"], 0.0, 0.05)
    br = np.clip(img - 0.9, 0, None)
    img = img + (cv2.GaussianBlur(br, (0, 0), 8) * 0.5 + cv2.GaussianBlur(br, (0, 0), 30) * 0.5) * 0.5
    out = tonemap(img, 1.08)
    out = out + 0.25 * (out - cv2.GaussianBlur(out, (0, 0), 1.0))
    if _vig is None:
        _vig = (1 - 0.08 * (((_xx - W / 2) / (W / 2)) ** 2 + ((_yy - H / 2) / (H / 2)) ** 2) / 2).astype(np.float32)
    out = out * _vig[..., None]
    if kind == "M" and st["u"] * 3.0 < 0.35:
        out = out + (1 - _ramp(st["u"] * 3.0, 0.0, 0.35)) * 0.85
    out = out + np.random.default_rng(int(t * 1000)).normal(0, 0.004, (H, W, 1)).astype(np.float32)
    fr = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    who, line = st["line"]
    if line:
        sub = subtitle(who, line)
        a0 = ks.SHOTS[st["idx"]][0]
        a0 = a0 + ks.SUB_DELAY.get(kind, 0.0)
        al = 1.0 if a0 == 0 else min(1.0, (t - a0 + 1 / 30) / (0.12 if kind != "J" else 0.4))
        if al <= 0:
            sub = None
        elif al < 1:
            sub = sub.copy(); sub.putalpha(sub.getchannel("A").point(lambda v: int(v * al)))
        if sub is not None:
            fr.alpha_composite(sub, (0, 290))
    return fr.convert("RGB")


if __name__ == "__main__":
    out = sys.argv[1]
    ts = [float(x) for x in sys.argv[2].split(",")]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    ims = []
    for t in ts:
        im = np.asarray(frame(t, ss))[..., ::-1]
        ims.append(cv2.resize(im, (432, 768), interpolation=cv2.INTER_AREA))
    cols = 5
    rows = [np.hstack(ims[i:i + cols] + [np.zeros_like(ims[0])] * (cols - len(ims[i:i + cols]))) for i in range(0, len(ims), cols)]
    cv2.imwrite(out, np.vstack(rows))
