#!/usr/bin/env python3
"""Sound for 'the plan' (14 s): ticking clock, drone, paper rustle, pin clicks, pencil scratch, whip whooshes, rising gold chimes, warm final chord. Synthesized.  usage: audio_plan.py OUT.wav"""
import sys, subprocess, wave
import numpy as np
SR = 44100; DUR = 14.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(5); out = np.zeros(N, np.float32)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
# drone bed
dr = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.5 * t + 0.6) + 0.3 * np.sin(2 * np.pi * 110 * t + 1.1)) * 0.2
out += dr * np.interp(t, [0, 3, 7, 10.6, 12.6, 14], [0.35, 0.5, 0.6, 0.8, 0.5, 0.0])
# clock ticks every 0.5 s (a hair louder on the beat)
for k in range(28):
    ts = 0.25 + k * 0.5; L = int(0.06 * SR); tt = np.arange(L) / SR
    add((bp(rng.randn(L).astype(np.float32), 1500, 5000) * np.exp(-tt / 0.008) * 0.9 + np.sin(2 * np.pi * 900 * tt) * np.exp(-tt / 0.012) * 0.3).astype(np.float32), ts, 0.22 if k % 2 == 0 else 0.15)
# pin clicks + paper snap
for tp in (0.62, 1.32, 2.02, 2.72, 7.05):
    L = int(0.12 * SR); tt = np.arange(L) / SR
    add((np.sin(2 * np.pi * 2100 * tt) * np.exp(-tt / 0.012) * 0.7 + bp(rng.randn(L).astype(np.float32), 2000, 8000) * np.exp(-tt / 0.02) * 0.6).astype(np.float32), tp, 0.55)
    L = int(0.25 * SR); tt = np.arange(L) / SR; add(bp(rng.randn(L).astype(np.float32), 800, 6000) * np.exp(-tt / 0.07) * 0.35, tp - 0.12, 0.5)
# paper crinkles while he crawls over the maps (3-6 s)
for k in range(10):
    ts = 3.2 + k * 0.27 + rng.uniform(-0.05, 0.05); L = int(0.2 * SR); tt = np.arange(L) / SR
    add(bp(rng.randn(L).astype(np.float32), 1500, 7000) * np.exp(-tt / 0.06) * (0.5 + 0.5 * rng.rand()), ts, 0.28)
# pencil scratch while he writes on the floor (7.6-10.6 s)
for k in range(24):
    ts = 7.75 + k * 0.12; L = int(0.1 * SR); tt = np.arange(L) / SR
    add(bp(rng.randn(L).astype(np.float32), 2500, 9000) * np.sin(np.pi * tt / 0.1) ** 2 * (0.6 + 0.4 * np.sin(k * 1.3) ** 2), ts, 0.16)
# whip whooshes on the cuts
for tc in (2.9, 5.9, 7.5, 10.5):
    L = int(0.55 * SR); tt = np.arange(L) / SR; w = bp(rng.randn(L).astype(np.float32), 300, 5000) * np.sin(np.pi * tt / 0.55) ** 2
    add(w * 0.9, tc, 0.5)
# thud on the closeup
L = int(0.7 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (70 * np.exp(-tt * 3)) * tt) * np.exp(-tt / 0.2)).astype(np.float32), 6.0, 0.7)
# gold route: rising chimes, one per segment, then a warm chord
for i, f in enumerate((523.3, 587.3, 659.3, 783.99, 1046.5)):
    ts = 10.9 + i * 0.38; L = int(1.4 * SR); tt = np.arange(L) / SR
    add(((np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt)) * np.exp(-tt / 0.6) * 0.5).astype(np.float32), ts, 0.38)
pad = np.zeros(N, np.float32)
for f, a in ((130.8, 1.0), (196.0, 0.7), (261.6, 0.6), (329.6, 0.5), (392.0, 0.4), (587.3, 0.25)):
    pad += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
out += pad * 0.06 * np.interp(t, [12.5, 13.1, 13.9, 14.0], [0, 1.0, 0.9, 0.0])
# boom as the hero turns to camera
L = int(1.4 * SR); tt = np.arange(L) / SR; add((np.tanh(np.sin(2 * np.pi * (84 * np.exp(-tt * 2.6)) * tt) * np.exp(-tt / 0.5) * 1.6)).astype(np.float32), 12.6, 0.8)
out = np.tanh(out * 1.1) * 0.9
tmp = "/tmp/plan_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afade=t=out:st=13.4:d=0.6,loudnorm=I=-14:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
