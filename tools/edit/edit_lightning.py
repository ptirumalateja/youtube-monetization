"""Lightning Short rough cut: stock clips + designed overlays, 1080x1920 @ 30 fps.

usage: python3 edit_lightning.py <raw_dir> <sfx_dir> <out.mp4> [vo.mp3]
Without a VO the cut uses the estimated timeline below (silent rough cut with SFX/music).
"""
import sys, subprocess, numpy as np, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

RAW, SFX, OUT = sys.argv[1:4]; VO = sys.argv[4] if len(sys.argv) > 4 else None
W, H, FPS = 1080, 1920, 30
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
F = lambda s: ImageFont.truetype(FB, s)

# shot: (start, end) on the master timeline
SEG = {1: (0, 3), 2: (3, 6), 3: (6, 13), 4: (13, 18), 5: (18, 21), 6: (21, 29)}
TOTAL = 29.0

def frames(name, ss, dur, vf, shape):
    """Yield RGB frames (numpy, shape = output w x h) of a source clip at 30 fps after an ffmpeg filter."""
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(dur), "-i", os.path.join(RAW, name),
           "-vf", f"fps={FPS},{vf}" if vf else f"fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    n = shape[0] * shape[1] * 3
    while True:
        b = proc.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(shape[1], shape[0], 3)

def track_crop(fr, cx, cy, cw, ch):
    """Crop a cw x ch window centred on (cx, cy) in pixels, clamped, resized to W x H."""
    h, w = fr.shape[:2]; cw, ch = int(cw), int(ch)
    x0 = int(min(max(cx - cw / 2, 0), w - cw)); y0 = int(min(max(cy - ch / 2, 0), h - ch))
    return np.asarray(Image.fromarray(fr[y0:y0 + ch, x0:x0 + cw]).resize((W, H), Image.LANCZOS)), (x0, y0)

def interp(keys, t):
    ts = [k[0] for k in keys]
    return [float(np.interp(t, ts, [k[i] for k in keys])) for i in range(1, len(keys[0]))]

def grade(a, mul=(1, 1, 1), gain=1.0, gamma=1.0):
    f = (a.astype(np.float32) / 255.0) ** gamma * gain * np.array(mul, np.float32)
    return f

VIG = (1 - 0.65 * (((np.linspace(-1, 1, W)[None, :]) ** 2 + (np.linspace(-1, 1, H)[:, None]) ** 2) / 2) ** 1.2)[..., None]
def night(img):
    """Day-for-night storm grade: dark, cold, low saturation, vignette."""
    f = (img.astype(np.float32) / 255.0) ** 1.6
    f = (f * 0.35 + f.mean(2, keepdims=True) * 0.65) * np.array([0.5, 0.64, 0.9], np.float32) * 1.1
    return f * VIG

def to8(f): return (np.clip(f, 0, 1) * 255).astype(np.uint8)

def stroke_text(d, xy, txt, size, fill=(255, 255, 255, 255), anchor="mm", sw=6):
    d.text(xy, txt, font=F(size), fill=fill, anchor=anchor, stroke_width=sw, stroke_fill=(0, 0, 0, fill[3]))

def env(t, t0, a=0.03, d=0.35):
    """Attack/decay envelope of a flash at t0."""
    if t < t0: return 0.0
    if t < t0 + a: return (t - t0) / a
    return float(np.exp(-(t - t0 - a) / d * 3))

def over(base, layer):
    """Alpha-composite an RGBA PIL layer onto a float RGB frame."""
    l = np.asarray(layer).astype(np.float32) / 255.0
    return base * (1 - l[..., 3:]) + l[..., :3] * l[..., 3:]

enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                        "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                        "-pix_fmt", "yuv420p", OUT + ".video.mp4"], stdin=subprocess.PIPE)
def emit(f):
    enc.stdin.write(to8(f).tobytes())

