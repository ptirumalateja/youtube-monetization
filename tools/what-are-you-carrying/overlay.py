"""Text layer for What Are You Carrying (Slow Light Dark look; helpers from ../slow-light-dark-common/sld_text.py).

Soft, sentence-case captions: plain lines in Inter Medium (white), the words that matter in Lora Italic (gold), fading in
and out with no pop. Place names in lowercase italic with thin curved arrows: old life (his start at the foot of the hill)
and new life (the hilltop, then the flag). Each stone's word lifts off it as it crumbles and drifts away. End card:
What are you / still carrying? + FOLLOW @SLOWLIGHTTV. All text sits below the Reels/Shorts top bar (y >= 270).

  python3 overlay.py still IN.jpg T OUT.jpg META     overlay one rendered frame at time T
  (compose.py imports draw() for the full video)
"""
import json, os, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_text import font as mono, tracked, sstep, CREAM, W, H
from PIL import ImageFont
FONTS = os.path.join(HERE, '..', 'slow-light-dark-common', 'fonts')
_F = {}
def font(size, wt='SemiBold'):
    """Sans (Inter Medium / SemiBold) for plain lines, Ital (Lora Italic) for the words that matter; mono weights fall through."""
    files = {'Sans': 'Inter-Medium.otf', 'SansSemi': 'Inter-SemiBold.otf', 'Ital': 'Lora_400Regular_Italic.ttf', 'ItalMed': 'Lora_500Medium_Italic.ttf'}
    if wt not in files: return mono(size, wt)
    k = (size, wt)
    if k not in _F: _F[k] = ImageFont.truetype(os.path.join(FONTS, files[wt]), size)
    return _F[k]
WHITE = (246, 242, 234)

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
GOLD = (240, 196, 120)
RED = (216, 58, 46)
META = None


def load_meta(path):
    global META
    META = json.load(open(path))


def frame_meta(t):
    fr = META['frames']; return fr[min(len(fr) - 1, max(0, round(t * TL['fps'])))]


def width(text, f, track):
    d = ImageDraw.Draw(Image.new('L', (1, 1)))
    return sum(d.textlength(c, font=f) for c in text) + track * (len(text) - 1)


def text_layer(items):
    """items: [(text, size, weight, track, cx, y, rgb, alpha)] -> (halo mask, RGBA layer)"""
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for text, size, wt, track, cx, y, rgb, a in items:
        if a <= 0: continue
        f = font(size, wt)
        if track: tracked(md, text, f, cx, y, track, int(255 * a)); tracked(ld, text, f, cx, y, track, rgb + (int(255 * a),))
        else: md.text((cx, y), text, font=f, fill=int(255 * a), anchor='ma'); ld.text((cx, y), text, font=f, fill=rgb + (int(255 * a),), anchor='ma')   # proportional fonts keep their kerning
    return mask, layer


def caption(t, lines, t0, t1, y=290, size=58):
    """lines: plain strings (white sans) or ('text',) tuples (gold italic, a touch larger). A soft fade, no pop: quiet, like a thought."""
    a = sstep(t0, t0 + 0.3, t) * (1 - sstep(t1 - 0.3, t1, t)); out = []; yy = y
    for ln in lines:
        if isinstance(ln, tuple): out.append((ln[0], int(size * 1.12), 'Ital', 0, W / 2, yy - 4, GOLD, a))
        else: out.append((ln, size, 'Sans', 0, W / 2, yy, WHITE, a))
        yy += int(size * 1.32)
    return out


def chip(base, text, cx, cy, a, pop=1.0, size=46):
    """A red label chip (the stones' names), with a soft drop shadow."""
    if a <= 0: return
    f = font(int(size * pop), 'ExtraBold'); w = width(text, f, 4)
    hw, hh = w / 2 + 20 * pop, 30 * pop
    cx = min(max(cx, hw + 24), W - hw - 24)
    sh = Image.new('L', (W, H), 0); ImageDraw.Draw(sh).rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=10, fill=int(200 * a))
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (sh.filter(ImageFilter.GaussianBlur(14)),)))
    c = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(c)
    cd.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=10, fill=RED + (int(235 * a),))
    tracked(cd, text, f, cx, cy - 21 * pop, 4, CREAM + (int(255 * a),))
    base.alpha_composite(c)


def arrow(mask, layer, p0, p1, rgb, a, bend=1, gap=26, w=4):
    """A slightly curved arrow p0 -> p1 (stops `gap` px short of p1), drawn into the text halo mask and the layer."""
    import math
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy)
    if L < gap * 2: return
    x1, y1 = x1 - dx / L * gap, y1 - dy / L * gap
    cx, cy = (x0 + x1) / 2 - dy / L * 0.22 * L * bend, (y0 + y1) / 2 + dx / L * 0.22 * L * bend
    pts = [((1 - u) ** 2 * x0 + 2 * (1 - u) * u * cx + u * u * x1, (1 - u) ** 2 * y0 + 2 * (1 - u) * u * cy + u * u * y1)
           for u in (i / 40 for i in range(41))]
    tx, ty = x1 - pts[-3][0], y1 - pts[-3][1]; tl = math.hypot(tx, ty) or 1; tx, ty = tx / tl, ty / tl
    head = [(x1 + tx * 4, y1 + ty * 4), (x1 - tx * 24 - ty * 14, y1 - ty * 24 + tx * 14), (x1 - tx * 24 + ty * 14, y1 - ty * 24 - tx * 14)]
    for d, fill in ((ImageDraw.Draw(mask), int(255 * a)), (ImageDraw.Draw(layer), rgb + (int(255 * a),))):
        d.line(pts, fill=fill, width=w, joint='curve'); d.polygon(head, fill=fill)


