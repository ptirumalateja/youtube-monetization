"""Lightning Short v3: premium animated plates (ChatGPT stills animated here), end question + brand card.

usage: PLATES=<plates_dir> python3 edit_lightning_v3.py <raw_dir> <sfx_dir> <vo.wav> <out.mp4>

Structure (times follow the tightened VO, ~33 s):
  hook     0.00-1.95  real strike (264199), bolt gated into real-length strikes, hook question on frame 0
           1.95-4.05  real storm sea (201766) relit by a second strike: "hundreds of millions of volts"
  question 4.05-6.45  dive -> real fish school (265150)
  explain  6.45-17.85 designed cross-section: strike, field spreads in every direction, iso-lines,
                      pan to a far fish sitting between two lines
  science  17.85-23.65 real fish (14691495) matched to the designed fish; widely spaced iso-lines, then clean
  danger   23.65-28.20 designed close-up at the strike: lines crowd across a near-surface fish, it turns red
  payoff   28.20-30.00 boat under a storm sky (223459), 30.00-end swimmer at water level (113675)
           "like you" -> sound drops out -> video ends; the loop restarts on the strike.
"""
import sys, os, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lightning_scene as LS
import lightning_plates as LP
PLATES = os.environ.get("PLATES", "")

RAW, SFX, VO, OUT = sys.argv[1:5]
W, H, FPS = 1080, 1920, 30
TOTAL = 36.25
VO_END = 32.95
FB = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"
FE = "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf"
font = lambda p, s: ImageFont.truetype(p, s)

# ---------------- helpers ----------------
def frames(name, ss, dur, vf, size):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(ss), "-t", str(dur), "-i", os.path.join(RAW, name),
           "-vf", f"fps={FPS}" + (f",{vf}" if vf else ""), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    n = size[0] * size[1] * 3
    while True:
        b = p.stdout.read(n)
        if len(b) < n: break
        yield np.frombuffer(b, np.uint8).reshape(size[1], size[0], 3)
    p.kill()

def crop(fr, cx, cy, cw, ch):
    """cw x ch window centred on (cx, cy) in source px, clamped, resized to W x H (float 0..1)."""
    h, w = fr.shape[:2]; cw, ch = int(round(cw)), int(round(ch))
    x0 = int(min(max(cx - cw / 2, 0), w - cw)); y0 = int(min(max(cy - ch / 2, 0), h - ch))
    im = Image.fromarray(fr[y0:y0 + ch, x0:x0 + cw]).resize((W, H), Image.LANCZOS)
    if cw < W:  # upscaled source: gentle sharpening
        im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=2))
    return np.asarray(im, np.float32) / 255, (x0, y0)

def interp(keys, t):
    ts = [k[0] for k in keys]
    return [float(np.interp(t, ts, [k[i] for k in keys])) for i in range(1, len(keys[0]))]

def ease(u): u = min(max(u, 0), 1); return u * u * (3 - 2 * u)

def env(t, t0, a=0.02, d=0.25):
    if t < t0: return 0.0
    if t < t0 + a: return (t - t0) / a
    return float(np.exp(-(t - t0 - a) / d * 3))

def flicker(t, t0):
    """Real lightning flickers: 2-3 return strokes within ~0.3 s."""
    return max(env(t, t0, 0.01, 0.12), 0.7 * env(t, t0 + 0.09, 0.01, 0.10), 0.5 * env(t, t0 + 0.22, 0.01, 0.2))

# one look for all footage: cold storm night, deep teal water, controlled highlights
def look(f, exp=1.0, sat=0.75, tint=(0.80, 0.95, 1.10), lift=0.012, gamma=1.15):
    f = np.clip(f * exp, 0, None) ** gamma
    g = f.mean(2, keepdims=True)
    f = g + (f - g) * sat
    f = f * np.array(tint, np.float32)
    f = f / (1 + 0.35 * f)  # soft shoulder
    return f * (1 - lift) + lift * np.array([0.25, 0.45, 0.55], np.float32)

def relight(f, k, col=(0.85, 0.92, 1.0)):
    return f * (1 + 1.6 * k) + k * 0.10 * np.array(col, np.float32)

