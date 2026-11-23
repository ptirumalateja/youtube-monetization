#!/usr/bin/env python3
"""'Revenge is a waste of time' v2: replica of the reference reel (same oblique camera, same beats) in our vinyl style.
Dark room, heavy iron-strapped wooden double door (left leaf closed, right leaf swung in), crowd in the gap, hero shuts the door, stands with a hand on the ring,
lets go, opens it and walks through. Captions: "Revenge is a waste of time." / "Just close the door." / "And move on..."
usage: render_door2.py prep | sheet OUT.png t... | frames OUTDIR [k] | video OUT.mp4 AUDIO.wav FRAMESDIR
"""
import sys, os, math, json, random, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import vinyl as V, hh_poses as HP
import render_door as RD

W, H = 1080, 1920; FPS = 30; DUR = 10.0
SC = RD.SC
FO = 1400.0
HW, HD = 440.0, 1480.0
CAM = np.array([420.0, 640.0, -1650.0], np.float32); TGT = np.array([-40.0, 700.0, 0.0], np.float32)
CR, CU, CF = V.lookat(CAM, TGT)
TINT = (1.0, 0.68, 0.26)
TH0 = math.radians(64)

def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
def lerp(a, b, t): return a + (b - a) * t
def nrm(v): v = np.array(v, np.float32); return v / (np.linalg.norm(v) + 1e-9)
def proj(p, flip=False):
    p = np.array(p, np.float32) - CAM
    if flip: p = p * 1.0
    zc = float(p @ CF)
    return W / 2 + FO * float(p @ CR) / zc, H / 2 - FO * float(p @ CU) / zc, zc
def Pj(x, y, z, flip=False):
    if flip: y = -y
    s = proj((x, y, z)); return (s[0], s[1])

# ------------------------------------------------------------------ door state
def theta(t):
    if t < 3.35: return TH0
    if t < 4.45: u = (t - 3.35) / 1.1; return TH0 * (1 - sm(u))
    if t < 8.3: return 0.0
    return TH0 * sm((t - 8.3) / 0.95)
def leaf_dir(th): return np.array([-math.cos(th), 0, -math.sin(th)], np.float32), np.array([math.sin(th), 0, -math.cos(th)], np.float32)
def right_leaf_pt(th, s, v, off=40.0):
    d, n = leaf_dir(th); return np.array([HW, 0, 0], np.float32) + s * HW * d + np.array([0, v * HD, 0], np.float32) + off * n
def left_leaf_pt(s, v, off=40.0): return np.array([-HW + s * HW, v * HD, -off], np.float32)
def ring_pos(side, th):
    return right_leaf_pt(th, 0.90, 0.46, 58.0) if side == "R" else left_leaf_pt(0.90, 0.46, 58.0)

# ------------------------------------------------------------------ hero
HERO_D = RD.HERO_D; HERO_T = RD.HERO_T
def ik_arm(P, sk_sh, tgt, pole=(0.5, -1.0, -0.3)):
    l1, l2 = V.LEN["uarm"], V.LEN["farm"] + 34
    sd = tgt - sk_sh; L = float(np.linalg.norm(sd)); d = sd / (L + 1e-9); L = min(L, l1 + l2 - 2)
    a = (l1 * l1 - l2 * l2 + L * L) / (2 * L); h = math.sqrt(max(l1 * l1 - a * a, 1.0))
    pv = nrm(pole); pv = nrm(pv - d * float(pv @ d)); el = sk_sh + d * a + pv * h
    return nrm(el - sk_sh), nrm(sk_sh + d * L - el)
def to_local(wp, hx, hz, phi):
    dx, dz = wp[0] - hx, wp[2] - hz; c, s = math.cos(phi), math.sin(phi)
    return np.array([dx * c - dz * s, wp[1], dx * s + dz * c], np.float32)
