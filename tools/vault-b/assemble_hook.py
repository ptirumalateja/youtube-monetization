"""Assemble the 5 s Vault B hook test: gold frames (0-2.5 s) hard-cut to door frames (2.5-5 s),
upscaled to 1080x1920, overlays timed per beat, muxed with audio/hook.wav.
python3 assemble_hook.py ANIM_DIR OUT.mp4
"""
import sys, os, subprocess
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlay as ov

FPS = 24
HIT_FRAME = 9   # door line lands with the hit (2.85 s = 0.35 s into the door shot)


def main():
    anim, out = sys.argv[1], sys.argv[2]
    tmp = os.path.join(anim, 'comp'); os.makedirs(tmp, exist_ok=True)
    gold = sorted(f for f in os.listdir(os.path.join(anim, 'gold')) if f.endswith('.png'))
    door = sorted(f for f in os.listdir(os.path.join(anim, 'door')) if f.endswith('.png'))
    n = 0
    for i, f in enumerate(gold):
        im = Image.open(os.path.join(anim, 'gold', f)).convert('RGB').resize((ov.W, ov.H), Image.LANCZOS)
        im = ov.tag(im)
        if i >= 6:  # line in after a quarter second of pure gold
            im = ov.big(im, ['THEY OPENED', 'FIVE DOORS.'])
        im.save(os.path.join(tmp, f'c{n:04d}.jpg'), quality=94); n += 1
    for i, f in enumerate(door):
        im = Image.open(os.path.join(anim, 'door', f)).convert('RGB').resize((ov.W, ov.H), Image.LANCZOS)
        im = ov.tag(im)
        if i >= HIT_FRAME:
            im = ov.big(im, ['THIS ONE,', 'THEY LEFT SHUT.'], cy=1520, size=84)
        im.save(os.path.join(tmp, f'c{n:04d}.jpg'), quality=94); n += 1
    wav = os.path.join(anim, 'hook.wav')
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(tmp, 'c%04d.jpg'),
                    '-i', wav, '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out, n, 'frames')


if __name__ == '__main__':
    main()
