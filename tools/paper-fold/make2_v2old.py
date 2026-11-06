"""Paper fold 103, v2 (35 s, ref layout, voiceover, real folding paper in a macro lens).
  python3 make2.py jobs OUT [frames]   -> OUT/jobs_*.json
  python3 make2.py comp OUT [frames]   -> OUT/frames
"""
import sys, os, json, math, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import make as mk
from make import font, draw_shadow_text, bigtext, fade, sstep, thick_text, flash, FPS, W, H, CREAM, RED

DUR = 37.0
NF = int(DUR * FPS)

# (t, n) anchors: the number word is spoken at that time (see vo timeline below)
NODES = [(0.4, 0.0), (5.2, 7.0), (7.7, 14.0), (10.4, 22.0), (12.8, 23.0), (15.4, 30.0), (18.1, 42.0), (20.5, 51.0), (23.25, 69.0), (25.7, 83.0), (28.3, 103.0), (60.0, 103.0)]

def n_of(t):
    if t <= NODES[0][0]: return 0.0
    for (t0, n0), (t1, n1) in zip(NODES, NODES[1:]):
        if t <= t1: return n0 + (n1 - n0) * (t - t0) / (t1 - t0)
    return 103.0

def t_of(n):
    for (t0, n0), (t1, n1) in zip(NODES, NODES[1:]):
        if n <= n1 and n1 > n0: return t0 + (t1 - t0) * (n - n0) / (n1 - n0)
    return NODES[-1][0]

# voiceover clips: name, start (s), file
VO = [('A', 0.20), ('B', 5.22), ('C', 7.63), ('D', 10.32), ('E', 12.70), ('F', 15.30), ('G', 17.99), ('H', 23.14), ('I', 25.62), ('J', 28.10), ('K', 32.64)]

# callouts: id, title, sub, fold at which it is passed, scene, dur
CALLS = [('mug', 'A COFFEE MUG', '9.5 cm', 10, 'G', 1.0), ('person', 'A PERSON', '1.65 m', 14, 'G', 1.5), ('hoop', 'BASKETBALL HOOP', '3.05 m', 15, 'G', 1.1),
         ('giraffe', 'A GIRAFFE', '5.5 m', 16, 'G', 1.1), ('liberty', 'STATUE OF LIBERTY', '93 m', 20, 'G', 1.4), ('eiffel', 'EIFFEL TOWER', '330 m', 22, 'G', 1.9),
         ('burj', 'BURJ KHALIFA', '828 m', 23, 'G', 2.2), ('everest', 'MOUNT EVEREST', '8,849 m', 27, 'G', 1.6), ('plane', 'AIRLINER', '11 km up', 27, 'G', 1.6),
         ('iss', 'SPACE STATION', '408 km up', 32, 'S', 1.3), ('moon', 'THE MOON', '384,400 km away', 42, 'S', 2.0), ('sun', 'THE SUN', '150 million km away', 51, 'S', 1.8),
         ('nep', 'NEPTUNE', '4.5 billion km away', 56, 'S', 1.4), ('prox', 'NEAREST STAR', '4.2 light-years away', 69, 'S', 2.0), ('mw', 'THE MILKY WAY', '100,000 light-years across', 83, 'S', 1.0),
         ('and', 'ANDROMEDA', '2.5 million light-years away', 88, 'S', 1.3)]

CAPS = [(0, "Every fold doubles the thickness."), (14, "14 folds: as tall as you."), (22, "22 folds: taller than the Eiffel Tower."),
        (23, "23 folds: taller than the Burj Khalifa."), (27, "27 folds: higher than Everest."), (30, "30 folds: it reaches space."),
        (42, "42 folds: past the Moon."), (51, "51 folds: past the Sun."), (56, "56 folds: past Neptune."), (69, "69 folds: past the nearest star."),
        (83, "83 folds: wider than our galaxy."), (88, "88 folds: past Andromeda."), (103, "103 folds: taller than the universe is wide.")]

def caption_for(f):
    c = CAPS[0][1]
    for a, tx in CAPS:
        if f >= a: c = tx
    return c

