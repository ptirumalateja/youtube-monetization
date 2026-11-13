"""Frame compositor v2: planets (kernel) + fireball swarm + impacts/scars + bloom + grade + chat UI."""
import math
import os
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import shots
from scene import tonemap, ease
from proj import project

W, H = 1080, 1920
EMO = os.path.join(os.environ.get("JB_TEX", "/tmp/claude-0/-home-user/be075317-9b13-5dc2-bdf1-585b08c9f335/scratchpad/tex"), "emoji")
F_SEMI = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
F_BOLD = "/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf"
F_BLACK = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
F_MED = "/usr/share/fonts/opentype/inter/Inter-Medium.otf"

# ------------------------------------------------------------------ chat script
# (time, who, text). S = Saturn, E = Earth, E! = Earth big, T = Earth typing, X = system line.
CHAT = [
    (1.33, "S", "Earth, you're so tiny {1f602}"),
    (2.33, "E", "I have life {1f331}"),
    (3.45, "S", "I have rings {1f48d}\nand REAL gravity {1f4aa}"),
    (4.50, "S", "who protects YOU? {1f60f}"),
    (5.65, "T", ""),
    (7.35, "E!", "I have him."),
    (10.20, "S", "...nvm {1f636}"),
    (10.90, "X", "Saturn left the chat"),
]
CHAT_CLEAR = [(0.0, 1.3), (5.6, 5.65), (9.0, 10.20)]
HOOK_TITLE = ("EARTH HAS A", "BODYGUARD {1f6e1}")
END_TITLE = ("TAG YOUR", "JUPITER {1f6e1}")
END_T = 12.05


def chat_anchor(t):
    """Bottom y of the chat stack: low in the Saturn/Earth close-ups, high over Jupiter later."""
    name, a, b = shots.shot_at(t)
    return 1425 if name in ("B1", "B2", "B3") else 1440


def _emoji(code, size):
    im = Image.open(os.path.join(EMO, code + ".png")).convert("RGBA")
    return im.resize((size, size), Image.LANCZOS)


def _split(text):
    out = []
    i = 0
    while i < len(text):
        j = text.find("{", i)
        if j < 0:
            out.append(("t", text[i:])); break
        if j > i:
            out.append(("t", text[i:j]))
        k = text.find("}", j)
        out.append(("e", text[j + 1:k]))
        i = k + 1
    return out


def rich_size(text, font, esz):
    w = 0
    for kind, s in _split(text):
        w += font.getlength(s) if kind == "t" else esz + 4
    return int(w)


def draw_rich(img, xy, text, font, fill, esz):
    d = ImageDraw.Draw(img)
    x, y = xy
    asc, desc = font.getmetrics()
    for kind, s in _split(text):
        if kind == "t":
            d.text((x, y), s, font=font, fill=fill)
            x += font.getlength(s)
        else:
            img.alpha_composite(_emoji(s, esz), (int(x + 2), int(y + (asc + desc - esz) / 2 + 2)))
            x += esz + 4


_bubble_cache = {}


