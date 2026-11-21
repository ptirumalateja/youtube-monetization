"""Recut of Teja's silent "3 Space Facts" Day 1 reel (29.5 s -> ~16 s).

Payoff-first hook (neutron star + "SOUNDS FAKE"), 3.8 s per fact with zoom-step
cuts every ~0.75 s, flashes + whooshes between facts, 1/3 counter as open loop,
everything shifted up so the cards sit inside the y 300-1440 safe zone, and the
original end card sped up. Beat is code-made; SFX come from tools/sfxlib.

usage: python3 recut.py SRC.mov OUT.mp4
"""
import subprocess, sys, os, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

SRC, OUT = sys.argv[1], sys.argv[2]
W, H, FPS = 1080, 1920, 30
HERE = os.path.dirname(os.path.abspath(__file__))
SFX = os.path.join(HERE, "..", "sfxlib")
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf"

# (out_start, src_start, src_end, speed, shift_up, kind)
SEGS = [
    (0.0, 16.5, 18.0, 1.0, 120, "hook"),
    (1.5, 5.3, 9.1, 1.0, 120, "f1"),
    (5.3, 12.8, 16.6, 1.0, 120, "f2"),
    (9.1, 19.9, 23.7, 1.0, 120, "f3"),
    (12.9, 25.6, 29.35, 1.5, 240, "cta"),
]
TOTAL = 16.0


def read_frames(t0, t1, speed):
    n = int(round((t1 - t0) / speed * FPS))
    vf = f"setpts=PTS/{speed},fps={FPS}" if speed != 1 else f"fps={FPS}"
    p = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t0), "-t", str(t1 - t0), "-i", SRC,
                        "-vf", vf, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True)
    a = np.frombuffer(p.stdout, np.uint8).reshape(-1, H, W, 3)
    return a, n


def shift(fr, s):
    out = np.empty_like(fr)
    out[:H - s] = fr[s:]
    out[H - s:] = fr[H - s:]  # reuse bottom starfield
    if s == 120:  # melt the old "FACT n - SPACE" chip into the background
        box = (300, 0, 780, 190)
        im = Image.fromarray(out)
        reg = im.crop(box)
        bl = reg.resize((24, 10), Image.BILINEAR).resize(reg.size, Image.BICUBIC)
        im.paste(bl, box[:2], FEATHER)
        out = np.asarray(im).copy()
    return out


def zoom(img, z, ay=1060):
    if abs(z - 1) < 1e-3:
        return img
    nw, nh = int(W * z), int(H * z)
    big = img.resize((nw, nh), Image.BICUBIC)
    x0 = int((nw - W) / 2)
    y0 = int(ay * z - ay)
    return big.crop((x0, y0, x0 + W, y0 + H))


