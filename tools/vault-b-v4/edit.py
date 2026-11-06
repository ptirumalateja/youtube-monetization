"""Vault B v4 'The Door': Blender clean plates (tools/vault-b-v4/plates/clean) + Teja's Google Flow clips (flow/),
new BlackvieW VO (vo/blackview_v2.mp3) with a gap after "door" for the strike. Writes output/vault-b-v4_silent.mp4 (1080x1920, 24 fps)
and output/flow_audio.json (where each Flow clip plays, so mix.py can lay its own audio under it).
python3 edit.py [--frames A B] [--out FILE]
"""
import json, os, sys, glob, subprocess, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

R = os.path.dirname(os.path.abspath(__file__)); FONTS = os.path.join(R, "..", "vault-b", "fonts")
W, H, FPS = 1080, 1920, 24
rng = np.random.default_rng(11)

# ---------------- VO timing (blackview_v2 word starts, seconds) ----------------
VOICE = os.environ.get("VOICE", "viraj")   # Teja 6 Nov: use Viraj
CUT = 2.84 if VOICE == "viraj" else 2.70   # VO is split here (after "door.") and the rest is pushed back by GAP
STRIKE_AT = 2.40 if VOICE == "viraj" else 2.26   # the giant cobra appears on "door"
S0, S_FAST, S_LUNGE, S_END = 6.2, 1.5, 1.1, 9.62   # strike_floor.mp4: in-point, rise speed, lunge speed, out-point
LUNGE = 7.45
STRIKE_END = STRIKE_AT + (LUNGE - S0) / S_FAST + (S_END - LUNGE) / S_LUNGE
BENEATH = STRIKE_END + 0.30
GAP = None
W0_BV = dict(they=0.10, warned=0.46, never=1.44, open=1.88, door=2.30, beneath=3.02, padma=3.42, temple=4.52, kerala=5.04, six=5.98,
          vaults=6.62, in2011=7.58, opened=8.60, five=9.02, gold=9.78, idols=10.06, eighteen=11.06, chain=12.02, sacks=12.68, coins=13.58,
          crowns=14.26, diamonds=15.08, over=16.02, lakh=16.50, rupees=17.08, rupees_end=17.62, then=18.14, reached=19.12, vaultb=19.48, b_end=19.92,
          handle=20.48, lock=21.38, keyhole=22.14, keyhole_end=22.72, just=23.14, cobras=23.54, guarding=24.28, door2_end=24.98,
          legend=25.48, naga=27.46, only=28.92, chant=29.68, openit=30.26, openit_end=30.76, weeks=31.26, man=32.36, was=34.84, dead=35.06,
          dead_end=35.38, still=35.96, shut_end=37.08, would=37.72, end=38.54)
W0_VJ = dict(they=0.10, warned=0.42, never=1.78, open=2.14, door=2.44, beneath=3.28, padma=3.62, temple=4.54, kerala=5.06, six=6.12,
          vaults=6.80, in2011=7.68, opened=8.88, five=9.26, gold=10.02, idols=10.26, eighteen=11.32, chain=12.62, sacks=13.30, coins=14.26,
          crowns=14.94, diamonds=15.68, over=16.64, lakh=17.30, rupees=18.12, rupees_end=18.56, then=19.00, reached=20.22, vaultb=20.66, b_end=21.10,
          handle=21.38, lock=22.10, keyhole=22.68, keyhole_end=23.22, just=23.48, cobras=23.94, guarding=24.68, door2_end=25.30,
          legend=26.10, naga=28.00, only=29.40, chant=30.64, openit=31.28, openit_end=31.70, weeks=32.80, man=34.04, was=36.60, dead=36.80,
          dead_end=37.04, still=37.90, shut_end=39.00, would=39.64, end=40.30)
W0 = W0_VJ if VOICE == "viraj" else W0_BV
GAP = BENEATH - W0["beneath"]
st = lambda k: W0[k] + (GAP if W0[k] >= CUT else 0.0)
DUR = st("end") + 1.9

# ---------------- sources ----------------
@functools.lru_cache(maxsize=48)
def img(path):
    return cv2.imread(path, cv2.IMREAD_COLOR).astype(np.float32) / 255.0

