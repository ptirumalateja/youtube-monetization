# The Ship Never Moves: text, counters and markers composited over the rendered frames.
# python3 overlay.py frames_dir proj.json out.mp4   (video only; mux.sh adds the sound)
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont
FR, PJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
P = json.load(open(PJ)); PF = P['f']
W, H, FPS = 1080, 1920, 30; N = 720
MB = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p, s): return ImageFont.truetype(p, s)
CREAM = (246, 240, 228); RED = (214, 62, 48); GOLD = (255, 184, 82); TEAL = (70, 226, 210)
def clamp(x): return max(0.0, min(1.0, x))
def sstep(a, b, x): k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k)
def win(t, a, b, fi=0.25, fo=0.3): return sstep(a, a + fi, t) * (1 - sstep(b - fo, b, t))

f_hook = F(MB, 76); f_chip = F(MB, 56); f_cap = F(MB, 46); f_cnt = F(MB, 92); f_lab = F(MR, 27); f_unit = F(MB, 36); f_tag = F(MR, 26); f_mark = F(MB, 34)

def tw(d, s, f): return d.textlength(s, font=f)
def text(d, x, y, s, f, fill, a, stroke=6):
    if a <= 0.01 or not s: return
    d.text((x, y), s, font=f, fill=fill + (int(255 * a),), stroke_width=stroke, stroke_fill=(0, 0, 0, int(235 * a)))
def ctext(d, y, s, f, fill, a, stroke=6): text(d, (W - tw(d, s, f)) / 2, y, s, f, fill, a, stroke)
def chip(d, x, y, s, f, a, full=None):
    if a <= 0.01 or not s: return
    w = tw(d, full or s, f) if full is not None else tw(d, s, f)
    d.rectangle((x - 14, y - 4, x + tw(d, s, f) + 14, y + f.size + 8), fill=RED + (int(245 * a),))
    d.text((x, y), s, font=f, fill=CREAM + (int(255 * a),))
def cchip(d, y, s, f, a, full): x = (W - tw(d, full, f)) / 2; chip(d, x, y, s, f, a)
def typed(s, t, t0, cps):           # characters revealed; never negative (playbook lesson: s[:n] with n<0)
    n = int((t - t0) * cps)
    return s[:max(0, min(len(s), n))]

# ---------------------------------------------------------------- counters (both must be monotonic)
TL = P['tl']
SIG_ARRIVE = PF[int(12.9 * FPS)]['sig']          # odometer lands on 4.20 as the star fills the frame
def dist_ly(f): return 4.2 * min(1.0, PF[f]['sig'] / SIG_ARRIVE)
def ship_clock(t): return max(0.0, t - TL['T_IGN'])
for fn in (lambda f: dist_ly(f), lambda f: ship_clock(f / FPS)):
    prev = -1
    for f in range(N):
        v = fn(f); assert v >= prev - 1e-9, ("counter went backwards", f); prev = v

HOOK1 = "THIS SHIP NEVER MOVES."; HOOK2 = "YET IT OUTRUNS LIGHT."
PL1 = "THE SHIP ISN'T FLYING."; PL2 = "SPACE IS."
TW1 = "IT NEEDS NEGATIVE ENERGY."; TW2a = "NOBODY KNOWS IF ENOUGH"; TW2b = "CAN EVER EXIST."
BL1 = "AND WHEN IT STOPS,"; BL2 = "IT BLASTS WHATEVER IS AHEAD."
END1 = "SPACE MOVED."; END2 = "THE SHIP NEVER DID."

def marker(d, pt, label, a, side=1):
    if not pt or a <= 0.01: return
    x, y = pt[0] * W, pt[1] * H
    if not (40 < x < W - 40 and 140 < y < H * 0.80): return
    d.ellipse((x - 24, y - 24, x + 24, y + 24), outline=RED + (int(255 * a),), width=5)
    tx = x + 40 if side > 0 else x - 40 - tw(d, label, f_mark) - 14
    tx = max(30, min(W - 30 - tw(d, label, f_mark) - 14, tx))
    chip(d, tx, y - 18, label, f_mark, a)

