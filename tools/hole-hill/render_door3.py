#!/usr/bin/env python3
"""'Revenge is a waste of time' v3: more immersive (moving camera, depth of field, light shafts, dust), quiet menacing crowd, suspense hold, and a light, golden reveal.
usage: render_door3.py prep | sheet OUT.png t... | frames OUTDIR [k] | video OUT.mp4 AUDIO.wav FRAMESDIR"""
import sys, os, math, json, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vinyl as V, hh_poses as HP, render_door as RD, render_door2 as R2

W, H = 1080, 1920; FPS = 30; DUR = 10.0; SC = RD.SC; FO = 1400.0
def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def lv(a, b, t): return np.array([lerp(a[i], b[i], t) for i in range(3)], np.float32)

# ------------------------------------------------------------------ camera
def cam_state(t):
    c0, g0 = (420, 640, -1650), (-40, 700, 0)
    c1, g1 = (300, 660, -1280), (-60, 720, 0)
    c2, g2 = (210, 770, -1320), (-25, 790, 0)       # close on the hand / ring
    c3, g3 = (260, 700, -1250), (-10, 700, 0)
    c4, g4 = (140, 650, -1200), (40, 680, 0)          # follows him into the light
    if t < 4.4: u = sm(t / 4.4); C, G = lv(c0, c1, u), lv(g0, g1, u)
    elif t < 5.9: u = sm((t - 4.4) / 1.5); C, G = lv(c1, c2, u), lv(g1, g2, u)
    elif t < 8.3: u = sm((t - 5.9) / 2.4); C, G = lv(c2, c2, 0), lv(g2, g2, 0); C = C + np.array([14 * u, 0, 70 * u], np.float32)
    elif t < 9.0: u = sm((t - 8.3) / 0.7); C, G = lv(c2, c3, u) + np.array([14, 0, 70], np.float32) * (1 - u), lv(g2, g3, u)
    else: u = sm((t - 9.0) / 1.0); C, G = lv(c3, c4, u), lv(g3, g4, u)
    C = C + np.array([4 * math.sin(t * 1.7), 3 * math.sin(t * 2.3), 0], np.float32); G = G + np.array([3 * math.sin(t * 1.3), 2 * math.sin(t * 1.9), 0], np.float32)
    return C, G
def set_cam(t):
    C, G = cam_state(t); R2.CAM = C; R2.TGT = G; R2.CR, R2.CU, R2.CF = V.lookat(C, G)

# ------------------------------------------------------------------ crowd (quiet, menacing)
CROWD = [(-10, 240, 0.32, "determined"), (70, 300, 0.38, "determined"), (-60, 380, 0.30, "strain"), (110, 400, 0.36, "determined"), (20, 470, 0.32, "determined")]
_CR = {}
def prep():
    V.RES["k"] = 1; set_cam(0.0)
    for i, (x, z, tn, mood) in enumerate(CROWD):
        for pn in ("glare_a", "glare_b"):
            yaw = R2.sprite_yaw(x, z, R2.crowd_phi(x, z))
            rgb, a, dist = RD.make_sprite(V.POSES[pn], mood, 1500.0, RD.HERO_T, yaw, tone=tn, scale=0.9)
            im, x0, y0 = RD.crop(rgb, a); fn = f"{SC}/d3_{i}_{pn}.png"; im.save(fn); json.dump(dict(x0=x0, y0=y0), open(fn + ".json", "w"))
def load_crowd():
    if _CR: return
    for i in range(len(CROWD)):
        for pn in ("glare_a", "glare_b"):
            fn = f"{SC}/d3_{i}_{pn}.png"; m = json.load(open(fn + ".json")); _CR[(i, pn)] = (Image.open(fn).convert("RGBA"), m["x0"], m["y0"])

# ------------------------------------------------------------------ light / outside
HY = float(os.environ.get('HY', '1.15'))
def light(t): return sm((t - 8.3) / 1.2)
def sunny_outside(L):
    hz = int(R2.proj((0, R2.CAM[1], 6000))[1])
    top, hor, gr = np.array([130, 190, 240], np.float32), np.array([255, 232, 178], np.float32), np.array([146, 176, 86], np.float32)
    yy = np.arange(H, dtype=np.float32)[:, None, None]
    sky = top * (1 - np.clip(yy / max(hz, 1), 0, 1)) + hor * np.clip(yy / max(hz, 1), 0, 1)
    ground = gr * (1 - 0.25 * np.clip((yy - hz) / (H - hz + 1), 0, 1))
    img = np.where(yy < hz, sky, ground); img = np.repeat(img, W, axis=1)
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA"); d = ImageDraw.Draw(im, "RGBA")
    rnd = random.Random(3)
    for k in range(18):
        x = rnd.uniform(-100, W + 100); r_ = rnd.uniform(50, 130); d.ellipse([x - r_, hz - r_ * 0.9, x + r_, hz + r_ * 0.4], fill=(84, 128, 66, 255))
    pw = 520; d.polygon([(W / 2 - 14, hz), (W / 2 + 14, hz), (W / 2 + pw, H), (W / 2 - pw, H)], fill=(240, 212, 156, 255))
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sun).ellipse([W / 2 - 220, hz - 330, W / 2 + 220, hz + 110], fill=(255, 236, 180, 200))
    im.alpha_composite(sun.filter(ImageFilter.GaussianBlur(60)))
    return im

