#!/usr/bin/env python3
"""Place the ElevenLabs phrases (single Higgsfield take, Fraser) on the Time Flies reel's beats, duck the synthesised SFX under it, master, mux.
usage: python3 mix_dreams.py <vo_raw.wav 48k mono> <sfx.wav> <video.mp4> <out.mp4>
Phrase source times come from faster-whisper word timestamps on the one 40.4 s take; phrases are sped up 10-15 % (atempo, pitch kept) to fit 22 s."""
import sys, subprocess, numpy as np
from scipy import signal
from scipy.io import wavfile
vo_p, sfx_p, vid, out = sys.argv[1:5]
SR = 48000; DUR = 22.0; N = int(SR * DUR)
sr, vo = wavfile.read(vo_p); vo = vo.astype(np.float64) / (32768.0 if vo.dtype == np.int16 else 1.0); assert sr == SR
# (name, src_start, src_end, speed, place_at)
PH = [("where did the last three hours go", 0.00, 2.12, 1.0, 0.25), ("when youre absorbed you pay less attention to time", 2.96, 5.90, 1.0, 3.00), ("so in the moment it flies", 6.16, 7.84, 1.0, 6.30),
      ("but later your brain counts the memories it stored", 8.36, 11.20, 1.0, 8.35), ("more new moments more memories", 11.74, 13.76, 1.0, 11.60), ("so the same hours can feel longer looking back", 14.32, 17.28, 1.0, 14.00),
      ("same clock a different experience", 17.42, 19.38, 1.0, 17.25)]
def tempo(seg, sp):
    if abs(sp - 1) < 1e-3: return seg
    wavfile.write('/tmp/_seg_in.wav', SR, (seg * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', '/tmp/_seg_in.wav', '-af', f'atempo={sp}', '/tmp/_seg_out.wav'], check=True)
    r, o = wavfile.read('/tmp/_seg_out.wav'); return o.astype(np.float64) / 32768.0
voice = np.zeros(N)
for name, a, b, sp, t0 in PH:
    seg = vo[int(a * SR):int(min(b, len(vo) / SR) * SR)].copy(); f0 = int(0.02 * SR); seg[:f0] *= np.linspace(0, 1, f0); seg[-f0:] *= np.linspace(1, 0, f0); seg = tempo(seg, sp)
    f = int(0.03 * SR); seg[:f] *= np.linspace(0, 1, f); seg[-f:] *= np.linspace(1, 0, f)
    i0 = int(t0 * SR); n = min(len(seg), N - i0); voice[i0:i0 + n] += seg[:n]
    print(f'{name:40s} {t0:6.2f} -> {t0 + len(seg) / SR:6.2f}')
voice = signal.sosfilt(signal.butter(2, 70, 'high', fs=SR, output='sos'), voice)
pres = signal.sosfilt(signal.butter(2, [2500, 5000], 'band', fs=SR, output='sos'), voice); voice = voice + 0.25 * pres
a = np.abs(voice); thr = 0.18; voice = np.where(a > thr, np.sign(voice) * (thr + (a - thr) / 3.0), voice); voice *= 0.75 / max(np.abs(voice).max(), 1e-6)
sfx_sr, sfx = wavfile.read(sfx_p); assert sfx_sr == SR; sfx = sfx.astype(np.float64) / 32768.0
env = signal.sosfilt(signal.butter(2, 8, 'low', fs=SR, output='sos'), np.abs(voice)); env = np.clip(env / max(env.max(), 1e-6) * 2.2, 0, 1); duck = 1 - 0.55 * env
mix = np.stack([sfx[:N, 0] * duck * 0.85 + voice * 0.95, sfx[:N, 1] * duck * 0.85 + voice * 0.95], 1); mix *= 0.8 / max(np.abs(mix).max(), 1e-6)
wavfile.write('/tmp/_tf_mix.wav', SR, mix.astype(np.float32))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', '/tmp/_tf_mix.wav', '-filter_complex', '[1:a]loudnorm=I=-15:TP=-2.0:LRA=9,aresample=48000[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(DUR), '-movflags', '+faststart', out], check=True)
print('wrote', out)
