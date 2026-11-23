#!/usr/bin/env python3
"""'Revenge is a waste of time' (10 s). Gold-cream vinyl hero, grey/black crowd shouting outside a double wooden door, he shuts it, breathes,
opens it, nobody is there, he walks out into the light.   1080x1920 @30.
usage: render_door.py prep | sheet OUT.png t... | frames OUTDIR [k] | video OUT.mp4 AUDIO.wav FRAMESDIR
"""
import sys, os, math, json, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vinyl as V, hh_poses as HP

W, H = 1080, 1920; FPS = 30; DUR = 10.0
SC = os.environ.get("HH_SCRATCH", "/tmp/claude-0/-home-user-youtube-monetization/a23e2797-2c3e-5eef-b6ce-d7544fada057/scratchpad/hh")
FONT = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
FO = 1400.0; DC = 1950.0; HC = 560.0; YOFF = 80.0
HW = 620.0; HD = 1400.0           # door half width / height (world units, wall plane z=0)
TH_OPEN = math.radians(65)
TINT = (1.0, 0.74, 0.34)          # gold-cream hero

def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def P3(x, y, z): d = DC + z; return W / 2 + FO * x / d, H / 2 + YOFF - FO * (y - HC) / d
def K(z): return FO / (DC + z)

# ------------------------------------------------------------------ timeline
def theta(t):
    if t < 3.6: return TH_OPEN
    if t < 4.25: return TH_OPEN * (1 - ((t - 3.6) / 0.65) ** 2)
    if t < 6.5: return 0.0
    return TH_OPEN * sm((t - 6.5) / 0.9)
def sunny(t): return sm((t - 4.4) / 1.2)
def hero_state(t):
    """pose, mood, yaw, x, z"""
    x, z = -250.0, -250.0; yaw = 0.0; mood = "neutral"; P = HP.lerp_pose("stand", "calm", 1.0)
    fl = 1.5 * math.sin(t * 17) * (1 if t < 2.9 else 0)
    if t < 2.9:
        P = HP.lerp_pose("stand", "calm", 0.6 + 0.4 * abs(math.sin(t * 5.5))); mood = "determined" if int(t * 4) % 3 else "neutral"
    elif t < 3.6:
        u = sm((t - 2.9) / 0.7); x = lerp(-250, 0, u); yaw = lerp(0, math.pi, u); P = HP.lerp_pose("calm", "reach", sm((t - 3.1) / 0.5)); mood = "neutral"
    elif t < 4.35:
        x = 0.0; yaw = math.pi; u = sm((t - 3.6) / 0.65); P = HP.lerp_pose("reach", "reach", 1.0); mood = "neutral"
        pull = 1 - ((t - 3.6) / 0.65) ** 2 if t < 4.25 else 0; P = HP.lerp_pose("reach", "calm", sm((t - 3.9) / 0.4))
    elif t < 5.2:
        x = 0.0; yaw = math.pi; P = HP.lerp_pose("calm", "stand", sm((t - 4.35) / 0.8)); P["pelvis"] = (0, 470 - 6 * math.sin((t - 4.35) * 2.6), 0)
    elif t < 6.0:
        u = sm((t - 5.2) / 0.7); x = 0.0; yaw = lerp(math.pi, 2 * math.pi, u); P = HP.lerp_pose("stand", "calm", 0.5); mood = "joy" if u > 0.8 else "neutral"
    elif t < 6.5:
        u = sm((t - 6.0) / 0.5); x = 0.0; yaw = lerp(2 * math.pi, 3 * math.pi, u); P = HP.lerp_pose("calm", "reach", sm((t - 6.2) / 0.3)); mood = "neutral"
    elif t < 7.4:
        x = 0.0; yaw = math.pi; P = HP.lerp_pose("reach", "stand", sm((t - 6.8) / 0.5))
    else:
        u = sm((t - 7.4) / 0.5); sp = min(1.0, (t - 7.4) / 0.6)
        z = -250 + 620 * (t - 7.4) * sp * (1 + 0.15 * (t - 7.4)) * 0 + 700 * ((t - 7.4) - 0.3 * (1 - math.exp(-(t - 7.4) / 0.3)) * 0)
        z = -250 + 720 * (t - 7.4); x = 0.0; yaw = math.pi
        P = HP.lerp_pose("stand", HP.walk_pose(t * 2 * math.pi * 1.9), u)
    return P, mood, yaw, x + fl, z

