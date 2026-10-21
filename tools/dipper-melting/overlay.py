# Info layer for The Dipper Is Melting: python3 overlay.py proj.json out.mov
# proj.json comes from proj.js (screen positions of the 7 stars and their year-0 ghosts, per frame).
import subprocess, math, sys, json
from PIL import Image, ImageDraw, ImageFont
PJ = json.load(open(sys.argv[1])); OUT = sys.argv[2]
W, H, FPS, T = 1080, 1920, 30, 20.0; N = int(T*FPS)
MB = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p, s): return ImageFont.truetype(p, s)
CREAM = (246, 240, 228); RED = (214, 62, 48); TEAL = (40, 220, 200); GOLD = (255, 200, 110)
def clamp(x): return max(0.0, min(1.0, x))
def sstep(a, b, x): k = clamp((x-a)/(b-a)); return k*k*(3-2*k)
def tw(d, txt, font, sp=0): return sum(d.textlength(c, font=font)+sp for c in txt)-sp if sp else d.textlength(txt, font=font)
def ctext(d, y, txt, font, fill, a=255, sp=0, stroke=0, chip=None, x=None):
    w = tw(d, txt, font, sp); x = (W-w)/2 if x is None else x
    if chip is not None:
        pad = 16; d.rectangle((x-pad, y-6, x+w+pad, y+font.size+10), fill=chip+(int(a*0.96),))
    if sp:
        for c in txt:
            d.text((x, y), c, font=font, fill=fill+(a,), stroke_width=stroke, stroke_fill=(0, 0, 0, min(a, 235))); x += d.textlength(c, font=font)+sp
    else: d.text((x, y), txt, font=font, fill=fill+(a,), stroke_width=stroke, stroke_fill=(0, 0, 0, min(a, 235)))
def typed_chip(d, y, pre, hot, n, font, a):
    """'pre' in cream, 'hot' on a red chip, typed n characters (n >= 1 only: negative slices type from the end)"""
    if n < 1: return
    full = pre+hot; txt = full[:min(len(full), n)]; x0 = (W-tw(d, full, font))/2
    d.text((x0, y), txt[:len(pre)], font=font, fill=CREAM+(a,), stroke_width=6, stroke_fill=(0, 0, 0, min(a, 235)))
    if len(txt) > len(pre):
        xo = x0+tw(d, pre, font); hs = txt[len(pre):]
        d.rectangle((xo-12, y-6, xo+tw(d, hs, font)+12, y+font.size+10), fill=RED+(int(a*0.97),)); d.text((xo, y), hs, font=font, fill=CREAM+(a,))
