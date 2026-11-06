#!/usr/bin/env python3
"""Caption PNGs for Indic scripts. libass in this ffmpeg does not shape Telugu/Devanagari (it draws dotted circles),
so captions are rendered with PIL + raqm and overlaid in mix4 (CAPPNG=<list.json>).
Same look as captions4: white ExtraBold, yellow keywords ({Y}..{W}), dark outline, blurred dark backing, centre y=1230.
Usage: CUTMOD=cut_xx.py TEMPO=1.08 capspng.py FONT.ttf OUT_DIR"""
import importlib.util, json, os, re, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont
FONT, OUT = sys.argv[1], sys.argv[2]
TEMPO = float(os.environ.get('TEMPO', '1.08'))
sp = importlib.util.spec_from_file_location('cm', os.environ['CUTMOD']); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)
W, H = 1080, 1920
YEL, WHT, OUTL = (255, 216, 47), (255, 255, 255), (16, 16, 16)
os.makedirs(OUT, exist_ok=True)

LATIN = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'     # Latin letters, & and arrows are not in the Indic fonts
is_lat = lambda ch: ch.isascii() and (ch.isalpha() or ch in '&?') or ch in '↓'

def runs(line):
    """split into (text, colour, use_latin_font); spaces, digits and punctuation stay with the current run"""
    out, col = [], WHT
    for part in re.split(r'(\{Y\}|\{W\})', line):
        if part == '{Y}': col = YEL; continue
        if part == '{W}': col = WHT; continue
        seg, script = '', None
        for ch in part:
            sc = True if is_lat(ch) else (False if ord(ch) >= 0x900 else None)
            if sc is not None and script is not None and sc != script:
                out.append((seg, col, script)); seg = ''
            if sc is not None: script = sc
            seg += ch
        if seg: out.append((seg, col, bool(script)))
    return out

items = []
for k, (a, b, txt) in enumerate(m.CAPS):
    size, cy = int(os.environ.get('CAPSIZE', '84')), 1230
    mm = re.match(r'\{\\pos\(540,(\d+)\)\\fs(\d+)\}', txt)
    if mm: cy, size = int(mm.group(1)), int(mm.group(2)) - 4; txt = txt[mm.end():]
    fonts = {False: ImageFont.truetype(FONT, size), True: ImageFont.truetype(LATIN, int(size * 0.92))}
    lines = [runs(l) for l in txt.split('\\N')]
    lh = int(size * 1.32); y0 = cy - lh * len(lines) / 2
    back = Image.new('L', (W, H), 0); db = ImageDraw.Draw(back)
    txtl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dt = ImageDraw.Draw(txtl)
    shad = Image.new('L', (W, H), 0); ds = ImageDraw.Draw(shad)
    for i, ln in enumerate(lines):
        wsum = sum(fonts[l].getlength(t) for t, _, l in ln); x = (W - wsum) / 2; y = y0 + i * lh + lh / 2
        for t, col, l in ln:
            font = fonts[l]
            db.text((x, y), t, font=font, fill=255, stroke_width=26, stroke_fill=255, anchor='lm')
            ds.text((x + 3, y + 3), t, font=font, fill=255, stroke_width=5, stroke_fill=255, anchor='lm')
            dt.text((x, y), t, font=font, fill=col + (255,), stroke_width=5, stroke_fill=OUTL + (255,), anchor='lm')
            x += font.getlength(t)
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    img.paste((0, 0, 0, 255), mask=back.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.56)))
    img.alpha_composite(Image.merge('RGBA', (*[Image.new('L', (W, H), 0)] * 3, shad.point(lambda v: int(v * 0.56)))))
    img.alpha_composite(txtl)
    p = f'{OUT}/cap{k:02d}.png'; img.save(p)
    items.append({'png': p, 'a': round(a / TEMPO, 3), 'b': round(b / TEMPO, 3)})
json.dump(items, open(f'{OUT}/list.json', 'w'), indent=0)
print(len(items), 'captions')
