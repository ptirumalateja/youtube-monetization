"""Text layer for Normal People vs Me (bedtime). One counter: the bedside clock, mirrored as a glowing HUD clock under the label.
Frame 0 carries "NORMAL PEOPLE:" + 9:00 PM over the flop, and the reel ends on the same flop, so it loops.

  python3 overlay.py still IN.jpg T OUT.jpg       overlay one rendered frame at time T
  python3 overlay.py frames IN_DIR OUT_DIR        overlay every fNNNNN.jpg (30 fps)
"""
import os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FONT_DIR = '/usr/share/fonts/truetype/jetbrains-mono'
W, H, FPS = 1080, 1920, 30
CREAM = (250, 240, 222); GOLD = (240, 184, 92); LED = (255, 96, 58); DIM = (200, 190, 175)
_f = {}
def font(size, weight='ExtraBold'):
    k = (size, weight)
    if k not in _f: _f[k] = ImageFont.truetype(os.path.join(FONT_DIR, f'JetBrainsMono-{weight}.ttf'), size)
    return _f[k]
def sstep(a, b, x):
    if b <= a: return 1.0 if x >= a else 0.0
    u = min(1.0, max(0.0, (x - a) / (b - a))); return u * u * (3 - 2 * u)
def win(t, a, b, fi=0.08, fo=0.1):
    if t < a or t > b: return 0.0
    return (1.0 if a <= 0 else sstep(a, a + fi, t)) * (1 - sstep(b - fo, b, t))
def tracked(d, text, size, cx, y, track, fill, weight='ExtraBold'):
    f = font(size, weight); ws = [d.textlength(c, font=f) for c in text]; tot = sum(ws) + track * (len(text) - 1); x = cx - tot / 2
    for c, w in zip(text, ws): d.text((x, y), c, font=f, fill=fill); x += w + track
    return tot

def clock_at(t):
    """(text, minutes) shown on the HUD clock; mirrors scene.js."""
    if t < 1.45: m = 21 * 60
    elif t < 2.4: m = 21 * 60 + 5
    elif t < 4.0: m = 21 * 60
    elif t < 5.0: m = 21 * 60 + 30
    elif t < 6.0: m = 22 * 60
    elif t < 8.4: m = 23 * 60
    elif t < 10.5: u = min(1.0, (t - 8.4) / 2.15); m = 23 * 60 + int(u ** 1.8 * 240)
    elif t < 12.8: m = 27 * 60
    elif t < 14.2: m = 28 * 60 + 59
    else: m = 29 * 60
    m %= 1440; h, mm = divmod(m, 60)
    return f'{(h % 12) or 12}:{mm:02d} {"AM" if h < 12 else "PM"}', m

def layer(t):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); G = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); g = ImageDraw.Draw(G)
    def both(text, size, y, col, a, track=4, glow=None):
        tracked(d, text, size, W / 2, y, track, col + (int(255 * a),))
        tracked(g, text, size, W / 2, y, track, (glow or col) + (int(200 * a),))
    # label
    a = win(t, 0, 2.38, 0, 0.04)
    if a: both('NORMAL PEOPLE:', 84, 230, CREAM, a)
    a = win(t, 2.4, 4.0, 0.0, 0.08)
    if a: both('ME:', 120, 210, GOLD, a)
    # the HUD clock (hidden on the window insert and after the alarm line takes over)
    txt, m = clock_at(t)
    show = (t < 13.4 or 14.2 <= t < 15.7)
    if show:
        slam = 1.0 + 0.35 * (1 - sstep(10.5, 10.75, t)) * (t >= 10.5) + 0.35 * (1 - sstep(14.2, 14.45, t)) * (t >= 14.2)
        size = int(150 * slam) if t >= 10.5 else 130
        y = 350 if t < 4.0 else 250
        col = LED if t >= 10.5 else (255, 140, 96)
        both(txt, size, y - (size - 130) // 2, col, 1.0, 2, LED)
    # rehooks and lines
    a = win(t, 7.35, 8.4)
    if a: both('JUST ONE VIDEO.', 76, 1460, CREAM, a)
    a = win(t, 15.75, 18.6, 0.06, 0.15)
    if a: both('ALARM IN', 96, 250, CREAM, a); both('1 HOUR.', 150, 360, GOLD, a)
    a = win(t, 17.3, 19.5, 0.12, 0.04)
    if a: both('TAG YOUR', 70, 1470, CREAM, a); both('3 AM FRIEND.', 84, 1550, GOLD, a)
    return L, G

def compose(img, t):
    img = img.convert('RGB').resize((W, H)); L, G = layer(t)
    glow = G.filter(ImageFilter.GaussianBlur(14)); sh = L.split()[3].filter(ImageFilter.GaussianBlur(8)).point(lambda v: int(v * 0.7))
    base = img.convert('RGBA'); base.alpha_composite(Image.merge('RGBA', (Image.new('L', (W, H), 0),) * 3 + (sh,)))
    base.alpha_composite(glow); base.alpha_composite(L); return base.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        compose(Image.open(sys.argv[2]), float(sys.argv[3])).save(sys.argv[4], quality=93)
    elif sys.argv[1] == 'frames':
        src, dst = sys.argv[2], sys.argv[3]; os.makedirs(dst, exist_ok=True)
        for fn in sorted(os.listdir(src)):
            if not fn.endswith('.jpg'): continue
            o = os.path.join(dst, fn)
            if os.path.exists(o): continue
            compose(Image.open(os.path.join(src, fn)), int(fn[1:6]) / FPS).save(o, quality=93)
