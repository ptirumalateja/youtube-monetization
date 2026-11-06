"""Paper fold 103, v2 (35 s, ref layout, voiceover, real folding paper in a macro lens).
  python3 make2.py jobs OUT [frames]   -> OUT/jobs_*.json
  python3 make2.py comp OUT [frames]   -> OUT/frames
"""
import sys, os, json, math, glob
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import make as mk
from make import font, draw_shadow_text, bigtext, fade, sstep, thick_text, flash, FPS, W, H, CREAM, RED


import tl4
DUR = tl4.DUR
NF = int(DUR * FPS)
NODES = [(b, a) for a, b in tl4.LAND[:-1]] + [(999.0, 103.0)]
NODES = [(b, a) for a, b in tl4.LAND if a <= 103] + [(999.0, 103.0)]

def n_of(t):
    """folds LANDED by time t (continuous, linear between landings)"""
    if t <= NODES[0][0]: return 0.0
    for (t0, n0), (t1, n1) in zip(NODES, NODES[1:]):
        if t <= t1: return n0 + (n1 - n0) * (t - t0) / (t1 - t0)
    return 103.0

def t_of(n):
    for (t0, n0), (t1, n1) in zip(NODES, NODES[1:]):
        if n <= n1 and n1 > n0: return t0 + (t1 - t0) * (n - n0) / (n1 - n0)
    return NODES[-1][0]

VO = [(c, tl4.P[c]) for c in tl4.P]
_L10 = t_of(10); _L30 = t_of(30); _P1 = tl4.P['S1']; _P11 = tl4.P['S11']
_RT = {4.65: _L10 - 0.5, 5.2: _L10, 4.9: _L10 - 0.25, 5.4: _L10 + 0.2, 5.1: _P1, 14.2: _L30 - 1.2, 14.75: _L30 - 0.65, 14.78: _L30 - 0.62, 15.4: _L30, 15.3: _L30,
       16.8: _L30 + 1.5, 28.3: t_of(103), 32.7: _P11, 35.3: tl4.END_VO, 35.4: tl4.END_VO + 0.1, 37.0: tl4.DUR}
def RT(t): return _RT[t]

# callouts: id, title, sub, fold at which it is passed, scene, dur
CALLS = [('mug', 'A COFFEE MUG', '9.5 cm', 10, 'G', 1.0), ('person', 'A PERSON', '1.65 m', 14, 'G', 1.5), ('hoop', 'BASKETBALL HOOP', '3.05 m', 15, 'G', 1.1),
         ('giraffe', 'A GIRAFFE', '5.5 m', 16, 'G', 1.1), ('liberty', 'STATUE OF LIBERTY', '93 m', 20, 'G', 1.4), ('eiffel', 'EIFFEL TOWER', '330 m', 22, 'G', 1.9),
         ('burj', 'BURJ KHALIFA', '828 m', 23, 'G', 2.2), ('everest', 'MOUNT EVEREST', '8,849 m', 27, 'G', 1.6), ('plane', 'AIRLINER', '11 km up', 27, 'G', 1.6),
         ('iss', 'SPACE STATION', '408 km up', 32, 'S', 0.9), ('moon', 'THE MOON', '384,400 km away', 42, 'S', 1.5), ('sun', 'THE SUN', '150 million km away', 51, 'S', 1.5),
         ('nep', 'NEPTUNE', '4.5 billion km away', 56, 'S', 1.0), ('prox', 'NEAREST STAR', '4.2 light-years away', 69, 'S', 1.6), ('mw', 'THE MILKY WAY', '100,000 light-years across', 83, 'S', 1.2),
         ('and', 'ANDROMEDA', '2.5 million light-years away', 88, 'S', 1.0)]

CAPS = [(0, "Every fold doubles the thickness."), (14, "14 folds: as tall as you."), (22, "22 folds: taller than the Eiffel Tower."),
        (23, "23 folds: taller than the Burj Khalifa."), (27, "27 folds: higher than Everest."), (30, "30 folds: it reaches space."),
        (42, "42 folds: past the Moon."), (51, "51 folds: past the Sun."), (56, "56 folds: past Neptune."), (69, "69 folds: past the nearest star."),
        (83, "83 folds: wider than our galaxy."), (88, "88 folds: past Andromeda."), (103, "103 folds: taller than the universe is wide.")]

def caption_for(f):
    c = CAPS[0][1]
    for a, tx in CAPS:
        if f >= a: c = tx
    return c

SW_MAX = 0.36
def cam_state(t):
    """k folds done, swing progress u of the NEXT fold (it lands exactly at its landing time), hinge angle, camera n"""
    n = n_of(t)
    if n >= 103 - 1e-9: return 103, 0.0, -90.0, 103.0
    j = int(math.floor(n + 1e-9)) + 1; Lj = t_of(j); Lp = t_of(j - 1)
    sw = min(SW_MAX, 0.85 * (Lj - Lp)); u = (t - (Lj - sw)) / sw
    if u <= 0: return j - 1, 0.0, -90.0, float(j - 1)
    x = max(0.0, min(1.0, u)); E = x * x * (3 - 2 * x)
    th = -90 + 180 * E; ec = max(0.0, math.sin(math.radians(th)))
    return j - 1, E, th, (j - 1) + math.log2(1 + ec)

