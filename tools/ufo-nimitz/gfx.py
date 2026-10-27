"""Motion-graphics generators for the Tic Tac film: map, radar, parallax diagram, text layers.
Everything is drawn here (PIL + numpy); nothing is taken from third-party media."""
import math, json, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
W, H = 1920, 1080
HERE = __file__.rsplit('/', 1)[0]
FD = '/usr/share/fonts/opentype/inter/'
FM = '/usr/share/fonts/truetype/jetbrains-mono/'
_fc = {}
def font(kind, sz):
    path = {'black': FD + 'InterDisplay-Black.otf', 'bold': FD + 'InterDisplay-Bold.otf',
            'semi': FD + 'InterDisplay-SemiBold.otf', 'mono': FM + 'JetBrainsMono-Medium.ttf',
            'monob': FM + 'JetBrainsMono-Bold.ttf',
            'serif': '/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf'}[kind]
    k = (path, sz)
    if k not in _fc: _fc[k] = ImageFont.truetype(path, sz)
    return _fc[k]

CREAM = (240, 232, 214); RED = (226, 58, 46); NAVY = (6, 10, 20); TEAL = (120, 220, 210)

def clamp(x, a=0., b=1.): return max(a, min(b, x))
def ease(t): t = clamp(t); return t * t * (3 - 2 * t)
def eout(t): t = clamp(t); return 1 - (1 - t) ** 3

def glow(img, r=12, k=1.0):
    """Add a soft bloom of an RGBA/RGB layer onto itself."""
    a = np.asarray(img, dtype=np.float32)
    b = np.asarray(img.filter(ImageFilter.GaussianBlur(r)), dtype=np.float32)
    return Image.fromarray(np.clip(a + b * k, 0, 255).astype(np.uint8), img.mode)

# ---------------------------------------------------------------- map
_LAND = _COAST = None
NIMITZ = (-117.9, 31.6); SANDIEGO = (-117.16, 32.72); CAP = (-118.9, 31.95)
def _load():
    global _LAND, _COAST
    if _LAND is None:
        _LAND = json.load(open(HERE + '/data/land_socal.json'))
        _COAST = json.load(open(HERE + '/data/coast_socal.json'))
MAP_C = (-118.4, 32.1); MAP_S = 150  # base map centre and px/deg at zoom 1
_base = None
def map_base():
    """Render once at 2x (3840x2160) for zooming."""
    global _base
    if _base is not None: return _base
    _load()
    S = 2; w, h = W * S, H * S; s = MAP_S * S
    k = math.cos(math.radians(MAP_C[1]))
    P = lambda lo, la: (w / 2 + (lo - MAP_C[0]) * s * k, h / 2 - (la - MAP_C[1]) * s)
    im = Image.new('RGB', (w, h), NAVY); d = ImageDraw.Draw(im)
    g = 34
    for y in range(0, h, g):
        for x in range(0, w, g): d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(18, 28, 46))
    for r in _LAND: d.polygon([P(a, b) for a, b in r], fill=(20, 20, 26))
    gl = Image.new('RGB', (w, h)); gd = ImageDraw.Draw(gl)
    for r in _COAST: gd.line([P(a, b) for a, b in r], fill=(235, 215, 180), width=4)
    im = Image.fromarray(np.clip(np.asarray(im, np.float32) + np.asarray(gl.filter(ImageFilter.GaussianBlur(14)), np.float32) * .55
                                 + np.asarray(gl, np.float32) * .6, 0, 255).astype(np.uint8))
    _base = im
    return im

