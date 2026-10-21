# overlay.py FRAMES_DIR PROJ_JSON OUT_MP4 : draws the info layer over the rendered frames and encodes the silent picture.
import sys, json, subprocess, math
from PIL import Image, ImageDraw, ImageFont
FR, PJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
W, H, FPS, N = 1080, 1920, 30, 660
MONO = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
SMALL = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
CREAM = (255, 240, 214); RED = (214, 62, 48); TEAL = (40, 224, 204); GOLD = (255, 180, 66)
F = {}
def font(p, s):
    if (p, s) not in F: F[(p, s)] = ImageFont.truetype(p, s)
    return F[(p, s)]
proj = json.load(open(PJ))
cnt = [r['count'] for r in proj]
assert all(b >= a for a, b in zip(cnt, cnt[1:])), 'counter must be monotonic'

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
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    # hook (typed by ~1.6 s), then the premise
    text(d, typed("MAPS DOESN'T", t, 0.0, 26), W / 2, 300, 72, win(t, -1, 2.45, 0, 0.25))
    text(d, typed("SEE CARS.", t, 0.5, 26), W / 2, 385, 72, win(t, -1, 2.45, 0, 0.25))
    text(d, 'ILLUSTRATION · NOT TO SCALE', 64, 150, 22, 0.7 * win(t, 2.5, 14.3), fp=SMALL, stroke=2, anchor='lm')
    # counter block
    ca = win(t, 2.45, 14.35, 0.2, 0.25)
    text(d, 'PHONES ON THIS STREET', W / 2, 235, 27, ca, spacing=5)
    text(d, f'{cnt[f]}', W / 2, 315, 92, ca)
    kmh = max(4, round(P['kmh'])); sa = ca * (1 - sst(10.3, 10.6, t))
    if sa > 0.01:
        col = TEAL if kmh > 24 else (GOLD if kmh > 9 else RED)
        s = f'AVG SPEED {kmh:>2} KM/H'; fo = font(MONO, 30); w_ = fo.getlength(s)
        d.ellipse([W / 2 - w_ / 2 - 40, 398 - 11, W / 2 - w_ / 2 - 18, 398 + 11], fill=col + (int(255 * sa),))
        text(d, s, W / 2 + 14, 398, 30, sa)
    # act 1 captions
    text(d, typed('IT SEES PHONES.', t, 2.55, 30), W / 2, 1360, 56, win(t, 2.5, 5.9))
    text(d, 'EACH DOT IS ONE PHONE', W / 2, 1440, 30, win(t, 3.1, 5.9), spacing=3)
    text(d, typed('PHONES SLOW DOWN.', t, 6.3, 30), W / 2, 1360, 56, win(t, 6.2, 9.95))
    text(d, typed('THE ROAD TURNS RED.', t, 7.6, 30), W / 2, 1440, 56, win(t, 7.5, 9.95))
    # the jam marker at the knot
    ka = win(t, 9.75, 10.9, 0.12, 0.2)
    if ka > 0: chip(d, 'TRAFFIC JAM', P['knot'][0] * W, P['knot'][1] * H - 120, 42, ka)
    # the reveal
    ra = win(t, 11.35, 14.4, 0.15, 0.25)
    chip(d, 'BERLIN, 2020', W / 2, 520, 42, ra)
    text(d, typed('NO CARS.', t, 11.45, 26), W / 2, 1290, 60, ra)
    text(d, typed('ONE WAGON.', t, 12.05, 26), W / 2, 1375, 60, ra)
    text(d, typed('99 PHONES.', t, 12.65, 26), W / 2, 1460, 60, ra)
    text(d, 'artist Simon Weckert, "Google Maps Hacks"', W / 2, 1535, 24, 0.8 * win(t, 12.9, 14.4), fp=SMALL, stroke=2)
    # rerouting
    qa = win(t, 15.25, 18.75, 0.2, 0.25)
    text(d, typed('MAPS BELIEVES IT', t, 15.3, 30), W / 2, 250, 56, qa)
    text(d, typed('AND STEERS YOU AROUND.', t, 16.3, 30), W / 2, 330, 56, qa)
    ya = win(t, 15.4, 18.75, 0.2, 0.25)
    if ya > 0:
        x, y = P['you'][0] * W, P['you'][1] * H
        text(d, 'YOU', x + 80, y - 10, 38, ya, anchor='lm')
    # end line, typed once, gone before the loop restarts the hook
    ea = win(t, 18.9, 21.95, 0.05, 0.3)
    text(d, typed('THE JAM IS', t, 19.0, 22), W / 2, 880, 74, ea)
    text(d, typed('MADE OF PHONES.', t, 19.5, 22), W / 2, 975, 74, ea)
    base.paste(ov, (0, 0), ov)
    enc.stdin.write(base.tobytes())
enc.stdin.close(); enc.wait()
print('ok', OUT)
