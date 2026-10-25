"""Text + divider layer for The 100th Hit (Slow Light Dark series look, shared helpers in ../slow-light-dark-common/sld_text.py).

Split screen: a thin gold divider at y 960; the hook and the end line sit on the divider (the line opens behind them).
Per-half hit counters (monotonic, from meta.json) at the top of each half; at 99 the top counter becomes QUITS AT 99,
at 100 the bottom one becomes HITS 100. "SLOW LIGHT" watermark bottom centre at 35%.

  python3 overlay.py still IN.jpg T OUT.jpg [META]     overlay one rendered frame at time T
  (compose.py imports draw() for the full video)
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_text import font, tracked, sstep, CREAM, W, H

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
GOLD = (232, 184, 90)
MID = H // 2
Y_TOP, Y_BOT = 196, MID + 86          # counter / label rows (top of each half; clear of the platform UI)
HT = None                             # hit times, set from meta.json (load_meta)


def load_meta(path):
    global HT
    HT = json.load(open(path))['events']['HT']


def hits(t, half):
    top = 99 if half == 0 else 100
    return sum(1 for k in range(1, top + 1) if HT[k] <= t)


def text_rows(t):
    """[(lines, size, track, y_top, alpha)]"""
    out = []
    a = sstep(-0.01, 0.1, t) * (1 - sstep(1.75, 1.98, t))
    if a > 0:
        out.append((['ONE OF THEM QUITS.'], 46, 9, MID - 30, a))
    for half, y in ((0, Y_TOP), (1, Y_BOT)):
        n = hits(t, half)
        lab_t = TL['quitText'] if half == 0 else TL['hitText']
        la = sstep(lab_t, lab_t + 0.3, t)
        out.append(([str(n)], 60, 14, y, 1 - la))
        if la > 0:
            out.append((['QUITS AT 99' if half == 0 else 'HITS 100'], 50, 12, y + 4, la))
    a = sstep(TL['endText'], TL['endText'] + 0.4, t)
    if a > 0:
        out.append((['YOU NEVER KNOW', 'WHICH HIT IS THE LAST.'], 40, 8, MID - 52, a))
    return out


def draw(img, t):
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    rows = text_rows(t)
    # divider: gold hairline with a soft glow, opened behind any text sitting on it
    div = Image.new('L', (W, H), 0); dd = ImageDraw.Draw(div)
    dd.rectangle([0, MID - 1, W, MID], fill=255)
    gap = Image.new('L', (W, H), 255); gd = ImageDraw.Draw(gap)
    for lines, size, track, y0, a in rows:
        if y0 < MID < y0 + len(lines) * size * 1.45 + 10:
            f = font(size); wmax = max(sum(gd.textlength(c, font=f) for c in l) + track * (len(l) - 1) for l in lines)
            g = int(255 * (1 - a)); gd.rectangle([W / 2 - wmax / 2 - 36, MID - 4, W / 2 + wmax / 2 + 36, MID + 4], fill=g)
    gap = gap.filter(ImageFilter.GaussianBlur(10))
    div = Image.composite(div, Image.new('L', (W, H), 0), gap)
    glow = div.filter(ImageFilter.GaussianBlur(6)).point(lambda v: int(v * 0.5))
    base = img.convert('RGBA')
    for m, op in ((glow, 1.0), (div, 0.9)):
        base.alpha_composite(Image.merge('RGBA', [Image.new('L', (W, H), c) for c in GOLD] + [m.point(lambda v: int(v * op))]))
    # text
    mask = Image.new('L', (W, H), 0); md = ImageDraw.Draw(mask)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(layer)
    for lines, size, track, y0, a in rows:
        if a <= 0: continue
        f = font(size)
        for i, line in enumerate(lines):
            y = y0 + i * int(size * 1.45)
            tracked(md, line, f, W / 2, y, track, int(255 * a))
            tracked(ld, line, f, W / 2, y, track, CREAM + (int(255 * a),))
    wf = font(24, 'Medium')
    tracked(md, 'SLOW LIGHT', wf, W / 2, 1548, 10, 90)
    tracked(ld, 'SLOW LIGHT', wf, W / 2, 1548, 10, CREAM + (int(255 * 0.35),))
    halo = mask.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, int(v * 1.1 * 0.6)))
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (halo,)))
    base.alpha_composite(layer)
    return base.convert('RGB')


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        load_meta(sys.argv[5] if len(sys.argv) > 5 else os.path.join(HERE, 'output', 'meta.json'))
        draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
