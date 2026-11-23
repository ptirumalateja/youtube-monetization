#!/usr/bin/env python3
"""Hole-becomes-hill reel (vinyl stickman hero + taller darker crowd). 1080x1920, 30 fps, DUR s.
usage:  render_hh.py prep                      (render crowd sprites once)
        render_hh.py frames OUTDIR [k] [t0 t1 step]
        render_hh.py sheet OUT.png t1 t2 ...   (preview frames, k=2)
        render_hh.py video OUT.mp4 AUDIO.wav FRAMESDIR
"""
import sys, os, math, json, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vinyl as V, hh_poses as HP

W, H = 1080, 1920
FPS = 30; DUR = 18.2
SC = os.environ.get("HH_SCRATCH", "/tmp/claude-0/-home-user-youtube-monetization/a23e2797-2c3e-5eef-b6ce-d7544fada057/scratchpad/hh")
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"

def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t

# ------------------------------------------------------------------ world
PIT_W, PIT_D, HILL_W, HILL_H = 330.0, 640.0, 820.0, 900.0
def m_of(t): return sm((t - 8.2) / 5.1)
def pit_prof(x):
    a = abs(x); return -PIT_D * (1 - sm((a - PIT_W) / 90.0))
def hill_prof(x):
    a = abs(x); return HILL_H * (0.5 * (1 + math.cos(math.pi * min(a / HILL_W, 1.0))))
def surf(x, t):
    m = m_of(t); return lerp(pit_prof(x), hill_prof(x), m)

# ------------------------------------------------------------------ camera
KEYS = [(0.0, -880, 480, 0.54), (3.0, -800, 520, 0.58), (4.4, -560, 420, 0.66), (5.2, -150, 0, 0.62), (6.0, 0, -250, 0.60),
        (7.4, 0, -250, 0.80), (9.1, 0, -200, 0.80), (11.0, -100, 150, 0.62), (13.3, -330, 480, 0.46), (15.7, -300, 560, 0.46),
        (16.2, 0, 1380, 0.80), (18.2, 0, 1400, 0.92)]
def cam(t):
    for i in range(len(KEYS) - 1):
        a, b = KEYS[i], KEYS[i + 1]
        if a[0] <= t <= b[0]:
            u = sm((t - a[0]) / (b[0] - a[0]))
            return lerp(a[1], b[1], u), lerp(a[2], b[2], u), lerp(a[3], b[3], u)
    k = KEYS[-1]; return k[1], k[2], k[3]
def shake(t):
    s = 0.0
    for t0, amp in ((4.75, 14), (5.85, 26), (13.4, 12)):
        if t0 <= t < t0 + 0.5: s += amp * (1 - (t - t0) / 0.5) * math.sin((t - t0) * 70)
    return s

# ------------------------------------------------------------------ actors
CROWD_X0 = [-740, -950, -1160, -1370, -1580]
def crowd_state(i, t):
    x = CROWD_X0[i] - 380 * sm((t - 9.0) / 4.2)
    y = surf(x, t)
    bob = 0.0
    if t < 3.1 and i in (1, 2): pose, mood, bob = "dig", "strain", 14 * abs(math.sin((t * 2.2 + i)))
    elif i == 0 and 4.4 <= t < 5.15: pose, mood = "shove", "smirk"; x += 60 * sm((t - 4.4) / 0.3)
    elif t >= 13.3: pose, mood = "lookup", "shocked"
    elif t < 9.0: pose, mood = "stand", "smirk"
    else: pose, mood = "stand", "neutral"
    return pose, mood, x, y + bob
