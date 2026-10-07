#!/usr/bin/env python3
"""Designed graphics for the Slow Light aliens long-form (1920x1080, 30 fps, eerie palette).

Usage: gfx_aliens.py OUTDIR [name ...]   (no names = render all)
Each graphic is a short MP4 written to OUTDIR/<name>.mp4. Rendered frame by frame with PIL, piped to ffmpeg.
"""
import math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1920, 1080, 30
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(ROOT, "edit_v7", "fonts")
BG = (6, 9, 13)
TEAL = (110, 190, 185)
GREEN = (90, 255, 140)
DIM = (120, 135, 145)
IVORY = (226, 230, 228)
RED = (205, 40, 40)
AMBER = (232, 176, 84)


def font(name, size, weight=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if weight:
        try:
            f.set_variation_by_axes([weight])
        except Exception:
            pass
    return f


MONO = None
for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf"):
    if os.path.exists(p):
        MONO = p
        break


def mono(size):
    return ImageFont.truetype(MONO, size) if MONO else font("Montserrat.ttf", size, 500)


def grain(img, amt=10, seed=0):
    a = np.asarray(img).astype(np.int16)
    rng = np.random.default_rng(seed)
    a = a + rng.integers(-amt, amt + 1, size=a.shape[:2])[..., None]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def vignette(img):
    y, x = np.ogrid[:H, :W]
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    m = np.clip(1 - 0.45 * d ** 2, 0.35, 1)[..., None]
    return Image.fromarray((np.asarray(img).astype(np.float32) * m).astype(np.uint8))


def ease(t):
    t = min(max(t, 0), 1)
    return t * t * (3 - 2 * t)


def write(name, frames_fn, seconds, outdir):
    n = int(seconds * FPS)
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                          os.path.join(outdir, name + ".mp4")], stdin=subprocess.PIPE)
    for i in range(n):
        img = frames_fn(i / FPS, i)
        p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close()
    p.wait()
    print(name, seconds, "s")


def centered(d, y, text, f, fill):
    w = d.textlength(text, font=f)
    d.text(((W - w) / 2, y), text, font=f, fill=fill)


