#!/usr/bin/env python3
"""SFX only for the 12 s 'mom's brightness' reel: snore, door creak, steps, screen-wake whine, flash hit + ringing, glare whoosh, earth ping, X-ray hum. usage: audio_mom.py OUT.wav"""
import sys, subprocess, wave
import numpy as np
SR = 44100; DUR = 12.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(31); out = np.zeros(N, np.float32)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
def noise(L): return rng.randn(L).astype(np.float32)
def tone(f, d, dec, amp=1.0, harm=0.3):
    L = int(d * SR); tt = np.arange(L) / SR; return ((np.sin(2 * np.pi * f * tt) + harm * np.sin(4 * np.pi * f * tt)) * np.exp(-tt / dec) * amp).astype(np.float32)
def step(a=1.0):
    L = int(0.14 * SR); tt = np.arange(L) / SR; return (np.sin(2 * np.pi * 85 * tt) * np.exp(-tt / 0.05) + bp(noise(L), 300, 1800) * np.exp(-tt / 0.018) * 0.5).astype(np.float32) * a
def tick(a=1.0):
    L = int(0.02 * SR); tt = np.arange(L) / SR; return (bp(noise(L), 2000, 8000) * np.exp(-tt / 0.004)).astype(np.float32) * a
out += bp(noise(N), 50, 260) * 0.014
# night room: slow snore (breath in/out) until 1.9
for k in range(2):
    L = int(0.9 * SR); tt = np.arange(L) / SR; env = np.sin(np.pi * np.minimum(tt / 0.9, 1)) ** 2
    add(bp(noise(L), 120, 700) * env * 0.35, 0.1 + k * 1.1, 0.5)
# door creak + light click, mom's steps, phone buzz
L = int(0.9 * SR); tt = np.arange(L) / SR; fr = 160 + 90 * tt + 18 * np.sin(2 * np.pi * 9 * tt)
add(bp((np.sign(np.sin(2 * np.pi * np.cumsum(fr) / SR)) * 0.5).astype(np.float32), 250, 2200) * (0.6 + 0.4 * np.sin(2 * np.pi * 13 * tt)) * np.sin(np.pi * tt / 0.9) ** 0.7, 1.8, 0.4)
for k in range(5): add(step(0.9), 2.1 + k * 0.32, 0.4)
add(tone(220, 0.35, 0.15, 0.5), 3.2, 0.3); add(tone(180, 0.4, 0.2, 0.5), 3.5, 0.3)
# he takes her phone: rustle, screen wakes with a rising whine, flash hit, ringing in the ears
L = int(0.35 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 1000, 6000) * np.sin(np.pi * tt / 0.35) ** 2, 4.45, 0.2)
L = int(1.0 * SR); tt = np.arange(L) / SR; add(np.sin(2 * np.pi * (300 + 2400 * (tt / 1.0) ** 2) * tt).astype(np.float32) * (tt / 1.0) ** 1.5, 4.95, 0.3)
add(tone(1000, 0.08, 0.02, 0.7), 5.0, 0.35)
rin = np.sin(2 * np.pi * 4200 * t) * np.interp(t, [5.6, 5.7, 7.2, 8.0], [0, 1, 0.5, 0]) * 0.05; out += rin.astype(np.float32)
# pain burst
L = int(0.8 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 500, 6000) * np.exp(-tt / 0.15), 5.6, 0.45)
add((np.sin(2 * np.pi * (95 * np.exp(-tt * 3.0)) * tt) * np.exp(-tt / 0.3)).astype(np.float32), 5.6, 0.7)
add(tone(300, 0.5, 0.2, 0.6, 1.0), 5.75, 0.3); add(tone(240, 0.5, 0.2, 0.6, 1.0), 6.05, 0.25)
# signal across the city, then the planet
L = int(1.1 * SR); tt = np.arange(L) / SR; add(bp(noise(L), 400, 7000) * (tt / 1.1) ** 1.5 * np.sin(np.pi * np.minimum(tt / 1.1, 1)) ** 0.5, 6.4, 0.5)
for k in range(4): add(tone(900 + 160 * k, 0.5, 0.2, 0.7), 6.55 + k * 0.2, 0.2)
L = int(1.4 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (60 * np.exp(-tt * 1.2)) * tt) * np.exp(-tt / 0.7)).astype(np.float32), 7.6, 0.6)
add(tone(1760, 1.2, 0.5, 0.8), 7.9, 0.4); add(tone(2637, 1.0, 0.4, 0.4), 7.95, 0.25)
# back in the room: electric hum from the glowing phone, bubble blip, low thud
hum = (np.sin(2 * np.pi * 196 * t) + 0.4 * np.sin(2 * np.pi * 392 * t)) * np.interp(t, [8.4, 8.9, 11.4, 12.0], [0, 0.07, 0.07, 0]); out += hum.astype(np.float32)
add(tone(660, 0.12, 0.05, 0.8), 9.4, 0.3); add(tone(880, 0.15, 0.06, 0.8), 9.52, 0.3)
add(tone(120, 0.9, 0.4, 0.8), 11.0, 0.3)
out = np.tanh(out * 1.2) * 0.9
tmp = "/tmp/mom_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "afade=t=out:st=11.4:d=0.6,loudnorm=I=-15:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True); print("wrote", sys.argv[1])
