"""Assemble Vault B 0-10 s: hook comp frames (from assemble_hook.py) + gopuram (5-7.5 s) + vault corridor (7.5-10 s),
muxed with audio/block2.py output. python3 assemble_b2.py ANIM_DIR OUT.mp4
"""
import sys, os, subprocess
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlay as ov

FPS = 24
TEXT_IN = 6          # lock-in line lands a quarter second after the cut


def main():
    anim, out = sys.argv[1], sys.argv[2]
    comp = os.path.join(anim, 'comp'); n = len([f for f in os.listdir(comp) if f.startswith('c')])
    assert n == 120, 'run assemble_hook.py first'
    for i, f in enumerate(sorted(os.listdir(os.path.join(anim, 'gopuram')))):
        im = Image.open(os.path.join(anim, 'gopuram', f)).convert('RGB').resize((ov.W, ov.H), Image.LANCZOS)
        if i >= TEXT_IN:
            im = ov.small(im, ['Beneath Padmanabhaswamy.', "India's richest room."], cy=1560, size=56)
        im.save(os.path.join(comp, f'c{n:04d}.jpg'), quality=94); n += 1
    for f in sorted(os.listdir(os.path.join(anim, 'vaults'))):
        im = Image.open(os.path.join(anim, 'vaults', f)).convert('RGB').resize((ov.W, ov.H), Image.LANCZOS)
        im.save(os.path.join(comp, f'c{n:04d}.jpg'), quality=94); n += 1
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(comp, 'c%04d.jpg'),
                    '-i', os.path.join(anim, 'block2.wav'), '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out, n, 'frames')


if __name__ == '__main__':
    main()