def ring(d, x, y, r, col, a, w=3): d.ellipse((x-r, y-r, x+r, y+r), outline=col+(int(a),), width=w)
def solid(c, a): return Image.new("RGBA", (W, H), c+(int(255*a),))
fh = F(MB, 76); flab = F(MR, 27); fcnt = F(MB, 92); fchip = F(MB, 44); fsub = F(MR, 28); ftag = F(MR, 23); fname = F(MR, 26); ftw = F(MB, 66)
GROUP = [1, 2, 3, 4, 5]; LONERS = [(0, "DUBHE"), (6, "ALKAID")]
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "png", OUT], stdin=subprocess.PIPE)
last = -1
for f in range(N):
    t = f/FPS; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); pj = PJ[f]
    S = lambda k: (pj['now'][k][0]*W, pj['now'][k][1]*H)
    # ---- hook (typed fast, done by ~1.5 s)
    if 0.12 <= t < 2.05:
        a = int(255*(1-sstep(1.85, 2.05, t))); n = int((t-0.12)*19)+1
        l1 = "THE BIG DIPPER"; ctext(d, 190, l1[:min(len(l1), n)], fh, CREAM, a, stroke=6)
        if n > len(l1): typed_chip(d, 290, "IS ", "MELTING.", n-len(l1), fh, a)
    # ---- monotonic years counter
    if 2.0 <= t < 17.75:
        a = int(255*sstep(2.0, 2.15, t)*(1-sstep(17.45, 17.75, t)))
        yr = int(round(pj['year']/100.0))*100
        assert yr >= last, (f, yr, last); last = yr
        ctext(d, 112, "THE SKY IN", flab, CREAM, int(a*0.85), sp=7, stroke=3)
        big = f"{yr:,} YEARS"; sc = 1.0+0.10*math.exp(-(t-13.2)/0.18) if t >= 13.2 else 1.0
        ctext(d, 146, big, fcnt if sc == 1.0 else F(MB, int(92*sc)), CREAM, a, stroke=6)
    # ---- the family (Ursa Major Moving Group) and the two loners
    if 9.3 <= t < 12.6:
        a = int(255*sstep(9.3, 9.5, t)*(1-sstep(12.35, 12.6, t)))
        ctext(d, 282, "5 OF THESE 7 STARS", fchip, CREAM, a, sp=2, chip=RED)
        s1 = "TRAVEL TOGETHER"; s2 = "DUBHE AND ALKAID DON'T"
        a1 = int(a*(1-sstep(10.85, 11.0, t))); a2 = int(a*sstep(11.0, 11.15, t))
        if a1 > 0: ctext(d, 352, s1, fsub, CREAM, a1, sp=3, stroke=3)
        if a2 > 0: ctext(d, 352, s2, fsub, CREAM, a2, sp=3, stroke=3)
        ga = a*sstep(9.45, 9.75, t)
        for k in GROUP:
            x, y = S(k); ring(d, x, y, 36+3*math.sin(t*5+k), TEAL, ga*0.95, 4)
        la = a*sstep(11.0, 11.3, t)
        for k, name in LONERS:
            x, y = S(k); ring(d, x, y, 38+3*math.sin(t*5+k), RED, la, 4)
            nx = x+52 if x < W/2 else x-52-tw(d, name, fname)
            d.text((nx, y-14), name, font=fname, fill=CREAM+(int(la),), stroke_width=3, stroke_fill=(0, 0, 0, int(min(la, 235))))
    # ---- reveal: same 7 stars, today's shape as a ghost
    if 13.25 <= t < 14.45:
        a = int(255*sstep(13.25, 13.45, t)*(1-sstep(14.25, 14.45, t)))
        ctext(d, 282, "SAME 7 STARS.", fchip, CREAM, a, sp=2, chip=RED)
        gx, gy = pj['ghost'][0][0]*W, pj['ghost'][0][1]*H
        ctext(d, gy-58, "TODAY", fname, CREAM, int(a*0.9), sp=4, stroke=3, x=gx-tw(d, "TODAY", fname, 4)/2)
    # ---- twist
    if 14.45 <= t < 17.75:
        a = int(255*(1-sstep(17.45, 17.75, t))); n = int((t-14.45)*24)+1
        l1 = "THE STARS ONLY"; ctext(d, 280, l1[:min(len(l1), n)], ftw, CREAM, a, stroke=6)
        if n > len(l1): typed_chip(d, 370, "LOOK ", "FIXED.", n-len(l1), ftw, a)
    # ---- data tag
    if 2.0 <= t < 17.75:
        ta = int(150*sstep(2.0, 2.3, t)*(1-sstep(17.45, 17.75, t)))
        d.text((48, 1528), "REAL STAR MOTIONS · HIPPARCOS DATA", font=ftag, fill=(235, 235, 235, ta))
    # ---- flashes (small, short: no white-outs)
    for (h, amp, n_) in ((2.0, 0.10, 4), (13.2, 0.14, 6)):
        k = int(round((t-h)*FPS))
        if 0 <= k < n_: im = Image.alpha_composite(im, solid((255, 255, 255), amp*(1-k/n_)))
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay done, last counter", last)
