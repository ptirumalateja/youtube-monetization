#!/usr/bin/env python3
"""Text / marker layer for the Black Hole Ladder (1080x1920, 30 fps, 28.2 s).
usage: overlay.py A|B proj.json out.mov
Draws: typed hook, ratio chips, left ladder + red marker, Sun / Mercury / Neptune labels, 60 km bracket,
red Solar System marker, ending line. Positions come from proj.json (tools/black-hole-ladder/proj_all.js)."""
import subprocess, math, sys, json
from PIL import Image, ImageDraw, ImageFont
VAR, PJ_PATH, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PJ = json.load(open(PJ_PATH))
W, H, FPS = 1080, 1920, 30
N = len(PJ)
MB = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
MR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p, s): return ImageFont.truetype(p, s)
CREAM = (246, 240, 228); RED = (214, 62, 48); GOLD = (255, 200, 110); TEAL = (120, 230, 215)
def clamp(x): return max(0.0, min(1.0, x))
def sstep(a, b, x):
    if b <= a: return 1.0 if x >= b else 0.0
    k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k)
def win(t, a, b, fi=0.25, fo=0.3):
    return sstep(a, a + fi, t) * (1 - sstep(b - fo, b, t))
def tw(d, txt, font, sp=0):
    return sum(d.textlength(c, font=font) + sp for c in txt) - sp if sp else d.textlength(txt, font=font)
def text(d, xy, txt, font, fill, a=255, stroke=5, anchor='la'):
    d.text(xy, txt, font=font, fill=fill + (a,), stroke_width=stroke, stroke_fill=(0, 0, 0, min(a, 235)), anchor=anchor)
def ctext(d, y, txt, font, fill, a=255, sp=0, stroke=5):
    w = tw(d, txt, font, sp); x = (W - w) / 2
    if sp:
        for c in txt:
            d.text((x, y), c, font=font, fill=fill + (a,), stroke_width=stroke, stroke_fill=(0, 0, 0, min(a, 235))); x += d.textlength(c, font=font) + sp
    else:
        text(d, (x, y), txt, font, fill, a, stroke)
def chip(d, y, txt, font, a=255, fill=RED, sp=0):
    w = tw(d, txt, font, sp); x = (W - w) / 2; pad = 18
    d.rounded_rectangle((x - pad, y - 8, x + w + pad, y + font.size + 12), radius=8, fill=fill + (int(a * 0.96),))
    if sp:
        xx = x
        for c in txt:
            d.text((xx, y), c, font=font, fill=CREAM + (a,)); xx += d.textlength(c, font=font) + sp
    else:
        d.text((x, y), txt, font=font, fill=CREAM + (a,))
def typed(s, t, t0, cps=46):
    n = int(max(0, (t - t0)) * cps)
    return s[:max(0, min(len(s), n))] if n > 0 else ''

fBIG = F(MB, 124); fHOOK = F(MB, 60); fCHIP = F(MB, 46); fSUB = F(MB, 30); fLAB = F(MB, 32); fTAG = F(MR, 26); fRUNG = F(MB, 34); fRUNGA = F(MB, 40); fEND = F(MB, 72)

HOOK = {'A': ["THIS IS OUR WHOLE", "SOLAR SYSTEM."], 'B': ["ONE BLACK HOLE IS", "43x WIDER THAN THIS."],
        'C': ["A BLACK HOLE CAN BE CITY-SIZED.", "OR BIGGER THAN THIS."], 'D': ["WHAT'S BIGGER THAN OUR", "WHOLE SOLAR SYSTEM?"]}[VAR]
_mx = max(len(HOOK[0]), len(HOOK[1])); fHOOK = F(MB, min(60, int(960 / (0.6 * _mx))))
HOOK_CPS = max(70.0, (len(HOOK[0]) + len(HOOK[1])) / 0.65)
_fc = {}
def FB(sz):
    sz = int(sz)
    if sz not in _fc: _fc[sz] = F(MB, sz)
    return _fc[sz]
