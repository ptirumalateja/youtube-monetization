# Code-made SFX for "Mom's Phone" (action-synced, no music). Usage: python3 sfx.py out.wav
import sys, wave
import numpy as np
SR = 48000; DUR = 11.9
rng = np.random.default_rng(4)
out = np.zeros(int(SR * DUR))

def add(sig, t, gain=1.0):
    i = int(t * SR); n = min(len(sig), len(out) - i)
    if n > 0: out[i:i + n] += sig[:n] * gain
def tt(d): return np.arange(int(d * SR)) / SR
def env(n, a, r):
    e = np.ones(n); A = int(a * SR); R = int(r * SR)
    if A: e[:A] = np.linspace(0, 1, A)
    if R: e[-R:] *= np.linspace(1, 0, R)
    return e
def lp(x, k):  # simple one-pole lowpass, k in 0..1
    y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s += k * (x[i] - s); y[i] = s
    return y
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))

# snore 0-1.6 s: two breaths, rumbly low noise with pitch pulse
for t0 in (0.05, 0.85):
    d = 0.7; t = tt(d); n = rng.standard_normal(len(t))
    buzz = np.sign(np.sin(2 * np.pi * 38 * t)) * 0.5 + bp(n, 80, 600) * 3
    e = np.sin(np.pi * t / d) ** 2
    add(buzz * e, t0, 0.18)
# door creak 0.32
t = tt(0.35); f = 380 + 160 * np.sin(2 * np.pi * 3 * t)
creak = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * (rng.random(len(t)) > 0.3)
add(bp(creak, 300, 2500) * env(len(t), 0.02, 0.12), 0.32, 0.12)
# bubble pop 1.95
t = tt(0.08); add(np.sin(2 * np.pi * (900 - 5000 * t) * t) * np.exp(-t * 60), 1.95, 0.35)
# phone handoff rustle 3.0
t = tt(0.3); add(bp(rng.standard_normal(len(t)), 1500, 6000) * env(len(t), 0.05, 0.2), 3.0, 0.12)
# button click 4.55
t = tt(0.04); add(bp(rng.standard_normal(len(t)), 2000, 9000) * np.exp(-t * 300), 4.55, 0.7)
t = tt(0.03); add(np.sin(2 * np.pi * 1800 * t) * np.exp(-t * 250), 4.56, 0.3)
# flash boom 5.0: sub drop + noise burst
t = tt(1.4); boom = np.sin(2 * np.pi * (90 * np.exp(-t * 2.5) + 30) * t) * np.exp(-t * 2.2)
add(boom, 5.0, 0.9)
t = tt(0.9); add(bp(rng.standard_normal(len(t)), 200, 8000) * np.exp(-t * 4), 5.0, 0.45)
# beam roar 6.05-7.55: rising filtered noise + hum
t = tt(1.6); n = rng.standard_normal(len(t))
roar = bp(n, 60, 3000) * 1.4 + np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 110 * t) * 0.25
e = np.minimum(1, t / 0.35) * env(len(t), 0, 0.15)
add(roar * e, 6.05, 0.5)
t = tt(0.6); add(np.sin(2 * np.pi * (300 + 1800 * t) * t) * env(len(t), 0.02, 0.2), 6.25, 0.15)  # whoosh up
# wind howl 7.55-8.5
t = tt(0.95); n = rng.standard_normal(len(t))
howl = bp(n, 300, 1800) * 2 + np.sin(2 * np.pi * (520 + 120 * np.sin(2 * np.pi * 2 * t)) * t) * 0.25
add(howl * env(len(t), 0.05, 0.3), 7.55, 0.4)
# sparkle 8.7
for k, f0 in enumerate((2637, 3136, 3951)):
    t = tt(0.9); add(np.sin(2 * np.pi * f0 * t) * np.exp(-t * 5), 8.7 + k * 0.06, 0.12)
# sizzle 9.75-11.5 fading
t = tt(1.8); n = rng.standard_normal(len(t)) * (rng.random(len(t)) > 0.92)
add(bp(n, 2500, 9000) * np.exp(-t * 1.4), 9.75, 0.6)
# blink ticks
for tb in (10.55, 11.3):
    t = tt(0.05); add(np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 120), tb, 0.12)

out /= max(1e-9, np.abs(out).max()) / 0.89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
