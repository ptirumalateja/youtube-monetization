"""v2 graphics: one look per radar beat (radio chain, altitude waterfall, redacted track log) and the drawn
right-hand panels for the split screens. All drawn here, nothing from third-party media."""
import math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
from gfx import W, H, CREAM, RED, NAVY, TEAL, font, glow, shadow_text, clamp, ease, eout

def jet_poly(cx, cy, s, ang):
    """F/A-18-like planform, top view, as a polygon (nose up at ang=0)."""
    pts = [(0, -1.0), (.07, -.75), (.09, -.25), (.55, .1), (.55, .2), (.12, .12), (.1, .45), (.3, .62), (.3, .7), (.06, .68),
           (0, .72)]
    pts = pts + [(-x, y) for x, y in reversed(pts[1:-1])]
    c, sn = math.cos(ang), math.sin(ang)
    return [(cx + s * (x * c - y * sn), cy + s * (x * sn + y * c)) for x, y in pts]

AMBER = (255, 176, 70)
DIM = (120, 128, 140)

def _dots(d, w, h, ox=0, col=(18, 28, 46), g=34, x0=0):
    for y in range(0, h, g):
        for x in range(int(ox) % g, w, g): d.ellipse([x0 + x - 2, y - 2, x0 + x + 2, y + 2], fill=col)

def _box(L, xy, w, h, title, sub, a, col=CREAM, sub_col=DIM):
    d = ImageDraw.Draw(L); x, y = xy
    d.rounded_rectangle([x - w / 2, y - h / 2, x + w / 2, y + h / 2], 10, outline=col + (int(255 * a),), width=3, fill=(12, 18, 30, int(230 * a)))
    d.text((x, y - 14), title, font=font('monob', 30), fill=col + (int(255 * a),), anchor='mm')
    d.text((x, y + 24), sub, font=font('mono', 22), fill=sub_col + (int(255 * a),), anchor='mm')

def chain_frame(t, d, marks):
    """60 miles, where the number came from: ship radar -> controller -> radio -> pilot; then what exists and what doesn't.
    marks = (have, dont) local times for the two bottom rows."""
    im = Image.new('RGB', (W, H), NAVY); dr = ImageDraw.Draw(im)
    _dots(dr, W, H, -20 * t / d)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    nodes = [(330, 'SPY-1 RADAR', 'USS PRINCETON'), (790, 'CONTROLLER', 'READS THE SCOPE'), (1250, 'RADIO', 'VOICE ONLY'),
             (1650, 'FRAVOR’S JET', 'HEARS “60 MILES”')]
    y = 400
    for i, (x, ti, su) in enumerate(nodes):
        a = clamp((t - .3 - i * .55) / .35)
        if a <= 0: continue
        if i:
            px = nodes[i - 1][0]
            seg = eout((t - .3 - i * .55) / .5)
            ld.line([(px + 175, y), (px + 175 + (x - px - 350) * seg, y)], fill=CREAM + (int(200 * a),), width=3)
            if seg > .95: ld.polygon([(x - 175, y), (x - 195, y - 10), (x - 195, y + 10)], fill=CREAM + (int(220 * a),))
        if i == 2:   # radio waves
            for k in range(3):
                r = 40 + ((t * 60 + k * 30) % 90)
                ld.arc([x - r, y - 120 - r * .5, x + r, y - 120 + r * .5], 200, 340, fill=TEAL + (int(200 * a * (1 - (r - 40) / 90)),), width=3)
        _box(L, (x, y), 330, 110, ti, su, a)
    L = glow(L, 8, .5); ld = ImageDraw.Draw(L)
    have, dont = marks
    a1 = clamp((t - have) / .3)
    if a1 > 0:
        ld.text((360, 640), '✓', font=font('black', 60), fill=TEAL + (int(255 * a1),), anchor='mm')
        ld.text((420, 640), 'WHAT WE HAVE:  THE AVIATORS’ ACCOUNTS OF WHAT THEY HEARD', font=font('monob', 34), fill=CREAM + (int(255 * a1),), anchor='lm')
    a2 = clamp((t - dont) / .3)
    if a2 > 0:
        ld.line([(340, 710), (380, 750)], fill=RED + (int(255 * a2),), width=8); ld.line([(340, 750), (380, 710)], fill=RED + (int(255 * a2),), width=8)
        ld.text((420, 730), 'WHAT WE DON’T:  THE RADAR TRACK ITSELF', font=font('monob', 34), fill=RED + (int(255 * a2),), anchor='lm')
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

