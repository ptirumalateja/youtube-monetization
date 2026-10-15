#!/usr/bin/env python3
"""Synthesised sound design for the dreams reel (30.0 s). All numpy, no samples, no credits.
usage: python3 sfx_dreams.py out.wav   (48 kHz stereo float32 -> int16 wav)
Beats follow scene15.js: world starts A = 0, 3.0, 4.6, 6.8, 9.0, 10.9, 12.8, 14.9, 16.8, 19.1, 20.9, 22.5, 24.2, 25.5, 26.9, 28.7"""
import sys, numpy as np
from scipy import signal
from scipy.io import wavfile
SR = 48000; DUR = 30.0; N = int(SR * DUR); rng = np.random.default_rng(11)
T = np.arange(N) / SR
L = np.zeros(N); R = np.zeros(N)
def add(sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N: return
    n = min(len(sig), N - i0); g = gain
    L[i0:i0 + n] += sig[:n] * g * (1 - max(pan, 0) * 0.6); R[i0:i0 + n] += sig[:n] * g * (1 + min(pan, 0) * 0.6)
def tt(d): return np.arange(int(d * SR)) / SR
def env(d, a=0.01, r=0.3, curve=2.0):
    t = tt(d); e = np.minimum(t / max(a, 1e-4), 1) * np.clip((d - t) / max(r, 1e-4), 0, 1); return e ** curve if curve != 1 else e
def noise(d): return rng.standard_normal(int(d * SR))
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, f0, f1, o=2): return signal.sosfilt(signal.butter(o, [f0, f1], 'band', fs=SR, output='sos'), x)
def sweep(d, f0, f1, shape='exp'):
    t = tt(d); k = t / d; f = f0 * (f1 / f0) ** k if shape == 'exp' else f0 + (f1 - f0) * k; return np.sin(2 * np.pi * np.cumsum(f) / SR)
def whoosh(d, f0, f1, gain=0.5, q=0.6):                      # noise through a moving band
    x = noise(d); y = np.zeros_like(x); k = tt(d) / d; blocks = 24
    for b in range(blocks):
        a, e = int(b / blocks * len(x)), int((b + 1) / blocks * len(x)); f = f0 * (f1 / f0) ** ((b + .5) / blocks)
        y[a:e] = bp(x[max(0, a - 600):e], max(40, f * (1 - q * .5)), min(SR / 2 - 100, f * (1 + q)), 2)[min(a, 600):][:e - a] if e - a > 0 else 0
    return y / (np.abs(y).max() + 1e-9) * gain * env(d, d * .35, d * .55, 1)
def thud(f=58, d=0.5, g=1.0):
    t = tt(d); return np.sin(2 * np.pi * (f * 0.55 + f * 0.45 * np.exp(-t * 18)) * t) * np.exp(-t * 7.5) * g
def chime(f, d=2.0, g=0.5):
    t = tt(d); return (np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * f * 2.01 * t) + 0.2 * np.sin(2 * np.pi * f * 3.02 * t)) * np.exp(-t * 2.2) * g * np.minimum(t / 0.004, 1)
def click(g=0.7):
    x = hp(noise(0.03), 1500) * np.exp(-tt(0.03) * 260); return x / (np.abs(x).max() + 1e-9) * g
# ---------- bed: dark drone + breath (whole film), loops into itself ----------
t = T; drone = (np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 82.4 * t + 1.0) * 0.3 + np.sin(2 * np.pi * 110.3 * t) * 0.2) * (0.55 + 0.45 * np.sin(2 * np.pi * 0.11 * t))
dg = np.interp(t, [0, 1.5, 24, 28.5, 29.8, 30], [0.0, 0.16, 0.2, 0.22, 0.1, 0.0]); add(drone * dg, 0)
breath = lp(noise(DUR), 700) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.27 * T - 1.2)) ** 2; add(breath * np.interp(T, [0, 0.4, 3.0, 4.0], [0, 0.12, 0.12, 0.0]), 0)
# ---------- soul lift 0.7 - 2.3 ----------
d = 1.7; sh = (sweep(d, 220, 880) * 0.5 + sweep(d, 330, 1320) * 0.3) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt(d))) * env(d, 0.4, 0.5, 1); add(sh, 0.7, 0.22)
add(whoosh(1.6, 300, 2500, 0.6), 0.8, 0.16, 0.3); add(chime(784, 2.2, 0.6), 2.1, 0.28, -0.2); add(chime(1175, 2.2, 0.4), 2.15, 0.18, 0.2)
# ---------- transitions: soft whoosh into every world ----------
for A in [3.0, 4.6, 6.8, 9.0, 10.9, 12.8, 14.9, 16.8, 19.1, 20.9, 22.5, 24.2, 25.5, 26.9, 28.7]:
    add(whoosh(0.7, 500, 3200, 0.55), A - 0.5, 0.18 if A != 3.0 else 0.32, 0.4 * (1 if int(A) % 2 else -1))
# ---------- fall 3.0 - 4.6 ----------
add(sweep(1.7, 900, 90) * env(1.7, 0.1, 1.2, 1) * 0.5, 3.0, 0.2); add(whoosh(1.6, 4000, 300, 0.8), 3.0, 0.3)
# ---------- brain 4.6 - 6.8: heartbeat + EKG tick ----------
for k in range(int((6.8 - 4.6) * 1.15)):
    tb = 4.6 + k / 1.15; add(thud(58, 0.5, 0.9), tb, 0.55); add(thud(70, 0.4, 0.6), tb + 0.2, 0.4); add(chime(1760, 0.18, 0.5) * 0.5, tb + 0.34, 0.12, 0.5)
