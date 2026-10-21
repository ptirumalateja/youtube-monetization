# Overlay for "Three Answers to One Fall" (v2: 19 s, 1080x1920, 30 fps): hook, year odometer, answer chips, left ladder, twist, tags.
# python3 overlay.py out.mov   -> PNG-in-MOV RGBA stream, composited over the 3D frames by build.sh
import subprocess, math, sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else "overlay.mov"
W, H, FPS, T = 1080, 1920, 30, 19.0
N = int(T * FPS)
MB = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"
MR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MRB = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
def F(p, s): return ImageFont.truetype(p, s)
CREAM = (246, 240, 228); RED = (214, 62, 48); GOLD = (255, 200, 110)
def clamp(x): return max(0.0, min(1.0, x))
def sstep(a, b, x): k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k)
def win(t, a, b, fi=0.18, fo=0.2): return sstep(a, a + fi, t) * (1 - sstep(b - fo, b, t))
def tw(d, txt, font, sp=0): return (sum(d.textlength(c, font=font) + sp for c in txt) - sp) if sp else d.textlength(txt, font=font)
def ctext(d, y, txt, font, fill, a=255, sp=0, stroke=0, chip=None, x=None):
    w = tw(d, txt, font, sp); x = (W - w) / 2 if x is None else x
    if a <= 0: return
    if chip is not None:
        pad = 16; d.rectangle((x - pad, y - 6, x + w + pad, y + font.size + 10), fill=chip + (int(a * 0.96),))
    sf = (0, 0, 0, min(a, 235))
    if sp:
        for c in txt:
            d.text((x, y), c, font=font, fill=fill + (a,), stroke_width=stroke, stroke_fill=sf); x += d.textlength(c, font=font) + sp
    else:
        d.text((x, y), txt, font=font, fill=fill + (a,), stroke_width=stroke, stroke_fill=sf)
def typed(d, y, full, red_from, n, font, a):
    """Type `full` (n chars shown, n>=1); characters from index red_from sit on a red chip."""
    if n < 1 or a <= 0: return
    txt = full[:min(len(full), n)]; x0 = (W - tw(d, full, font)) / 2
    pre = txt[:red_from]
    d.text((x0, y), pre, font=font, fill=CREAM + (a,), stroke_width=6, stroke_fill=(0, 0, 0, min(a, 235)))
    if len(txt) > red_from:
        xo = x0 + tw(d, full[:red_from], font); seg = txt[red_from:]; wo = tw(d, seg, font)
        d.rectangle((xo - 12, y - 6, xo + wo + 12, y + font.size + 10), fill=RED + (int(a * 0.97),)); d.text((xo, y), seg, font=font, fill=CREAM + (a,))
def solid(c, a): return Image.new("RGBA", (W, H), c + (int(255 * a),))

# ---- year odometer: 1687 (Principia) -> 1915 (general relativity) -> 2026 (today). Must only go up.
YK = [(1.65, 1600), (2.0, 1687), (5.05, 1687), (5.5, 1915), (10.2, 1915), (10.75, 2026), (13.5, 2026)]
def year(t):
    for (a, ya), (b, yb) in zip(YK, YK[1:]):
        if a <= t <= b: return int(round(ya + (yb - ya) * sstep(a, b, t)))
    return None
SECTIONS = [  # start, end, header, chip, meaning lines [(a,b,text,font-key)]
    (1.6, 5.05, "ANSWER 1 OF 3", "NEWTON", [(1.85, 5.05, "A FORCE PULLS IT DOWN.", "m"), (2.6, 5.05, "EQUAL TIMES, GROWING GAPS: IT SPEEDS UP", "s")]),
    (5.1, 10.05, "ANSWER 2 OF 3", "EINSTEIN", [(5.45, 8.3, "NO FORCE. TIME RUNS SLOWER BELOW.", "m"), (6.0, 8.3, "1 METRE LOWER: 1 SECOND LOST EVERY ~290 MILLION YEARS", "s"),
                                                  (8.3, 10.05, "THE APPLE FOLLOWS BENT SPACETIME.", "m"), (8.55, 10.05, "SO DOES LIGHT (MEASURED IN 1919)", "s")]),
    (10.15, 13.5, "ANSWER 3 OF 3", "QUANTUM GRAVITY", [(10.45, 13.5, "SPACETIME ITSELF MAY TURN TO FOAM", "m"), (10.9, 13.5, "AT 10⁻³⁵ METRES: THE PLANCK LENGTH", "s")]),
]
RUNGS = [("NEWTON", 1290), ("EINSTEIN", 1185), ("???", 1080)]
def impact(t):
    k = int(round(t * FPS))
    if 0 <= k < 4: return solid((255, 255, 255), 0.12 * (1 - k / 4))
    k = int(round((t - 14.0) * FPS))
    if 0 <= k < 5: return solid((255, 255, 255), 0.15 * (1 - k / 5))
    return None

