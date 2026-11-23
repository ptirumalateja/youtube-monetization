#!/usr/bin/env python3
"""Sound v3 for the door reel (10 s): quiet menacing murmur (no shouting), rising drone + heartbeat, door shut, three muffled knocks, then silence (suspense),
creak, warm light swell with birds and soft footsteps. Synthesized.   usage: audio_door3.py OUT.wav"""
import sys, subprocess, wave
import numpy as np
SR = 44100; DUR = 10.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(11); out = np.zeros(N, np.float32)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
# murmur: low, breathy, slow swells (whispered crowd), cut by the door
mur = np.zeros(N, np.float32)
for v in range(7):
    src = rng.randn(N).astype(np.float32) * 0.6 + np.sign(np.sin(2 * np.pi * rng.uniform(100, 170) * t)) * 0.2
    vo = bp(src, 250, 1200)
    am = np.clip(np.sin(2 * np.pi * rng.uniform(1.6, 3.2) * t + rng.uniform(0, 6)) + 0.2, 0, 1) ** 1.6
    mur += vo * am
mur /= np.abs(mur).max() + 1e-6
env = np.interp(t, [0, 0.8, 3.6, 4.28, 4.4, 4.7], [0.0, 0.16, 0.34, 0.36, 0.05, 0.0])
out += mur * env
cm = bp(mur, 80, 450) * np.interp(t, [4.3, 4.45, 4.9, 5.4], [0, 0.14, 0.05, 0]); out += cm
# rising drone + sub swell, drops out at the shut
dr = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.5 * t) + 0.3 * np.sin(2 * np.pi * 110 * t + 1)) * 0.2
out += dr * np.interp(t, [0, 3.0, 4.35, 4.6, 8.2, 8.8], [0.2, 0.7, 0.9, 0.12, 0.08, 0.0])
# heartbeat: speeds up to the shut, then slow under the silence
def beat(t0, amp):
    for off, a in ((0.0, 1.0), (0.22, 0.6)):
        L = int(0.3 * SR); tt = np.arange(L) / SR
        add((np.sin(2 * np.pi * (62 - 20 * tt / 0.3) * tt) * np.exp(-tt / 0.075) * a).astype(np.float32), t0 + off, amp)
tb = 0.6
while tb < 4.2: beat(tb, 0.20 + 0.25 * tb / 4.2); tb += 1.1 - 0.35 * tb / 4.2
tb = 5.2
while tb < 8.2: beat(tb, 0.22); tb += 1.25 + 0.1 * (tb - 5.2)
# door shut at 4.42
L = int(1.6 * SR); tt = np.arange(L) / SR
thud = np.sin(2 * np.pi * (84 * np.exp(-tt * 3.0)) * tt) * np.exp(-tt / 0.3) * 1.1
crack = bp(rng.randn(L).astype(np.float32), 300, 3500) * np.exp(-tt / 0.045) * 0.7
tail = bp(rng.randn(L).astype(np.float32), 80, 900) * np.exp(-tt / 0.55) * 0.22
add(np.tanh((thud + crack + tail) * 1.3).astype(np.float32), 4.4, 0.9)
# three muffled knocks from the other side, fading, then nothing
for tk, a in ((5.35, 0.55), (6.0, 0.38), (6.55, 0.22)):
    L = int(0.35 * SR); tt = np.arange(L) / SR
    add(np.tanh((np.sin(2 * np.pi * 110 * tt) * np.exp(-tt / 0.07) + bp(rng.randn(L).astype(np.float32), 200, 900) * np.exp(-tt / 0.03) * 0.5) * 1.2).astype(np.float32), tk, a)
# room tone in the silence
out += bp(rng.randn(N).astype(np.float32), 60, 350) * np.interp(t, [4.5, 5.0, 8.1, 8.4], [0, 0.07, 0.07, 0.0])
# breath at the "move on" beat
L = int(1.0 * SR); tt = np.arange(L) / SR; add(bp(rng.randn(L).astype(np.float32), 400, 2600) * np.sin(np.pi * tt) ** 2 * 0.16, 6.45)
# creak 8.3-9.2
L = int(1.0 * SR); tt = np.arange(L) / SR; fr = 150 + 120 * tt + 25 * np.sin(2 * np.pi * 9 * tt)
creak = bp((np.sign(np.sin(2 * np.pi * np.cumsum(fr) / SR)) * 0.5).astype(np.float32), 250, 2200) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * tt)) * np.sin(np.pi * tt) ** 0.7
add(creak.astype(np.float32), 8.3, 0.5)
# warm swell (Cmaj add9) + birds + soft wind + footsteps
pad = np.zeros(N, np.float32)
for f, a in ((130.8, 1.0), (196.0, 0.7), (261.6, 0.6), (329.6, 0.5), (392.0, 0.4), (587.3, 0.25), (784.0, 0.12)):
    pad += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (1 + 0.15 * np.sin(2 * np.pi * rng.uniform(0.2, 0.5) * t))
out += pad * 0.07 * np.interp(t, [8.3, 9.3, 9.8, 10.0], [0, 0.8, 1.0, 0.7])
for tb_ in (8.9, 9.25, 9.6, 9.8):
    L = int(0.25 * SR); tt = np.arange(L) / SR; f = 3300 + 900 * np.sin(2 * np.pi * 14 * tt) + rng.uniform(-300, 300)
    add((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.25) ** 2 * 0.06).astype(np.float32), tb_, 1.0)
out += bp(rng.randn(N).astype(np.float32), 200, 1400) * np.interp(t, [8.3, 9.0, 10], [0, 0.04, 0.04])
for k in range(4):
    ts = 9.15 + k * 0.28; L = int(0.18 * SR); tt = np.arange(L) / SR
    add((np.sin(2 * np.pi * 70 * tt) * np.exp(-tt / 0.05) + bp(rng.randn(L).astype(np.float32), 500, 2500) * np.exp(-tt / 0.02) * 0.3).astype(np.float32), ts, 0.4)
out = np.tanh(out * 1.1) * 0.9
tmp = "/tmp/door3_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "loudnorm=I=-15:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