# ---------- logic switch 7.8: click + power-down ----------
add(click(0.9), 7.82, 0.5); add(sweep(1.2, 320, 38) * env(1.2, 0.02, 0.9, 1) * 0.6, 7.85, 0.28); add(lp(noise(1.2), 400) * env(1.2, .05, .9, 1), 7.85, 0.2)
# ---------- island cracks 9.0 - 10.8 ----------
for tc in [9.25, 9.5, 9.8, 10.1, 10.45]:
    x = hp(noise(0.25), 900) * np.exp(-tt(0.25) * 22); add(x / np.abs(x).max(), tc, 0.34, rng.uniform(-.6, .6)); add(thud(48, 0.7, 0.8), tc + 0.02, 0.22)
add(lp(noise(2.0), 180) * env(2.0, 0.2, 1.2, 1), 9.0, 0.35)
# ---------- stairs 10.9 - 12.8: endless rising arpeggio (shepard-like) ----------
for k in range(14):
    f = 220 * 2 ** ((k % 7) / 7 * 1.0) * (1 if k < 7 else 2); add(chime(f, 0.5, 0.5), 11.0 + k * 0.12, 0.13 * (1 - k / 20), (k % 2) * 0.8 - 0.4)
# ---------- REM 12.8 - 14.9: locked body, muffled ----------
add(lp(noise(2.1), 260) * env(2.1, .3, .8, 1), 12.8, 0.3); add(click(0.6), 13.25, 0.35); add(click(0.6), 13.45, 0.3); add(click(0.6), 13.7, 0.28)
for k in range(2): add(thud(52, 0.6, 0.9), 13.1 + k * 0.85, 0.4)
# ---------- ship 14.9 - 16.8: creak + sea ----------
cr = sweep(1.4, 70, 130) * 0.5 + sweep(1.4, 140, 260) * 0.25; cr = cr * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * tt(1.4))); add(cr * env(1.4, .2, .5, 1), 15.0, 0.22); add(whoosh(1.9, 200, 1400, 0.6), 14.9, 0.2)
# ---------- wave 16.8 - 19.1: swell, crest on heartbeat ----------
add(whoosh(2.4, 150, 2200, 0.9, 0.9), 16.8, 0.42)
for k in range(4): add(thud(54, 0.5, 0.9), 17.2 + k * 0.52, 0.45)
add(thud(44, 1.1, 1.0), 17.95, 0.5); add(whoosh(1.0, 3000, 600, 0.8), 17.9, 0.22)
# ---------- corridor 19.1 - 20.9: footsteps toward the light ----------
for k in range(3): add(lp(noise(0.12), 400) * np.exp(-tt(0.12) * 38), 19.3 + k * 0.55, 0.45, 0.1)
add(sweep(1.8, 196, 392) * env(1.8, 0.8, 0.8, 1) * 0.4, 19.1, 0.16); add(chime(392, 2.6, 0.5), 20.5, 0.18)
# ---------- ribbon 20.9 - 22.5: projector flutter ----------
for k in range(int(1.6 * 24)): add(click(0.5), 20.9 + k / 24, 0.12 * np.sin(np.pi * k / (1.6 * 24)), 0.2)
# ---------- whale 22.5 - 24.2: slow song ----------
ws = (sweep(2.0, 90, 150, 'lin') + 0.5 * sweep(2.0, 180, 300, 'lin')) * (1 + 0.15 * np.sin(2 * np.pi * 4.5 * tt(2.0))) * env(2.0, .5, .9, 1); add(ws, 22.5, 0.26, -0.3)
# ---------- web 24.2 - 25.5: spinning shimmer ----------
sw = bp(noise(1.6), 1500, 6000) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * tt(1.6))) * env(1.6, .3, .6, 1); add(sw, 24.2, 0.2, 0.4); add(sweep(1.5, 400, 1600) * env(1.5, .2, .6, 1) * 0.3, 24.3, 0.16)
# ---------- eye 25.5 - 26.9: suck in, near silence ----------
add(sweep(1.3, 1800, 70) * env(1.3, .1, 0.7, 1) * 0.5, 25.5, 0.26); add(whoosh(1.2, 4000, 200, 0.7), 25.6, 0.2)
# ---------- lucid 26.9 - 28.7: light-bulb ping + warm chord ----------
add(chime(1568, 2.4, 0.6), 27.15, 0.3, 0.1); add(chime(2349, 2.0, 0.3), 27.18, 0.14, -0.2)
for f in (196, 294, 392): add(np.sin(2 * np.pi * f * tt(2.2)) * env(2.2, .6, 1.0, 1) * 0.5, 26.9, 0.1)
# ---------- end: fall into the bed, thud, loop link ----------
add(sweep(1.0, 700, 80) * env(1.0, .05, .6, 1) * 0.5, 28.7, 0.22); add(whoosh(0.9, 3000, 300, 0.8), 28.7, 0.22)
add(thud(50, 0.9, 1.0), 29.35, 0.55); add(chime(196, 1.6, 0.5), 29.4, 0.2)
# gentle stereo width + final trim
L, R = L * 1.0, R * 1.0
m = max(np.abs(L).max(), np.abs(R).max(), 1e-6); L, R = L / m * 0.85, R / m * 0.85
f = int(0.05 * SR); L[:f] *= np.linspace(0, 1, f); R[:f] *= np.linspace(0, 1, f); L[-f:] *= np.linspace(1, 0, f); R[-f:] *= np.linspace(1, 0, f)
wavfile.write(sys.argv[1], SR, (np.stack([L, R], 1) * 32767).astype(np.int16)); print('wrote', sys.argv[1])
