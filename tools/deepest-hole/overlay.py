# Draws the tag, hook, the depth counter (one odometer, only goes up), the red name chips tracked to each hole, the caption
# and the scale note into an RGBA PNG .mov (1080x1920, 30 fps). usage: python3 overlay.py proj.json out.mov [hook-key]
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
TL = json.load(open('timeline.json')); T = TL['T']; TX = TL['text']; ST = TL['strokes']; EV = TL['events']; HO = TL['holes']
PROJ = {int(k): v for k, v in json.load(open(sys.argv[1])).items()}
if len(sys.argv) > 3: TX['hook']['s'] = sys.argv[3]
CREAM = (244, 232, 210); RED = (214, 62, 48); BLACK = (0, 0, 0)
F = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'; FS = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
def font(n, f=F): return ImageFont.truetype(f, n)
def cl(x, a=0.0, b=1.0): return min(b, max(a, x))

def typed(spec, t):
    if t < spec['t0']: return None, 0.0
    n = max(1, int(len(spec['s']) * cl((t - spec['t0']) / (spec['t1'] - spec['t0']))))   # n>=1: no negative slicing
    o0, o1 = spec['out']; return spec['s'][:n], 1.0 - cl((t - o0) / (o1 - o0))

def wrap(d, s, f, maxw):
    lines, cur = [], ''
    for w in s.split(' '):
        c = (cur + ' ' + w).strip()
        if d.textlength(c, font=f) <= maxw: cur = c
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def text_block(d, s, f, cx, y, maxw, alpha, full, spacing=1.18):
    pos = 0
    for ln in wrap(d, full, f, maxw):
        part = s[pos:pos + len(ln) + 1].rstrip() if pos < len(s) else ''
        if part: d.text((cx - d.textlength(ln, font=f) / 2, y), part, font=f, fill=CREAM + (int(255 * alpha),), stroke_width=6, stroke_fill=BLACK + (int(255 * alpha),))
        pos += len(ln) + 1; y += int(f.size * spacing)

def drilled(h, t):
    dr = h.get('drill')
    if not dr: return h['depth']
    u = cl((t - dr[0]) / (dr[1] - dr[0])); return h['depth'] * (1 - (1 - u) ** 1.6)

def counter(t):
    v = 0.0
    for ts, dv in ST:
        if ts <= t: v = dv
    if t > EV['water_hit']:
        v = max(v, *(drilled(HO[k], t) for k in ('wood', 'mine', 'kola')))
    return v

def fmt(v): return f'{v:.1f} M' if v < 100 else f'{v:,.0f} M'

def chip(d, ax, ay, name, line, a):
    A = int(255 * a); fn, fl = font(40), font(27)
    tw = max(d.textlength(name, font=fn) + 28, d.textlength(line, font=fl)); right = ax < W * 0.55
    x = ax + 70 if right else ax - 70 - tw; x = cl(x, 40, W - 40 - tw); y = cl(ay - 30, 560, 1480)
    d.ellipse((ax - 14, ay - 14, ax + 14, ay + 14), outline=RED + (A,), width=5)
    d.line((ax + (14 if right else -14), ay, x if right else x + tw, y + 28), fill=RED + (A,), width=3)
    d.rounded_rectangle((x, y, x + d.textlength(name, font=fn) + 28, y + 56), radius=9, fill=RED + (A,))
    d.text((x + 14, y + 28), name, font=fn, fill=CREAM + (A,), anchor='lm')
    d.text((x + 2, y + 66), line, font=fl, fill=CREAM + (A,), stroke_width=4, stroke_fill=BLACK + (A,))

def frame(fi):
    t = fi / FPS
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    s, a = typed(TX['tag'], t)
    if s and a > 0: d.text((W / 2, 108), s, font=font(22, FS), fill=CREAM + (int(190 * a),), anchor='mm', stroke_width=4, stroke_fill=BLACK + (int(190 * a),))
    ca = 1.0 - cl((t - 19.6) / 0.3)
    if ca > 0:
        al = (int(255 * ca * 0.85),)
        d.text((W / 2, 178), 'D E P T H', font=font(27), fill=CREAM + al, anchor='mm', stroke_width=4, stroke_fill=BLACK + al)
        d.text((W / 2, 262), fmt(counter(t)), font=font(92), fill=CREAM + (int(255 * ca),), anchor='mm', stroke_width=7, stroke_fill=BLACK + (int(255 * ca),))
        na = ca * cl((t - 6.0) / 0.4)
        if na > 0: d.text((W / 2, 336), 'REAL DEPTHS · HOLES SHOWN SIDE BY SIDE', font=font(20, FS), fill=CREAM + (int(150 * na),), anchor='mm', stroke_width=3, stroke_fill=BLACK + (int(150 * na),))
    for k, sz in (('hook', 66), ('caption', 50)):
        s, a = typed(TX[k], t)
        if s and a > 0: text_block(d, s, font(sz), W / 2, 410, 960, a, TX[k]['s'])
    for i, c in enumerate(TL['chips']):
        t0, t1 = c['t']; a = cl((t - t0) / 0.2) * (1 - cl((t - (t1 - 0.25)) / 0.25))
        if a <= 0 or fi not in PROJ: continue
        px, py, _ = PROJ[fi][i]; chip(d, px * W, py * H, c['name'], c['line'], a)
    return img

if __name__ == '__main__':
    out = sys.argv[2]; n = int(round(T * FPS))
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'png', '-pix_fmt', 'rgba', out], stdin=subprocess.PIPE)
    last = -1.0
    for i in range(n):
        v = counter(i / FPS); assert v >= last, (i, v, last); last = v     # the odometer only goes up
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