# ---------------- finishing (applied to every frame) ----------------
yy, xx = np.mgrid[0:H, 0:W]
VIG = (1 - 0.55 * (((xx - W / 2) / (W / 2)) ** 2 * 0.6 + ((yy - H / 2) / (H / 2)) ** 2) ** 1.3).clip(0.25, 1)[..., None].astype(np.float32)
RG = np.random.default_rng(3)
GRAIN = [np.asarray(Image.fromarray(((RG.standard_normal((H // 2, W // 2)) * 40 + 128).clip(0, 255)).astype(np.uint8))
                    .resize((W, H), Image.BICUBIC), np.float32)[..., None] / 255 - 0.5 for _ in range(12)]

def finish(f, i):
    f = f * VIG
    hi = np.clip(f - 0.62, 0, None)  # bloom / halation on highlights
    small = Image.fromarray((np.clip(hi, 0, 1) * 255).astype(np.uint8)).resize((W // 8, H // 8), Image.BILINEAR)
    bl = np.asarray(small.filter(ImageFilter.GaussianBlur(6)).resize((W, H), Image.BILINEAR), np.float32) / 255
    f = f + bl * np.array([0.9, 1.0, 1.1]) * 0.9
    lum = f.mean(2, keepdims=True)
    f = f + GRAIN[i % 12] * (0.07 - 0.04 * np.clip(lum, 0, 1))  # more grain in shadows, film-like
    return np.clip(f, 0, 1)

# ---------------- text ----------------
def text_layer(lines, y, size, colors, a=1.0, fnt=FB, spacing=1.08):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(sh)
    for k, (ln, c) in enumerate(zip(lines, colors)):
        yy_ = y + k * size * spacing
        ds.text((W // 2, yy_ + 6), ln, font=font(fnt, size), fill=(0, 0, 0, int(200 * a)), anchor="mm")
        d.text((W // 2, yy_), ln, font=font(fnt, size), fill=c + (int(255 * a),), anchor="mm",
               stroke_width=3, stroke_fill=(0, 0, 0, int(160 * a)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    return Image.alpha_composite(sh, lay)

def over(f, lay):
    l = np.asarray(lay, np.float32) / 255
    return f * (1 - l[..., 3:]) + l[..., :3] * l[..., 3:]

WHITE, YEL = (255, 255, 255), (255, 214, 64)
CAPS = [("SEAWATER CONDUCTS", 6.66, 7.80, 0), ("ELECTRICITY", 7.80, 8.42, 1), ("SO THE CURRENT", 8.42, 9.40, 0),
        ("DOESN'T STAY", 9.40, 10.10, 0), ("IN ONE PLACE", 10.10, 11.28, 0), ("IT SPREADS OUT", 11.30, 12.05, 1),
        ("THROUGH THE WATER", 12.05, 12.74, 0), ("IN EVERY DIRECTION", 12.74, 13.90, 1), ("AND WEAKENS FAST", 13.90, 15.28, 1),
        ("WITH DISTANCE", 15.28, 16.60, 0), ("AWAY FROM THE STRIKE", 16.70, 18.00, 0), ("A FISH IS SMALL", 18.00, 19.02, 0),
        ("AND SURROUNDED BY WATER", 19.02, 20.42, 0), ("ONLY A TINY VOLTAGE", 20.42, 22.26, 1), ("CROSSES ITS BODY", 22.26, 23.80, 0),
        ("RIGHT NEXT TO THE STRIKE", 23.82, 25.20, 0), ("NEAR THE SURFACE?", 25.20, 26.80, 0), ("FISH CAN STILL DIE", 26.80, 28.40, 2),
        ("BUT THE REAL DANGER", 28.50, 29.38, 0), ("IS ANYTHING STICKING OUT", 29.38, 30.72, 1), ("OF THE WATER", 30.72, 32.02, 0),
        ("LIKE YOU.", 32.05, VO_END, 2)]
CAP_CACHE = {}
def captions(f, T):
    for txt, a, b, hl in CAPS:
        if a <= T < b:
            pop = min(1, (T - a) / 0.08)
            key = (txt, round(pop, 1))
            if key not in CAP_CACHE:
                col = [WHITE, YEL, (255, 92, 70)][hl]
                size = 78
                while font(FB, size).getlength(txt) > 960: size -= 2
                CAP_CACHE[key] = text_layer([txt], 1330, int(size * (0.92 + 0.08 * pop)), [col], pop, FB)
            return over(f, CAP_CACHE[key])
    return f
HOOK = None
def hook(f, T):
    global HOOK
    if T < 6.30:
        if HOOK is None:
            HOOK = text_layer(["WHY ARE THESE FISH", "STILL ALIVE?"], 300, 84, [WHITE, YEL], 1.0, FB)
        a = 1.0 if T < 6.0 else 1 - (T - 6.0) / 0.3
        lay = HOOK if a >= 1 else Image.fromarray((np.asarray(HOOK) * np.array([1, 1, 1, a])).astype(np.uint8))
        return over(f, lay)
    return f

# ---------------- shots ----------------
SH = [("strike", 0.00, 1.95), ("storm", 1.95, 4.05), ("school", 4.05, 6.45), ("explain", 6.45, 17.85),
      ("fish", 17.85, 23.65), ("danger", 23.65, 28.20), ("boat", 28.20, 30.00), ("swimmer", 30.00, VO_END),
      ("question", VO_END, 34.75), ("brand", 34.75, TOTAL)]
def n_of(a, b): return int(round(b * FPS)) - int(round(a * FPS))

_PL = {}
def plate(n):
    if n not in _PL: _PL[n] = LP.Plate(PLATES, n)
    return _PL[n]

def pl_look(f):  # plates are already graded; pull them a touch toward the footage look
    g = f.mean(2, keepdims=True)
    return (g + (f - g) * 0.9) * np.array([0.95, 1.0, 1.02], np.float32)

def smear(f, s, k=30):
    im = Image.fromarray((np.clip(f, 0, 1) * 255).astype(np.uint8)).filter(ImageFilter.BoxBlur(int(1 + k * s)))
    return np.asarray(im, np.float32) / 255

def shake(f, t, t0, amp=18, d=0.35):
    sh = env(t, t0, 0.0, d)
    if sh > 0.02:
        f = np.roll(np.roll(f, int(np.sin(t * 95) * amp * sh), 1), int(np.cos(t * 77) * amp * 0.8 * sh), 0)
    return f

def shot_strike(a, b):
    P = plate("p2_strike")
    for i in range(n_of(a, b)):
        t = i / FPS; u = ease(t / (b - a))
        k = max(flicker(t, -0.02), 0.9 * (t < 0.30), flicker(t, 1.15))
        f = P.frame(bolt_k=k, splash_k=0.6 + 0.4 * k)
        f, ts, ppu = LP.view(f, 0.50, 0.33 + 0.03 * u, 1.55 - 0.2 * u)
        f = LP.rings(f, 0.05, t, ts, ppu, P.sx, P.sy, n=2, every=0.5, strength=0.7)
        f = LP.rain(f, t, 0.9)
        f = shake(f, t, 0.0)
        yield pl_look(f)

def shot_storm(a, b):
    P = plate("p2_strike")
    for i in range(n_of(a, b)):
        t = i / FPS; u = ease(t / (b - a))
        k = flicker(t, 0.30)
        f = P.frame(bolt_k=k, splash_k=0.6 + 0.4 * k)
        f, ts, ppu = LP.view(f, 0.50, 0.36 + 0.14 * u, 1.35 - 0.35 * u)
        f = LP.rain(f, t + 2, 1.0)
        if t > (b - a) - 0.25:  # tilt down into the water
            sv = (t - (b - a - 0.25)) / 0.25; f = smear(f, sv) * (1 - 0.5 * sv)
        yield pl_look(f)

def shot_school(a, b):
    P = plate("p1_split")
    for i in range(n_of(a, b)):
        t = i / FPS; u = ease(t / (b - a))
        k = max(flicker(t, 0.15), flicker(t, 1.30))
        f = P.frame(bolt_k=0.4 + 0.8 * k)
        f, ts, ppu = LP.view(f, 0.62 - 0.17 * u, 0.24 + 0.36 * u, 1.45 - 0.33 * u)
        f = LP.shimmer(f, t, 500, 1.5)
        f = LP.bubbles(f, t, 0.8, 0.3)
        if t < 0.3: s_ = 1 - t / 0.3; f = smear(f, s_, 18) + s_ * 0.2 * np.array([0.5, 0.85, 1.0])
        yield pl_look(f)

def shot_explain(a, b):
    P2, P1, P3 = plate("p2_strike"), plate("p1_split"), plate("p3_nobolt")
    for i in range(n_of(a, b)):
        t = i / FPS; T = a + t
        if T < 11.30:      # strike lands; current spreads across the surface; arrows on "doesn't stay in one place"
            u = ease((T - a) / (11.30 - a))
            k = flicker(T, 6.62) + 0.5 * flicker(T, 7.9)
            f = P2.frame(bolt_k=k, splash_k=0.65 + 0.35 * k)
            f, ts, ppu = LP.view(f, 0.50, 0.36 + 0.06 * u, 1.45 - 0.40 * u)
            f = LP.rings(f, 6.70, T, ts, ppu, P2.sx, P2.sy, every=0.5, n=14, life=4.0)
            f = LP.arrows(f, 8.80, T, ts, ppu, P2.sx, P2.sy, n=8, dur=1.3)
            f = LP.rain(f, T, 0.5)
            la = ease((T - 7.0) / 0.3) * (1 - ease((T - 9.4) / 0.3))
            ax, ay = ts(P2.sx, P2.sy)
            f = LP.label(f, (ax + 190, ay - 170), (ax + 6, ay - 4), "STRIKE POINT", la)
        elif T < 14.20:    # through the water, in every direction: pulses travel out from the strike
            u = ease((T - 11.30) / 2.9)
            k = flicker(T, 11.32)
            f = P1.frame(bolt_k=0.4 + 0.8 * k)
            f, ts, ppu = LP.view(f, 0.60, 0.36 + 0.06 * u, 1.25 + 0.15 * u)
            f = LP.shimmer(f, T, 450, 1.5)
            f = LP.wave_glow(f, 11.35, T, ts(P1.sx, P1.sy), speed=850, width=150, strength=0.8)
            f = LP.bubbles(f, T, 0.6, 0.35)
        else:              # aftermath: rings fading with distance, then away from the strike
            if T < 16.6: cx, cy, z = 0.50, 0.42 + 0.06 * ease((T - 14.2) / 2.4), 1.15 - 0.15 * ease((T - 14.2) / 2.4)
            else:        u = ease((T - 16.6) / 1.25); cx, cy, z = 0.50 + 0.12 * u, 0.48 + 0.30 * u, 1.0 + 0.25 * u
            f = P3.frame(bolt_k=0.0, splash_k=1.0)
            f, ts, ppu = LP.view(f, cx, cy, z)
            sxp, syp = ts(P3.sx, P3.sy)
            Y, X = np.mgrid[0:H, 0:W]
            f = f + np.exp(-(((X - sxp) ** 2) + ((Y - syp) / 0.45) ** 2) / (2 * 70 ** 2))[..., None] * LP.VOLT * 0.5
            f = LP.rings(f, 12.6, T, ts, ppu, P3.sx, P3.sy, every=0.6, n=10, life=4.5, strength=0.9)
            f = LP.rain(f, T, 0.35)
        yield pl_look(f)

FISHKEY = [(0, .53, .72), (.74, .45, .67), (1.48, .40, .59), (2.21, .31, .61), (2.95, .31, .65), (3.69, .27, .70), (4.43, .24, .72), (5.17, .17, .74), (5.9, .14, .75)]
def shot_fish(a, b):
    for i, fr in enumerate(frames("14691495_3840_2160_30fps.mp4", 0.0, 5.9, None, (3840, 2160))):
        if i >= n_of(a, b): return
        t = i / FPS; T = a + t
        fx, fy = interp(FISHKEY, t)
        cw = 1000 - 40 * t
        f, (x0, y0) = crop(fr, fx * 3840 - 60, fy * 2160 - 60, cw, cw * 16 / 9)
        f = look(f, 0.85, 0.55, (0.70, 0.95, 1.05), gamma=1.2)
        # restrained science cue: widely spaced iso-lines drift across; the fish fits between two of them
        la = ease((T - 20.45) / 0.5) * (1 - ease((T - 22.9) / 0.5))
        if la > 0:
            sc = W / cw; px = (fx * 3840 - x0) * sc; py = (fy * 2160 - y0) * sc
            spacing = 1.9 * 0.16 * 3840 * sc  # lines ~2 body lengths apart: tiny difference across the fish
            X = np.arange(W)[None, :]
            ph = (X - px + 0.55 * spacing) / spacing
            d = np.abs(ph - np.round(ph)) * spacing
            line = np.exp(-(d / 2.2) ** 2) * np.ones((H, 1))
            f = f + line[..., None] * LS.VOLT * 0.75 * la
            # bracket across the body + tiny delta label
            lay = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(lay)
            L = 0.16 * 3840 * sc / 2; px = px + 0.02 * 3840 * sc; yb = py - 0.11 * 2160 * sc
            c = (150, 220, 255, int(230 * la))
            dr.line([px - L, yb, px + L, yb], fill=c, width=4)
            for xq in (px - L, px + L): dr.line([xq, yb - 16, xq, yb + 16], fill=c, width=4)
            dr.text((px, yb - 50), "TINY DIFFERENCE", font=font(FE, 54), fill=c, anchor="mm", stroke_width=3, stroke_fill=(0, 0, 0, int(150 * la)))
            f = over(f, lay)
        yield f

def shot_danger(a, b):
    P4, P5 = plate("p4_danger"), plate("p5_fish_hit")
    for i in range(n_of(a, b)):
        t = i / FPS; T = a + t
        if T < 26.55:   # right next to the strike, near the surface
            u = ease((T - a) / (26.55 - a))
            k = max(flicker(T, a + 0.05), flicker(T, a + 1.4))
            f = P4.frame(bolt_k=0.4 + 0.9 * k)
            f, ts, ppu = LP.view(f, 0.45 - 0.07 * u, 0.36, 1.2 + 0.3 * u)
            f = LP.shimmer(f, T, 700, 1.5)
            f = LP.bubbles(f, T, 0.8, 0.35)
            f = LP.red_pulse(f, T, ts(0.36, 0.39), 90, 0.25 + 0.35 * u)
        else:           # fish can still die
            u = ease((T - 26.55) / (b - 26.55))
            k = flicker(T, 26.55)
            f = P5.frame(bolt_k=0.5 + 1.0 * k)
            f, ts, ppu = LP.view(f, 0.50, 0.52 + 0.04 * u, 1.12 + 0.2 * u)
            f = LP.bubbles(f, T, 1.0, 0.3)
            f = LP.red_pulse(f, T, ts(0.47, 0.60), 160, 0.7)
            f = f + env(T, 26.55, 0.0, 0.18) * 0.6
            f = shake(f, T, 26.55, 22, 0.4)
        yield pl_look(f)

def shot_boat(a, b):
    for i, fr in enumerate(frames("223459_medium.mp4", 9.4, b - a + 0.5, None, (2560, 1440))):
        if i >= n_of(a, b): return
        t = i / FPS; u = t / (b - a)
        z = 1 + 0.08 * u
        f, _ = crop(fr, 1357 - 30 * t, 640, 760 / z, 1351 / z)
        f = look(f, 0.70, 0.65, (0.95, 0.88, 0.95), gamma=1.25)  # warmer, threatening sky
        f = relight(f, flicker(t, 0.55), (1.0, 0.9, 0.95))
        yield f

def shot_swimmer(a, b):
    for i, fr in enumerate(frames("113675-698820547_medium.mp4", 6.0, b - a + 0.5, None, (1280, 720))):
        if i >= n_of(a, b): return
        t = i / FPS; T = a + t; u = t / (b - a)
        z = 1 + 0.10 * ease(u) + (0.06 * ease((T - 32.05) / 0.4))  # push in on "like you"
        f, _ = crop(fr, 700, 420, 405 / z, 720 / z)
        f = look(f, 0.85, 0.45, (0.75, 0.93, 1.10), gamma=1.15)  # sunny day -> grey storm light
        f = relight(f, flicker(t, 0.9) * 0.7)
        yield f

def shot_question(a, b):
    P = plate("p3_nobolt")
    base = None
    for i in range(n_of(a, b)):
        t = i / FPS
        f = P.frame(bolt_k=0.0) * (0.42 + 0.5 * flicker(t, 0.9))
        f, ts, ppu = LP.view(f, 0.5, 0.40, 1.15 + 0.04 * t)
        f = LP.rain(f, t, 0.5)
        a1 = ease(t / 0.25); a2 = ease((t - 0.35) / 0.25); a3 = ease((t - 0.7) / 0.25)
        f = over(f, text_layer(["WATER OR BOAT?"], 760, 118, [YEL], a1))
        f = over(f, text_layer(["WHERE WOULD YOU", "BE SAFER?"], 920, 84, [WHITE, WHITE], a2))
        f = over(f, text_layer(["COMMENT BELOW \u2193"], 1180, 54, [(170, 215, 255)], a3, FE))
        yield f

BRAND = None
def shot_brand(a, b):
    global BRAND
    P = plate("p3_nobolt")
    for i in range(n_of(a, b)):
        t = i / FPS
        f = P.frame(bolt_k=0.0) * 0.16
        f, _, _ = LP.view(f, 0.5, 0.30, 1.0 + 0.03 * t)
        if BRAND is None:
            BRAND = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(BRAND)
            d.text((W // 2, 880), "S L O W     L I G H T", font=font("/usr/share/fonts/opentype/inter/InterDisplay-Light.otf", 84), fill=(240, 244, 250, 255), anchor="mm")
            d.line([(W // 2 - 60, 960), (W // 2 + 60, 960)], fill=(200, 210, 225, 255), width=2)
            d.text((W // 2, 1030), "Stories worth slowing down for.", font=font("/usr/share/fonts/opentype/inter/InterDisplay-Light.otf", 46), fill=(200, 210, 225, 255), anchor="mm")
        al = ease(t / 0.4)
        lay = Image.fromarray((np.asarray(BRAND) * np.array([1, 1, 1, al])).astype(np.uint8))
        yield over(f, lay)

GEN = dict(strike=shot_strike, storm=shot_storm, school=shot_school, explain=shot_explain,
           fish=shot_fish, danger=shot_danger, boat=shot_boat, swimmer=shot_swimmer,
           question=shot_question, brand=shot_brand)

ONLY = os.environ.get("ONLY")  # render one shot (parallel renders / quick checks)
VIDEO = os.environ.get("VIDEO")  # skip rendering, mix sound onto this already-rendered video
if VIDEO: os.link(VIDEO, OUT + ".video.mp4") if not os.path.exists(OUT + ".video.mp4") else None
enc = None if VIDEO else subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                        "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "16", "-pix_fmt", "yuv420p",
                        OUT + ".video.mp4"], stdin=subprocess.PIPE)
gi = 0
for name, a, b in ([] if VIDEO else SH):
    if ONLY and name != ONLY: continue
    gi = int(round(a * FPS))
    for k, f in enumerate(GEN[name](a, b)):
        T = a + k / FPS
        f = finish(f, gi)
        f = hook(f, T)
        f = captions(f, T)
        enc.stdin.write((f * 255).astype(np.uint8).tobytes()); gi += 1
    print(name, "done", flush=True)
if enc: enc.stdin.close(); enc.wait()
if ONLY:
    os.replace(OUT + ".video.mp4", OUT); sys.exit()

# ---------------- sound ----------------
# (file, start on timeline, offset into file, duration, volume, filters)
S = lambda n: os.path.join(SFX, n)
CUES = [
    ("thunder_rain.mp3", 0.00, 0.00, 4.15, 1.00, "afade=t=out:st=3.85:d=0.3"),
    ("boom.mp3", 0.00, 0.00, 3.0, 0.55, ""),
    ("distant_thunder.mp3", 2.10, 5.70, 2.0, 0.6, "afade=t=out:st=1.7:d=0.3"),
    ("dive_underwater.mp3", 3.92, 0.00, 2.0, 0.9, ""),
    ("underwater_ambience.mp3", 4.05, 0.00, 22.0, 0.75, "afade=t=in:d=0.2"),
    ("underwater_ambience.mp3", 25.9, 2.00, 2.35, 0.75, "afade=t=out:st=2.0:d=0.3"),
    ("distant_thunder.mp3", 4.30, 12.0, 23.8, 0.35, "lowpass=f=300,afade=t=out:st=23.4:d=0.4"),
    ("deep_drone.mp3", 4.05, 3.00, 28.0, 0.55, "afade=t=in:d=1.5,afade=t=out:st=27.6:d=0.4"),
    ("thunder_rain.mp3", 6.62, 0.00, 2.6, 0.55, "lowpass=f=900,afade=t=out:st=2.0:d=0.6"),
    ("electric_spark.mp3", 8.40, 0.00, 2.5, 0.35, "afade=t=out:st=2.0:d=0.5"),
    ("electric_spark.mp3", 11.40, 0.00, 3.0, 0.25, "afade=t=out:st=2.4:d=0.6"),
    ("electric_spark.mp3", 23.68, 0.00, 2.0, 0.40, "afade=t=out:st=1.5:d=0.5"),
    ("boom.mp3", 26.55, 0.00, 1.6, 0.6, "afade=t=out:st=1.2:d=0.4"),
    ("electric_spark.mp3", 26.55, 0.00, 1.0, 0.6, "afade=t=out:st=0.6:d=0.4"),
    ("distant_thunder.mp3", 32.95, 20.0, 3.3, 0.5, "afade=t=in:d=0.3,afade=t=out:st=2.8:d=0.5"),
    ("deep_drone.mp3", 32.95, 12.0, 3.3, 0.35, "afade=t=in:d=0.3,afade=t=out:st=2.6:d=0.7"),
    ("boom.mp3", 34.75, 0.00, 1.5, 0.3, "lowpass=f=220,afade=t=out:st=1.0:d=0.5"),
    ("ocean_storm.mp3", 28.20, 4.00, 3.85, 0.85, "afade=t=out:st=3.55:d=0.3"),
    ("big_thunder.mp3", 28.45, 8.80, 3.6, 0.9, "afade=t=out:st=3.2:d=0.4"),
    ("pool_jump.mp3", 30.10, 3.60, 1.8, 0.35, "afade=t=out:st=1.4:d=0.4"),
]
inp = ["-i", OUT + ".video.mp4", "-i", VO]
for fn, *_ in CUES: inp += ["-i", S(fn)]
fc = "[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay=0|0,volume=1.0,asplit=2[vo][vosc];"
for k, (fn, st, off, dur, vol, flt) in enumerate(CUES):
    ms = int(st * 1000)
    fc += (f"[{k+2}:a]aresample=48000,aformat=channel_layouts=stereo,atrim={off}:{off+dur},asetpts=PTS-STARTPTS,"
           f"{flt + ',' if flt else ''}volume={vol},adelay={ms}|{ms}[c{k}];")
fc += "".join(f"[c{k}]" for k in range(len(CUES))) + f"amix=inputs={len(CUES)}:normalize=0[fx];"
fc += "[fx][vosc]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=250[fxd];"
# "like you": the world drops out
fc += "[fxd]volume='if(between(t,32.0,32.95),0.08,1)':eval=frame[fxe];"
fc += f"[fxe][vo]amix=inputs=2:normalize=0,apad,atrim=0:{TOTAL},afade=t=out:st={TOTAL-0.4}:d=0.4,loudnorm=I=-13:TP=-1.0:LRA=11[aout]"
subprocess.run(["ffmpeg", "-v", "error", "-y", *inp, "-filter_complex", fc, "-map", "0:v", "-map", "[aout]",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", str(TOTAL), OUT], check=True)
os.remove(OUT + ".video.mp4")
print("wrote", OUT)