def hero_state(t):
    th = theta(t); phi_gap = None
    hx, hz = -60.0, -370.0; mood = "neutral"
    base = HP.lerp_pose("stand", "calm", 0.5)
    reach = 0.0; walk = 0.0
    if t < 2.6:
        base = HP.lerp_pose("stand", "calm", 0.5 + 0.5 * math.sin(t * 1.3) ** 2 * 0.3)
    elif t < 3.4:
        u = sm((t - 2.6) / 0.8); hz = lerp(-370, -330, u); reach = u
    elif t < 4.5:
        hz = lerp(-330, -300, sm((t - 3.4) / 1.1)); reach = 1.0; walk = 0.0
    elif t < 7.7:
        hz = -300.0; reach = 1.0
    elif t < 8.3:
        u = sm((t - 7.7) / 0.6); hz = lerp(-300, -380, u); hx = lerp(-60, -90, u); reach = 1 - 0.0 * u
    elif t < 9.0:
        u = sm((t - 8.3) / 0.7); hz = lerp(-380, -430, u); hx = lerp(-90, -110, u); reach = 1 - sm((t - 8.6) / 0.4)
    else:
        u = sm((t - 9.0) / 1.0); hx = lerp(-110, 95, u); hz = lerp(-430, -130, u); walk = 1.0
    # facing: toward the ring / gap, turning to walking direction at the end
    tx, tz = (130.0, -120.0)
    phi = math.atan2(tx - hx, tz - hz)
    if t >= 9.0:
        phi = lerp(phi, math.atan2(95 - hx + 1e-3, -130 - hz), 0.8)
    if walk > 0.5:
        P = HP.lerp_pose(base, HP.walk_pose(t * 2 * math.pi * 1.7), sm((t - 9.0) / 0.25))
    elif walk > 0.0:
        P = HP.lerp_pose(base, HP.walk_pose(t * 2 * math.pi * 1.2), 0.3)
    else: P = dict(base)
    if t > 7.7 and t < 8.3 and False: pass
    if reach > 0.01:
        sk = V.skeleton(dict(P)); sh = sk["shR"]
        ring = ring_pos("R", th)
        tgt = to_local(ring, hx, hz, phi)
        rest_ua, rest_fa = np.array(P.get("uaR", HP.DEF["uaR"]), np.float32), np.array(P.get("faR", HP.DEF["faR"]), np.float32)
        ua, fa = ik_arm(P, sh, tgt)
        P["uaR"] = tuple(rest_ua * (1 - reach) + ua * reach); P["faR"] = tuple(rest_fa * (1 - reach) + fa * reach)
        P["spine"] = (0.0, 1.0, 0.12 * reach); P["neck"] = (0.0, 1.0, 0.1 * reach)
    return P, mood, phi, hx, hz

def sprite_yaw(wx, wz, phi): return math.atan2(CAM[0] - wx, CAM[2] - wz) - phi

# ------------------------------------------------------------------ crowd
CROWD = [(-10, 240, 0.34, "determined"), (70, 300, 0.40, "strain"), (-60, 380, 0.32, "determined"), (110, 400, 0.38, "strain"), (20, 470, 0.34, "determined")]
def crowd_phi(x, z): return math.atan2(-60 - x, -370 - z)
_CROWD = {}
def prep():
    V.RES["k"] = 1
    for i, (x, z, tn, mood) in enumerate(CROWD):
        for pn in ("rage_a", "rage_b"):
            yaw = sprite_yaw(x, z, crowd_phi(x, z))
            rgb, a, dist = RD.make_sprite(V.POSES[pn], mood, HERO_D, HERO_T, yaw, tone=tn, scale=0.9)
            im, x0, y0 = RD.crop(rgb, a); fn = f"{SC}/d2_{i}_{pn}.png"; im.save(fn); json.dump(dict(x0=x0, y0=y0), open(fn + ".json", "w"))
        print("crowd", i)
def load_crowd():
    if _CROWD: return
    for i in range(len(CROWD)):
        for pn in ("rage_a", "rage_b"):
            fn = f"{SC}/d2_{i}_{pn}.png"; m = json.load(open(fn + ".json")); _CROWD[(i, pn)] = (Image.open(fn).convert("RGBA"), m["x0"], m["y0"])

# ------------------------------------------------------------------ drawing
def shade(base, n, amb=0.35):
    L = nrm((-0.5, 0.7, -0.5)); k = amb + 0.75 * max(0.0, float(nrm(n) @ L)); return tuple(int(min(255, c * k)) for c in base)
