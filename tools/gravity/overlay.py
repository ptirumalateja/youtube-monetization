#!/usr/bin/env python3
"""Gravity reel: composite text over rendered frames and pipe to ffmpeg (silent video).
usage: overlay.py <frames_dir> <out.mp4>   (frames fNNNN.jpg + state_*.json from render.js, 30 fps, 480 frames)"""
import sys, json, glob, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
D, OUT = sys.argv[1], sys.argv[2]; W, H, FPS, NF = 1080, 1920, 30, 480
st = []
for f in sorted(glob.glob(f'{D}/state_*.json'), key=lambda p: int(p.split('_')[-2])): st += json.load(open(f))
assert len(st) >= NF, len(st)
F = '/usr/share/fonts/opentype/inter/'
def font(n, s): return ImageFont.truetype(F + n, s)
INK = (18, 30, 52)
def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def tw(d, s, f, sp):  # tracked width
    return sum(d.textlength(c, font=f) + sp for c in s) - sp
def tracked(d, xy, s, f, sp, fill):
    x, y = xy
    for c in s: d.text((x, y), c, font=f, fill=fill); x += d.textlength(c, font=f) + sp
def centre(layer, y, s, f, sp, fill, a=1.0):
    d = ImageDraw.Draw(layer); w = tw(d, s, f, sp); tracked(d, ((W - w) / 2, y), s, f, sp, fill[:3] + (int(255 * a),))
def halo(layer, r=10):  # soft white glow under dark text for legibility
    a = layer.split()[3].filter(ImageFilter.GaussianBlur(r)); g = Image.new('RGBA', layer.size, (255, 255, 255, 0)); g.putalpha(a.point(lambda v: min(255, v * 2)))
    return Image.alpha_composite(g, layer)
def vertical(base, x, ytop_from_bottom, lines):
    """text rotated to read bottom-to-top along the left edge; lines = [(text, font, sp, fill, alpha)]"""
    L = Image.new('RGBA', (H, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L); y = 0
    for s, f, sp, fill, a in lines:
        tracked(d, (0, y), s, f, sp, fill[:3] + (int(255 * a),)); y += f.size + 14
    r = L.rotate(90, expand=True)  # now 200 wide, H tall; text runs upward from the bottom
    base.alpha_composite(halo(r, 6), (x, -(0)))
fT = font('InterDisplay-Regular.otf', 112); fS = font('Inter-SemiBold.otf', 38); fC = font('InterDisplay-Light.otf', 40); fCn = font('InterDisplay-SemiBold.otf', 74); fG = font('Inter-SemiBold.otf', 30)
fQ = font('InterDisplay-Regular.otf', 84); fL = font('InterDisplay-Regular.otf', 92)
ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-i', '-', '-c:v', 'libx264', '-crf', '21', '-preset', 'medium', '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', OUT], stdin=subprocess.PIPE)
for i in range(NF):
    ts = i / FPS; s = st[i]; tg, h = s['tg'], s['h']
    im = Image.open(f'{D}/f{i:04d}.jpg').convert('RGBA')
    # closing veil
    q = ease((ts - 14.2) / 0.5)
    if q > 0: im.alpha_composite(Image.new('RGBA', (W, H), (246, 249, 253, int(150 * q))))
    # title (0 - 2.2 s)
    a = ease(ts / 0.5) * (1 - ease((ts - 1.7) / 0.5))
    if a > 0:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y0 = 330 - int(14 * (1 - ease(ts / 0.8)))
        centre(L, y0, 'WHAT IF GRAVITY', fT, 4, INK, a); centre(L, y0 + 130, 'SWITCHED OFF?', fT, 4, INK, a)
        centre(L, y0 + 300, 'HOW LONG UNTIL YOU ACTUALLY FLOAT?', fS, 6, INK, a * 0.85)
        im.alpha_composite(halo(L, 12))
    # left-edge counters (from 1.8 s)
    ca = ease((ts - 1.8) / 0.4) * (1 - ease((ts - 14.2) / 0.4))
    if ca > 0:
        hs = f'{h:.2f} m' if h < 10 else f'{h:.1f} m'
        lines = [('TIME WITHOUT GRAVITY', fG, 5, INK, ca * .8), (f'{tg:4.1f} s', fCn, 2, INK, ca),
                 ('HEIGHT OFF THE GROUND', fG, 5, INK, ca * .8), (hs, fCn, 2, INK, ca)]
        if ts > 2.2: lines.append(('TIME-LAPSE x2.7', fG, 5, INK, ca * .8))
        L = Image.new('RGBA', (H, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L); y = 0
        for s_, f_, sp, fill, aa in lines:
            tracked(d, (430, y), s_, f_, sp, fill[:3] + (int(255 * aa),)); y += int(f_.size * 1.3) + (6 if f_ is fG else 22)
        r = halo(L.rotate(90, expand=True), 6)  # 340 wide, H tall; text runs upward from the left of the bottom
        im.alpha_composite(r.crop((0, 0, 420, H)), (24, 0))
        # (rotated block sits at the left edge, anchored to the bottom of the rotated image)
        # marker
        if 4.9 < ts < 6.8:
            m = Image.new('RGBA', (W, H), (0, 0, 0, 0)); aa = ease((ts - 4.9) / 0.3) * (1 - ease((ts - 6.2) / 0.5)); dm = ImageDraw.Draw(m)
            for k_, t_ in enumerate(['ONE METRE', 'OFF THE GROUND']): tracked(dm, (450, 1330 + k_ * 56), t_, fS, 6, INK + (int(255 * aa),))
            im.alpha_composite(halo(m, 10))
        g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); centre(g, 1560, 'HYDERABAD  17.4° N  ·  IGNORING AIR AND WATER', fG, 4, INK, ca * .75); im.alpha_composite(halo(g, 8))
    # centre line
    la = ease((ts - 9.0) / 0.6) * (1 - ease((ts - 12.6) / 0.6))
    if la > 0:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); centre(L, 330, 'People. Cars. Water. You.', fL, 0, INK, la); im.alpha_composite(halo(L, 12))
    # closing question
    if q > 0:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); y0 = 700
        for k, t in enumerate(['WOULD YOU RATHER', 'FLOAT FOR 10 SECONDS', 'OR FALL FOR 3?']): centre(L, y0 + k * 120, t, fQ, 3, INK, ease((ts - 14.2 - k * 0.18) / 0.4))
        im.alpha_composite(L)
    b = __import__('io').BytesIO(); im.convert('RGB').save(b, 'JPEG', quality=95); ff.stdin.write(b.getvalue())
ff.stdin.close(); ff.wait()