def hero_state(t):
    hx = -520.0; yaw = -0.35; mood = "determined"
    sway = 8 * math.sin(t * 2.4)
    if t < 4.55: P = dict(V.POSES["guard"]); P["pelvis"] = (0, 470 + abs(sway) * 0.8, 0)
    elif t < 5.9:
        u = sm((t - 4.55) / 0.3); P = HP.lerp_pose("guard", "fall", u); mood = "shocked"
        hx = lerp(-520, 0, sm((t - 4.55) / 1.05)); yaw = lerp(-0.35, -0.5, u)
    elif t < 7.4:
        u = sm((t - 5.9) / 0.45); P = HP.lerp_pose("fall", "sad", u); mood = "neutral"; hx = 0.0; yaw = -0.5
    elif t < 8.1:
        u = sm((t - 7.4) / 0.6); P = HP.lerp_pose("sad", "dig", u); mood = "strain" if u > 0.5 else "neutral"; hx = 0.0; yaw = lerp(-0.5, -0.95, u)
    elif t < 13.3:
        per = 0.8 if t < 9.0 else 0.72
        w = 0.5 - 0.5 * math.cos(2 * math.pi * (t - 8.1) / per)
        P = HP.lerp_pose("dig", "dig_up", w); mood = "strain"; hx = 0.0; yaw = -0.95
    elif t < 13.9:
        u = sm((t - 13.3) / 0.45); P = HP.lerp_pose("dig", "triumph", u); mood = "joy" if u > 0.4 else "strain"; hx = 0.0; yaw = lerp(-0.95, -0.2, u)
    elif t < 15.8:
        P = dict(V.POSES["triumph"]); mood = "joy"; hx = 0.0; yaw = -0.2 + 0.12 * math.sin((t - 13.9) * 2)
    elif t < 16.3:
        u = sm((t - 15.8) / 0.5); P = HP.lerp_pose("triumph", "guard", u); mood = "determined"; hx = 0.0; yaw = lerp(-0.2, 0.0, u)
    else:
        P = dict(V.POSES["guard"]); mood = "determined"; hx = 0.0; yaw = 0.0
    if t < 4.85: hy = surf(hx, t)
    else:
        fall = -PIT_D * min(((t - 4.85) / 1.0) ** 2, 1.0)
        hy = max(fall, surf(hx, t)) if t < 6.0 else surf(hx, t)
    if t < 4.85: hy = 0.0
    return P, mood, yaw, hx, hy

# ------------------------------------------------------------------ sprites
HERO_D = 1500.0; HERO_T = np.array([0, 470, 0], np.float32)
CROWD_D = 1900.0; CROWD_T = np.array([0, 600, 0], np.float32)
CROWD_SET = [("stand", "smirk"), ("stand", "neutral"), ("dig", "strain"), ("shove", "smirk"), ("lookup", "shocked")]
def _cam(Dd, T, yaw):
    C = np.array([Dd * math.sin(yaw), 520, Dd * math.cos(yaw)], np.float32); r, u, f = V.lookat(C, T)
    return C, r, u, f, float(np.linalg.norm(C - T))
def make_sprite(P, mood, Dd, T, yaw, **kw):
    C, r, u, f, dist = _cam(Dd, T, yaw)
    P = dict(P); P["head_yaw"] = P.get("head_yaw", 0.0)
    rgb, a = V.render(P, mood, C, r, u, f, sprite=True, **kw)
    return rgb, a, dist
def crop(rgb, a):
    ys, xs = np.nonzero(a > 0.01)
    if len(xs) == 0: return None
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([rgb[y0:y1, x0:x1], a[y0:y1, x0:x1, None]])
    return Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA"), x0, y0
def paste_sprite(img, spr, sx, sy, q):
    im, x0, y0 = spr
    w, h = max(1, int(im.width * q)), max(1, int(im.height * q))
    s = im.resize((w, h), Image.LANCZOS)
    img.alpha_composite(s, (int(round(sx + (x0 - W / 2) * q)), int(round(sy + (y0 - H / 2) * q)))) if (0 <= sx + (x0 - W / 2) * q and 0 <= sy + (y0 - H / 2) * q and sx + (x0 - W / 2) * q + w <= W and sy + (y0 - H / 2) * q + h <= H) else _paste_clip(img, s, int(round(sx + (x0 - W / 2) * q)), int(round(sy + (y0 - H / 2) * q)))
def _paste_clip(img, s, x, y):
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); layer.paste(s, (x, y)); img.alpha_composite(layer)

_CROWD = {}
def load_crowd():
    if _CROWD: return
    for pose, mood in CROWD_SET:
        fn = f"{SC}/crowd_{pose}_{mood}.png"; meta = json.load(open(fn + ".json"))
        _CROWD[(pose, mood)] = (Image.open(fn).convert("RGBA"), meta["x0"], meta["y0"], meta["dist"])
def prep():
    V.RES["k"] = 1
    for pose, mood in CROWD_SET:
        rgb, a, dist = make_sprite(V.POSES[pose], mood, CROWD_D, CROWD_T, -0.95, scale=1.3, tone=0.42)
        im, x0, y0 = crop(rgb, a); im.save(f"{SC}/crowd_{pose}_{mood}.png"); json.dump(dict(x0=int(x0), y0=int(y0), dist=dist), open(f"{SC}/crowd_{pose}_{mood}.png.json", "w"))
        print("crowd", pose, mood, im.size)

