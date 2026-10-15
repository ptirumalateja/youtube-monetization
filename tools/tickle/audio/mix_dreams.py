#!/usr/bin/env python3
"""Place the ElevenLabs phrases (single Higgsfield take, Fraser) on the dreams reel's beats, duck the synthesised SFX under it, master, mux.
usage: python3 mix_dreams.py <vo_raw.wav 48k mono> <sfx.wav> <video.mp4> <out.mp4>
Phrase source times come from faster-whisper word timestamps on the one 40.4 s take; phrases are sped up 10-15 % (atempo, pitch kept) to fit 30 s."""
import sys, subprocess, numpy as np
from scipy import signal
from scipy.io import wavfile
vo_p, sfx_p, vid, out = sys.argv[1:5]
SR = 48000; DUR = 30.0; N = int(SR * DUR)
sr, vo = wavfile.read(vo_p); vo = vo.astype(np.float64) / (32768.0 if vo.dtype == np.int16 else 1.0); assert sr == SR
# (name, src_start, src_end, speed, place_at)
PH = [("you fall asleep", 0.00, 1.30, 1.0, 0.15), ("this is a dream", 2.12, 3.40, 1.0, 1.30), ("and it feels real", 3.34, 5.60, 1.15, 2.65), ("same brain different state", 6.45, 8.98, 1.1, 4.95),
      ("your logic centre switches off", 9.60, 11.60, 1.1, 7.30), ("no reality check no questions", 11.88, 14.12, 1.15, 9.25), ("impossible places feel believable", 14.88, 17.15, 1.15, 11.30),
      ("your body is locked", 18.05, 19.20, 1.15, 13.35), ("your mind isnt", 19.68, 21.18, 1.15, 14.55), ("the fear the joy the loss", 21.65, 24.30, 1.1, 16.00), ("all real", 24.80, 25.98, 1.1, 18.55),
      ("built from your memories", 26.65, 27.90, 1.1, 19.75), ("your brain weaves it all in real time", 28.45, 31.85, 1.15, 23.00), ("and sometimes you realise", 35.30, 37.75, 1.15, 26.05), ("you wake up", 38.35, 40.0, 1.15, 28.50)]
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
wavfile.write('/tmp/_dreams_mix.wav', SR, mix.astype(np.float32))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', '/tmp/_dreams_mix.wav', '-filter_complex', '[1:a]loudnorm=I=-15:TP=-2.0:LRA=9,aresample=48000[a]', '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-t', str(DUR), '-movflags', '+faststart', out], check=True)
print('wrote', out)
