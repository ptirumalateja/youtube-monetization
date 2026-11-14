"""Compositor for the Kepler cut: kernel render + nebula backdrop + asteroid + film subtitles + grade."""
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
from proj import project  # noqa: E402
import kshots  # noqa: E402
from kassets import load  # noqa: E402

W, H = kshots.W, kshots.H
T = load()
_FONT = {}


def font(size, var=b"Bold Italic"):
    k = (size, var)
    if k not in _FONT:
        f = ImageFont.truetype(T["font_it"], size)
        f.set_variation_by_name(var)
        _FONT[k] = f
    return _FONT[k]


# ------------------------------------------------------------------ render
def raw(st, ss=2):
    tex = st["tex"]
    day, night, cloud = (T["kday"], T["knight"], T["kcloud"]) if tex == "kepler" else (T["earth_day"], T["earth_night"], T["earth_cloud"])
    sat = {"io": T["io"], "moon": T["moon"]}.get(tex, T["sat"])
    objs = np.array(st["objs"])
    return render(W, H, st["cam"], objs, len(objs), st["L"], day, night, cloud, T["jup"], sat, T["ring"],
                  T["sky"], T["neb"], st["prm"], ss)


def planet_mask(cam, objs):
    """1 where a pixel's ray hits any body (sphere approx with flattening on local y)."""
    th = cam[12]
    xs = (np.arange(W) + 0.5) / W * 2 - 1
    ys = 1 - (np.arange(H) + 0.5) / H * 2
    px = xs[None, :] * th * W / H
    py = ys[:, None] * th
    d = cam[9:12][None, None] + cam[3:6][None, None] * px[..., None] + cam[6:9][None, None] * py[..., None]
    d /= np.linalg.norm(d, axis=2, keepdims=True)
    m = np.zeros((H, W), np.float32)
    for P in objs:
        c, R, f = P[0:3], P[3], P[4]
        M = np.array([P[5:8], P[8:11], P[11:14]])          # rows = local axes
        sc = np.array([1 / R, 1 / (R * f), 1 / R])
        oc = (M @ (cam[0:3] - c)) * sc
        dl = (d @ M.T) * sc
        a2 = (dl * dl).sum(2)
        b = dl @ oc
        cc = oc @ oc - 1.0
        disc = b * b - a2 * cc
        m = np.maximum(m, (disc > 0).astype(np.float32))
    return cv2.GaussianBlur(m, (0, 0), 1.0)


def nebula_bg(name, t, u, scale=1.15, gain=0.55):
    img = T["nebimg"][name]
    h, w = img.shape[:2]
    s = max(W / w, H / h) * (scale + 0.05 * u)
    im = cv2.resize(img, (int(w * s) + 2, int(h * s) + 2), interpolation=cv2.INTER_AREA)
    y0 = (im.shape[0] - H) // 2
    x0 = (im.shape[1] - W) // 2
    im = im[y0:y0 + H, x0:x0 + W]
    lin = np.power(np.clip(im, 0, 1), 2.2) * gain
    return lin.astype(np.float32)


_patch = {}


def neb_patch(name):
    """A soft nebula cloud tucked into the upper-right corner, like a distant glow behind the planet."""
    if name not in _patch:
        img = T["nebimg"][name]
        c = img[img.shape[0] // 5: img.shape[0] // 5 + 700, img.shape[1] // 3: img.shape[1] // 3 + 700]
        c = cv2.resize(c, (620, 620))
        yy, xx = np.mgrid[0:620, 0:620]
        r = np.sqrt((xx - 310) ** 2 + (yy - 310) ** 2) / 310
        a = np.clip(1 - r, 0, 1) ** 1.6
        lay = np.zeros((H, W, 3), np.float32)
        lay[120:740, 600:1080] = (np.power(c, 2.2) * a[..., None] * 0.55)[:, :480]
        _patch[name] = lay
    return _patch[name]


# ------------------------------------------------------------------ asteroid for the GRS shot
def asteroid(st, t):
    """One burning rock streaks in from the upper right, bends hard and slams into the clouds."""
    lay = np.zeros((H, W, 3), np.float32)
    u = st["u"]
    a0, a1 = 0.10, 0.62
    if u < a0:
        return lay
    # screen-space cubic: enters top-right heading down-left (toward where Earth would be), hooks into the GRS
    P0 = np.array([1160.0, 180.0]); P1 = np.array([980.0, 560.0]); P2 = np.array([860.0, 980.0]); P3 = np.array([735.0, 1290.0])
    def at(s):
        m = 1 - s
        return m ** 3 * P0 + 3 * m * m * s * P1 + 3 * m * s * s * P2 + s ** 3 * P3
    s_now = min((u - a0) / (a1 - a0), 1.0) ** 1.35
    if s_now < 1.0:
        ss = np.linspace(max(s_now - 0.35, 0), s_now, 60)
        pts = [at(s) for s in ss]
        for k in range(len(pts) - 1):
            f = (k + 1) / len(pts)
            w = max(1, int(26 * f ** 1.4))
            cv2.line(lay, tuple(int(v) for v in pts[k]), tuple(int(v) for v in pts[k + 1]),
                     (2.4 * f, 1.1 * f, 0.3 * f), w, cv2.LINE_AA)
        hx, hy = at(s_now)
        cv2.circle(lay, (int(hx), int(hy)), 16, (3.0, 2.6, 2.0), -1, cv2.LINE_AA)
    else:
        dt = (u - a1) * (st_dur(st))
        cx, cy = 735, 1290
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        ex = (xx - cx) / 1.0; ey = (yy - cy) / 0.32                  # perspective-flattened on the cloud deck
        r = np.sqrt(ex * ex + ey * ey)
        flash = math.exp(-dt * 9)
        glow = np.exp(-(r / (60 + 260 * (1 - math.exp(-dt * 3)))) ** 2)
        ringr = 40 + 520 * (1 - math.exp(-dt * 2.2))
        ring = np.exp(-((r - ringr) / (14 + 30 * dt)) ** 2) * math.exp(-dt * 1.6)
        core = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * (40 + 90 * flash) ** 2)) * flash
        lay += core[..., None] * np.array([6.0, 5.4, 4.6], np.float32)
        lay += glow[..., None] * np.array([2.0, 0.75, 0.18], np.float32) * (0.35 + 0.65 * math.exp(-dt * 1.2))
        lay += ring[..., None] * np.array([1.6, 1.0, 0.55], np.float32)
        # plume rising off the deck
        ph = 340 * (1 - math.exp(-dt * 2.5))
        pl = np.exp(-((xx - cx) / (50 + 40 * dt)) ** 2 - ((yy - (cy - ph * 0.6)) / (ph * 0.55 + 10)) ** 2)
        lay += pl[..., None] * np.array([1.8, 0.8, 0.25], np.float32) * math.exp(-dt * 1.4)
    return lay


