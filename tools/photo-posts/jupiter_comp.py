import sys, os, numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter, ImageFont
sys.path.insert(0, os.environ['JBDIR'])
from scene import tonemap
hdr = np.load(sys.argv[1]); out = sys.argv[2]
H, W = hdr.shape[:2]
# bloom: glow from bright pixels (Jupiter + Earth limb)
lum = hdr.mean(2)
bright = hdr * np.clip((lum - 0.35) / 0.6, 0, 1)[..., None]
bloom = sum(cv2.GaussianBlur(bright, (0, 0), s) * w for s, w in [(8, 0.25), (30, 0.30), (90, 0.35)])
# warm halo tint around Jupiter
bloom *= np.array([1.0, 0.82, 0.62], np.float32)
img = tonemap(hdr + bloom * 0.9, 1.05)
# lift the deep sky so no edge reads as a black border: add a soft violet-navy floor
yy = np.linspace(0, 1, H)[:, None, None]
floor = np.array([0.075, 0.06, 0.13]) * (1.0 - 0.5 * yy) + np.array([0.04, 0.03, 0.08])
img = 1 - (1 - img) * (1 - floor)
img = (np.clip(img, 0, 1) * 255).astype(np.uint8)
im = Image.fromarray(img).convert('RGBA')
F = '/usr/share/fonts/opentype/inter/'
def text_layer(lines):
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for (txt, font, y, col, track) in lines:
        # tracked text, centred
        widths = [d.textlength(c, font=font) for c in txt]
        tw = sum(widths) + track * (len(txt) - 1)
        x = (W - tw) / 2
        for c, w in zip(txt, widths):
            d.text((x, y), c, font=font, fill=col); x += w + track
    return lay
gold = (255, 196, 92, 255); white = (248, 244, 236, 255)
lines = [
    ('EARTH HAS A', ImageFont.truetype(F + 'Inter-ExtraBold.otf', 58), 120, white, 6),
    ('BODYGUARD', ImageFont.truetype(F + 'Inter-Black.otf' if os.path.exists(F + 'Inter-Black.otf') else F + 'Inter-ExtraBold.otf', 132), 182, gold, 4),
]
lay = text_layer(lines)
a = np.asarray(lay)[..., 3]
sh = Image.fromarray((cv2.GaussianBlur(a, (0, 0), 14) * 0.75).astype(np.uint8))
shadow = Image.new('RGBA', im.size, (8, 6, 20, 0)); shadow.putalpha(sh)
glow = Image.new('RGBA', im.size, (255, 170, 70, 0)); glow.putalpha(Image.fromarray((cv2.GaussianBlur(np.asarray(text_layer(lines[1:]))[..., 3], (0, 0), 22) * 0.45).astype(np.uint8)))
im = Image.alpha_composite(im, shadow); im = Image.alpha_composite(im, glow); im = Image.alpha_composite(im, lay)
# watermark
wm = text_layer([('SLOW LIGHT', ImageFont.truetype(F + 'Inter-SemiBold.otf', 22), H - 62, (255, 255, 255, 170), 9)])
wa = np.asarray(wm)[..., 3]
ws = Image.new('RGBA', im.size, (0, 0, 0, 0)); ws.putalpha(Image.fromarray((cv2.GaussianBlur(wa, (0, 0), 6) * 0.8).astype(np.uint8)))
im = Image.alpha_composite(im, ws); im = Image.alpha_composite(im, wm)
im.convert('RGB').save(out, quality=95)
a = np.asarray(im.convert('L')).astype(float)
for n, b in [('top', a[:150]), ('bot', a[-200:]), ('left', a[:, :80]), ('right', a[:, -80:])]: print(n, round(b.mean(), 1), round(b.std(), 1))
