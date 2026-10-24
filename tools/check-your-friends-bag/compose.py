"""Check Your Friend's Bag: info layer + final encode.

python3 compose.py frames_dir timing.json mix.wav|none out.mp4 [crf]
Draws the Part 2 tag, the captions, the rock labels (anchors projected from the scene by times.js), the blue ROCK
counter and the end card over the rendered 3D frames with PIL (Part 1's palette, fonts and sizes), then pipes them to ffmpeg with the mix ("none" = silent music-ready cut).
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
CREAM, GOLD, TEAL, BLUE, INK = (240, 232, 214), (240, 186, 92), (150, 214, 208), (79, 158, 224), (6, 9, 16)   # Part 1 style sheet
F = lambda s, p=MONO: ImageFont.truetype(p, s)
f_hook, f_cap, f_end, f_num, f_chip, f_small, f_tag = F(62), F(54), F(60), F(60), F(40), F(30), F(26, SMALL)
f_lab, f_step = F(38), F(28)
RUST = (214, 128, 72)
PLACE = T['place']
META = T['frames']


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


def chip_text(d, x, y, s, font, accent, alpha):
    """label: cream text on a dark chip with a thin accent edge, centred on x, bottom at y"""
    w = d.textlength(s, font=font)
    h = font.size
    x0, y0 = x - w / 2 - 12, y - h - 14
    d.rounded_rectangle([x0, y0, x0 + w + 24, y], radius=8, fill=(8, 12, 20, int(190 * alpha)), outline=accent + (int(230 * alpha),), width=3)
    d.text((x0 + 12, y0 + 5), s, font=font, fill=CREAM + (int(255 * alpha),))
    return x0, y0, x0 + w + 24, y


def draw_labels(d, f, t):
    m = META[f]
    # X-ray: the five big weights, stacked beside the bag with leader lines (never overlapping)
    a = sstep(T['xray'] + 0.25, T['xray'] + 0.55, t) * (1 - sstep(5.7, 6.0, t))
    if a > 0.01:
        xr = [L for L in m['labels'] if L['xr'] and L['state'] == 0 and L['at'][2]]
        xr.sort(key=lambda L: L['at'][1])
        bx, by = m['bag'][0] * W, m['bag'][1] * H
        col_x = min(W - 230, max(230, bx + (260 if bx < W / 2 else -260)))
        y = max(470, by - 140 - 34 * len(xr) / 2)
        for L in xr:
            ax, ay = L['at'][0] * W, L['at'][1] * H
            box = chip_text(d, col_x, y + 54, L['txt'], f_lab, RUST, a)
            ex = box[0] if col_x > ax else box[2]
            d.line([(ex, y + 30), (ax, ay)], fill=RUST + (int(170 * a),), width=3)
            d.ellipse([ax - 6, ay - 6, ax + 6, ay + 6], fill=RUST + (int(220 * a),))
            y += 68
    # rocks out of the bag: ALONE as it is lifted and carried, every rock as it is handed across, every step once set
    for L in m['labels']:
        if not L['at'][2] or L['hide'] > 0.5:
            continue
        x, y = L['at'][0] * W, L['at'][1] * H
        if not (40 < x < W - 40 and 420 < y < 1560):
            continue
        if L['state'] == 2:
            al = sstep(0, 0.25, L['age']) * (1 - 0.55 * sstep(18.6, 19.2, t)) * (1 - sstep(19.2, 19.45, t))
            font = f_lab if L['dist'] < 4.5 else f_step
            acc = (110, 180, 255) if L['txt'] != 'TOO LATE' else GOLD
        elif L['state'] == 1 and (L['i'] == 0 and t > T['lift'][0] + 0.15 or T['cyc2'] <= t):
            al, font, acc = 1.0, (f_lab if L['dist'] < 4.5 else f_step), RUST
        else:
            continue
        chip_text(d, x, y - 10, L['txt'], font, acc, al)



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
import os
ONLY = [int(x) for x in os.environ.get('ONLY', '').split(',') if x]
ff = None if ONLY else subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in (ONLY or range(NF)):
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

    draw_labels(d, f, t)

    # blue ROCK counter (the friend's staircase), lower third; only ever goes up
    n = sum(1 for p in PLACE if p <= t)
    assert n >= last_n, (f, n, last_n)
    last_n = n
    a = sstep(PLACE[0], PLACE[0] + 0.1, t) * (1 - sstep(17.75, 18.05, t))
    if n >= 1 and a > 0.01:
        age = t - max(p for p in PLACE if p <= t)
        pulse = 1 + 0.16 * max(0.0, 1 - age / 0.25)
        fn = F(int(60 * pulse))
        num, chip = f'{n}', 'ROCK'
        cw = d.textlength(chip, font=f_chip) + 30
        nw = d.textlength(num, font=fn)
        x0 = (W - (cw + 22 + nw)) / 2
        y0 = 1440
        d.rounded_rectangle([x0, y0 + 14, x0 + cw, y0 + 70], radius=8, fill=BLUE + (int(235 * a),))
        d.text((x0 + 15, y0 + 18), chip, font=f_chip, fill=CREAM + (int(255 * a),))
        d.text((x0 + cw + 22, y0 + 42 - fn.size * 0.55), num, font=fn, fill=CREAM + (int(255 * a),), stroke_width=7, stroke_fill=INK + (int(235 * a),))

    frame = Image.alpha_composite(base.convert('RGBA'), ov)
    # end card: fade the world down, "PART 2" + channel
    e = sstep(19.35, 19.75, t)
    if e > 0:
        dim = Image.new('RGBA', (W, H), (6, 9, 16, int(150 * e)))
        frame = Image.alpha_composite(frame, dim)
        d2 = ImageDraw.Draw(frame)
        text_c(d2, 820, 'PART 2', f_end, GOLD, e, stroke=8, spacing=6)
        text_c(d2, 912, 'slowlighttv', f_small, CREAM, e, stroke=5, spacing=3)
    if ONLY:
        frame.convert('RGB').save(f'{out}_{f:04d}.jpg', quality=90)
        continue
    ff.stdin.write(frame.convert('RGB').tobytes())
if ff:
    ff.stdin.close()
    ff.wait()
print('wrote', out)
