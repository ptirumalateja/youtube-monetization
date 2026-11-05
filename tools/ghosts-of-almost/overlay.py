"""Caption overlay for Ghosts of Almost stills/frames.
python3 overlay.py IN.jpg OUT.jpg "LINE ONE|LINE TWO" [y_frac]
Big white Inter ExtraBold caps with a soft dark shadow, centred, upper third (clear of IG/FB top UI)."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONT = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'


def caption(im, lines, y_frac=0.17, size_frac=0.068):
    W, H = im.size
    f = ImageFont.truetype(FONT, int(W * size_frac))
    lh = int(W * size_frac * 1.18)
    y0 = int(H * y_frac)
    sh = Image.new('L', im.size, 0)
    ds = ImageDraw.Draw(sh)
    pos = []
    for i, s in enumerate(lines):
        w = ds.textlength(s, font=f)
        x, y = (W - w) / 2, y0 + i * lh
        pos.append((x, y, s))
        ds.text((x, y + W * 0.004), s, font=f, fill=200)
    sh = sh.filter(ImageFilter.GaussianBlur(W * 0.012))
    out = im.convert('RGB')
    out.paste(Image.new('RGB', im.size, (12, 7, 5)), (0, 0), sh)
    d = ImageDraw.Draw(out)
    for x, y, s in pos:
        d.text((x, y), s, font=f, fill=(255, 247, 232))
    return out


if __name__ == '__main__':
    src, dst, text = sys.argv[1:4]
    y = float(sys.argv[4]) if len(sys.argv) > 4 else 0.17
    caption(Image.open(src), text.split('|'), y).save(dst, quality=93)


def tags(im, items, size_frac=0.04):
    """items: [(text, cx, cy, angle_deg)] paper tags in screen space (pixels)."""
    W, H = im.size
    f = ImageFont.truetype(FONT, int(W * size_frac))
    out = im.convert('RGB')
    for text, cx, cy, ang in items:
        pad = int(W * 0.018)
        tw = int(ImageDraw.Draw(out).textlength(text, font=f))
        th = int(W * size_frac * 1.25)
        t = Image.new('RGBA', (tw + 2 * pad + 40, th + 2 * pad + 40), (0, 0, 0, 0))
        d = ImageDraw.Draw(t)
        d.rounded_rectangle((20, 20, 20 + tw + 2 * pad, 20 + th + 2 * pad), radius=int(W * 0.01), fill=(255, 246, 228, 255))
        d.text((20 + pad, 20 + pad - int(W * 0.004)), text, font=f, fill=(42, 29, 23, 255))
        t = t.rotate(ang, resample=Image.BICUBIC, expand=True)
        sh = Image.new('RGBA', t.size, (0, 0, 0, 0)); sh.putalpha(t.split()[3].point(lambda a: a * 0.55))
        sh = sh.filter(ImageFilter.GaussianBlur(W * 0.008))
        x, y = int(cx - t.width / 2), int(cy - t.height / 2)
        out.paste((10, 6, 4), (x + 6, y + 10), sh)
        out.paste(t, (x, y), t)
    return out
