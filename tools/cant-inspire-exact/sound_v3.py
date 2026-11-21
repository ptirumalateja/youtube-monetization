"""Synthesised sound for "Locked From the Inside" (numpy only, no samples).
Usage: python3 sound.py out.wav   (event times mirror scene.html)"""
import sys, wave
import numpy as np

SR = 48000
DUR = 27.0
N = int(DUR * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(11)


def place(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i + len(sig) <= 0: return
    if i < 0: sig = sig[-i:]; i = 0
    n = min(len(sig), N - i)
    gl, gr = gain * np.sqrt(0.5 * (1 - pan)), gain * np.sqrt(0.5 * (1 + pan))
    L[i:i + n] += sig[:n] * gl; R[i:i + n] += sig[:n] * gr


def tt(d): return np.arange(int(d * SR)) / SR


def bandnoise(n, lo, hi):
    X = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)


def chime(freq, dur=1.6, bright=1.0):
    t = tt(dur); y = np.zeros(len(t))
    for mult, amp, dec in [(1, 1.0, 1.0), (2.0, 0.35, 0.6), (2.76, 0.4 * bright, 0.4), (5.4, 0.18 * bright, 0.18)]:
        y += amp * np.sin(2 * np.pi * freq * mult * t + rng.random() * 6) * np.exp(-t / dec)
    y *= np.minimum(1, t / 0.002)
    return y / np.abs(y).max()


def pour(dur, heavy=1.0):
    t = tt(dur); n = len(t)
    base = bandnoise(n, 500 / heavy, 5000)
    glug = 0.5 + 0.5 * np.sin(2 * np.pi * (8 + 4 * np.sin(2 * np.pi * 1.1 * t)) * t)
    low = bandnoise(n, 60, 400) * heavy * 0.6
    e = np.minimum(1, t / 0.04) * np.minimum(1, (dur - t) / 0.08)
    return (0.6 * base * glug + low) * e


def splat(big=1.0):
    t = tt(0.45)
    n = bandnoise(len(t), 300, 7000) * np.exp(-t / (0.05 * big))
    thump = np.sin(2 * np.pi * (120 * np.exp(-t * 8) + 50) * t) * np.exp(-t / 0.12) * big
    return 0.7 * n + 0.8 * thump


def clink(f=3100):
    t = tt(0.6); y = sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / d) for m, a, d in [(1, 1, .25), (1.51, .6, .15), (2.4, .4, .08)])
    return y * np.minimum(1, t / 0.001)


def thud(f0=90, d=0.25):
    t = tt(d * 3)
    return np.sin(2 * np.pi * (f0 * 2.5 * np.exp(-t * 30) + f0) * t) * np.exp(-t / d) + 0.3 * bandnoise(len(t), 80, 1500) * np.exp(-t / 0.02)


def knock():
    t = tt(0.25)
    return (np.sin(2 * np.pi * 420 * t) * 0.6 + np.sin(2 * np.pi * 690 * t) * 0.4) * np.exp(-t / 0.035) + 0.5 * bandnoise(len(t), 800, 4000) * np.exp(-t / 0.008)


def whoosh(d, lo=200, hi=4000, rev=False):
    t = tt(d); n = len(t)
    y = bandnoise(n, lo, hi) * np.sin(np.pi * t / d) ** 2
    return y[::-1] if rev else y


def sweep(f0, f1, d, amp=1.0):
    t = tt(d); f = f0 * (f1 / f0) ** (t / d)
    return amp * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d)


def kick():
    t = tt(0.3)
    return np.sin(2 * np.pi * (55 + 120 * np.exp(-t * 40)) * t) * np.exp(-t / 0.11)


def hat():
    t = tt(0.06)
    return bandnoise(len(t), 6000, 14000) * np.exp(-t / 0.015)


def pad(freqs, d):
    t = tt(d); y = np.zeros(len(t))
    for f in freqs:
        for det in (-0.6, 0.6):
            y += np.sin(2 * np.pi * (f + det) * t + rng.random() * 6)
    e = np.minimum(1, t / 1.2) * np.minimum(1, (d - t) / 0.8)
    return y / len(freqs) / 2 * e




def nt(n): return 440 * 2 ** ((n - 69) / 12)
def piano(f, d=3.0):
    t = tt(d); y = np.zeros(len(t))
    for h, a, dec in [(1, 1, 1.6), (2, .5, 1.0), (3, .25, .6), (4, .12, .4), (5, .06, .25)]:
        y += a * np.sin(2 * np.pi * f * h * (1 + 0.0004 * h * h) * t) * np.exp(-t / dec)
    y += 0.15 * bandnoise(len(t), 1000, 6000) * np.exp(-t / 0.01)
    return y * np.minimum(1, t / 0.002)
def hb():
    t = tt(0.25); return np.sin(2 * np.pi * (48 + 40 * np.exp(-t * 30)) * t) * np.exp(-t / 0.07)
def boom(d=2.5):
    t = tt(d); return np.sin(2 * np.pi * (32 + 30 * np.exp(-t * 4)) * t) * np.exp(-t / 0.7) + 0.2 * bandnoise(len(t), 30, 300) * np.exp(-t / 0.4)