def map_frame(t, zoom=1.0, center=MAP_C, marker=1., jets=0., cap=0., labels=1., tag=None):
    base = map_base()
    k = math.cos(math.radians(MAP_C[1]))
    def B(lo, la):  # base pixel coords (2x)
        return (W + (lo - MAP_C[0]) * MAP_S * 2 * k, H - (la - MAP_C[1]) * MAP_S * 2)
    cx, cy = B(*center)
    cw, ch = W * 2 / zoom, H * 2 / zoom
    x0, y0 = cx - cw / 2, cy - ch / 2
    im = base.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))
    def S(lo, la):
        bx, by = B(lo, la); return ((bx - x0) / cw * W, (by - y0) / ch * H)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    nx, ny = S(*NIMITZ)
    if marker > 0:
        for i in range(3):
            ph = (t * .6 + i / 3) % 1
            R = 10 + ph * 140; a = int(210 * (1 - ph) * marker)
            d.ellipse([nx - R, ny - R, nx + R, ny + R], outline=RED + (a,), width=3)
        d.ellipse([nx - 10, ny - 10, nx + 10, ny + 10], fill=RED + (int(255 * marker),))
    if jets > 0:  # two jets flying from the ship toward the contact
        e = ease(jets)
        tx, ty = S(NIMITZ[0] - .35, NIMITZ[1] - .25)
        for j, off in enumerate([(0, 0), (-26, -18)]):
            px, py = nx + (tx - nx) * e + off[0], ny + (ty - ny) * e + off[1]
            ang = math.atan2(ty - ny, tx - nx)
            pts = [(px + 16 * math.cos(ang), py + 16 * math.sin(ang)),
                   (px + 12 * math.cos(ang + 2.5), py + 12 * math.sin(ang + 2.5)),
                   (px + 12 * math.cos(ang - 2.5), py + 12 * math.sin(ang - 2.5))]
            d.polygon(pts, fill=CREAM + (255,))
            d.line([(nx + off[0] * e, ny + off[1] * e), (px, py)], fill=CREAM + (70,), width=2)
        if jets > .7:
            a = int(255 * clamp((jets - .7) / .3))
            for i in range(2):
                ph = (t * .9 + i / 2) % 1; R = 8 + ph * 60
                d.ellipse([tx - R, ty - R, tx + R, ty + R], outline=(255, 255, 255, int(a * (1 - ph))), width=2)
            d.ellipse([tx - 6, ty - 6, tx + 6, ty + 6], fill=(255, 255, 255, a))
    if cap > 0:
        sx, sy = S(NIMITZ[0] - .35, NIMITZ[1] - .25); ex, ey = S(*CAP)
        e = eout(cap)
        d.line([(sx, sy), (sx + (ex - sx) * e, sy + (ey - sy) * e)], fill=(255, 255, 255, 230), width=4)
        d.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill=(255, 255, 255, 160))
        if cap >= 1:
            for i in range(2):
                ph = (t * 1.2 + i / 2) % 1; R = 10 + ph * 80
                d.ellipse([ex - R, ey - R, ex + R, ey + R], outline=(255, 255, 255, int(220 * (1 - ph))), width=3)
            d.ellipse([ex - 9, ey - 9, ex + 9, ey + 9], fill=(255, 255, 255, 255))
            d.text((ex, ey - 30), 'CAP POINT', font=font('monob', 30), fill=CREAM + (255,), anchor='ms')
    ov = Image.alpha_composite(glow(ov, 8, .8), ov)
    im = Image.alpha_composite(im.convert('RGBA'), ov)
    d = ImageDraw.Draw(im)
    if labels > 0:
        a = int(255 * labels)
        sx, sy = S(*SANDIEGO)
        d.ellipse([sx - 6, sy - 6, sx + 6, sy + 6], fill=CREAM + (a,))
        d.text((sx + 18, sy), 'SAN DIEGO', font=font('bold', 30), fill=CREAM + (a,), anchor='lm')
        px, py = S(-120.4, 31.0)
        d.text((px, py), 'P A C I F I C   O C E A N', font=font('semi', 28), fill=(120, 140, 170, a), anchor='mm')
        if marker > 0:
            d.text((nx + 28, ny + 4), 'USS NIMITZ STRIKE GROUP', font=font('bold', 30), fill=CREAM + (int(a * marker),), anchor='lm')
    return im.convert('RGB')