# ------------------------------------------------------------------ sprites
HERO_D = 1500.0; HERO_T = np.array([0, 470, 0], np.float32)
CROWD_D = 1900.0; CROWD_T = np.array([0, 600, 0], np.float32)
CROWD_SET = [(p, m, tn) for p in ("rage_a", "rage_b") for m in ("shocked", "strain") for tn in (0.26, 0.42)]
def make_sprite(P, mood, Dd, T, yaw, **kw):
    C = np.array([Dd * math.sin(yaw), 520, Dd * math.cos(yaw)], np.float32); r, u, f = V.lookat(C, T)
    rgb, a = V.render(dict(P), mood, C, r, u, f, sprite=True, **kw)
    return rgb, a, float(np.linalg.norm(C - T))
def crop(rgb, a):
    ys, xs = np.nonzero(a > 0.01)
    if len(xs) == 0: return None
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    rgba = np.dstack([rgb[y0:y1, x0:x1], a[y0:y1, x0:x1, None]])
    return Image.fromarray((np.clip(rgba, 0, 1) * 255).astype(np.uint8), "RGBA"), int(x0), int(y0)
def paste_sprite(layer, spr, sx, sy, q):
    im, x0, y0 = spr
    w, h = max(1, int(im.width * q)), max(1, int(im.height * q))
    s = im.resize((w, h), Image.LANCZOS)
    tmp = Image.new("RGBA", layer.size, (0, 0, 0, 0)); tmp.paste(s, (int(round(sx + (x0 - W / 2) * q)), int(round(sy + (y0 - H / 2) * q))))
    layer.alpha_composite(tmp)
_CROWD = {}
def load_crowd():
    if _CROWD: return
    for p, m, tn in CROWD_SET:
        fn = f"{SC}/door_{p}_{m}_{tn}.png"; meta = json.load(open(fn + ".json"))
        _CROWD[(p, m, tn)] = ((Image.open(fn).convert("RGBA"), meta["x0"], meta["y0"]), meta["dist"])
def prep():
    V.RES["k"] = 1
    for p, m, tn in CROWD_SET:
        rgb, a, dist = make_sprite(V.POSES[p], m, CROWD_D, CROWD_T, 0.0, scale=1.3, tone=tn)
        im, x0, y0 = crop(rgb, a); fn = f"{SC}/door_{p}_{m}_{tn}.png"; im.save(fn); json.dump(dict(x0=x0, y0=y0, dist=dist), open(fn + ".json", "w")); print("crowd", p, m, tn)

# ------------------------------------------------------------------ scene
def vgrad(top, bot, y0, y1):
    yy = np.clip((np.arange(H, dtype=np.float32) - y0) / max(1, (y1 - y0)), 0, 1)[:, None, None]
    return (np.array(top, np.float32) * (1 - yy) + np.array(bot, np.float32) * yy)
