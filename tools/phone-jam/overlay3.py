# overlay3.py FRAMES_DIR PROJ_JSON OUT_MP4 : v3 info layer (no counters; the 99 appears once) over the rendered frames.
import sys, json, subprocess, math
from PIL import Image, ImageDraw, ImageFont
FR, PJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS = 1080, 1920, 30
N = 660
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
SMALL = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
CREAM = (255, 240, 214); RED = (214, 62, 48); TEAL = (40, 224, 204); GOLD = (255, 180, 66)
F = {}
def font(p, s):
    if (p, s) not in F: F[(p, s)] = ImageFont.truetype(p, s)
    return F[(p, s)]
proj = json.load(open(PJ))

def sst(a, b, x):
    if b <= a: return 1.0 if x >= a else 0.0
    k = min(1, max(0, (x - a) / (b - a))); return k * k * (3 - 2 * k)
def win(t, a, b, fi=0.15, fo=0.2):
    return sst(a, a + fi, t) * (1 - sst(b - fo, b, t))
def typed(s, t, t0, cps=24):
    n = int((t - t0) * cps) + 1
    return s[:max(1, min(len(s), n))] if t >= t0 else ''
def text(d, s, cx, y, size, a, fill=CREAM, fp=MONO, stroke=None, spacing=0, anchor='mm'):
    if not s or a <= 0.01: return
    f = font(fp, size); sw = stroke if stroke is not None else max(3, size // 12)
    al = int(255 * a)
    if spacing:
        widths = [f.getlength(c) + spacing for c in s]; tot = sum(widths) - spacing; x = cx - tot / 2 if anchor == 'mm' else cx
        for c, w_ in zip(s, widths):
            d.text((x, y), c, font=f, fill=fill + (al,), stroke_width=sw, stroke_fill=(0, 0, 0, int(al * 0.85)), anchor='lm'); x += w_
        return
    d.text((cx, y), s, font=f, fill=fill + (al,), stroke_width=sw, stroke_fill=(0, 0, 0, int(al * 0.85)), anchor=anchor)
def chip(d, s, cx, y, size, a, col=RED):
    if a <= 0.01: return
    f = font(MONO, size); w_ = f.getlength(s); pad = size * 0.45
    d.rounded_rectangle([cx - w_ / 2 - pad, y - size * 0.72, cx + w_ / 2 + pad, y + size * 0.72], radius=int(size * 0.25), fill=col + (int(235 * a),))
    d.text((cx, y), s, font=f, fill=CREAM + (int(255 * a),), anchor='mm')


enc = subprocess.Popen(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
for f in range(N):
    t = f / FPS; P = proj[f]
    base = Image.open(f'{FR}/f{f:04d}.jpg').convert('RGB')
    if base.size != (W, H): base = base.resize((W, H), Image.LANCZOS)
    ov = Image.Image.new('RGBA', (W, H), (0, 0, 0, 0)) if False else Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    # 0-2.4: the contradiction, typed fast
    text(d, typed("THE ROAD WAS EMPTY.", t, 0.0, 30), W / 2, 300, 72, win(t, -1, 2.45, 0, 0.25))
    text(d, typed("MAPS SAID: TRAFFIC JAM.", t, 0.55, 30), W / 2, 385, 60, win(t, -1, 2.45, 0, 0.25))
    text(d, 'ILLUSTRATION · NOT TO SCALE', 64, 150, 22, 0.7 * win(t, 2.5, 18.9), fp=SMALL, stroke=2, anchor='lm')
    ka = win(t, 0.35, 3.4, 0.2, 0.4)
    if ka > 0: chip(d, 'TRAFFIC JAM', P['knot'][0] * W, P['knot'][1] * H - 90, 36, ka)
    text(d, typed('NOT ONE CAR.', t, 2.7, 26), W / 2, 1360, 64, win(t, 2.6, 4.6))
    text(d, typed('ONE PERSON.', t, 4.7, 26), W / 2, 1360, 64, win(t, 4.6, 6.9))
    # the reveal: 99 appears once
    text(d, typed('99 PHONES.', t, 7.15, 18), W / 2, 330, 96, win(t, 7.1, 10.1, 0.1, 0.3))
    chip(d, 'REAL STORY · BERLIN 2020', W / 2, 440, 38, win(t, 8.5, 10.2, 0.2, 0.3))
    text(d, 'artist Simon Weckert, "Google Maps Hacks"', W / 2, 1535, 24, 0.8 * win(t, 8.7, 10.2), fp=SMALL, stroke=2)
    # map: why
    text(d, typed('THE MAP THOUGHT', t, 10.4, 28), W / 2, 1290, 58, win(t, 10.3, 13.7))
    text(d, typed('THEY WERE CARS.', t, 11.2, 28), W / 2, 1375, 58, win(t, 10.3, 13.7))
    ra = win(t, 14.3, 18.6, 0.2, 0.3)
    if ra > 0: chip(d, 'TRAFFIC JAM', P['knot'][0] * W + 90, P['knot'][1] * H - 10, 36, ra * 0.95)
    text(d, typed('A JAM THAT', t, 14.4, 26), W / 2, 250, 60, win(t, 14.3, 18.7))
    text(d, typed('NEVER EXISTED.', t, 15.1, 26), W / 2, 330, 60, win(t, 14.3, 18.7))
    ya = win(t, 15.4, 18.75, 0.2, 0.25)
    if ya > 0:
        x, y = P['you'][0] * W, P['you'][1] * H
        text(d, 'YOU', x + 80, y - 10, 38, ya, anchor='lm')
    ea = win(t, 19.0, 21.95, 0.05, 0.3)
    text(d, typed('NO TRAFFIC.', t, 19.1, 22), W / 2, 880, 78, ea)
    text(d, typed('JUST DATA.', t, 19.7, 22), W / 2, 975, 78, ea)
    base.paste(ov, (0, 0), ov)
    enc.stdin.write(base.tobytes())
enc.stdin.close(); enc.wait()
print('ok', OUT)