_fc = {}
def frames(kind, name):
    key = (kind, name)
    if key not in _fc:
        _fc[key] = sorted(glob.glob(f"{R}/plates/clean/{name}/f*.jpg")) if kind == "plate" else sorted(glob.glob(f"{R}/flow/{name}_frames/*.jpg"))
    return _fc[key]

def src_frame(kind, name, tsec):
    fs = frames(kind, name); return img(fs[int(np.clip(round(tsec * FPS), 0, len(fs) - 1))])

GOLD = "/mnt/project-files/final-reels/vault-b-stills-v4/01-gold_clean.jpg"

def fit(im, zoom=1.0, cx=0.5, cy=0.5, rot=0.0, wm=False):
    """uniform cover-scale into 9:16 (never stretched). wm=True keeps the bottom 13.5% (Veo sparkle) out of frame."""
    h, w = im.shape[:2]; wm = wm and h > w
    if wm: zoom *= 1.16
    s = max(W / w, H / h) * zoom
    vis_w, vis_h = W / s / w, H / s / h            # visible fraction of the source
    if wm: cy = min(cy, 0.865 - vis_h / 2)
    cx = float(np.clip(cx, vis_w / 2, 1 - vis_w / 2)); cy = float(np.clip(cy, vis_h / 2, 1 - vis_h / 2))
    M = cv2.getRotationMatrix2D((cx * w, cy * h), rot, s)
    M[0, 2] += W / 2 - cx * w; M[1, 2] += H / 2 - cy * h
    return cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# ---------------- grade / fx ----------------
def grade(f, mode, amt=1.0):
    if mode == "warm":
        f = f * np.array([0.9, 1.0, 1.06], np.float32); f = f / (1 + 0.12 * f) * 1.08
    elif mode == "horror":   # crushed, red-gold, high contrast for the hook flashes
        f = np.clip((f - 0.06) * 1.35, 0, None) * np.array([0.78, 0.92, 1.12], np.float32)
    elif mode == "cold":
        l = (f * np.array([0.11, 0.59, 0.30], np.float32)).sum(2, keepdims=True)
        hi = np.clip((f.max(2, keepdims=True) - 0.62) / 0.3, 0, 1)
        sat = 1 - 0.6 * amt * (1 - hi); f = l + (f - l) * sat
        f = f * np.array([1 + 0.14 * amt, 1 + 0.03 * amt, 1 - 0.10 * amt], np.float32) * (0.94 + 0.06 * (1 - amt))
    return f

_y, _x = np.mgrid[0:H, 0:W].astype(np.float32)
VIG = (1 - 0.18 * np.clip((np.sqrt(((_x - W / 2) / (W * 0.75)) ** 2 + ((_y - H / 2) / (H * 0.62)) ** 2) - 0.5) / 0.6, 0, 1) ** 1.5)[..., None]
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
def grain(f, i, a=0.022):
    return f + cv2.resize(GRAIN[i % 6], (W, H))[..., None] * a * (0.4 + 0.6 * f)

COINS = [dict(x=rng.uniform(0, W), y0=rng.uniform(-H, H), v=rng.uniform(380, 900), r=rng.uniform(10, 34), w=rng.uniform(3, 9), ph=rng.uniform(0, 6.3)) for _ in range(90)]
def coin_rain(f, t, density=1.0, start=0.0):
    layer = np.zeros((H, W, 3), np.float32); n = int(len(COINS) * density * 0.3)
    for c in COINS[:n]:
        y = (c["y0"] + c["v"] * (t - start)) % (H + 200) - 100; sx = abs(math.cos(c["w"] * t + c["ph"]))
        ax = (int(c["r"]), max(2, int(c["r"] * (0.15 + 0.85 * sx)))); b = (0.55 + 0.45 * sx) * 0.7
        cv2.ellipse(layer, (int(c["x"]), int(y)), ax, (c["ph"] * 40) % 180, 0, 360, (0.25 * b, 0.62 * b, 1.0 * b), -1, cv2.LINE_AA)
    mb = cv2.blur(layer, (1, 25)); blur = cv2.GaussianBlur(layer, (0, 0), 9) * 0.35
    return f * (1 - np.clip(mb.max(2, keepdims=True), 0, 1) * 0.9) + mb * 0.95 + blur