def layers_at(t):
    out = []
    if t < RT(4.65):
        cs = cam_state(t); out.append(('D', {'k': cs[0] + cs[1], 't': t}, 1.0))
    elif t < RT(5.2):
        a = sstep(RT(4.65), RT(5.2), t)
        out += [('D', {'k': 10.0, 't': t}, 1 - a), ('G', {'n': cam_state(t)[3], 't': t}, a)]
    elif t < RT(14.75):
        out.append(('G', {'n': cam_state(t)[3], 't': t}, 1.0))
    else:
        out.append(('S', {'n': cam_state(t)[3], 't': t, 'push': 0.0 if t < RT(28.3) else 0.03 * min(1, (t - RT(28.3)) / 3)}, 1.0))
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
    if t < RT(5.1):
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

PAPER = (247, 241, 228); EDGE = (150, 128, 96)
def hinge(im, t, marks, scene):
    """draw the paper stack column as a real hinge fold: top copy swings 180 deg around the stack's top, thin arc trail, orange tip dot"""
    if scene == 'D' or t < RT(4.9): return
    a = sstep(RT(4.9), RT(5.4), t)
    mb = next((q for q in marks if q['id'] == 'base'), None); mt = next((q for q in marks if q['id'] == 'top'), None)
    if not mb or not mt: return
    k, u, th, nc = cam_state(t)
    ec = max(0.0, math.sin(math.radians(th)))
    S = 2; w, h = im.size
    xb, yb, yt = mb['x'] * S, mb['y'] * S, mt['y'] * S
    Hk = (yb - yt) / (1 + ec)
    if Hk < 6: return
    BW = 26 * S
    lay = Image.new('RGBA', (w * S, h * S), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    nl = min(2 ** k, 26)
    def bar(p0, p1, n_ticks):
        dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy) or 1; nx, ny = -dy / L * BW / 2, dx / L * BW / 2
        quad = [(p0[0] + nx, p0[1] + ny), (p1[0] + nx, p1[1] + ny), (p1[0] - nx, p1[1] - ny), (p0[0] - nx, p0[1] - ny)]
        d.polygon(quad, fill=PAPER + (255,), outline=EDGE + (255,), width=2)
        for i in range(1, n_ticks):
            f = i / n_ticks; cx, cy = p0[0] + dx * f, p0[1] + dy * f
            d.line([(cx + nx, cy + ny), (cx - nx, cy - ny)], fill=(205, 186, 156, 255), width=2)
    # lower stack (stays put)
    ptop = (xb, yb - Hk)
    bar((xb, yb), ptop, nl)
    # swinging copy, pivot at the top of the stack
    r = Hk; rad = math.radians(th); tip = (ptop[0] - r * math.cos(rad), ptop[1] - r * math.sin(rad))
    if u > 0.001 and k < 103:
        # arc trail
        pts = []
        for ang in range(-90, int(th) + 1, 3):
            rr = math.radians(ang); pts.append((ptop[0] - r * math.cos(rr), ptop[1] - r * math.sin(rr)))
        if len(pts) > 1: d.line(pts, fill=(255, 255, 255, 235), width=3 * S // 2 + 1)
        bar(ptop, tip, nl)
        d.ellipse([tip[0] - 7 * S, tip[1] - 7 * S, tip[0] + 7 * S, tip[1] + 7 * S], fill=RED + (255,))
    elif k < 103:
        pass
    d.ellipse([ptop[0] - 5 * S, ptop[1] - 5 * S, ptop[0] + 5 * S, ptop[1] + 5 * S], fill=(90, 70, 50, 255))
    lay = lay.resize((w, h), Image.LANCZOS)
    sh = lay.split()[3].filter(ImageFilter.GaussianBlur(9)).point(lambda v: int(v * 0.55 * a))
    im.paste((12, 8, 6), (6, 8), sh)
    al = lay.split()[3].point(lambda v: int(v * a)); lay.putalpha(al); im.paste(lay, (0, 0), lay)

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
    if RT(15.3) <= t < RT(16.8):
        bigtext(im, ['30 FOLDS.', 'IT REACHES SPACE.'], 1480, 84, mul=fade(t, RT(15.3), RT(16.8), 0.08, 0.3), scale=mk.pulse(t, RT(15.3)))
    if RT(32.7) <= t < RT(35.3):
        bigtext(im, ['REAL RECORD:', '12 FOLDS.'], 1330, 104, mul=fade(t, RT(32.7), RT(35.3), 0.25, 0.3), sub='Guinness: 1,219 m of tissue paper')
    if RT(35.4) <= t <= DUR:
        bigtext(im, ['HOW MANY FOLDS TO PASS', "YOUR CITY'S TALLEST", 'BUILDING?'], 1260, 62, mul=fade(t, RT(35.4), DUR + 0.5, 0.25, 0.1), sub='Comment it.  Follow @slowlighttv')

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
    if RT(14.2) <= t < RT(15.4): wa = sstep(RT(14.2), RT(14.75), t) if t < RT(14.78) else 1 - sstep(RT(14.78), RT(15.4), t)
    if wa > 0: im = flash(im, wa * 0.97, (255, 228, 214))
    for t0, dur, col, amp in [(RT(15.3), 0.22, (255, 245, 230), 0.4), (RT(28.3), 0.5, (255, 245, 230), 0.6)]:
        if t0 <= t < t0 + dur: im = flash(im, amp * (1 - (t - t0) / dur) ** 2, col)
    hinge(im, t, marks, sc)
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
