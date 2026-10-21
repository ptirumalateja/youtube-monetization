# Draws the tag, hook, depth counter, the red 20 CM chip, the reveal caption and the end line into an RGBA PNG .mov
# (1080x1920, 30 fps). usage: python3 overlay.py proj.json out.mov
import json, subprocess, sys
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
TL = json.load(open('timeline.json')); T = TL['T']; TX = TL['text']; ST = TL['strokes']; EV = TL['events']
PROJ = {int(k): v for k, v in json.load(open(sys.argv[1])).items()}
CREAM = (244, 232, 210); RED = (214, 62, 48); BLACK = (0, 0, 0)
F = '/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf'; FS = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'
def font(n, f=F): return ImageFont.truetype(f, n)

def typed(spec, t):
    if t < spec['t0']: return None, 0.0
    n = max(1, int(len(spec['s']) * min(1.0, (t - spec['t0']) / (spec['t1'] - spec['t0']))))   # n>=1: no negative slicing
    o0, o1 = spec['out']; a = 1.0 - min(1.0, max(0.0, (t - o0) / (o1 - o0)))
    return spec['s'][:n], a

def wrap(d, s, f, maxw):
    lines, cur = [], ''
    for w in s.split(' '):
        c = (cur + ' ' + w).strip()
        if d.textlength(c, font=f) <= maxw: cur = c
        else: lines.append(cur); cur = w
    lines.append(cur); return lines

def text_block(d, s, f, cx, y, maxw, alpha, full, spacing=1.18):
    pos = 0
    for ln in wrap(d, full, f, maxw):
        part = s[pos:pos + len(ln) + 1].rstrip() if pos < len(s) else ''
        x = cx - d.textlength(ln, font=f) / 2
        if part: d.text((x, y), part, font=f, fill=CREAM + (int(255 * alpha),), stroke_width=6, stroke_fill=BLACK + (int(255 * alpha),))
        pos += len(ln) + 1; y += int(f.size * spacing)

def depth_shown(t):
    k = 0
    for i, (ts, d) in enumerate(ST):
        if ts <= t: k = i
    return ST[k][1], t - ST[k][0]

def frame(fi):
    t = fi / FPS
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    s, a = typed(TX['tag'], t)
    if s: d.text((W / 2, 108), s, font=font(22, FS), fill=CREAM + (int(190 * a),), anchor='mm', stroke_width=4, stroke_fill=BLACK + (int(190 * a),))
    # depth counter: steps on every shovel impact, only ever goes up
    ca = 1.0 - min(1.0, max(0.0, (t - 13.75) / 0.2))
    if ca > 0:
        dv, age = depth_shown(t); pop = 1.0 + 0.08 * max(0.0, 1 - age / 0.12)
        al = (int(255 * ca * 0.85),)
        d.text((W / 2, 178), 'D E P T H', font=font(27), fill=CREAM + al, anchor='mm', stroke_width=4, stroke_fill=BLACK + al)
        d.text((W / 2, 262), f'{dv:.1f} M', font=font(int(92 * pop)), fill=CREAM + (int(255 * ca),), anchor='mm', stroke_width=7, stroke_fill=BLACK + (int(255 * ca),))
        na = ca * min(1.0, max(0.0, (t - 1.2) / 0.3))
        if na > 0: d.text((W / 2, 336), 'A PARABLE  ·  NOT TO SCALE', font=font(20, FS), fill=CREAM + (int(150 * na),), anchor='mm', stroke_width=3, stroke_fill=BLACK + (int(150 * na),))
    for k, sz in (('hook', 64), ('reveal', 60), ('end', 76)):
        s, a = typed(TX[k], t)
        if s and a > 0: text_block(d, s, font(sz), W / 2, 410, 960, a, TX[k]['s'])
    # red chip beside the bracket, tracked to the 3D anchor
    s, a = typed(TX['chip'], t)
    if s and a > 0 and fi in PROJ:
        x, y = PROJ[fi][0] * W, PROJ[fi][1] * H; f = font(46); tw = d.textlength(TX['chip']['s'], font=f)
        x = min(x + 18, W - 48 - tw - 36); A = int(255 * a)
        d.rounded_rectangle((x, y - 38, x + tw + 36, y + 38), radius=10, fill=RED + (A,))
        d.text((x + 18, y), s, font=f, fill=CREAM + (A,), anchor='lm')
    return img

if __name__ == '__main__':
    out = sys.argv[2]; n = int(round(T * FPS))
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'png', '-pix_fmt', 'rgba', out], stdin=subprocess.PIPE)
    last = -1.0
    for i in range(n):
        dv, _ = depth_shown(i / FPS); assert dv >= last; last = dv     # counter is monotonic
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
