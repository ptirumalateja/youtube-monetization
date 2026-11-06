#!/usr/bin/env python3
"""Map flash for the Greece & Crete beat: start tight on Roopkund, a line draws west to Crete while the view pulls out.
Usage: mapflash.py ne_50m_land.geojson out.mp4 DURATION_S"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
GEO, OUT, DUR = sys.argv[1], sys.argv[2], float(sys.argv[3])
W, H, FPS = 1080, 1920, 30
ROOP = (79.73, 30.26); CRETE = (24.9, 35.2); GREECE = (22.0, 39.0)
CY = 760                        # map centre height on screen (captions sit at y=1230)
BG, LAND, EDGE, LINE, DOT = (46, 60, 66), (104, 134, 140), (170, 215, 218), (255, 216, 47), (255, 90, 70)
FONT = os.environ.get('MAP_FONT', '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf')
try: ImageFont.truetype(FONT, 10)
except OSError: FONT = '/usr/share/fonts/opentype/inter/InterDisplay-Medium.otf'
polys = []
for f in json.load(open(GEO))['features']:
    g = f['geometry']; parts = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for p in parts:
        ring = p[0]
        xs = [c[0] for c in ring]; ys = [c[1] for c in ring]
        if max(xs) < -10 or min(xs) > 110 or max(ys) < 0 or min(ys) > 60: continue
        polys.append(ring)
ease = lambda t: 0.5 - 0.5 * math.cos(math.pi * min(max(t, 0), 1))
def hav(a, b):
    la1, la2 = math.radians(a[1]), math.radians(b[1]); dl = math.radians(b[0] - a[0])
    return 6371 * 2 * math.asin(math.sqrt(math.sin((la2-la1)/2)**2 + math.cos(la1)*math.cos(la2)*math.sin(dl/2)**2))
KM = round(hav(ROOP, CRETE), -2)
# great-circle-ish arc: lerp with a northward bulge
def arc(t):
    x = ROOP[0] + (CRETE[0] - ROOP[0]) * t; y = ROOP[1] + (CRETE[1] - ROOP[1]) * t + 7 * math.sin(math.pi * t)
    return x, y
N = round(DUR * FPS)
p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                      '-c:v', 'libx264', '-crf', '15', '-preset', 'fast', '-pix_fmt', 'yuv420p', OUT], stdin=subprocess.PIPE)
f_big = ImageFont.truetype(FONT, 46); f_sm = ImageFont.truetype(FONT, 34)
for i in range(N):
    t = i / FPS
    k = ease((t - 0.05) / 1.25)                     # line progress (lands ~1.3 s, on "Greece")
    z = ease(t / 1.4)
    scale = 50 + (15.5 - 50) * z                   # px per degree
    cx = ROOP[0] + ((ROOP[0] + CRETE[0]) / 2 - ROOP[0]) * z
    cy = ROOP[1] + (((ROOP[1] + CRETE[1]) / 2 + 3) - ROOP[1]) * z
    P = lambda lon, lat: (W / 2 + (lon - cx) * scale, CY - (lat - cy) * scale)
    img = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(img)
    for ring in polys:
        pts = [P(*c) for c in ring]
        d.polygon(pts, fill=LAND)
    edge = Image.new('RGB', (W, H), (0, 0, 0)); de = ImageDraw.Draw(edge)
    for ring in polys: de.line([P(*c) for c in ring], fill=EDGE, width=2)
    img = Image.blend(img, Image.composite(edge, img, edge.convert('L').point(lambda v: 255 if v > 0 else 0)), 0.8)
    glow = Image.new('RGB', (W, H), (0, 0, 0)); dg = ImageDraw.Draw(glow)
    if k > 0:
        seg = [P(*arc(s / 60 * k)) for s in range(61)]
        dg.line(seg, fill=LINE, width=14)
    r = 10 + 4 * math.sin(t * 9)
    x0, y0 = P(*ROOP); dg.ellipse([x0 - 3*r, y0 - 3*r, x0 + 3*r, y0 + 3*r], fill=DOT)
    if k >= 0.999:
        x1, y1 = P(*CRETE); dg.ellipse([x1 - 34, y1 - 34, x1 + 34, y1 + 34], fill=LINE)
    img = Image.composite(Image.new('RGB', (W, H), (255, 255, 255)), img, Image.new('L', (W, H), 0))
    img = Image.blend(img, Image.fromarray(__import__('numpy').maximum(__import__('numpy').asarray(img), __import__('numpy').asarray(glow.filter(ImageFilter.GaussianBlur(14))))), 1.0)
    d = ImageDraw.Draw(img)
    if k > 0:
        d.line([P(*arc(s / 60 * k)) for s in range(61)], fill=LINE, width=5)
    d.ellipse([x0 - r, y0 - r, x0 + r, y0 + r], fill=DOT)
    d.text((x0 + 22 - 44 * z, y0 + 18), os.environ.get('MAP_ROOP', 'ROOPKUND'), font=f_sm, fill=(240, 240, 240), stroke_width=3, stroke_fill=BG, anchor='la' if z < 0.5 else 'ra')
    if k >= 0.999:
        x1, y1 = P(*CRETE); d.ellipse([x1 - 11, y1 - 11, x1 + 11, y1 + 11], fill=LINE)
        a = min(1, (t - 1.3) / 0.15)
        col = tuple(int(BG[j] + (c - BG[j]) * a) for j, c in enumerate((255, 216, 47)))
        d.text((x1 - 20, y1 + 26), os.environ.get('MAP_GC', 'GREECE & CRETE'), font=f_big, fill=col, stroke_width=4, stroke_fill=BG, anchor='la')
        mx, my = P(*arc(0.5))
        d.text((mx, my - 40), f'~{int(KM):,} '+os.environ.get('MAP_KM', 'km'), font=f_sm, fill=tuple(int(BG[j] + (c - BG[j]) * a) for j, c in enumerate((220, 230, 230))),
               stroke_width=3, stroke_fill=BG, anchor='mm')
    p.stdin.write(img.tobytes())
p.stdin.close(); p.wait(); print('km', KM)
