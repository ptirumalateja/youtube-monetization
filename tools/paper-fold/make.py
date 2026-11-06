"""Paper fold 103: timeline, job split, GL render (rshoot.js), HUD composite, mux.
  python3 make.py jobs  OUT   -> writes OUT/jobs_*.json  (per worker)
  python3 make.py comp  OUT   -> composites frames from OUT/layers into OUT/frames
  python3 make.py still OUT t -> composite one frame (needs its layers rendered: see 'jobs' with only=t)
"""
import sys, os, json, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
DUR = 31.0
NF = int(DUR * FPS)
FD = '/usr/share/fonts/opentype/inter/'
CREAM = (246, 239, 226); RED = (232, 88, 60)

NODES = [(5.0, 7), (9.5, 22), (11.0, 26.5), (12.3, 30), (14.3, 42), (16.3, 51), (17.3, 56), (19.0, 69),
         (21.3, 83), (22.8, 88), (24.0, 95), (25.6, 103), (60, 103)]

def n_of(t):
    if t <= NODES[0][0]: return 7.0
    for (t0, n0), (t1, n1) in zip(NODES, NODES[1:]):
        if t <= t1: return n0 + (n1 - n0) * (t - t0) / (t1 - t0)
    return 103.0

def k_of(t):  # desk fold progress 0..7 over 2.0 -> 4.9 s
    return max(0.0, min(7.0, (t - 2.0) / (4.9 - 2.0) * 7.0))

def sstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a))); return t * t * (3 - 2 * t)

def layers_at(t):
    """-> list of (scene, params, alpha)"""
    if t < 2.0:
        return [('S', {'n': 42.0, 't': t, 'push': -0.0 + 0.05 * (t / 2.0)}, 1.0)]
    if t < 4.7:
        return [('D', {'k': k_of(t), 't': t}, 1.0)]
    if t < 5.25:
        a = sstep(4.7, 5.25, t)
        return [('D', {'k': 7.0, 't': t}, 1 - a), ('G', {'n': 7.0, 't': t}, a)]
    if t < 11.25:
        return [('G', {'n': n_of(t), 't': t}, 1.0)]
    return [('S', {'n': n_of(t), 't': t, 'push': 0.0 if t < 25.6 else 0.04 * min(1, (t - 25.6) / 3)}, 1.0)]

# ------------------------------------------------------------------ number formatting
def sig3(x):
    s = f"{x:.3g}"
    if 'e' in s: s = f"{x:.0f}"
    return s

def thick_text(f):
    m = 1e-4 * 2 ** f
    if m < 0.01: return f"{sig3(m*1000)} mm"
    if m < 0.5: return f"{sig3(m*100)} cm"
    if m < 1000: return f"{sig3(m)} m"
    km = m / 1000
    if km < 1e6: return f"{km:,.0f} km" if km >= 1000 else f"{sig3(km)} km"
    if km < 1e9: return f"{sig3(km/1e6)} million km"
    ly = m / 9.4607e15
    if ly < 0.1: return f"{sig3(km/1e9)} billion km"
    if ly < 1000: return f"{sig3(ly)} light-years"
    if ly < 1e6: return f"{sig3(ly/1e3)} thousand light-years"
    if ly < 1e9: return f"{sig3(ly/1e6)} million light-years"
    return f"{sig3(ly/1e9)} billion light-years"

CAPS = [(0, "Every fold doubles the thickness."), (7, "7 folds: as thick as your notebook."), (10, "10 folds: as thick as your hand."), (12, "12 folds: knee high."), (13, "13 folds: waist high."), (14, "14 folds: as tall as you."),
        (20, "20 folds: taller than Qutub Minar."), (22, "22 folds: taller than the Statue of Unity."), (27, "27 folds: higher than Everest."),
        (30, "30 folds: it leaves Earth."), (42, "42 folds: past the Moon."), (51, "51 folds: past the Sun."), (56, "56 folds: past Neptune."),
        (69, "69 folds: past the nearest star."), (83, "83 folds: wider than our galaxy."), (88, "88 folds: past Andromeda."),
        (95, "95 folds: across the cosmic web."), (103, "103 folds: taller than the whole universe.")]