def outside(t):
    b = sunny(t); hz = int(960 + YOFF)
    storm = dict(top=(46, 50, 70), hor=(128, 130, 146), gr=(62, 72, 66), path=(98, 94, 96), tree=(40, 48, 52))
    sun = dict(top=(120, 186, 238), hor=(255, 232, 178), gr=(150, 176, 84), path=(238, 208, 150), tree=(88, 130, 64))
    mix = lambda k: tuple(lerp(storm[k][i], sun[k][i], b) for i in range(3))
    sky = vgrad(mix("top"), mix("hor"), 0, hz)
    img = np.repeat(sky, W, axis=1)
    img[hz:] = np.repeat(vgrad(mix("gr"), tuple(c * 0.85 for c in mix("gr")), hz, H)[hz:], W, axis=1)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB"); d = ImageDraw.Draw(im)
    if b > 0.01:  # sun glow
        g = Image.new("RGB", (W, H), (0, 0, 0)); gd = ImageDraw.Draw(g); gd.ellipse([W / 2 - 260, hz - 420, W / 2 + 260, hz + 100], fill=(int(255 * b), int(228 * b), int(150 * b)))
        g = g.filter(ImageFilter.GaussianBlur(90)); im = Image.fromarray(np.clip(np.asarray(im, np.float32) + np.asarray(g, np.float32) * 0.9, 0, 255).astype(np.uint8)); d = ImageDraw.Draw(im)
    rnd = random.Random(5)
    for k in range(22):   # tree blobs along the horizon
        x = rnd.uniform(-100, W + 100); r_ = rnd.uniform(60, 150); d.ellipse([x - r_, hz - r_ * 0.9, x + r_, hz + r_ * 0.5], fill=tuple(int(c) for c in mix("tree")))
    if b < 0.99:   # storm clouds
        cl = Image.new("L", (W, H), 0); cd = ImageDraw.Draw(cl)
        for k in range(9):
            x = (rnd.uniform(0, W) + t * 18) % (W + 400) - 200; y = rnd.uniform(120, 620); cd.ellipse([x - 260, y - 70, x + 260, y + 70], fill=int(150 * (1 - b)))
        cl = cl.filter(ImageFilter.GaussianBlur(40)); im.paste(Image.new("RGB", (W, H), (30, 32, 44)), (0, 0), cl)
        d = ImageDraw.Draw(im)
    # path converging to the vanishing point
    pc = tuple(int(c) for c in mix("path")); vx = W / 2
    d.polygon([(vx - 8, hz), (vx + 8, hz), (vx + FO * 760 / DC, H), (vx - FO * 760 / DC, H)], fill=pc)
    return im.convert("RGBA")
def shout_marks(layer, x, y, k, t, i):
    d = ImageDraw.Draw(layer)
    for j in range(3):
        a = math.radians(-60 + j * 60 + 10 * math.sin(t * 14 + i))
        r0, r1 = 150 * k * 1.6, (200 + 40 * ((t * 7 + i + j) % 1)) * k * 1.6
        d.line([(x + r0 * math.cos(a), y - 170 * k * 1.3 - r0 * math.sin(a) * 0.7), (x + r1 * math.cos(a), y - 170 * k * 1.3 - r1 * math.sin(a) * 0.7)], fill=(236, 236, 240, 200), width=max(2, int(7 * k * 1.6)))
CROWD_POS = [(-330, 660, 0.26), (-90, 760, 0.42), (160, 640, 0.26), (330, 820, 0.42), (30, 980, 0.30 if False else 0.26)]
def crowd(layer, t):
    load_crowd()
    for i in sorted(range(len(CROWD_POS)), key=lambda i: -CROWD_POS[i][1]):
        x, z, tn = CROWD_POS[i]; ph = int((t * 7.5 + i * 0.37) % 2); mo = "shocked" if int((t * 5 + i * 1.3) % 2) == 0 else "strain"
        key = ("rage_a" if ph == 0 else "rage_b", mo, tn); spr, dist = _CROWD[key]
        k = K(z); sx, sy = P3(x, 0, z)
        bounce = 10 * k * abs(math.sin(t * 9 + i * 1.7))
        paste_sprite(layer, spr, sx, sy - 600 * k + (-bounce) , 0.52 * 0 + (1900.0 / (DC + z)) * 1.0)
        shout_marks(layer, sx, sy - bounce, k, t, i)
def leaf_pt(side, th, s, v, z_off=0.0):
    x = side * HW * (1 - s * math.cos(th)); z = HW * s * math.sin(th)
    return P3(x, v * HD, z)
