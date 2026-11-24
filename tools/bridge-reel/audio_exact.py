#!/usr/bin/env python3
"""SFX only for 'what success looks like' (15 s). usage: audio_success.py OUT.wav"""
import sys, subprocess, wave, math
import numpy as np
sys.path.insert(0, "/home/user/youtube-monetization/tools/bridge-reel")
SR = 44100; DUR = 15.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(21); out = np.zeros(N, np.float32)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
def noise(L): return rng.randn(L).astype(np.float32)
def knock(f=520):
    L = int(0.1 * SR); tt = np.arange(L) / SR
    return ((np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.02) + bp(noise(L), 700, 4000) * np.exp(-tt / 0.01) * 0.6)).astype(np.float32)
def tick(amp=1.0):
    L = int(0.02 * SR); tt = np.arange(L) / SR; return (bp(noise(L), 2000, 8000) * np.exp(-tt / 0.004)).astype(np.float32) * amp
def step(amp=1.0):
    L = int(0.14 * SR); tt = np.arange(L) / SR
    return (np.sin(2 * np.pi * 85 * tt) * np.exp(-tt / 0.05) + bp(noise(L), 300, 1800) * np.exp(-tt / 0.018) * 0.5).astype(np.float32) * amp
def sm(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)
import render_exact as RX
out += bp(noise(N), 50, 300) * 0.012
# expectation: the single post flies out, counter ticks fast, confetti burst
L = int(0.5 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 600, 5000) * np.sin(np.pi * tt / 0.5) ** 2, 0.4, 0.25)
add(knock(900), 1.1, 0.3)
tk = 0.9
while tk < 1.9: add(tick(0.8), tk, 0.18); tk += 0.03
def burst(t0):
    L = int(0.6 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 800, 7000) * np.exp(-tt / 0.18), t0, 0.5)
    L = int(0.9 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (80 * np.exp(-tt * 3)) * tt) * np.exp(-tt / 0.3)).astype(np.float32), t0, 0.6)
    for k in range(14): add(tick(1.0), t0 + 0.05 + rng.uniform(0, 1.0), 0.14)
burst(1.8); burst(12.0)
# reality: a knock for every few books that appear, steps while he climbs
def books(tt): return int(round(RX.real_posts(tt) / 1000.0 * RX.BOOKS))
last = 0; tt_ = 2.6
while tt_ < 10.1:
    n = books(tt_)
    if n > last: add(knock(430 + 60 * rng.rand()), tt_, 0.22 + 0.12 * rng.rand())
    last = n; tt_ += 0.01
for k in range(3): add(step(0.8), 2.65 + k * 0.2, 0.3)
for k in range(14):
    for fr in (0.0, 0.5): add(step(0.7), 3.2 + k * 0.5 + fr * 0.25, 0.22)
# followers counter: slow ticks, then the jump
tk = 2.6
while tk < 10.0: add(tick(0.6), tk, 0.1); tk += 0.14
tk = 10.0
while tk < 12.0: add(tick(0.9), tk, 0.18); tk += 0.035
L = int(0.6 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 600, 6000) * np.sin(np.pi * tt / 0.6) ** 2, 10.2, 0.25)
# closing line
add(tick(1.0), 13.0, 0.3); L = int(0.5 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 500, 4000) * np.sin(np.pi * tt / 0.5) ** 2, 12.95, 0.12)
out = np.tanh(out * 1.2) * 0.9
tmp = "/tmp/exact_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afade=t=out:st=14.3:d=0.7,loudnorm=I=-15:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
