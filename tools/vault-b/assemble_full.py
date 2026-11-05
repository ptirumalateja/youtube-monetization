"""Assemble the full 20 s Vault B reel: comp frames 0-10 s (assemble_hook.py + assemble_b2.py) + blocks 3-4
from door.py shots, timed text, muxed with audio/full.py. python3 assemble_full.py ANIM_DIR OUT.mp4
"""
import sys, os, subprocess
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlay as ov

FPS = 24
# shot, frames, overlay(frame index in shot) -> image
SHOTS = [
    ('lamp', 36, lambda im, i: ov.big(im, ['THEN THEY', 'REACHED B.'], cy=1240) if i >= 5 else im),
    ('heads', 42, lambda im, i: ov.small(im, ['No handle.', 'No lock.'], cy=1480, size=62) if i >= 4 else im),
    ('seam', 42, lambda im, i: ov.small(im, ['They say only a chant', 'can open it.'], cy=1420, size=58) if i >= 4 else im),
    ('hand', 42, lambda im, i: im),
    ('eyes', 78, lambda im, i: ov.small(ov.big(im, ['STILL SHUT.'], cy=1460, size=104), ['Would you open it?'], cy=1610, size=58) if i >= 36
                              else (ov.big(im, ['STILL SHUT.'], cy=1460, size=104) if i >= 10 else im)),
]


def main():
    anim, out = sys.argv[1], sys.argv[2]
    comp = os.path.join(anim, 'comp')
    n = 240
    assert len([f for f in os.listdir(comp) if f.startswith('c')]) >= 240, 'run assemble_hook.py and assemble_b2.py first'
    for shot, cnt, fn in SHOTS:
        for i in range(cnt):
            im = Image.open(os.path.join(anim, shot, f'f{i:04d}.png')).convert('RGB').resize((ov.W, ov.H), Image.LANCZOS)
            fn(im, i).save(os.path.join(comp, f'c{n:04d}.jpg'), quality=94); n += 1
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(comp, 'c%04d.jpg'),
                    '-i', os.path.join(anim, 'full.wav'), '-frames:v', str(n), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out, n, 'frames')


if __name__ == '__main__':
    main()