# ---------------------------------------------------------------- radar (illustrative)
def radar_frame(t, drop=0., ping=0.):
    """Scope on the left, altitude ladder on the right. drop 0..1 = contacts falling 80k -> 20k ft."""
    S = 1
    im = Image.new('RGB', (W, H), (3, 8, 10))
    a = np.zeros((H, W), np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy, R = 620, 540, 420
    dx, dy = xx - cx, yy - cy; r = np.sqrt(dx * dx + dy * dy); th = np.arctan2(dy, dx)
    sweep = (t * 1.6) % (2 * math.pi)
    dth = (sweep - th) % (2 * math.pi)
    inside = r < R
    a += inside * np.exp(-dth * 2.2) * .55
    for rr in (R * .25, R * .5, R * .75, R):
        a += np.exp(-((r - rr) / 1.6) ** 2) * .35
    a += inside * (np.exp(-(np.abs(dx) / 1.2) ** 2) + np.exp(-(np.abs(dy) / 1.2) ** 2)) * .12
    # contacts
    rnd = np.random.RandomState(4)
    for i in range(5):
        ang = rnd.uniform(0, 2 * math.pi); rad = rnd.uniform(.3, .85) * R
        bx, by = cx + rad * math.cos(ang), cy + rad * math.sin(ang)
        age = (sweep - ang) % (2 * math.pi)
        a += np.exp(-((xx - bx) ** 2 + (yy - by) ** 2) / 60.) * (.4 + 1.6 * math.exp(-age * 1.1))
    col = np.stack([a * 90, a * 255, a * 210], -1)
    im = Image.fromarray(np.clip(col, 0, 255).astype(np.uint8))
    im = glow(im, 10, .7)
    d = ImageDraw.Draw(im)
    # altitude ladder
    lx = 1250; top, bot = 140, 960
    def Y(ft): return bot - (ft / 90000) * (bot - top)
    d.line([(lx, top), (lx, bot)], fill=(90, 160, 150), width=2)
    for ft in range(0, 90001, 10000):
        y = Y(ft); d.line([(lx - 12, y), (lx + 12, y)], fill=(90, 160, 150), width=2)
        d.text((lx - 24, y), f'{ft // 1000}k ft' if ft else '0', font=font('mono', 24), fill=(140, 210, 200), anchor='rm')
    y35 = Y(35000)
    for x in range(lx, lx + 520, 18): d.line([(x, y35), (x + 9, y35)], fill=(140, 120, 90), width=2)
    d.text((lx + 530, y35), 'AIRLINERS', font=font('mono', 22), fill=(190, 160, 120), anchor='lm')
    rnd = np.random.RandomState(9)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    for i in range(3):
        x = lx + 90 + i * 130
        d0 = clamp(drop * 1.15 - i * .07)
        ft = 80000 - 60000 * eout(d0)
        y = Y(ft)
        od.line([(x, Y(80000)), (x, y)], fill=(255, 255, 255, 60), width=3)
        od.ellipse([x - 11, y - 11, x + 11, y + 11], fill=(255, 255, 255, 255))
    if ping > 0:
        od.text((lx + 270, Y(80000) - 50), '80,000 FT  →  20,000 FT', font=font('monob', 30), fill=CREAM + (int(255 * ping),), anchor='mm')
    im = Image.alpha_composite(im.convert('RGBA'), glow(ov, 9, 1.))
    return im.convert('RGB')

# ---------------------------------------------------------------- GOFAST parallax diagram
def parallax_frame(t, u):
    """Side view: jet high, object at ~13,000 ft, line of sight sweeping the sea far below."""
    im = Image.new('RGB', (W, H), (5, 9, 18))
    g = np.linspace(0, 1, H)[:, None]
    bg = np.stack([5 + 12 * g, 9 + 22 * g, 18 + 40 * g], -1) * np.ones((1, W, 1))
    im = Image.fromarray(bg.astype(np.uint8))
    d = ImageDraw.Draw(im, 'RGBA')
    sea = 900
    for x in range(0, W, 6):
        y = sea + 6 * math.sin(x * .02 + t * 3) + 3 * math.sin(x * .07 - t * 5)
        d.line([(x, y), (x, H)], fill=(10, 40, 70, 255), width=6)
    d.line([(0, sea), (W, sea)], fill=(90, 150, 200, 200), width=2)
    jx = 260 + u * 700; jy = 170
    ox = 820 + u * 90; oy = 560
    # sightline through the object to the sea
    sx = jx + (ox - jx) * (sea - jy) / (oy - jy)
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); od = ImageDraw.Draw(ov)
    od.line([(jx, jy), (sx, sea)], fill=(255, 220, 160, 150), width=3)
    for k in range(1, 12):  # sea "rushing" trail of past aim points
        uu = max(0, u - k * .02)
        jx2 = 260 + uu * 700; ox2 = 820 + uu * 90
        sx2 = jx2 + (ox2 - jx2) * (sea - jy) / (oy - jy)
        od.ellipse([sx2 - 6, sea - 6, sx2 + 6, sea + 6], fill=(255, 200, 120, int(150 * (1 - k / 12))))
    od.ellipse([sx - 10, sea - 10, sx + 10, sea + 10], fill=(255, 220, 160, 255))
    od.ellipse([ox - 12, oy - 12, ox + 12, oy + 12], fill=(255, 255, 255, 255))
    od.polygon([(jx + 40, jy), (jx - 30, jy - 16), (jx - 18, jy), (jx - 30, jy + 16)], fill=CREAM + (255,))
    im = Image.alpha_composite(im.convert('RGBA'), glow(ov, 10, 1.1))
    d = ImageDraw.Draw(im)
    d.text((ox + 30, oy - 10), 'OBJECT  ≈ 13,000 FT', font=font('monob', 32), fill=CREAM, anchor='lm')
    d.text((jx, jy - 40), 'JET', font=font('monob', 28), fill=CREAM, anchor='ms')
    d.text((sx, sea + 70), 'WHERE THE CAMERA POINTS: THE SEA', font=font('mono', 28), fill=(255, 220, 160), anchor='ms')
    return im.convert('RGB')