# ---------------- text (Cinzel) ----------------
def cfont(size, weight=700):
    f = ImageFont.truetype(os.path.join(FONTS, "Cinzel.ttf"), size)
    try: f.set_variation_by_axes([weight])
    except Exception: pass
    return f
RUPEE = lambda size: ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf", int(size * 0.92))

def gold_grad(h):
    stops = [(0.0, (255, 246, 214)), (0.45, (240, 196, 110)), (0.55, (204, 146, 58)), (1.0, (255, 214, 140))]
    col = np.zeros((h, 3), np.float32)
    for y in range(h):
        t = y / max(1, h - 1)
        for (a, ca), (b, cb) in zip(stops, stops[1:]):
            if a <= t <= b: k = (t - a) / (b - a); col[y] = [ca[i] + (cb[i] - ca[i]) * k for i in range(3)]; break
    return col

@functools.lru_cache(maxsize=96)
def text_rgba(lines, size, weight, style, cy, track=2, step=1.18):
    mask = Image.new("L", (W, H), 0); d = ImageDraw.Draw(mask); f = cfont(size, weight)
    sp = int(size * step); y0 = cy - sp * (len(lines) - 1) / 2
    for li, ln in enumerate(lines):
        fonts = [RUPEE(size) if ch == "₹" else f for ch in ln]
        ws = [d.textlength(ch, font=fo) for ch, fo in zip(ln, fonts)]; tw = sum(ws) + track * (len(ln) - 1)
        asc, desc = f.getmetrics(); x = (W - tw) / 2; y = y0 + li * sp - (asc + desc) / 2
        for ch, wv, fo in zip(ln, ws, fonts):
            d.text((x, y + (size * 0.06 if fo is not f else 0)), ch, font=fo, fill=255); x += wv + track
    m = np.asarray(mask, np.float32) / 255.0; bb = mask.getbbox() or (0, 0, W, H)
    shadow = cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5))), (0, 0), size * 0.16) * 0.9
    glow = cv2.GaussianBlur(m, (0, 0), size * 0.22) * 0.45
    if style == "gold":
        g = np.zeros((H, W, 3), np.float32); gg = gold_grad(bb[3] - bb[1] + 2)[:, ::-1] / 255.0
        g[bb[1]:bb[1] + len(gg)] = gg[: H - bb[1]][:, None, :]; fill = g; glow_c = np.array([0.24, 0.62, 1.0], np.float32)
    elif style == "blood":
        fill = np.ones((H, W, 3), np.float32) * np.array([0.30, 0.34, 0.92], np.float32); glow_c = np.array([0.02, 0.04, 0.7], np.float32)
    elif style == "ice":
        fill = np.ones((H, W, 3), np.float32) * np.array([0.93, 0.93, 0.90], np.float32); glow_c = np.array([0.9, 0.75, 0.55], np.float32)
    else:
        fill = np.ones((H, W, 3), np.float32) * np.array([0.86, 0.94, 1.0], np.float32); glow_c = np.array([0.24, 0.62, 1.0], np.float32)
    edge = np.clip(np.roll(m, 2, 0) - m, 0, 1)[..., None]
    a = shadow[..., None]; col = np.zeros((H, W, 3), np.float32) + np.array([0.02, 0.03, 0.05], np.float32) * a
    col = col * (1 - glow[..., None]) + glow_c * glow[..., None] * 0.9; a = a + glow[..., None] * (1 - a) * 0.6
    col = col * (1 - edge) + np.array([0.05, 0.2, 0.35], np.float32) * edge; a = np.maximum(a, edge)
    mm = m[..., None]; col = col * (1 - mm) + fill * mm; a = a * (1 - mm) + mm
    return col.astype(np.float32), np.clip(a, 0, 1).astype(np.float32)