# ------------------------------------------------------------------ background
def lerp_col(a, b, t): return tuple(int(lerp(a[i], b[i], t)) for i in range(3))
_BG = {}
def sky_img():
    if "sky" not in _BG:
        yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
        top = np.array([22, 28, 60], np.float32); mid = np.array([118, 58, 104], np.float32); hor = np.array([255, 176, 112], np.float32)
        a = np.clip(yy / 0.55, 0, 1); b = np.clip((yy - 0.55) / 0.45, 0, 1)
        col = np.where(yy < 0.55, top * (1 - a) + mid * a, mid * (1 - b) + hor * b)
        _BG["sky"] = np.repeat(col, W, axis=1).astype(np.uint8)
    return _BG["sky"]
def draw_bg(t, cx, cy, z):
    img = Image.fromarray(sky_img(), "RGB"); d = ImageDraw.Draw(img)
    X = lambda x: W / 2 + (x - cx) * z
    Y = lambda y: H / 2 - (y - cy) * z
    # sun + far hills (slow parallax)
    sxp, syp = W * 0.84, 760
    for r_, c_ in ((120, (255, 190, 130)), (80, (255, 226, 170))): d.ellipse([sxp - r_, syp - r_, sxp + r_, syp + r_], fill=c_)
    img = Image.blend(img, Image.fromarray(sky_img(), "RGB"), 0.0)
    d = ImageDraw.Draw(img)
    for k, (col, par, base, amp) in enumerate([((92, 52, 92), 0.25, 520, 220), ((64, 38, 74), 0.45, 300, 180)]):
        pts = [(0, H)]
        for px in range(0, W + 24, 24):
            wx = (px - W / 2) / z + cx * par
            pts.append((px, Y(base + amp * (0.5 + 0.5 * math.sin(wx * 0.0021 + k * 2.0) * math.cos(wx * 0.0007 + k)) - 300 + cy * (1 - par))))
        pts.append((W, H)); d.polygon(pts, fill=col)
    xs = [px for px in range(0, W + 8, 8)]
    wxs = [(px - W / 2) / z + cx for px in xs]
    y0 = Y(0)
    # rear wall of the pit (darker earth) from original ground level down
    if y0 < H: d.rectangle([0, max(0, y0), W, H], fill=(58, 38, 34))
    # hill sky cover: where the surface is above ground level nothing to do (front earth drawn next)
    bands = [(0, (122, 84, 58)), (170, (108, 72, 50)), (380, (92, 60, 44)), (640, (78, 50, 38)), (980, (66, 42, 34)), (1500, (54, 35, 30)), (9000, (44, 29, 26))]
    for bi in range(len(bands) - 1):
        o1, c1 = bands[bi]; o2 = bands[bi + 1][0]
        top = [(px, Y(surf(wx, t) - o1)) for px, wx in zip(xs, wxs)]; bot = [(px, Y(surf(wx, t) - o2)) for px, wx in zip(xs, wxs)][::-1]
        d.polygon(top + bot, fill=c1)
    # grass strip along the surface
    d.line([(px, Y(surf(wx, t))) for px, wx in zip(xs, wxs)], fill=(70, 92, 52), width=max(8, int(26 * z)), joint="curve")
    d.line([(px, Y(surf(wx, t)) - max(3, int(10 * z))) for px, wx in zip(xs, wxs)], fill=(112, 134, 70), width=max(3, int(8 * z)), joint="curve")
    return img.convert("RGBA")

def dirt(img, t, hx, hy, cx, cy, z):
    d = ImageDraw.Draw(img)
    X = lambda x: W / 2 + (x - cx) * z
    Y = lambda y: H / 2 - (y - cy) * z
    k = 0
    while True:
        ts = 8.1 + 0.4 + (0.8 if True else 0) * k * 0.9
        ts = 8.5 + 0.77 * k
        if ts > 13.2: break
        tau = t - ts
        if 0 <= tau < 1.3:
            rnd = random.Random(k * 91)
            for j in range(9):
                vx = (rnd.uniform(160, 900) if k % 2 == 0 else -rnd.uniform(160, 900)) * rnd.uniform(0.5, 1.1)
                vy = rnd.uniform(1000, 1700)
                x0 = hx + 160; y0 = surf(hx, ts) + 620
                px = x0 + vx * tau; py = y0 + vy * tau - 0.5 * 2600 * tau * tau
                if py < surf(px, t) - 4 and tau > 0.05:
                    py = surf(px, t) + 8   # settled on the mound
                    if tau > 1.15: continue
                r_ = rnd.uniform(14, 26) * z
                d.ellipse([X(px) - r_, Y(py) - r_, X(px) + r_, Y(py) + r_], fill=rnd.choice([(92, 62, 42), (110, 76, 50), (74, 50, 36)]))
        k += 1
    return img

