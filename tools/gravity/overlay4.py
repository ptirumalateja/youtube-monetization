#!/usr/bin/env python3
"""Gravity reel v4 (23.5 s): serif text, gravity / time / height / speed readouts, flashes and grade over the rendered street frames, piped to ffmpeg (silent video).
usage: overlay3.py <frames_dir> <out.mp4> [nframes=705]   (frames fNNNN.jpg + state_*.json from render.js with PAGE=street4.html at 1296x2304, 30 fps)"""
import sys, json, glob, subprocess, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
D, OUT = sys.argv[1], sys.argv[2]; NF = int(sys.argv[3]) if len(sys.argv) > 3 else 705; W, H, FPS = 1080, 1920, 30
st = []
for f in sorted(glob.glob(f'{D}/state_*.json'), key=lambda p: int(p.split('_')[-2])): st += json.load(open(f))
assert len(st) >= NF, len(st)
SW, TF, TI = 2.2, st[0]['tf'], st[0]['ti']; TG_END, PHI_END = st[NF - 1]['tg'], st[0]['phil']
T1M = next(i / FPS for i, x in enumerate(st) if x['h'] >= 1.0); Q0 = TI + 2.5
SF = '/usr/share/fonts/truetype/liberation/LiberationSerif-'
def font(n, s): return ImageFont.truetype(SF + n + '.ttf', s)
fT, fSub, fLab, fNum, fSm, fIt, fIt2, fQ = font('Regular', 100), font('Regular', 34), font('Regular', 26), font('Regular', 68), font('Regular', 24), font('Italic', 74), font('Italic', 56), font('Regular', 82)
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def tw(d, s, f, sp): return sum(d.textlength(c, font=f) + sp for c in s) - sp
def tracked(d, xy, s, f, sp, fill):
    x, y = xy
    for c in s: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp
def put(layer, x, y, s, f, sp=0, a=1.0, centre=False):
    d = ImageDraw.Draw(layer)
    if centre: x = (W - tw(d, s, f, sp)) / 2
    tracked(d, (x, y), s, f, sp, (255, 255, 255, int(255 * a)))
def shadow(layer, r=7, k=170):
    a = layer.split()[3]; sh = Image.new('RGBA', layer.size, (8, 12, 24, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v: min(255, int(v * k / 100))))
    return Image.alpha_composite(sh, layer)
def gval(ts):   # displayed gravity, m/s2: Earth 9.8, ramps to 0 at the switch, ramps back at TF
    if ts < SW: return 9.8
    if ts < SW + 0.3: return 9.8 * (1 - ease((ts - SW) / 0.3))
    if ts < TF: return 0.0
    return 9.8 * ease((ts - TF) / 0.3)
ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '18', '-preset', 'medium', '-maxrate', '16M', '-bufsize', '32M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for i in range(NF):
    ts = i / FPS; s = st[i]; tg, h, phi, vf, rate = s['tg'], s['h'], s['phi'], s['vfall'], s['rate']
    im = Image.open(f'{D}/f{i:04d}.jpg').convert('RGB').resize((W, H), Image.LANCZOS)
    im = im.filter(ImageFilter.UnsharpMask(radius=1.4, percent=70, threshold=2)); im = ImageEnhance.Color(im).enhance(1.10); im = ImageEnhance.Contrast(im).enhance(1.06); im = im.convert('RGBA')
    q = ease((ts - Q0) / 0.6); iv = ease((ts - TI - 0.35) / 1.4) * (1 - q)
    if iv > 0: im.alpha_composite(Image.new('RGBA', (W, H), (10, 16, 30, int(190 * iv))))
    if q > 0: im.alpha_composite(Image.new('RGBA', (W, H), (10, 16, 30, int(190 + 50 * q))))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = ease(ts / 0.35) * (1 - ease((ts - 1.8) / 0.4))     # title
    if a > 0:
        put(L, 0, 420, 'What if gravity', fT, 0, a, True); put(L, 0, 540, 'switched off?', fT, 0, a, True)
        put(L, 0, 700, 'HOW LONG UNTIL YOU ACTUALLY FLOAT?', fSub, 5, a * .9, True)
    fa = ease(ts / 0.3) * (1 - ease((ts - TI - 1.6) / 0.5))     # left block
    if fa > 0:
        g = gval(ts); gs = '0 m/s²' if g <= 0.001 else f'{g:.1f} m/s²'
        put(L, 72, 920, 'GRAVITY', fLab, 4, fa * .95); put(L, 72, 958, gs, fNum, 1, fa)
        put(L, 72, 1034, 'SWITCHED OFF' if SW + 0.3 <= ts < TF else ('EARTH NORMAL' if ts < SW else 'BACK ON'), fSm, 4, fa * .8)
        if ts >= SW:
            ka = ease((ts - SW) / 0.4) * fa; fall = ts > TF
            put(L, 72, 560, 'TIME FALLING' if fall else 'TIME WITHOUT GRAVITY', fLab, 4, ka * .95)
            put(L, 72, 598, f'{phi:.1f} s' if fall else f'{tg:.1f} s', fNum, 1, ka)
            put(L, 72, 672, 'SHOWN IN REAL TIME' if fall else f'SHOWN IN TIME-LAPSE ×{rate:.1f}', fSm, 4, ka * .8)
            hs = f'{h:.2f} m' if h < 10 else f'{h:.1f} m'
            put(L, 72, 740, 'YOUR HEIGHT', fLab, 4, ka * .95); put(L, 72, 778, hs, fNum, 1, ka)
            put(L, 72, 852, f'FALL SPEED {vf * 3.6:.0f} km/h' if fall else 'ABOVE THE STREET', fSm, 4, ka * .8)
        if SW <= ts < TI + 0.5: put(L, 0, 1530, 'HYDERABAD · 17.4° N · IGNORING AIR AND WATER', fSm, 4, fa * .75, True)
    caps = [(T1M - 0.1, T1M + 1.6, 'ONE METRE OFF THE GROUND', fLab, 5), (7.6, 11.0, 'People. Cars. Water. You.', fIt, 0), (11.4, 14.8, 'Buildings stay. Everything else leaves.', fIt2, 0),
            (TF + 0.1, TF + 1.9, 'Gravity is back.', fIt, 0), (TI + 1.0, TI + 2.5, f'You floated {TG_END:.0f} seconds. You fell {PHI_END:.1f}.', fIt2, 0)]
    for t0, t1, txt, f, sp in caps:
        k = ease((ts - t0) / 0.4) * (1 - ease((ts - (t1 - 0.4)) / 0.4))
        if k > 0: put(L, 0, 1400, txt, f, sp, k, True)
    if q > 0:
        for k, t in enumerate(['Would you rather', 'float for 10 seconds', 'or fall for 3?']): put(L, 0, 640 + k * 118, t, fQ, 0, ease((ts - Q0 - 0.1 - k * 0.2) / 0.45), True)
    im.alpha_composite(shadow(L))
    for t0, dur, al in [(SW, 0.14, 150), (TF, 0.12, 120), (TI, 0.16, 230)]:   # flashes on the switch, gravity back and the impact
        u = (ts - t0) / dur
        if 0 <= u < 1: im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(al * (1 - u) ** 2))))
    b = io.BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=96); ff.stdin.write(b.getvalue())
ff.stdin.close(); ff.wait()