WOODS = [(98, 62, 38), (108, 70, 42), (88, 56, 34), (102, 66, 40), (92, 58, 36), (112, 74, 44), (96, 60, 36), (104, 68, 42)]
def draw_leaf(d, face_fn, n, flip, alpha=255):
    N = 8; rnd = random.Random(11)
    for i in range(N):
        s0, s1 = i / N, (i + 1) / N; col = shade(WOODS[i % 8], n)
        q = [face_fn(s0, 1.0), face_fn(s1, 1.0), face_fn(s1, 0.0), face_fn(s0, 0.0)]
        d.polygon([Pj(*p, flip) for p in q], fill=col + (alpha,))
        d.line([Pj(*face_fn(s1, 0.0), flip), Pj(*face_fn(s1, 1.0), flip)], fill=(22, 14, 10, alpha), width=3)
        for g in range(3):   # grain streaks
            ss = s0 + (s1 - s0) * rnd.uniform(0.2, 0.8)
            d.line([Pj(*face_fn(ss, rnd.uniform(0, 0.4)), flip), Pj(*face_fn(ss, rnd.uniform(0.6, 1.0)), flip)], fill=tuple(int(c * 0.72) for c in col) + (alpha,), width=2)
    for (v0, v1) in ((0.875, 0.915), (0.60, 0.64), (0.155, 0.195)):   # iron straps
        q = [face_fn(0.0, v1), face_fn(0.95, v1), face_fn(0.99, (v0 + v1) / 2), face_fn(0.95, v0), face_fn(0.0, v0)]
        off = [tuple(np.array(p) + np.array([0, 0, 0])) for p in q]
        d.polygon([Pj(*p, flip) for p in q], fill=shade((24, 24, 28), n, 0.5) + (alpha,))
        for rv in np.linspace(0.08, 0.9, 6):
            c = Pj(*face_fn(rv, (v0 + v1) / 2), flip); r_ = 5; d.ellipse([c[0] - r_, c[1] - r_, c[0] + r_, c[1] + r_], fill=(70, 70, 76, alpha))
    for v in (0.89, 0.18):   # hinge blocks
        q = [face_fn(0.0, v + 0.05), face_fn(0.13, v + 0.05), face_fn(0.13, v - 0.05), face_fn(0.0, v - 0.05)]
        d.polygon([Pj(*p, flip) for p in q], fill=shade((18, 18, 22), n, 0.5) + (alpha,))