def put_text(f, lines, t, t0, t1, size=92, weight=900, style="cream", cy=1240, pop=True, fade=0.1, track=2):
    if not (t0 <= t < t1): return f
    col, a = text_rgba(tuple(lines), size, weight, style, cy, track)
    k = min(1, (t - t0) / fade, (t1 - t) / fade)
    if pop:
        s = 1 + 0.08 * max(0, 1 - (t - t0) / 0.18)
        if s > 1.001:
            M = cv2.getRotationMatrix2D((W / 2, cy), 0, s); col = cv2.warpAffine(col, M, (W, H)); a = cv2.warpAffine(a, M, (W, H))
            if a.ndim == 2: a = a[..., None]
    return f * (1 - a * k) + col * k

TAG_SH = (np.exp(-(((_x - W / 2) / 560) ** 2 + ((_y - 300) / 170) ** 2) * 1.6) * 0.55)[..., None]
def tag(f, alpha):
    if alpha <= 0: return f
    f = f * (1 - TAG_SH * alpha)
    for c, a in (text_rgba(("PADMANABHASWAMY",), 66, 800, "gold", 262, 4), text_rgba(("TEMPLE  ·  KERALA",), 36, 700, "gold", 344, 10)):
        f = f * (1 - a * alpha) + c * alpha
    for y in (198, 392): f[y:y + 2, 210:870] = f[y:y + 2, 210:870] * (1 - 0.85 * alpha) + np.array([0.36, 0.70, 0.89], np.float32) * 0.85 * alpha
    return f

