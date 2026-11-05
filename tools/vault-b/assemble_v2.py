"""Vault B fact cut (v2): same renders, retimed (retime.py), fact text on every shot, mixed with audio/mix_v2.py.
python3 assemble_v2.py OUT.mp4 [WAV]
"""
import sys, os, subprocess
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import overlay as ov
import timeline_v2 as T

VAULT_LABELS = ['GOLD IDOLS', 'AN 18-FT GOLD CHAIN', 'SACKS OF COINS', 'GOLD CROWNS', 'DIAMONDS & RUBIES']
VAULT_STARTS = [3, 13, 22, 31, 40]


def label(im, text):
    f = ov.font(66, 800)
    return ov.text_layer(im, text, f, 1480, fill='gold', track=3, glow_r=18, glow_a=0.45, shadow=1.0)


def text_for(shot, i, n, im):
    s = i / max(1, n - 1)
    if shot == 'gold':
        im = ov.tag(im)
        if i >= 3: im = ov.big(im, ['2011.', 'THEY OPENED', 'THE VAULTS.'], cy=1120, size=92)
        if i >= 40: im = ov.small(im, ['Over 1 lakh crore rupees inside.'], cy=1420, size=54)
    elif shot == 'door':
        im = ov.tag(im)
        if i >= 9: im = ov.big(im, ['EXCEPT ONE.'], cy=1520, size=100)
    elif shot == 'gopuram':
        if i >= 6: im = ov.small(im, ['Padmanabhaswamy Temple, Kerala.', 'One of the richest temples on Earth.'], cy=1560, size=52)
    elif shot == 'vaults':
        raw = i * T.RAW['vaults'] / n
        cur = None
        for k, st in enumerate(VAULT_STARTS):
            if raw >= st + 2: cur = k
        if cur is not None: im = label(im, VAULT_LABELS[cur])
    elif shot == 'lamp':
        if i >= 5: im = ov.big(im, ['THEN THEY', 'REACHED', 'VAULT B.'], cy=720, size=92)
    elif shot == 'heads':
        if i >= 4: im = ov.big(im, ['NO HANDLE.', 'NO LOCK.', 'NO KEYHOLE.'], cy=1460, size=84)
    elif shot == 'seam':
        if i >= 4: im = ov.small(im, ['Legend says a "Naga Bandham"', 'seals it.'], cy=1300, size=56)
        if i >= 34: im = ov.small(im, ['Only a chant can open it.'], cy=1480, size=56)
    elif shot == 'hand':
        if i >= 3: im = ov.small(im, ['Weeks later, the man who asked', 'to open the vaults died.'], cy=1520, size=52)
        if i >= 44: im = ov.small(im, ['Believers called it a warning.'], cy=1680, size=52)
    elif shot == 'eyes':
        if i >= 6: im = ov.big(im, ['NO ONE HAS', 'OPENED IT SINCE.'], cy=1420, size=84)
        if i >= 46: im = ov.big(im, ['WOULD YOU?'], cy=1660, size=100)
    return im


def main():
    out = sys.argv[1]
    wav = sys.argv[2] if len(sys.argv) > 2 else os.path.join(T.HERE, 'output', 'anim', 'mix_v2.wav')
    comp = os.path.join(T.HERE, 'output', 'anim', 'comp_v2'); os.makedirs(comp, exist_ok=True)
    st, c = T.starts(); k = 0
    for shot in T.ORDER:
        n = c[shot]
        for i in range(n):
            im = Image.open(os.path.join(T.RT, shot, f'f{i:04d}.png')).convert('RGB').resize((ov.W, ov.H), Image.LANCZOS)
            text_for(shot, i, n, im).save(os.path.join(comp, f'c{k:04d}.jpg'), quality=94); k += 1
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-framerate', '24', '-i', os.path.join(comp, 'c%04d.jpg'),
                    '-i', wav, '-frames:v', str(k), '-c:v', 'libx264', '-profile:v', 'high', '-level', '4.1', '-preset', 'slow', '-crf', '18',
                    '-maxrate', '12M', '-bufsize', '24M', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', out], check=True)
    print('wrote', out, k, 'frames')


if __name__ == '__main__':
    main()