def st_dur(st):
    s = kshots.SHOTS[st["idx"]]
    return s[1] - s[0]


# ------------------------------------------------------------------ subtitles
_sub = {}


def subtitle(who, text, italic_only=False):
    key = (who, text)
    if key in _sub:
        return _sub[key]
    fb = font(50, b"Bold Italic")
    fr = font(46, b"Italic")
    maxw = 880
    words = text.split(" ")
    first = (who + ": ") if who else ""
    lines, cur = [], first
    f_main = fr if italic_only else fb
    for wd in words:
        trial = cur + wd + " "
        if f_main.getlength(trial) > maxw and cur.strip():
            lines.append(cur.rstrip()); cur = wd + " "
        else:
            cur = trial
    lines.append(cur.rstrip())
    lh = 66
    im = Image.new("RGBA", (W, lh * len(lines) + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, ln in enumerate(lines):
        y = 20 + i * lh
        wl = f_main.getlength(ln)
        x = (W - wl) / 2
        if i == 0 and who:
            nm = who + ":"
            d.text((x, y), nm, font=f_main, fill=COLR(who))
            x += f_main.getlength(nm + " ")
            ln = ln[len(nm) + 1:]
        d.text((x, y), ln, font=f_main, fill=(244, 244, 248, 255))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.85)))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.alpha_composite(sh, (0, 3))
    out.alpha_composite(im)
    _sub[key] = out
    return out


def COLR(who):
    return kshots.COL.get(who, (255, 255, 255)) + (255,)


# ------------------------------------------------------------------ frame
_vig = None


def frame(t, ss=2):
    global _vig
    st = kshots.setup(t)
    img = raw(st, ss).astype(np.float32)
    if st["bg"]:
        m = planet_mask(st["cam"], st["objs"])
        img = img + nebula_bg(st["bg"], t, st["u"]) * (1 - m[..., None])
    if st["nebpatch"]:
        m = planet_mask(st["cam"], st["objs"])
        img = img + neb_patch(st["nebpatch"]) * (1 - m[..., None])
    if st["shot"] == "G":
        img = img + asteroid(st, t)
    br = np.clip(img - 0.85, 0, None)
    img = img + (cv2.GaussianBlur(br, (0, 0), 10) * 0.5 + cv2.GaussianBlur(br, (0, 0), 40) * 0.5) * 0.7
    out = tonemap(img, 1.05)
    out = out + 0.5 * (out - cv2.GaussianBlur(out, (0, 0), 1.2))
    # cool, deep grade with lifted blacks (never dead black)
    out = out * np.array([0.97, 0.99, 1.03], np.float32) + np.array([0.010, 0.014, 0.026], np.float32)
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W]
        _vig = (1 - 0.10 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2).astype(np.float32)
    out = out * _vig[..., None]
    out = out + np.random.default_rng(int(t * 1000)).normal(0, 0.006, (H, W, 1)).astype(np.float32)
    fr = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")
    who, line = st["line"]
    sub = subtitle(who, line, italic_only=(who is None))
    a0 = kshots.SHOTS[st["idx"]][0]
    al = 1.0 if a0 == 0 else min(1.0, (t - a0 + 1 / 30) / 0.12)
    if al < 1:
        sub = sub.copy(); sub.putalpha(sub.getchannel("A").point(lambda v: int(v * al)))
    y = 300
    fr.alpha_composite(sub, (0, y))
    return fr.convert("RGB")


if __name__ == "__main__":
    out = sys.argv[1]
    ts = [float(x) for x in sys.argv[2].split(",")]
    ss = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    ims = []
    for t in ts:
        im = np.asarray(frame(t, ss))[..., ::-1]
        ims.append(cv2.resize(im, (432, 768), interpolation=cv2.INTER_AREA))
    rows = [np.hstack(ims[i:i + 5] + [np.zeros_like(ims[0])] * (5 - len(ims[i:i + 5]))) for i in range(0, len(ims), 5)]
    cv2.imwrite(out, np.vstack(rows))