def bubble(who, text):
    key = (who, text)
    if key in _bubble_cache:
        return _bubble_cache[key]
    big = who == "E!"
    fs = 118 if big else 60
    font = ImageFont.truetype(F_BOLD if big else F_SEMI, fs)
    esz = int(fs * 1.05)
    lines = text.split("\n")
    lh = int(fs * 1.25)
    if who == "T":
        tw = 120
        nlines = 1
    else:
        tw = max(rich_size(l, font, esz) for l in lines)
        nlines = len(lines)
    padx, pady = (40, 24) if not big else (56, 34)
    bw, bh = tw + 2 * padx, lh * nlines + 2 * pady
    av = 80
    name_h = 44
    gap = 14
    Wb = bw + av + gap + 30
    Hb = bh + name_h + 30
    im = Image.new("RGBA", (Wb, Hb), (0, 0, 0, 0))
    left = who == "S"
    bx = av + gap if left else 0
    by = name_h
    col = (40, 40, 46, 240) if left else (10, 132, 255, 248)
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((bx, by + 8, bx + bw, by + bh + 8), 44, fill=(0, 0, 0, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    if big:
        gl = Image.new("RGBA", im.size, (0, 0, 0, 0))
        ImageDraw.Draw(gl).rounded_rectangle((bx, by, bx + bw, by + bh), 56, fill=(70, 160, 255, 220))
        im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(20)))
    ImageDraw.Draw(im).rounded_rectangle((bx, by, bx + bw, by + bh), 46 if not big else 56, fill=col)
    if who == "T":
        d = ImageDraw.Draw(im)
        for i in range(3):
            cx = bx + padx + 20 + i * 40
            cy = by + bh // 2
            d.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(255, 255, 255, 235))
    else:
        for i, l in enumerate(lines):
            draw_rich(im, (bx + padx, by + pady - 4 + i * lh), l, font, (255, 255, 255, 255), esz)
    nf = ImageFont.truetype(F_MED, 36)
    d = ImageDraw.Draw(im)
    if left:
        im.alpha_composite(_emoji("1fa90", av), (0, by + bh - av))
        d.text((bx + 14, 0), "Saturn", font=nf, fill=(235, 235, 245, 240))
    else:
        im.alpha_composite(_emoji("1f30d", av), (bw + gap, by + bh - av))
        d.text((bw - 14 - nf.getlength("Earth"), 0), "Earth", font=nf, fill=(235, 235, 245, 240))
    _bubble_cache[key] = im
    return im


def system_line(text):
    f = ImageFont.truetype(F_BOLD, 54)
    w = int(f.getlength(text)) + 80
    im = Image.new("RGBA", (w, 100), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, 98), 49, fill=(0, 0, 0, 170))
    ImageDraw.Draw(im).text((40, 17), text, font=f, fill=(255, 255, 255, 255))
    return im