def caption_for(f):
    c = CAPS[0][1]
    for a, tx in CAPS:
        if f >= a: c = tx
    return c

# callouts: id, title, sub, n window (start, end) in folds on the layer scene
CALLS = [('person', 'A PERSON', '1.7 m', 14, 16.2, 'G'), ('qutub', 'QUTUB MINAR', '72.5 m', 20, 23, 'G'),
         ('unity', 'STATUE OF UNITY', '182 m, 240 m with base', 22, 25, 'G'),
         ('moon', 'THE MOON', '384,400 km away', 41.2, 48, 'S'), ('sun', 'THE SUN', '150 million km away', 50.2, 58, 'S'),
         ('nep', 'NEPTUNE', '4.5 billion km away', 55.2, 64, 'S'), ('prox', 'NEAREST STAR', '4.2 light-years away', 68.2, 77, 'S'),
         ('mw', 'THE MILKY WAY', '100,000 light-years across', 82.2, 88.4, 'S'), ('and', 'ANDROMEDA', '2.5 million light-years away', 87.6, 94, 'S'),
         ('uni', 'OBSERVABLE UNIVERSE', '93 billion light-years across', 102.4, 104, 'S')]

_f = {}
def font(name, size):
    k = (name, size)
    if k not in _f: _f[k] = ImageFont.truetype(FD + name, size)
    return _f[k]

def draw_shadow_text(im, items, blur=9, alpha=170, mul=1.0):
    """items: list of (xy, text, font, fill, anchor). Draws soft shadow then text, text opacity mul."""
    sh = Image.new('L', im.size, 0); d = ImageDraw.Draw(sh)
    for xy, tx, fo, fi, an in items: d.text(xy, tx, font=fo, fill=255, anchor=an)
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha / 255 * mul))
    im.paste((10, 6, 4), (0, 0), sh)
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for xy, tx, fo, fi, an in items: d.text(xy, tx, font=fo, fill=fi + (int(255 * mul),), anchor=an)
    im.paste(lay, (0, 0), lay)

def hud(im, t, f, marks, scene, mode):
    s = 1.0
    x0 = 84
    items = []
    fc = font('InterDisplay-SemiBold.otf', 42); fl = font('InterDisplay-Bold.otf', 30)
    fn = font('InterDisplay-Black.otf', 260); fv = font('InterDisplay-ExtraBold.otf', 74)
    ycap = 250
    cap = caption_for(f)
    items.append(((x0, ycap), cap, fc, CREAM, 'la'))
    items.append(((x0 + 6, ycap + 110), 'FOLDS', fl, RED, 'la'))
    items.append(((x0, ycap + 132), str(f), fn, CREAM, 'la'))
    items.append(((x0 + 6, ycap + 396), 'THICKNESS', fl, RED, 'la'))
    items.append(((x0, ycap + 434), thick_text(f), fv, CREAM, 'la'))
    return items

def bigtext(im, lines, cy, size, mul=1.0, scale=1.0, sub=None):
    sc = Image.new('L', im.size, 0); ImageDraw.Draw(sc).rounded_rectangle([40, cy - size * len(lines) * 0.62 - 30, W - 40, cy + size * len(lines) * 0.62 + (110 if sub else 40)], radius=60, fill=int(120 * mul))
    sc = sc.filter(ImageFilter.GaussianBlur(40)); im.paste((22, 14, 28), (0, 0), sc)
    fo = font('InterDisplay-Black.otf', int(size * scale)); items = []
    lh = int(size * scale * 1.04)
    y = cy - lh * (len(lines) - 1) / 2
    for ln in lines:
        items.append(((W / 2, y), ln, fo, CREAM, 'mm')); y += lh
    if sub:
        items.append(((W / 2, y + 30 * scale), sub, font('InterDisplay-SemiBold.otf', int(40 * scale)), CREAM, 'mm'))
    draw_shadow_text(im, items, blur=14, alpha=200, mul=mul)

