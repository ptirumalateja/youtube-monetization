"""V4 assembly (built on V2): a 0.8 s title card (HOW NORMAL PEOPLE SLEEP / vs / ME) that swipes into the bedroom, then every scene frame
through overlay.compose, silent mp4, mux with output/mix4.wav.

  python3 build_v4.py            (scene frames in output/v4/frames, 609 of them)
"""
import os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import overlay
from overlay import W, H, font, tracked, sstep
OUT = os.path.join(HERE, 'output', 'v4'); FR = os.path.join(OUT, 'frames'); CP = os.path.join(OUT, 'comp'); os.makedirs(CP, exist_ok=True)
NT, NS = 24, 609; WIPE0 = 17
ORANGE = (255, 150, 64); CREAM = (235, 228, 214)
def sm5(u): u = min(1.0, max(0.0, u)); return u * u * u * (u * (u * 6 - 15) + 10)
def title(t):
    bg = Image.new('RGB', (W, H), (9, 9, 12)); L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    a = sstep(0.0, 0.15, t); tracked(d, 'HOW NORMAL PEOPLE SLEEP', 50, W / 2, 690, 8, CREAM + (int(235 * a),), 'Light')
    a = sstep(0.1, 0.25, t); tracked(d, 'vs', 46, W / 2, 790, 4, ORANGE + (int(255 * a),), 'Medium')
    u = t - 0.22
    if u > 0:
        sc = 0.4 + 0.72 * sm5(u / 0.18) if u < 0.18 else (1.12 - 0.12 * sm5((u - 0.18) / 0.1) if u < 0.28 else 1.0); rot = 2.6 * math.sin(u * 28) * math.exp(-u * 3.2)
        me = Image.new('RGBA', (900, 520), (0, 0, 0, 0)); md = ImageDraw.Draw(me); tracked(md, 'ME', 400, 450, 40, 6, ORANGE + (255,), 'ExtraBold')
        gl = me.filter(ImageFilter.GaussianBlur(26)); me.alpha_composite(gl, (0, 0)) if False else None
        me2 = me.resize((int(900 * sc), int(520 * sc)), Image.LANCZOS).rotate(rot, resample=Image.BICUBIC, expand=True); gl2 = me2.filter(ImageFilter.GaussianBlur(30))
        cx, cy = W // 2, 1060
        for im, al in ((gl2, 0.8), (me2, 1.0)):
            im = im.copy(); im.putalpha(im.split()[3].point(lambda v: int(v * al))); L.alpha_composite(im, (cx - im.width // 2, cy - im.height // 2))
    out = bg.convert('RGBA'); out.alpha_composite(L); return out.convert('RGB')
def comp(i): return overlay.compose(Image.open(os.path.join(FR, f'f{i:05d}.jpg')), i / 30)
B0 = np.asarray(comp(0)).astype(np.float32)
n = 0
def save(im):
    global n; im.save(os.path.join(CP, f'f{n:05d}.jpg'), quality=93); n += 1
for k in range(NT):
    t = k / 30; A = np.asarray(title(t)).astype(np.float32)
    if k < WIPE0: save(Image.fromarray(A.astype(np.uint8))); continue
    p = sm5((k - WIPE0 + 1) / (NT - WIPE0 + 1)); strip = np.concatenate([A, B0], axis=1); acc = np.zeros_like(A)
    for j in range(-4, 5):
        x = int(round(min(1.0, max(0.0, p + j * 0.012)) * W)); acc += strip[:, x:x + W]
    save(Image.fromarray((acc / 9).clip(0, 255).astype(np.uint8)))
for i in range(NS): save(comp(i))
print('composed', n)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '30', '-i', os.path.join(CP, 'f%05d.jpg'), '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', os.path.join(OUT, 'silent.mp4')], check=True)
import sld_sound as S
print(S.master_to_mp4(os.path.join(OUT, 'silent.mp4'), os.path.join(HERE, 'output', 'mix4.wav'), os.path.join(OUT, 'normal-people-vs-me-sleep.mp4')))
