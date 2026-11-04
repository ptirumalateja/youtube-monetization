"""Text overlay for Vault B stills: engraved-gold temple tag + one big line per beat.
python3 overlay.py SRC_DIR OUT_DIR   (reads raw-<shot>.png, writes NN-<shot>.jpg at 1080x1920)
"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 1080, 1920


def font(size, weight=700):
    f = ImageFont.truetype(os.path.join(HERE, 'fonts', 'Cinzel.ttf'), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def gold_fill(size):
    g = Image.new('RGB', size)
    d = ImageDraw.Draw(g)
    stops = [(0.0, (255, 246, 214)), (0.45, (240, 196, 110)), (0.55, (204, 146, 58)), (1.0, (255, 214, 140))]
    for y in range(size[1]):
        t = y / max(1, size[1] - 1)
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= t <= b:
                k = (t - a) / (b - a)
                d.line([(0, y), (size[0], y)], fill=tuple(int(ca[i] + (cb[i] - ca[i]) * k) for i in range(3)))
                break
    return g


def text_layer(img, text, f, cy, fill='gold', track=0, glow=(255, 170, 60), glow_r=18, glow_a=0.55, shadow=0.75):
    """Draw centred text at vertical centre cy with gold or cream fill, dark soft shadow and warm glow."""
    d0 = ImageDraw.Draw(img)
    # measure with tracking
    widths = [d0.textlength(ch, font=f) for ch in text]
    tw = sum(widths) + track * (len(text) - 1)
    asc, desc = f.getmetrics()
    th = asc + desc
    x0 = (W - tw) / 2
    y0 = cy - th / 2
    mask = Image.new('L', (W, H), 0)
    dm = ImageDraw.Draw(mask)
    x = x0
    for ch, w in zip(text, widths):
        dm.text((x, y0), ch, font=f, fill=255)
        x += w + track
    # shadow (keeps text legible on bright gold)
    sh = mask.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(12)).point(lambda v: min(255, int(v * shadow * 1.3)))
    img.paste(Image.new('RGB', (W, H), (20, 10, 4)), (0, 0), sh)
    # glow
    gl = mask.filter(ImageFilter.GaussianBlur(glow_r)).point(lambda v: int(v * glow_a))
    img.paste(Image.new('RGB', (W, H), glow), (0, 0), gl)
    # fill
    if fill == 'gold':
        bbox = mask.getbbox()
        gf = Image.new('RGB', (W, H))
        gf.paste(gold_fill((W, bbox[3] - bbox[1] + 2)), (0, bbox[1]))
        # engraved look: darker 2px edge below the letters
        edge = ImageChops.subtract(mask.transform(mask.size, Image.AFFINE, (1, 0, 0, 0, 1, -2)), mask)
        img.paste(Image.new('RGB', (W, H), (90, 52, 14)), (0, 0), edge)
        img.paste(gf, (0, 0), mask)
    else:
        img.paste(Image.new('RGB', (W, H), fill), (0, 0), mask)
    return img


def tag(img):
    """PADMANABHASWAMY TEMPLE · KERALA, engraved gold, top third, with thin rules."""
    sh = Image.new('L', (W, H), 0); ds = ImageDraw.Draw(sh); ds.ellipse((60, 200, 1020, 530), fill=150); sh = sh.filter(ImageFilter.GaussianBlur(70))
    img.paste(Image.new('RGB', (W, H), (26, 14, 5)), (0, 0), sh)
    f = font(62, 800)
    text_layer(img, 'PADMANABHASWAMY', f, 330, track=4, glow_r=16, glow_a=0.4, shadow=0.95)
    f2 = font(38, 700)
    text_layer(img, 'TEMPLE  ·  KERALA', f2, 412, track=10, glow_r=10, glow_a=0.3, shadow=0.95)
    d = ImageDraw.Draw(img)
    for y in (262, 466):
        d.line([(200, y), (880, y)], fill=(226, 178, 92), width=3)
    return img


def big(img, lines, cy=1180, size=92, fill=(255, 244, 222)):
    f = font(size, 900)
    step = int(size * 1.18)
    start = cy - step * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        text_layer(img, ln, f, start + i * step, fill=fill, track=2, glow_r=24, glow_a=0.5, shadow=1.0)
    return img


def small(img, lines, cy=1460, size=50):
    f = font(size, 600)
    step = int(size * 1.35)
    start = cy - step * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        text_layer(img, ln, f, start + i * step, fill=(255, 240, 214), track=1, glow_r=12, glow_a=0.35, shadow=0.9)
    return img


PLAN = [
    ('gold', lambda im: big(tag(im), ['THEY OPENED', 'FIVE DOORS.'])),
    ('door', lambda im: big(tag(im), ['THIS ONE,', 'THEY LEFT SHUT.'], cy=1520, size=84)),
    ('tower', lambda im: small(im, ['Beneath Padmanabhaswamy.', "India's richest room."], cy=1250, size=54)),
    ('vaults', lambda im: im),
    ('lamp', lambda im: big(im, ['THEN THEY', 'REACHED B.'], cy=1240)),
    ('macro', lambda im: small(im, ['No handle. No lock.', 'They say only a chant', 'can open it.'], cy=1300, size=56)),
    ('hand', lambda im: im),
    ('eyes', lambda im: small(big(im, ['STILL SHUT.'], cy=1180, size=104), ['Would you open it?'], cy=1330, size=58)),
]

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    for i, (shot, fn) in enumerate(PLAN, 1):
        im = Image.open(os.path.join(src, f'raw-{shot}.png')).convert('RGB').resize((W, H), Image.LANCZOS)
        clean = im.copy()
        im = fn(im)
        im.save(os.path.join(out, f'{i:02d}-{shot}.jpg'), quality=93)
        clean.save(os.path.join(out, f'{i:02d}-{shot}_clean.jpg'), quality=93)
        print('wrote', shot)
