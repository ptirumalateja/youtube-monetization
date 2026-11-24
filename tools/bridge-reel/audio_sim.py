#!/usr/bin/env python3
"""SFX only for the 10 s simultaneous 'what success looks like' cut. usage: audio_sim.py OUT.wav"""
import sys, subprocess, wave
import numpy as np
sys.path.insert(0, "/home/user/youtube-monetization/tools/bridge-reel")
import render_sim as RS
SR = 44100; DUR = 10.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(51); out = np.zeros(N, np.float32)
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
def tick(a=1.0):
    L = int(0.02 * SR); tt = np.arange(L) / SR; return (bp(noise(L), 2000, 8000) * np.exp(-tt / 0.004)).astype(np.float32) * a
def step(a=1.0):
    L = int(0.14 * SR); tt = np.arange(L) / SR
    return (np.sin(2 * np.pi * 85 * tt) * np.exp(-tt / 0.05) + bp(noise(L), 300, 1800) * np.exp(-tt / 0.018) * 0.5).astype(np.float32) * a
out += bp(noise(N), 50, 300) * 0.012
# top: post whoosh, race of ticks to a million, repeated celebration pops
L = int(0.4 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 600, 5000) * np.sin(np.pi * tt / 0.4) ** 2, 0.25, 0.25)
tk = 0.7
while tk < 1.3: add(tick(0.8), tk, 0.18); tk += 0.025
def burst(t0, a=0.5):
    L = int(0.6 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 800, 7000) * np.exp(-tt / 0.18), t0, a)
    L = int(0.9 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (80 * np.exp(-tt * 3)) * tt) * np.exp(-tt / 0.3)).astype(np.float32), t0, a * 1.1)
    for k in range(12): add(tick(1.0), t0 + 0.05 + rng.uniform(0, 1.0), 0.13)
for t0 in (1.3, 3.1, 4.9, 6.7): burst(t0, 0.5 if t0 < 2 else 0.22)
# bottom: knocks per few books, footsteps, slow ticks then the jump, big burst
def books(tt): return int(round(RS.real_posts(RS.tmap(tt)) / 1000.0 * RS.BOOKS))
last = 0; x = 0.25
while x < 6.0:
    n = books(x)
    if n > last: add(knock(430 + 60 * rng.rand()), x, 0.24 + 0.12 * rng.rand())
    last = n; x += 0.005
for k in range(3): add(step(0.8), 0.28 + k * 0.14, 0.3)
for k in range(14):
    for fr in (0.0, 0.5): add(step(0.7), 0.8 + k * 0.38 + fr * 0.19, 0.2)
tk = 0.3
while tk < 5.9: add(tick(0.6), tk, 0.1); tk += 0.11
tk = 5.9
while tk < 7.4: add(tick(0.9), tk, 0.18); tk += 0.03
L = int(0.6 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 600, 6000) * np.sin(np.pi * tt / 0.6) ** 2, 6.1, 0.25)
burst(7.4, 0.55)
add(tick(1.0), 8.3, 0.3); L = int(0.5 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 500, 4000) * np.sin(np.pi * tt / 0.5) ** 2, 8.25, 0.12)
out = np.tanh(out * 1.2) * 0.9
tmp = "/tmp/sim_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afade=t=out:st=9.4:d=0.6,loudnorm=I=-15:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
