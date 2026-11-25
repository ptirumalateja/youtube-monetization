"""Text layer for What Are You Carrying (Slow Light Dark look, helpers from ../slow-light-dark-common/sld_text.py).

- Hook from frame 0 (the 3-second test: the text says what is happening): TRYING TO REACH / A NEW LIFE...  then
  ...WHILE CARRYING / THE OLD ONE.
- Small place names on the wide shots: OLD LIFE at the foot of the hill, NEW LIFE at the top under the lamp.
- Beat captions: IT'S NOT THE CLIMB. / IT'S THE WEIGHT.   LET IT GO.
- A red chip names each stone as he lifts it and throws it: FEAR, EXCUSES, SELF-DOUBT, TOXIC PEOPLE, BAD HABITS.
- End card at the top of the frame, over the enlightenment (no darkening; it lands as he reaches the flag):
  WHAT ARE YOU / STILL CARRYING? + FOLLOW @SLOWLIGHTTV.
All captions sit below the Reels/Shorts top bar (y >= 270).

  python3 overlay.py still IN.jpg T OUT.jpg META     overlay one rendered frame at time T
  (compose.py imports draw() for the full video)
"""
import json, os, sys
from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_text import font, tracked, sstep, CREAM, W, H

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
        tracked(md, text, f, cx, y, track, int(255 * a)); tracked(ld, text, f, cx, y, track, rgb + (int(255 * a),))
    return mask, layer


def caption(t, lines, t0, t1, y=290, size=58, colors=None):
    a = sstep(t0, t0 + 0.18, t) * (1 - sstep(t1 - 0.25, t1, t))
    pop = 1 + 0.06 * (1 - sstep(t0, t0 + 0.2, t))
    return [(ln, int(size * pop), 'ExtraBold', 4, W / 2, y + i * int(size * 1.3), (colors or [CREAM] * len(lines))[i], a) for i, ln in enumerate(lines)]


def chip(base, text, cx, cy, a, pop=1.0, size=38):
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


def draw(img, t):
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    card = sstep(TL['card'], TL['card'] + 0.5, t)
    if card > 0:
        img = ImageEnhance.Brightness(img).enhance(1 - 0.08 * card)   # the enlightenment stays visible under the question
    base = img.convert('RGBA'); m = frame_meta(t); items = []
    items += caption(t, ['TRYING TO REACH', 'A NEW LIFE...'], *TL['capA'], y=280, size=68, colors=[CREAM, GOLD])
    items += caption(t, ['...WHILE CARRYING', 'THE OLD ONE.'], *TL['capB'], y=280, size=68, colors=[CREAM, CREAM])
    items += caption(t, ["IT'S NOT THE CLIMB.", "IT'S THE WEIGHT."], *TL['capC'], colors=[CREAM, GOLD])
    items += caption(t, ['LET IT GO.'], *TL['capD'], size=72, colors=[GOLD])
    # place names on the wide shots
    wide = (1 - sstep(TL['push0'], TL['push0'] + 0.4, t)) + sstep(TL['pull1'] - 0.2, TL['pull1'] + 0.4, t) * (1 - card)
    nl = 'newLife' if t > TL['pull1'] else 'newLifeWide'   # on the hill top in the opening, at the flag at the end
    for key, name, col in (('oldLife', 'OLD LIFE', CREAM), (nl, 'NEW LIFE', GOLD)):
        x, y, vis = m[key]
        if vis and 0.04 < x < 0.96 and 0.05 < y < 0.92:
            hw = width(name, font(28, 'Bold'), 6) / 2 + 30
            items.append((name, 28, 'Bold', 6, min(max(x * W, hw), W - hw), y * H - 60, col, 0.85 * min(1.0, wide)))
    mask, layer = text_layer(items)
    composite_text(base, mask, layer)
    # the stones' names: from the moment he lifts each one until shortly after it leaves his hand
    for i, (T, name) in enumerate(zip(TL['throws'], TL['labels'])):
        s = m['stones'][i]
        if not s: continue
        a = sstep(T - 0.5, T - 0.38, t) * (1 - sstep(T + 0.35, T + 0.6, t))
        if a > 0:
            chip(base, name, s[0] * W, s[1] * H - 30, a, 1 + 0.12 * (1 - sstep(T - 0.5, T - 0.3, t)))
    # end card
    if card > 0:
        a = sstep(TL['card'] + 0.2, TL['card'] + 0.55, t); pop = 1 + 0.05 * (1 - a)
        em, el = text_layer([('WHAT ARE YOU', int(80 * pop), 'ExtraBold', 4, W / 2, 285, CREAM, a),
                             ('STILL CARRYING?', int(84 * pop), 'ExtraBold', 4, W / 2, 390, GOLD, sstep(TL['card'] + 0.5, TL['card'] + 0.85, t)),
                             ('FOLLOW @SLOWLIGHTTV', 26, 'Bold', 8, W / 2, 520, CREAM, 0.75 * sstep(TL['card'] + 1.1, TL['card'] + 1.5, t))])
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