# stops: (label start, label end, ratio, name, sub)
STOPS = [
    (6.5, 7.9, None, "STELLAR-MASS BLACK HOLE", "~10 SUNS · ~60 KM ACROSS"),
    (9.2, 12.9, "430,000x", "SAGITTARIUS A*", "~4.3 MILLION SUNS · ~25 MILLION KM"),
    (15.0, 18.9, "1,500x", "M87*", "~6.5 BILLION SUNS · ~38 BILLION KM"),
    (21.3, 25.2, "10x", "TON 618", "UP TO ~66 BILLION SUNS · ~390 BILLION KM"),
]
RUNG_NAMES = ["STELLAR", "SGR A*", "M87*", "TON 618"]
RUNG_Y = [1330, 1180, 1030, 880]
def rung_pos(t):
    # marker climbs between rungs while the camera pulls back
    keys = [(0, -1), (6.5, 0), (7.0, 0), (8.6, 1), (12.4, 1), (14.6, 2), (18.4, 2), (20.8, 3), (25.2, 3)]
    if t <= keys[0][0]: return -1
    for (a, va), (b, vb) in zip(keys, keys[1:]):
        if t <= b:
            u = sstep(a, b, t) if va >= 0 else sstep(a, b, t)
            return va + (vb - va) * u
    return 3

def on(p):  # inside frame
    return p[2] > 0.5 and -0.05 < p[0] < 1.05 and -0.05 < p[1] < 1.05
def X(p): return p[0] * W
def Y(p): return p[1] * H

def ring(d, cx, cy, r, a, col=RED, w=5):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col + (a,), width=w)
def leader(d, p0, p1, a, col=CREAM):
    d.line([p0, p1], fill=col + (int(a * 0.8),), width=3)
def label(d, xy_target, xy_text, txt, a, col=CREAM, align='l'):
    leader(d, xy_target, (xy_text[0], xy_text[1] + 16), a, col)
    w = d.textlength(txt, font=fLAB); x = xy_text[0] if align == 'l' else xy_text[0] - w
    text(d, (x, xy_text[1]), txt, fLAB, col, a, 5)

