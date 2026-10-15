#!/usr/bin/env python3
"""Place the ElevenLabs voice phrases on the cut's beats, duck the synthesised SFX under the voice, master to about -15 LUFS, mux with the video.
usage: python3 mix_tickle.py <vo_raw.wav (48k mono)> <sfx.wav> <video.mp4> <out.mp4>
Phrase boundaries come from silencedetect on the single Higgsfield/ElevenLabs take (see PH below)."""
import sys, subprocess, numpy as np
from scipy import signal
from scipy.io import wavfile
vo_p, sfx_p, vid, out = sys.argv[1:5]
SR = 48000; DUR = 23.2; N = int(SR * DUR)
sr, vo = wavfile.read(vo_p); vo = vo.astype(np.float64) / (32768.0 if vo.dtype == np.int16 else 1.0)
assert sr == SR
# (name, src_start, src_end, place_at)  -- places chosen to the beats of cut v3
PH = [("you cant tickle yourself", 0.00, 1.64, 0.45), ("your brain cheats", 3.08, 4.37, 2.30), ("before you touch", 5.84, 6.97, 4.35), ("it predicts the touch", 7.30, 8.68, 5.65),
      ("the command goes out", 9.44, 10.70, 8.95), ("the prediction arrives first", 11.14, 12.72, 10.40), ("predicted touch", 13.62, 14.66, 12.80), ("dampened", 15.58, 16.10, 13.95),
      ("someone else", 17.56, 18.38, 14.50), ("no prediction", 19.19, 19.97, 15.80), ("thats why it tickles", 20.78, 21.95, 18.30), ("but you cant make it a surprise", 22.60, 24.48, 20.50)]
voice = np.zeros(N)
for name, a, b, t0 in PH:
    seg = vo[int(a * SR):int(b * SR)].copy(); f = int(0.025 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    i0 = int(t0 * SR); n = min(len(seg), N - i0); voice[i0:i0 + n] += seg[:n]
# voice chain: gentle high-pass, presence lift, compression, level
voice = signal.sosfilt(signal.butter(2, 70, 'high', fs=SR, output='sos'), voice)
pres = signal.sosfilt(signal.butter(2, [2500, 5000], 'band', fs=SR, output='sos'), voice); voice = voice + 0.25 * pres
a = np.abs(voice); thr = 0.18; voice = np.where(a > thr, np.sign(voice) * (thr + (a - thr) / 3.0), voice)
voice *= 0.75 / max(np.abs(voice).max(), 1e-6)
sfx_sr, sfx = wavfile.read(sfx_p); assert sfx_sr == SR; sfx = sfx.astype(np.float64)
env = signal.sosfilt(signal.butter(2, 8, 'low', fs=SR, output='sos'), np.abs(voice)); env = np.clip(env / max(env.max(), 1e-6) * 2.2, 0, 1)
duck = 1 - 0.5 * env                       # SFX dips ~6 dB under speech
mix = np.stack([sfx[:N, 0] * duck * 0.85 + voice * 0.95, sfx[:N, 1] * duck * 0.85 + voice * 0.95], 1)
mix *= 0.8 / max(np.abs(mix).max(), 1e-6)
wavfile.write('/tmp/_tickle_mix.wav', SR, mix.astype(np.float32))
# master: -15 LUFS integrated, true peak <= -1.5 dB, then AAC mux; peak is re-measured after AAC (playbook 4.3)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', '/tmp/_tickle_mix.wav', '-filter_complex', '[1:a]loudnorm=I=-15:TP=-2.0:LRA=9,aresample=48000[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(DUR), '-movflags', '+faststart', out], check=True)
print('wrote', out)