def draw(t, f):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); pf = PF[f]
    ctext(d, 112, "THOUGHT EXPERIMENT · NOT TO SCALE", f_tag, CREAM, 0.72, stroke=4)
    # hook: typed fast, done by ~1.8 s
    a = 1 - sstep(2.55, 2.95, t)
    ctext(d, 250, typed(HOOK1, t, 0.0, 22), f_hook, CREAM, a)
    cchip(d, 356, typed(HOOK2, t, 1.1, 32), f_chip, a, HOOK2)
    # readouts: distance odometer + ship's own speed
    ra = win(t, 2.8, 14.6, 0.3, 0.4)
    if ra > 0:
        text(d, 64, 1338, "DISTANCE CROSSED", f_lab, CREAM, ra, stroke=4)
        v = dist_ly(f); s = f"{v:.2f}"; text(d, 64, 1372, s, f_cnt, CREAM, ra)
        text(d, 64 + tw(d, s, f_cnt) + 14, 1420, "LIGHT-YEARS", f_unit, CREAM, ra)
        chip(d, 78, 1494, "SHIP'S OWN SPEED: 0", f_mark, ra)
    # squeeze / stretch
    la = win(t, 3.0, 4.9, 0.25, 0.3)
    ctext(d, 300, "SPACE SQUEEZES AHEAD", f_cap, GOLD, la)
    sa = la * sstep(3.5, 3.8, t)
    text(d, W - 64 - tw(d, "SPACE STRETCHES", f_cap), 1180, "SPACE STRETCHES", f_cap, TEAL, sa)
    text(d, W - 64 - tw(d, "BEHIND", f_cap), 1232, "BEHIND", f_cap, TEAL, sa)
    # planet pass
    pa = win(t, 5.0, 6.6, 0.2, 0.3)
    ctext(d, 280, typed(PL1, t, 5.0, 30), f_chip, CREAM, pa)
    ctext(d, 356, typed(PL2, t, 5.85, 24), f_hook, GOLD, pa)
    # inside the bubble
    ia = win(t, 6.95, 9.0, 0.25, 0.3)
    ctext(d, 280, "INSIDE: NO PUSH.", f_chip, CREAM, ia)
    ctext(d, 350, "NO G-FORCE.", f_chip, CREAM, ia * sstep(7.4, 7.7, t))
    ca = ia * sstep(7.9, 8.2, t)
    if ca > 0:
        c = ship_clock(t); s = f"SHIP CLOCK  0:{int(c):02d}.{int(c * 10) % 10}"
        text(d, W - 64 - tw(d, s, f_mark), 1180, s, f_mark, CREAM, ca); text(d, W - 64 - tw(d, "TICKS NORMALLY", f_lab), 1226, "TICKS NORMALLY", f_lab, CREAM, ca, stroke=4)
    # light beam
    ma = win(t, 10.2, 11.75, 0.25, 0.3)
    marker(d, pf['light'], "LIGHT", ma, side=-1)
    text(d, 64, 840, "A LIGHT BEAM,", f_chip, CREAM, win(t, 10.4, 11.75, 0.25, 0.3))
    text(d, 64, 910, "LEFT BEHIND.", f_chip, CREAM, win(t, 10.9, 11.75, 0.25, 0.3))
    # arrival
    aa = win(t, 12.9, 14.05, 0.25, 0.3)
    ctext(d, 280, "4.2 LIGHT-YEARS LATER:", f_cap, CREAM, aa)
    ctext(d, 340, "THE NEAREST STAR.", f_chip, GOLD, aa * sstep(13.2, 13.45, t))
    # twist 1: negative energy (marker on the ring)
    ta = win(t, T1 := TL['T_TWIST'], 17.1, 0.05, 0.3)
    cchip(d, 260, typed(TW1, t, T1, 40), f_chip, ta, TW1)
    ctext(d, 352, typed(TW2a, t, T1 + 0.8, 30), f_cap, CREAM, ta)
    ctext(d, 404, typed(TW2b, t, T1 + 0.8 + len(TW2a) / 30, 30), f_cap, CREAM, ta)
    marker(d, pf['ringL'], "NEGATIVE ENERGY", ta * sstep(T1 + 0.5, T1 + 0.8, t), side=1)
    # twist 2: the stop-blast
    ba = win(t, 17.2, 20.6, 0.1, 0.35)
    ctext(d, 260, typed(BL1, t, 17.2, 30), f_chip, CREAM, ba)
    cchip(d, 340, typed(BL2, t, TL['T_BLAST'] + 0.05, 45), f_chip, ba, BL2)
    # end line (thesis), fades just before the loop point
    ea = 1 - sstep(23.55, 23.93, t)
    ctext(d, 250, typed(END1, t, 20.8, 18), f_hook, CREAM, ea)
    ctext(d, 344, typed(END2, t, 20.8 + len(END1) / 18 + 0.25, 18), f_hook, GOLD, ea)
    return im

ff = subprocess.Popen(["ffmpeg", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                       "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p", OUT], stdin=subprocess.PIPE)
for f in range(N):
    t = f / FPS
    base = Image.open(f"{FR}/f{f:04d}.jpg").convert("RGBA")
    if base.size != (W, H): base = base.resize((W, H), Image.LANCZOS)
    base.alpha_composite(draw(t, f))
    ff.stdin.write(base.convert("RGB").tobytes())
ff.stdin.close(); ff.wait()
print("ok", OUT)
