"""V5 = V4 cut with the pictogram hero (scene_dark.js V5 figure re-rendered into output/v3/frames). V4 assembly: splice the danger beat (night road at 100 km/h, rendered at scene time 22.0-24.2) in after the lifetime beat,
and cut the near-black pupil-to-brain gap. Frames and sound are both cut from the V3 source timeline, so nothing else re-renders.

  python3 build_v5.py            -> output/v5/ov/*.jpg, output/v5/mix.wav, output/silent5.mp4, output/final5.mp4

Source frames (30 fps) -> output order:
  0-377    hook .. lifetime (0.0-12.6 s)
  660-725  danger beat (scene 22.0-24.2 s)
  390-433  eye push (13.0-14.47 s, cut before the pupil goes black)
  450-659  brain .. mirror .. CTA .. lids close (15.0-22.0 s)
"""
import os, sys, wave
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import overlay
from overlay import tracked, win, W, CREAM, GOLD
from sld_sound import *
from mix import thup
FPS = 30
SEGS = [(0, 378), (660, 726), (390, 434), (450, 660)]
OUT = os.path.join(HERE, 'output')

def danger_text(L, t):
    """Text for the danger beat (scene time 22.0-24.2): the setup, then the number slams in as the lid reopens."""
    from PIL import ImageDraw
    d = ImageDraw.Draw(L)
    a = win(t, 22.05, 24.2, 0.1, 0.02)
    if a: tracked(d, 'AT 100 km/h,', 72, W / 2, 190, 4, CREAM + (int(255 * a),))
    a = win(t, 22.45, 24.2, 0.1, 0.02)
    if a: tracked(d, 'EVERY BLINK =', 72, W / 2, 280, 4, CREAM + (int(255 * a),))
    a = win(t, 23.3, 24.2, 0.04, 0.02)
    if a: tracked(d, '3 METRES BLIND.', 96, W / 2, 380, 4, GOLD + (int(255 * a),))

def apply(img, t):
    if t < 22.0: return overlay.apply(img, t)
    from PIL import Image as I, ImageFilter
    L = I.new('RGBA', img.size, (0, 0, 0, 0)); danger_text(L, t)
    sh = I.new('RGBA', img.size, (0, 0, 0, 0)); sh.putalpha(L.getchannel('A').point(lambda v: int(v * 0.75))); sh = sh.filter(ImageFilter.GaussianBlur(10))
    base = img.convert('RGBA'); base.alpha_composite(sh, (0, 6)); base.alpha_composite(L); return base.convert('RGB')

def frames():
    src = os.path.join(OUT, 'v3', 'frames'); dst = os.path.join(OUT, 'v5', 'ov'); os.makedirs(dst, exist_ok=True); os.makedirs(os.path.join(OUT, 'v5'), exist_ok=True); k = 0
    for a, b in SEGS:
        for f in range(a, b):
            apply(Image.open(os.path.join(src, f'f{f:05d}.jpg')), f / FPS).save(os.path.join(dst, f'f{k:05d}.jpg'), quality=94); k += 1
    print('frames', k, f'{k / FPS:.3f} s'); return k

def danger_audio():
    """2.2 s: engine and tyre roar, wind, the blink muffles everything for 0.22 s, a hit as the number lands."""
    D = 2.2; N = int(D * SR); t = np.arange(N) / SR; bus = new_buses(N); R = np.random.default_rng(5)
    eng = sum(a * np.sin(2 * np.pi * f * t + p) for f, a, p in [(46, 1.0, 0), (92, 0.55, 1), (138, 0.3, 2), (184, 0.15, 0.5)]) * (0.85 + 0.15 * np.sin(2 * np.pi * 7 * t))
    road = bp(noise(N), 700, 0.8) * 0.9 + hp(noise(N), 3500) * 0.18
    lid = np.clip(np.where(t < 1.1, 0, np.where(t < 1.16, (t - 1.1) / 0.06, np.where(t < 1.23, 1, 1 - (t - 1.23) / 0.09))), 0, 1)
    muff = lp(road, 400)
    body = (eng * 0.32 + road * (1 - lid) + muff * lid) * np.minimum(1, t / 0.05)
    bus['bed'] += np.stack([body * 0.9, body * 0.85])
    for k, tk in enumerate(np.arange(0.06, D, 0.432)): place(bus['fol'], thud(300 + k, 90, 0.05, 0.25), tk, 1.0, 0.3)   # a dash every 12 m at 27.8 m/s
    place(bus['fol'], thup(77, 1.0), 1.12, 1.0, 0.0)
    place(bus['hit'], thud(901, 44, 0.4, 1.2), 1.31, 1.0, 0.0); place(bus['hit'], sub_boom(1.0), 1.31, 0.8, 0.0)
    duck = np.ones(N); return finish(bus, duck)

def read_wav(p):
    with wave.open(p) as w: x = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float64) / 32767
    return x.reshape(-1, 2).T

def audio(nframes):
    src = read_wav(os.path.join(OUT, 'mix3.wav')); dng = danger_audio(); dng = dng / max(1e-9, np.abs(dng).max()) * np.abs(src).max() * 0.92
    xf = int(0.012 * SR); parts = []
    for a, b in SEGS:
        if a >= 660: parts.append(dng[:, :int((b - a) / FPS * SR)])
        else: parts.append(src[:, int(a / FPS * SR):int(b / FPS * SR)])
    out = parts[0]
    for p in parts[1:]:
        r = np.linspace(0, 1, xf); out[:, -xf:] = out[:, -xf:] * (1 - r) + p[:, :xf] * r; out = np.concatenate([out, p[:, xf:]], 1)
    n = int(nframes / FPS * SR); out = out[:, :n] if out.shape[1] >= n else np.pad(out, ((0, 0), (0, n - out.shape[1])))
    tb = int((378 + 66 + 44) / FPS * SR); th = thud(130, 60, 0.25, 0.5); out[:, tb:tb + len(th)] += th[None, :out.shape[1] - tb] * 0.5   # whoomp into the brain at the new cut
    write_wav(out / max(1.0, np.abs(out).max()), os.path.join(OUT, 'v5', 'mix.wav')); print('audio', out.shape[1] / SR)

if __name__ == '__main__':
    n = frames(); audio(n)
    os.system(f"ffmpeg -v error -y -framerate 30 -i {OUT}/v5/ov/f%05d.jpg -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -movflags +faststart {OUT}/silent5.mp4")
    print(master_to_mp4(f'{OUT}/silent5.mp4', f'{OUT}/v5/mix.wav', f'{OUT}/final5.mp4'))
