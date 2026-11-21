"""Synthesised sound for "Locked From the Inside" (numpy only, no samples).
Usage: python3 sound.py out.wav   (event times mirror scene.html)"""
import sys, wave
import numpy as np

SR = 48000
DUR = 19.6
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


TR = 0.13
# ---------- hook (payoff first): pour onto shut lid, splats, big hit at 0.30 ----------
place(pour(1.05, 1.0), 0.0, 0.35)
for k in range(9): place(splat(0.6), 0.02 + k * 0.11 + rng.random() * 0.03, 0.22, pan=rng.uniform(-.4, .4))
place(splat(1.6), 0.30, 0.9); place(clink(2600), 0.30, 0.35); place(thud(70, 0.3), 0.30, 0.8)
# rewind whip
place(whoosh(0.4, 300, 6000, rev=True), 0.92, 0.6); place(sweep(1600, 300, 0.35, 0.25), 0.98, 1.0)
# ---------- groove 1.3-10.0 (energy never drops in the first 5 s) ----------
b = 1.30
while b < 9.95:
    place(kick(), b, 0.55)
    place(hat(), b + 0.25, 0.18, pan=0.3)
    b += 0.5
# bass pulse
for k, t0 in enumerate(np.arange(1.30, 9.9, 0.5)):
    f = [55, 55, 65.4, 49][(k // 2) % 4]
    t = tt(0.45); place(np.tanh(2 * np.sin(2 * np.pi * f * t)) * np.exp(-t / 0.2), t0, 0.22)
# chain pours + rising chimes on each lighting
chain = [(1.36, 1.80), (1.98, 2.42), (2.60, 3.04)]
notes = [523.3, 587.3, 659.3, 784.0, 880.0, 1046.5, 1174.7, 1318.5, 1568.0, 1760.0]
for k, (s0, s1) in enumerate(chain):
    place(pour(s1 - s0 + TR, 0.7), s0, 0.3, pan=-0.2)
    place(chime(notes[k]), s1 + TR + 0.02, 0.4)
# hero celebrates
place(chime(1046.5, 1.2, 1.4), 3.22, 0.25)
# slam
place(thud(60, 0.3), 4.22, 1.0); place(clink(1900), 4.22, 0.35); place(whoosh(0.18, 500, 5000), 4.05, 0.3)
# counter ticks
for t0 in [2.0, 2.62, 3.2, 4.56, 5.45, 6.02, 6.70, 7.30, 8.70]:
    place(sweep(1800, 2600, 0.05, 1.0), t0, 0.15)
# TRY 1 pour + splats
place(pour(0.75, 0.8), 4.56, 0.3)
for k in range(6): place(splat(0.7), 4.70 + k * 0.1, 0.25, pan=rng.uniform(-.4, .4))
# TRY 2 knocks
for t0 in [5.62, 5.82]: place(knock(), t0, 0.9)
# TRY 3 squeak
place(sweep(900, 1500, 0.3, 0.25) * np.sign(np.sin(np.arange(int(0.3 * SR)) / SR * 2 * np.pi * 40)), 6.08, 0.6)
place(sweep(1400, 800, 0.3, 0.25), 6.36, 0.5)
# TRY 4 sad two-note
place(chime(392.0, 1.0, 0.4), 6.72, 0.35); place(chime(349.2, 1.0, 0.4), 6.95, 0.35)
# TRY 5 rattle
for k in range(14): place(knock() * 0.5, 7.32 + k * 0.042, 0.35, pan=rng.uniform(-.3, .3))
# rehook tension: riser + heartbeat
place(sweep(80, 160, 0.8, 0.5), 7.9, 0.6); place(whoosh(0.8, 2000, 9000), 7.9, 0.12)
for t0 in [7.95, 8.18, 8.40, 8.58]: place(thud(48, 0.12), t0, 0.7)
# TRY 6 flood
place(pour(1.15, 1.8), 8.86, 0.55)
for k in range(16): place(splat(1.0), 8.99 + k * 0.065, 0.28, pan=rng.uniform(-.6, .6))
place(sweep(400, 120, 1.0, 0.3), 9.0, 0.5)  # he drains
# ---------- reveal ----------
place(thud(45, 0.5), 10.0, 1.0); place(sweep(300, 2400, 0.45, 0.4), 10.0, 0.5)
t = tt(3.0); place(sum(a * np.sin(2 * np.pi * 220 * m * t) * np.exp(-t / d) for m, a, d in [(1, 1, 1.4), (2.01, .5, .9), (2.98, .35, .5)]), 10.05, 0.35)
place(pad([110, 130.8, 164.8], 2.0), 10.1, 0.25)
# lets go: soft breath whoosh + refill shimmer
place(whoosh(0.5, 400, 3000), 11.8, 0.25)
for k in range(5): place(chime(notes[k] * 2, 0.6, 0.6), 11.95 + k * 0.1, 0.08)
# pour over the jar + chain finale
place(whoosh(0.4, 600, 6000), 12.30, 0.3)
fin = [(12.50, 13.05), (13.34, 13.74), (13.90, 14.30), (14.46, 14.86), (15.02, 15.40), (15.52, 15.90), (16.02, 16.40), (16.52, 16.90), (17.02, 17.40)]
for k, (s0, s1) in enumerate(fin):
    place(pour(s1 - s0 + TR, 0.7), s0, 0.18 if k else 0.3)
    place(chime(notes[min(k + 2, 9)], 1.4), s1 + TR + 0.02, 0.32 if k < 4 else 0.24)
# warm resolve
place(pad([130.8, 164.8, 196.0, 261.6], 7.2), 12.4, 0.35)
b = 12.5
while b < 18.6:
    place(kick() * 0.6, b, 0.35); b += 0.5

mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.1)
mix *= 0.89 / np.abs(mix).max()
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', DUR)
