"""One Step a Day: info layer + final encode.

python3 compose.py frames_dir timing.json mix.wav out.mp4 [crf]
Draws the hook, the day counter (red DAY chip, big number, height line), the mid caption and the end
line over the rendered 3D frames with PIL, then pipes them to ffmpeg with the mix.
"""
import json, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

frames, timing_f, wav, out = sys.argv[1:5]
crf = sys.argv[5] if len(sys.argv) > 5 else '18'
T = json.load(open(timing_f))
DAYS = T['days']
FPS, W, H = 30, 1080, 1920
NF = len(DAYS)
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
SMALL = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
CREAM, GOLD, TEAL, RED, INK = (244, 236, 220), (255, 200, 120), (150, 214, 208), (214, 62, 48), (6, 9, 16)
F = lambda s, p=MONO: ImageFont.truetype(p, s)
f_hook, f_cap, f_end, f_num, f_chip, f_small, f_tag = F(64), F(54), F(70), F(92), F(46), F(31), F(24, SMALL)


def sstep(a, b, x):
    u = min(1, max(0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def typed(s, t, t0, dur):
    n = int(round(len(s) * (t - t0) / dur))
    return s[:max(1, min(len(s), n))] if t >= t0 else ''   # never a negative slice (playbook 8)


def text_c(d, y, s, font, fill, alpha, stroke=7, spacing=0):
    if not s or alpha <= 0.01:
        return
    w = d.textlength(s, font=font) + spacing * max(0, len(s) - 1)
    x = (W - w) / 2
    col = fill + (int(255 * alpha),)
    ink = INK + (int(235 * alpha),)
    if spacing:
        for ch in s:
            d.text((x, y), ch, font=font, fill=col, stroke_width=stroke, stroke_fill=ink)
            x += d.textlength(ch, font=font) + spacing
    else:
        d.text((x, y), s, font=font, fill=col, stroke_width=stroke, stroke_fill=ink)


def height_str(n):
    h = n * 0.17
    return f'{h:.1f} M UP' if h < 10 else f'{int(h)} M UP'


last_day = 0
last_h = -1.0
cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
       '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'film',
       '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out]
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in range(NF):
    t = f / FPS
    base = Image.open(f'{frames}/f{f:04d}.jpg').convert('RGB')
    if base.size != (W, H):
        base = base.resize((W, H), Image.LANCZOS)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # hook (typed by 1.5 s), then the mid caption, then the end line
    a = 1 - sstep(2.9, 3.3, t)
    text_c(d, 250, typed('DAY 1.', t, 0.0, 0.45), f_hook, CREAM, a)
    text_c(d, 336, typed('THEY LAUGHED.', t, 0.5, 1.0), f_hook, GOLD, a)
    a = sstep(6.0, 6.2, t) * (1 - sstep(9.6, 10.0, t))
    if t >= 6.0:
        text_c(d, 286, typed('THEY STOPPED LAUGHING.', t, 6.0, 0.9), f_cap, CREAM, a)
    a = sstep(13.45, 13.6, t) * (1 - sstep(15.55, 15.9, t))
    if t >= 13.45:
        text_c(d, 236, typed('ONE STEP A DAY.', t, 13.45, 0.6), f_end, GOLD, a, stroke=8)
        b = a * sstep(14.0, 14.3, t)
        text_c(d, 340, '365 STEPS x 17 CM = 62 M', f_small, CREAM, b, stroke=5)
        text_c(d, 384, 'ABOUT A 20-STOREY BUILDING', f_small, CREAM, b, stroke=5)
        text_c(d, 438, 'THOUGHT EXPERIMENT', f_tag, TEAL, b * 0.9, stroke=4, spacing=3)

    # day counter, lower third (above the bottom 18% safe zone)
    a = sstep(0.0, 0.05, t) * (1 - sstep(15.55, 15.9, t))
    day = max(1, DAYS[f])
    assert day >= last_day, (f, day, last_day)   # counters only go up
    last_day = day
    if a > 0.01:
        pulse = 1 + 0.18 * np.exp(-max(0, t - T['place'][-1]) / 0.18) * (t >= T['place'][-1])
        fn = F(int(92 * pulse))
        num = f'{day}'
        chip = 'DAY'
        cw = d.textlength(chip, font=f_chip) + 30
        nw = d.textlength(num, font=fn)
        gap = 22
        x0 = (W - (cw + gap + nw)) / 2
        y0 = 1430
        d.rounded_rectangle([x0, y0 + 18, x0 + cw, y0 + 18 + 64], radius=8, fill=RED + (int(240 * a),))
        d.text((x0 + 15, y0 + 22), chip, font=f_chip, fill=CREAM + (int(255 * a),))
        d.text((x0 + cw + gap, y0 + 50 - fn.size * 0.55), num, font=fn, fill=CREAM + (int(255 * a),), stroke_width=7, stroke_fill=INK + (int(235 * a),))
        h = DAYS[f] * 0.17
        assert h >= last_h
        last_h = h
        text_c(d, y0 + 118, height_str(max(1, DAYS[f])), f_small, TEAL, a, stroke=5, spacing=4)
    frame = Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')
    ff.stdin.write(frame.tobytes())
ff.stdin.close()
ff.wait()
print('wrote', out)