def waterfall_frame(t, d):
    """Kevin Day's account: groups of up to ten contacts dropping from ~28,000 ft toward the sea, day after day. Amber, time scrolls left."""
    im = Image.new('RGB', (W, H), (14, 10, 6)); dr = ImageDraw.Draw(im)
    x0, x1, top, bot = 260, 1780, 150, 900
    def Y(ft): return bot - ft / 30000 * (bot - top)
    for ft in range(0, 30001, 5000):
        y = Y(ft); dr.line([(x0, y), (x1, y)], fill=(40, 30, 18), width=1)
        dr.text((x0 - 20, y), f'{ft // 1000}k ft' if ft else 'SEA', font=font('mono', 24), fill=(200, 150, 80), anchor='rm')
    dr.line([(x0, top), (x0, bot)], fill=(160, 120, 60), width=2); dr.line([(x0, bot), (x1, bot)], fill=(160, 120, 60), width=2)
    dr.text((x1, bot + 40), 'DAYS  →', font=font('monob', 26), fill=(200, 150, 80), anchor='rm')
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    speed = 150.   # px per second of scroll
    rnd = np.random.RandomState(11)
    groups = [(x1 + 120 - speed * 0 - i * 260 + rnd.uniform(-40, 40), int(rnd.randint(4, 11)), rnd.uniform(0, 1)) for i in range(14)]
    for gx, n, ph in groups:
        x = gx - speed * t + 260 * 6     # groups already on screen at t=0, more arriving from the right
        if x < x0 + 10 or x > x1 + 200: continue
        age = (x1 + 200 - x) / speed     # seconds since the group entered
        drop = eout(age / 5.0)
        for k in range(n):
            xx = x + (k - n / 2) * 13
            if xx < x0 + 6 or xx > x1: continue
            ft = 28000 - 27500 * clamp(drop * (1.1 - k * .02))
            for s in range(0, 12):
                f2 = 28000 - (28000 - ft) * s / 11
                ld.ellipse([xx - 2, Y(f2) - 2, xx + 2, Y(f2) + 2], fill=AMBER + (int(40 + 60 * s / 11),))
            ld.ellipse([xx - 7, Y(ft) - 7, xx + 7, Y(ft) + 7], fill=AMBER + (255,))
        if age > .4 and x < x1 - 40:
            ld.text((x, Y(29500)), f'{n}', font=font('monob', 26), fill=AMBER + (220,), anchor='mm')
    L = glow(L, 9, .9)
    ld = ImageDraw.Draw(L)
    ld.text((x1, top - 50), 'GROUPS OF UP TO 10  ·  ≈ 28,000 FT → SEA', font=font('monob', 30), fill=CREAM + (255,), anchor='rm')
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

