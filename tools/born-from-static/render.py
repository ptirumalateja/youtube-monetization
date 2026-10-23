"""Render Born From Static: static -> 50 denoising steps -> painting -> static.

    python3 render.py PAINTING.npy OUT.mp4 [--notext]

Frames are piped straight into ffmpeg (silent video; sound.py makes the audio).
"""
import sys
import numpy as np
from multiprocessing import Pool
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import timeline as tl

W, H = 1080, 1920
NW, NH = W // 2, H // 2            # static is drawn in 2x2 blocks (reads as TV static, compresses better)
CREAM = (246, 238, 222)
RED = (214, 62, 48)
TEAL = (90, 230, 200)
F_CAP = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
F_HUD = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf"
F_HUD_R = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"

PAINT = None
NOTEXT = "--notext" in sys.argv


def ease(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def zoom_at(t):
    if t < tl.FORWARD[0]:
        z = 1.0 + 0.075 * ease(t / tl.FORWARD[0])
    else:
        z = 1.075 - 0.075 * ease((t - tl.FORWARD[0]) / (tl.DUR - tl.FORWARD[0]))
    if t >= tl.REVEAL:
        z += 0.02 * np.exp(-(t - tl.REVEAL) / 0.35)
    return z


def noise_seed(t):
    """Fresh static every frame, except during the steps: one sample per step."""
    f = int(round(t * tl.FPS))
    if tl.STEP_START <= t < tl.FORWARD[0]:
        return 100000 + tl.step_at(t)
    return f


def base_frame(t):
    z = zoom_at(t)
    cw, ch = W / z, H / z
    x0, y0 = (W - cw) / 2, (H - ch) / 2 - 40 * (z - 1)   # drift slightly toward the planet
    img = PAINT.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    # coarse first: early steps only know the big shapes (diffusion settles low
    # frequencies before fine detail), so the clean estimate is blurred early on
    k = tl.step_at(t) if t < tl.FORWARD[0] else tl.STEPS
    blur = 36 * max(0.0, 1 - k / 38) ** 2
    if blur > 0.5:
        img = img.filter(ImageFilter.GaussianBlur(blur))
    x = np.asarray(img, np.float32) / 255.0 * 2 - 1

    s = tl.signal_at(t)
    n = np.sqrt(max(0.0, 1 - s * s))
    if n > 1e-4:
        r = np.random.default_rng(noise_seed(t))
        eps = r.standard_normal((NH, NW, 3)).astype(np.float32)
        mono = r.standard_normal((NH, NW, 1)).astype(np.float32)
        eps = 0.65 * eps + 0.76 * mono          # part colour confetti, part TV static (unit variance)
        eps = eps.repeat(2, 0).repeat(2, 1)
        x = s * x + n * eps
    out = (x + 1) / 2

    # held breath: dim before the reveal; flash on the hit
    if tl.BREATH[0] <= t < tl.REVEAL:
        out *= 1 - 0.18 * ease((t - tl.BREATH[0]) / (tl.REVEAL - tl.BREATH[0]))
    if tl.REVEAL <= t < tl.REVEAL + 0.2:
        out = out + 0.13 * (1 - (t - tl.REVEAL) / 0.2)
    return np.clip(out, 0, 1)


# ---- text ---------------------------------------------------------------------
CAPTIONS = [
    # t0, t1, lines, size, type speed (chars/s)
    (0.0, 2.05, ["AI ART STARTS", "AS PURE STATIC."], 78, 36),
    (2.2, 5.0, ["IT DOESN'T", "DRAW."], 84, 30),
    (5.1, 8.45, ["IT DELETES NOISE.", "STEP BY STEP."], 74, 32),
    (9.0, 11.45, ["UNTIL ONLY", "A PICTURE IS LEFT."], 72, 40),
    (11.6, 14.65, ["IT LEARNED THIS", "BY BURYING BILLIONS", "OF IMAGES IN NOISE."], 62, 34),
]
CAP_Y = 300            # top of the caption block (sky, above the planet)
PROMPT = ["a lone traveller on a sea cliff,", "a ringed planet rising, painterly"]


def font(path, size, cache={}):
    k = (path, size)
    if k not in cache:
        cache[k] = ImageFont.truetype(path, size)
    return cache[k]


def typed(lines, n):
    out, left = [], n
    for ln in lines:
        out.append(ln[:max(0, left)])
        left -= len(ln)
    return out


def draw_captions(layer, t):
    d = ImageDraw.Draw(layer)
    for t0, t1, lines, size, cps in CAPTIONS:
        if not (t0 <= t < t1):
            continue
        # the hook starts part-typed so frame 0 already reads
        n = int((t - t0) * cps) + (8 if t0 == 0.0 else 1)
        shown = typed(lines, n)
        fade = min(1.0, (t1 - t) / 0.15)
        a = int(255 * fade)
        f = font(F_CAP, size)
        lh = int(size * 1.18)
        # soft dark band behind the block
        band = Image.new("L", (W, H), 0)
        bd = ImageDraw.Draw(band)
        bh = lh * len(lines) + 60
        bd.rounded_rectangle((40, CAP_Y - 30, W - 40, CAP_Y - 30 + bh), 36, fill=int(150 * fade))
        band = band.filter(ImageFilter.GaussianBlur(28))
        layer.paste((0, 0, 0, 255), (0, 0), band)
        for i, ln in enumerate(shown):
            full_w = d.textlength(lines[i], font=f)
            x = (W - full_w) / 2
            y = CAP_Y + i * lh
            d.text((x, y), ln, font=f, fill=CREAM + (a,), stroke_width=6, stroke_fill=(0, 0, 0, a))
            # red block cursor on the line being typed
            if 0 < len(ln) < len(lines[i]):
                cx = x + d.textlength(ln, font=f) + 4
                d.rectangle((cx, y + 6, cx + size * 0.5, y + size), fill=RED + (a,))


HUD_Y = 1452


def draw_hud(layer, t):
    d = ImageDraw.Draw(layer)
    x0, x1, y0, y1 = 56, W - 56, HUD_Y, HUD_Y + 134
    box = Image.new("L", (W, H), 0)
    ImageDraw.Draw(box).rounded_rectangle((x0, y0, x1, y1), 22, fill=175)
    layer.paste((6, 4, 12, 255), (0, 0), box)
    d.rounded_rectangle((x0, y0, x1, y1), 22, outline=(255, 255, 255, 60), width=2)

    fp, fr = font(F_HUD, 30), font(F_HUD_R, 29)
    d.text((x0 + 24, y0 + 14), "PROMPT", font=fp, fill=TEAL + (255,))
    # prompt types in over the first 1.6 s, then stays
    n = 255 if t > 1.8 else int(6 + t * 45)
    shown = typed(PROMPT, n)
    for i, ln in enumerate(shown):
        d.text((x0 + 160, y0 + 14 + i * 36), ln, font=fr, fill=CREAM + (255,))

    yb = y0 + 88
    if t < tl.FORWARD[0]:
        k = tl.step_at(t)
        label = f"STEP {k:02d}/{tl.STEPS}"
        d.text((x0 + 24, yb - 4), label, font=fp, fill=CREAM + (255,))
        frac = k / tl.STEPS
        col = TEAL
    else:
        d.rounded_rectangle((x0 + 18, yb - 6, x0 + 18 + 330, yb + 32), 8, fill=RED + (255,))
        d.text((x0 + 30, yb - 4), "TRAINING: +NOISE", font=fp, fill=(255, 255, 255, 255))
        u = (t - tl.FORWARD[0]) / (tl.DUR - tl.FORWARD[0])
        frac = 1 - min(1, u)
        col = RED
    bx0, bx1 = x0 + 380, x1 - 26
    d.rounded_rectangle((bx0, yb + 4, bx1, yb + 20), 8, fill=(255, 255, 255, 40))
    if frac > 0:
        d.rounded_rectangle((bx0, yb + 4, bx0 + max(16, (bx1 - bx0) * frac), yb + 20), 8, fill=col + (255,))


def frame(fi):
    t = fi / tl.FPS
    rgb = (base_frame(t) * 255 + 0.5).astype(np.uint8)
    if NOTEXT:
        return rgb.tobytes()
    im = Image.fromarray(rgb).convert("RGBA")
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw_captions(layer, t)
    draw_hud(layer, t)
    im = Image.alpha_composite(im, layer)
    return np.asarray(im.convert("RGB")).tobytes()


def init(path):
    global PAINT
    arr = np.load(path)
    PAINT = Image.fromarray((arr * 255 + 0.5).astype(np.uint8))


if __name__ == "__main__":
    src, out = sys.argv[1], sys.argv[2]
    only = [int(a.split("=")[1]) for a in sys.argv if a.startswith("--frame=")]
    if only:
        init(src)
        for fi in only:
            Image.frombytes("RGB", (W, H), frame(fi)).save(out.replace(".png", f"_{fi:04d}.png"))
        sys.exit()
    ff = subprocess.Popen([
        "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
        "-r", str(tl.FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow", "-crf", "12",
        "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    with Pool(4, initializer=init, initargs=(src,)) as p:
        for i, buf in enumerate(p.imap(frame, range(tl.N_FRAMES), chunksize=4)):
            ff.stdin.write(buf)
            if i % 50 == 0:
                print("frame", i, flush=True)
    ff.stdin.close()
    ff.wait()