def title(lines, size=128, color=(255, 255, 255, 255)):
    f = ImageFont.truetype(F_BLACK, size)
    esz = int(size * 0.95)
    ws = [rich_size(l, f, esz) for l in lines]
    w = max(ws) + 90; lh = int(size * 1.08)
    im = Image.new("RGBA", (w, lh * len(lines) + 70), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    for i, l in enumerate(lines):
        draw_rich(sh, ((w - ws[i]) / 2, 35 + i * lh), l, f, (0, 0, 0, 255), esz)
    sh = sh.filter(ImageFilter.GaussianBlur(16))
    for _ in range(3):
        im.alpha_composite(sh)
    for i, l in enumerate(lines):
        draw_rich(im, ((w - ws[i]) / 2, 35 + i * lh), l, f, color, esz)
    return im


def pop(t, t0, dur=0.2):
    x = (t - t0) / dur
    if x <= 0:
        return 0.0, 0.0
    if x >= 1:
        return 1.0, 1.0
    y = x - 1
    sc = 1 + 2.70158 * y ** 3 + 1.70158 * y ** 2   # easeOutBack
    return min(1.0, x * 3.0), 0.6 + 0.4 * sc


def _fade(im, a):
    if a >= 1:
        return im
    al = np.asarray(im).copy(); al[..., 3] = (al[..., 3] * a).astype(np.uint8)
    return Image.fromarray(al)


def chat_layer(t):
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if t >= END_T:
        return ov
    for a, b in CHAT_CLEAR:
        if a <= t < b:
            return ov
    last_clear = max([c[1] for c in CHAT_CLEAR if c[1] <= t] + [0.0])
    msgs = [m for m in CHAT if last_clear - 1e-6 <= m[0] <= t]
    if any(m[1] == "E!" for m in msgs):
        msgs = [m for m in msgs if m[1] != "T"]
    if not msgs:
        return ov
    msgs = msgs[-3:]
    y = chat_anchor(t)
    for m in reversed(msgs):
        im = system_line(m[2]) if m[1] == "X" else bubble(m[1], m[2])
        a, sc = pop(t, m[0], 0.32 if m[1] == "E!" else 0.2)
        if sc <= 0:
            continue
        h = im.size[1]
        imw = im.resize((max(1, int(im.size[0] * sc)), max(1, int(im.size[1] * sc))), Image.LANCZOS) if sc != 1 else im
        imw = _fade(imw, a)
        if m[1] == "S":
            x = 60
        elif m[1] == "X":
            x = (W - imw.size[0]) // 2
        else:
            x = W - 60 - imw.size[0]
        ov.alpha_composite(imw, (int(x), max(0, int(y - imw.size[1]))))
        y -= int((h + 10) * min(1.0, (t - m[0]) / 0.07))
    return ov


# ------------------------------------------------------------------ fireballs
def _visible(cam, p, objs):
    o = cam[0:3]
    d = np.asarray(p) - o
    dist = np.linalg.norm(d); d = d / dist
    for P in objs:
        c = P[0:3]; R = P[3]
        oc = o - c
        b = oc @ d
        cc = oc @ oc - R * R
        disc = b * b - cc
        if disc > 0:
            tt = -b - math.sqrt(disc)
            if 0 < tt < dist - 1e-3:
                return False
    return True


PX_PER_UNIT = 960 / math.tan(math.radians(23))   # ~2262 px per world unit at depth 1
FIRE_OUT = np.array([0.05, 0.30, 1.10], np.float32)   # BGR, orange flame
FIRE_IN = np.array([0.35, 0.85, 1.55], np.float32)    # BGR, yellow-white core


def _trail(lay, pts2, widths, col):
    """Draw a tapered trail into a scratch ROI with overwrite (no beads), then add."""
    xs = [p[0] for p in pts2]; ys = [p[1] for p in pts2]
    pad = int(max(widths)) + 4
    x0, x1 = int(max(min(xs) - pad, 0)), int(min(max(xs) + pad, W))
    y0, y1 = int(max(min(ys) - pad, 0)), int(min(max(ys) + pad, H))
    if x1 <= x0 or y1 <= y0:
        return
    m = np.zeros((y1 - y0, x1 - x0), np.float32)
    for k in range(len(pts2) - 1):
        f = (k + 1) / len(pts2)
        cv2.line(m, (int((pts2[k][0] - x0) * 4), int((pts2[k][1] - y0) * 4)),
                 (int((pts2[k + 1][0] - x0) * 4), int((pts2[k + 1][1] - y0) * 4)),
                 float(f ** 1.6), max(1, int(widths[k + 1])), cv2.LINE_AA, shift=2)
    lay[y0:y1, x0:x1] += m[..., None] * col


def fireballs(t, cam, objs):
    lay = np.zeros((H, W, 3), np.float32)      # additive light (BGR, linear)
    scar = np.zeros((H, W), np.float32)        # darkening on Jupiter's clouds
    sw = shots.asteroid_state(t)
    if not sw:
        return lay, scar, []
    flashes = []
    for idx, a in enumerate(sw):
        ts, ps, hit = a["ts"], a["ps"], a["hit"]
        if t < ts[0]:
            continue
        if hit is not None and t >= hit[0]:
            flashes.append((t - hit[0], hit[1], idx))
            continue
        i1 = np.searchsorted(ts, t)
        i0 = np.searchsorted(ts, t - 0.5)
        seg = ps[max(i0, 0):max(i1, 1)]
        if len(seg) < 2:
            continue
        pts = []
        for p in seg:
            x, y, z = project(cam, p)
            if z <= 0.5 or not _visible(cam, p, objs):
                pts.append(None)
            else:
                pts.append((x, y, z))
        # longest visible tail run ending at the head
        run = []
        for q in reversed(pts):
            if q is None:
                break
            run.append(q)
        run = run[::-1]
        if len(run) >= 2:
            ws = [PX_PER_UNIT / q[2] * 0.20 * ((k + 1) / len(run)) ** 1.2 for k, q in enumerate(run)]
            _trail(lay, run, ws, FIRE_OUT)
            _trail(lay, run, [w * 0.38 for w in ws], FIRE_IN)
        hd = pts[-1]
        if hd is not None:
            pu = PX_PER_UNIT / hd[2]
            r = max(3, pu * 0.11)
            rng = np.random.default_rng(int(t * 30) * 131 + idx)
            # turbulent flame head: jittered blobs
            for j in range(7):
                ox, oy = rng.normal(0, r * 0.45, 2)
                rr = r * rng.uniform(0.6, 1.2)
                cv2.circle(lay, (int(hd[0] + ox), int(hd[1] + oy)), max(2, int(rr * 1.8)), tuple(float(v) for v in FIRE_OUT * 0.55), -1, cv2.LINE_AA)
            cv2.circle(lay, (int(hd[0]), int(hd[1])), max(2, int(r)), tuple(float(v) for v in FIRE_IN * 1.4), -1, cv2.LINE_AA)
            # embers shed behind
            if len(run) > 6:
                bx, by = run[-6][0], run[-6][1]
                for _ in range(8):
                    sx = bx + rng.normal(0, r * 2.0); sy = by + rng.normal(0, r * 2.0)
                    cv2.circle(lay, (int(sx), int(sy)), max(1, int(r * 0.22)), tuple(float(v) for v in FIRE_OUT * 1.6), -1, cv2.LINE_AA)
    J = objs[0]
    for dt, p, idx in flashes:
        x, y, z = project(cam, p)
        nrm = (p - J[0:3]); nrm /= np.linalg.norm(nrm)
        vdir = (cam[0:3] - p); vdir /= np.linalg.norm(vdir)
        if nrm @ vdir <= 0.05 or not _visible(cam, p + nrm * 0.05, objs[1:]):
            continue
        sc = PX_PER_UNIT / z
        fs = max(0.15, float(nrm @ vdir))
        # screen direction of the surface normal = minor axis of the projected disc
        x2, y2, _ = project(cam, p + nrm * 0.5)
        ang = math.degrees(math.atan2(y2 - y, x2 - x))
        # scar: dark, elongated along the cloud bands, stays
        sr = sc * (0.2 + 0.45 * (1 - math.exp(-dt * 2.5)))
        cv2.ellipse(scar, (int(x), int(y)), (max(int(sr * fs), 1), max(int(sr * 1.4), 2)), ang, 0, 360, 0.8, -1, cv2.LINE_AA)
        if dt > 1.4:
            continue
        k = math.exp(-dt * 3.0)
        # orange fireball flash (kept below clipping)
        cv2.ellipse(lay, (int(x), int(y)), (max(int(sc * 0.35 * fs * (0.5 + dt)), 2), max(int(sc * 0.35 * (0.5 + dt)), 2)), ang, 0, 360,
                    (0.15 * k, 0.75 * k, 2.0 * k), -1, cv2.LINE_AA)
        cv2.ellipse(lay, (int(x), int(y)), (max(int(sc * 0.13 * fs), 2), max(int(sc * 0.13), 2)), ang, 0, 360,
                    (0.9 * k, 1.6 * k, 2.4 * k), -1, cv2.LINE_AA)
        # one soft shock ring lying on the sphere
        rr = sc * (0.2 + 1.1 * (1 - math.exp(-dt * 2.4)))
        cv2.ellipse(lay, (int(x), int(y)), (max(int(rr * fs), 1), max(int(rr), 2)), ang, 0, 360,
                    (0.10 * k, 0.38 * k, 0.85 * k), max(3, int(sc * 0.12)), cv2.LINE_AA)
        # debris sparks thrown off the impact
        if dt < 0.6:
            rng = np.random.default_rng(idx * 17)
            for j in range(10):
                th = rng.uniform(0, 2 * math.pi); sp = rng.uniform(0.6, 1.6) * sc
                d = sp * dt * 2.2
                sx = x + math.cos(th) * d; sy = y + math.sin(th) * d * 0.8 - 0.4 * d
                cv2.circle(lay, (int(sx), int(sy)), max(1, int(sc * 0.05)), (0.3 * k, 1.0 * k, 2.2 * k), -1, cv2.LINE_AA)
    soft = cv2.GaussianBlur(lay, (0, 0), 2.0)
    glow = cv2.GaussianBlur(lay, (0, 0), 14)
    scar = cv2.GaussianBlur(scar, (0, 0), 5)
    return (soft * 1.0 + glow * 0.8)[..., ::-1].copy(), scar, flashes


PULSES = [0.02, 7.35]


def gravity_pulse(img, t, cam, objs):
    """Radial refraction wave out of Jupiter: the pull made visible."""
    for t0 in PULSES:
        dt = t - t0
        if not (0 <= dt < 0.9):
            continue
        J = objs[0]
        jx, jy, jz = project(cam, J[0:3])
        if jz <= 0:
            continue
        rj = J[3] / jz / cam[12] * 960
        R = rj * (1.0 + 1.6 * dt / 0.9)
        amp = 28 * (1 - dt / 0.9) ** 1.5
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        dx, dy = xx - jx, yy - jy
        r = np.sqrt(dx * dx + dy * dy) + 1e-3
        w = np.exp(-((r - R) / 60.0) ** 2) * amp
        mx = xx - dx / r * w; my = yy - dy / r * w
        img = cv2.remap(img.astype(np.float32), mx.astype(np.float32), my.astype(np.float32), cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        # faint bright crest
        img = (img + (np.exp(-((r - R) / 25.0) ** 2) * 0.05 * (1 - dt / 0.9))[..., None] * np.array([1.0, 0.8, 0.6], np.float32)).astype(np.float32)
    return img


# ------------------------------------------------------------------ frame
_vig = None


def finish(raw, t, cam, objs, name):
    global _vig
    fb, scar, flashes = fireballs(t, cam, objs)
    img = raw * (1 - scar[..., None] * np.array([0.6, 0.68, 0.75], np.float32)) + fb
    img = gravity_pulse(img, t, cam, objs)
    fl = sum(math.exp(-d * 7) for d, _, _ in flashes if d < 1)
    img = img * (1 + 0.08 * min(fl, 2))
    br = np.clip(img - 0.9, 0, None)
    bloom = cv2.GaussianBlur(br, (0, 0), 8) * 0.5 + cv2.GaussianBlur(br, (0, 0), 30) * 0.5 + cv2.GaussianBlur(br, (0, 0), 90) * 0.4
    img = img + bloom * 0.6
    out = tonemap(img, 1.0)
    out = out * 0.97 + np.array([0.012, 0.008, 0.022], np.float32)
    if _vig is None:
        yy, xx = np.mgrid[0:H, 0:W]
        _vig = (1 - 0.08 * (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 2).astype(np.float32)
    out = out * _vig[..., None]
    rng = np.random.default_rng(int(t * 1000))
    out = out + rng.normal(0, 0.007, (H, W, 1)).astype(np.float32)
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).convert("RGBA")


_title_cache = {}


def _title_pill(text):
    if text not in _title_cache:
        f = ImageFont.truetype(F_BOLD, 50)
        w = int(f.getlength(text)) + 80
        im = Image.new("RGBA", (w, 96), (0, 0, 0, 0))
        ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, 94), 47, fill=(255, 255, 255, 235))
        ImageDraw.Draw(im).text((40, 16), text, font=f, fill=(20, 20, 26, 255))
        _title_cache[text] = im
    return _title_cache[text]


def _title(key, lines, size):
    if key not in _title_cache:
        _title_cache[key] = title(lines, size)
    return _title_cache[key]


def overlay(frame, t):
    frame.alpha_composite(chat_layer(t))
    if t < 1.3:
        ti = _title("hook", HOOK_TITLE, 104)
        frame.alpha_composite(ti, ((W - ti.size[0]) // 2, 1440 - ti.size[1] + 20))
    if 1.3 <= t < 2.25:
        pl = _title_pill("earlier...")
        a = min(1.0, (t - 1.3) / 0.1) * min(1.0, (2.25 - t) / 0.15)
        frame.alpha_composite(_fade(pl, a), ((W - pl.size[0]) // 2, 1090))
    if t >= END_T:
        a, sc = pop(t, END_T + 0.05, 0.3)
        if sc > 0:
            ti = _title("end", END_TITLE, 124)
            ti = _fade(ti.resize((int(ti.size[0] * sc), int(ti.size[1] * sc)), Image.LANCZOS), a)
            frame.alpha_composite(ti, ((W - ti.size[0]) // 2, 470 - ti.size[1] // 2))
    return frame.convert("RGB")
