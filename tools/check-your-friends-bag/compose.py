"""Check Your Friend's Bag: info layer + final encode.

python3 compose.py frames_dir timing.json mix.wav|none out.mp4 [crf]
Draws the Part 2 tag, the captions, the X-ray scan, the blue ROCK counter and the end card over the
rendered 3D frames with PIL, then pipes them to ffmpeg with the mix ("none" = silent music-ready cut).
"""
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

frames, timing_f, wav, out = sys.argv[1:5]
crf = sys.argv[5] if len(sys.argv) > 5 else '18'
T = json.load(open(timing_f))
FPS, W, H = 30, 1080, 1920
NF = int(round(T['dur'] * FPS))
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
SMALL = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
CREAM, GOLD, TEAL, BLUE, INK = (244, 236, 220), (255, 200, 120), (150, 214, 208), (79, 158, 224), (6, 9, 16)
F = lambda s, p=MONO: ImageFont.truetype(p, s)
f_hook, f_cap, f_end, f_num, f_chip, f_small, f_tag = F(64), F(54), F(58), F(92), F(46), F(31), F(26, SMALL)
PLACE = T['place']


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


def caption(d, t, t0, t1, lines, font, cols, y=250, gap=74, tdur=0.5):
    """lines typed one after another from t0, all out by t1"""
    a = sstep(t0, t0 + 0.08, t) * (1 - sstep(t1 - 0.3, t1, t))
    start = t0
    for i, s in enumerate(lines):
        dur = tdur * len(s) / 14
        text_c(d, y + i * gap, typed(s, t, start, dur), font, cols[i % len(cols)], a)
        start += dur + 0.12


CAPS = [  # t0, t1, lines, font, colours
    (0.15, 3.05, ['YOU MADE IT.'], f_hook, [CREAM]),
    (3.6, 5.95, ['SOMEONE ELSE IS', 'STILL CARRYING IT.'], f_cap, [CREAM, GOLD]),
    (6.45, 9.75, ["SUCCESS ISN'T", 'STAYING ON TOP.'], f_cap, [CREAM, GOLD]),
    (10.3, 13.75, ["IT'S SHOWING SOMEONE", 'ELSE HOW TO BUILD.'], f_cap, [CREAM, GOLD]),
    (14.3, 18.0, ['ONE ROCK AT A TIME.', 'TOGETHER.'], f_cap, [CREAM, TEAL]),
    (18.45, 19.45, ['YOUR STAIRS CAN BECOME', "SOMEONE ELSE'S BRIDGE."], f_end, [CREAM, GOLD]),
]

last_n = 0
cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-']
if wav != 'none':
    cmd += ['-i', wav]
cmd += ['-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'film']
if wav != 'none':
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

    # series tag, first 3 s (below the top strip)
    a = sstep(0.0, 0.1, t) * (1 - sstep(2.7, 3.05, t))
    text_c(d, 172, 'PART 2  ·  IF YOU SAW PART 1...', f_tag, TEAL, a * 0.95, stroke=4, spacing=2)
    # hook: "YOU MADE IT." (pause) "NOW LOOK BACK."
    for t0, t1, lines, font, cols in CAPS:
        if t0 - 0.01 <= t <= t1:
            caption(d, t, t0, t1, lines, font, cols, y=250 if font is not f_end else 236, gap=74 if font is not f_end else 70)
    a = sstep(1.25, 1.33, t) * (1 - sstep(2.75, 3.05, t))
    text_c(d, 336, typed('NOW LOOK BACK.', t, 1.25, 0.5), f_hook, GOLD, a)

    # X-ray scan: one cyan band sweeps down as the X-ray switches on
    xs = T['xray'][0]
    if xs - 0.05 <= t <= xs + 0.4:
        yb = (t - xs + 0.05) / 0.45 * (H + 200) - 100
        for k in range(60):
            al = int(70 * (1 - k / 60) * (1 - sstep(xs + 0.3, xs + 0.4, t)))
            d.line([(0, yb - k * 3), (W, yb - k * 3)], fill=(150, 230, 225, al), width=3)

    # blue ROCK counter (the friend's staircase), lower third; only ever goes up
    n = sum(1 for p in PLACE if p <= t)
    assert n >= last_n, (f, n, last_n)
    last_n = n
    a = sstep(PLACE[0], PLACE[0] + 0.1, t) * (1 - sstep(17.75, 18.05, t))
    if n >= 1 and a > 0.01:
        age = t - max(p for p in PLACE if p <= t)
        pulse = 1 + 0.16 * max(0.0, 1 - age / 0.25)
        fn = F(int(92 * pulse))
        num, chip = f'{n}', 'ROCK'
        cw = d.textlength(chip, font=f_chip) + 30
        nw = d.textlength(num, font=fn)
        x0 = (W - (cw + 22 + nw)) / 2
        y0 = 1430
        d.rounded_rectangle([x0, y0 + 18, x0 + cw, y0 + 82], radius=8, fill=BLUE + (int(235 * a),))
        d.text((x0 + 15, y0 + 22), chip, font=f_chip, fill=CREAM + (int(255 * a),))
        d.text((x0 + cw + 22, y0 + 50 - fn.size * 0.55), num, font=fn, fill=CREAM + (int(255 * a),), stroke_width=7, stroke_fill=INK + (int(235 * a),))

    frame = Image.alpha_composite(base.convert('RGBA'), ov)
    # end card: fade the world down, "PART 2" + channel
    e = sstep(19.35, 19.75, t)
    if e > 0:
        dim = Image.new('RGBA', (W, H), (6, 9, 16, int(150 * e)))
        frame = Image.alpha_composite(frame, dim)
        d2 = ImageDraw.Draw(frame)
        text_c(d2, 820, 'PART 2', f_end, GOLD, e, stroke=8, spacing=6)
        text_c(d2, 912, 'slowlighttv', f_small, CREAM, e, stroke=5, spacing=3)
    ff.stdin.write(frame.convert('RGB').tobytes())
ff.stdin.close()
ff.wait()
print('wrote', out)
