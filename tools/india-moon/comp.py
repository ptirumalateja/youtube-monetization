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
# text: (t0, t1, [(text, size, weight, y)], fade-in, fade-out)
HOOK = [('11 INDIAS', 200, 'Black', 290), ('FIT ON THE MOON.', 92, 'ExtraBold', 480)]
TEXT = [
    (-1.0, 1.6, HOOK, .25, .3),
    (16.15, 18.0, [('INDIA IS', 150, 'Black', 270), ('A PIXEL TOO.', 124, 'Black', 430)], .25, .3),
    (18.1, 20.05, [('WHICH STATE GOES', 84, 'Black', 270), ('ON THE MOON NEXT?', 84, 'Black', 372)], .25, .3),
    (20.15, 99, HOOK, .45, .3),
]
RING = (16.3, 18.0)

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
        f, v, a = cam.params(i / FPS)
        jobs.append(dict(out=plate_path(O, i), w=W, h=H, f=f, v=v, a=a))
    json.dump(jobs, open(f'{O}/jobs{part}.json', 'w'))
    subprocess.run(['node', os.path.dirname(__file__) + '/gl/render.mjs', f'{O}/jobs{part}.json'], check=True)

# ---------- dust (world-space motes, three scales) ----------
rng = np.random.default_rng(5)
_B = cam.bodies(16.0)
SCALES = [(_B[0], 1.6, 150), (_B[1], 7., 170), (_B[2], 70., 220), (_B[3] + np.array([0, 60., 0]), 700., 260)]
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

def project(p, v, f):
    cp, fw, rt, up, fl = basis(v, f); d = np.array(p) - cp; z = d @ fw
    return (d @ rt) / z * fl * H + W / 2, H / 2 - (d @ up) / z * fl * H

def text_layer(t, v, f):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    def put(s, sz, w, y, al, shadow=True):
        fo = font(sz, w)
        while d.textlength(s, font=fo) > 940 and sz > 20: sz -= 2; fo = font(sz, w)
        x = (W - d.textlength(s, font=fo)) / 2
        if shadow:
            for dx, dy, a in ((3, 6, 150), (0, 0, 70)):
                d.text((x + dx, y + dy), s, font=fo, fill=(0, 0, 0, int(a * al)), stroke_width=6 if dx == 0 else 0, stroke_fill=(0, 0, 0, int(a * al)))
        d.text((x, y), s, font=fo, fill=(255, 246, 232, int(255 * al)))
    for t0, t1, lines, fi, fo_ in TEXT:
        al = env(t, t0, t1, fi, fo_)
        if al > 0:
            for k, (s, sz, w, y) in enumerate(lines):
                kk = min(max((t - t0 - .12 * k) / .35, 0), 1) if t0 > 0 else 1
                put(s, sz, w, y + (1 - kk) * 16, al * (min(max((t - t0 - .12 * k) / .2, 0), 1) if t0 > 0 else 1))
    # counter
    val, lab = cam.counter(t)
    if lab:
        span = [(0.95, 5.65), (5.95, 9.0), (9.55, 12.6), (13.15, 16.35)]
        al = max(env(t, a, b, .2, .35) for a, b in span)
        if val and al > 0:
            big = val == '1.85 MILLION'
            put(val, 150 if big else 190, 'Black', 1420 + (20 if big else 0), al); put(lab, 46, 'Bold', 1630, al * .92)
    # payoff: ring around the Earth dot
    al = env(t, RING[0], RING[1], .3, .3)
    if al > 0:
        x, y = project(v['uCE'], v, f); r = 30 + 14 * (1 - min((t - RING[0]) / .5, 1)) ** 2
        for rr, a, wd in ((r + 3, 90, 7), (r, 255, 3)):
            d.ellipse((x - rr, y - rr, x + rr, y + rr), outline=(255, 236, 200, int(a * al)) if a == 255 else (0, 0, 0, int(a * al)), width=wd)
    return np.asarray(lay, np.float32) / 255

def do_frame(O, i):
    out = f'{O}/frames/f{i:04d}.png'
    if os.path.exists(out): return
    t = i / FPS; f, v, _ = cam.params(t)
    pl = np.asarray(Image.open(plate_path(O, i)).convert('RGBA'), np.float32) / 255
    rgb, a = pl[..., :3], pl[..., 3]
    tsurf = np.where(a > 0, 2 ** (np.clip(a - .02, 0, 1) / .98 * 11.5) - 1, 1e9)
    cp, fw, rt, up, fl = basis(v, f)
    focus = float(np.linalg.norm(np.array(v['uCamT']) - cp))
    img = rgb + dust_layer(t, cp, fw, rt, up, fl, tsurf, focus, f['uRoll']) * .55
    img = bloom(img)
    yy, xx = np.mgrid[0:H, 0:W]; r2 = ((xx - W / 2) / (W * .75)) ** 2 + ((yy - H / 2) / (H * .62)) ** 2
    img += (np.random.default_rng(i).standard_normal((H, W, 1)) * .012).astype(np.float32)
    tl = text_layer(t, v, f); img = img * (1 - tl[..., 3:]) + tl[..., :3] * tl[..., 3:]
    Image.fromarray(np.clip(img * 255 + .5, 0, 255).astype(np.uint8)).save(out + '.tmp.png'); os.replace(out + '.tmp.png', out)

def do_frames(O, part=0, parts=1):
    os.makedirs(f'{O}/frames', exist_ok=True)
    for i in range(part, NF, parts):
        if os.path.exists(plate_path(O, i)): do_frame(O, i)

def events(O):
    ev = dict(dur=cam.DUR, sheet=cam.T_SHEET[1], moon=[float(ta) for _, ta in cam.MOON_SCHED],
              drops={k: list(v) for k, v in cam.T_DROP.items()}, waves={k: list(v) for k, v in cam.T_WAVE.items()},
              pay=cam.T_PAY[0], prompt=cam.T_PROMPT[0], lifts={k: list(v) for k, v in cam.T_LIFT.items()})
    # tick times for each wave: when the counter passes each step (Earth: every India; Jupiter/Sun: a grain stream)
    for key, n in (('E', 155), ('J', 90), ('S', 120)):
        a, b = cam.T_WAVE[key]; ts = np.linspace(a, b, 2000); fr = np.array([cam.wave_frac(x, key) for x in ts])
        ev['tick_' + key] = [float(np.interp((j + .5) / n, fr, ts)) for j in range(n)]
    json.dump(ev, open(f'{O}/events.json', 'w'))

if __name__ == '__main__':
    cmd, O = sys.argv[1], sys.argv[2]
    part = int(sys.argv[3]) if len(sys.argv) > 3 else 0; parts = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    {'plates': lambda: do_plates(O, part, parts), 'frames': lambda: do_frames(O, part, parts), 'events': lambda: events(O)}[cmd]()
