"""Extended-cut compositor (21 s, loop). python3 comp2.py plates|frames|events OUT [part parts]
Frames 0-10.3 s reuse the original plates through the time warp in cam2; later frames render into plates2/."""
import json, math, os, subprocess, sys
import numpy as np
from PIL import Image
from scipy.ndimage import uniform_filter1d
import cam, cam2, comp
from comp import W, H, font, env, basis, dust_layer, bloom
from PIL import ImageDraw

FPS = 30; NF2 = int(round(cam2.DUR2 * FPS))
Wi, Wv = cam2.Winv, cam2.W
# original fill / close windows mapped into the new timeline
FILL = [tuple(Wi(x) for x in w) for w in (cam.T_FILL_E, cam.T_FILL_J, cam.T_FILL_S)]
CLOSE = [tuple(Wi(x) for x in w) for w in (cam.T_CLOSE_E, cam.T_CLOSE_J, cam.T_CLOSE_S)]
COUNTS = [(49, 'MOONS IN EARTH'), (1321, 'EARTHS IN JUPITER'), (985, 'JUPITERS IN THE SUN')]
HOOK = [('49 MOONS', 190, 'Black', 330), ('FIT INSIDE EARTH.', 86, 'ExtraBold', 505)]
TEXT = [
    (-.1, 1.25, HOOK, .05),
    (1.35, Wi(5.4), [('EARTH IS ABOUT', 46, 'Bold', 168), ('4 MOONS WIDE.', 46, 'Bold', 226)], .25),
    (Wi(8.0), Wi(10.7), [('JUPITER IS 11×', 46, 'Bold', 168), ('WIDER THAN EARTH.', 46, 'Bold', 226)], .25),
    (Wi(13.6), Wi(16.3), [('THE SUN IS 10×', 46, 'Bold', 168), ('WIDER THAN JUPITER.', 46, 'Bold', 226)], .25),
    (cam2.T_COUNT, cam2.T_CUT, [('STEPHENSON 2-18 IS ABOUT', 46, 'Bold', 168), ('2,150× WIDER THAN THE SUN.', 46, 'Bold', 226)], .25),
    (cam2.T_CUT + .05, cam2.T_PROMPT - .1, [('YOU ARE SMALLER', 124, 'Black', 760), ('THAN ONE PIXEL.', 124, 'Black', 900)], .35),
    (cam2.T_PROMPT, 19.2, [('WHAT SHOULD', 118, 'Black', 760), ('WE SQUEEZE NEXT?', 100, 'Black', 900)], .35),
]

def put(d, s, sz, w, y, al, shadow=True, dx=0):
    f = font(sz, w)
    while d.textlength(s, font=f) > 900 and sz > 20: sz -= 2; f = font(sz, w)
    x = (W - d.textlength(s, font=f)) / 2 + dx
    if shadow: d.text((x + 3, y + 6), s, font=f, fill=(0, 0, 0, int(150 * al)))
    d.text((x, y), s, font=f, fill=(255, 246, 232, int(255 * al)))

def fmt(v): return f'{int(round(v)):,}'

def text_layer(t):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for t0, t1, lines, fi in TEXT:
        al = env(t, t0, t1, fi, .3 if t0 > 0 else .25)
        if t0 < 0: al = min(1., al)
        if al > 0:
            for k, (s, sz, w, y) in enumerate(lines):
                put(d, s, sz, w, y + (1 - min(max((t - t0 - .1 * k) / .3, 0), 1)) * 14 * (t0 > 0), al * min(max((t - t0 - .1 * k) / .2, 0), 1) if t0 > 0 else al)
    # loop: the hook line re-forms and is fully on at the last frame, matching frame 0
    ra = min(max((t - 19.8) / 1.1, 0), 1)
    if ra > 0 and t > 19.8:
        for s, sz, w, y in HOOK: put(d, s, sz, w, y, ra)
    # counters for the three bowls: driven by the original fill curve through the time warp
    to = Wv(t) if t <= cam2.T_SHRINK else 99
    for (n, lab), (a, b), (ca, cb) in zip(COUNTS, FILL, CLOSE):
        al = env(t, a - .04, cb + .35, .15, .3)
        if al > 0:
            fr = min(max(cam.ease_fill(Wv(t), Wv(a), Wv(b)) / 1.06, 0), 1)
            put(d, fmt(n * fr), 190, 'Black', 1400, al); put(d, lab, 46, 'Bold', 1630, al * .9)
    # tier 4: the count runs away; the final number lands with a punch
    if cam2.T_COUNT <= t < cam2.T_CUT:
        al = env(t, cam2.T_COUNT, cam2.T_CUT, .15, .05)
        if t < cam2.T_JUMP:
            k = (t - cam2.T_COUNT) / (cam2.T_JUMP - .15 - cam2.T_COUNT); k = min(max(k, 0), 1)
            v = math.exp(math.log(985.) + (math.log(1e9) - math.log(985.)) * k ** 1.6)
            s, sz = fmt(v), 190
        else:
            pk = min(max((t - cam2.T_JUMP) / .25, 0), 1); s, sz = '10,000,000,000', int(150 + 40 * (1 - pk) ** 2)
        put(d, s, sz, 'Black', 1400, al); put(d, 'SUNS FIT INSIDE STEPHENSON 2-18', 46, 'Bold', 1630, al * .9)
    return np.asarray(lay, np.float32) / 255

