#!/usr/bin/env python3
"""Sound for the 'love is a bridge' replica (14 s): soft pad, plank taps, phone blips, heart swell, low 'too far' drone, slump thud. Synthesized.  usage: audio_bridge.py OUT.wav"""
import sys, subprocess, wave
import numpy as np
SR = 44100; DUR = 14.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(9); out = np.zeros(N, np.float32)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
def note(f, dur, amp=1.0, dec=0.5):
    L = int(dur * SR); tt = np.arange(L) / SR; return ((np.sin(2 * np.pi * f * tt) + 0.3 * np.sin(4 * np.pi * f * tt) + 0.1 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt / dec) * amp).astype(np.float32)
# soft minor arpeggio (A minor) for the first 8 s, warm major after the hug
MIN = [220.0, 261.6, 329.6, 261.6]; MAJ = [261.6, 329.6, 392.0, 523.3]
k = 0; ts = 0.2
while ts < 8.0: add(note(MIN[k % 4], 1.6, 0.30, 0.7), ts, 1.0); ts += 0.5; k += 1
ts = 8.0; k = 0
while ts < 13.6: add(note(MAJ[k % 4], 2.0, 0.34, 0.9), ts, 1.0); ts += 0.5; k += 1
pad = np.zeros(N, np.float32)
for f, a in ((110.0, 1.0), (164.8, 0.6), (220.0, 0.5)): pad += a * np.sin(2 * np.pi * f * t)
out += pad * 0.05 * np.interp(t, [0, 2, 8, 9, 13, 14], [0.4, 0.6, 0.7, 0.2, 0.0, 0.0])
warm = np.zeros(N, np.float32)
for f, a in ((130.8, 1.0), (196.0, 0.7), (261.6, 0.6), (329.6, 0.5), (392.0, 0.3)): warm += a * np.sin(2 * np.pi * f * t)
out += warm * 0.07 * np.interp(t, [7.6, 8.4, 11.0, 14.0], [0, 1.0, 0.8, 0.0])
# plank taps (top: both builders every 0.583 s, bottom: slower)
TP = 7.0 / 12.0
for n in range(12):
    for off in (0.0, 0.07): 
        L = int(0.08 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * 760 * tt) * np.exp(-tt / 0.014) + bp(rng.randn(L).astype(np.float32), 800, 4000) * np.exp(-tt / 0.01) * 0.5).astype(np.float32), n * TP + 0.45 * TP + off, 0.35)
for n in range(10):
    L = int(0.08 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * 620 * tt) * np.exp(-tt / 0.016)).astype(np.float32), n * 0.9 + 0.45 * 0.9, 0.22)
# phone: blip when the glow starts, notification buzzes
for tb, f in ((0.55, 1320), (2.7, 1170), (5.2, 1170), (7.4, 1170)):
    L = int(0.25 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.07) * 0.5).astype(np.float32), tb, 0.35)
# heart: swell + two beats at 8.1
for i, tb in enumerate((8.1, 8.9, 9.7, 10.5)):
    for off, a in ((0.0, 1.0), (0.2, 0.6)):
        L = int(0.3 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (62 - 18 * tt / 0.3) * tt) * np.exp(-tt / 0.08) * a).astype(np.float32), tb + off, 0.5)
# 'too far' drone (cold) and the slump
dr = (np.sin(2 * np.pi * 55 * t) + np.sin(2 * np.pi * 58.3 * t)) * 0.08
out += dr * np.interp(t, [8.8, 9.4, 11.0, 12.5, 13.8], [0, 0.8, 1.0, 0.7, 0.0])
L = int(1.2 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (120 * np.exp(-tt * 2.4)) * tt) * np.exp(-tt / 0.35)).astype(np.float32), 10.9, 0.6)
# typed-text ticks
for tk in np.arange(0.5, 2.0, 0.11): 
    L = int(0.02 * SR); tt = np.arange(L) / SR; add(bp(rng.randn(L).astype(np.float32), 2000, 7000) * np.exp(-tt / 0.004), float(tk), 0.12)
for tk in np.arange(11.0, 13.4, 0.07):
    L = int(0.02 * SR); tt = np.arange(L) / SR; add(bp(rng.randn(L).astype(np.float32), 2000, 7000) * np.exp(-tt / 0.004), float(tk), 0.1)
out = np.tanh(out * 1.2) * 0.9
tmp = "/tmp/bridge_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afade=t=out:st=13.2:d=0.8,loudnorm=I=-15:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