def pulse(t, t0, dur=0.28):  # scale punch 1.18 -> 1
    u = (t - t0) / dur
    return 1.0 if u >= 1 or u < 0 else 1.0 + 0.18 * (1 - u) ** 2

def fade(t, a, b, fi=0.18, fo=0.25):
    if t < a or t > b: return 0.0
    return min(1.0, (t - a) / fi, (b - t) / fo)

def callouts(im, t, nf, marks, scene):
    items_all = []
    dr = None
    for cid, ti, su, a, b, sc in CALLS:
        if sc != scene: continue
        m = next((q for q in marks if q['id'] == cid), None)
        if not m or not m['vis']: continue
        al = sstep(a, a + 0.5, nf) * (1 - sstep(b - 0.6, b, nf))
        if cid == 'uni': al = fade(t, 25.75, 27.35, 0.25, 0.3)
        if al <= 0.01: continue
        x, y = m['x'], m['y']
        if cid == 'unity': y -= 0
        x = max(190, min(W - 110, x)); y = max(820 if scene == 'S' else 420, min(H - 260, y))
        fl = font('InterDisplay-Bold.otf', 38); fs = font('InterDisplay-SemiBold.otf', 34)
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        side = -1 if x > W * 0.45 else 1
        lx = x + side * 70
        d.line([(x, y), (lx, y)], fill=CREAM + (int(230 * al),), width=3)
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=RED + (int(255 * al),))
        sh = Image.new('L', im.size, 0); sd = ImageDraw.Draw(sh)
        anc = 'rs' if side < 0 else 'ls'
        sd.text((lx + side * 14, y - 14), ti, font=fl, fill=255, anchor=anc); sd.text((lx + side * 14, y + 44), su, font=fs, fill=255, anchor=anc)
        sh = sh.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(min(255, v * 1.4 * al))); im.paste((10, 6, 4), (0, 0), sh)
        d.text((lx + side * 14, y - 14), ti, font=fl, fill=CREAM + (int(255 * al),), anchor=anc)
        d.text((lx + side * 14, y + 44), su, font=fs, fill=CREAM + (int(235 * al),), anchor=anc)
        im.paste(lay, (0, 0), lay)

def overlay_frame(im, t, f, nf, marks, scene):
    # hook
    if t < 2.0:
        al = min(1.0, t / 0.15) * (1 if t < 1.85 else max(0.0, (2.0 - t) / 0.15))
        bigtext(im, ['THIS IS ONE', 'NOTEBOOK PAGE.'], 470, 104, mul=1.0, scale=pulse(t, 0.0, 0.3))
        draw_shadow_text(im, [((W / 2, 690), 'folded 42 times', font('InterDisplay-SemiBold.otf', 46), CREAM, 'mm')], mul=min(1, max(0, (t - 0.5) / 0.3)))
        return
    # regular HUD (hide during whiteout peak? keep)
    items = hud(im, t, f, marks, scene, None)
    draw_shadow_text(im, items)
    callouts(im, t, nf, marks, scene)
    # rehook hits
    if 12.1 <= t < 13.7:
        bigtext(im, ['30 FOLDS.', 'IT LEAVES EARTH.'], 1330, 96, mul=fade(t, 12.1, 13.7, 0.08, 0.3), scale=pulse(t, 12.1))
    if 19.0 <= t < 20.7:
        bigtext(im, ['69 FOLDS.', 'PAST THE NEAREST STAR.'], 1330, 84, mul=fade(t, 19.0, 20.7, 0.08, 0.3), scale=pulse(t, 19.0))
    if 27.5 <= t < 29.3:
        bigtext(im, ['REAL RECORD:', '12 FOLDS.'], 1330, 104, mul=fade(t, 27.5, 29.3, 0.25, 0.3), sub='Guinness: 1,219 m of tissue paper')
    if 29.4 <= t <= DUR:
        bigtext(im, ['HOW MANY FOLDS TO PASS', "YOUR CITY'S TALLEST", 'BUILDING?'], 1260, 62, mul=fade(t, 29.4, DUR + 0.5, 0.25, 0.1),
                sub='Comment it.  Follow @slowlighttv')

