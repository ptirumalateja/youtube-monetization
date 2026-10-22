"""He Moved a Mountain: info layer + final encode.

python3 compose.py frames_dir timing.json mix.wav out.mp4 [crf]
Draws the hook, the YEAR counter (red chip, big number, metres carved), the mid caption, the reveal lines
and the end line over the rendered 3D frames with PIL, then pipes them to ffmpeg with the mix.
"""
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont

frames, timing_f, wav, out = sys.argv[1:5]
crf = sys.argv[5] if len(sys.argv) > 5 else '18'
T = json.load(open(timing_f))
YEAR, MET = T['year'], T['m']
DROP = T['drop']
FPS, W, H = 30, 1080, 1920
NF = len(YEAR)
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
SMALL = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
CREAM, GOLD, TEAL, RED, INK = (244, 236, 220), (255, 200, 120), (150, 214, 208), (214, 62, 48), (6, 9, 16)
F = lambda s, p=MONO: ImageFont.truetype(p, s)
f_hook, f_cap, f_end, f_num, f_chip, f_small, f_tag, f_leg = F(66), F(54), F(70), F(92), F(46), F(31), F(24, SMALL), F(36)


def sstep(a, b, x):
    u = min(1, max(0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def typed(s, t, t0, dur):
    n = int(round(len(s) * (t - t0) / dur))
    return s[:max(1, min(len(s), n))] if t >= t0 else ''   # never a negative slice (playbook 8)


def text_c(d, y, s, font, fill, alpha, stroke=7, spacing=0, x=None):
    if not s or alpha <= 0.01:
        return
    w = d.textlength(s, font=font) + spacing * max(0, len(s) - 1)
    x = (W - w) / 2 if x is None else x
    col = fill + (int(255 * alpha),)
    ink = INK + (int(235 * alpha),)
    if spacing:
        for ch in s:
            d.text((x, y), ch, font=font, fill=col, stroke_width=stroke, stroke_fill=ink)
            x += d.textlength(ch, font=font) + spacing
    else:
        d.text((x, y), s, font=font, fill=col, stroke_width=stroke, stroke_fill=ink)


last_year, last_m = 0, -1.0
cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-i', wav,
       '-c:v', 'libx264', '-preset', 'slow', '-crf', crf, '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-tune', 'film',
       '-af', 'volume=4.5dB,alimiter=limit=0.84:attack=2:release=80:level=disabled', '-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest', '-movflags', '+faststart', out]
ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for f in range(NF):
    t = f / FPS
    base = Image.open(f'{frames}/f{f:04d}.jpg').convert('RGB')
    if base.size != (W, H):
        base = base.resize((W, H), Image.LANCZOS)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)

    # hook, typed by 1.7 s
    a = 1 - sstep(3.0, 3.4, t)
    text_c(d, 230, typed('ONE MAN.', t, 0.0, 0.35), f_hook, CREAM, a)
    if t >= 0.45:
        text_c(d, 316, typed('ONE HAMMER.', t, 0.45, 0.5), f_hook, CREAM, a)
    if t >= 1.05:
        text_c(d, 402, typed('ONE MOUNTAIN.', t, 1.05, 0.6), f_hook, GOLD, a, stroke=8)
    # mid caption (true: "people called me a lunatic")
    a = sstep(6.4, 6.6, t) * (1 - sstep(9.4, 9.8, t))
    if t >= 6.4:
        text_c(d, 286, typed('THEY CALLED HIM MAD.', t, 6.4, 0.8), f_cap, CREAM, a)
    # after the break
    a = sstep(17.3, 17.45, t) * (1 - sstep(21.25, 21.55, t))
    if t >= 17.3:
        text_c(d, 236, typed('22 YEARS.', t, 17.3, 0.45), f_end, GOLD, a, stroke=8)
        text_c(d, 336, 'ONE HAMMER AND CHISEL.', f_small, CREAM, a * sstep(17.9, 18.2, t), stroke=5)
    a = sstep(20.0, 20.2, t) * (1 - sstep(21.25, 21.55, t))
    if a > 0.01:
        # route legend, matched to the lines drawn in the scene
        b = a * sstep(20.3, 20.5, t)
        text_c(d, 408, 'HIS ROAD   15 KM', f_leg, GOLD, a, stroke=6)
        text_c(d, 460, 'OLD ROAD   55 KM', f_leg, (240, 120, 100), b, stroke=6)
        text_c(d, 520, 'ROUTES NOT TO SCALE', f_tag, TEAL, b * 0.9, stroke=4, spacing=3)
    # end line
    a = sstep(21.7, 21.85, t) * (1 - sstep(23.2, 23.55, t))
    if t >= 21.7:
        text_c(d, 236, typed('HE MOVED', t, 21.7, 0.35), f_end, CREAM, a, stroke=8)
        if t >= 22.05:
            text_c(d, 322, typed('A MOUNTAIN.', t, 22.05, 0.45), f_end, GOLD, a, stroke=8)
        text_c(d, 430, 'TRUE STORY: DASHRATH MANJHI', f_tag, TEAL, a * sstep(22.4, 22.6, t), stroke=4, spacing=2)
        text_c(d, 466, 'GEHLAUR, BIHAR, 1960-1982', f_tag, TEAL, a * sstep(22.4, 22.6, t), stroke=4, spacing=2)

    # year counter, under the hook lines (the lower third belongs to him)
    a = sstep(0.0, 0.05, t) * (1 - sstep(21.25, 21.55, t))
    yr, m = YEAR[f], MET[f]
    if t < 23.6:
        assert yr >= last_year and m >= last_m, (f, yr, last_year, m, last_m)   # counters only go up
        last_year, last_m = yr, m
    if a > 0.01:
        pulse = 1 + 0.18 * (2.718 ** (-max(0, t - DROP) / 0.2)) * (t >= DROP)
        fn = F(int(92 * pulse))
        num, chip = f'{yr}', 'YEAR'
        cw = d.textlength(chip, font=f_chip) + 30
        nw = d.textlength(num, font=fn)
        gap = 22
        x0 = (W - (cw + gap + nw)) / 2
        y0 = 590
        d.rounded_rectangle([x0, y0 + 18, x0 + cw, y0 + 18 + 64], radius=8, fill=RED + (int(240 * a),))
        d.text((x0 + 15, y0 + 22), chip, font=f_chip, fill=CREAM + (int(255 * a),))
        d.text((x0 + cw + gap, y0 + 50 - fn.size * 0.55), num, font=fn, fill=CREAM + (int(255 * a),), stroke_width=7, stroke_fill=INK + (int(235 * a),))
        ms = f'{m:.1f} M CARVED' if m < 10 else f'{int(m)} M CARVED'
        text_c(d, y0 + 118, ms, f_small, TEAL, a, stroke=5, spacing=4)
    frame = Image.alpha_composite(base.convert('RGBA'), ov).convert('RGB')
    ff.stdin.write(frame.tobytes())
ff.stdin.close()
ff.wait()
print('wrote', out)
