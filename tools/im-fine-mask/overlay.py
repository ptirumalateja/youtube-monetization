"""Text layer for I'm Fine (Slow Light Dark series look, copied from the pilot tools/chain-never-locked/overlay.py).

Top centre, wide-tracked small caps in cream (JetBrains Mono, OFL), soft dark halo for legibility over the beam.
Small captions use the same font. "SLOW LIGHT" watermark bottom centre at 35% opacity.

  python3 overlay.py still IN.jpg T OUT.jpg     overlay one rendered frame at time T (seconds)
  (compose.py imports draw() for the full video)
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
FONT_DIR = '/usr/share/fonts/truetype/jetbrains-mono'
CREAM = (237, 230, 214)
W, H = 1080, 1920
_fonts = {}


def font(size, weight='SemiBold'):
    k = (size, weight)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(os.path.join(FONT_DIR, f'JetBrainsMono-{weight}.ttf'), size)
    return _fonts[k]


def tracked(draw, text, f, cx, y, track, fill):
    """Draw text centred on cx with extra letter spacing (track, px)."""
    widths = [draw.textlength(c, font=f) for c in text]
    total = sum(widths) + track * (len(text) - 1)
    x = cx - total / 2
    for c, w in zip(text, widths):
        draw.text((x, y), c, font=f, fill=fill)
        x += w + track


def sstep(a, b, x):
    u = min(1.0, max(0.0, (x - a) / (b - a)))
    return u * u * (3 - 2 * u)


ARR = [0] + [b for a, b in TL['truck']]


def blocks(t):
    """Text blocks visible at t: (lines, size, track, y, alpha). A line may be a list of (word, alpha) pairs."""
    out = []
    # hook: on from frame 0, out as the camera leaves the first pool
    a = sstep(-0.01, 0.12, t) * (1 - sstep(1.75, 2.0, t))
    if a > 0:
        out.append((['HE WORE IT EVERYWHERE.'], 46, 9, 262, a))
    # WORK. FRIENDS. FAMILY. -- one small line, each word arrives with its pool; all gone as he leaves the last one
    a = 1 - sstep(TL['truck'][3][0], TL['truck'][3][0] + 0.25, t)
    if t >= ARR[1] - 0.15 and a > 0:
        words = [(w, sstep(ARR[k] - 0.15, ARR[k] + 0.1, t)) for k, w in ((1, 'WORK.'), (2, 'FRIENDS.'), (3, 'FAMILY.'))]
        out.append(([words], 34, 8, 262, a))
    # the end line
    a = sstep(TL['endText'], TL['endText'] + 0.4, t)
    if a > 0:
        out.append((['SOMEONE HAS TO', 'GO FIRST.'], 50, 9, 262, a))
    return out


def draw(img, t):
    """Return img (RGB, 1080x1920) with the text layer for time t."""
    if img.size != (W, H):
        img = img.resize((W, H), Image.LANCZOS)
    txt = Image.new('L', (W, H), 0)
    d = ImageDraw.Draw(txt)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for lines, size, track, y0, a in blocks(t):
        f = font(size)
        for i, line in enumerate(lines):
            y = y0 + i * int(size * 1.45)
            if isinstance(line, list):   # words with their own alpha, laid out as one centred line (gaps kept for words still to come)
                text = '  '.join(w for w, _ in line); widths = [d.textlength(c, font=f) for c in text]
                x = W / 2 - (sum(widths) + track * (len(text) - 1)) / 2
                for w, wa in line:
                    ww = sum(d.textlength(c, font=f) for c in w) + track * (len(w) - 1)
                    if wa > 0:
                        tracked(d, w, f, x + ww / 2, y, track, int(255 * a * wa))
                        tracked(ld, w, f, x + ww / 2, y, track, CREAM + (int(255 * a * wa),))
                    x += ww + track + 2 * (d.textlength(' ', font=f) + track)
                continue
            tracked(d, line, f, W / 2, y, track, int(255 * a))
            tracked(ld, line, f, W / 2, y, track, CREAM + (int(255 * a),))
    # watermark
    wf = font(24, 'Medium')
    tracked(d, 'SLOW LIGHT', wf, W / 2, 1548, 10, 90)
    tracked(ld, 'SLOW LIGHT', wf, W / 2, 1548, 10, CREAM + (int(255 * 0.35),))
    halo = txt.filter(ImageFilter.GaussianBlur(9)).point(lambda v: min(255, int(v * 1.1)))
    base = img.convert('RGBA')
    base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (halo.point(lambda v: int(v * 0.55)),)))
    base.alpha_composite(layer)
    return base.convert('RGB')


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        draw(Image.open(sys.argv[2]).convert('RGB'), float(sys.argv[3])).save(sys.argv[4], quality=94)