# ---------------- edit decision list ----------------
# (t0, t1, kind, name, args, grade)  kind: plate | flow | gold | black.  args: src (s), speed, z0/z1 zoom, c0/c1 centre, coins
s = st
HOOK = [  # flashes under "They were warned... never to open the door"
    ("flow", "coins", dict(src=5.2, z0=1.25, z1=1.4, c0=(0.42, 0.62))),        # cobra eye over the gold
    ("flow", "blood", dict(src=7.4, z0=1.2, z1=1.35, c0=(0.5, 0.7))),          # blood spreading
    ("flow", "corridor", dict(src=7.6, z0=1.15, z1=1.3, c0=(0.5, 0.35))),      # giant hood in the corridor
    ("gold", "gold", dict(z0=1.35, z1=1.5, c0=(0.5, 0.55))),                   # the gold
    ("flow", "carvings", dict(src=5.1, z0=1.3, z1=1.45, c0=(0.5, 0.58))),      # red eyes ignite
    ("flow", "blood", dict(src=3.4, z0=1.18, z1=1.28, c0=(0.5, 0.55))),        # blood seeping under the door
    ("flow", "coins", dict(src=1.0, z0=1.2, z1=1.35, c0=(0.4, 0.6))),          # scales sliding
    ("plate", "door", dict(src=1.0, z0=1.05, z1=1.2, c0=(0.5, 0.45))),         # the door
    ("flow", "strike", dict(src=8.9, z0=1.0, z1=1.12, c0=(0.5, 0.45))),        # fangs (sub-flash)
    ("flow", "corridor", dict(src=4.4, z0=1.05, z1=1.15, c0=(0.5, 0.4))),      # giant cobra rearing in the corridor
]
cuts = [c * STRIKE_AT / 2.26 for c in [0.0, 0.24, 0.46, 0.70, 0.92, 1.14, 1.34, 1.52, 1.86, 1.96]] + [STRIKE_AT]
EDL = [(a, b, k, n, dict(ar, flash=True), "horror") for (a, b), (k, n, ar) in zip(zip(cuts, cuts[1:]), HOOK)]
EDL += [
    (STRIKE_AT, STRIKE_END, "strike", "strike_floor", {}, "warm"),
    (STRIKE_END, BENEATH - 0.06, "black", "", {}, None),
    (BENEATH - 0.06, s("six") - 0.06, "plate", "gopuram", dict(src=0, speed=0.62, z0=1.0, z1=1.08, c0=(0.5, 0.5), c1=(0.5, 0.46)), "warm"),
    (s("six") - 0.06, s("gold") - 0.06, "plate", "vaults", dict(src=0, speed=0.52, z0=1.0, z1=1.04), "warm"),          # slow-mo doors opening
    (s("gold") - 0.06, s("eighteen") - 0.06, "gold", "gold", dict(z0=1.0, z1=1.1, c0=(0.5, 0.56), c1=(0.52, 0.5), coins=0.6), "warm"),
    (s("eighteen") - 0.06, s("sacks") - 0.06, "flow", "coins", dict(src=0.9, z0=1.0, z1=1.06), "warm"),                # cobra sliding over coins
    (s("sacks") - 0.06, s("crowns") - 0.06, "flow", "coins", dict(src=3.1, z0=1.0, z1=1.08), "warm"),
    (s("crowns") - 0.06, s("diamonds") - 0.06, "gold", "gold", dict(z0=1.7, z1=1.85, c0=(0.47, 0.42), c1=(0.47, 0.40), coins=0.4), "warm"),
    (s("diamonds") - 0.06, s("over") - 0.08, "flow", "coins", dict(src=5.0, z0=1.0, z1=1.08), "warm"),                # the eye passes
    (s("over") - 0.08, s("then") - 0.45, "flow", "corridor", dict(src=0.6, speed=1.0, z0=1.0, z1=1.06), "warm"),       # 30-ft cobra in the money
    (s("then") - 0.45, s("then"), "black", "", {}, None),
    (s("then"), s("vaultb") - 0.04, "plate", "lamp", dict(src=0, speed=0.75, z0=1.0, z1=1.05), "cold"),
    (s("vaultb") - 0.04, s("handle") - 0.06, "plate", "door", dict(src=0.2, speed=0.8, z0=1.0, z1=1.12, c0=(0.5, 0.5), c1=(0.5, 0.42)), "cold"),
    (s("handle") - 0.06, s("lock") - 0.06, "plate", "heads", dict(src=0, speed=0.9, z0=1.0, z1=1.05), "cold"),
    (s("lock") - 0.06, s("keyhole") - 0.06, "plate", "seam", dict(src=0, speed=0.9, z0=1.0, z1=1.06), "cold"),
    (s("keyhole") - 0.06, s("just") - 0.1, "plate", "seam", dict(src=1.0, speed=0.9, z0=1.25, z1=1.35, c0=(0.5, 0.5)), "cold"),
    (s("just") - 0.1, s("legend") - 0.08, "flow", "carvings", dict(src=2.6, speed=1.0, z0=1.0, z1=1.05), "cold"),       # the two cobras turn, eyes ignite
    (s("legend") - 0.08, s("naga") - 0.08, "plate", "heads", dict(src=0.6, speed=0.6, z0=1.15, z1=1.3, c0=(0.5, 0.42)), "cold"),
    (s("naga") - 0.08, s("weeks") - 0.3, "flow", "carvings", dict(src=5.25, speed=1.0, z0=1.0, z1=1.08), "cold"),       # mouths open, hiss
    (s("weeks") - 0.3, s("dead") - 0.06, "plate", "hand", dict(src=0, speed=0.4, z0=1.0, z1=1.1, c0=(0.5, 0.5), c1=(0.5, 0.55)), "cold"),
    (s("dead") - 0.06, s("still") - 0.12, "flow", "blood", dict(src=7.2, speed=1.0, z0=1.0, z1=1.05), "cold"),
    (s("still") - 0.12, s("would") - 0.08, "plate", "door", dict(src=0.5, speed=0.6, z0=1.15, z1=1.0, c0=(0.5, 0.45)), "cold"),
    (s("would") - 0.08, s("end") + 0.55, "flow", "corridor", dict(src=8.0, speed=1.0, z0=1.0, z1=1.1, c0=(0.5, 0.45)), "warm"),
    (s("end") + 0.55, s("end") + 0.85, "flow", "strike", dict(src=8.6, speed=1.0, z0=1.05, z1=1.25, c0=(0.5, 0.5)), "horror"),  # last strike
    (s("end") + 0.85, DUR + 1, "black", "", {}, None),
]
GOPURAM_T0 = BENEATH - 0.06