proc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                         "-c:v", "png", "-pix_fmt", "rgba", OUT], stdin=subprocess.PIPE)
for f in range(N):
    t = f / FPS; pj = PJ[f]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # ---- hook (typed), then "STARTING SMALL." beat
    a_h = win(t, 0.0, 3.2, 0.05, 0.5)
    if a_h > 0.01:
        l1, l2 = HOOK
        s1 = typed(l1, t, 0.30, HOOK_CPS); s2 = typed(l2, t, 0.30 + len(l1) / HOOK_CPS, HOOK_CPS)
        if s1: ctext(d, 215, s1, fHOOK, CREAM, int(255 * a_h), stroke=6)
        if s2: ctext(d, 292, s2, fHOOK, CREAM, int(255 * a_h), stroke=6)
    a_s = win(t, 3.3, 5.3, 0.3, 0.4)
    if a_s > 0.01:
        s = typed("NOW: THE SMALLEST ONE.", t, 3.3, 50); ctext(d, 236, s, fHOOK, CREAM, int(255 * a_s), stroke=6)
    # tag (thought experiment)
    a_t = win(t, 0.1, 2.6, 0.2, 0.5) + win(t, 26.6, 28.2, 0.2, 0.0)
    if a_t > 0.01: ctext(d, 1495, "THOUGHT EXPERIMENT · NOT TO SCALE", fTAG, CREAM, int(190 * min(1, a_t)), stroke=4)
    # ---- the speck (60 km black hole) in the Solar System
    if 2.9 < t < 6.2:
        a = win(t, 2.9, 6.2, 0.4, 0.15)
        sp = pj['speck']
        if on(sp):
            cx, cy = X(sp), Y(sp); r = 30 + 6 * math.sin(t * 6.0)
            if t > 5.3: r = max(r, pj['speckR'] * H * 1.15)
            ring(d, cx, cy, r, int(255 * a), RED, 5)
            if t < 5.4:
                cy2 = cy - 150; leader(d, (cx, cy - r), (cx, cy2 + 56), a); chip(d, cy2, "60 KM BLACK HOLE", fCHIP, int(255 * a))
    # ---- stop labels
    for i, (a0, a1, ratio, name, sub) in enumerate(STOPS):
        a = win(t, a0, a1, 0.25, 0.4)
        if a <= 0.01: continue
        A = int(255 * a); y = 230
        if ratio:
            # big for the first ~1.2 s, then recede to a small tag so the horizon can take over
            k = sstep(a0 + 1.25, a0 + 1.85, t); sz = 124 - 60 * k; r_txt = typed(ratio, t, a0, 22)
            ctext(d, y, r_txt, FB(sz), CREAM, A, stroke=int(8 - 3 * k)); y += int(1.15 * sz + 10)
        n_txt = typed(name, t, a0 + 0.12, 40)
        if n_txt: chip(d, y, n_txt, fCHIP, A)
        if t - a0 > 0.5 + len(name) / 40: ctext(d, y + 74, sub, fSUB, CREAM, A, stroke=4)
    # ---- object labels
    # Sun beside Sgr A*
    a = win(t, 9.7, 12.2, 0.3, 0.4)
    if a > 0.01 and on(pj['sun']):
        sx, sy = X(pj['sun']), Y(pj['sun']); ring(d, sx, sy, 24, int(255 * a), RED, 4); label(d, (sx, sy + 24), (sx - 20, sy + 120), "THE SUN", int(255 * a), GOLD)
    if a > 0.01 and on(pj['mercR']):
        mx, my = X(pj['mercR']), Y(pj['mercR']); label(d, (mx - 4, my), (min(mx - 20, W - 40) - 300, my + 170), "MERCURY'S ORBIT", int(255 * a), TEAL)
    # Neptune ring inside M87* shadow
    a = win(t, 15.6, 18.2, 0.3, 0.4)
    if a > 0.01 and on(pj['nepR']):
        nx, ny = X(pj['nepR']), Y(pj['nepR']); label(d, (nx, ny + 6), (nx + 24, ny + 130), "NEPTUNE'S ORBIT", int(255 * a), GOLD)
    # stellar bracket: city = 60 km
    a = win(t, 6.7, 7.9, 0.2, 0.4)
    if a > 0.01 and on(pj['city']):
        cx, cy = X(pj['city']), Y(pj['city']); wpx = 2 * (pj['shR'][0] / 2.6) * H
        yb = cy + wpx * 0.62; d.line([(cx - wpx / 2, yb), (cx + wpx / 2, yb)], fill=CREAM + (int(220 * a),), width=4)
        for xx in (cx - wpx / 2, cx + wpx / 2): d.line([(xx, yb - 12), (xx, yb + 12)], fill=CREAM + (int(220 * a),), width=4)
        text(d, (cx, yb + 18), "60 KM  ·  A CITY", fLAB, CREAM, int(255 * a), 5, 'ma')
    # red marker on our Solar System speck at TON 618
    a = win(t, 22.3, 27.0, 0.4, 0.5)
    if a > 0.01 and on(pj['ss']):
        sx, sy = X(pj['ss']), Y(pj['ss']); r = max(34, min(260, pj['ssR'] * H * 1.12)) if t > 26.0 else 34 + 5 * math.sin(t * 5.0)
        if t < 25.6 or t > 26.4: ring(d, sx, sy, r, int(255 * a), RED, 5)
        if t < 25.2:
            leader(d, (sx, sy + r), (sx, sy + 150), a); chip(d, sy + 150, "OUR SOLAR SYSTEM", fCHIP, int(255 * a))
    # held breath line (TON 618)
    a = win(t, 23.6, 25.2, 0.3, 0.4)
    if a > 0.01: ctext(d, 1440, "LIGHT NEEDS 15 DAYS TO CROSS THIS.", fSUB, CREAM, int(255 * a), stroke=4)
    # ---- left ladder
    a_l = win(t, 6.5, 25.4, 0.5, 0.6)
    if a_l > 0.01:
        rp = rung_pos(t); AL = int(255 * a_l)
        d.line([(70, RUNG_Y[3] - 40), (70, RUNG_Y[0] + 40)], fill=CREAM + (int(110 * a_l),), width=3)
        for k, (nm, yy) in enumerate(zip(RUNG_NAMES, RUNG_Y)):
            act = clamp(1 - abs(rp - k)); col = CREAM; font = fRUNGA if act > 0.5 else fRUNG
            d.ellipse((62, yy - 8, 78, yy + 8), fill=CREAM + (int(220 * a_l),))
            text(d, (96, yy - 20), nm, font, col, int((130 + 125 * act) * a_l), 4)
        if rp >= 0:
            yy = RUNG_Y[0] + (RUNG_Y[3] - RUNG_Y[0]) * (rp / 3.0)
            d.ellipse((54, yy - 16, 86, yy + 16), fill=RED + (AL,), outline=CREAM + (AL,), width=3)
    # ---- ending line
    a = win(t, 27.0, 28.2, 0.2, 0.0)
    if a > 0.01:
        s = typed("OUR SOLAR SYSTEM.", t, 27.05, 24); ctext(d, 1290, s, fEND, CREAM, int(255 * a), stroke=7)
    proc.stdin.write(im.tobytes())
proc.stdin.close(); proc.wait()
print("overlay done", N)
