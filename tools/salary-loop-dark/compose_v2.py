"""Assemble The Salary Loop V2 from a hard-cut render of ../salary-loop-warm.

  (cd ../salary-loop-warm && XF=0 OUT=RENDER_DIR node render.cjs frames W N 20 30)   # four workers, W = 0..3, N = 4
  (cd ../salary-loop-warm && python3 mix.py RENDER_DIR/mix.wav)
  python3 compose_v2.py RENDER_DIR OUT_DIR

Writes salary-loop-v2.mp4 (master, -15 LUFS) and salary-loop-v2_music-ready.mp4 (silent). The sound is the V1 mix cut on the same
frame boundaries as the picture, with 10 ms crossfades at every join and short fades at the loop seam.
"""
import os, sys, wave
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import subprocess
import overlay_v2 as OV
from sld_sound import master_to_mp4, write_wav, SR

src, out = sys.argv[1], sys.argv[2]; os.makedirs(out, exist_ok=True)
silent = os.path.join(out, 'salary-loop-v2_music-ready.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '1080x1920', '-r', str(OV.FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'slow', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', silent], stdin=subprocess.PIPE)
for f, s in enumerate(OV.MAP):
    enc.stdin.write(OV.draw(Image.open(os.path.join(src, 'frames', f'f{s:05d}.jpg')).convert('RGB'), f).tobytes())
enc.stdin.close(); assert enc.wait() == 0; print('video ok', OV.TOTAL, 'frames')

with wave.open(os.path.join(src, 'mix.wav')) as w:
    ch, sw, sr = w.getnchannels(), w.getsampwidth(), w.getframerate(); assert sw == 2 and sr == SR
    x = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, ch).astype(np.float64) / 32768
spf = SR // OV.FPS; xf = int(0.01 * SR); segs = OV.ED['segments']; r = np.linspace(0, 1, xf)[:, None]
y = x[segs[0][0] * spf:segs[0][1] * spf].copy(); pb = segs[0][1]
for a, b in segs[1:]:                                   # crossfade: the outgoing segment runs on for xf samples past its cut while the next fades in
    seg = x[a * spf:b * spf].copy(); seg[:xf] = seg[:xf] * r + x[pb * spf:pb * spf + xf] * (1 - r); y = np.concatenate([y, seg]); pb = b
y[:xf] *= r; y[-xf:] *= 1 - r                          # the loop seam: both ends sit on the next-month bell
assert len(y) == OV.TOTAL * spf, (len(y), OV.TOTAL * spf)
wav = os.path.join(src, 'mix_v2.wav'); write_wav(y.T, wav)
lufs, peak = master_to_mp4(silent, wav, os.path.join(out, 'salary-loop-v2.mp4'))
print(f'master after AAC: {lufs} LUFS, true peak {peak} dBTP')