def printout_frame(t, d):
    """The raw radar data: an illustrative track log, every value redacted, stamped NOT PUBLIC."""
    im = Image.new('RGB', (W, H), (10, 10, 12)); dr = ImageDraw.Draw(im)
    rnd = np.random.RandomState(3)
    z = 1 + .04 * t / d
    pw, ph = 1180 * z, 740 * z; cx, cy = W / 2, 500
    x0, y0 = cx - pw / 2, cy - ph / 2
    dr.rectangle([x0, y0, x0 + pw, y0 + ph], fill=(214, 208, 192))
    # paper grain
    a = np.asarray(im, np.float32); a += np.random.RandomState(int(t * 30) % 6).normal(0, 4, (H, W, 1)); im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(im)
    f, fb = font('mono', int(24 * z)), font('monob', int(24 * z))
    dr.text((x0 + 40 * z, y0 + 44 * z), 'RADAR TRACK DATA · USS PRINCETON (CG-59) · NOV 2004', font=fb, fill=(30, 30, 34), anchor='lm')
    dr.text((x0 + pw - 40 * z, y0 + 44 * z), 'ILLUSTRATIVE', font=f, fill=(150, 60, 50), anchor='rm')
    cols = ['TIME', 'TRACK', 'ALT FT', 'RANGE NM', 'BRG', 'SPEED']
    cx_ = [x0 + (60 + i * 185) * z for i in range(6)]
    for x, c in zip(cx_, cols): dr.text((x, y0 + 110 * z), c, font=fb, fill=(30, 30, 34), anchor='lm')
    dr.line([(x0 + 40 * z, y0 + 135 * z), (x0 + pw - 40 * z, y0 + 135 * z)], fill=(40, 40, 44), width=2)
    for r in range(13):
        y = y0 + (175 + r * 42) * z
        for i, x in enumerate(cx_):
            ws = rnd.uniform(.55, 1.0) * 150 * z
            dt = clamp((t - .1 - r * .06 - i * .02) / .25)
            if dt > 0: dr.rectangle([x, y - 13 * z, x + ws * dt, y + 13 * z], fill=(14, 14, 16))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sa = clamp((t - 1.3) / .12)
    if sa > 0:
        st = Image.new('RGBA', (700, 200), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        sd.rectangle([10, 10, 690, 190], outline=RED + (int(235 * sa),), width=10)
        sd.text((350, 100), 'NOT PUBLIC', font=font('black', 110), fill=RED + (int(235 * sa),), anchor='mm')
        sc = 1 + .5 * (1 - eout((t - 1.3) / .2))
        st = st.resize((int(700 * sc), int(200 * sc))).rotate(-9, expand=True, resample=Image.BICUBIC)
        L.alpha_composite(st, (int(cx - st.width / 2), int(cy - st.height / 2 + 40)))
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

# ---------------------------------------------------------------- split screens
HALF = W // 2
def fill_rect(img, box, w, h, zoom=1.0, cy=.5):
    if box: img = img.crop(box)
    iw, ih = img.size
    cw = iw / zoom; ch = cw * h / w
    if ch > ih / zoom: ch = ih / zoom; cw = ch * w / h
    x0 = (iw - cw) / 2; y0 = min(max(cy * ih - ch / 2, 0), ih - ch)
    return img.resize((w, h), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))

def split_compose(left, right, lt, labels=('', ''), tag_cols=(RED, RED)):
    """left/right: HALFxH images. Slides apart from the centre on entry, red divider, a small label on each half."""
    im = Image.new('RGB', (W, H))
    s = eout(lt / .45)
    im.paste(left, (int(-HALF * (1 - s) * .25), 0)); im.paste(right, (HALF + int(HALF * (1 - s) * .25), 0))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle([HALF - 3, 0, HALF + 3, H], fill=RED + (255,))
    for i, (txt, col) in enumerate(zip(labels, tag_cols)):
        if not txt: continue
        x = 64 + i * HALF; y = 130
        w = d.textlength(txt, font=font('monob', 26))
        d.rectangle([x - 14, y - 22, x + w + 16, y + 22], fill=(8, 10, 14, 170))
        d.rectangle([x - 14, y - 22, x - 8, y + 22], fill=col + (255,))
        d.text((x + 4, y), txt, font=font('monob', 26), fill=CREAM + (255,), anchor='lm')
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')

def _panel_bg(t):
    p = Image.new('RGB', (HALF, H), NAVY); _dots(ImageDraw.Draw(p), HALF, H, -12 * t)
    return p