def flash(im, a, col=(255, 236, 200)):
    if a <= 0.003: return im
    return Image.blend(im, Image.new('RGB', im.size, col), min(1, a))

def frame_state(i):
    t = i / FPS
    L = layers_at(t)
    top = L[-1]
    if top[0] == 'D': f = int(math.floor(top[1]['k'] + 1e-6)); nf = f
    else: f = min(103, int(math.floor(top[1]['n'] + 1e-6))); nf = top[1]['n']
    return t, L, f, nf, top[0]

def whiteout_a(t):
    return sstep(10.6, 11.2, t) * (1 - sstep(11.2, 12.0, t)) if t < 11.2 else (1 - sstep(11.25, 12.0, t))

def compose_frame(i, outdir, layerdir, marks_by_file):
    t, L, f, nf, sc = frame_state(i)
    im = None
    for li, (name, p, al) in enumerate(L):
        fn = f"{layerdir}/f{i:04d}_{li}.jpg"
        l = Image.open(fn).convert('RGB')
        if im is None: im = l
        else: im = Image.blend(im, l, al)
    marks = marks_by_file.get(f"{layerdir}/f{i:04d}_{len(L)-1}.jpg", [])
    # whiteout through the clouds
    wa = 0.0
    if 10.5 <= t < 12.0:
        wa = sstep(10.5, 11.15, t) if t < 11.2 else 1 - sstep(11.2, 12.0, t)
    if wa > 0: im = flash(im, wa * 0.97, (255, 228, 214))
    # cut flash at 2.0 and hits
    for t0, dur, col, amp in [(2.0, 0.18, (255, 240, 215), 0.6), (12.3, 0.22, (255, 245, 230), 0.45), (19.0, 0.22, (255, 245, 230), 0.4), (25.6, 0.5, (255, 245, 230), 0.7)]:
        if t0 <= t < t0 + dur: im = flash(im, amp * (1 - (t - t0) / dur) ** 2, col)
    overlay_frame(im, t, f, nf, marks, sc)
    # fade out at the very end
    if t > DUR - 0.25: im = Image.blend(im, Image.new('RGB', im.size, (20, 14, 12)), (t - (DUR - 0.25)) / 0.25 * 0.0)
    return im

if __name__ == '__main__':
    cmd, out = sys.argv[1], sys.argv[2]
    os.makedirs(out + '/layers', exist_ok=True); os.makedirs(out + '/frames', exist_ok=True)
    if cmd == 'jobs':
        only = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else range(NF)
        nw = int(os.environ.get('WORKERS', '3')); jobs = [[] for _ in range(nw)]
        for c, i in enumerate(only):
            t, L, f, nf, sc = frame_state(i)
            for li, (name, p, al) in enumerate(L):
                jobs[c % nw].append({'file': f"{out}/layers/f{i:04d}_{li}.jpg", 'name': name, 'p': p})
        for w, j in enumerate(jobs): json.dump(j, open(f"{out}/jobs_{w}.json", 'w'))
        print('jobs', sum(len(j) for j in jobs))
    elif cmd == 'comp':
        marks = {}
        import glob
        for fnm in glob.glob(out + '/jobs_*.out.json'):
            for r in json.load(open(fnm)): marks[r['file']] = r['marks']
        only = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else range(NF)
        for i in only:
            im = compose_frame(i, out, out + '/layers', marks)
            im.save(f"{out}/frames/{i:04d}.jpg", quality=93)
        print('composed', len(list(only)))
