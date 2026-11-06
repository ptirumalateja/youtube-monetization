"""Slow Light regional brand kit: redraws Teja's mark (ringed planet with a light streak) at any size and adds the
channel name in Telugu / Hindi. python3 slowlight_regional.py OUTDIR -> logo + YouTube banner + Facebook cover per language."""
import os, sys, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vault-b", "fonts")
LANGS = {
    "telugu": dict(name="స్లో లైట్", tag="ఆగి వినాల్సిన కథలు", font="indic/NotoSerif-telugu-800.ttf"),
    "hindi": dict(name="स्लो लाइट", tag="रुककर सुनने लायक कहानियाँ", font="indic/NotoSerif-devanagari-800.ttf"),
}
CREAM, ORANGE = (232, 228, 220), (255, 178, 80)

def background(w, h, cx, cy, r):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32); d = np.clip(np.hypot(x - cx, y - cy) / r, 0, 1) ** 1.2
    c0, c1 = np.array([38, 45, 62], np.float32), np.array([8, 12, 22], np.float32)
    return Image.fromarray((c0 * (1 - d[..., None]) + c1 * d[..., None]).astype(np.uint8))

def mark(size):
    """the mark on a transparent square canvas, drawn 4x and downsampled. Geometry measured from the 600 px original."""
    S = size * 4; k = S / 600.0; im = Image.new("RGBA", (S, S), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    cx, cy, r = 300 * k, 295 * k, 148 * k
    disc = Image.new("RGBA", (S, S), (0, 0, 0, 0)); dd = ImageDraw.Draw(disc)
    dd.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(60, 68, 88, 90)); im.alpha_composite(disc)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CREAM + (255,), width=int(7 * k))
    pts = [(68, 242), (152, 266), (445, 287), (540, 320)]
    for off, a, wd in ((22, 40, 16), (11, 80, 16), (-11, 80, 16), (-22, 40, 16)):   # the faded light trail
        layer = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(layer).line([(x * k, (y + off) * k) for x, y in pts], fill=(150, 110, 60, a), width=int(wd * k), joint="curve")
        im.alpha_composite(layer)
    glow = Image.new("RGBA", (S, S), (0, 0, 0, 0)); ImageDraw.Draw(glow).line([(x * k, y * k) for x, y in pts], fill=ORANGE + (120,), width=int(30 * k), joint="curve")
    im.alpha_composite(glow.filter(ImageFilter.GaussianBlur(10 * k)))
    d.line([(x * k, y * k) for x, y in pts], fill=ORANGE + (255,), width=int(15 * k), joint="curve")
    return im.resize((size, size), Image.LANCZOS)

def text(d, xy, s, font, fill, anchor="mm"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)

def cinzel(size):
    f = ImageFont.truetype(os.path.join(F, "Cinzel.ttf"), size)
    try: f.set_variation_by_axes([700])
    except Exception: pass
    return f

for lang, L in LANGS.items():
    fnt = lambda s: ImageFont.truetype(os.path.join(F, L["font"]), s)
    # 1) profile logo 2048 (YouTube 800x800, Instagram, Facebook all crop to a circle): mark up top, name below, inside the circle
    N = 2048; im = background(N, N, N / 2, N * 0.45, N * 0.75).convert("RGBA")
    m = mark(int(N * 0.86)); im.alpha_composite(m, (int(N * 0.07), int(N * 0.0)))
    d = ImageDraw.Draw(im); text(d, (N / 2, N * 0.80), L["name"], fnt(int(N * 0.115)), CREAM)
    im.convert("RGB").save(f"{OUT}/slowlight-{lang}_logo.png")
    # mark-only logo (cleanest at tiny sizes), with a small script badge
    im = background(N, N, N / 2, N / 2, N * 0.75).convert("RGBA"); im.alpha_composite(mark(N)); im.convert("RGB").save(f"{OUT}/slowlight-{lang}_logo-mark.png")
    # 2) YouTube banner 2560x1440, everything inside the 1546x423 centre safe area
    Wb, Hb = 2560, 1440; im = background(Wb, Hb, Wb / 2, Hb / 2, Wb * 0.55).convert("RGBA")
    ms = 520; im.alpha_composite(mark(ms), (int(Wb / 2 - 530), int(Hb / 2 - ms / 2)))
    d = ImageDraw.Draw(im); x0 = Wb / 2 - 10
    text(d, (x0, Hb / 2 - 55), L["name"], fnt(150), CREAM, "lm")
    text(d, (x0 + 4, Hb / 2 + 70), L["tag"], fnt(62), ORANGE, "lm")
    text(d, (x0 + 6, Hb / 2 + 150), "SLOW LIGHT", cinzel(40), (150, 150, 160), "lm")
    im.convert("RGB").save(f"{OUT}/slowlight-{lang}_youtube-banner.png")
    # 3) Facebook cover 1640x624 (mobile crops the sides, so content sits in the middle ~1200 px; profile photo covers bottom-left)
    Wf, Hf = 1640, 624; im = background(Wf, Hf, Wf / 2, Hf / 2, Wf * 0.6).convert("RGBA")
    ms = 380; im.alpha_composite(mark(ms), (int(Wf / 2 - 430), int(Hf / 2 - ms / 2 - 10)))
    d = ImageDraw.Draw(im); x0 = Wf / 2 - 60
    text(d, (x0, Hf / 2 - 50), L["name"], fnt(118), CREAM, "lm")
    text(d, (x0 + 4, Hf / 2 + 50), L["tag"], fnt(48), ORANGE, "lm")
    text(d, (x0 + 6, Hf / 2 + 115), "SLOW LIGHT", cinzel(30), (150, 150, 160), "lm")
    im.convert("RGB").save(f"{OUT}/slowlight-{lang}_facebook-cover.png")
print("ok", sorted(os.listdir(OUT)))