def layers_at(t):
    out = []
    if t < 4.65:
        out.append(('D', {'k': max(0.0, min(7.0, (n_of(t)))), 't': t}, 1.0))
    elif t < 5.2:
        a = sstep(4.65, 5.2, t)
        out += [('D', {'k': 7.0, 't': t}, 1 - a), ('G', {'n': 7.0, 't': t}, a)]
    elif t < 14.75:
        out.append(('G', {'n': n_of(t), 't': t}, 1.0))
    else:
        out.append(('S', {'n': n_of(t), 't': t, 'push': 0.0 if t < 28.3 else 0.03 * min(1, (t - 28.3) / 3)}, 1.0))
    if t >= 5.0 and t < 28.9:
        out.append(('L', {'n': n_of(t), 't': t}, 1.0))
    return out

def frame_state(i):
    t = i / FPS; L = layers_at(t)
    main = [x for x in L if x[0] != 'L'][-1]
    nn = n_of(t)
    f = int(math.floor(main[1].get('k', nn) + 1e-6)) if main[0] == 'D' else min(103, int(math.floor(nn + 1e-6)))
    return t, L, f, nn, main[0]

# ---------------------------------------------------------------- drawing
def layers_text(f):
    v = 2 ** f
    if v < 1e6: return f"{v:,} LAYERS"
    e = int(math.floor(math.log10(v))); m = v / 10 ** e
    return f"{m:.1f} x 10^{e} LAYERS"

def hud_items(t, f):
    x0 = 84; ycap = 250
    fc = font('InterDisplay-SemiBold.otf', 42); fl = font('InterDisplay-Bold.otf', 30)
    fn = font('InterDisplay-Black.otf', 260); fv = font('InterDisplay-ExtraBold.otf', 74)
    items = []
    if t < 5.1:
        items.append(((x0, ycap), "What if you folded a sheet of paper in half", fc, CREAM, 'la'))
        items.append(((x0, ycap + 54), "103 times?", font('InterDisplay-Bold.otf', 46), RED, 'la'))
        yb = ycap + 70
    else:
        items.append(((x0, ycap), caption_for(f), fc, CREAM, 'la')); yb = ycap
    items.append(((x0 + 6, yb + 110), 'FOLDS', fl, RED, 'la'))
    items.append(((x0, yb + 132), str(f), fn, CREAM, 'la'))
    items.append(((x0 + 6, yb + 396), 'THICKNESS', fl, RED, 'la'))
    items.append(((x0, yb + 434), thick_text(f), fv, CREAM, 'la'))
    return items

def callouts(im, t, marks, scene):
    for cid, ti, su, pn, sc, dur in CALLS:
        if sc != scene: continue
        m = next((q for q in marks if q['id'] == cid), None)
        if not m or not m['vis']: continue
        tp = t_of(pn); al = fade(t, tp, tp + dur, 0.18, 0.3)
        if al <= 0.01: continue
        x, y = m['x'], m['y']
        x = max(200, min(W - 330, x)); y = max(800, min(1090 if scene == 'S' else H - 420, y))
        fl = font('InterDisplay-Bold.otf', 38); fs = font('InterDisplay-SemiBold.otf', 34)
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        side = -1 if x > W * 0.55 else 1; lx = x + side * 70; anc = 'rs' if side < 0 else 'ls'
        d.line([(x, y), (lx, y)], fill=CREAM + (int(230 * al),), width=3)
        d.ellipse([x - 8, y - 8, x + 8, y + 8], fill=RED + (int(255 * al),))
        sh = Image.new('L', im.size, 0); sd = ImageDraw.Draw(sh)
        sd.text((lx + side * 14, y - 14), ti, font=fl, fill=255, anchor=anc); sd.text((lx + side * 14, y + 44), su, font=fs, fill=255, anchor=anc)
        sh = sh.filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(min(255, v * 1.4 * al))); im.paste((10, 6, 4), (0, 0), sh)
        d.text((lx + side * 14, y - 14), ti, font=fl, fill=CREAM + (int(255 * al),), anchor=anc)
        d.text((lx + side * 14, y + 44), su, font=fs, fill=CREAM + (int(235 * al),), anchor=anc)
        im.paste(lay, (0, 0), lay)

