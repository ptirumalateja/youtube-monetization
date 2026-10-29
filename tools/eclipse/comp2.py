"""python3 comp2.py plates|frames|still|video OUT [scale] [part parts|times]   Helium cut: scene2.glsl plates -> bloom, CA, grain, flashes, text."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import cam2 as cam
from comp import bloom, font, env, plate_path

FPS = 30; NF = int(round(cam.DUR * FPS))
os.environ['FRAG'] = 'scene2.glsl'
TOP = 255
# (t0, t1, [(text, size, weight)])
TEXT = [
    (0.12, 2.40, [("WE FOUND IT", 138, 'Black'), ("ON THE SUN FIRST.", 98, 'Black')]),
    (2.62, 4.45, [("GUNTUR, INDIA", 84, 'Black'), ("18 AUGUST 1868", 60, 'Bold')]),
    (4.55, 6.4, [("RED. BLUE. VIOLET.", 68, 'Black'), ("ALL HYDROGEN.", 68, 'Black')]),
    (6.6, 8.85, [("THEN, A YELLOW LINE.", 74, 'Black')]),
    (8.95, 10.0, [("NOT SODIUM.", 116, 'Black')]),
    (10.05, 11.45, [("BOTH REPORTS REACHED", 62, 'Black'), ("PARIS THE SAME DAY.", 62, 'Black')]),
    (11.65, 13.1, [("THEY NAMED IT", 80, 'Black'), ("AFTER THE SUN.", 80, 'Black')]),
    (13.2, 14.95, [("HELIUM.", 190, 'Black')]),
    (15.05, 16.95, [("FOR 27 YEARS,", 92, 'Black'), ("NOBODY HAD HELD IT.", 80, 'Black')]),
    (17.1, 18.3, [("1895. A ROCK.", 84, 'Black'), ("A GLASS TUBE.", 84, 'Black')]),
    (18.4, 20.0, [("THE GAS IN A BIRTHDAY", 62, 'Black'), ("BALLOON WAS FOUND", 62, 'Black'), ("ON THE SUN FIRST.", 62, 'Black')]),
    (20.1, 21.0, [("Follow @slowlighttv", 62, 'Black'), ("stories worth slowing down for", 38, 'Bold')]),
]
# (t, amplitude, decay seconds): white flashes on the hits
FLASH = [(.3, .55, .2), (11.2, .75, .22), (11.52, .55, .2), (17.32, .45, .2), (18.72, .32, .22)]

def do_plates(O, S, part=0, parts=1, only=None):
    os.makedirs(f'{O}/plates', exist_ok=True)
    W, H = int(1080 * S), int(1920 * S)
    jobs = []
    for i in (only if only is not None else range(NF)):
        if i % parts != part: continue
        f, v = cam.params(i / FPS)
        jobs.append(dict(out=plate_path(O, i), w=W, h=H, f=f, v=v))
    json.dump(jobs, open(f'{O}/jobs{part}.json', 'w'))
    subprocess.run(['node', os.path.dirname(os.path.abspath(__file__)) + '/gl/render.mjs', f'{O}/jobs{part}.json'], check=True)

def text_layer(t, W, H, S, f, v):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for t0, t1, lines in TEXT:
        al = env(t, t0, t1)
        if al <= 0: continue
        y = TOP * S
        for k, (s, sz, w) in enumerate(lines):
            sz = int(sz * S); fo = font(sz, w)
            while d.textlength(s, font=fo) > 960 * S and sz > 20: sz -= 2; fo = font(sz, w)
            a = al * min(max((t - t0 - .09 * k) / .16, 0), 1)
            rise = (1 - min(max((t - t0 - .09 * k) / .3, 0), 1)) * 14 * S
            x = (W - d.textlength(s, font=fo)) / 2
            col = (255, 214, 64) if s in ("HELIUM.",) else (255, 248, 238)
            d.text((x + 2 * S, y + rise + 5 * S), s, font=fo, fill=(0, 0, 0, int(160 * a)))
            d.text((x, y + rise), s, font=fo, fill=col + (int(255 * a),))
            y += sz * 1.12
    # sodium label under the ruler, placed from the shader's own mapping
    if f.get('uShot') == 10 and f.get('uD', 0) > .05:
        span, ctr = f['uZoom'], f['uA']
        px = (( (589.3 - ctr) / span * 2 * .485) + .5) * W + v['uCen'][0] * W
        py = H / 2 + .35 * W * 1.0 + 56 * S
        fo = font(int(34 * S), 'Bold'); s = "SODIUM"
        a = int(255 * f['uD'])
        d.text((px + 14 * S, py), s, font=fo, fill=(255, 150, 60, a))
        px2 = (((587.56 - ctr) / span * 2 * .485) + .5) * W + v['uCen'][0] * W
        fo2 = font(int(34 * S), 'Black'); s2 = "NEW"
        d.text((px2 - 26 * S - d.textlength(s2, font=fo2), py - 150 * S), s2, font=fo2, fill=(255, 232, 90, a))
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(14 * S)).point(lambda q: int(q * .55))
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0)); shadow.putalpha(sh)
    return Image.alpha_composite(shadow, lay)

rng = np.random.default_rng(3)
def frame(O, i, S):
    t = i / FPS
    f, v = cam.params(t)
    img = np.asarray(Image.open(plate_path(O, i)).convert('RGB'), np.float32) / 255
    H, W = img.shape[:2]
    img = bloom(img)
    # lens: slight chromatic aberration (R out, B in) and vignette
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r2 = ((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2
    img *= (1 - .35 * np.clip(r2 * 1.6, 0, 1))[..., None]
    pil = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    ch = list(pil.split())
    ch[0] = ch[0].resize((int(W * 1.004), int(H * 1.004)), Image.BILINEAR).crop((int(W * .002), int(H * .002), int(W * .002) + W, int(H * .002) + H))
    ch[2] = ch[2].resize((int(W * .997), int(H * .997)), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    img = np.asarray(Image.merge('RGB', ch), np.float32) / 255
    g = rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32)
    g = np.asarray(Image.fromarray(((g * 18) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR), np.float32) / 255 - .5
    img = img + g[..., None] * .04 * (1 - img)
    for t0, a, dec in FLASH:
        if t >= t0: img = img + a * math.exp(-(t - t0) / dec) * (1 - img)
    im = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).convert('RGBA')
    im = Image.alpha_composite(im, text_layer(t, W, H, S, f, v)).convert('RGB')
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