CAPS = [  # (lines, t0, t1, kw)
    (["THEY WERE WARNED"], s("warned"), s("open") - 0.04, dict(size=78)),
    (["NEVER TO OPEN", "THE DOOR."], s("open") - 0.04, STRIKE_AT + 0.5, dict(size=96)),
    (["6 SECRET VAULTS"], s("six"), s("in2011") - 0.06, dict(size=92, style="gold", cy=1500)),
    (["2011.", "THEY OPENED FIVE."], s("in2011"), s("gold") - 0.06, dict(size=88, cy=1500)),
    (["GOLD IDOLS"], s("gold"), s("eighteen") - 0.06, dict(size=100, style="gold", cy=1300)),
    (["AN 18-FOOT", "GOLD CHAIN"], s("eighteen"), s("sacks") - 0.06, dict(size=96, style="gold", cy=1300)),
    (["SACKS OF", "ANCIENT COINS"], s("sacks"), s("crowns") - 0.06, dict(size=92, style="gold", cy=1300)),
    (["CROWNS"], s("crowns"), s("diamonds") - 0.06, dict(size=110, style="gold", cy=1300)),
    (["DIAMONDS"], s("diamonds"), s("over") - 0.08, dict(size=110, style="gold", cy=1300)),
    (["OVER", "₹1 LAKH CRORE"], s("lakh") - 0.1, s("then") - 0.45, dict(size=104, style="gold", cy=1250)),
    (["THEN THEY", "REACHED..."], s("then"), s("vaultb") - 0.04, dict(size=92, style="ice", cy=720)),
    (["VAULT B."], s("vaultb"), s("handle") - 0.06, dict(size=160, style="ice", cy=1480)),
    (["NO HANDLE."], s("handle"), s("just") - 0.1, dict(size=92, style="ice", cy=1240)),
    (["NO LOCK."], s("lock"), s("just") - 0.1, dict(size=92, style="ice", cy=1360)),
    (["NO KEYHOLE."], s("keyhole"), s("just") - 0.1, dict(size=92, style="ice", cy=1480)),
    (["JUST TWO COBRAS", "GUARDING THE DOOR."], s("cobras") - 0.1, s("legend") - 0.08, dict(size=72, style="ice", cy=1520)),
    (["Legend says it is sealed by"], s("legend"), s("naga") - 0.08, dict(size=62, weight=700, style="ice", cy=1460, pop=False)),
    (["NAGA BANDHAM"], s("naga") - 0.08, s("only") - 0.08, dict(size=94, style="gold", cy=1460)),
    (["Only a perfect chant", "can open it."], s("only") - 0.08, s("weeks") - 0.3, dict(size=66, weight=700, style="ice", cy=1460, pop=False)),
    (["Weeks later, the man", "who fought to open", "the vaults..."], s("weeks"), s("was") - 0.08, dict(size=62, weight=700, style="ice", cy=1460, pop=False)),
    (["WAS DEAD."], s("was") - 0.04, s("still") - 0.12, dict(size=130, style="blood", cy=1300)),
    (["VAULT B IS", "STILL SHUT."], s("still") - 0.12, s("would") - 0.08, dict(size=100, style="ice", cy=1520)),
    (["WOULD YOU", "OPEN IT?"], s("would") - 0.08, s("end") + 0.55, dict(size=120, style="gold", cy=1480)),
]
PUNCH = [s(k) for k in ["five", "gold", "eighteen", "sacks", "crowns", "diamonds", "lakh", "vaultb", "handle", "lock", "keyhole", "naga", "was"]]

def strike_src(lt):
    """strike_floor.mp4 time for local time lt: hood high (fast) -> lunge into the lens (near real time)"""
    t_rise = (LUNGE - S0) / S_FAST
    return S0 + lt * S_FAST if lt < t_rise else LUNGE + (lt - t_rise) * S_LUNGE

def ease(u): return u * u * (3 - 2 * u) * 0.35 + u * 0.65

