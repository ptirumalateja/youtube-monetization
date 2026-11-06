"""HUD overlay for paper-fold plates: caption, FOLDS counter, THICKNESS, landmark callout.
usage: python3 hud.py plate.png out.jpg folds thickness "caption" [callout_title callout_sub x y]
"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

F = '/usr/share/fonts/opentype/inter/'
CREAM = (246, 239, 226); RED = (230, 84, 58)

def font(name, size): return ImageFont.truetype(F + name, size)

def shadowed(base, draw_fn, blur=10, alpha=150):
    W, H = base.size
    sh = Image.new('L', (W, H), 0); draw_fn(ImageDraw.Draw(sh), True)
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * alpha // 255)
    base.paste((10, 6, 4), (0, 0), sh)
    draw_fn(ImageDraw.Draw(base), False)

def hud(plate, out, folds, thick, caption, callout=None, down=False):
    im = Image.open(plate).convert('RGB'); W, H = im.size; s = W / 1080
    x0 = int(84 * s); ycap = int(250 * s)
    fc = font('InterDisplay-SemiBold.otf', int(46 * s)); fl = font('InterDisplay-Bold.otf', int(30 * s))
    fn = font('InterDisplay-Black.otf', int(260 * s)); fv = font('InterDisplay-ExtraBold.otf', int(74 * s))
    fsub = font('InterDisplay-SemiBold.otf', int(30 * s))
    def draw(d, mask):
        c = (lambda col: 255) if mask else (lambda col: col)
        d.text((x0, ycap), caption, font=fc, fill=c(CREAM))
        y = ycap + int(110 * s)
        d.text((x0 + 6 * s, y), 'FOLDS', font=fl, fill=c(RED)); y += int(36 * s)
        d.text((x0, y - 30 * s), str(folds), font=fn, fill=c(CREAM)); y += int(250 * s)
        d.text((x0 + 6 * s, y), 'THICKNESS', font=fl, fill=c(RED)); y += int(38 * s)
        d.text((x0, y), thick, font=fv, fill=c(CREAM))
        if callout:
            t, sub, cx, cy = callout; cx, cy = int(cx * s), int(cy * s)
            d.ellipse([cx - 8 * s, cy - 8 * s, cx + 8 * s, cy + 8 * s], fill=c(RED))
            if down:  # leader goes down, label under it
                d.line([(cx, cy), (cx, cy + int(70 * s))], fill=c(CREAM), width=max(2, int(3 * s)))
                tx, ty = cx - int(40 * s), cy + int(84 * s)
            else:
                d.line([(cx, cy), (cx - int(220 * s), cy)], fill=c(CREAM), width=max(2, int(3 * s)))
                tx, ty = cx - int(220 * s), cy - int(78 * s)
            d.text((tx, ty), t, font=fl, fill=c(CREAM))
            d.text((tx, ty + int(38 * s)), sub, font=fsub, fill=c(CREAM))
    shadowed(im, draw)
    im.save(out, quality=92)

if __name__ == '__main__':
    a = sys.argv[1:]
    co = (a[5], a[6], float(a[7]), float(a[8])) if len(a) > 5 else None
    hud(a[0], a[1], a[2], a[3], a[4], co, len(a) > 9 and a[9] == 'down')