def buzz(d=0.22):
    t = tt(d); return (np.sign(np.sin(2 * np.pi * 100 * t)) * 0.3 + 0.3 * bandnoise(len(t), 2000, 8000)) * np.sin(np.pi * t / d)
# level envelope for the bed (atmosphere -> pulse -> drop -> build -> silence)
def bed_gain(t):
    return np.interp(t, [0, 5, 6, 12, 12.6, 17.6, 18.2, 23.0, 23.25, 23.7, 27], [0.6, 0.7, 1.0, 1.0, 0.15, 0.15, 0.8, 1.0, 0.0, 0.0, 0.0])
# room tone
n = bandnoise(N, 40, 500); amb = n * 0.08
L += amb * bed_gain(np.arange(N) / SR); R += amb[::-1] * bed_gain(np.arange(N) / SR)
# heartbeat 0-12, faint later
tb = 0.15
while tb < 23.0:
    g = float(bed_gain(tb)) * (0.55 if tb < 12 else 0.4)
    place(hb(), tb, g); place(hb() * 0.7, tb + 0.24, g * 0.8)
    tb += 0.95 if tb < 5 else 0.78
# low cinematic pulse 5-12 and 18-23
for t0 in np.arange(5.0, 12.0, 0.78): t = tt(0.6); place(np.tanh(3 * np.sin(2 * np.pi * 41 * t)) * np.exp(-t / 0.25), t0 + 0.39, 0.25)
for k, t0 in enumerate(np.arange(18.2, 23.0, 0.6)): t = tt(0.5); place(np.tanh(3 * np.sin(2 * np.pi * 41 * t)) * np.exp(-t / 0.2), t0, 0.15 + 0.03 * k)
# piano: sparse minor motif
for t0, m in [(0.1, 57), (3.1, 64), (5.1, 60), (7.1, 59), (9.7, 57), (12.2, 52), (15.6, 45), (18.0, 57), (19.4, 60), (20.8, 64)]:
    place(piano(nt(m)), t0, 0.22); place(piano(nt(m - 12)), t0, 0.12)
# final line after the silence: one open chord, fading out
for m in [45, 52, 57, 60, 64]: place(piano(nt(m), 4.5), 23.7, 0.13)
# booms on key beats
for t0, g in [(0.02, 0.6), (9.7, 0.5), (15.55, 0.75)]: place(boom(), t0, g)
# flicker buzzes (visual flickers mapped from story time)
MAP = [[0, 3, 13.0, 14.8], [3, 5, 20.6, 22.4], [5, 7, 23.0, 24.6], [7, 9.5, 17.0, 19.6], [9.5, 12, 22.4, 25.0], [12, 15.5, 15.0, 16.8], [15.5, 17.5, 19.6, 21.0], [17.5, 23.5, 25.2, 31.2], [23.5, 27.0, 31.2, 33.4]]
for f in [0.35, 2.9, 7.6, 12.95, 16.2, 19.9, 24.6, 27.3, 32.7, 37.0]:
    for a, b2, c, d in MAP:
        if c <= f < d and not (23.2 < a < 23.8): place(buzz(), a + (f - c) / (d - c) * (b2 - a), 0.18)
# action SFX
for t0 in [3.58, 3.98, 4.38]: place(clink(2400) * 0.8, t0, 0.5)
place(whoosh(0.4, 300, 2500), 7.0, 0.25)
for k in range(12): place(knock() * 0.4, 8.25 + k * 0.056, 0.35)
place(thud(70, 0.15), 8.95, 0.5)
for k in range(7): place(thud(120, 0.05), 17.55 + k * 0.16, 0.25)
place(pour(1.35, 0.9), 20.65, 0.32)
# hulk growth at 21.95 (1.1 s): heaves, glass cracks, roar
def heave(f0):
    t = tt(0.5); return np.sin(2 * np.pi * (f0 + 90 * np.exp(-t * 14)) * t) * np.exp(-t / 0.16) + 0.25 * bandnoise(len(t), 100, 900) * np.exp(-t / 0.06)
def roar(d=1.0):
    t = tt(d); n = bandnoise(len(t), 120, 1600); saw = ((np.cumsum(70 + 20 * np.sin(2 * np.pi * 6 * t)) / SR) % 1) * 2 - 1
    return (0.6 * n * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t)) + 0.5 * saw) * np.sin(np.pi * t / d) ** 0.7
g = 21.95
for k in range(3): place(heave(55 - 6 * k), g + k * 0.367, 0.8)
for k in range(5): place(clink(3800 + 900 * k) * 0.5, g + 0.367 * (k % 3) + 0.02 * k, 0.12)
place(roar(0.75), g + 0.55, 0.5)
mix = np.stack([L, R], 1)
mix[int(23.25 * SR):int(23.7 * SR)] *= np.linspace(1, 0, int(23.7 * SR) - int(23.25 * SR))[:, None] * 0 + 0.05
mix = np.tanh(mix * 1.1); mix *= 0.89 / np.abs(mix).max()
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', DUR)