CAPS = [(0.0, 2.7, ["WHAT DO YOU DO", "WHEN THEY DIG", "YOUR GRAVE?"]), (3.1, 4.3, ["YOU BUILD", "A HILL."]), (4.65, 5.75, ["THEY PUSHED", "HIM IN."]),
        (5.9, 7.1, ["AND LEFT", "HIM THERE."]), (7.4, 8.9, ["SO HE PICKED UP", "THE SHOVEL."]), (9.1, 11.3, ["EVERY SCOOP THEY", "MEANT TO BURY HIM WITH"]),
        (11.3, 13.4, ["BECAME THE GROUND", "HE STOOD ON."]), (13.5, 15.8, ["NOW THEY HAVE", "TO LOOK UP."]), (16.2, 18.2, ["WHO IS", "DIGGING YOURS?"])]
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(FONT, sz)
    return _F[sz]
def overlay_text(img, t):
    d = ImageDraw.Draw(img)
    for a, b, lines in CAPS:
        if a <= t < b:
            al = min(1.0, (t - a) / 0.18, (b - t) / 0.18) if b - a > 0.4 else 1.0
            sz = 88 if max(len(l) for l in lines) < 17 else 70
            layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); dl = ImageDraw.Draw(layer)
            y = 210
            for ln in lines:
                w = dl.textlength(ln, font=font(sz)); dl.text(((W - w) / 2, y), ln, font=font(sz), fill=(255, 255, 255, int(255 * al)), stroke_width=7, stroke_fill=(20, 14, 26, int(235 * al)))
                y += int(sz * 1.12)
            img.alpha_composite(layer)
            break
    d = ImageDraw.Draw(img); lab = "S L O W   L I G H T"; w = d.textlength(lab, font=font(32))
    d.text(((W - w) / 2, 1822), lab, font=font(32), fill=(255, 255, 255, 215), stroke_width=4, stroke_fill=(20, 14, 26, 200))

# ------------------------------------------------------------------ frame
def frame(t):
    cx, cy, z = cam(t); sh = shake(t); cx += sh / z * 0.5; cy += sh / z * 0.35
    img = draw_bg(t, cx, cy, z)
    X = lambda x: W / 2 + (x - cx) * z
    Y = lambda y: H / 2 - (y - cy) * z
    load_crowd()
    order = sorted(range(5), key=lambda i: -i)
    for i in order:
        pose, mood, x, y = crowd_state(i, t)
        spr = _CROWD[(pose, mood)]; q = z / (V.FO / spr[3]) * (1.0 if i % 2 == 0 else 0.94)
        paste_sprite(img, spr[:3], X(x), Y(y + 600 * (1.0 if i % 2 == 0 else 0.94)), q)
    P, mood, yaw, hx, hy = hero_state(t)
    rgb, a, dist = make_sprite(P, mood, HERO_D, HERO_T, yaw)
    sp = crop(rgb, a)
    if sp is not None: paste_sprite(img, sp, X(hx), Y(hy + 470), z / (V.FO / dist))
    img = dirt(img, t, hx, hy, cx, cy, z)
    overlay_text(img, t)
    return img.convert("RGB")

def _job(args):
    i, t, out, k = args
    V.RES["k"] = k
    frame(t).save(f"{out}/f{i:04d}.png", compress_level=1)
    return i

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep": prep()
    elif cmd == "sheet":
        V.RES["k"] = 2; ts = [float(a) for a in sys.argv[3:]]
        n = len(ts); cols = min(n, 6); rows = math.ceil(n / cols); tw, th = 270, 480
        sheet = Image.new("RGB", (tw * cols, th * rows))
        for j, t in enumerate(ts): sheet.paste(frame(t).resize((tw, th), Image.LANCZOS), ((j % cols) * tw, (j // cols) * th))
        sheet.save(sys.argv[2]); print("wrote", sys.argv[2])
    elif cmd == "frames":
        from multiprocessing import Pool
        out = sys.argv[2]; k = int(sys.argv[3]) if len(sys.argv) > 3 else 1; os.makedirs(out, exist_ok=True)
        jobs = [(i, i / FPS, out, k) for i in range(int(DUR * FPS)) if not os.path.exists(f"{out}/f{i:04d}.png")]
        with Pool(4) as p:
            for n, i in enumerate(p.imap_unordered(_job, jobs)):
                if n % 20 == 0: print(n, "/", len(jobs), flush=True)
    elif cmd == "video":
        out, audio, fr = sys.argv[2:5]
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{fr}/f%04d.png", "-i", audio, "-t", str(DUR), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True)
        print("wrote", out)
