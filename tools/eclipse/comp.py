"""python3 comp.py plates|frames|video OUT [scale]   plates: shader renders; frames: bloom, grain, text; video: encode."""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import cam

FPS = 30
NF = int(round(cam.DUR * FPS))
FD = '/usr/share/fonts/opentype/inter/'
def font(sz, w='Black'): return ImageFont.truetype(FD + f'Inter-{w}.otf', sz)

# (t0, t1, [(text, size, weight)]): one short line per beat, top third
TEXT = [
    (0.15, 2.35, [("THE MOON", 132, 'Black'), ("SHOULDN'T FIT.", 104, 'Black')]),
    (2.75, 4.0, [("THE SUN IS 400× WIDER.", 76, 'Black')]),
    (4.05, 5.35, [("AND ABOUT 400×", 76, 'Black'), ("FARTHER AWAY.", 76, 'Black')]),
    (5.45, 6.45, [("SO THEY FIT.", 96, 'Black')]),
    (6.7, 9.95, [("FOR A FEW MINUTES,", 72, 'Black'), ("DAY TURNS TO NIGHT.", 72, 'Black')]),
    (10.05, 11.45, [("BUT IT'S", 130, 'Black'), ("ENDING.", 130, 'Black')]),
    (11.65, 13.3, [("THE MOON DRIFTS", 74, 'Black'), ("3.8 CM AWAY EVERY YEAR.", 74, 'Black')]),
    (13.4, 14.95, [("SOME ECLIPSES", 84, 'Black'), ("ALREADY MISS.", 84, 'Black')]),
    (15.05, 16.95, [("IN ABOUT 600 MILLION YEARS,", 66, 'Black'), ("THE LAST ONE.", 96, 'Black')]),
    (17.15, 19.45, [("YOU WERE BORN", 92, 'Black'), ("IN THE WINDOW.", 92, 'Black')]),
    (19.6, 21.0, [("NEXT ONE: 2 AUG 2027", 76, 'Black'), ("6 MIN 23 S OF NIGHT.", 64, 'Black')]),
]
TOP = 250

def env(t, a, b, fi=.18, fo=.22): return min(max((t - a) / fi, 0), 1) * min(max((b - t) / fo, 0), 1)

def plate_path(O, i): return f'{O}/plates/p{i:04d}.png'

def do_plates(O, S, part=0, parts=1, only=None):
    os.makedirs(f'{O}/plates', exist_ok=True)
    W, H = int(1080 * S), int(1920 * S)
    jobs = []
    idx = only if only is not None else range(NF)
    for i in idx:
        if i % parts != part: continue
        f, v = cam.params(i / FPS)
        jobs.append(dict(out=plate_path(O, i), w=W, h=H, f=f, v=v))
    json.dump(jobs, open(f'{O}/jobs{part}.json', 'w'))
    subprocess.run(['node', os.path.dirname(os.path.abspath(__file__)) + '/gl/render.mjs', f'{O}/jobs{part}.json'], check=True)

def bloom(img):
    H, W = img.shape[:2]
    lum = img.max(2, keepdims=True)
    br = np.clip((lum - .62) / .38, 0, 1) ** 1.5 * img
    b = Image.fromarray(np.clip(br * 255, 0, 255).astype(np.uint8))
    out = img.copy()
    for div, rad, k in ((1, 6, .25), (4, 14, .35), (12, 22, .45)):
        small = b.resize((max(W // div, 8), max(H // div, 8)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(rad))
        out += np.asarray(small.resize((W, H), Image.BICUBIC), np.float32) / 255 * k
    return 1 - (1 - np.clip(out, 0, 1.6) / 1.6) ** 1.6 if False else np.clip(out, 0, 1)

def text_layer(t, W, H, S):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for t0, t1, lines in TEXT:
        al = env(t, t0, t1)
        if al <= 0: continue
        y = TOP * S
        for k, (s, sz, w) in enumerate(lines):
            sz = int(sz * S); f = font(sz, w)
            while d.textlength(s, font=f) > 960 * S and sz > 20: sz -= 2; f = font(sz, w)
            a = al * min(max((t - t0 - .1 * k) / .16, 0), 1)
            rise = (1 - min(max((t - t0 - .1 * k) / .3, 0), 1)) * 14 * S
            x = (W - d.textlength(s, font=f)) / 2
            for r, aa in ((10, 70), (4, 110)):
                pass
            d.text((x + 2 * S, y + rise + 5 * S), s, font=f, fill=(0, 0, 0, int(160 * a)))
            d.text((x, y + rise), s, font=f, fill=(255, 248, 238, int(255 * a)))
            y += sz * 1.12
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(14 * S)).point(lambda v: int(v * .55))
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); shadow.putalpha(sh)
    return Image.alpha_composite(shadow, lay)

rng = np.random.default_rng(3)
def frame(O, i, S):
    t = i / FPS
    img = np.asarray(Image.open(plate_path(O, i)).convert('RGB'), np.float32) / 255
    H, W = img.shape[:2]
    img = bloom(img)
    # flash at the hook bloom / annulus flood (from the timeline: big photosphere gain)
    g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    g = np.asarray(Image.fromarray(((g * 18) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255 - .5
    img = np.clip(img + g[..., None] * .035 * (1 - img), 0, 1)
    im = Image.fromarray((img * 255).astype(np.uint8)).convert('RGBA')
    im = Image.alpha_composite(im, text_layer(t, W, H, S)).convert('RGB')
    os.makedirs(f'{O}/frames', exist_ok=True)
    im.save(f'{O}/frames/f{i:04d}.jpg', quality=95)

if __name__ == '__main__':
    mode, O = sys.argv[1], sys.argv[2]; S = float(sys.argv[3]) if len(sys.argv) > 3 else 1
    if mode == 'plates':
        part, parts = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 1)
        do_plates(O, S, part, parts)
    elif mode == 'frames':
        part, parts = (int(sys.argv[4]), int(sys.argv[5])) if len(sys.argv) > 5 else (0, 1)
        for i in range(part, NF, parts): frame(O, i, S)
    elif mode == 'still':
        for t in map(float, sys.argv[4].split(',')):
            i = int(round(t * FPS)); do_plates(O, S, only=[i]); frame(O, i, S)
    elif mode == 'video':
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-framerate', str(FPS), '-i', f'{O}/frames/f%04d.jpg',
                        '-c:v', 'libx264', '-crf', '16', '-preset', 'slow', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', f'{O}/silent.mp4'], check=True)