def text_layer(lines, y, size, colors=None, stroke=10):
    """Return RGBA full-frame layer with centred lines starting at y."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = ImageFont.truetype(FONT, size)
    cy = y
    for i, ln in enumerate(lines):
        col = (colors or [(255, 255, 255)] * len(lines))[i]
        bw = d.textlength(ln, font=f)
        d.text(((W - bw) / 2, cy), ln, font=f, fill=col + (255,), stroke_width=stroke,
               stroke_fill=(10, 6, 30, 255))
        cy += int(size * 1.08)
    # soft drop shadow
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(14))
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow.putalpha(sh.point(lambda v: int(v * 0.7)))
    return Image.alpha_composite(shadow, lay)


def pill(txt, x, y, size=64):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    f = ImageFont.truetype(FONT, size)
    tw = d.textlength(txt, font=f)
    pad = 28
    d.rounded_rectangle((x, y, x + tw + 2 * pad, y + size + 36), radius=40,
                        fill=(110, 200, 255, 235))
    d.text((x + pad, y + 12), txt, font=f, fill=(12, 8, 40, 255))
    return lay


def pop(layer, t, t_in, dur=0.13):
    """scale 1.3 -> 1 over dur, alpha in; returns layer or None."""
    if t < t_in:
        return None
    k = min(1.0, (t - t_in) / dur)
    s = 1.3 - 0.3 * (1 - (1 - k) ** 3)
    if abs(s - 1) > 1e-3:
        bb = layer.getbbox()
        if bb:
            cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
            nl = layer.resize((int(W * s), int(H * s)), Image.BICUBIC)
            out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            out.paste(nl, (int(cx - cx * s), int(cy - cy * s)))
            layer = out
    if k < 1:
        a = layer.split()[3].point(lambda v: int(v * k))
        layer = layer.copy(); layer.putalpha(a)
    return layer


FEATHER = Image.new("L", (480, 190), 0)
ImageDraw.Draw(FEATHER).rounded_rectangle((40, 20, 440, 150), radius=40, fill=255)
FEATHER = FEATHER.filter(ImageFilter.GaussianBlur(22))

# overlays -------------------------------------------------------------
HOOK1 = text_layer(["THIS SOUNDS", "FAKE."], 320, 150)
HOOK2 = text_layer(["IT'S 100% REAL"], 640, 82, [(120, 220, 255)], stroke=8)
COUNT = {k: pill(f"{i}/3", 56, 300) for i, k in enumerate(["f1", "f2", "f3"], 1)}
REHOOK = text_layer(["THE WEIRDEST ONE"], 400, 84, [(255, 214, 110)], stroke=8)

ZSTEPS = [1.0, 1.06, 1.02, 1.09, 1.04, 1.1]  # zoom step every 0.75 s


def compose(seg, i_local, t_local, base):
    kind = seg[5]
    img = Image.fromarray(base)
    if kind != "cta":
        step = int(t_local / 0.75)
        z = ZSTEPS[step % len(ZSTEPS)] + 0.012 * ((t_local % 0.75) / 0.75)  # tiny push inside step
        if kind == "hook":
            z = [1.12, 1.04, 1.08][min(2, int(t_local / 0.4))] + 0.02 * (t_local % 0.4)
        img = zoom(img, z)
    else:
        z = 1.0 + 0.02 * t_local
        img = zoom(img, z, ay=1000)
    img = img.convert("RGBA")
    layers = []
    if kind == "hook":
        layers += [HOOK1, pop(HOOK2, t_local, 0.4)]
    elif kind in COUNT:
        layers.append(pop(COUNT[kind], t_local, 0.0))
        if kind == "f3" and t_local < 1.2:
            layers.append(pop(REHOOK, t_local, 0.0))
    for l in layers:
        if l is not None:
            img = Image.alpha_composite(img, l)
    arr = np.asarray(img.convert("RGB")).astype(np.float32)
    # white flash on segment start
    if i_local < 4 and kind != "hook":
        a = [0.5, 0.3, 0.12, 0.04][i_local]
        arr = arr * (1 - a) + 255 * a
    return arr.clip(0, 255).astype(np.uint8)


def main():
    tmpv = OUT + ".v.mp4"
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
                            "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", tmpv],
                           stdin=subprocess.PIPE)
    total_frames = int(TOTAL * FPS)
    written = 0
    for si, seg in enumerate(SEGS):
        start = seg[0]
        end = SEGS[si + 1][0] if si + 1 < len(SEGS) else TOTAL
        nout = int(round((end - start) * FPS))
        frames, _ = read_frames(seg[1], seg[2], seg[3])
        for i in range(nout):
            src = frames[min(i, len(frames) - 1)]
            fr = compose(seg, i, i / FPS, shift(src, seg[4]))
            enc.stdin.write(fr.tobytes())
            written += 1
        del frames
    enc.stdin.close(); enc.wait()
    assert written == total_frames, written

    # audio ---------------------------------------------------------------
    sr = 48000
    n = int(TOTAL * sr)
    mix = np.zeros(n, np.float32)
    t = np.arange(int(0.35 * sr)) / sr
    kick = np.sin(2 * np.pi * (45 * t + (110 / 18) * (1 - np.exp(-18 * t)))) * np.exp(-9 * t)
    th = np.arange(int(0.05 * sr)) / sr
    rng = np.random.default_rng(1)
    hat = rng.standard_normal(len(th)) * np.exp(-90 * th)
    hat = np.diff(hat, prepend=0)  # brighten
    bpm_step = 0.5
    bass_notes = [55.0, 55.0, 65.41, 49.0]  # A, A, C, G
    for k in range(int(TOTAL / bpm_step)):
        p = int(k * bpm_step * sr)
        if k * bpm_step >= TOTAL - 0.6:
            break
        seg_k = kick[: n - p]
        mix[p:p + len(seg_k)] += 0.55 * seg_k
        ph = p + int(0.25 * sr)
        if ph < n:
            hh = hat[: n - ph]; mix[ph:ph + len(hh)] += 0.12 * hh
        # sub bass pluck
        f0 = bass_notes[(k // 4) % 4]
        bt = np.arange(int(0.45 * sr)) / sr
        b = (np.sin(2 * np.pi * f0 * bt) + 0.3 * np.sin(2 * np.pi * 2 * f0 * bt)) * np.exp(-5 * bt)
        b = b[: n - p]; mix[p:p + len(b)] += 0.22 * b
    # soft pad
    pt = np.arange(n) / sr
    pad = sum(np.sin(2 * np.pi * f * pt) for f in (220, 261.63, 329.63)) / 3
    env = np.minimum(1, pt / 0.2) * np.minimum(1, (TOTAL - pt) / 0.8)
    mix += 0.05 * pad * env

    def load(name, gain, at, maxdur=None):
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SFX, name), "-ac", "1",
                            "-ar", str(sr), "-f", "f32le", "-"], capture_output=True)
        a = np.frombuffer(p.stdout, np.float32)
        if maxdur:
            a = a[: int(maxdur * sr)].copy()
            fade = int(0.15 * sr); a[-fade:] *= np.linspace(1, 0, fade)
        a = a / (np.abs(a).max() + 1e-9)
        s = int(at * sr); a = a[: n - s]
        mix[s:s + len(a)] += gain * a

    load("722633__chakong__cinematic-braaam.wav", 0.55, 0.0, 1.5)
    for at in (1.5, 5.3, 9.1, 12.9):
        load("238375__stewdio2003__cp_subby_whoosh.aiff", 0.35, at - 0.18, 0.6)
    mix /= np.abs(mix).max() / 0.89
    wav = OUT + ".a.wav"
    import wave
    with wave.open(wav, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((mix * 32767).astype(np.int16).tobytes())
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmpv, "-i", wav, "-af",
                    "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-ar", "48000", "-shortest", "-movflags", "+faststart", OUT], check=True)
    os.remove(tmpv); os.remove(wav)


if __name__ == "__main__":
    main()
