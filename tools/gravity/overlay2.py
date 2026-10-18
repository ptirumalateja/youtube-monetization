#!/usr/bin/env python3
"""Gravity reel v2 (20 s): serif text over the rendered street frames, piped to ffmpeg (silent video).
usage: overlay2.py <frames_dir> <out.mp4> [nframes=600]   (frames fNNNN.jpg + state_*.json from render.js with PAGE=street.html, 30 fps)"""
import sys, json, glob, subprocess, io
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D, OUT = sys.argv[1], sys.argv[2]; NF = int(sys.argv[3]) if len(sys.argv) > 3 else 600; W, H, FPS = 1080, 1920, 30
st = []
for f in sorted(glob.glob(f'{D}/state_*.json'), key=lambda p: int(p.split('_')[-2])): st += json.load(open(f))
assert len(st) >= NF, len(st)
SF = '/usr/share/fonts/truetype/liberation/LiberationSerif-'
def font(n, s): return ImageFont.truetype(SF + n + '.ttf', s)
fIt2 = font('Italic', 56)
fT, fSub, fLab, fNum, fSm, fIt, fQ = font('Regular', 100), font('Regular', 34), font('Regular', 31), font('Regular', 88), font('Regular', 28), font('Italic', 74), font('Regular', 82)
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def tw(d, s, f, sp): return sum(d.textlength(c, font=f) + sp for c in s) - sp
def tracked(d, xy, s, f, sp, fill):
    x, y = xy
    for c in s: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp
def put(layer, x, y, s, f, sp=0, a=1.0, centre=False):
    d = ImageDraw.Draw(layer)
    if centre: x = (W - tw(d, s, f, sp)) / 2
    tracked(d, (x, y), s, f, sp, (255, 255, 255, int(255 * a)))
def shadow(layer, r=7, k=170):  # soft dark shadow under white text for legibility on any background
    a = layer.split()[3]; sh = Image.new('RGBA', layer.size, (8, 12, 24, 0)); sh.putalpha(a.filter(ImageFilter.GaussianBlur(r)).point(lambda v: min(255, int(v * k / 100))))
    return Image.alpha_composite(sh, layer)
ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for i in range(NF):
    ts = i / FPS; s = st[i]; tg, h = s['tg'], s['h']
    im = Image.open(f'{D}/f{i:04d}.jpg').convert('RGBA')
    q = ease((ts - 17.0) / 0.6)
    if q > 0: im.alpha_composite(Image.new('RGBA', (W, H), (10, 16, 30, int(120 * q))))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    a = ease(ts / 0.35) * (1 - ease((ts - 1.8) / 0.4))     # title 0 - 2.2 s
    if a > 0:
        put(L, 0, 420, 'What if gravity', fT, 0, a, True); put(L, 0, 540, 'switched off?', fT, 0, a, True)
        put(L, 0, 700, 'HOW LONG UNTIL YOU ACTUALLY FLOAT?', fSub, 5, a * .9, True)
    ca = ease((ts - 2.2) / 0.4) * (1 - ease((ts - 17.0) / 0.5))   # left counters
    if ca > 0:
        hs = f'{h:.2f} m' if h < 10 else f'{h:.1f} m'
        put(L, 36, 640, 'TIME WITHOUT GRAVITY', fLab, 4, ca * .95); put(L, 36, 684, f'{tg:.1f} s', fNum, 1, ca)
        put(L, 36, 790, 'SHOWN IN TIME-LAPSE ×2.7', fSm, 4, ca * .8)
        put(L, 36, 900, 'YOUR HEIGHT', fLab, 4, ca * .95); put(L, 36, 944, hs, fNum, 1, ca)
        put(L, 36, 1050, 'ABOVE THE STREET', fSm, 4, ca * .8)
        put(L, 0, 1500, 'HYDERABAD · 17.4° N · IGNORING AIR AND WATER', fSm, 4, ca * .75, True)
    for t0, t1, txt, f, sp in [(5.1, 6.7, 'ONE METRE OFF THE GROUND', fLab, 5), (9.6, 13.6, 'People. Cars. Water. You.', fIt, 0), (14.4, 16.9, 'Buildings stay. Everything else leaves.', fIt2, 0)]:
        k = ease((ts - t0) / 0.5) * (1 - ease((ts - (t1 - 0.5)) / 0.5))
        if k > 0: put(L, 0, 1250, txt, f, sp, k, True)
    if q > 0:
        for k, t in enumerate(['Would you rather', 'float for 10 seconds', 'or fall for 3?']): put(L, 0, 640 + k * 118, t, fQ, 0, ease((ts - 17.1 - k * 0.2) / 0.45), True)
    im.alpha_composite(shadow(L))
    b = io.BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=95); ff.stdin.write(b.getvalue())
ff.stdin.close(); ff.wait()
