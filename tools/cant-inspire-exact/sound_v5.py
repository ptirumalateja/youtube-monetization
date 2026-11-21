"""Synthesised sound for "The Unteachable (v5)" (numpy only, no samples).
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
def pluck(f, d=0.35, bright=1.0):
    t = tt(d); y = sum(a * np.sin(2 * np.pi * f * h * t) * np.exp(-t / dd) for h, a, dd in [(1, 1, .18), (2, .5 * bright, .09), (3, .3 * bright, .05)])
    return y * np.minimum(1, t / 0.003)
def clap():
    t = tt(0.12); return bandnoise(len(t), 900, 6000) * np.exp(-t / 0.025)
def heaveS(f0):
    t = tt(0.5); return np.sin(2 * np.pi * (f0 + 90 * np.exp(-t * 14)) * t) * np.exp(-t / 0.16) + 0.25 * bandnoise(len(t), 100, 900) * np.exp(-t / 0.06)
def roar(d=1.0):
    t = tt(d); n = bandnoise(len(t), 120, 1600); saw = ((np.cumsum(70 + 20 * np.sin(2 * np.pi * 6 * t)) / SR) % 1) * 2 - 1
    return (0.6 * n * (0.6 + 0.4 * np.sin(2 * np.pi * 23 * t)) + 0.5 * saw) * np.sin(np.pi * t / d) ** 0.7
def tinny(d, melody, step=0.18):
    # music leaking from headphones: thin, high-passed, fast
    y = np.zeros(int(d * SR))
    for k in range(int(d / step)):
        m = melody[k % len(melody)]
        if m is None: continue
        p = pluck(nt(m), 0.16, 1.6); i = int(k * step * SR); n2 = min(len(p), len(y) - i)
        if n2 > 0: y[i:i + n2] += p[:n2]
    hp = bandnoise(len(y), 1500, 7000) * 0.0
    Y = np.fft.rfft(y); f = np.fft.rfftfreq(len(y), 1 / SR); Y[f < 900] *= 0.05; Y[f > 6000] = 0
    return np.fft.irfft(Y, len(y)) + hp
def garble(d):
    t = tt(d); saw = ((np.cumsum(180 + 60 * np.sin(2 * np.pi * 3.3 * t) + 40 * rng.standard_normal(len(t)) * 0) / SR) % 1) * 2 - 1
    syl = np.clip(np.sin(2 * np.pi * 5.5 * t + 2 * np.sin(2 * np.pi * 1.3 * t)), 0, 1) ** 0.5
    y = saw * syl + 0.3 * bandnoise(len(t), 1200, 3500) * syl
    Y = np.fft.rfft(y); f = np.fft.rfftfreq(len(y), 1 / SR); Y[(f < 500) | (f > 3800)] = 0
    y = np.fft.irfft(Y, len(y)); return np.tanh(3 * y / (np.abs(y).max() + 1e-9))

# ---------- room tone (always on, dips in the silence beat) ----------
n = bandnoise(N, 40, 500) * 0.07; L += n; R += n[::-1]
# ---------- sneaky dark pizzicato bed 0-15 ----------
pat = [50, None, 53, None, 57, None, 56, None, 55, None, 53, None, 50, None, 49, None]
k = 0; t0 = 0.0
while t0 < 15.0:
    m = pat[k % 16]
    if m is not None:
        g = 0.22 if t0 < 11.5 else 0.28
        place(pluck(nt(m - 12), 0.4, 0.6), t0, g)
        if t0 >= 11.5: place(pluck(nt(m), 0.25), t0, 0.1)
    if k % 4 == 0: place(hb(), t0, 0.35)
    k += 1; t0 += 0.25
# ---------- 0-1.6 hook: pour onto the shut lid, it all bounces off ----------
place(pour(2.1, 1.0), 0.0, 0.32)
place(clink(1300), 0.03, 0.5); place(thud(70, 0.2), 0.03, 0.7); place(boom(1.5), 0.0, 0.45)
for k in range(16): place(splat(0.6), 0.05 + k * 0.1 + rng.random() * 0.04, 0.22, pan=rng.uniform(-.5, .5))
for k in range(6): place(knock() * 0.5, 0.2 + k * 0.24, 0.25, pan=0.3)  # drops pinging the lid
# ---------- 4-9 board ----------
place(sweep(1400, 300, 0.7, 1.0), 4.15, 0.12); place(whoosh(0.6, 300, 3000), 4.3, 0.3)
place(thud(80, 0.2), 4.9, 0.9); place(knock(), 4.9, 0.6); place(clink(900), 4.92, 0.2)
for t0 in [5.42, 5.87, 6.32]: place(knock() * 0.7, t0, 0.35, pan=-0.1)   # chalk taps
place(whoosh(0.32, 400, 5000), 6.75, 0.4); place(thud(110, 0.1), 7.05, 0.7); place(knock(), 7.05, 0.7)
place(sweep(900, 260, 0.45, 1.0), 6.98, 0.22)   # 938's double take
for k in range(9): place(thud(140, 0.04), 7.4 + k * 0.17, 0.25)  # frustrated stomp-shake
# ---------- 9-15 megaphone vs headphones ----------
place(sweep(2600, 3400, 0.4, 1.0), 9.15, 0.12)  # feedback squeal
place(garble(1.9), 9.4, 0.32, pan=-0.1)
for k in range(9): place(sweep(1200, 2400, 0.12, 1.0), 9.75 + k * 0.175, 0.08, pan=0.4)   # waves bounce off
place(knock() * 0.6, 9.95, 0.5)   # headphones clack on
mel = [76, 79, 83, 79, 76, None, 74, 76, 79, 81, 79, None, 76, 74, 71, None]
place(tinny(5.0, mel), 9.97, 0.3, pan=0.25)
place(tinny(6.0, mel), 15.0, 0.1, pan=0.25)
place(sweep(300, 900, 0.6, 1.0), 11.8, 0.18)   # "lift the lid" demo
# wrong imitation: screw it on tighter
for k in range(10): place(knock() * 0.35, 13.3 + k * 0.08, 0.3)
place(sweep(1500, 900, 0.8, 0.25) * np.sign(np.sin(2 * np.pi * 37 * tt(0.8))), 13.3, 0.18)
place(thud(90, 0.12), 14.12, 0.5)
for k in range(6): place(clap(), 14.23 + k * 0.143, 0.45, pan=0.2)
# ---------- 15-21 realisation: music drops, heartbeat ----------
place(boom(2.2), 15.0, 0.6)
tb = 15.3
while tb < 21.0:
    place(hb(), tb, 0.5); place(hb() * 0.7, tb + 0.24, 0.4); tb += 0.9
for t0, m in [(15.05, 50), (16.6, 57), (17.8, 53), (19.2, 49)]: place(piano(nt(m)), t0, 0.2); place(piano(nt(m - 12)), t0, 0.1)
# ---------- 21-25.4 walk away ----------
place(whoosh(0.3, 300, 3000), 21.05, 0.25); place(knock() * 0.6, 21.35, 0.4)
place(whoosh(0.5, 200, 4000), 21.4, 0.45)
place(thud(70, 0.2), 21.9, 0.9); 
for k in range(6): place(knock() * 0.6, 21.92 + k * 0.05 + rng.random() * 0.03, 0.4, pan=rng.uniform(-.3, .3))
for k in range(6): place(thud(150, 0.05), 22.25 + k * 0.262, 0.4, pan=0.1 * k)  # footsteps
for k, m in enumerate([62, 65, 69, 74]): place(pluck(nt(m), 0.6), 22.3 + k * 0.33, 0.12)  # warm lift
place(pour(0.9, 0.8), 23.95, 0.32)
g = 24.65
for k in range(3): place(heaveS(55 - 6 * k), g + k * 0.367, 0.75)
place(roar(0.75), g + 0.55, 0.4)
for k in range(4): place(sweep(900, 1600, 0.25, 1.0), 25.0 + k * 0.1, 0.06, pan=0.5)  # little cheers
# ---------- silence, then the last line ----------
place(piano(nt(45), 4.0), 25.75, 0.3); place(piano(nt(57), 4.0), 25.75, 0.18); place(piano(nt(60), 4.0), 25.75, 0.12)
place(tinny(1.0, mel), 26.2, 0.12, pan=0.25)
# flicker buzzes
for f in [0.3, 3.4, 8.2, 12.6, 16.2, 19.9, 22.6, 26.2]: place(buzz(), f, 0.15)
mix = np.stack([L, R], 1)
a, b = int(25.35 * SR), int(25.75 * SR)
mix[a:b] *= 0.04
mix = np.tanh(mix * 1.1); mix *= 0.89 / np.abs(mix).max()
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok', DUR)
