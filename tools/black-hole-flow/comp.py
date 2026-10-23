"""One continuous fall through four black holes, built from Google Flow clips.

Each segment ends by diving into its black hole (accelerating zoom into the tracked shadow,
radial motion blur) until the frame is black, and the next segment starts inside its own
black hole and pulls out. A 3D dust/ember field streams out of the current hole toward the
camera through the whole reel (true perspective, depth of field, streaks during dives),
so the depth and motion carry across every join.

usage: comp.py CLIPDIR TRACKDIR [notext] | ffmpeg -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 24 -i - ...
Also writes dives.json (dive and emerge times) next to TRACKDIR for the sound mix.
"""
import json
import subprocess
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

CLIPS, TRACK = sys.argv[1], sys.argv[2]
TEXT = len(sys.argv) < 4
W, H, FPS = 1080, 1920, 24
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
HOOK = ["WHAT'S ON", "THE OTHER SIDE?"]

# clip, source start (s), duration (s), emerge length (s), dive length (s), emerge starts at this fraction
SEGS = [
    ("2c9d849a", 0.4, 2.9, 0.55, 0.95, 0.55),   # blade (hook); frame 0 is already half out of the dark
    ("e500d365", 0.2, 3.0, 0.85, 0.95, 0.0),    # galaxy reveal
    ("5b667070", 0.0, 2.9, 0.85, 0.95, 0.0),    # the ring
    ("419ba376", 3.8, 3.2, 0.85, 1.05, 0.0),    # vortex with debris, dives back into the blade
]


def load(key, start, dur):
    path = subprocess.check_output(f"ls {CLIPS}/{key}*/*.mp4", shell=True, text=True).strip()
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-ss", str(start), "-i", path, "-t", str(dur + 0.2),
                          "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3)


