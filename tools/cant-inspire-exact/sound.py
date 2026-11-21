"""Synthesised sound for "Locked From the Inside" (numpy only, no samples).
Usage: python3 sound.py out.wav   (event times mirror scene.html)"""
import sys, wave
import numpy as np

SR = 48000
DUR = 38.4
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



TR = 0.14
# ---------- music bed: plucked minor waltz-ish loop, warmer at the end ----------
def pluck(f, d=0.6, b=0.5):
    t = tt(d); y = np.zeros(len(t))
    for h, a in [(1, 1), (2, .45 * b), (3, .2 * b), (4, .1 * b)]: y += a * np.sin(2 * np.pi * f * h * t) * np.exp(-t * (5 + 3 * h))
    return y * np.minimum(1, t / 0.004)
def nt(n): return 440 * 2 ** ((n - 69) / 12)
beat = 60 / 104
prog_min = [(57, [57, 60, 64]), (53, [53, 57, 60]), (55, [55, 59, 62]), (52, [52, 55, 59])]   # Am F G Em
prog_maj = [(48, [48, 52, 55]), (55, [55, 59, 62]), (57, [57, 60, 64]), (53, [53, 57, 60])]   # C G Am F
mel = [76, 74, 72, 74, 76, 79, 76, 74, 72, 71, 72, 74, 72, 71, 69, 67]
b = 0.0; i = 0
while b < DUR - 0.5:
    sad = 17.0 <= b < 26.0
    prog = prog_maj if b >= 26.0 else prog_min
    root, ch = prog[(i // 4) % 4]
    place(pluck(nt(root - 12), 0.9, 0.3), b, 0.30 if not sad else 0.22)
    for k, n in enumerate(ch):
        if i % 2 == 1 or not sad: place(pluck(nt(n), 0.5, 0.4), b + 0.02 * k, 0.07, pan=(k - 1) * 0.4)
    if not sad or i % 2 == 0:
        mn = mel[i % 16] + (0 if b < 26.0 else 0)
        place(pluck(nt(mn), 0.5, 0.8), b + beat * 0.5, 0.11 if not sad else 0.07, pan=0.2)
    b += beat; i += 1
# ---------- pours ----------
for s0, s1, sil in [(1.05, 1.85, 1), (3.05, 3.85, 1), (4.65, 5.45, 1), (5.75, 6.55, 0), (8.15, 9.0, 0), (10.6, 11.45, 0), (28.35, 29.55, 0), (34.0, 35.3, 0)]:
    place(pour(s1 - s0 + TR, 0.9), s0, 0.28 if sil else 0.36, pan=0.1)
# ---------- hulk growth: three heaves + roar ----------
def heave(f0):
    t = tt(0.5)
    return np.sin(2 * np.pi * (f0 + 90 * np.exp(-t * 14)) * t) * np.exp(-t / 0.16) + 0.25 * bandnoise(len(t), 100, 900) * np.exp(-t / 0.06)
def stretch(d):
    t = tt(d); f = 180 + 260 * t / d
    return 0.6 * np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.sin(np.pi * t / d) * 0.3
def roar(d=0.7):
    t = tt(d); n = bandnoise(len(t), 120, 1600)
    saw = ((np.cumsum(70 + 20 * np.sin(2 * np.pi * 6 * t)) / SR) % 1) * 2 - 1
    return (0.6 * n * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t)) + 0.5 * saw) * np.sin(np.pi * t / d) ** 0.7
for g, d, sil in [(1.85, .75, 1), (3.85, .75, 1), (5.45, .75, 1), (6.62, 1.1, 0), (9.05, 1.1, 0), (11.5, 1.1, 0), (29.65, 1.1, 0), (35.4, 1.1, 0)]:
    for k in range(3):
        place(heave(55 - 6 * k), g + k * d / 3, 0.75 if not sil else 0.55)
        place(stretch(d / 3 * 0.8), g + k * d / 3, 0.10)
    place(roar(0.6 if sil else 0.8), g + d * 0.7, 0.35 if not sil else 0.22)
    place(chime(784.0 if not sil else 659.3, 1.2), g + d, 0.18)
# cut to colour
place(whoosh(0.35, 300, 5000), 5.8, 0.3)
# ---------- jar ----------
place(whoosh(0.4, 400, 3000), 17.0, 0.25)
place(clink(1700), 17.7, 0.3)
for k in range(12): place(knock() * 0.4, 18.3 + k * 0.058, 0.35)
place(thud(70, 0.15), 19.0, 0.5)
for t0 in [21.18, 21.58, 21.98]: place(clink(2400) * 0.8, t0, 0.55); place(thud(300, 0.03), t0, 0.12)
place(sweep(500, 330, 0.5, 0.4), 23.2, 0.25)  # sigh
for k in range(7): place(thud(120, 0.05), 25.25 + k * 0.16, 0.25)
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.1)
mix *= 0.89 / np.abs(mix).max()
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', DUR)