# ---------------------------------------------------------------- text layers (RGBA, drawn over picture)
def shadow_text(layer, xy, text, f, fill, anchor='mm', shadow=150, spread=10):
    sh = Image.new('RGBA', layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text(xy, text, font=f, fill=(0, 0, 0, shadow), anchor=anchor)
    sh = sh.filter(ImageFilter.GaussianBlur(spread))
    layer.alpha_composite(sh)
    ImageDraw.Draw(layer).text(xy, text, font=f, fill=fill, anchor=anchor)

def tag(layer, text, a=1.0, color=RED):
    """Top-left source tag, e.g. REAL NAVY FOOTAGE."""
    if a <= 0: return
    d = ImageDraw.Draw(layer)
    f = font('monob', 26)
    x, y = 64, 58
    w = d.textlength(text, font=f)
    d.rectangle([x - 14, y - 22, x + w + 16, y + 22], fill=(8, 10, 14, int(170 * a)))
    d.rectangle([x - 14, y - 22, x - 8, y + 22], fill=color + (int(255 * a),))
    d.text((x + 4, y), text, font=f, fill=CREAM + (int(255 * a),), anchor='lm')

def source_line(layer, text, a=1.0):
    if a <= 0: return
    f = font('mono', 22)
    shadow_text(layer, (W - 64, H - 54), text, f, (220, 214, 200, int(230 * a)), anchor='rs', shadow=int(200 * a), spread=6)

def headline(layer, text, t, dur, y=540, size=118, color=CREAM, sub=None):
    """Big one-line hit: punches in, holds, fades."""
    if t < 0 or t > dur: return
    a = clamp(t / .12) * clamp((dur - t) / .25)
    sc = 1.0 + .08 * (1 - eout(t / .35)) + .02 * t / dur
    f = font('black', int(size * sc))
    shadow_text(layer, (W / 2, y), text, f, color + (int(255 * a),), shadow=int(190 * a), spread=18)
    if sub:
        shadow_text(layer, (W / 2, y + size * .78), sub, font('monob', 30), CREAM + (int(230 * a),), shadow=int(180 * a), spread=8)

def lower_third(layer, name, role, t, dur):
    if t < 0 or t > dur: return
    a = clamp(t / .3) * clamp((dur - t) / .3)
    x = 110 - 30 * (1 - eout(t / .5)); y = 860
    d = ImageDraw.Draw(layer)
    d.rectangle([x - 22, y - 46, x - 14, y + 52], fill=RED + (int(255 * a),))
    shadow_text(layer, (x, y - 10), name, font('black', 56), CREAM + (int(255 * a),), anchor='ls', shadow=int(170 * a), spread=10)
    shadow_text(layer, (x, y + 38), role, font('monob', 28), (210, 205, 190, int(240 * a)), anchor='ls', shadow=int(170 * a), spread=8)

def quote(layer, text, who, t, dur, y=760):
    """Testimony quote, typed on word by word."""
    if t < 0 or t > dur: return
    a = clamp((dur - t) / .3)
    words = text.split(' ')
    nshow = int(clamp(t / max(.6, dur * .45)) * len(words) + .999)
    shown = ' '.join(words[:nshow])
    f = font('serif', 64)
    shadow_text(layer, (W / 2, y), '“' + shown + ('”' if nshow == len(words) else ''), f, CREAM + (int(255 * a),), shadow=int(210 * a), spread=16)
    if nshow == len(words):
        shadow_text(layer, (W / 2, y + 70), who, font('monob', 26), (220, 210, 190, int(230 * a)), shadow=int(190 * a), spread=8)

def callout_box(layer, cx, cy, w, h, text, t, dur):
    if t < 0 or t > dur: return
    a = clamp(t / .2) * clamp((dur - t) / .25)
    d = ImageDraw.Draw(layer)
    s = 1 + .3 * (1 - eout(t / .3)); w2, h2 = w * s / 2, h * s / 2
    L = 26
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = cx + sx * w2, cy + sy * h2
            d.line([(x, y), (x - sx * L, y)], fill=RED + (int(255 * a),), width=5)
            d.line([(x, y), (x, y - sy * L)], fill=RED + (int(255 * a),), width=5)
    shadow_text(layer, (cx, cy + h2 + 46), text, font('monob', 32), CREAM + (int(255 * a),), shadow=int(200 * a), spread=8)