def smoothstep(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def zoom_view(img, z, cx, cy, th):
    """Zoom 1/z toward the hole (cx, cy), drifting it toward frame centre, rolled by th radians."""
    k = (1.0 / z) ** 1.25
    ccx = cx + (W / 2 - cx) * k
    ccy = cy + (H / 2 - cy) * k
    hw, hh = W / (2 * z), H / (2 * z)
    # keep the (rotated) window inside the frame
    ex = abs(np.cos(th)) * hw + abs(np.sin(th)) * hh
    ey = abs(np.sin(th)) * hw + abs(np.cos(th)) * hh
    ccx = min(max(ccx, ex), W - ex) if ex < W / 2 else W / 2
    ccy = min(max(ccy, ey), H - ey) if ey < H / 2 else H / 2
    c, s = np.cos(th), np.sin(th)
    # output pixel p -> source = centre + R(th) (p - frame centre) / z
    a, b = c / z, -s / z
    d, e = s / z, c / z
    data = (a, b, ccx - a * W / 2 - b * H / 2, d, e, ccy - d * W / 2 - e * H / 2)
    v = img.transform((W, H), Image.AFFINE, data, Image.BICUBIC)
    # where the hole lands on screen (inverse map)
    qx, qy = cx - ccx, cy - ccy
    return v, (W / 2 + (c * qx + s * qy) * z, H / 2 + (-s * qx + c * qy) * z)


# ---------- 3D dust / ember field ----------
rng = np.random.default_rng(5)
N = 1400
px = rng.uniform(-1.6, 1.6, N)
py = rng.uniform(-2.8, 2.8, N)
pz = rng.uniform(0.15, 7.0, N)
pb = 1.4 * rng.uniform(0.3, 1.0, N) ** 2
ember = rng.uniform(0, 1, N) < 0.18
pcol = np.where(ember[:, None], np.array([[255, 150, 60]]), np.array([[255, 236, 205]]))
prev = None


def particles(vx, vy, speed, dt, streak):
    """Advance and draw the field; vanishing point = hole on screen. Returns three depth layers."""
    global pz, prev
    pz = pz - speed * dt
    re = pz < 0.12
    pz[re] = 7.0
    px[re] = rng.uniform(-1.6, 1.6, re.sum())
    py[re] = rng.uniform(-2.8, 2.8, re.sum())
    f = 620.0
    sx = vx + px / pz * f
    sy = vy + py / pz * f
    fade = np.clip((7.0 - pz) / 2.0, 0, 1) * np.clip((pz - 0.12) / 0.15, 0, 1)
    layers = [Image.new("RGB", (W, H)) for _ in range(3)]
    draws = [ImageDraw.Draw(l) for l in layers]
    for i in range(N):
        if not (-200 < sx[i] < W + 200 and -200 < sy[i] < H + 200):
            continue
        z = pz[i]
        b = pb[i] * fade[i] * (1.6 if ember[i] else 1.0)
        size = max(0.7, 2.2 / z)
        layer = 2 if z < 0.7 else (1 if z < 2.0 else 0)
        if layer == 2:
            b *= 0.7                          # big out-of-focus bokeh stays soft
        c = tuple(int(min(255, v * b)) for v in pcol[i])
        d = draws[layer]
        if streak > 0.02 and prev is not None and re[i] == 0:
            x0, y0 = prev[0][i], prev[1][i]
            d.line((x0, y0, sx[i], sy[i]), fill=c, width=max(1, int(size * 0.8)))
        else:
            d.ellipse((sx[i] - size, sy[i] - size, sx[i] + size, sy[i] + size), fill=c)
    prev = (sx.copy(), sy.copy())
    return layers


def hook_layer(alpha, n):
    """Two centred lines, typed on character by character across both."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if alpha <= 0 or n < 1:
        return lay
    f = ImageFont.truetype(FONT, 84)
    d = ImageDraw.Draw(lay)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    sp = 4.0
    left = n
    for li, line in enumerate(HOOK):
        widths = [d.textlength(c, font=f) for c in line]
        x = (W - (sum(widths) + sp * (len(line) - 1))) / 2
        y = 1400 + li * 104
        for k, c in enumerate(line[:max(left, 0)]):
            ds.text((x, y), c, font=f, fill=(0, 0, 0, int(220 * alpha)))
            d.text((x, y), c, font=f, fill=(246, 236, 214, int(255 * alpha)))
            x += widths[k] + sp
        left -= len(line)
    return Image.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), lay)


yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
vign = 1 - 0.28 * np.clip((np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2) - 0.25) / 0.45, 0, 1) ** 1.5
grng = np.random.default_rng(9)
out = sys.stdout.buffer
dives, emerges = [], []
tglob = 0.0
for key, s0, dur, em, dv, em0 in SEGS:
    frames = load(key, s0, dur)
    tr = json.load(open(f"{TRACK}/{key}.json"))
    nf = int(round(dur * FPS))
    r_end = None
    lnz_prev = None
    emerges.append(tglob)
    dives.append(tglob + dur - dv)
    for j in range(nf):
        tau = j / FPS
        si = min(int(round((s0 + tau) * FPS)), len(tr) - 1)
        cx, cy, r = tr[si]
        cx, cy, rr = cx * W, cy * H, r * W
        zfull = 1.15 * np.hypot(W / 2, H / 2) / max(rr, 20)        # zoom at which the shadow fills the frame
        lnz = 0.0
        if tau < em:                                              # emerge: start inside the hole, pull out
            u = em0 + (1 - em0) * tau / em
            lnz += np.log(zfull) * (1 - smoothstep(u)) ** 1.6
        if tau > dur - dv:                                        # dive: accelerate into the hole
            u = (tau - (dur - dv)) / dv
            lnz += np.log(zfull) * u ** 2.4
        lnz += 0.07 * tau                                         # constant gentle push: the camera never stops
        th = 0.025 * tau
        if tau < em:
            th -= 0.9 * (1 - smoothstep(em0 + (1 - em0) * tau / em)) ** 1.6
        if tau > dur - dv:
            th += 0.9 * ((tau - (dur - dv)) / dv) ** 2.4          # the spin builds as we fall in
        lnz = max(lnz, float(np.log(abs(np.cos(th)) + (H / W) * abs(np.sin(th)))) + 0.01)   # no empty corners when rolled
        vel = 0.0 if lnz_prev is None else (lnz - lnz_prev) * FPS
        lnz_prev = lnz
        img = Image.fromarray(frames[min(j, len(frames) - 1)])
        # radial motion blur: average zoom samples across half a frame of travel
        span = abs(vel) / FPS * 0.6
        ns = int(min(14, max(1, span / 0.006)))
        acc = None
        for k in range(ns):
            o = (k / max(ns - 1, 1) - 0.5) * span if ns > 1 else 0.0
            v, (hx, hy) = zoom_view(img, float(np.exp(lnz + o)), cx, cy, th)
            a = np.asarray(v, np.float32)
            acc = a if acc is None else acc + a
        base = acc / ns
        # dust field streams out of the hole; faster during dives and emerges
        speed = 0.6 + 1.4 * abs(vel)
        layers = particles(hx, hy, speed, 1 / FPS, abs(vel))
        far = np.asarray(layers[0], np.float32)
        mid = np.asarray(layers[1].filter(ImageFilter.GaussianBlur(1.6)), np.float32)
        near = np.asarray(layers[2].filter(ImageFilter.GaussianBlur(9)), np.float32)
        img = base + (far * 0.8 + mid + near * 1.6) * (1 - 0.6 * smoothstep((lnz - 1.5) / 1.5))
        img = img * vign[..., None] * 1.0
        img = img + grng.standard_normal((H, W, 1)).astype(np.float32) * 3.0
        frame = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
        t = tglob + tau
        if TEXT and t < 2.9:
            n = int(sum(len(x) for x in HOOK) * smoothstep((t - 0.25) / 0.9) + 0.999)
            a = 1 - smoothstep((t - 2.1) / 0.5)
            frame = Image.alpha_composite(frame.convert("RGBA"), hook_layer(a, n)).convert("RGB")
        out.write(frame.tobytes())
    tglob += nf / FPS
json.dump({"dur": tglob, "dives": dives, "emerges": emerges}, open(f"{TRACK}/dives.json", "w"))