LENS_D = 340; LENS_X = 700; LENS_Y = 1190
def lens(im, lim, t, f):
    a = sstep(5.0, 5.5, t) * (1 - sstep(27.8, 28.6, t))
    if a <= 0.01: return
    s = LENS_D
    l = lim.convert('RGB').resize((s, s), Image.LANCZOS)
    mask = Image.new('L', (s * 3, s * 3), 0); ImageDraw.Draw(mask).ellipse([0, 0, s * 3 - 1, s * 3 - 1], fill=int(255 * a)); mask = mask.resize((s, s), Image.LANCZOS)
    sh = Image.new('L', im.size, 0); ImageDraw.Draw(sh).ellipse([LENS_X + 8, LENS_Y + 14, LENS_X + s + 8, LENS_Y + s + 14], fill=int(150 * a)); sh = sh.filter(ImageFilter.GaussianBlur(14)); im.paste((8, 5, 4), (0, 0), sh)
    im.paste(l, (LENS_X, LENS_Y), mask)
    ring = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse([LENS_X, LENS_Y, LENS_X + s, LENS_Y + s], outline=CREAM + (int(235 * a),), width=5); im.paste(ring, (0, 0), ring)
    items = [((LENS_X + s / 2, LENS_Y + s + 34), layers_text(f), font('InterDisplay-Bold.otf', 30), CREAM, 'mm')]
    draw_shadow_text(im, items, mul=a)

def overlay(im, lim, t, f, marks, scene):
    draw_shadow_text(im, hud_items(t, f))
    callouts(im, t, marks, scene)
    if lim is not None: lens(im, lim, t, f)
    if 15.3 <= t < 16.8:
        bigtext(im, ['30 FOLDS.', 'IT REACHES SPACE.'], 1480, 84, mul=fade(t, 15.3, 16.8, 0.08, 0.3), scale=mk.pulse(t, 15.3))
    if 32.7 <= t < 35.3:
        bigtext(im, ['REAL RECORD:', '12 FOLDS.'], 1330, 104, mul=fade(t, 32.7, 35.3, 0.25, 0.3), sub='Guinness: 1,219 m of tissue paper')
    if 35.4 <= t <= DUR:
        bigtext(im, ['HOW MANY FOLDS TO PASS', "YOUR CITY'S TALLEST", 'BUILDING?'], 1260, 62, mul=fade(t, 35.4, DUR + 0.5, 0.25, 0.1), sub='Comment it.  Follow @slowlighttv')

def compose_frame(i, layerdir, marks_by_file):
    t, L, f, nn, sc = frame_state(i)
    main = [(li, x) for li, x in enumerate(L) if x[0] != 'L']
    im = None
    for li, (name, p, al) in main:
        l = Image.open(f"{layerdir}/f{i:04d}_{li}.jpg").convert('RGB')
        im = l if im is None else Image.blend(im, l, al)
    lim = None
    for li, (name, p, al) in enumerate(L):
        if name == 'L': lim = Image.open(f"{layerdir}/f{i:04d}_{li}.jpg")
    lastli = main[-1][0]; marks = marks_by_file.get(f"{layerdir}/f{i:04d}_{lastli}.jpg", [])
    wa = 0.0
    if 14.2 <= t < 15.4: wa = sstep(14.2, 14.75, t) if t < 14.78 else 1 - sstep(14.78, 15.4, t)
    if wa > 0: im = flash(im, wa * 0.97, (255, 228, 214))
    for t0, dur, col, amp in [(15.3, 0.22, (255, 245, 230), 0.4), (28.3, 0.5, (255, 245, 230), 0.6)]:
        if t0 <= t < t0 + dur: im = flash(im, amp * (1 - (t - t0) / dur) ** 2, col)
    overlay(im, lim, t, f, marks, sc)
    return im

if __name__ == '__main__':
    cmd, out = sys.argv[1], sys.argv[2]
    os.makedirs(out + '/layers', exist_ok=True); os.makedirs(out + '/frames', exist_ok=True)
    only = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else range(NF)
    if cmd == 'jobs':
        nw = int(os.environ.get('WORKERS', '3')); jobs = [[] for _ in range(nw)]; c = 0
        for i in only:
            t, L, f, nn, sc = frame_state(i)
            for li, (name, p, al) in enumerate(L):
                jobs[c % nw].append({'file': f"{out}/layers/f{i:04d}_{li}.jpg", 'name': name, 'p': p}); c += 1
        for w, j in enumerate(jobs): json.dump(j, open(f"{out}/jobs_{w}.json", 'w'))
        print('jobs', sum(len(j) for j in jobs))
    elif cmd == 'comp':
        marks = {}
        for fnm in glob.glob(out + '/jobs_*.out.json'):
            for r in json.load(open(fnm)): marks[r['file']] = r['marks']
        for i in only:
            compose_frame(i, out + '/layers', marks).save(f"{out}/frames/{i:04d}.jpg", quality=93)
        print('composed', len(list(only)))
