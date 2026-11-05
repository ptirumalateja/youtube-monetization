"""Vault B v3 'The Door' - chief-editor cut. No Blender: real Commons photos + video, my own Three.js shots (tools/vault-b),
2D coin rain / dust / grade / text here. Writes output/vault-b-v3.mp4 (1080x1920, 24 fps) muxed with audio/vault-b-v3-mix.wav.
python3 edit.py [--preview START END]   (preview renders a range at half res, fast)
"""
import json, os, sys, glob, subprocess, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

R = os.path.dirname(os.path.abspath(__file__)); FONTS = os.path.join(R, "..", "vault-b", "fonts")
W, H, FPS = 1080, 1920, 24
T = {x["key"]: x for x in json.load(open(f"{R}/vo/vo_timeline.json"))}
st = lambda k: T[k]["start"]; en = lambda k: T[k]["end"]
DUR = en("would") + 2.6
rng = np.random.default_rng(7)

# ---------------- sources ----------------
@functools.lru_cache(maxsize=8)
def photo(name):
    im = cv2.imread(name if "/" in name else f"{R}/footage/temple/{name}", cv2.IMREAD_COLOR)
    return im.astype(np.float32) / 255.0

@functools.lru_cache(maxsize=6)
def still(path):
    return cv2.imread(path, cv2.IMREAD_COLOR).astype(np.float32) / 255.0

def seq_frames(name):
    return sorted(glob.glob(f"{R}/cg/{name}/f*.jpg"))

_seqcache = {}
def seq(name, i):
    fs = _seqcache.setdefault(name, seq_frames(name))
    if not fs: return np.zeros((H, W, 3), np.float32)
    i = int(np.clip(i, 0, len(fs) - 1)); return still(fs[i])

_vidcache = {}
def vid(name, t):
    """frames pre-extracted at 24 fps into footage/snake/<name>_frames/"""
    fs = _vidcache.setdefault(name, sorted(glob.glob(f"{R}/footage/snake/{name}_frames/*.jpg")))
    if not fs: return None
    return still(fs[int(np.clip(round(t * FPS), 0, len(fs) - 1))])

def fit(img, zoom=1.0, cx=0.5, cy=0.5, rot=0.0):
    """cover-crop img into 9:16 at zoom, centred on (cx, cy) in source-relative coords"""
    h, w = img.shape[:2]; s = max(W / w, H / h) * zoom
    M = cv2.getRotationMatrix2D((cx * w, cy * h), rot, s)
    M[0, 2] += W / 2 - cx * w; M[1, 2] += H / 2 - cy * h
    # clamp so we never show outside the image
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

def kb(img, u, z0, z1, c0, c1, rot=0.0):
    e = u * u * (3 - 2 * u) * 0.35 + u * 0.65
    return fit(img, z0 + (z1 - z0) * e, c0[0] + (c1[0] - c0[0]) * e, c0[1] + (c1[1] - c0[1]) * e, rot)

# ---------------- grade / fx ----------------
def grade(f, mode, t, amt=1.0):
    if mode == "warm":
        f = f * np.array([0.86, 1.0, 1.08], np.float32)  # BGR: push red/gold
        f = np.clip(f, 0, None); f = f / (1 + 0.15 * f)
        f = f * 1.08
    elif mode == "night":
        l = f.mean(2, keepdims=True); f = l + (f - l) * 0.85
        f = f * np.array([0.92, 1.0, 1.06], np.float32)
    elif mode == "cold":
        l = (f * np.array([0.11, 0.59, 0.30], np.float32)).sum(2, keepdims=True)
        hi = np.clip((f.max(2, keepdims=True) - 0.62) / 0.3, 0, 1)  # flames / red eyes keep their colour
        sat = 1 - 0.72 * amt * (1 - hi); f = l + (f - l) * sat
        f = f * np.array([1 + 0.16 * amt, 1 + 0.03 * amt, 1 - 0.12 * amt], np.float32)  # teal-steel
        f = f * (0.92 + 0.08 * (1 - amt))
    return f

def vignette():
    y, x = np.mgrid[0:H, 0:W].astype(np.float32); d = np.sqrt(((x - W / 2) / (W * 0.75)) ** 2 + ((y - H / 2) / (H * 0.62)) ** 2)
    return (1 - 0.22 * np.clip((d - 0.45) / 0.6, 0, 1) ** 1.5)[..., None]
