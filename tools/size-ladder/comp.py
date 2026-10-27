"""Compositor: python3 comp.py plates|frames|events OUT [w h].  Shader plates (RGB + depth in alpha) -> dust in the same camera, bloom, text, counter."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import cam

FPS = 30; W, H = 1080, 1920
NF = int(round(cam.DUR * FPS))
FD = '/usr/share/fonts/opentype/inter/'
def font(sz, w='Black'): return ImageFont.truetype(FD + f'Inter-{w}.otf', sz)
sm = cam.sm
COUNTS = [(49, 'MOONS IN EARTH', cam.T_FILL_E), (1300, 'EARTHS IN JUPITER', cam.T_FILL_J), (1000, 'JUPITERS IN THE SUN', cam.T_FILL_S)]
CLOSE = [cam.T_CLOSE_E, cam.T_CLOSE_J, cam.T_CLOSE_S]

# text: (t0, t1, [(text, size, weight, y)], kind)
TEXT = [
    (0.10, 2.40, [('49 MOONS', 190, 'Black', 330), ('FIT INSIDE EARTH.', 86, 'ExtraBold', 505)]),
    (2.70, 5.40, [('EARTH IS ABOUT', 46, 'Bold', 168), ('4 MOONS WIDE.', 46, 'Bold', 226)]),
    (5.65, 7.30, [('NOW EARTH', 150, 'Black', 330), ('IS THE MOON.', 112, 'Black', 490)]),
    (8.00, 10.70, [('JUPITER IS 11\u00d7', 46, 'Bold', 168), ('WIDER THAN EARTH.', 46, 'Bold', 226)]),
    (10.85, 12.50, [('NOW JUPITER', 150, 'Black', 330), ('IS THE MOON.', 112, 'Black', 490)]),
    (13.60, 16.30, [('THE SUN IS 10\u00d7', 46, 'Bold', 168), ('WIDER THAN JUPITER.', 46, 'Bold', 226)]),
    (16.70, 19.6, [('1,000 JUPITERS.', 120, 'Black', 330), ('IN ONE STAR.', 84, 'ExtraBold', 468), ('STARS GET MUCH BIGGER.', 54, 'Bold', 575)]),
]
CTA = (18.4, 19.6, 'Follow @slowlighttv')
HUMAN = (17.9, 19.6, 'You are smaller than 1 pixel on this screen.')

def env(t, a, b, fi=.25, fo=.3): return min(max((t - a) / fi, 0), 1) * min(max((b - t) / fo, 0), 1)

def basis(v, f):
    cp, tg = np.array(v['uCamP']), np.array(v['uCamT'])
    fw = tg - cp; fw /= np.linalg.norm(fw); rt = np.cross(fw, [0, 1, 0]); rt /= np.linalg.norm(rt); up = np.cross(rt, fw)
    return cp, fw, rt, up, 1. / math.tan(f['uFov'] / 2) * .5

def plate_path(O, i): return f'{O}/plates/p{i:04d}.png'

def do_plates(O, part=0, parts=1):
    os.makedirs(f'{O}/plates', exist_ok=True)
    jobs = []
    for i in range(part, NF, parts):
        f, v = cam.params(i / FPS)
        jobs.append(dict(out=plate_path(O, i), w=W, h=H, f=f, v=v))
    json.dump(jobs, open(f'{O}/jobs{part}.json', 'w'))
    subprocess.run(['node', os.path.dirname(__file__) + '/gl/render.mjs', f'{O}/jobs{part}.json'], check=True)

# ---------- dust (world-space motes, three scales) ----------
rng = np.random.default_rng(5)
SCALES = [(np.array([0., 0, 0]), 7., 170), (np.array([0., 9, 0]), 70., 220), (np.array([0., 70, 0]), 700., 260)]
DUST = []
for c, L, n in SCALES:
    P = c + (rng.random((n, 3)) - .5) * 2 * L; DUST.append((P, rng.random(n), rng.random((n, 3)) - .5, L, c))

def dust_layer(t, cp, fw, rt, up, fl, tsurf, focus, camroll):
    lay = np.zeros((H, W, 3), np.float32)
    for P, br, vel, L, c in DUST:
        w = float(np.clip((8 * L - np.linalg.norm(cp - c)) / (6 * L), 0, 1)) ** 1.5
        if w <= .01: continue
        Pt = P + vel * L * .02 * t
        d = Pt - cp; z = d @ fw
        ok = z > L * .04
        x = (d @ rt) / np.where(ok, z, 1) * fl; y = (d @ up) / np.where(ok, z, 1) * fl
        px = x * H + W / 2; py = H / 2 - y * H
        for k in np.where(ok & (px > -40) & (px < W + 40) & (py > -40) & (py < H + 40))[0]:
            ix, iy = int(px[k]), int(py[k])
            ts = tsurf[min(max(iy, 0), H - 1), min(max(ix, 0), W - 1)]
            if np.linalg.norm(d[k]) > ts: continue
            r0 = L * .0035 / z[k] * fl * H
            blur = min(1., abs(z[k] - focus) / max(focus, 1e-3))
            r = max(1.6, r0) + 9 * blur; a = (.5 + .5 * br[k]) * w * (1.6 / (1 + (r / 2.2) ** 2)) * float(np.clip((z[k] - L * .04) / (L * .2), 0, 1))
            R = int(r * 2.2) + 1
            x0, x1, y0, y1 = max(ix - R, 0), min(ix + R + 1, W), max(iy - R, 0), min(iy + R + 1, H)
            if x0 >= x1 or y0 >= y1: continue
            yy, xx = np.mgrid[y0:y1, x0:x1]
            g = np.exp(-((xx - px[k]) ** 2 + (yy - py[k]) ** 2) / (2 * (r * .55) ** 2)) * a
            lay[y0:y1, x0:x1] += g[..., None] * np.array([1., .93, .82], np.float32) * (.8 if blur < .4 else 1)
    return lay

def bloom(img):
    im = Image.fromarray(np.clip(img * 255, 0, 255).astype(np.uint8))
    a = img.copy(); lum = a.mean(2, keepdims=True); br = np.clip((lum - .78) * 2.6, 0, 1) * a
    b = Image.fromarray(np.clip(br * 255, 0, 255).astype(np.uint8))
    b1 = np.asarray(b.filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    b2 = np.asarray(b.resize((W // 4, H // 4)).filter(ImageFilter.GaussianBlur(22)).resize((W, H), Image.BICUBIC), np.float32) / 255
    return img + b1 * .22 + b2 * .32

def icons(d, al):
    # Facebook / YouTube / Instagram marks, drawn flat in the text colour so they read on any frame
    a = int(255 * al); ink = (255, 246, 232, a); hole = (24, 18, 20, a); sz = 76; gap = 64; y = 1782
    x0 = (W - (3 * sz + 2 * gap)) / 2; f = font(60, 'Black')
    for k in range(3):
        x = x0 + k * (sz + gap)
        d.rounded_rectangle((x + 3, y + 6, x + sz + 3, y + sz + 6), 20, fill=(0, 0, 0, int(120 * al)))
        d.rounded_rectangle((x, y, x + sz, y + sz), 20, fill=ink)
        cx, cy = x + sz / 2, y + sz / 2
        if k == 0:      # Facebook: lowercase f
            d.text((cx + 4, cy + 8), 'f', font=f, fill=hole, anchor='mm')
        elif k == 1:    # YouTube: play triangle
            d.polygon([(cx - 11, cy - 16), (cx - 11, cy + 16), (cx + 18, cy)], fill=hole)
        else:           # Instagram: camera ring + dot
            d.rounded_rectangle((cx - 22, cy - 22, cx + 22, cy + 22), 11, outline=hole, width=5)
            d.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), outline=hole, width=5)
            d.ellipse((cx + 11, cy - 17, cx + 17, cy - 11), fill=hole)

def text_layer(t):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def put(s, sz, w, y, al, shadow=True):
        f = font(sz, w)
        while d.textlength(s, font=f) > 900 and sz > 20: sz -= 2; f = font(sz, w)
        x = (W - d.textlength(s, font=f)) / 2
        if shadow: d.text((x + 3, y + 6), s, font=f, fill=(0, 0, 0, int(150 * al)))
        d.text((x, y), s, font=f, fill=(255, 246, 232, int(255 * al)))
    for t0, t1, lines in TEXT:
        al = env(t, t0, t1)
        if al > 0:
            for k, (s, sz, w, y) in enumerate(lines):
                put(s, sz, w, y + (1 - min(max((t - t0 - .12 * k) / .35, 0), 1)) * 16, al * min(max((t - t0 - .12 * k) / .2, 0), 1))
    # counter
    for (n, lab, (a, b)), (ca, cb) in zip(COUNTS, CLOSE):
        al = env(t, a - .05, cb + .6, .25, .45)
        if al > 0:
            fr = min(max(cam.ease_fill(t, a, b) / 1.06, 0), 1)
            v = int(round(n * fr))
            s = f'{v:,}' if n == 49 else f'≈ {v:,}'
            put(s, 190, 'Black', 1400, al); put(lab, 46, 'Bold', 1630, al * .9)
    t0, t1, s = HUMAN; al = env(t, t0, t1, .5, .0001)
    if al > 0: put(s, 38, 'Bold', 1560, al * .92)
    t0, t1, s = CTA; al = env(t, t0, t1, .3, .0001)
    if al > 0:
        put(s, 54, 'Bold', 1690, al)
        icons(d, al)
    return np.asarray(lay, np.float32) / 255

def do_frame(O, i):
    out = f'{O}/frames/f{i:04d}.png'
    if os.path.exists(out): return
    t = i / FPS; f, v = cam.params(t)
    pl = np.asarray(Image.open(plate_path(O, i)).convert('RGBA'), np.float32) / 255
    rgb, a = pl[..., :3], pl[..., 3]
    tsurf = np.where(a > 0, 2 ** (np.clip(a - .02, 0, 1) / .98 * 11.5) - 1, 1e9)
    cp, fw, rt, up, fl = basis(v, f)
    focus = float(np.linalg.norm(np.array(v['uCamT']) - cp))
    img = rgb + dust_layer(t, cp, fw, rt, up, fl, tsurf, focus, f['uRoll']) * .55
    img = bloom(img)
    yy, xx = np.mgrid[0:H, 0:W]; r2 = ((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2
    img += (np.random.default_rng(i).standard_normal((H, W, 1)) * .012).astype(np.float32)
    tl = text_layer(t); img = img * (1 - tl[..., 3:]) + tl[..., :3] * tl[..., 3:]
    Image.fromarray(np.clip(img * 255 + .5, 0, 255).astype(np.uint8)).save(out + '.tmp.png'); os.replace(out + '.tmp.png', out)

def do_frames(O, part=0, parts=1):
    os.makedirs(f'{O}/frames', exist_ok=True)
    for i in range(part, NF, parts):
        if os.path.exists(plate_path(O, i)): do_frame(O, i)

def events(O):
    ev = dict(dur=cam.DUR, hit=[cam.T_CLOSE_E[0], cam.T_CLOSE_J[0], cam.T_CLOSE_S[0]], fills=[], fall=2.05,
              waves=[cam.T_WAVE_J, cam.T_WAVE_S], hook=2.4)
    for (n, lab, (a, b)), nr in zip(COUNTS, (49, 56, 56)):
        # impact times of the falling units: j-th lands when the fill fraction reaches (j+.5)/nr, same law as the shader's rain
        ts = [round(x, 4) for x in cam.moon_land_times(a, b)] if n == 49 else [round(a + (b - a) * (1 - (1 - (j + .5) / nr) ** (1 / 1.6)), 4) for j in range(nr)]
        ev['fills'].append(dict(n=n, t=ts, a=a, b=b))
    json.dump(ev, open(f'{O}/events.json', 'w'))

if __name__ == '__main__':
    cmd, O = sys.argv[1], sys.argv[2]
    part = int(sys.argv[3]) if len(sys.argv) > 3 else 0; parts = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    {'plates': lambda: do_plates(O, part, parts), 'frames': lambda: do_frames(O, part, parts), 'events': lambda: events(O)}[cmd]()
