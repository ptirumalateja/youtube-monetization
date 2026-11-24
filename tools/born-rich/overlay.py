"""Text layer for Born Rich (Slow Light Dark look, helpers from ../slow-light-dark-common/sld_text.py).

- Hook from frame 0: SAME GROUND. / SAME FINISH LINE.  (the 3-second test: the text says what is happening)
- Name tags above the runners' heads (screen positions from meta.json): MOTIVATION, DISCIPLINE, EGO; staggered at the
  start line so they do not overlap, then level.
- Beat captions: MOTIVATION BURNS OUT. / EGO TAKES THE LEAD. / EGO CELEBRATES TOO EARLY. / HE DIDN'T RUN. HE JUST ARRIVED.
- A red BORN RICH tag rides on the car from the moment it crosses the line, then above his head once he stands on the roof.
- End card over the darkened last frames: WAS IT EVER A / FAIR RACE? (FAIR RACE? in red), FOLLOW @SLOWLIGHTTV.

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
    fr = META['frames']; i = min(len(fr) - 1, max(0, round(t * TL['fps']))); return fr[i]


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


def composite(base, mask, layer, halo=12, k=0.8):
    h = mask.filter(ImageFilter.GaussianBlur(halo)).point(lambda v: min(255, int(v * k)))
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (h,)))
    base.alpha_composite(layer)


def caption(t, lines, t0, t1, y=168, size=58, colors=None):
    a = sstep(t0, t0 + 0.18, t) * (1 - sstep(t1 - 0.25, t1, t))
    pop = 1 + 0.06 * (1 - sstep(t0, t0 + 0.2, t))
    out = []
    for i, ln in enumerate(lines):
        out.append((ln, int(size * pop), 'ExtraBold', 4, W / 2, y + i * int(size * 1.3), (colors or [CREAM] * len(lines))[i], a))
    return out


def draw(img, t):
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    card = sstep(TL['card'], TL['card'] + 0.45, t)
    if card > 0:   # end card: the last picture darkens and softens under the question
        dark = ImageEnhance.Brightness(img.filter(ImageFilter.GaussianBlur(6 * card))).enhance(1 - 0.55 * card)
        img = Image.blend(img, dark, card)
    base = img.convert('RGBA'); m = frame_meta(t); items = []
    # hook
    items += caption(t, ['SAME GROUND.', 'SAME FINISH LINE.'], *TL['capHook'], y=160, size=78, colors=[CREAM, GOLD])
    items += caption(t, ['MOTIVATION', 'BURNS OUT.'], *TL['capBurn'])
    items += caption(t, ['EGO TAKES', 'THE LEAD.'], *TL['capLead'])
    items += caption(t, ['EGO CELEBRATES', 'TOO EARLY.'], *TL['capEgo'])
    items += caption(t, ["HE DIDN'T RUN.", 'HE JUST ARRIVED.'], *TL['capArrive'], colors=[CREAM, RED])
    # name tags over the heads (staggered at the start line)
    tag_a = sstep(0.15, 0.45, t) * (1 - card)
    lvl = sstep(1.2, 2.6, t)
    for k, name, st in (('M', 'MOTIVATION', 120), ('D', 'DISCIPLINE', 75), ('E', 'EGO', 30)):
        x, y, vis = m[k]
        if not vis: continue
        dy = 30   # lanes are stacked in the side view, no stagger needed
        a = tag_a * (0.7 if (k == 'M' and t > TL['burnout1']) else 1.0)
        items.append((name, 33, 'Bold', 5, x * W, y * H - dy - 40, CREAM, a))
    mask, layer = text_layer(items)
    # BORN RICH: red chip on the car
    ca = sstep(TL['carCross'], TL['carCross'] + 0.12, t) * (1 - card)
    if ca > 0 and m['carVis']:
        x, y, _ = m['car']
        if m.get('rich'):   # once he stands on the roof the tag rides above his head
            u = sstep(TL['richLand'], TL['richPose'], t); x = x + (m['rich'][0] - x) * u; y = y + (m['rich'][1] - y) * u
        f = font(36, 'ExtraBold'); w = width('BORN RICH', f, 5); cx, cy = x * W, y * H - 40
        pop = 1 + 0.15 * (1 - sstep(TL['carCross'], TL['carCross'] + 0.2, t))
        chip = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(chip)
        hw, hh = (w / 2 + 22) * pop, 32 * pop
        cd.rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=10, fill=RED + (int(235 * ca),))
        tracked(cd, 'BORN RICH', font(int(36 * pop), 'ExtraBold'), cx, cy - 22 * pop, 5, CREAM + (int(255 * ca),))
        shadow = Image.new('L', (W, H), 0); ImageDraw.Draw(shadow).rounded_rectangle([cx - hw, cy - hh, cx + hw, cy + hh], radius=10, fill=int(200 * ca))
        base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (shadow.filter(ImageFilter.GaussianBlur(14)),)))
        base.alpha_composite(chip)
    # end card
    if card > 0:
        a = sstep(TL['card'] + 0.15, TL['card'] + 0.5, t); pop = 1 + 0.05 * (1 - sstep(TL['card'] + 0.15, TL['card'] + 0.5, t))
        e_items = [('WAS IT EVER A', int(92 * pop), 'ExtraBold', 4, W / 2, 700, CREAM, a),
                   ('FAIR RACE?', int(118 * pop), 'ExtraBold', 4, W / 2, 820, RED, sstep(TL['card'] + 0.45, TL['card'] + 0.8, t)),
                   ('FOLLOW @SLOWLIGHTTV', 26, 'Bold', 8, W / 2, 1060, CREAM, 0.75 * sstep(TL['card'] + 1.0, TL['card'] + 1.4, t))]
        em, el = text_layer(e_items)
        mask = ImageChops.lighter(mask, em)
        layer.alpha_composite(el)
    # watermark
    wf = font(24, 'Medium'); wd = ImageDraw.Draw(layer)
    tracked(ImageDraw.Draw(mask), 'SLOW LIGHT', wf, W / 2, 1548, 10, 90)
    tracked(wd, 'SLOW LIGHT', wf, W / 2, 1548, 10, CREAM + (int(255 * 0.35),))
    composite(base, mask, layer)
    return base.convert('RGB')


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        load_meta(sys.argv[5])
        draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