def main():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "png", OUT], stdin=subprocess.PIPE)
    fhook = F(MB, 90); fhdr = F(MR, 27); fcnt = F(MB, 104); fchip = F(MB, 48); fm = F(MB, 36); fs = F(MR, 25); ftag = F(MR, 23); frung = F(MB, 30); ftw = F(MB, 80); fstamp = F(MB, 44)
    last_year = 0
    for f in range(N):
        t = f / FPS; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        # hook: complete on frame 0 (no typing), held until the pull-back; fades back in over the last 0.4 s so the loop lands on it
        if t < 1.65 or t >= 18.6:
            a = int(255 * ((1 - sstep(1.45, 1.65, t)) if t < 1.65 else sstep(18.6, 19.0, t)))
            typed(d, 1150, "WHY DOES IT FALL?", 12, 99, fhook, a)
        # sections
        for (s0, s1, hdr, chip, lines) in SECTIONS:
            if s0 <= t < s1:
                A = int(255 * win(t, s0, s1))
                ctext(d, 214, hdr, fhdr, CREAM, int(A * 0.85), sp=7, stroke=3)
                y = year(t)
                if y is not None:
                    assert y >= last_year, f"year odometer went backwards at t={t:.2f}: {y} < {last_year}"; last_year = y
                    ctext(d, 252, str(y) if not (chip == "QUANTUM GRAVITY" and y == 2026) else "2026: TODAY", fcnt if y != 2026 else F(MB, 80), CREAM, A, stroke=6)
                ctext(d, 378, chip, fchip, CREAM, A, sp=4, chip=RED)
                ly = {"m": 462, "s": 512}
                for (a0, a1, txt, k) in lines:
                    if a0 <= t < a1:
                        la = int(255 * win(t, a0, a1, 0.2, 0.2))
                        if k == "m": ctext(d, ly["m"], txt, fm, CREAM, la, stroke=4)
                        else: ctext(d, ly["s"], txt, fs, CREAM, int(la * 0.9), sp=1, stroke=3)
                if chip == "QUANTUM GRAVITY" and t >= 12.0:
                    sa = int(255 * win(t, 12.0, 13.5, 0.08, 0.2)); txt = "UNKNOWN"; w = tw(d, txt, fstamp, 6); x = (W - w) / 2; yy = 1180
                    ctext(d, yy, txt, fstamp, CREAM, sa, sp=6, stroke=3)
                    d.rectangle((x - 22, yy - 14, x + w + 22, yy + fstamp.size + 18), outline=RED + (sa,), width=5)
        # left ladder: NEWTON -> EINSTEIN -> ???
        if 1.6 <= t < 13.5:
            LA = int(255 * win(t, 1.6, 13.5, 0.3, 0.25)); cur = 0 if t < 5.1 else 1 if t < 10.15 else 2
            d.line((64, RUNGS[2][1], 64, RUNGS[0][1]), fill=CREAM + (int(LA * 0.5),), width=3)
            for i, (name, y) in enumerate(RUNGS):
                if i == cur: d.ellipse((53, y - 11, 75, y + 11), fill=RED + (LA,))
                elif i < cur: d.ellipse((58, y - 6, 70, y + 6), fill=CREAM + (int(LA * 0.9),))
                else: d.ellipse((58, y - 6, 70, y + 6), outline=CREAM + (int(LA * 0.7),), width=2)
                d.text((92, y - 16), name, font=frung, fill=CREAM + (int(LA * (1.0 if i == cur else 0.6)),), stroke_width=3, stroke_fill=(0, 0, 0, min(LA, 220)))
        # twist
        if 14.0 <= t < 17.7:
            a = int(255 * (1 - sstep(17.3, 17.7, t))); n = int((t - 14.04) * 30) + 1 if t >= 14.04 else 0
            L = ["NOBODY HAS", "THE THIRD", "ANSWER YET."]
            for i, line in enumerate(L):
                k = n - sum(len(x) for x in L[:i])
                if k >= 1: typed(d, 330 + i * 104, line, 7 if i == 2 else len(line), k, ftw, a)
        # tag
        if t >= 0.3:
            ta = int(140 * (1 - sstep(18.3, 18.7, t))); txt = "THOUGHT EXPERIMENT · NOT TO SCALE" + (" · CLOCKS EXAGGERATED" if 5.1 <= t < 10.1 else "")
            d.text((48, 1500), txt, font=ftag, fill=(235, 235, 235, ta))
        imp = impact(t)
        if imp is not None: im = Image.alpha_composite(im, imp)
        p.stdin.write(im.tobytes())
    p.stdin.close(); p.wait(); print("overlay done", OUT)

if __name__ == "__main__":
    main()