# ---------- G01: oscilloscope, static then the 72-second spike ----------
def g01(t, i):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for gx in range(0, W, 120):
        d.line([(gx, 140), (gx, H - 140)], fill=(16, 32, 30))
    for gy in range(140, H - 139, 100):
        d.line([(0, gy), (W, gy)], fill=(16, 32, 30))
    rng = np.random.default_rng(i)
    pts = []
    mid = H / 2
    spike = ease((t - 1.2) / 1.6)
    for x in range(0, W, 4):
        n = rng.normal(0, 6 + 4 * (1 - spike))
        bump = spike * 300 * math.exp(-((x - W * 0.55) / 70) ** 2)
        pts.append((x, mid + n - bump))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(pts, fill=GREEN, width=7)
    glow = glow.filter(ImageFilter.GaussianBlur(9))
    img = Image.fromarray(np.clip(np.asarray(img).astype(np.int16) + np.asarray(glow).astype(np.int16) // 2, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.line(pts, fill=GREEN, width=2)
    f = mono(26)
    d.text((60, 70), "BIG EAR  ·  15 AUG 1977  ·  22:16 EDT", font=f, fill=DIM)
    if t > 1.2:
        secs = min(72, int((t - 1.2) / 2.2 * 72))
        d.text((W - 360, 70), f"SIGNAL  {secs:02d} s", font=f, fill=GREEN)
    return vignette(grain(img, 12, i))


# ---------- G02: the printout, 6EQUJ5, red circle, "Wow!" ----------
PAPER = (214, 210, 196)
COLS = ["1 1   1", "  1 1  ", "1    1 ", " 6EQUJ5", "  1   1", "1  1   ", " 1   1 ", "  1  1 ", "1      ", "   1 1 "]


def g02(t, i):
    rng = random.Random(7)
    img = Image.new("RGB", (W, H), (20, 20, 18))
    paper = Image.new("RGB", (1100, 1400), PAPER)
    pd = ImageDraw.Draw(paper)
    for y in range(0, 1400, 40):
        pd.rectangle([0, y, 1100, y + 19], fill=(205, 214, 200))
    for y in range(20, 1400, 60):
        pd.ellipse([18, y, 34, y + 16], fill=(170, 166, 154))
        pd.ellipse([1066, y, 1082, y + 16], fill=(170, 166, 154))
    f = mono(34)
    rows = 30
    for r in range(rows):
        line = list("".join(rng.choice("   1  1 12 ") for _ in range(26)))
        if 10 <= r <= 19:  # keep the famous column and the circle clear
            for c in range(19, 26):
                line[c] = " "
        pd.text((90, 20 + r * 44), "".join(line), font=f, fill=(60, 62, 70))
    # the famous column, typed out one character at a time
    seq = "6EQUJ5"
    shown = min(6, int(max(0, t - 0.6) / 0.45))
    for k in range(shown):
        pd.text((560, 20 + (12 + k) * 44), seq[k], font=font("Montserrat.ttf", 40, 700), fill=(20, 20, 26))
    # red circle drawn around it
    prog = ease((t - 3.6) / 1.4)
    if prog > 0:
        pd.arc([520, 20 + 11 * 44, 620, 20 + 18.4 * 44], start=-90, end=-90 + 360 * prog, fill=RED, width=6)
    # handwritten Wow!
    if t > 5.4:
        a = ease((t - 5.4) / 0.6)
        wf = font("Cinzel.ttf", 92, 700)
        col = tuple(int(PAPER[c] * (1 - a) + RED[c] * a) for c in range(3))
        pd.text((660, 20 + 13.2 * 44), "Wow!", font=wf, fill=col)
    # slow push in on the paper
    z = 1.0 + 0.18 * ease(t / 9)
    pw, ph = int(1100 * z), int(1400 * z)
    paper = paper.resize((pw, ph), Image.LANCZOS).rotate(-2.5, expand=False, fillcolor=(20, 20, 18))
    img.paste(paper, ((W - pw) // 2, (H - ph) // 2 + int(80 * z)))
    return vignette(grain(img, 9, i))


# ---------- G03: radio spectrum with the hydrogen line ----------
def g03(t, i):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(i)
    base = H * 0.66
    x0, x1 = 160, W - 160
    d.line([(x0, base + 40), (x1, base + 40)], fill=(40, 60, 62), width=2)
    pts = []
    peak = ease((t - 1.0) / 2.0)
    for x in range(x0, x1, 3):
        f = (x - x0) / (x1 - x0)
        noise = abs(rng.normal(0, 14))
        line = peak * 210 * math.exp(-((f - 0.5) / 0.012) ** 2)
        pts.append((x, base - noise - line))
    d.line(pts, fill=TEAL, width=2)
    fl = mono(26)
    for k, lab in enumerate(["1 GHz", "1.2", "1.42", "1.6", "1.8 GHz"]):
        x = x0 + (x1 - x0) * k / 4
        d.text((x - 30, base + 56), lab, font=fl, fill=DIM)
    if peak > 0.2:
        a = int(255 * ease((t - 2.2) / 1.0))
        tf = font("Montserrat.ttf", 44, 600)
        txt = "1420 MHz  ·  THE HYDROGEN LINE"
        w = d.textlength(txt, font=tf)
        d.text(((W - w) / 2, base - 330), txt, font=tf, fill=(a * TEAL[0] // 255, a * TEAL[1] // 255, a * TEAL[2] // 255))
    return vignette(grain(img, 10, i))


# ---------- G05: timeline with the Proxima stamp ----------
EVENTS = [("1960", "PROJECT OZMA"), ("1977", "THE WOW! SIGNAL"), ("2015", "BREAKTHROUGH LISTEN"), ("2019", "A SIGNAL FROM PROXIMA?")]


def g05(t, i):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    y = H / 2
    x0, x1 = 200, W - 200
    prog = ease(t / 3.5)
    d.line([(x0, y), (x0 + (x1 - x0) * prog, y)], fill=(70, 100, 102), width=3)
    fy, fl = font("Cinzel.ttf", 54, 700), font("Montserrat.ttf", 26, 600)
    for k, (yr, lab) in enumerate(EVENTS):
        x = x0 + (x1 - x0) * k / 3
        a = ease((t - k * 0.8) / 0.6)
        if a <= 0:
            continue
        c = tuple(int(v * a) for v in IVORY)
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=c)
        w = d.textlength(yr, font=fy)
        d.text((x - w / 2, y - 110), yr, font=fy, fill=c)
        w = d.textlength(lab, font=fl)
        d.text((x - w / 2, y + 40), lab, font=fl, fill=tuple(int(v * a) for v in DIM))
    if t > 4.6:
        a = ease((t - 4.6) / 0.25)
        st = Image.new("RGBA", (620, 120), (0, 0, 0, 0))
        sd = ImageDraw.Draw(st)
        sd.rectangle([4, 4, 616, 116], outline=RED + (int(230 * a),), width=6)
        sf = font("Montserrat.ttf", 48, 800)
        w = sd.textlength("LOCAL INTERFERENCE", font=sf)
        sd.text(((620 - w) / 2, 30), "LOCAL INTERFERENCE", font=sf, fill=RED + (int(230 * a),))
        st = st.rotate(-8, expand=True, resample=Image.BICUBIC)
        sc = 1.4 - 0.4 * a
        st = st.resize((int(st.width * sc), int(st.height * sc)), Image.LANCZOS)
        x = int(min(x0 + (x1 - x0) - st.width / 2, W - st.width - 70))
        img.paste(st, (x, int(y + 120)), st)
    return vignette(grain(img, 10, i))


# ---------- G06: TECHNOSIGNATURES ----------
def g06(t, i):
    img = Image.new("RGB", (W, H), (3, 5, 8))
    d = ImageDraw.Draw(img)
    word = "TECHNOSIGNATURES"
    f = font("Cinzel.ttf", 108, 700)
    total = d.textlength(word, font=f) + 14 * (len(word) - 1)
    x = (W - total) / 2
    rng = random.Random(3)
    for k, ch in enumerate(word):
        a = ease((t - 0.25 - k * 0.07) / 0.5)
        if rng.random() < 0.15 and 0 < a < 1:
            a *= 0.3
        c = tuple(int(v * a) for v in TEAL)
        d.text((x, H / 2 - 70), ch, font=f, fill=c)
        x += d.textlength(ch, font=f) + 14
    return vignette(grain(img, 8, i))


# ---------- G08: 144 reports, 1 explained ----------
GRID = [(c, r) for r in range(9) for c in range(16)]


def g08(t, i, phase="a"):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    sx, sy = 104, 76
    ox, oy = (W - 15 * sx) / 2, 250
    rng = random.Random(11)
    order = list(range(144))
    rng.shuffle(order)
    explained_n = 1 if phase == "a" else int(1 + 120 * ease(t / 6.5))
    explained = set(order[:explained_n])
    cats = ["balloons", "drones", "birds", "satellites", "sensor artefacts"]
    for k, (c, r) in enumerate(GRID):
        a = ease((t - k * 0.008) / 0.4) if phase == "a" else 1
        x, y = ox + c * sx, oy + r * sy
        if k in explained:
            d.ellipse([x - 13, y - 13, x + 13, y + 13], outline=(70, 80, 84), width=2)
        else:
            col = tuple(int(v * a) for v in (150, 210, 205))
            d.ellipse([x - 13, y - 13, x + 13, y + 13], fill=col)
    hf = font("Montserrat.ttf", 40, 600)
    if phase == "a":
        centered(d, 110, "144 REPORTS", hf, IVORY)
        if t > 9.6:  # lands on the narration's "only one"
            k = order[0]
            c, r = GRID[k]
            x, y = ox + c * sx, oy + r * sy
            lf = font("Montserrat.ttf", 30, 600)
            d.line([(x, y + 16), (x, y + 70)], fill=DIM, width=2)
            d.text((x - 60, y + 74), "BALLOON", font=lf, fill=DIM)
            centered(d, H - 130, "1 EXPLAINED", hf, AMBER)
    else:
        centered(d, 110, "LATER REVIEWS  ·  MANY EXPLAINED", hf, IVORY)
        centered(d, H - 130, "  ·  ".join(c.upper() for c in cats), font("Montserrat.ttf", 30, 600), DIM)
    return vignette(grain(img, 10, i))


# ---------- G10: a hot tub against the oceans ----------
def g10(t, i):
    img = Image.new("RGB", (W, H), (3, 6, 10))
    d = ImageDraw.Draw(img)
    # the oceans as a huge disc that keeps growing as the camera pulls back
    z = 1 - 0.75 * ease(t / 7)
    R = int(2600 * z)
    cx, cy = W // 2, H // 2 + 40
    d.ellipse([cx - R, cy - R, cx + R, cy + R], fill=(10, 34, 52))
    # the hot tub: a dot that shrinks to almost nothing
    r = max(2, int(36 * z * z))
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=AMBER)
    f = font("Montserrat.ttf", 40, 600)
    if t > 1.0:
        centered(d, 90, "EVERYTHING WE'VE SEARCHED: ~7,700 LITRES", f, AMBER)
    if t > 3.0:
        centered(d, H - 150, "EARTH'S OCEANS: 1.335 BILLION TRILLION LITRES", f, (120, 170, 200))
    return vignette(grain(img, 9, i))


# ---------- title and end cards ----------
def title(t, i):
    img = Image.new("RGB", (W, H), (2, 3, 5))
    d = ImageDraw.Draw(img)
    a = ease(t / 1.2) * (1 - ease((t - 4.2) / 0.8))
    k = font("Montserrat.ttf", 30, 700)
    centered(d, 380, "SLOW LIGHT  ·  THE UNKNOWN", k, tuple(int(v * a) for v in TEAL))
    f = font("Cinzel.ttf", 76, 700)
    centered(d, 460, "WHAT IF WE'RE LOOKING FOR ALIENS", f, tuple(int(v * a) for v in IVORY))
    centered(d, 560, "IN THE WRONG PLACE?", f, tuple(int(v * a) for v in IVORY))
    return grain(img, 7, i)


def endcard(t, i):
    img = Image.new("RGB", (W, H), (0, 0, 0))
    d = ImageDraw.Draw(img)
    a = ease((t - 0.8) / 1.5)
    centered(d, 470, "SLOW LIGHT", font("Cinzel.ttf", 84, 700), tuple(int(v * a) for v in IVORY))
    centered(d, 590, "stories worth slowing down for", font("Montserrat.ttf", 34, 500), tuple(int(v * a) for v in DIM))
    return img


ALL = {
    "G01_scope": (g01, 4.0), "G02_printout": (g02, 11.0), "G03_spectrum": (g03, 12.5), "G05_timeline": (g05, 9.5),
    "G06_techno": (g06, 4.5), "G08a_grid": (lambda t, i: g08(t, i, "a"), 13.5), "G08b_grid": (lambda t, i: g08(t, i, "b"), 11.0),
    "G10_scale": (g10, 8.5), "T_title": (title, 5.0), "T_end": (endcard, 6.0),
}

if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name in (sys.argv[2:] or ALL):
        fn, sec = ALL[name]
        write(name, fn, sec, out)
