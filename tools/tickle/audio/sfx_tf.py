#!/usr/bin/env python3
"""Synthesised sound design for the Time Flies reel (22.0 s). All numpy, no samples, no credits.
usage: python3 sfx_dreams.py out.wav   (48 kHz stereo float32 -> int16 wav)
Beats follow scene15.js: world starts A = 0, 3.0, 4.6, 6.8, 9.0, 10.9, 12.8, 14.9, 16.8, 19.1, 20.9, 22.5, 24.2, 25.5, 26.9, 28.7"""
import sys, numpy as np
from scipy import signal
from scipy.io import wavfile
SR = 48000; DUR = 22.0; N = int(SR * DUR); rng = np.random.default_rng(11)
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
# ---------- Time Flies (22.0 s): the ticking IS the story ----------
def tick(g=0.5, f=1900, d=0.05):
    t = tt(d); x = (np.sin(2 * np.pi * f * t) * 0.6 + noise(d) * 0.4) * np.exp(-t * 70); return x / (np.abs(x).max() + 1e-9) * g
def tock(g=0.5): return tick(g, 1300, 0.06)
def shutter(g=0.7):
    a = hp(noise(0.05), 2500) * np.exp(-tt(0.05) * 90); b = lp(noise(0.08), 900) * np.exp(-tt(0.08) * 40); out = np.zeros(int(0.16 * SR)); out[:len(a)] += a; out[int(0.07 * SR):int(0.07 * SR) + len(b)] += b * 0.7; return out / (np.abs(out).max() + 1e-9) * g
# bed: low drone + slow swell across the whole film, tail links back to the start
dr = (np.sin(2 * np.pi * 65.4 * T) * 0.5 + np.sin(2 * np.pi * 98 * T + 0.7) * 0.3 + np.sin(2 * np.pi * 130.8 * T) * 0.15) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.09 * T))
add(dr * np.interp(T, [0, 1.0, 17, 20.5, 21.7, 22], [0, 0.16, 0.2, 0.2, 0.08, 0]), 0)
# 0 - 2.9 hook: steady 1 Hz clock ticks, vortex swirl
for k in range(3): add(tick(0.55), 0.25 + k * 0.95, 0.55 if k % 2 == 0 else 0.45); 
add(whoosh(2.2, 250, 1800, 0.6, 0.9), 0.4, 0.16); add(sweep(2.2, 120, 300, 'lin') * env(2.2, .6, .9, 1) * 0.4, 0.4, 0.18)
# 2.9 - 4.5 absorbed: ticks fade out while a bright pad blooms (you stop hearing time)
for k in range(4): add(tick(0.5), 3.0 + k * 0.9, 0.45 * (1 - k / 4.0))
add(sum(np.sin(2 * np.pi * f * tt(1.8)) for f in (392, 494, 587)) * env(1.8, .5, .9, 1) * 0.12, 2.9, 0.3)
# 4.5 - 6.2 brain: red-node pings + soft heartbeat
rr = np.random.default_rng(3)
for k in range(9): add(chime(float(rr.choice([880, 1175, 1480, 1760])), 0.5, 0.5), 4.6 + k * 0.17, 0.12, float(rr.uniform(-.7, .7)))
for k in range(3): add(thud(56, 0.5, 0.8), 4.7 + k * 0.52, 0.32)
# 6.2 - 8.3 flies: ticks accelerate into a rush, whoosh sweeps past
tk, rate = 6.3, 3.0
while tk < 7.85: add(tick(0.5), tk, 0.4 + 0.25 * (tk - 6.3) / 1.5); rate *= 1.07; tk += 1.0 / rate
add(whoosh(1.8, 600, 5000, 0.9, 0.8), 6.25, 0.3); add(sweep(1.8, 200, 1400) * env(1.8, 0.2, 0.9, 1) * 0.3, 6.3, 0.2)
# 8.3 - 10.0 memory swirl: camera-shutter clicks as memories are counted
for k in range(5): add(shutter(0.9), 8.7 + k * 0.28, 0.32, [-.5, .5, -.3, .3, 0][k])
add(whoosh(1.5, 400, 2600, 0.6, 0.9), 8.3, 0.14)
# 10.0 - 11.6 film strip: projector flutter
for k in range(int(1.4 * 24)): add(click(0.5), 10.1 + k / 24, 0.10 * np.sin(np.pi * k / (1.4 * 24)), 0.2)
# 11.6 - 13.9 ribbon: ascending pentatonic ping per memory frame
for i, f in enumerate([523, 587, 659, 784, 880, 1047]): add(chime(f, 1.2, 0.6), 11.7 + i * 0.4, 0.2, (i % 2) * 0.8 - 0.4)
# 13.9 - 17.2 geo payoff: top = fast tight ticking (short DURING), bottom = slow notes per polaroid (long AFTER)
for k in range(int(2.8 * 11)): add(tick(0.4, 2300, 0.03), 14.0 + k / 11.0, 0.22 * (1 - 0.5 * k / 31))
for i, f in enumerate([262, 330, 392, 523, 659]): add(chime(f, 1.6, 0.6), 14.35 + i * 0.6, 0.24, (i - 2) * 0.35)
add(sum(np.sin(2 * np.pi * f * tt(3.2)) for f in (131, 196, 262)) * env(3.2, 1.0, 1.4, 1) * 0.15, 13.9, 0.25)
# 17.2 - 18.7 droste: pull-in swell, shutter at the inner photo, deep thud
add(sweep(1.5, 200, 900) * env(1.5, .3, .8, 1) * 0.4, 17.2, 0.2); add(whoosh(1.4, 300, 3000, 0.8, 0.8), 17.2, 0.22); add(shutter(1.0), 18.45, 0.4); add(thud(46, 0.9, 1.0), 18.5, 0.5)
# 18.7 - 20.2 gear: slowed time, deep heavy ticks + gear whir
for k in range(3): add(tock(0.9), 18.85 + k * 0.65, 0.45); add(thud(70, 0.4, 0.6), 18.85 + k * 0.65, 0.32)
add(bp(noise(1.5), 200, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 9 * tt(1.5))) * env(1.5, .2, .6, 1), 18.7, 0.12)
# 20.2 - 22: one last tick, chord resolve, loop-link
add(tick(0.8), 20.45, 0.5); add(thud(55, 1.0, 0.9), 20.45, 0.35); add(chime(392, 2.2, 0.5), 20.5, 0.22); add(chime(587, 2.0, 0.4), 20.55, 0.16)
# transitions
for A in [2.9, 4.5, 6.2, 8.3, 10.0, 11.6, 13.9, 17.2, 18.7, 20.2]: add(whoosh(0.7, 500, 3200, 0.55), A - 0.5, 0.14, 0.4 * (1 if int(A) % 2 else -1))
m = max(np.abs(L).max(), np.abs(R).max(), 1e-6); L, R = L / m * 0.85, R / m * 0.85
f = int(0.05 * SR); L[:f] *= np.linspace(0, 1, f); R[:f] *= np.linspace(0, 1, f); L[-f:] *= np.linspace(1, 0, f); R[-f:] *= np.linspace(1, 0, f)
wavfile.write(sys.argv[1], SR, (np.stack([L, R], 1) * 32767).astype(np.int16)); print('wrote', sys.argv[1])
