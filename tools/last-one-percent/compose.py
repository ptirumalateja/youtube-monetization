"""Last 1%: info layer + final encode.

python3 compose.py frames_dir timing.json mix.wav|- out.mp4 [crf]
Draws the hook, the battery icon over his head, the draining counter (only goes down), the CHARGING chip
and the end line over the rendered 3D frames with PIL, then pipes them to ffmpeg with the mix.
Pass '-' instead of a wav for a silent, music-ready copy.
"""
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

frames, timing_f, wav, out = sys.argv[1:5]
crf = sys.argv[5] if len(sys.argv) > 5 else '18'
T = json.load(open(timing_f))
PROJ = T['proj']
FPS, W, H = 30, 1080, 1920
NF = len(PROJ)
T_PLUG, T_SW = T['T_PLUG'], T['T_SW']
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
SMALL = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
CREAM, GOLD, TEAL, RED, INK = (244, 236, 220), (255, 200, 120), (150, 214, 208), (214, 62, 48), (6, 9, 16)
F = lambda s, p=MONO: ImageFont.truetype(p, s)
f_hook, f_end, f_num, f_chip, f_small = F(84), F(66), F(96), F(40), F(28, SMALL)


def sstep(a, b, x):
    u = min(1, max(0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def typed(s, t, t0, dur):
    n = int(round(len(s) * (t - t0) / dur))
    return s[:max(1, min(len(s), n))] if t >= t0 else ''   # never a negative slice (playbook 8)


def text_c(d, y, s, font, fill, alpha, stroke=7, cx=W / 2):
    if not s or alpha <= 0.01:
        return
    w = d.textlength(s, font=font)
    d.text((cx - w / 2, y), s, font=font, fill=fill + (int(255 * alpha),), stroke_width=stroke, stroke_fill=INK + (int(235 * alpha),))


def bolt(d, cx, cy, s, fill):
    pts = [(0.10, -0.50), (-0.25, 0.05), (0.0, 0.05), (-0.10, 0.50), (0.25, -0.08), (0.0, -0.08)]
    d.polygon([(cx + x * s, cy + y * s) for x, y in pts], fill=fill)


def battery(d, cx, cy, w, frac, col, a, outline=CREAM):
    h = w * 0.48
    x0, y0 = cx - w / 2, cy - h / 2
    lw = max(3, int(w * 0.07))
    d.rounded_rectangle([x0 - 2, y0 - 2, x0 + w + 2, y0 + h + 2], radius=int(h * 0.22), outline=INK + (int(200 * a),), width=lw + 4)
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=int(h * 0.2), outline=outline + (int(255 * a),), width=lw)
    d.rectangle([x0 + w + 2, cy - h * 0.2, x0 + w + lw + 3, cy + h * 0.2], fill=outline + (int(255 * a),))
    pad = lw + 3
    fw = max(lw, (w - 2 * pad) * frac)
    d.rectangle([x0 + pad, y0 + pad, x0 + pad + fw, y0 + h - pad], fill=col + (int(255 * a),))


last_pct = 9.0
cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if wav != '-':
    cmd += ['-i', wav]
cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'film']
if wav != '-':
    cmd += ['-af', 'alimiter=limit=0.84:attack=2:release=80:level=disabled', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest']
cmd += ['-movflags', '+faststart', out]
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in range(NF):
    t = f / FPS
    base = Image.open(f'{frames}/f{f:04d}.jpg').convert('RGB')
    if base.size != (W, H):
        base = base.resize((W, H), Image.LANCZOS)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    pr = PROJ[f]

    # hook: typed by 0.6 s
    a = 1 - sstep(2.7, 3.1, t)
    s1 = typed('1% LEFT.', t, 0.0, 0.6)
    if s1 and a > 0.01:
        w_all = d.textlength('1% LEFT.', font=f_hook)
        x = (W - w_all) / 2
        red_part, rest = s1[:2], s1[2:]
        d.text((x, 230), red_part, font=f_hook, fill=(255, 90, 72, int(255 * a)), stroke_width=8, stroke_fill=INK + (int(235 * a),))
        d.text((x + d.textlength('1%', font=f_hook), 230), rest, font=f_hook, fill=CREAM + (int(255 * a),), stroke_width=8, stroke_fill=INK + (int(235 * a),))

    if pr is not None:
        # battery icon above his head (his battery, readable at any angle)
        blink = 1.0 if t >= T_PLUG else (0.35 if (t * 2.6) % 1 > 0.7 and pr['pct'] < 0.5 else 1.0)
        sc = min(1.35, max(0.55, 3.4 / pr['d']))
        aw = 96 * sc
        hx, hy = pr['x'], pr['y'] - 34 * sc
        on = 0 <= hx <= W and 120 <= hy <= H * 0.8
        a_icon = (1 - sstep(T_SW - 0.6, T_SW - 0.2, t)) * (1 if on else 0)
        if a_icon > 0.01:
            if t < T_PLUG:
                battery(d, hx, hy, aw, 0.04 + 0.04 * pr['pct'], RED, a_icon * blink)
            else:
                battery(d, hx, hy, aw, 0.08 + 0.92 * pr['charge'], TEAL, a_icon)
                bolt(d, hx, hy, aw * 0.42, INK + (int(230 * a_icon),))

        # counter, lower third (above the bottom 18% safe zone): only goes down until the plug
        a = sstep(0.0, 0.05, t) * (1 - sstep(T_SW - 0.5, T_SW - 0.1, t))
        y0 = 1400
        if t < T_PLUG:
            p = pr['pct']
            assert p <= last_pct + 1e-9, (f, p, last_pct)
            last_pct = p
            num = f'{p:.2f}%'
            nw = d.textlength(num, font=f_num)
            col = (255, 90, 72) if p < 0.3 else CREAM
            d.text(((W - nw) / 2, y0), num, font=f_num, fill=col + (int(255 * a * blink),), stroke_width=8, stroke_fill=INK + (int(235 * a),))
            text_c(d, y0 + 112, 'BATTERY', f_small, CREAM, a * 0.9, stroke=5)
        else:
            pulse = 1 + 0.25 * max(0.0, 1 - (t - T_PLUG) / 0.25)
            fc = F(int(46 * pulse))
            lab = 'CHARGING'
            lw = d.textlength(lab, font=fc)
            cw = lw + 110
            x0 = (W - cw) / 2
            d.rounded_rectangle([x0, y0 + 20, x0 + cw, y0 + 20 + 84 * pulse], radius=12, fill=(40, 120, 116, int(235 * a)))
            bolt(d, x0 + 50, y0 + 20 + 42 * pulse, 56 * pulse, GOLD + (int(255 * a),))
            d.text((x0 + 88, y0 + 20 + 42 * pulse - fc.size * 0.6), lab, font=fc, fill=CREAM + (int(255 * a),))

    # the twist: the real phone is the one at 1%, and its charger is right there
    a = sstep(20.3, 20.5, t) * (1 - sstep(22.1, 22.45, t))
    if t >= 20.3:
        text_c(d, 236, typed('THE CHARGER WAS', t, 20.3, 0.55), f_end, CREAM, a, stroke=8)
        text_c(d, 318, typed('RIGHT THERE.', t, 20.85, 0.45), f_end, GOLD, a, stroke=8)

    frame = Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')
    ff.stdin.write(frame.tobytes())
ff.stdin.close()
ff.wait()
print('wrote', out)
