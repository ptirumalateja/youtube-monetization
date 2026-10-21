# Nine Minutes overlay: hook, labels, the minutes timer (monotonic, asserted), end line. Writes overlay.mov (PNG, RGBA).
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont
OUT = sys.argv[1] if len(sys.argv) > 1 else "overlay.mov"
W, H, FPS, T = 1080, 1920, 30, 22.0; N = int(T * FPS)
MB = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p, s): return ImageFont.truetype(p, s)
CREAM = (246, 240, 228); RED = (214, 62, 48); GOLD = (255, 200, 110); TEAL = (150, 235, 225)
def clamp(x): return max(0.0, min(1.0, x))
def sstep(a, b, x): k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k)
def win(t, a, b, fi=0.2, fo=0.25): return sstep(a, a + fi, t) * (1 - sstep(b - fo, b, t))
def tw(d, txt, font, sp=0): return sum(d.textlength(c, font=font) + sp for c in txt) - sp if sp else d.textlength(txt, font=font)
def ctext(d, y, txt, font, fill, a=1.0, sp=0, stroke=5, chip=None):
    if a <= 0.01 or not txt: return
    A = int(255 * a); w = tw(d, txt, font, sp); x = (W - w) / 2
    if chip is not None:
        d.rectangle((x - 16, y - 6, x + w + 16, y + font.size + 10), fill=chip + (int(A * 0.96),)); stroke = 0
    if sp:
        for c in txt:
            d.text((x, y), c, font=font, fill=fill + (A,), stroke_width=stroke, stroke_fill=(0, 0, 0, min(A, 235))); x += d.textlength(c, font=font) + sp
    else:
        d.text((x, y), txt, font=font, fill=fill + (A,), stroke_width=stroke, stroke_fill=(0, 0, 0, min(A, 235)))
def typed(txt, t, t0, cps):  # always at least 1 char once started (negative-slice lesson)
    if t < t0: return ""
    n = max(1, int((t - t0) * cps)); return txt[:min(len(txt), n)]
# timer: seconds since contact, piecewise linear in video time -> monotonic by construction, asserted below
TK = [(8.7, 0), (12.0, 180), (16.3, 525), (17.3, 540)]
def timer_s(t):
    if t < TK[0][0]: return None
    for (a, va), (b, vb) in zip(TK, TK[1:]):
        if t < b: return va + (vb - va) * (t - a) / (b - a)
    return 540
fh = F(MB, 76); fchip = F(MB, 48); fsp = F(MR, 27); fmean = F(MR, 30); ftag = F(MR, 23); ftim = F(MB, 120); fcap = F(MB, 44); fend = F(MB, 72); fsrc = F(MR, 25)
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "png", OUT], stdin=subprocess.PIPE)
last = -1
for f in range(N):
    t = f / FPS; im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ctext(d, 150, "ILLUSTRATION · NOT TO SCALE · TIME-LAPSE", ftag, CREAM, 0.62, stroke=3)
    # hook
    a = 1 - sstep(2.05, 2.35, t)
    l1 = typed("WATCH IT DIE IN", t, 0.0, 22); ctext(d, 290, l1, fh, CREAM, a, stroke=6)
    l2 = typed("9 MINUTES.", t, 0.75, 16); ctext(d, 392, l2, fh, CREAM, a, chip=RED if l2 else None)
    ctext(d, 1400, "LEUKEMIA CELL", fchip, CREAM, win(t, 0.45, 2.3), chip=RED)
    # the engineered T cell
    a = win(t, 2.75, 5.0)
    ctext(d, 300, "THE PATIENT'S OWN T CELL", fsp, CREAM, a, sp=3, stroke=4)
    ctext(d, 352, "CAR-T CELL", fchip, CREAM, a, chip=RED)
    a2 = win(t, 3.25, 5.0)
    ctext(d, 1380, "given a new receptor in a lab", fmean, GOLD, a2, stroke=4)
    ctext(d, 1428, "(the CAR)", fmean, GOLD, a2, stroke=4)
    # the hunt
    a = win(t, 5.35, 8.55)
    ctext(d, 300, "IT HUNTS ONE MARKER", fsp, CREAM, a, sp=3, stroke=4)
    ctext(d, 352, "CD19", fchip, CREAM, a, chip=RED)
    ctext(d, 1400, "red dots on the leukemia cell", fmean, CREAM, win(t, 5.8, 8.55), stroke=4)
    # timer
    s = timer_s(t)
    if s is not None:
        assert s >= last - 1e-9, f"timer went backwards at {t}"; last = s
        ta = sstep(8.62, 8.8, t) * (1 - sstep(19.6, 20.0, t))
        sec = int(s + 1e-6); txt = f"{sec // 60:02d}:{sec % 60:02d}"
        ctext(d, 236, "SINCE CONTACT", fsp, CREAM, ta, sp=4, stroke=4)
        if 17.3 <= t < 17.6:  # 09:00 lands: brief scale pulse
            k = 1 + 0.18 * (1 - (t - 17.3) / 0.3); ft = F(MB, int(120 * k)); ctext(d, 280 - int(60 * (k - 1)), txt, ft, CREAM, ta, stroke=7)
        else: ctext(d, 280, txt, ftim, CREAM, ta, stroke=7)
        ctext(d, 440, "SYNAPSE FORMING", fcap, TEAL, win(t, 9.0, 11.95), stroke=5)
        ctext(d, 440, "LOCKED ON", fcap, TEAL, win(t, 12.0, 13.45, 0.12), stroke=5)
        ctext(d, 498, "stable within ~3 min", fmean, CREAM, win(t, 12.1, 13.45, 0.12), stroke=4)
        ctext(d, 440, "TOXIC GRANULES DELIVERED", fcap, GOLD, win(t, 13.5, 16.2), stroke=5)
        ctext(d, 440, "APOPTOSIS", fchip, CREAM, win(t, 17.42, 19.65, 0.12), chip=RED)
        ctext(d, 508, "the cancer cell self-destructs", fmean, CREAM, win(t, 17.6, 19.65), stroke=4)
    # end
    e = typed("A LIVING DRUG.", t, 20.15, 18); ctext(d, 320, e, fend, CREAM, 1.0, stroke=7)
    ea = win(t, 20.5, 22.2, 0.3, 0.01)
    ctext(d, 1390, "timings from one cell pair in a lab dish", fsrc, CREAM, ea * 0.85, stroke=3)
    ctext(d, 1428, "Lee et al., eLife 2020", fsrc, CREAM, ea * 0.85, stroke=3)
    # impact flashes (max 14%, playbook 3.5)
    for ts, amp, dur in ((0.0, 0.10, 4), (8.7, 0.08, 4), (17.3, 0.14, 6)):
        k = f - int(round(ts * FPS))
        if 0 <= k < dur:
            im = Image.alpha_composite(Image.new("RGBA", (W, H), (255, 244, 225, int(255 * amp * (1 - k / dur)))), im)
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("overlay ok, timer monotonic, final", last)
