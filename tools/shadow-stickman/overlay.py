# Draws hook, stopwatch, reveal captions and the end line into an RGBA PNG .mov (1080x1920, 30 fps).
# usage: python3 overlay.py out.mov
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
TL = json.load(open('timeline.json')); T = TL['T']; TX = TL['text']
CREAM = (244, 232, 210); RED = (214, 62, 48); BLACK = (0, 0, 0)
F = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'
def font(n): return ImageFont.truetype(F, n)

def typed(spec, t):
    if t < spec['t0']: return None, 0.0
    n = int(len(spec['s']) * min(1.0, (t - spec['t0']) / (spec['t1'] - spec['t0']))); n = max(n, 1)   # n>=1: no negative slicing
    o0, o1 = spec['out']; a = 1.0 - min(1.0, max(0.0, (t - o0) / (o1 - o0)))
    return spec['s'][:n], a

def wrap(d, s, f, maxw):
    words, lines, cur = s.split(' '), [], ''
    for w in words:
        c = (cur + ' ' + w).strip()
        if d.textlength(c, font=f) <= maxw: cur = c
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def text_block(d, s, f, cx, y, maxw, alpha, spacing=1.18, full=None):
    lines = wrap(d, full or s, f, maxw); shown = s; out_y = y
    pos = 0
    for ln in lines:
        part = shown[pos:pos + len(ln) + 1].rstrip() if pos < len(shown) else ''
        w = d.textlength(ln, font=f); x = cx - w / 2
        if part:
            d.text((x, out_y), part, font=f, fill=CREAM + (int(255 * alpha),), stroke_width=6, stroke_fill=BLACK + (int(255 * alpha),))
        pos += len(ln) + 1; out_y += int(f.size * spacing)

def frame(fi):
    t = fi / FPS
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    fo = 1.0 - min(1.0, max(0.0, (t - (T - 0.7)) / 0.5))                  # everything clears before the loop point
    co = 1.0 - min(1.0, max(0.0, (t - TL['counter_out'][0]) / (TL['counter_out'][1] - TL['counter_out'][0])))   # stopwatch leaves at the reveal
    fo *= co
    # stopwatch: one monotonic odometer; label flips at the reveal
    lab = TL['chip'][0] if t < TL['chip_switch'] else TL['chip'][1]
    cf = font(27); cw = d.textlength(lab, font=cf) + 44
    chip = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cd = ImageDraw.Draw(chip)
    cd.rounded_rectangle((W / 2 - cw / 2, 150, W / 2 + cw / 2, 198), 8, fill=RED + (int(235 * fo),))
    cd.text((W / 2, 174), lab, font=cf, fill=CREAM + (int(255 * fo),), anchor='mm'); img.alpha_composite(chip)
    mm, ss = int(t // 60), t - 60 * int(t // 60)
    ts = f'{mm:02d}:{ss:04.1f}'
    d.text((W / 2, 262), ts, font=font(92), fill=CREAM + (int(255 * fo),), anchor='mm', stroke_width=6, stroke_fill=BLACK + (int(255 * fo),))
    # tag (small, top)
    s, a = typed(TX['tag'], t)
    if s: d.text((W / 2, 108), s, font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 22), fill=CREAM + (int(190 * a),), anchor='mm', stroke_width=4, stroke_fill=BLACK + (int(190 * a),))
    # hook
    s, a = typed(TX['hook'], t)
    if s and a > 0: text_block(d, s, font(64), W / 2, 380, 940, a, full=TX['hook']['s'])
    # reveal captions + end line
    for k, y, sz in (('reveal1', 1300, 62), ('end', 1300, 62)):
        s, a = typed(TX[k], t)
        if s and a > 0: text_block(d, s, font(sz), W / 2, y, 960, a, full=TX[k]['s'])
    return img, t

if __name__ == '__main__':
    out = sys.argv[1]; n = int(T * FPS)
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'png', '-pix_fmt', 'rgba', out], stdin=subprocess.PIPE)
    last = -1
    for i in range(n):
        im, t = frame(i); assert t >= last; last = t        # counter is monotonic by construction
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait()
