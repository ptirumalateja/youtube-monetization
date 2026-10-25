"""DOUBT etched in the floor: alpha maps for the carved groove (dark) and its lit lower edge (highlight). Run once; writes doubt.png, doubt_hi.png."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
import numpy as np
W, H = 1024, 630
f = ImageFont.truetype('/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf', 250)
t = Image.new('L', (W, H), 0); d = ImageDraw.Draw(t)
x = W / 2 - (sum(d.textlength(c, font=f) for c in 'DOUBT') + 26 * 4) / 2
for c in 'DOUBT':
    d.text((x, H / 2 - 150), c, font=f, fill=255); x += d.textlength(c, font=f) + 26
rng = np.random.default_rng(3); n = (rng.random((H, W)) * 0.5 + 0.5)
wear = Image.fromarray((np.array(Image.fromarray((n * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(2))) ).astype('uint8'))
a = ImageChops.multiply(t.filter(ImageFilter.GaussianBlur(1.2)), wear)
a.save('doubt.png')
hi = ImageChops.subtract(t.filter(ImageFilter.GaussianBlur(1.2)), ImageChops.offset(t, 0, -5).filter(ImageFilter.GaussianBlur(1.2)))
hi = ImageChops.multiply(hi, wear); hi.point(lambda v: min(255, v * 2)).save('doubt_hi.png')
