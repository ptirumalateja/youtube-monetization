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
