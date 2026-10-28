"""V7 = V6 with the laptop + phone montage (scene 6.4-8.4 s) slowed to 0.8x so each counter value and screen lands (Meta AI note via Teja),
and the book pages blurred (scene_dark.js pageTex). The slowed frames are rendered at fractional scene times into output/v7/stretch
(render.cjs stills, t = 6.4 + k * 0.8 / 30, k = 0..74); the overlay follows scene time, so the counter slows with them.

  python3 build_v7.py            -> output/v7/ov/*.jpg, output/v7/mix.wav, output/silent7.mp4, output/final7.mp4
"""
import glob, os, sys
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from build_v4 import apply, FPS, OUT
from sld_sound import master_to_mp4
import mix_v7

def frames():
    src = os.path.join(OUT, 'v3', 'frames'); dst = os.path.join(OUT, 'v7', 'ov'); os.makedirs(dst, exist_ok=True)
    seq = [(os.path.join(src, f'f{f:05d}.jpg'), f / FPS) for f in range(0, 192)]
    st = sorted(glob.glob(os.path.join(OUT, 'v7', 'stretch', 'still-*.jpg'))); assert len(st) == 75, len(st)
    seq += [(p, 6.4 + k * 0.8 / 30) for k, p in enumerate(st)]
    for a, b in [(252, 378), (660, 726), (390, 434), (450, 660)]: seq += [(os.path.join(src, f'f{f:05d}.jpg'), f / FPS) for f in range(a, b)]
    for k, (p, t) in enumerate(seq): apply(Image.open(p), t).save(os.path.join(dst, f'f{k:05d}.jpg'), quality=94)
    print('frames', len(seq), f'{len(seq) / FPS:.3f} s'); return len(seq)

if __name__ == '__main__':
    n = frames(); mix_v7.main(f'{OUT}/v7/mix.wav')
    os.system(f"ffmpeg -v error -y -framerate 30 -i {OUT}/v7/ov/f%05d.jpg -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -movflags +faststart {OUT}/silent7.mp4")
    print(master_to_mp4(f'{OUT}/silent7.mp4', f'{OUT}/v7/mix.wav', f'{OUT}/final7.mp4'))