def draw(img, t):
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    card = sstep(TL['card'], TL['card'] + 0.5, t)
    if card > 0:
        img = ImageEnhance.Brightness(img).enhance(1 - 0.08 * card)   # the enlightenment stays visible under the question
    base = img.convert('RGBA'); m = frame_meta(t); items = []
    items += caption(t, ['Trying to reach', ('a new life...',)], *TL['capA'], y=285, size=62)
    items += caption(t, ['...while carrying', ('the old one.',)], *TL['capB'], y=285, size=62)
    items += caption(t, ["It's not the climb.", ("It's the weight.",)], *TL['capC'], y=285, size=60)
    items += caption(t, [('Let it go.',)], *TL['capD'], y=285, size=70)
    # place names on the wide shots
    wide = sstep(1.3, 1.8, t) * (1 - sstep(TL['push0'], TL['push0'] + 0.4, t)) + sstep(TL['pull1'] - 0.2, TL['pull1'] + 0.4, t) * (1 - card)
    # the label sits off to one side and a small hand-drawn arrow curves to the spot it names
    end = t > TL['pull1']
    arrows = []
    for key, pt, name, col, off in (('oldLife', 'oldPt', 'old life', CREAM, (150, 150)),
                                    ('newLife' if end else 'newLifeWide', 'newPt' if end else 'newPtWide', 'new life', GOLD,
                                     (90, -300) if end else (-170, -190))):
        x, y, vis = m[pt]
        if not (vis and 0.03 < x < 0.97 and 0.05 < y < 0.95): continue
        a = 0.9 * min(1.0, wide)
        if a <= 0: continue
        hw = font(48, 'Ital').getlength(name) / 2
        tx, ty = x * W, y * H
        lx = min(max(tx + off[0], hw + 30), W - hw - 30); ly = min(max(ty + off[1], 300), H - 140)
        items.append((name, 48, 'Ital', 0, lx, ly - 30, col, a))
        # start just off the label's edge facing the target, end a little short of the target
        sx = lx + (hw + 8) * (1 if tx > lx else -1) * 0.55; sy = ly + (32 if ty > ly else -32)
        arrows.append(((sx, sy), (tx, ty), col, a, 1 if off[0] * off[1] > 0 else -1))
    mask, layer = text_layer(items)
    for ar in arrows: arrow(mask, layer, *ar)
    composite_text(base, mask, layer)
    # the stones' names: from the moment he lifts each one until shortly after it leaves his hand
    for i, (T, name) in enumerate(zip(TL['throws'], TL['labels'])):
        s = m['stones'][i] or (frame_meta(min(t, T + 0.5))['stones'][i] if T - 0.6 < t < T + 1.0 else None)   # the word outlives the stone
        if not s: continue
        a = sstep(T - 0.5, T - 0.3, t) * (1 - sstep(T + 0.45, T + 0.95, t))
        if a > 0:   # the word lifts off the stone as it breaks and drifts away into the air
            rise = 140 * sstep(T, T + 0.95, t) ** 1.3
            wm_, wl_ = text_layer([(name.lower(), 54, 'ItalMed', 0, min(max(s[0] * W, 170), W - 170), s[1] * H - 90 - rise, WHITE, a)])
            composite_text(base, wm_, wl_)
    # end card
    if card > 0:
        a = sstep(TL['card'] + 0.2, TL['card'] + 0.55, t); pop = 1 + 0.05 * (1 - a)
        em, el = text_layer([('What are you', 66, 'Sans', 0, W / 2, 300, WHITE, a),
                             ('still carrying?', 76, 'Ital', 0, W / 2, 384, GOLD, sstep(TL['card'] + 0.6, TL['card'] + 1.1, t)),
                             ('FOLLOW @SLOWLIGHTTV', 40, 'SansSemi', 6, W / 2, 515, (255, 255, 255), sstep(TL['card'] + 0.9, TL['card'] + 1.2, t))])
        composite_text(base, em, el)
    # watermark
    wm, wl = text_layer([])
    wf = font(24, 'Medium'); tracked(ImageDraw.Draw(wm), 'SLOW LIGHT', wf, W / 2, 1548, 10, 90)
    tracked(ImageDraw.Draw(wl), 'SLOW LIGHT', wf, W / 2, 1548, 10, CREAM + (int(255 * 0.35),))
    composite_text(base, wm, wl)
    return base.convert('RGB')


def composite_text(base, mask, layer, halo=12, k=0.8):
    h = mask.filter(ImageFilter.GaussianBlur(halo)).point(lambda v: min(255, int(v * k)))
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (h,)))
    base.alpha_composite(layer)


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        load_meta(sys.argv[5])
        draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