def frame(t):
    set_cam(t); R2.load_crowd(); load_crowd()
    th = R2.theta(t); L = light(t)
    P_, mood, phi, hx, hz = R2.hero_state(t)
    # ---------- environment
    wall_c = lv((26, 26, 32), (120, 104, 98), L); floor_c = lv((14, 14, 19), (84, 66, 58), L)
    wall = Image.new("RGBA", (W, H), tuple(int(c) for c in wall_c) + (255,)); d = ImageDraw.Draw(wall)
    fl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(fl).polygon([R2.Pj(-3000, 0, -1400), R2.Pj(3000, 0, -1400), R2.Pj(3000, 0, 0), R2.Pj(-3000, 0, 0)], fill=tuple(int(c) for c in floor_c) + (255,))
    wall.alpha_composite(fl)
    # outside through the opening: black + crowd, then sunlit world
    out = Image.new("RGBA", (W, H), (4, 4, 7, 255))
    of = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(of).polygon([R2.Pj(-3000, 0, 0), R2.Pj(3000, 0, 0), R2.Pj(3000, 0, 3000), R2.Pj(-3000, 0, 3000)], fill=(14, 14, 20, 255)); out.alpha_composite(of)
    if t < 4.5:
        for i in sorted(range(len(CROWD)), key=lambda i: -CROWD[i][1]):
            x, z, tn, mood = CROWD[i]; ph = int((t * 0.9 + i * 0.37) % 2); spr = _CR[(i, "glare_a" if ph == 0 else "glare_b")]
            sx, sy, zc = R2.proj((x, 0, z)); q = 1500.0 / zc
            fade = 1.0 if t < 4.2 else max(0.0, 1 - (t - 4.2) / 0.3)
            if fade > 0: RD.paste_sprite(out, spr, sx + 2 * math.sin(t * 1.3 + i), sy - 470 * (FO / zc), q)
    if L > 0.0:
        so = sunny_outside(L); a = np.asarray(so, np.float32); out_a = np.asarray(out, np.float32)
        out = Image.fromarray(np.clip(out_a * (1 - L) + a * L, 0, 255).astype(np.uint8), "RGBA")
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([R2.Pj(-R2.HW, 0, 0), R2.Pj(R2.HW, 0, 0), R2.Pj(R2.HW, R2.HD, 0), R2.Pj(-R2.HW, R2.HD, 0)], fill=255)
    wall.paste(out, (0, 0), mask); img = wall
    # light shaft on the floor + soft floor pool in front of the door
    shaft = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(shaft)
    gx = 100 + 0 * L
    sd.polygon([R2.Pj(-R2.HW * 0.2, 0, 0), R2.Pj(R2.HW * 0.9, 0, 0), R2.Pj(R2.HW * 1.5 + gx, 0, -1300), R2.Pj(-R2.HW * 0.8, 0, -1300)], fill=(255, 226, 160, int(190 * L)))
    img.alpha_composite(shaft.filter(ImageFilter.GaussianBlur(40)))
    # door reflection + door
    ref = Image.new("RGBA", (W, H), (0, 0, 0, 0)); R2.door_geometry(ref, th, flip=True, alpha=255)
    ra = np.asarray(ref, np.float32); yy = np.arange(H, dtype=np.float32)[:, None]; y0 = R2.proj((0, 0, 0))[1]
    ra[..., 3] *= np.clip(1 - (yy - y0) / 600, 0, 1) * (0.20 + 0.12 * L); ra[..., 3] *= (yy > y0)
    img.alpha_composite(Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8), "RGBA"))
    R2.door_geometry(img, th)
    # depth of field on the environment during the close-up beat
    blur = 3.2 * sm((t - 4.6) / 1.0) * (1 - sm((t - 8.2) / 0.6))
    if blur > 0.3: img = img.filter(ImageFilter.GaussianBlur(blur))
    # ---------- hero
    P = dict(P_)
    if 5.3 < t < 7.9:
        g = sm((t - 5.3) / 0.7) * (1 - sm((t - 7.4) / 0.5)); P["head_yaw"] = HY * g
        mood = "neutral" if g < 0.6 else "joy"
    sx, sy, zc = R2.proj((hx, 0, hz)); Dd = max(850.0, min(1500.0, zc)); q = Dd / zc; k = FO / zc
    yaw = R2.sprite_yaw(hx, hz, phi)
    rgb, a, dist = RD.make_sprite(P, mood, Dd, RD.HERO_T, yaw, tint=R2.TINT)
    sp = RD.crop(rgb, a)
    shl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(shl).ellipse([sx - 200 * k, sy - 24 * k, sx + 200 * k, sy + 30 * k], fill=(0, 0, 0, int(150 - 70 * L)))
    img.alpha_composite(shl.filter(ImageFilter.GaussianBlur(9)))
    if sp is not None:
        im, x0, y0_ = sp; fl_im = im.transpose(Image.FLIP_TOP_BOTTOM); ra = np.asarray(fl_im, np.float32).copy()
        ys = np.linspace(1, 0, ra.shape[0], dtype=np.float32)[:, None]; ra[..., 3] *= (ys ** 1.5) * 0.28
        w_, h_ = max(1, int(im.width * q)), max(1, int(im.height * q)); rs = Image.fromarray(ra.astype(np.uint8), "RGBA").resize((w_, h_), Image.LANCZOS)
        sprite_bottom = sy - 470 * k + (y0_ + im.height - H / 2) * q
        refl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); refl.paste(rs, (int(round(sx + (x0 - W / 2) * q)), int(round(2 * sy - sprite_bottom)))); img.alpha_composite(refl)
        # warm rim: a blurred copy of the silhouette, offset toward the key light, added behind the hero
        al = Image.new("RGBA", (W, H), (0, 0, 0, 0)); RD.paste_sprite(al, sp, sx, sy - 470 * k, q)
        A = al.split()[3]; glow = A.filter(ImageFilter.GaussianBlur(14)); glow_l = Image.new("RGBA", (W, H), (255, 190, 110, 0)); glow_l.putalpha(glow.point(lambda v: int(v * (0.22 + 0.25 * L))))
        img.alpha_composite(glow_l); img.alpha_composite(al)
    # dust motes in the beam / room
    rnd = random.Random(8); dust = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dust)
    for j in range(46):
        bx, by = rnd.uniform(0, W), rnd.uniform(300, 1500); sp_ = rnd.uniform(6, 22)
        x = (bx + 12 * math.sin(t * 0.7 + j)) % W; y = (by - sp_ * t * 3) % 1500 + 250
        r_ = rnd.uniform(1.5, 3.6); a_ = int((50 + 120 * L) * (0.5 + 0.5 * math.sin(t * 2 + j)))
        dd.ellipse([x - r_, y - r_, x + r_, y + r_], fill=(255, 236, 200, max(0, a_)))
    img.alpha_composite(dust.filter(ImageFilter.GaussianBlur(1.2)))
    # grade: vignette + warm lift on the reveal + bloom
    arr = np.asarray(img.convert("RGB"), np.float32)
    xx, yy2 = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    vig = np.clip(1 - (0.55 - 0.30 * L) * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy2 - H * 0.45) / (H * 0.7)) ** 2), 0.3, 1.0)
    arr = arr * vig[..., None]
    if L > 0:
        bl = np.asarray(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(40)), np.float32)
        arr = arr + (np.clip(bl - 170, 0, None) * 0.35 + np.array([14, 8, 0], np.float32) * L)
    img = ImageOps.mirror(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")).convert("RGBA")
    text(img, t); return img.convert("RGB")

CAPS = [(0.0, 3.0, "Revenge is a waste of time."), (3.0, 6.33, "Just close the door."), (6.33, 8.3, "And move on..."), (8.3, 10.1, "Then open it again.")]
_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", sz)
    return _F[sz]
def text(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    for a, b, s in CAPS:
        if a <= t < b:
            al = min(1.0, (t - a) / 0.45) * min(1.0, (b - t) / 0.2) if b - a > 0.5 else 1.0
            w = d.textlength(s, font=font(52)); layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
            ld.text(((W - w) / 2 + 2, 262 + 3), s, font=font(52), fill=(0, 0, 0, int(150 * al))); ld.text(((W - w) / 2, 262), s, font=font(52), fill=(255, 255, 255, int(255 * al))); img.alpha_composite(layer); break
    lab = "S L O W   L I G H T"; w = d.textlength(lab, font=font(30))
    d.text(((W - w) / 2, 1822), lab, font=font(30), fill=(255, 255, 255, 215), stroke_width=3, stroke_fill=(10, 10, 14, 170))

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