VIG = vignette()
GRAIN = [rng.normal(0, 1, (H // 2, W // 2)).astype(np.float32) for _ in range(6)]
def grain(f, i, a=0.028):
    g = cv2.resize(GRAIN[i % 6], (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    return f + g * a * (0.4 + 0.6 * f)

# 2D falling coins (warm discs that turn edge-on as they spin), additive glow
COINS = [dict(x=rng.uniform(0, W), y0=rng.uniform(-H, H), v=rng.uniform(380, 900), r=rng.uniform(10, 34), w=rng.uniform(3, 9), ph=rng.uniform(0, 6.3)) for _ in range(90)]
def coin_rain(f, t, density=1.0, start=0.0):
    layer = np.zeros((H, W, 3), np.float32); n = int(len(COINS) * density * 0.3)
    for c in COINS[:n]:
        y = (c["y0"] + c["v"] * (t - start)) % (H + 200) - 100; sx = abs(math.cos(c["w"] * t + c["ph"]))
        ax = (int(c["r"]), max(2, int(c["r"] * (0.15 + 0.85 * sx)))); bright = (0.55 + 0.45 * sx) * 0.7
        cv2.ellipse(layer, (int(c["x"]), int(y)), ax, (c["ph"] * 40) % 180, 0, 360, (0.25 * bright, 0.62 * bright, 1.0 * bright), -1, cv2.LINE_AA)
    blur = cv2.GaussianBlur(layer, (0, 0), 9) * 0.35
    mb = cv2.blur(layer, (1, 25))
    return f * (1 - np.clip(mb.max(2, keepdims=True), 0, 1) * 0.9) + mb * 0.95 + blur

MOTES = [dict(x=rng.uniform(0, W), y=rng.uniform(0, H), vx=rng.uniform(-14, 14), vy=rng.uniform(-22, -4), r=rng.uniform(1.2, 3.5), a=rng.uniform(0.2, 0.7)) for _ in range(140)]
def motes(f, t, col=(0.55, 0.78, 1.0), k=1.0):
    layer = np.zeros((H // 2, W // 2, 3), np.float32)
    for m in MOTES:
        x = (m["x"] + m["vx"] * t + 20 * math.sin(t * 0.7 + m["y"])) % W; y = (m["y"] + m["vy"] * t) % H
        cv2.circle(layer, (int(x / 2), int(y / 2)), max(1, int(m["r"] / 1.4)), tuple(c * m["a"] * k for c in col), -1, cv2.LINE_AA)
    layer = cv2.GaussianBlur(cv2.resize(layer, (W, H)), (0, 0), 2.2)
    return f + layer * 0.6

# ---------------- text ----------------
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

@functools.lru_cache(maxsize=128)
def text_rgba(lines, size, weight, style, cy, track=2, step=1.18):
    """returns (premultiplied BGR float, alpha float) full-frame layers"""
    lines = list(lines); mask = Image.new("L", (W, H), 0); d = ImageDraw.Draw(mask); f = cfont(size, weight)
    sp = int(size * step); y0 = cy - sp * (len(lines) - 1) / 2
    for li, ln in enumerate(lines):
        fonts = [RUPEE(size) if ch == "₹" else f for ch in ln]
        ws = [d.textlength(ch, font=fo) for ch, fo in zip(ln, fonts)]; tw = sum(ws) + track * (len(ln) - 1)
        asc, desc = f.getmetrics(); x = (W - tw) / 2; y = y0 + li * sp - (asc + desc) / 2
        for ch, wv, fo in zip(ln, ws, fonts):
            d.text((x, y + (size * 0.06 if fo is not f else 0)), ch, font=fo, fill=255); x += wv + track
    m = np.asarray(mask, np.float32) / 255.0
    bb = mask.getbbox() or (0, 0, W, H)
    shadow = cv2.GaussianBlur(cv2.dilate(m, np.ones((5, 5))), (0, 0), size * 0.14) * 0.85
    glow = cv2.GaussianBlur(m, (0, 0), size * 0.22) * 0.45
    if style == "gold":
        g = np.zeros((H, W, 3), np.float32); gg = gold_grad(bb[3] - bb[1] + 2)[:, ::-1] / 255.0
        g[bb[1]:bb[1] + len(gg)] = gg[: H - bb[1]][:, None, :]
        fill = g; glow_c = np.array([0.24, 0.62, 1.0], np.float32)
    elif style == "blood":
        fill = np.ones((H, W, 3), np.float32) * np.array([0.62, 0.70, 0.93], np.float32); glow_c = np.array([0.05, 0.08, 0.85], np.float32)
    elif style == "ice":
        fill = np.ones((H, W, 3), np.float32) * np.array([0.93, 0.93, 0.90], np.float32); glow_c = np.array([0.9, 0.75, 0.55], np.float32)
    else:
        fill = np.ones((H, W, 3), np.float32) * np.array([0.86, 0.94, 1.0], np.float32); glow_c = np.array([0.24, 0.62, 1.0], np.float32)
    edge = np.clip(np.roll(m, 2, 0) - m, 0, 1)[..., None]
    # composite into premultiplied colour + alpha
    a_sh = shadow[..., None]; col = np.zeros((H, W, 3), np.float32) + np.array([0.02, 0.04, 0.08], np.float32) * a_sh
    a = a_sh
    col = col * (1 - glow[..., None]) + glow_c * glow[..., None] * 0.9; a = a + glow[..., None] * (1 - a) * 0.6
    col = col * (1 - edge) + np.array([0.05, 0.2, 0.35], np.float32) * edge; a = np.maximum(a, edge)
    mm = m[..., None]; col = col * (1 - mm) + fill * mm; a = a * (1 - mm) + mm
    return col.astype(np.float32), np.clip(a, 0, 1).astype(np.float32)

def put_text(f, lines, t, t0, t1, size=92, weight=900, style="cream", cy=1240, pop=True, fade=0.12, track=2):
    if not (t0 <= t < t1): return f
    col, a = text_rgba(tuple(lines), size, weight, style, cy, track)
    k = min(1, (t - t0) / fade, (t1 - t) / fade)
    if pop:  # quick scale pop 1.08 -> 1.0
        s = 1 + 0.08 * max(0, 1 - (t - t0) / 0.18)
        if s > 1.001:
            M = cv2.getRotationMatrix2D((W / 2, cy), 0, s); col = cv2.warpAffine(col, M, (W, H)); a = cv2.warpAffine(a, M, (W, H))[..., None] if a.ndim == 3 else cv2.warpAffine(a, M, (W, H))
            if a.ndim == 2: a = a[..., None]
    return f * (1 - a * k) + col * k

_y, _x = np.mgrid[0:H, 0:W].astype(np.float32)
TAG_SH = (np.exp(-(((_x - W / 2) / 520) ** 2 + ((_y - 285) / 150) ** 2) * 1.6) * 0.55)[..., None]
def tag(f, t, alpha=1.0):
    f = f * (1 - TAG_SH * alpha)
    col, a = text_rgba(("PADMANABHASWAMY",), 60, 800, "gold", 250, 4)
    col2, a2 = text_rgba(("TEMPLE  ·  KERALA",), 34, 700, "gold", 326, 10)
    for c, aa in ((col, a), (col2, a2)): f = f * (1 - aa * alpha) + c * alpha
    y1, y2 = 192, 372
    for y in (y1, y2): f[y:y + 2, 230:850] = f[y:y + 2, 230:850] * (1 - 0.85 * alpha) + np.array([0.36, 0.70, 0.89], np.float32) * 0.85 * alpha
    return f

# ---------------- edit decision list ----------------
gap0 = st("then") - 0.45
COBRA = "Snake_charmer_in_Jaipur_Rajasthan"   # real footage (Commons, CC BY-SA 4.0)
EDL = [  # (t0, t1, kind, args, grade)
    (0.00, st("notopen") - 0.04, "photo", dict(name=f"{R}/footage/cobra/Indian_Cobra_Naja_naja_by_Dr_Raju_Kasambe_DSCN4991_2_.jpg", z=(2.3, 2.0), c0=(0.5, 0.36), c1=(0.5, 0.38), dark=0.78), "warm"),
    (st("notopen") - 0.04, st("six") - 0.08, "seq", dict(name="door_glimpse"), "warm"),
    (st("six") - 0.08, st("five") - 0.08, "photo", dict(name="Sree_Padmanabhaswamy_Temple_3.jpg", z=(1.05, 1.16), c0=(0.5, 0.40), c1=(0.5, 0.33)), "night"),
    (st("five") - 0.08, st("idols") - 0.06, "seq", dict(name="vaults", gain=0.78, contrast=1.25), "warm"),
    (st("idols") - 0.06, st("chain") - 0.06, "still", dict(name="gold_wide", z=(1.0, 1.10), c0=(0.5, 0.55), c1=(0.52, 0.5), coins=0.6), "warm"),
    (st("chain") - 0.06, st("sacks") - 0.06, "still", dict(name="gold_close", z=(1.05, 1.18), c0=(0.45, 0.55), c1=(0.55, 0.52), coins=0.5), "warm"),
    (st("sacks") - 0.06, st("diamonds") - 0.06, "still", dict(name="gold_low", z=(1.0, 1.1), c0=(0.5, 0.6), c1=(0.5, 0.55), coins=0.7), "warm"),
    (st("diamonds") - 0.06, st("crowns") - 0.06, "still", dict(name="gold_close", z=(1.5, 1.62), c0=(0.62, 0.52), c1=(0.6, 0.5), coins=0.4), "warm"),
    (st("crowns") - 0.06, st("lakh") - 0.12, "still", dict(name="gold_wide", z=(1.45, 1.55), c0=(0.62, 0.52), c1=(0.6, 0.5), coins=0.5), "warm"),
    (st("lakh") - 0.12, st("temple") - 0.12, "still", dict(name="gold_wide", z=(1.0, 1.22), c0=(0.5, 0.62), c1=(0.5, 0.5), coins=1.0), "warm"),
    (st("temple") - 0.12, gap0, "photo", dict(name="Sree_Padmanabhaswamy_Temple_2.jpg", z=(1.0, 1.1), c0=(0.5, 0.45), c1=(0.5, 0.36)), "warm"),
    (gap0, st("then"), "black", {}, None),
    (st("then"), st("handle") - 0.04, "seq", dict(name="door_reach"), "cold"),
    (st("handle") - 0.04, st("lock") - 0.04, "seq", dict(name="macro", zoom=1.0, off=0), "cold"),
    (st("lock") - 0.04, st("keyhole") - 0.04, "seq", dict(name="macro", zoom=1.3, off=30, cx=0.45, cy=0.55), "cold"),
    (st("keyhole") - 0.04, st("legend") - 0.08, "seq", dict(name="macro", zoom=1.65, off=60, cx=0.5, cy=0.45), "cold"),
    (st("legend") - 0.08, st("chant") - 0.08, "seq", dict(name="lamp"), "cold"),
    (st("chant") - 0.08, st("wrong") - 0.08, "seq", dict(name="door_reach", off=40, speed=0.5, zoom=1.12), "cold"),
    (st("wrong") - 0.08, en("wrong") + 0.35, "photo", dict(name=f"{R}/footage/cobra/Naja-naja-kobra-kopf.jpg", z=(1.3, 1.6), c0=(0.47, 0.38), c1=(0.47, 0.36), dark=0.7), "cold"),
    (en("wrong") + 0.35, st("weeks") - 0.06, "black", {}, None),
    (st("weeks") - 0.06, st("warning") - 0.08, "seq", dict(name="hand"), "cold"),
    (st("warning") - 0.08, st("never") - 0.08, "seq", dict(name="eyes", speed=0.65, zoom=1.4, cx=0.5, cy=0.2), "cold"),
    (st("never") - 0.08, en("never") + 0.45, "photo", dict(name="Sree_Padmanabhaswamy_Temple_night.jpg", z=(1.35, 1.12), c0=(0.42, 0.42), c1=(0.42, 0.45)), "cold"),
    (en("never") + 0.45, DUR + 1, "black", {}, None),
]
# subliminal 2-frame cobra flashes (horror), and the eye flash after "Would you?"
FLASH = [(st("notopen") + 0.55, "cobra"), (st("lock") + 0.42, "cobra"), (st("weeks") + 3.2, "cobra"), (en("would") + 0.25, "eyes")]

CAPS = [  # (lines, t0, t1, kw)
    (["THEY WERE WARNED"], st("warned"), st("notopen") - 0.04, dict(size=88)),
    (["NOT TO OPEN IT."], st("notopen"), st("six") - 0.08, dict(size=96)),
    (["6 SEALED VAULTS"], st("six"), st("five") - 0.08, dict(size=92, style="gold")),
    (["2011.", "THEY OPENED FIVE."], st("five"), st("idols") - 0.06, dict(size=92)),
    (["GOLD IDOLS"], st("idols"), st("chain") - 0.06, dict(size=96, style="gold", cy=1300)),
    (["AN 18-FOOT", "CHAIN OF SOLID GOLD"], st("chain"), st("sacks") - 0.06, dict(size=68, style="gold", cy=1300)),
    (["SACKS OF COINS"], st("sacks"), st("diamonds") - 0.06, dict(size=92, style="gold", cy=1300)),
    (["DIAMONDS"], st("diamonds"), st("crowns") - 0.06, dict(size=104, style="gold", cy=1300)),
    (["CROWNS"], st("crowns"), st("lakh") - 0.12, dict(size=104, style="gold", cy=1300)),
    (["OVER", "₹1 LAKH CRORE"], st("lakh"), st("temple") - 0.12, dict(size=104, style="gold", cy=1200)),
    (["One of the richest", "places on Earth."], st("temple") + 0.1, gap0 - 0.02, dict(size=62, weight=700, cy=1420, pop=False)),
    (["THEN THEY REACHED"], st("then"), st("handle") - 0.04, dict(size=78, style="ice", cy=1140)),
    (["VAULT B."], en("then") - 0.75, st("handle") - 0.04, dict(size=150, style="ice", cy=1290)),
    (["NO HANDLE."], st("handle"), st("legend") - 0.08, dict(size=92, style="ice", cy=1120, pop=True)),
    (["NO LOCK."], st("lock"), st("legend") - 0.08, dict(size=92, style="ice", cy=1240)),
    (["NO KEYHOLE."], st("keyhole"), st("legend") - 0.08, dict(size=92, style="ice", cy=1360)),
    (["Legend says it is sealed", "by a NAGA BANDHAM"], st("legend"), st("chant") - 0.08, dict(size=64, weight=700, style="ice", cy=1360, pop=False)),
    (["Only a perfect chant", "can break it."], st("chant"), st("wrong") - 0.08, dict(size=64, weight=700, style="ice", cy=1360, pop=False)),
    (["GET ONE WORD", "WRONG..."], st("wrong"), st("weeks") - 0.06, dict(size=100, style="blood", cy=1200)),
    (["Weeks after the vaults", "were opened, the man", "who fought to open them"], st("weeks"), st("weeks") + 3.3, dict(size=58, weight=700, style="ice", cy=1400, pop=False)),
    (["WAS DEAD."], st("weeks") + 3.3, st("warning") - 0.08, dict(size=120, style="blood", cy=1300)),
    (["Believers called it", "a warning."], st("warning"), st("never") - 0.08, dict(size=66, weight=700, style="ice", cy=1450, pop=False)),
    (["VAULT B HAS NEVER", "BEEN OPENED."], st("never"), en("never") + 0.45, dict(size=88, style="ice", cy=1250)),
    (["WOULD YOU?"], st("would") - 0.05, DUR + 1, dict(size=130, style="gold", cy=960)),
]
PUNCH = [st(k) for k in ["five", "idols", "chain", "sacks", "diamonds", "crowns", "lakh", "handle", "lock", "keyhole", "warning", "never"]] + [en("then") - 0.75, st("weeks") + 3.3]

def shot_frame(t):
    for t0, t1, kind, a, gmode in EDL:
        if t0 <= t < t1: break
    lt = t - t0; u = (t - t0) / max(1e-3, t1 - t0)
    if kind == "black": return np.zeros((H, W, 3), np.float32), None, u
    if kind == "photo":
        f = kb(photo(a["name"]), u, a["z"][0], a["z"][1], a["c0"], a["c1"]) * a.get("dark", 1.0)
    elif kind == "still":
        f = kb(still(f"{R}/cg/{a['name']}/f0000.jpg"), u, a["z"][0], a["z"][1], a["c0"], a["c1"])
        if a.get("coins"): f = coin_rain(f, t, a["coins"], t0)
    elif kind == "seq":
        f = seq(a["name"], a.get("off", 0) + lt * FPS * a.get("speed", 1.0))
        if a.get("zoom", 1.0) != 1.0 or "cx" in a: f = fit(f, a.get("zoom", 1.0) * (1 + 0.03 * u), a.get("cx", 0.5), a.get("cy", 0.5))
    elif kind == "video":
        v = vid(a["name"], a["off"] + lt * a.get("speed", 1.0))
        if v is None:  # Commons video blocked -> real cobra photo with a slow push, else my own eyes shot
            ph = sorted(glob.glob(f"{R}/footage/cobra/Indian_Cobra*.jpg"))
            v = still(ph[a.get("photo", 0) % len(ph)]) if ph else seq("eyes", 30)
        f = fit(v, a.get("zoom", 1.0) * (1 + 0.05 * u), a.get("cx", 0.5), a.get("cy", 0.5))
        if a.get("dark"): f = f * a["dark"]
    if "gain" in a: f = np.clip((f - 0.5) * a.get("contrast", 1.0) + 0.5, 0, 1) * a["gain"]
    amt = 1.0
    if gmode == "cold" and t < st("handle"): amt = np.clip((t - st("then")) / 1.2, 0, 1)
    if gmode: f = grade(f, gmode, t, amt)
    return f, gmode, u

def flash_frame(kind):
    if kind == "cobra":
        v = vid(COBRA, 6.0)
        if v is None:
            v = photo(f"{R}/footage/cobra/Indian_Cobra_Naja_naja_by_Dr_Raju_Kasambe_DSCN4991_16_.jpg")
        f = fit(v, 2.0, 0.43, 0.36); l = f.mean(2, keepdims=True); f = np.clip((l - 0.2) * 2.2, 0, 1) * np.array([0.35, 0.45, 1.0], np.float32)
        return f
    f = seq("eyes", 34); return grade(f, "cold", 0) * 1.2

def render(t, i):
    f, gmode, u = shot_frame(t)
    for ft, kind in FLASH:
        if ft <= t < ft + 2.0 / FPS: f = flash_frame(kind)
    # impact punch-in + micro shake
    for pt in PUNCH:
        if pt <= t < pt + 0.22:
            k = 1 - (t - pt) / 0.22; s = 1 + 0.045 * k
            M = cv2.getRotationMatrix2D((W / 2 + 6 * k * math.sin(t * 90), H / 2 + 6 * k * math.cos(t * 77)), 0, s); f = cv2.warpAffine(f, M, (W, H), borderMode=cv2.BORDER_REFLECT)
    if gmode in ("warm", "night"): f = motes(f, t, (0.45, 0.75, 1.0), 0.8)
    elif gmode == "cold": f = motes(f, t, (0.85, 0.85, 0.8), 0.5)
    # lamp-like exposure breathing
    if gmode: f = f * (1 + 0.025 * math.sin(t * 7.1) + 0.015 * math.sin(t * 17.3))
    f = f * VIG
    # tag: on from frame 0, dims on the black beats, gone for the final question
    tag_a = 1.0
    if t >= en("never") + 0.45: tag_a = max(0, 1 - (t - en("never") - 0.45) / 0.3)
    f = tag(f, t, tag_a)
    for lines, t0, t1, kw in CAPS:
        f = put_text(f, lines, t, t0, t1, **kw)
    f = grain(f, i)
    return np.clip(f, 0, 1)

def main():
    a = sys.argv[1:]; preview = "--preview" in a
    t_start, t_end = (float(a[a.index("--preview") + 1]), float(a[a.index("--preview") + 2])) if preview else (0, DUR)
    os.makedirs(f"{R}/output", exist_ok=True)
    out = a[a.index("--out") + 1] if "--out" in a else f"{R}/output/{'preview' if preview else 'vault-b-v3_silent'}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    n0, n1 = int(t_start * FPS), int(t_end * FPS)
    if "--frames" in a: n0, n1 = int(a[a.index("--frames") + 1]), min(int(DUR * FPS), int(a[a.index("--frames") + 2]))
    for i in range(n0, n1):
        f = render(i / FPS, i); p.stdin.write((f * 255 + 0.5).astype(np.uint8).tobytes())
        if i % 48 == 0: print("frame", i, "/", n1, flush=True)
    p.stdin.close(); p.wait(); print("wrote", out)

if __name__ == "__main__":
    main()
