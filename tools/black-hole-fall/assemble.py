"""Loop crossfade + text, piped to ffmpeg as raw RGB.

usage: assemble.py FRAMEDIR W H | ffmpeg -f rawvideo -pix_fmt rgb24 -s WxH -r 30 -i - ...
Frames are fNNNNN.png with NNNNN = frame index + 100; indices -24..-1 are the pre-roll
(camera slightly farther out) that the last 24 frames dissolve into, so the reel loops.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D, W, H = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
L, X = 540, 24
CREAM = (246, 236, 214)
FONT = "/usr/share/fonts/opentype/inter/InterDisplay-SemiBold.otf"
s = W / 1080


def load(i):
    return np.asarray(Image.open(f"{D}/f{i + 100:05d}.png").convert("RGB"), np.float32)


def text_layer(txt, size, y, alpha, shown, track=0.06):
    """Centered, letter-spaced line; `shown` characters typed so far."""
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if alpha <= 0 or shown < 1:
        return lay
    f = ImageFont.truetype(FONT, int(size * s))
    d = ImageDraw.Draw(lay)
    sp = size * s * track
    widths = [d.textlength(c, font=f) for c in txt]
    total = sum(widths) + sp * (len(txt) - 1)
    x = (W - total) / 2
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(shadow)
    for k, c in enumerate(txt[:shown]):
        ds.text((x, y * s), c, font=f, fill=(0, 0, 0, int(200 * alpha)))
        d.text((x, y * s), c, font=f, fill=CREAM + (int(255 * alpha),))
        x += widths[k] + sp
    shadow = shadow.filter(ImageFilter.GaussianBlur(10 * s))
    return Image.alpha_composite(shadow, lay)


def ramp(t, a, b):
    return min(max((t - a) / (b - a), 0.0), 1.0)


HOOK = "YOU'RE FALLING IN."
END = "NOTHING COMES BACK."
out = sys.stdout.buffer
for i in range(L):
    fr = load(i)
    if i >= L - X:
        w = (i - (L - X) + 1) / X
        w = w * w * (3 - 2 * w)
        fr = fr * (1 - w) + load(i - L) * w
    t = i / 30.0
    img = Image.fromarray(np.clip(fr + 0.5, 0, 255).astype(np.uint8)).convert("RGBA")
    # hook: typed by 0.75 s, holds, fades out by 3.4 s
    n = int(len(HOOK) * ramp(t, 0.0, 0.75) + 0.999)
    a = 1 - ramp(t, 2.8, 3.4)
    img = Image.alpha_composite(img, text_layer(HOOK, 74, 1330, a, n))
    # closing line: fades in at 13.4 s, gone before the loop dissolve
    a2 = ramp(t, 13.4, 14.2) * (1 - ramp(t, 16.4, 17.1))
    img = Image.alpha_composite(img, text_layer(END, 64, 1330, a2, len(END)))
    out.write(np.asarray(img.convert("RGB")).tobytes())