# ---------- shot 1: bolt hits the sea (264199, 1920x1080, bolt near x~1580) ----------
STRIKES = [0.0, 1.25, 2.15]
def shot1():
    s, e = SEG[1]; n = int((e - s) * FPS)
    for i, fr in enumerate(frames("264199.mp4", 0.5, e - s + 0.5, None, (1920, 1080))):
        if i >= n: break
        t = i / FPS
        bx = 1580 - 40 * t / 3
        # gate the persistent bolt so it strikes and vanishes like real lightning
        g = fr.astype(np.float32) / 255.0
        lum = g.mean(2)
        bg = np.asarray(Image.fromarray(fr).filter(ImageFilter.GaussianBlur(14))).astype(np.float32) / 255.0
        m = np.clip((lum - bg.mean(2) - 0.12) * 5, 0, 1)
        m[int(0.37 * 1080):] = 0; m[:, : int(bx - 260)] = 0; m[:, int(bx + 260):] = 0
        m = np.asarray(Image.fromarray(to8(m)).filter(ImageFilter.GaussianBlur(3))).astype(np.float32) / 255.0
        k = max(env(t, st, 0.02, 0.25) for st in STRIKES)
        vis = m * (0.05 + 0.95 * k)
        g = (fr.astype(np.float32) / 255.0) * vis[..., None] + bg * (m * (1 - vis))[..., None] + \
            (fr.astype(np.float32) / 255.0) * (1 - m)[..., None]
        g *= 0.75 + 0.6 * k  # sky lights up with each strike
        img, _ = track_crop(to8(g), bx - 80, 540, 608, 1080)
        f = img.astype(np.float32) / 255.0
        f = f + env(t, 0.03, 0.0, 0.15) * 0.35 + env(t, 1.25, 0.0, 0.12) * 0.3  # flash, bolt stays readable on frame 0
        # shake on the first strike
        sh = env(t, 0.0, 0.0, 0.4)
        if sh > 0.02:
            dx, dy = int(np.sin(t * 90) * 22 * sh), int(np.cos(t * 70) * 16 * sh)
            f = np.roll(np.roll(f, dx, 1), dy, 0)
        yield t + s, f

# ---------- shot 2: dark school of fish (15158164, 4K) ----------
def shot2():
    s, e = SEG[2]; n = int((e - s) * FPS)
    for i, fr in enumerate(frames("15158164_3840_2160_50fps.mp4", 2.0, e - s + 0.5, "scale=1920:1080", (1920, 1080))):
        if i >= n: break
        t = i / FPS
        img, _ = track_crop(fr, 900 + 30 * t, 520, 560 - 20 * t, int((560 - 20 * t) * 16 / 9))
        f = grade(img, (0.85, 1.0, 1.15), 1.25, 0.9)
        f += env(t, 0.0, 0.0, 0.2) * np.linspace(0.6, 0, H)[:, None, None]  # strike light from above
        yield t + s, f