def panel_eye(t, d):
    """FLIR1's crew: one jet, the WSO seat lit, sensor only, no visual."""
    p = _panel_bg(t); L = Image.new('RGBA', (HALF, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    a = clamp(t / .4)
    shadow_text(L, (HALF / 2, 230), 'HIS CREW NEVER SAW IT BY EYE', font('black', 50), RED + (int(255 * a),), spread=10)
    ld.polygon(jet_poly(HALF / 2, 600, 300, 0), outline=(235, 215, 180, 255), fill=(30, 36, 52, 255))
    for dy, role, lit in ((-193, 'PILOT', .25), (-147, 'WSO · CHAD UNDERWOOD', 1.0)):
        y = 600 + dy; r = 15
        ld.ellipse([HALF / 2 - r, y - r, HALF / 2 + r, y + r], fill=(int(60 + 166 * lit), int(70 + 128 * lit), int(80 + 2 * lit), 255))
        ld.text((HALF / 2 + 36, y), role, font=font('monob', 26), fill=CREAM + (int(255 * max(lit, .45)),), anchor='lm')
    b = clamp((t - .8) / .4)
    # camera pod under the jet, its narrow beam reaching off-panel
    ld.line([(HALF / 2 + 40, 640), (HALF - 20, 470)], fill=TEAL + (int(200 * b),), width=3)
    ld.text((HALF / 2 + 70, 700), 'ATFLIR CAMERA POD', font=font('monob', 26), fill=TEAL + (int(255 * b),), anchor='lm')
    c = clamp((t - 1.6) / .4)
    ex, ey = HALF / 2, 900
    ld.ellipse([ex - 70, ey - 32, ex + 70, ey + 32], outline=CREAM + (int(255 * c),), width=4)
    ld.ellipse([ex - 18, ey - 18, ex + 18, ey + 18], fill=CREAM + (int(255 * c),))
    ld.line([(ex - 85, ey + 45), (ex + 85, ey - 45)], fill=RED + (int(255 * c),), width=7)
    ld.text((ex, ey + 80), 'SENSOR ONLY · NO VISUAL CONTACT', font=font('monob', 26), fill=CREAM + (int(255 * c),), anchor='mm')
    return Image.alpha_composite(p.convert('RGBA'), glow(L, 6, .4)).convert('RGB')

def panel_lock(t, d):
    """Two readings of FLIR1's ending, looped: A the object accelerates out; B the camera loses lock and the frame drifts."""
    p = _panel_bg(t); L = Image.new('RGBA', (HALF, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    a = clamp(t / .4)
    shadow_text(L, (HALF / 2, 170), 'BURST OF SPEED — OR LOST LOCK?', font('black', 46), CREAM + (int(255 * a),), spread=10)
    per = 3.2; u = (t % per) / per
    for i, (yc, title) in enumerate(((440, 'A · IT ACCELERATED'), (800, 'B · THE CAMERA LOST LOCK'))):
        bw, bh = 640, 260; x0 = (HALF - bw) / 2; y0 = yc - bh / 2
        ld.rectangle([x0, y0, x0 + bw, y0 + bh], outline=(90, 110, 130, 255), width=2, fill=(4, 8, 14, 255))
        ld.text((x0, y0 - 26), title, font=font('monob', 28), fill=(RED if i else CREAM) + (255,), anchor='ls')
        cx, cy = x0 + bw / 2, yc
        if i == 0:   # reticle stays locked to the frame centre, the object leaves at speed
            ox = cx - (eout(clamp((u - .45) / .3)) ** 1.0) * 520 if u > .45 else cx
            box = (cx, cy)
        else:        # object drifts steadily; the tracking box stops following and the object slides out
            ox = cx - clamp((u - .3) / .7) * 420
            box = (cx - clamp((u - .3) / .25) * 60, cy) if u > .3 else (ox, cy)
        if x0 < ox < x0 + bw:
            ld.ellipse([ox - 10, cy - 6, ox + 10, cy + 6], fill=(235, 235, 235, 255))
            if i == 0 and u > .45:
                for k in range(1, 6): ld.ellipse([ox + k * 18 - 6, cy - 3, ox + k * 18 + 6, cy + 3], fill=(235, 235, 235, int(120 - k * 20)))
        bx, by = box; s = 34
        for sx in (-1, 1):
            for sy in (-1, 1):
                ld.line([(bx + sx * s, by + sy * s), (bx + sx * s - sx * 14, by + sy * s)], fill=TEAL + (255,), width=3)
                ld.line([(bx + sx * s, by + sy * s), (bx + sx * s, by + sy * s - sy * 14)], fill=TEAL + (255,), width=3)
        ld.text((x0 + bw - 12, y0 + bh - 14), 'LOCK' if (i == 0 or u < .3) else 'LOCK LOST', font=font('monob', 22),
                fill=(TEAL if (i == 0 or u < .3) else RED) + (255,), anchor='rs')
    return Image.alpha_composite(p.convert('RGBA'), L).convert('RGB')

def panel_timeline(t, d):
    """14 Nov 2004: the close encounter had no video; FLIR1 came on a later flight."""
    p = _panel_bg(t); L = Image.new('RGBA', (HALF, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    a = clamp(t / .4)
    shadow_text(L, (HALF / 2, 190), 'THE VIDEO CAME LATER', font('black', 56), CREAM + (int(255 * a),), spread=10)
    ld.text((HALF / 2, 280), '14 NOV 2004', font=font('monob', 30), fill=(200, 190, 170, int(255 * a)), anchor='mm')
    lx = 170; ln = eout(t / 1.2)
    ld.line([(lx, 340), (lx, 340 + 560 * ln)], fill=CREAM + (200,), width=3)
    rows = [(470, .5, 'EARLIER · FRAVOR & DIETRICH', '4 AVIATORS SEE IT · NO VIDEO', CREAM),
            (760, 1.4, 'LATER FLIGHT · UNDERWOOD', 'FLIR1 RECORDED · NO VISUAL', RED)]
    for y, t0, ti, su, col in rows:
        b = clamp((t - t0) / .4)
        if b <= 0: continue
        ld.ellipse([lx - 14, y - 14, lx + 14, y + 14], fill=col + (int(255 * b),))
        ld.text((lx + 44, y - 18), ti, font=font('monob', 32), fill=col + (int(255 * b),), anchor='lm')
        ld.text((lx + 44, y + 24), su, font=font('mono', 26), fill=(200, 200, 205, int(255 * b)), anchor='lm')
    return Image.alpha_composite(p.convert('RGBA'), glow(L, 6, .4)).convert('RGB')

PANELS = {'eye': panel_eye, 'lock': panel_lock, 'timeline': panel_timeline}

def scoreboard_frame(t, d, bg, times, verdicts=None):
    """The evidence on the record: EYES / RADAR / VIDEO / DOCUMENTS. Titles light one by one; with verdicts, each gets a one-line result."""
    im = bg.copy(); L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(L)
    cw, ch, gap = 390, 300, 36; x0 = (W - (4 * cw + 3 * gap)) // 2; y0 = 360
    for i, name in enumerate(('EYES', 'RADAR', 'VIDEO', 'DOCUMENTS')):
        a = clamp((t - times[i]) / .3)
        x = x0 + i * (cw + gap); col = verdicts[i][1] if verdicts else CREAM
        ld.rounded_rectangle([x, y0, x + cw, y0 + ch], 10, fill=(10, 12, 18, int(170 * (.35 + .65 * a))), outline=col + (int(255 * (.3 + .7 * a)),), width=4 if a > 0 else 2)
        shadow_text(L, (x + cw / 2, y0 + 110), name, font('black', 62 if name != 'DOCUMENTS' else 50), CREAM + (int(255 * (.35 + .65 * a)),), spread=10)
        if verdicts and a > 0:
            shadow_text(L, (x + cw / 2, y0 + 215), verdicts[i][0], font('monob', 32), col + (int(255 * a),), spread=10)
    return Image.alpha_composite(im.convert('RGBA'), L).convert('RGB')
