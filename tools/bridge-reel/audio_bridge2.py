#!/usr/bin/env python3
"""SFX only (no music) for 'who tries harder' (12 s): plank knocks, footsteps, kneel thumps, phone taps/buzz, day-counter ticks, typing, hug air swell + heartbeat, rumble, slump.
usage: audio_bridge2.py OUT.wav"""
import sys, subprocess, wave
import numpy as np
SR = 44100; DUR = 12.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(13); out = np.zeros(N, np.float32)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
def noise(L): return rng.randn(L).astype(np.float32)
def knock(f=520, amp=1.0):
    L = int(0.14 * SR); tt = np.arange(L) / SR
    return ((np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.025) + 0.5 * np.sin(2 * np.pi * f * 1.9 * tt) * np.exp(-tt / 0.015)) * amp + bp(noise(L), 600, 3500) * np.exp(-tt / 0.012) * 0.5).astype(np.float32)
def step(amp=1.0):
    L = int(0.16 * SR); tt = np.arange(L) / SR
    return (np.sin(2 * np.pi * 85 * tt) * np.exp(-tt / 0.05) + bp(noise(L), 300, 1800) * np.exp(-tt / 0.018) * 0.5).astype(np.float32) * amp
def tick(amp=1.0):
    L = int(0.02 * SR); tt = np.arange(L) / SR; return (bp(noise(L), 2000, 8000) * np.exp(-tt / 0.004)).astype(np.float32) * amp
# room tone
out += bp(noise(N), 50, 300) * 0.012
# top builders: plank knocks (both sides, a hair apart), kneel thumps, long-stride footsteps
for n in range(3):
    t0 = 0.6 + n * 1.4
    add(step(0.9), t0 + 0.02, 0.5); add(step(0.9), t0 + 0.05, 0.5)             # kneel down
    for k in range(3):
        tp = t0 + (k + 1) / 3.4 * 0.8
        add(knock(540 + 40 * k), tp, 0.55); add(knock(500 + 40 * k), tp + 0.04, 0.45)
    ts = t0 + 0.8
    for j, fr in enumerate((0.15, 0.45)):
        add(step(), ts + fr * 0.6, 0.6); add(step(), ts + fr * 0.6 + 0.03, 0.55)
# bottom builder (slower): knocks and steps
for n in range(3):
    t0 = 0.8 + n * 1.9
    add(step(0.8), t0 + 0.02, 0.4)
    for k in range(3): add(knock(430 + 30 * k), t0 + (k + 1) / 3.4 * 1.15, 0.45)
    ts = t0 + 1.15
    for fr in (0.15, 0.5): add(step(), ts + fr * 0.75, 0.5)
# phone: lift rustle, taps, buzz
L = int(0.3 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 1200, 6000) * np.sin(np.pi * tt / 0.3) ** 2, 0.3, 0.12)
for tk in (0.9, 1.2, 1.6, 2.0, 3.1, 3.4, 4.2, 4.6, 5.0, 6.1, 6.5):
    L = int(0.05 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * 1800 * tt) * np.exp(-tt / 0.008) * 0.6).astype(np.float32), tk, 0.18)
for tb in (2.4, 4.0, 6.8):
    L = int(0.4 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * 150 * tt) * (0.5 + 0.5 * np.sin(2 * np.pi * 30 * tt)) * np.exp(-tt / 0.25)).astype(np.float32), tb, 0.35)
# DAY counter ticks (fast, fading), lock click at 365
tk = 0.5
while tk < 5.2:
    add(tick(0.7 * (1.0 - 0.6 * (tk - 0.5) / 4.7)), tk, 0.2); tk += 0.05
L = int(0.08 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * 900 * tt) * np.exp(-tt / 0.015) + bp(noise(L), 1500, 6000) * np.exp(-tt / 0.01)).astype(np.float32), 5.2, 0.45)
# typed text ticks (labels) and the final line
for a, b, r in ((0.4, 1.7, 0.09), (0.8, 1.7, 0.1), (2.4, 3.5, 0.09), (5.0, 5.7, 0.07), (5.7, 6.4, 0.08), (7.2, 7.9, 0.1), (8.4, 9.0, 0.12)):
    for x in np.arange(a, b, r): add(tick(0.7), float(x), 0.1)
for x in np.arange(9.2, 11.4, 0.055): add(tick(0.8), float(x), 0.11)
# hug: air swell + sub boom + soft heartbeat
L = int(1.4 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 400, 4500) * np.sin(np.pi * tt / 1.4) ** 2, 5.3, 0.35)
L = int(1.0 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (70 * np.exp(-tt * 3)) * tt) * np.exp(-tt / 0.3)).astype(np.float32), 5.7, 0.7)
for tb in (6.1, 6.9, 7.7):
    for off, a in ((0.0, 1.0), (0.2, 0.6)):
        L = int(0.3 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (60 - 16 * tt / 0.3) * tt) * np.exp(-tt / 0.08) * a).astype(np.float32), tb + off, 0.35)
# too far: cold rumble swell, slump thud + cloth
rum = bp(noise(N), 35, 120) * np.interp(t, [7.0, 7.8, 8.6, 9.6], [0, 0.6, 0.9, 0.0]); out += rum * 0.9
L = int(1.3 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (110 * np.exp(-tt * 2.6)) * tt) * np.exp(-tt / 0.35)).astype(np.float32), 8.7, 0.75)
L = int(0.7 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 500, 4000) * np.exp(-tt / 0.2) * np.sin(np.pi * np.minimum(tt / 0.1, 1) / 2), 8.65, 0.2)
out = np.tanh(out * 1.2) * 0.9
tmp = "/tmp/bridge2_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afade=t=out:st=11.4:d=0.6,loudnorm=I=-15:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