def shot(t):
    for t0, t1, kind, name, a, gmode in EDL:
        if t0 <= t < t1: break
    lt = t - t0; u = (t - t0) / max(1e-3, t1 - t0); e = ease(u)
    if kind == "black": return np.zeros((H, W, 3), np.float32), None
    z = a.get("z0", 1.0) + (a.get("z1", a.get("z0", 1.0)) - a.get("z0", 1.0)) * e
    c0 = a.get("c0", (0.5, 0.5)); c1 = a.get("c1", c0); cx, cy = c0[0] + (c1[0] - c0[0]) * e, c0[1] + (c1[1] - c0[1]) * e
    if kind == "strike":
        ts = strike_src(lt); f = fit(src_frame("flow", name, ts), 1.0 + 0.06 * u, 0.5, 0.45, wm=True)
        if ts > 8.3:  # landing shake
            k = min(1, (ts - 8.3) / 0.3); M = np.float32([[1, 0, 14 * k * math.sin(t * 61)], [0, 1, 10 * k * math.cos(t * 53)]])
            f = cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    elif kind == "gold":
        f = fit(img(GOLD), z, cx, cy)
        if a.get("coins"): f = coin_rain(f, t, a["coins"], t0)
    else:
        f = src_frame(kind, name, a.get("src", 0) + lt * a.get("speed", 1.0))
        f = fit(f, z, cx, cy, wm=(kind == "flow"))
    if a.get("flash"):  # hook flashes: hot first frame, fast decay
        f = f * (1 + 0.9 * max(0, 1 - lt / 0.06))
    amt = 1.0
    if gmode == "cold" and t < s("vaultb"): amt = np.clip((t - s("then")) / 1.0, 0, 1)
    if gmode: f = grade(f, gmode, amt)
    return f, gmode

def render(t, i):
    f, gmode = shot(t)
    for pt in PUNCH:
        if pt <= t < pt + 0.22:
            k = 1 - (t - pt) / 0.22
            M = cv2.getRotationMatrix2D((W / 2 + 6 * k * math.sin(t * 90), H / 2 + 6 * k * math.cos(t * 77)), 0, 1 + 0.04 * k)
            f = cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if gmode: f = f * (1 + 0.02 * math.sin(t * 7.1) + 0.012 * math.sin(t * 17.3))
    f = f * VIG
    # temple name: tag rises in on "Padmanabhaswamy", stays to the vaults
    ta = np.clip((t - (s("padma") - 0.15)) / 0.35, 0, 1) * np.clip((s("six") - 0.06 - t) / 0.2, 0, 1)
    f = tag(f, float(ta))
    for lines, t0, t1, kw in CAPS: f = put_text(f, lines, t, t0, t1, **kw)
    return np.clip(grain(f, i), 0, 1)

def flow_audio():
    """segments where a Flow clip is on screen: (t0, t1, clip, src_in, speed)"""
    out = []
    for t0, t1, kind, name, a, g in EDL:
        if kind == "flow": out.append(dict(t0=t0, t1=t1, clip=name, src=a.get("src", 0), speed=a.get("speed", 1.0), flash=bool(a.get("flash"))))
        if kind == "strike": out.append(dict(t0=t0, t1=t1, clip=name, src=S0, speed=1.0, flash=False))
    return out

def main():
    a = sys.argv[1:]
    os.makedirs(f"{R}/output", exist_ok=True)
    json.dump(dict(VOICE=VOICE, HOOK_CUTS=cuts, DUR=DUR, CUT=CUT, GAP=GAP, STRIKE_AT=STRIKE_AT, STRIKE_END=STRIKE_END, LUNGE_T=STRIKE_AT + (LUNGE - S0) / S_FAST,
                   words={k: st(k) for k in W0}, flow=flow_audio()), open(f"{R}/output/timeline.json", "w"), indent=1)
    if "--timeline" in a: return
    out = a[a.index("--out") + 1] if "--out" in a else f"{R}/output/vault-b-v4_silent.mp4"
    n0, n1 = 0, int(DUR * FPS)
    if "--frames" in a: n0, n1 = int(a[a.index("--frames") + 1]), min(n1, int(a[a.index("--frames") + 2]))
    if "--stills" in a:
        for tt in a[a.index("--stills") + 1].split(","):
            tt = float(tt); cv2.imwrite(f"{R}/output/still_{tt:05.2f}.jpg", (render(tt, int(tt * FPS)) * 255).astype(np.uint8))
        return
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(n0, n1):
        p.stdin.write((render(i / FPS, i) * 255 + 0.5).astype(np.uint8).tobytes())
        if i % 48 == 0: print("frame", i, "/", n1, flush=True)
    p.stdin.close(); p.wait(); print("wrote", out)

if __name__ == "__main__":
    main()
