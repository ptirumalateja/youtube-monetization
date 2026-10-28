"""Text layer for The Salary Loop V3 (19.3 s). Everything reads timeline.json.

One overlay at a time, never over his face:
  0.0-2.5   SALARY CREDITED +₹50,000 card blooming out of the phone glow; GUESS WHICH DAY / IT HITS ZERO. typed by 1.0 s
  debits    a crimson-edged card per buzz: LABEL -AMOUNT · LEFT (the balance only falls)
  zero      DAY 6. / ₹0.  then  24 DAYS OF WORK LEFT. (the pad is still thick)
  false hope  LOW BALANCE · ₹0
  close     WHICH DAY BROKE YOU?  then the hook starts typing again in the last 6 frames (the loop)
No balance pill, no day counter text, no alarm card: the tear-off calendar is the counter.

  python3 overlay_v3.py still IN.jpg T OUT.jpg
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
W, H = 1080, 1920
FD = '/usr/share/fonts/truetype/jetbrains-mono'
CREAM = (246, 238, 222); GOLD = (240, 196, 112); CRIMSON = (226, 84, 66); GREEN = (40, 140, 84); INK = (34, 28, 24)
_f = {}


def font(size, w='SemiBold'):
    k = (size, w)
    if k not in _f: _f[k] = ImageFont.truetype(os.path.join(FD, f'JetBrainsMono-{w}.ttf'), size)
    return _f[k]


def sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


def money(v): return '₹' + f'{int(v):,}'


RUPEE = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'   # JetBrains Mono has no ₹ glyph
_rf = {}


def gf(c, f):
    if c != '₹': return f
    k = f.size
    if k not in _rf: _rf[k] = ImageFont.truetype(RUPEE, int(k * 0.92))
    return _rf[k]


def tracked(d, text, f, cx, y, track, fill, anchor='c'):
    ws = [d.textlength(c, font=gf(c, f)) for c in text]; tw = sum(ws) + track * (len(text) - 1)
    x = cx - tw / 2 if anchor == 'c' else cx
    for c, w in zip(text, ws): d.text((x, y + (f.size * 0.06 if c == '₹' else 0)), c, font=gf(c, f), fill=fill); x += w + track
    return tw


def big_lines(layer, mask, lines, y0, a, size=78, gap=None, cols=None, typed=None):
    """Top lines: wide-tracked caps with a soft halo. typed = number of characters shown (type-on)."""
    if a <= 0: return
    gap = gap or int(size * 1.32); d = ImageDraw.Draw(layer); md = ImageDraw.Draw(mask); n = typed if typed is not None else 10 ** 6
    for i, ln in enumerate(lines):
        show = ln[:max(0, n)]; n -= len(ln)
        if not show: break
        c = (cols or [CREAM])[min(i, len(cols or [CREAM]) - 1)]; f = font(size, 'Bold')
        # centre on the full line so typing does not slide
        full = sum(d.textlength(ch, font=gf(ch, f)) for ch in ln) + 6 * (len(ln) - 1)
        x0 = W / 2 - full / 2
        tracked(md, show, f, x0, y0 + i * gap, 6, int(255 * a), anchor='l'); tracked(d, show, f, x0, y0 + i * gap, 6, c + (int(255 * a),), anchor='l')


def rr(d, box, r, fill, outline=None, width=0): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)


def card(layer, y, a, kind, title, amount, sub=None, scale=1.0):
    """kind 'credit' (cream, green amount) or 'debit' (dark, crimson edge). Drawn on its own layer for the soft shadow."""
    if a <= 0: return
    w, h = int(760 * scale), int(200 * scale); x0 = (W - w) // 2; c = Image.new('RGBA', (W, h + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
    sh = Image.new('RGBA', (W, h + 80), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x0 + 6, 46, x0 + w + 6, 40 + h + 12], 34, fill=(0, 0, 0, 150)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
    if kind == 'credit':
        rr(d, [x0, 40, x0 + w, 40 + h], 34, (250, 246, 236, 250), (226, 186, 96, 255), 4)
        rr(d, [x0 + 32, 72, x0 + 102, 142], 18, (244, 186, 70, 255)); d.ellipse([x0 + 52, 88, x0 + 82, 122], fill=(255, 255, 255, 255)); d.rectangle([x0 + 49, 112, x0 + 85, 120], fill=(255, 255, 255, 255))
        tracked(d, 'SLOW LIGHT BANK', font(24, 'Medium'), x0 + 128, 74, 3, (110, 96, 84, 255), anchor='l')
        tracked(d, title, font(34, 'Bold'), x0 + 128, 108, 5, INK + (255,), anchor='l')
        tracked(d, amount, font(64, 'Bold'), x0 + 128, 150, 2, GREEN + (255,), anchor='l')
    else:
        rr(d, [x0, 40, x0 + w, 40 + h], 34, (24, 20, 22, 238), CRIMSON + (255,), 4)
        rr(d, [x0 + 32, 72, x0 + 102, 142], 18, CRIMSON + (255,)); tracked(d, '₹', font(46, 'Bold'), x0 + 50, 78, 0, (255, 255, 255, 255), anchor='l')
        tracked(d, title, font(32, 'Bold'), x0 + 128, 76, 4, CREAM + (255,), anchor='l')
        tracked(d, amount, font(58, 'Bold'), x0 + 128, 118, 2, CRIMSON + (255,), anchor='l')
        if sub: tracked(d, sub, font(30, 'SemiBold'), x0 + w - 36 - sum(d.textlength(ch, font=gf(ch, font(30, 'SemiBold'))) for ch in sub) - 2 * len(sub), 140, 2, (CRIMSON if sub.startswith('₹0') else (214, 204, 186)) + (255,), anchor='l')
    if a < 1: c.putalpha(c.getchannel('A').point(lambda v: int(v * a)))
    layer.alpha_composite(c, (0, int(y) - 40))


def debit_at(t):
    """The debit card on screen at t: (alpha, slide, row) or None. Each holds until 0.1 s before the next buzz (min 0.5 s)."""
    D = TL['debits']
    for i, (tc, lab, amt, left) in enumerate(D):
        tn = D[i + 1][0] - 0.12 if i + 1 < len(D) else tc + 1.1
        if tc - 0.05 <= t < tn + 0.12:
            a = sstep(tc - 0.05, tc + 0.08, t) * (1 - sstep(tn, tn + 0.12, t)); return a, sstep(tc - 0.05, tc + 0.12, t), (lab, amt, left)
    return None


def draw(img, t):
    if img.size != (W, H): img = img.resize((W, H), Image.LANCZOS)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0)); mask = Image.new('L', (W, H), 0)
    # ---- the hook: credit card + typed line (and its restart in the last 6 frames)
    ca = sstep(0.0, 0.22, t) * (1 - sstep(2.3, 2.6, t))
    if ca > 0:
        rise = sstep(0.0, 0.5, t); y = 560 + 40 * (1 - rise) - 60 * sstep(2.3, 2.6, t)   # floats over the bed under the hook line, V2 style
        card(layer, y, ca, 'credit', 'SALARY CREDITED', '+₹50,000', scale=0.86 + 0.14 * rise - 0.3 * sstep(2.3, 2.6, t))
    hook = ['YOUR SALARY', 'LASTS 6 DAYS.']; nchar = len(''.join(hook))
    if t < 2.8:
        big_lines(layer, mask, hook, 150, 1 - sstep(2.45, 2.75, t), size=84, cols=[CREAM, GOLD], typed=int(nchar * sstep(0.05, 0.9, t) + 0.999))
    if t > TL['duration'] - 0.2:
        big_lines(layer, mask, hook, 150, 1, size=84, cols=[CREAM, GOLD], typed=int(nchar * (t - (TL['duration'] - 0.2)) / 0.95 + 0.999))
    # ---- debits (street + desk)
    dc = debit_at(t)
    if dc:
        a, sl, (lab, amt, left) = dc; y = 1300 - 60 * sl
        card(layer, y, a, 'debit', lab, '-' + money(amt), sub=f'{money(left)} LEFT')
        di = [r[1] for r in TL['debits']].index(lab) + 1   # the hook's promise, paid off visually: DAY 1 ... DAY 6
        dl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(dl); tracked(dd, f'DAY {di}', font(34, 'Bold'), W / 2 - 380 + 4, y - 56, 6, GOLD + (int(255 * a),), anchor='l'); layer.alpha_composite(dl)
    # ---- zero, then the thick pad
    za = sstep(TL['zero'] + 0.08, TL['zero'] + 0.2, t) * (1 - sstep(TL['reveal'][0] - 0.1, TL['reveal'][0] + 0.05, t))
    big_lines(layer, mask, ['DAY 6.', '₹0.'], 150, za, size=118, cols=[CREAM, CRIMSON])
    ra = sstep(TL['reveal'][0], TL['reveal'][0] + 0.15, t) * (1 - sstep(TL['reveal'][1] - 0.05, TL['reveal'][1] + 0.1, t))
    big_lines(layer, mask, ['24 DAYS', 'OF WORK LEFT.'], 150, ra, size=86, cols=[GOLD, CREAM])
    # ---- false hope
    fh = TL['falseHope']; fa = sstep(fh[0] + 0.12, fh[0] + 0.22, t) * (1 - sstep(fh[0] + 0.75, fh[0] + 0.9, t))
    card(layer, 1300, fa, 'debit', 'LOW BALANCE', '₹0', sub='DAY 27')
    # ---- the close
    cl = sstep(15.5, 15.8, t) * (1 - sstep(18.4, 18.7, t))
    big_lines(layer, mask, ["WHICH DAY", "BROKE YOU?"], 150, cl, size=88, cols=[CREAM, GOLD])
    wk = sstep(10.95, 11.15, t) * (1 - sstep(14.75, 14.95, t))
    big_lines(layer, mask, ["YOUR WORK", "LASTS ALL 30."], 150, wk, size=84, cols=[CREAM, GOLD])   # the payoff line, held over the time-lapse
    # ---- watermark
    d = ImageDraw.Draw(layer); md = ImageDraw.Draw(mask)
    tracked(d, 'SLOW LIGHT', font(24, 'Medium'), W / 2, 1548, 10, CREAM + (80,)); tracked(md, 'SLOW LIGHT', font(24, 'Medium'), W / 2, 1548, 10, 80)
    halo = mask.filter(ImageFilter.GaussianBlur(10)).point(lambda v: min(255, int(v * 0.6)))
    base = img.convert('RGBA'); base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (halo,))); base.alpha_composite(layer)
    return base.convert('RGB')


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=92)
