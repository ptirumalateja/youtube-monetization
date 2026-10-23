"""Two shots joined by a hard cut, optional hook text, piped to ffmpeg as raw RGB.

usage: assemble2.py FRAMEDIR W H [notext]
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D, W, H = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
TEXT = len(sys.argv) < 5
CREAM = (246, 236, 214)
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
HOOK = "NOTHING ESCAPES THIS."
s = W / 1080


def hook_layer(alpha, shown, size=70, y=1420, track=0.06):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if alpha <= 0 or shown < 1:
        return lay
    f = ImageFont.truetype(FONT, int(size * s))
    d = ImageDraw.Draw(lay)
    sp = size * s * track
    widths = [d.textlength(c, font=f) for c in HOOK]
    x = (W - (sum(widths) + sp * (len(HOOK) - 1))) / 2
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow)
    for k, c in enumerate(HOOK[:shown]):
        ds.text((x, y * s), c, font=f, fill=(0, 0, 0, int(210 * alpha)))
        d.text((x, y * s), c, font=f, fill=CREAM + (int(255 * alpha),))
        x += widths[k] + sp
    return Image.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10 * s)), lay)


def ramp(t, a, b):
    return min(max((t - a) / (b - a), 0.0), 1.0)


out = sys.stdout.buffer
for sh in (0, 1):
    for f in range(150):
        img = Image.open(f"{D}/s{sh}_{f:04d}.png").convert("RGBA")
        t = sh * 5 + f / 30
        if TEXT and sh == 0:
            n = int(len(HOOK) * ramp(t, 0.0, 0.8) + 0.999)
            img = Image.alpha_composite(img, hook_layer(1 - ramp(t, 2.6, 3.2), n))
        out.write(np.asarray(img.convert("RGB")).tobytes())