def draw_ring(d, center, n, flip, alpha=255):
    c = Pj(*center, flip); sc = FO / proj(center)[2]; r_ = 60 * sc
    view = nrm(CAM - center); k = max(0.35, abs(float(nrm(n) @ view)))
    d.rectangle([c[0] - r_ * 0.34 * k, c[1] - r_ * 0.62, c[0] + r_ * 0.34 * k, c[1] + r_ * 0.2], fill=(20, 20, 24, alpha))
    d.ellipse([c[0] - r_ * k, c[1] - r_ * 0.2, c[0] + r_ * k, c[1] + r_ * 1.5], outline=(14, 14, 18, alpha), width=max(4, int(11 * sc)))
    d.ellipse([c[0] - r_ * k + 3, c[1] - r_ * 0.2 + 3, c[0] + r_ * k - 3, c[1] + r_ * 1.5 - 3], outline=(70, 70, 76, alpha // 2), width=2)
def door_geometry(img, th, flip=False, alpha=255):
    d = ImageDraw.Draw(img, "RGBA")
    FZ = -60.0; PW = 90.0
    # frame
    wood_f = (74, 48, 30)
    quads = [
        ([(-HW - PW, 0, FZ), (-HW, 0, FZ), (-HW, HD + PW, FZ), (-HW - PW, HD + PW, FZ)], (0, 0, -1)),
        ([(HW, 0, FZ), (HW + PW, 0, FZ), (HW + PW, HD + PW, FZ), (HW, HD + PW, FZ)], (0, 0, -1)),
        ([(-HW - PW, HD, FZ), (HW + PW, HD, FZ), (HW + PW, HD + PW, FZ), (-HW - PW, HD + PW, FZ)], (0, 0, -1)),
        ([(-HW, 0, FZ), (-HW, 0, 0), (-HW, HD, 0), (-HW, HD, FZ)], (1, 0, 0)),        # left jamb (visible from the right)
        ([(-HW, HD, FZ), (HW, HD, FZ), (HW, HD, 0), (-HW, HD, 0)], (0, -1, 0)),       # lintel underside
        ([(HW + PW, 0, FZ), (HW + PW, 0, 0), (HW + PW, HD + PW, 0), (HW + PW, HD + PW, FZ)], (1, 0, 0)),   # right post outer side
        ([(-HW - PW, HD + PW, FZ), (HW + PW, HD + PW, FZ), (HW + PW, HD + PW, 0), (-HW - PW, HD + PW, 0)], (0, 1, 0)),  # top
    ]
    for q, n in quads:
        vis = float(nrm(n) @ nrm(CAM - np.array(q[0], np.float32))) > 0 if not flip else True
        if vis: d.polygon([Pj(*p, flip) for p in q], fill=shade(wood_f, n, 0.4) + (alpha,))
    # leaves (left closed, right swung in)
    draw_leaf(d, lambda s, v: tuple(left_leaf_pt(s, v)), (0, 0, -1), flip, alpha)
    draw_ring(d, ring_pos("L", 0.0), (0, 0, -1), flip, alpha)
    # right leaf drawn mirrored in s (hinge at s=0)
    d_, n_ = leaf_dir(th)
    draw_leaf(d, lambda s, v: tuple(right_leaf_pt(th, 1 - s, v)), tuple(n_), flip, alpha)   # s reversed so hinge blocks sit on the hinge side
    draw_ring(d, ring_pos("R", th), n_, flip, alpha)
    # free edge thickness of the right leaf
    q = [right_leaf_pt(th, 0.995, 1.0, 0), right_leaf_pt(th, 0.995, 1.0, 40), right_leaf_pt(th, 0.995, 0.0, 40), right_leaf_pt(th, 0.995, 0.0, 0)]
    d.polygon([Pj(*p, flip) for p in q], fill=shade((60, 38, 24), d_, 0.4) + (alpha,))

def background():
    yy = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    img = np.repeat(np.array([20, 20, 26], np.float32) * (1.15 - 0.6 * yy), W, axis=1)
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
def floor_layer(z0, z1):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([Pj(-3000, 0, z0), Pj(3000, 0, z0), Pj(3000, 0, z1), Pj(-3000, 0, z1)], fill=(16, 16, 20, 255)); return im

def frame(t):
    th = theta(t); load_crowd()
    base = background()
    # wall (dark) + interior floor
    wall = base.copy(); d = ImageDraw.Draw(wall)
    d.rectangle([0, 0, W, H], fill=(28, 28, 33, 255))
    fl = floor_layer(-1000, 0); wall.alpha_composite(fl)
    # floor sheen: soft light pool in front of the door
    pool = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(pool).ellipse([Pj(-300, 0, -300)[0] - 380, Pj(-300, 0, -300)[1] - 60, Pj(-300, 0, -300)[0] + 380, Pj(-300, 0, -300)[1] + 90], fill=(90, 78, 70, 90))
    wall.alpha_composite(pool.filter(ImageFilter.GaussianBlur(40)))
    # outside layer seen through the opening
    out = Image.new("RGBA", (W, H), (4, 4, 6, 255)); od = ImageDraw.Draw(out)
    of = floor_layer(0, 3000); out.alpha_composite(of)
    if t < 4.5:
        for i in sorted(range(len(CROWD)), key=lambda i: -CROWD[i][1]):
            x, z, tn, mood = CROWD[i]; ph = int((t * 7.0 + i * 0.37) % 2); spr = _CROWD[(i, "rage_a" if ph == 0 else "rage_b")]
            sx, sy, zc = proj((x, 0, z)); q = HERO_D / zc
            bob = 8 * q * abs(math.sin(t * 9 + i * 1.9)) * (1 if t < 4.0 else max(0, 1 - (t - 4.0) / 0.5))
            RD.paste_sprite(out, spr, sx, sy - 470 * (FO / zc) - bob, q)
    mask = Image.new("L", (W, H), 0); ImageDraw.Draw(mask).polygon([Pj(-HW, 0, 0), Pj(HW, 0, 0), Pj(HW, HD, 0), Pj(-HW, HD, 0)], fill=255)
    wall.paste(out, (0, 0), mask)
    img = wall
    # door reflection on the glossy floor
    ref = Image.new("RGBA", (W, H), (0, 0, 0, 0)); door_geometry(ref, th, flip=True, alpha=255)
    ra = np.asarray(ref, np.float32); yy = np.arange(H, dtype=np.float32)[:, None]; y0 = proj((0, 0, 0))[1]
    ra[..., 3] *= np.clip(1 - (yy - y0) / 500, 0, 1) * 0.20; ra[..., 3] *= (yy > y0)
    img.alpha_composite(Image.fromarray(np.clip(ra, 0, 255).astype(np.uint8), "RGBA"))
    door_geometry(img, th)
    # hero
    P, mood, phi, hx, hz = hero_state(t)
    yaw = sprite_yaw(hx, hz, phi)
    rgb, a, dist = RD.make_sprite(P, mood, HERO_D, HERO_T, yaw, tint=TINT)
    sp = RD.crop(rgb, a)
    sx, sy, zc = proj((hx, 0, hz)); k = FO / zc; q = HERO_D / zc
    shl = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(shl).ellipse([sx - 200 * k, sy - 24 * k, sx + 200 * k, sy + 30 * k], fill=(0, 0, 0, 150))
    img.alpha_composite(shl.filter(ImageFilter.GaussianBlur(9)))
    if sp is not None:
        # reflection (flipped, faded)
        im, x0, y0 = sp; fl_im = im.transpose(Image.FLIP_TOP_BOTTOM); ra = np.asarray(fl_im, np.float32).copy()
        ys = np.linspace(1, 0, ra.shape[0], dtype=np.float32)[:, None]; ra[..., 3] *= (ys ** 1.5) * 0.28
        fl_sp = (Image.fromarray(ra.astype(np.uint8), "RGBA"), x0, 2 * HERO_D * 0 + (H - (y0 + im.height)))
        refl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        w_, h_ = max(1, int(im.width * q)), max(1, int(im.height * q)); rs = fl_sp[0].resize((w_, h_), Image.LANCZOS)
        foot_y = sy; top = int(foot_y + (sy - 470 * k + (y0 - H / 2) * q + h_ * 0) * 0)
        # place so the flipped sprite starts at the feet line
        sprite_bottom = sy - 470 * k + (y0 + im.height - H / 2) * q
        refl.paste(rs, (int(round(sx + (x0 - W / 2) * q)), int(round(2 * sy - sprite_bottom))))
        img.alpha_composite(refl)
        RD.paste_sprite(img, sp, sx, sy - 470 * k, q)
    arr = np.asarray(img.convert("RGB"), np.float32)
    xx, yy2 = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    vig = 1 - 0.55 * (((xx - W / 2) / (W * 0.75)) ** 2 + ((yy2 - H * 0.45) / (H * 0.7)) ** 2)
    arr = np.clip(arr * np.clip(vig, 0.25, 1.0)[..., None], 0, 255)
    img = ImageOps.mirror(Image.fromarray(arr.astype(np.uint8), "RGB")).convert("RGBA"); text(img, t); return img.convert("RGB")

_F = {}
def font(sz):
    if sz not in _F: _F[sz] = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Medium.otf", sz)
    return _F[sz]
CAPS = [(0.0, 3.0, "Revenge is a waste of time."), (3.0, 6.33, "Just close the door."), (6.33, 10.1, "And move on...")]
def text(img, t):
    d = ImageDraw.Draw(img, "RGBA")
    for a, b, s in CAPS:
        if a <= t < b:
            al = min(1.0, (t - a) / 0.45) if a == 0.0 or True else 1.0
            w = d.textlength(s, font=font(50)); layer = Image.new("RGBA", img.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
            ld.text(((W - w) / 2 + 2, 432 + 3), s, font=font(50), fill=(0, 0, 0, int(140 * al)))
            ld.text(((W - w) / 2, 432), s, font=font(50), fill=(255, 255, 255, int(255 * al))); img.alpha_composite(layer); break
    lab = "S L O W   L I G H T"; w = d.textlength(lab, font=font(30))
    d.text(((W - w) / 2, 1822), lab, font=font(30), fill=(255, 255, 255, 200), stroke_width=3, stroke_fill=(10, 10, 14, 200))

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
