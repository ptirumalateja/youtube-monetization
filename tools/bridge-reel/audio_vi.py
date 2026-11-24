#!/usr/bin/env python3
"""SFX only for the 21 s gamer-timeline reel. usage: audio_vi.py OUT.wav"""
import sys, subprocess, wave
import numpy as np
SR = 44100; DUR = 21.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(41); out = np.zeros(N, np.float32)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
def noise(L): return rng.randn(L).astype(np.float32)
def tone(f, d, dec, amp=1.0, harm=0.3):
    L = int(d * SR); tt = np.arange(L) / SR; return ((np.sin(2 * np.pi * f * tt) + harm * np.sin(4 * np.pi * f * tt)) * np.exp(-tt / dec) * amp).astype(np.float32)
def tick(a=1.0):
    L = int(0.02 * SR); tt = np.arange(L) / SR; return (bp(noise(L), 2000, 8000) * np.exp(-tt / 0.004)).astype(np.float32) * a
def whoosh(t0, d=0.35, a=0.3):
    L = int(d * SR); tt = np.arange(L) / SR; add(bp(noise(L), 400, 6000) * np.sin(np.pi * tt / d) ** 2, t0, a)
out += bp(noise(N), 50, 260) * 0.014
for c in (1.6, 3.4, 6.2, 8.0, 11.5, 13.2, 16.5): whoosh(c - 0.12)
# controller clicks (button mashing) through the scenes
for a, b, r in ((0.3, 1.6, 0.18), (2.0, 3.3, 0.14), (3.6, 6.1, 0.2), (6.4, 7.9, 0.2), (8.2, 11.4, 0.15), (11.7, 13.1, 0.4)):
    for x in np.arange(a, b, r): add(tick(1.0), float(x + rng.uniform(0, 0.05)), 0.14)
# paper rustle (cheat sheet)
for k in range(6): L = int(0.22 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 1500, 7000) * np.exp(-tt / 0.06), 1.7 + k * 0.28, 0.18)
# CRT power-on + hum, retro game beeps
L = int(0.8 * SR); tt = np.arange(L) / SR; add(np.sin(2 * np.pi * (200 + 9000 * (tt / 0.8) ** 3) * tt).astype(np.float32) * np.exp(-tt / 0.5), 3.45, 0.14)
out += (np.sin(2 * np.pi * 15734 / 4 * t) * 0.0 + np.sin(2 * np.pi * 120 * t) * 0.02).astype(np.float32) * np.interp(t, [3.4, 3.6, 6.1, 6.3], [0, 1, 1, 0])
for x in np.arange(4.0, 6.1, 0.55): add(tone(520, 0.1, 0.05, 0.6, 0.0), float(x), 0.12); add(tone(780, 0.1, 0.05, 0.6, 0.0), float(x) + 0.12, 0.1)
# 2013: car engine + tyre hiss (rising and falling revs)
rev = 90 + 70 * np.sin(2 * np.pi * 0.4 * t); ph = 2 * np.pi * np.cumsum(rev) / SR
eng = (np.sign(np.sin(ph)) * 0.5 + np.sin(ph * 2) * 0.3).astype(np.float32); eng = bp(eng, 70, 900)
out += eng * np.interp(t, [8.0, 8.3, 11.3, 11.6], [0, 0.09, 0.09, 0]); out += bp(noise(N), 800, 4000) * np.interp(t, [8.0, 8.4, 11.3, 11.6], [0, 0.03, 0.03, 0])
# gasps at the wow moments
def gasp(t0, a=0.3):
    L = int(0.45 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 500, 3500) * np.sin(np.pi * np.minimum(tt / 0.45, 1)) ** 1.5, t0, a)
gasp(0.2, 0.25); gasp(6.3, 0.25); gasp(11.6, 0.3); gasp(13.3, 0.2)
# the reveal: rising swell, boom, sparkle, warm chord
L = int(1.6 * SR); tt = np.arange(L) / SR; add(np.sin(2 * np.pi * (180 + 1600 * (tt / 1.6) ** 2) * tt).astype(np.float32) * (tt / 1.6) ** 1.4, 13.0, 0.28)
L = int(1.4 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (70 * np.exp(-tt * 2.5)) * tt) * np.exp(-tt / 0.5)).astype(np.float32), 14.1, 0.75)
for k, f in enumerate((1318, 1568, 1976, 2637, 3136)): add(tone(f, 0.8, 0.3, 0.6), 14.15 + k * 0.1, 0.16)
pad = np.zeros(N, np.float32)
for f, a in ((130.8, 1.0), (196.0, 0.7), (261.6, 0.6), (329.6, 0.5), (392.0, 0.4)): pad += a * np.sin(2 * np.pi * f * t)
out += pad * 0.05 * np.interp(t, [14.1, 15.2, 16.4, 17.2], [0, 1, 1, 0])
# laughing: rhythmic voiced bursts, then sniff and a tear wipe
def ha(t0, f0, a=0.3):
    L = int(0.16 * SR); tt = np.arange(L) / SR; v = np.sin(2 * np.pi * (f0 - 30 * tt / 0.16) * tt + 4 * np.sin(2 * np.pi * 30 * tt)); v = v + 0.5 * np.sin(4 * np.pi * f0 * tt)
    add(((bp((v + noise(L) * 0.4).astype(np.float32), 200, 2600)) * np.sin(np.pi * tt / 0.16) ** 1.2), t0, a)
x = 16.9
while x < 20.5: ha(x, 170 + 40 * rng.rand(), 0.22 + 0.1 * rng.rand()); x += 0.21 + 0.05 * rng.rand()
L = int(0.4 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 600, 3500) * np.sin(np.pi * tt / 0.4) ** 2, 19.15, 0.2)
out = np.tanh(out * 1.2) * 0.9
tmp = "/tmp/vi_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afade=t=out:st=20.3:d=0.7,loudnorm=I=-15:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