# ---------- shot 3: dark sea from above + current rings (17890015, swimmer cropped out) ----------
RC = (540, 760)
def shot3():
    s, e = SEG[3]; n = int((e - s) * FPS)
    for i, fr in enumerate(frames("17890015-uhd_3840_2160_30fps.mp4", 0.0, e - s + 0.5, "scale=1920:1080", (1920, 1080))):
        if i >= n: break
        t = i / FPS
        img, _ = track_crop(fr, 1600 - 8 * t, 540, 600, 1067)
        f = night(img)
        f += env(t, 0.0, 0.0, 0.25) * 0.15
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        # glow at the strike point
        for r in range(140, 0, -14):
            a = int(255 * (1 - r / 140) * (0.5 + 0.5 * env(t % 0.8, 0.0, 0.0, 0.5)))
            d.ellipse([RC[0] - r, RC[1] - r * 0.55, RC[0] + r, RC[1] + r * 0.55], fill=(170, 220, 255, a // 3))
        # rings spread outward and weaken with distance
        for k in range(12):
            age = t - k * 0.55
            if age < 0: continue
            r = 40 + age * 380
            a = 255 * min(1, 160 / (60 + r)) * max(0, 1 - age / 3.2)
            if a < 4: continue
            wdt = max(3, int(22 * 120 / (120 + r)))
            for gw, ga in ((wdt * 3, 0.25), (wdt, 1.0)):  # soft glow + core line
                d.ellipse([RC[0] - r, RC[1] - r * 0.55, RC[0] + r, RC[1] + r * 0.55], outline=(150, 215, 255, int(a * ga)), width=gw)
        lay = lay.filter(ImageFilter.GaussianBlur(2)); d = ImageDraw.Draw(lay)
        # strength labels: meaning of the rings is spelled out (no unexplained graphics)
        la = min(1, max(0, (t - 1.5) / 0.4))
        if la > 0:
            stroke_text(d, (RC[0], RC[1] + 20), "STRONG", 46, (255, 255, 255, int(255 * la)))
            stroke_text(d, (RC[0], RC[1] + 470), "WEAK", 46, (170, 200, 230, int(255 * min(1, max(0, (t - 3) / 0.4)))))
            # falloff bar: current strength drops with distance
            bx0, by = 160, 1480
            for j in range(40):
                v = 1 / (1 + j * 0.35)
                if j / 40 > (t - 1.5) / 3: break
                d.rectangle([bx0 + j * 19, by - int(220 * v), bx0 + j * 19 + 14, by], fill=(150, 215, 255, int(230 * la)))
            stroke_text(d, (W // 2, by + 60), "CURRENT  vs  DISTANCE", 40, (255, 255, 255, int(230 * la)), sw=4)
        yield t + s, over(f, lay)

# ---------- shot 4: single fish, tiny voltage across its body (14691495, 4K) ----------
FISH = [(0, .53, .72), (.74, .45, .67), (1.48, .40, .59), (2.21, .31, .61), (2.95, .31, .65),
        (3.69, .27, .70), (4.43, .24, .72), (5.17, .17, .74)]
def shot4():
    s, e = SEG[4]; n = int((e - s) * FPS)
    for i, fr in enumerate(frames("14691495_3840_2160_30fps.mp4", 0.0, 5.9, "scale=1920:1080", (1920, 1080))):
        if i >= n: break
        t = i / FPS
        fx, fy = interp(FISH, t * 5.9 / (e - s) * 0.95)
        cw = 600 - 25 * t; ch = int(cw * 16 / 9)
        img, (x0, y0) = track_crop(fr, fx * 1920 + 60, fy * 1080 - 120, int(cw), ch)
        f = grade(img, (0.9, 1.0, 1.1), 1.15, 1.0)
        sc = W / cw; px, py = (fx * 1920 - x0) * sc, (fy * 1080 - y0) * sc
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        a = min(1, max(0, (t - 0.6) / 0.4))
        if a > 0:
            L = 0.075 * 1920 * sc  # half body length in output pixels
            hx, tx = px - L, px + L * 0.9
            yy = py - 0.06 * 1080 * sc
            col = (255, 230, 120, int(255 * a))
            d.line([hx, yy, tx, yy], fill=col, width=5)
            for x in (hx, tx):
                d.line([x, yy - 22, x, yy + 22], fill=col, width=5)
                d.ellipse([x - 9, py - 9, x + 9, py + 9], outline=col, width=4)
            stroke_text(d, ((hx + tx) / 2, yy - 70), "VOLTAGE ACROSS ITS BODY", 50, (255, 255, 255, int(255 * a)), sw=4)
            stroke_text(d, ((hx + tx) / 2, yy - 150), "TINY", 110, col, sw=8)
        yield t + s, over(f, lay)

# ---------- shot 5: surface from below, near the strike = danger (265150 top of frame) ----------
def shot5():
    s, e = SEG[5]; n = int((e - s) * FPS)
    for i, fr in enumerate(frames("265150_medium.mp4", 1.0, e - s + 0.5, None, (2560, 1440))):
        if i >= n: break
        t = i / FPS
        img, _ = track_crop(fr, 1100 + 40 * t, 560, 630, 1120)
        f = grade(img, (0.85, 0.95, 1.05), 1.0, 1.0)
        fl = max(env(t, st, 0.0, 0.15) for st in (0.2, 0.9, 1.15, 2.1))
        f += fl * 0.8 * np.linspace(1, 0, H)[:, None, None] ** 2
        red = 0.25 + 0.2 * np.sin(t * 8) ** 2
        f = f * (1 - red) + red * np.array([0.9, 0.08, 0.05]) * f.mean(2, keepdims=True) * 2.2
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        a = min(1, max(0, (t - 0.8) / 0.3))
        stroke_text(d, (W // 2, 1250), "NEAR THE STRIKE", 64, (255, 255, 255, int(255 * a)))
        stroke_text(d, (W // 2, 1340), "FISH CAN STILL DIE", 64, (255, 90, 70, int(255 * a)))
        yield t + s, over(f, lay)

# ---------- shot 6: swimmer at the surface, push in, final flash (17890015) ----------
SWIM = [(0, .44, .585), (4, .48, .607), (8, .502, .612)]
def shot6():
    s, e = SEG[6]; n = int((e - s) * FPS)
    for i, fr in enumerate(frames("17890015-uhd_3840_2160_30fps.mp4", 6.0, e - s + 0.5, None, (3840, 2160))):
        if i >= n: break
        t = i / FPS; u = t / (e - s)
        sx, sy = interp(SWIM, t)
        ch = int(1700 - (1700 - 520) * (1 - (1 - u) ** 2)); cw = int(ch * 9 / 16)
        img, (x0, y0) = track_crop(fr, sx * 3840, sy * 2160, cw, ch)
        f = night(img)
        fl = max(env(t, st, 0.0, 0.2) for st in (1.2, 1.45, 4.0, 6.5, 6.7))
        f = f * (1 + fl * 1.1) + fl * np.array([0.12, 0.13, 0.16])  # lightning lights up the sea
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        if t > 5.6:  # "...like you": mark the swimmer
            sc = W / cw; px, py = (sx * 3840 - x0) * sc, (sy * 2160 - y0) * sc
            a = min(1, (t - 5.6) / 0.25); r = 130 + 20 * np.sin(t * 10)
            d.ellipse([px - r, py - r, px + r, py + r], outline=(255, 70, 60, int(255 * a)), width=8)
            stroke_text(d, (W // 2, py - r - 80), "YOU", 90, (255, 255, 255, int(255 * a)))
        yield t + s, over(f, lay)

for gen in (shot1, shot2, shot3, shot4, shot5, shot6):
    for t, f in gen():
        if 0.35 < t < SEG[2][1]:  # hook question over the opening shots
            a = min(1, (t - 0.35) / 0.15)
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
            stroke_text(d, (W // 2, 330), "WHY ARE THESE FISH", 72, (255, 255, 255, int(255 * a)), sw=7)
            stroke_text(d, (W // 2, 420), "STILL ALIVE?", 92, (255, 225, 90, int(255 * a)), sw=8)
            f = over(f, lay)
        emit(f)
enc.stdin.close(); enc.wait()

# ---------- sound: reuse library SFX + music (no new credits) ----------
cues = [("impact.mp3", 0.0, 1.0), ("titlehit.mp3", 0.0, 0.6), ("impact.mp3", 1.25, 0.4),
        ("whoosh.mp3", 2.85, 0.5), ("whoosh.mp3", 5.85, 0.5), ("pulse.mp3", 6.0, 0.7), ("rift.mp3", 6.6, 0.5),
        ("whoosh.mp3", 12.85, 0.4), ("pulse.mp3", 14.0, 0.4), ("impact.mp3", 18.2, 0.5), ("rift.mp3", 18.9, 0.4),
        ("whoosh.mp3", 20.85, 0.5), ("riser.mp3", 23.3, 0.6), ("impact.mp3", 26.6, 0.7)]
inp = ["-i", OUT + ".video.mp4", "-stream_loop", "-1", "-i", f"{SFX}/wind.mp3", "-i", f"{SFX}/music.mp3"]
for nm, _, _ in cues: inp += ["-i", f"{SFX}/{nm}"]
fc = f"[1:a]atrim=0:{TOTAL},volume=0.35[wind];[2:a]atrim=0:{TOTAL},volume=0.45[mus];"
for k, (_, t, v) in enumerate(cues):
    ms = int(t * 1000); fc += f"[{k+3}:a]volume={v},adelay={ms}|{ms}[c{k}];"
fc += "[wind][mus]" + "".join(f"[c{k}]" for k in range(len(cues))) + \
      f"amix=inputs={len(cues)+2}:normalize=0,atrim=0:{TOTAL},afade=t=out:st={TOTAL-0.05}:d=0.05,loudnorm=I=-14:TP=-1.0[aout]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(TOTAL), OUT], check=True)
os.remove(OUT + ".video.mp4")
print("wrote", OUT)