def draw_leaf(img, side, th, t):
    d = ImageDraw.Draw(img, "RGBA"); lit = 0.62 + 0.38 * math.cos(th * 0.9)
    base = np.array([138, 88, 50], np.float32) * lit
    N = 10
    for i in range(N):
        s0, s1 = i / N, (i + 1) / N
        q = [leaf_pt(side, th, s0, 1), leaf_pt(side, th, s1, 1), leaf_pt(side, th, s1, 0), leaf_pt(side, th, s0, 0)]
        shade = 1.0 + 0.07 * (1 if i % 2 else -1); d.polygon(q, fill=tuple(int(c * shade) for c in base))
    for (v0, v1) in ((0.08, 0.46), (0.54, 0.92)):   # recessed panels
        q = [leaf_pt(side, th, 0.14, v1), leaf_pt(side, th, 0.86, v1), leaf_pt(side, th, 0.86, v0), leaf_pt(side, th, 0.14, v0)]
        d.polygon(q, fill=tuple(int(c * 0.78) for c in base), outline=tuple(int(c * 0.55) for c in base))
    q = [leaf_pt(side, th, 0.965, 1), leaf_pt(side, th, 1.0, 1), leaf_pt(side, th, 1.0, 0), leaf_pt(side, th, 0.965, 0)]
    d.polygon(q, fill=tuple(int(c * 1.25) for c in np.minimum(base, 200)))
    hx, hy = leaf_pt(side, th, 0.90, 0.46); r_ = 13 * K(HW * 0.9 * math.sin(th)) * 1.8
    d.ellipse([hx - r_, hy - r_, hx + r_, hy + r_], fill=(236, 190, 90, 255))

def wall_with_door(t):
    wall = np.zeros((H, W, 3), np.float32); yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    wall[:] = np.array([30, 44, 58], np.float32) * (1.1 - 0.5 * yy) ; wall = np.repeat(wall[:, :1], W, axis=1)
    xx = np.linspace(-1, 1, W, dtype=np.float32)[None, :, None]; wall *= (1 - 0.35 * xx ** 2)
    im = Image.fromarray(np.clip(wall, 0, 255).astype(np.uint8), "RGB").convert("RGBA"); d = ImageDraw.Draw(im)
    xl, yt = P3(-HW, HD, 0); xr, yb = P3(HW, 0, 0)
    # baseboard + frame
    fw = 52 * K(0)
    d.rectangle([0, yb - 70 * K(0), W, yb], fill=(24, 34, 46, 255))
    return im, (xl, yt, xr, yb), fw
def floor(img, t):
    d = ImageDraw.Draw(img); _, yb = P3(0, 0, 0)
    d.rectangle([0, yb, W, H], fill=(86, 54, 36))
    for i in range(-14, 15):
        x0 = i * 220.0
        d.line([P3(x0, 0, 0), P3(x0 * 1.0, 0, -DC + 420)], fill=(60, 36, 24), width=3)
    for j, zz in enumerate([-120, -280, -480, -740, -1100, -1600]):
        sx, sy = P3(0, 0, zz); d.line([(0, sy), (W, sy)], fill=(62, 38, 26), width=2)
    g = Image.new("L", (W, H), 0); gd = ImageDraw.Draw(g); gd.rectangle([0, yb - 30, W, H], fill=60)
    return img

