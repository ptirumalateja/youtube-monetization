#!/usr/bin/env python3
"""SFX only for 'what success looks like' (12 s). usage: audio_success.py OUT.wav"""
import sys, subprocess, wave, math
import numpy as np
sys.path.insert(0, "/home/user/youtube-monetization/tools/bridge-reel")
SR = 44100; DUR = 12.0; N = int(SR * DUR); t = np.arange(N) / SR
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
def posts_n(tt):
    p = min(1.0, max(0.0, (tt - 0.8) / 7.2)); return int(1000 * (p * p * (3 - 2 * p) * 0.85 + p * 0.15))
out += bp(noise(N), 50, 300) * 0.012
# expectation: the single post (whoosh + pop), then fast counter ticks, burst
L = int(0.4 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 600, 5000) * np.sin(np.pi * tt / 0.4) ** 2, 0.8, 0.25)
add(knock(900), 1.38, 0.3)
tk = 1.0
while tk < 2.5: add(tick(0.8), tk, 0.18); tk += 0.035
def burst(t0):
    L = int(0.6 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 800, 7000) * np.exp(-tt / 0.18), t0, 0.5)
    L = int(0.9 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (80 * np.exp(-tt * 3)) * tt) * np.exp(-tt / 0.3)).astype(np.float32), t0, 0.6)
    for k in range(14): add(tick(1.0), t0 + 0.05 + rng.uniform(0, 1.0), 0.14)
burst(2.5); burst(9.9)
# reality: a knock per ~14 posts (it speeds up and slows), footsteps while climbing
last = 0; tt_ = 0.8
while tt_ < 8.0:
    n = posts_n(tt_)
    if n // 14 > last // 14: add(knock(430 + 60 * rng.rand()), tt_, 0.2 + 0.15 * rng.rand())
    last = n; tt_ += 0.004
for k in range(8): add(step(0.8), 0.9 + k * 0.1, 0.3)
for k in range(10):
    for fr in (0.0, 0.5): add(step(0.7), 1.8 + k * 0.62 + fr * 0.3, 0.25)
# reality follower counter ticks (slow, then the jump)
tk = 0.8
while tk < 8.4: add(tick(0.6), tk, 0.1); tk += 0.16
tk = 8.4
while tk < 9.9: add(tick(0.9), tk, 0.18); tk += 0.035
# closing line swap
L = int(0.5 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 500, 5000) * np.sin(np.pi * tt / 0.5) ** 2, 9.35, 0.22)
out = np.tanh(out * 1.2) * 0.9
tmp = "/tmp/success_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afade=t=out:st=11.4:d=0.6,loudnorm=I=-15:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
