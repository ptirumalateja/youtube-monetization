"""Assemble The Salary Loop V3 (19.3 s = 579 frames at 30 fps).

  OUT=RENDER_DIR node render.cjs frames W 4 19.3 30      # four workers, W = 0..3
  python3 mix_v3.py RENDER_DIR/mix.wav
  python3 compose_v3.py RENDER_DIR OUT_DIR

Writes salary-loop-v3_music-ready.mp4 (silent) and salary-loop-v3.mp4 (master, -15 LUFS, true peak measured after AAC).
Short fades at the loop seam: the next-month buzz wraps from the last frames into frame 0.
"""
import os, sys, wave, subprocess
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import overlay_v3 as OV
from sld_sound import master_to_mp4, write_wav, SR

src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
FPS = OV.TL['fps']; TOTAL = round(OV.TL['duration'] * FPS)
silent = os.path.join(out, 'salary-loop-v3_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f in range(TOTAL):
    enc.stdin.write(OV.draw(Image.open(os.path.join(src, 'frames', f'f{f:05d}.jpg')).convert('RGB'), f / FPS).tobytes())
enc.stdin.close(); assert enc.wait() == 0; print('video ok', TOTAL, 'frames')
with wave.open(os.path.join(src, 'mix.wav')) as w:
    ch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate(); assert sw == 2 and sr == SR
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(np.float64) / 32768
y = x[:TOTAL * (SR // FPS)].copy(); xf = int(0.01 * SR); y[:xf] *= np.linspace(0, 1, xf)[:, None]; y[-xf:] *= np.linspace(1, 0, xf)[:, None]
wav = os.path.join(src, 'mix_v3.wav'); write_wav(y.T, wav)
lufs, peak = master_to_mp4(silent, wav, os.path.join(out, 'salary-loop-v3.mp4'))
print(f'master after AAC: {lufs} LUFS, true peak {peak} dBTP')