def frame(t):
    sh = 0.0
    for t0, amp in ((4.25, 18),):
        if t0 <= t < t0 + 0.45: sh += amp * (1 - (t - t0) / 0.45) * math.sin((t - t0) * 60)
    out = outside(t)
    if t < 4.3: crowd(out, t)
    th = theta(t)
    if th > 0.001 or True:
        draw_leaf(out, -1, th, t); draw_leaf(out, 1, th, t)
    wall, (xl, yt, xr, yb), fw = wall_with_door(t)
    # cut the doorway: outside shows through the opening only
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).rectangle([xl, yt, xr, yb], fill=255)
    wall.paste(out, (0, 0), mask)
    d = ImageDraw.Draw(wall)
    for k_ in range(3):   # door frame
        d.rectangle([xl - fw + k_ * 3, yt - fw + k_ * 3, xr + fw - k_ * 3, yb], outline=(74 + 10 * k_, 46 + 6 * k_, 28 + 4 * k_, 255), width=int(fw / 3))
    floor(wall, t)
    img = wall
    # hero
    load_crowd()
    P, mood, yaw, hx, hz = hero_state(t)
    rgb, a, dist = make_sprite(P, mood, HERO_D, HERO_T, yaw, tint=TINT)
    sp = crop(rgb, a)
    sx, sy = P3(hx, 0, hz); k = K(hz)
    sh_l = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh_l).ellipse([sx - 230 * k, sy - 22 * k, sx + 230 * k, sy + 28 * k], fill=(0, 0, 0, 110))
    img.alpha_composite(sh_l.filter(ImageFilter.GaussianBlur(10)))
    if sp is not None:
        q = HERO_D / (DC + hz)
        paste_sprite(img, sp, sx, sy - 470 * k, q)
    # light spill + final bloom
    arr = np.asarray(img.convert("RGB"), np.float32)
    if t > 6.7:
        u = sm((t - 6.7) / 1.0); xx, yy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        gl = np.exp(-(((xx - W / 2) / 420) ** 2 + ((yy - 900) / 700) ** 2)); arr += gl[..., None] * np.array([255, 214, 140], np.float32) * 0.28 * u
    if t > 9.3:
        u = sm((t - 9.3) / 0.7); xx, yy = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
        gl = np.exp(-(((xx - W / 2) / 700) ** 2 + ((yy - 980) / 900) ** 2)); arr = arr * (1 - 0.55 * u * gl[..., None]) + np.array([255, 236, 190], np.float32) * 0.55 * u * gl[..., None]
    vig = 1 - 0.30 * (((np.arange(W) - W / 2) / (W / 2)) ** 2)[None, :, None]
    arr = np.clip(arr * vig, 0, 255)
    # camera shake
    im = Image.fromarray(arr.astype(np.uint8), "RGB")
    if sh: im = im.transform((W, H), Image.AFFINE, (1, 0, sh * 0.7, 0, 1, sh), Image.BILINEAR)
    im = im.convert("RGBA"); text(im, t); return im.convert("RGB")

_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype(FONT, sz)
    return _F[sz]
def text(img, t):
    d = ImageDraw.Draw(img); a = min(1.0, t / 0.25)
    lines = [[("REVENGE IS A", (255, 255, 255))], [("WASTE OF TIME", (255, 210, 40))]]; y = 150
    for ln in lines:
        w = sum(d.textlength(s, font=font(92)) for s, _ in ln); x = (W - w) / 2
        for s, c in ln:
            d.text((x, y), s, font=font(92), fill=c + (int(255 * a),), stroke_width=8, stroke_fill=(16, 12, 22, int(240 * a))); x += d.textlength(s, font=font(92))
        y += 106
    lab = "S L O W   L I G H T"; w = d.textlength(lab, font=font(32))
    d.text(((W - w) / 2, 1822), lab, font=font(32), fill=(255, 255, 255, 220), stroke_width=4, stroke_fill=(20, 14, 26, 200))

def _job(a):
    i, t, out, k = a; V.RES["k"] = k; frame(t).save(f"{out}/f{i:04d}.png", compress_level=1); return i
if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "prep": prep()
    elif cmd == "sheet":
        V.RES["k"] = 2; ts = [float(a) for a in sys.argv[3:]]; cols = min(len(ts), 6); rows = math.ceil(len(ts) / cols); tw, th_ = 270, 480
        sheet = Image.new("RGB", (tw * cols, th_ * rows))
        for j, t in enumerate(ts): sheet.paste(frame(t).resize((tw, th_), Image.LANCZOS), ((j % cols) * tw, (j // cols) * th_))
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
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", f"{fr}/f%04d.png", "-i", audio, "-t", str(DUR), "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", out], check=True); print("wrote", out)
