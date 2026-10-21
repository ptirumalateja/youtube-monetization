# The Ship Never Moves: text, counters and markers composited over the rendered frames.
# python3 overlay.py frames_dir proj.json out.mp4   (video only; mux.sh adds the sound)
import sys, json, math, subprocess
from PIL import Image, ImageDraw, ImageFont
FR, PJ, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
P = json.load(open(PJ)); PF = P['f']
W, H, FPS = 1080, 1920, 30; N = 660
MB = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"; MR = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p, s): return ImageFont.truetype(p, s)
CREAM = (246, 240, 228); RED = (214, 62, 48); GOLD = (255, 184, 82); TEAL = (70, 226, 210)
def clamp(x): return max(0.0, min(1.0, x))
def sstep(a, b, x): k = clamp((x - a) / (b - a)); return k * k * (3 - 2 * k)
def win(t, a, b, fi=0.25, fo=0.3): return sstep(a, a + fi, t) * (1 - sstep(b - fo, b, t))

f_hook = F(MB, 70); f_chip = F(MB, 54); f_cap = F(MB, 44); f_cnt = F(MB, 92); f_lab = F(MR, 27); f_unit = F(MB, 36); f_tag = F(MR, 26); f_mark = F(MB, 34)

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
SIG_ARRIVE = PF[int(15.3 * FPS)]['sig']
def dist_ly(f): return 4.2 * min(1.0, PF[f]['sig'] / SIG_ARRIVE)
def ship_clock(t): return max(0.0, t - 1.95)
prev = -1
for f in range(N):
    v = dist_ly(f); assert v >= prev - 1e-9, ("distance went backwards", f); prev = v
prev = -1
for f in range(N):
    v = ship_clock(f / FPS); assert v >= prev - 1e-9; prev = v

HOOK1 = "THIS SHIP NEVER MOVES."; HOOK2 = "YET IT OUTRUNS LIGHT."
TW1 = "IT NEEDS NEGATIVE ENERGY."; TW2a = "NOBODY KNOWS IF ENOUGH"; TW2b = "CAN EVER EXIST."
END1 = "SPACE MOVED."; END2 = "THE SHIP NEVER DID."

def draw(t, f):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    # tag (always on)
    ctext(d, 112, "THOUGHT EXPERIMENT · NOT TO SCALE", f_tag, CREAM, 0.72, stroke=4)
    # hook: typed fast, done by ~1.9 s
    a = 1 - sstep(3.3, 3.75, t)
    ctext(d, 250, typed(HOOK1, t, 0.0, 17), f_hook, CREAM, a)
    cchip(d, 352, typed(HOOK2, t, 1.25, 30), f_chip, a, HOOK2)
    # readouts: distance odometer (left) + ship's own speed (red chip)
    ra = win(t, 3.5, 16.25, 0.35, 0.35)
    if ra > 0:
        text(d, 64, 1338, "DISTANCE CROSSED", f_lab, CREAM, ra, stroke=4)
        v = dist_ly(f); s = f"{v:.2f}"; text(d, 64, 1372, s, f_cnt, CREAM, ra)
        text(d, 64 + tw(d, s, f_cnt) + 14, 1420, "LIGHT-YEARS", f_unit, CREAM, ra)
        chip(d, 78, 1494, "SHIP'S OWN SPEED: 0", f_mark, ra)
    # squeeze / stretch labels (3D grid colours: gold = squeezed, teal = stretched)
    la = win(t, 4.0, 8.2, 0.35, 0.4)
    ctext(d, 300, "SPACE SQUEEZES AHEAD", f_cap, GOLD, la)
    x2 = W - 64 - tw(d, "BEHIND", f_cap)
    text(d, W - 64 - tw(d, "SPACE STRETCHES", f_cap), 1180, "SPACE STRETCHES", f_cap, TEAL, la * sstep(4.8, 5.2, t))
    text(d, x2, 1232, "BEHIND", f_cap, TEAL, la * sstep(4.8, 5.2, t))
    # inside the bubble
    ia = win(t, 9.05, 11.25, 0.3, 0.3)
    ctext(d, 280, "INSIDE: FLAT, STILL SPACE", f_cap, CREAM, ia)
    ctext(d, 340, "NO PUSH. NO G-FORCE.", f_cap, CREAM, ia * sstep(9.6, 9.9, t))
    ca = ia * sstep(10.0, 10.3, t)
    if ca > 0:
        c = ship_clock(t); s = f"SHIP CLOCK  0:{int(c):02d}.{int(c * 10) % 10}"
        x = W - 64 - tw(d, s, f_mark); text(d, x, 1180, s, f_mark, CREAM, ca); text(d, W - 64 - tw(d, "TICKS NORMALLY", f_lab), 1226, "TICKS NORMALLY", f_lab, CREAM, ca, stroke=4)
    # light beam: marker on the beam's head + caption
    L = PF[f]['light']; ma = win(t, 12.6, 15.25, 0.3, 0.3)
    if L and ma > 0:
        x, y = L[0] * W, L[1] * H
        if 0 < x < W and 0 < y < H * 0.80:
            d.ellipse((x - 26, y - 26, x + 26, y + 26), outline=RED + (int(255 * ma),), width=5)
            chip(d, x - 150, y - 16, "LIGHT", f_mark, ma)
    text(d, 64, 840, "A LIGHT BEAM,", f_chip, CREAM, win(t, 12.9, 15.25, 0.3, 0.3))
    text(d, 64, 910, "LEFT BEHIND.", f_chip, CREAM, win(t, 13.5, 15.25, 0.3, 0.3))
    # twist (after the held breath)
    ta = win(t, 16.2, 19.4, 0.05, 0.4)
    cchip(d, 260, typed(TW1, t, 16.2, 40), f_chip, ta, TW1)
    ctext(d, 352, typed(TW2a, t, 17.0, 30), f_cap, CREAM, ta)
    ctext(d, 404, typed(TW2b, t, 17.0 + len(TW2a) / 30, 30), f_cap, CREAM, ta)
    # end line (thesis), fades just before the loop point
    ea = 1 - sstep(21.55, 21.93, t)
    ctext(d, 250, typed(END1, t, 19.6, 18), f_hook, CREAM, ea)
    ctext(d, 340, typed(END2, t, 19.6 + len(END1) / 18 + 0.25, 18), f_hook, GOLD, ea)
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