def finish(img):
    """anamorphic streak on highlights + a hair of chromatic fringing"""
    lum = img.mean(2)
    br = np.clip((lum - .8) * 3., 0, 1)[..., None] * img
    sm_ = np.asarray(Image.fromarray(np.clip(br * 255, 0, 255).astype(np.uint8)).resize((W // 4, H // 4), Image.BILINEAR), np.float32) / 255
    st = uniform_filter1d(uniform_filter1d(sm_, 70, axis=1), 5, axis=0)
    st = np.asarray(Image.fromarray(np.clip(st * 255, 0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC), np.float32) / 255
    img = img + st * np.array([.16, .2, .34], np.float32)
    img[..., 0] = np.roll(img[..., 0], 1, axis=1); img[..., 2] = np.roll(img[..., 2], -1, axis=1)
    return img

def plate2(O, i): return f'{O}/plates2/p{i:04d}.png'
def plate_file(O, t):
    kind, idx = cam2.plate_src(t)
    return comp.plate_path(O, idx) if kind == 'old' else plate2(O, idx)

def do_plates(O, part=0, parts=1):
    os.makedirs(f'{O}/plates2', exist_ok=True); jobs = []
    for i in range(part, NF2, parts):
        if cam2.plate_src(i / FPS)[0] != 'new': continue
        f, v = cam2.params(i / FPS); jobs.append(dict(out=plate2(O, i), w=W, h=H, f=f, v=v))
    json.dump(jobs, open(f'{O}/jobs2_{part}.json', 'w'))
    subprocess.run(['node', os.path.dirname(os.path.abspath(__file__)) + '/gl/render.mjs', f'{O}/jobs2_{part}.json'], check=True)

def do_frame(O, i):
    out = f'{O}/frames2/f{i:04d}.png'
    if os.path.exists(out): return
    t = i / FPS; f, v = cam2.params(t)
    pl = np.asarray(Image.open(plate_file(O, t)).convert('RGBA'), np.float32) / 255
    rgb, a = pl[..., :3], pl[..., 3]
    tsurf = np.where(a > 0, 2 ** (np.clip(a - .02, 0, 1) / .98 * 11.5) - 1, 1e9)
    cp, fw, rt, up, fl = basis(v, f)
    focus = float(np.linalg.norm(np.array(v['uCamT']) - cp))
    img = rgb + dust_layer(f['uT'], cp, fw, rt, up, fl, tsurf, focus, f['uRoll']) * .55
    img = finish(bloom(img))
    img += (np.random.default_rng(i).standard_normal((H, W, 1)) * .012).astype(np.float32)
    tl = text_layer(t); img = img * (1 - tl[..., 3:]) + tl[..., :3] * tl[..., 3:]
    Image.fromarray(np.clip(img * 255 + .5, 0, 255).astype(np.uint8)).save(out + '.tmp.png'); os.replace(out + '.tmp.png', out)

def do_frames(O, part=0, parts=1):
    os.makedirs(f'{O}/frames2', exist_ok=True)
    for i in range(part, NF2, parts):
        if os.path.exists(plate_file(O, i / FPS)): do_frame(O, i)

def events(O):
    """sound cues in NEW time. Fill landing times come from the original timeline through the inverse warp."""
    old = json.load(open(f'{O}/events.json'))
    ev = dict(dur=cam2.DUR2, hit=[Wi(h) for h in old['hit']], fall=Wi(old['fall']), waves=[[Wi(a), Wi(b)] for a, b in old['waves']], fills=[], t4=dict(
        shrink=cam2.T_SHRINK, count=cam2.T_COUNT, jump=cam2.T_JUMP, whip=cam2.T_WHIP, cut=cam2.T_CUT, prompt=cam2.T_PROMPT, loop=cam2.T_LOOP))
    for fl in old['fills']:
        ev['fills'].append(dict(n=fl['n'], t=[round(Wi(x), 4) for x in fl['t']], a=Wi(fl['a']), b=Wi(fl['b']), fall=round(.85 * (Wi(fl['b']) - Wi(fl['a'])) / (fl['b'] - fl['a']), 4)))
    json.dump(ev, open(f'{O}/events2.json', 'w'))

if __name__ == '__main__':
    cmd, O = sys.argv[1], sys.argv[2]
    part = int(sys.argv[3]) if len(sys.argv) > 3 else 0; parts = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    {'plates': lambda: do_plates(O, part, parts), 'frames': lambda: do_frames(O, part, parts), 'events': lambda: events(O)}[cmd]()
