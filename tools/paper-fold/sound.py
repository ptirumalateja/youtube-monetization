"""Sound for the paper-fold reel: warm pad, fold ticks (paper crinkle -> bright blips), whooshes, hits, silence before the record line.
python3 sound.py out.wav
"""
import sys, math, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from make import NODES, n_of, DUR

SR = 44100
N = int(SR * (DUR + 0.5))
rng = np.random.default_rng(11)
mix = np.zeros((2, N))

def t_arr(n): return np.arange(n) / SR
def add(sig, t0, gain=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N: return
    j = min(N, i + len(sig)); seg = sig[:j - i] * gain
    mix[0, i:j] += seg * (1 - pan) ** 0.5 * 0.9; mix[1, i:j] += seg * (1 + pan) ** 0.5 * 0.9

def lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y

def noise_lp(n, fc): return lp(rng.standard_normal(n), fc)

# ---------------- bed: warm pad, evolves with the story
tt = t_arr(N)
def env(points):  # list of (t, v)
    xs, vs = zip(*points); return np.interp(tt, xs, vs)
pad = np.zeros(N)
for f, a in [(55.0, 0.5), (82.4, 0.4), (110.0, 0.35), (164.8, 0.25), (220.0, 0.2), (329.6, 0.12)]:
    det = 1 + 0.0035 * np.sin(2 * np.pi * (0.13 + f / 700) * tt)
    pad += a * np.sin(2 * np.pi * f * det * tt + f)
bright = np.zeros(N)
for f, a in [(440.0, 0.08), (659.3, 0.06), (880.0, 0.05), (1318.5, 0.03)]:
    bright += a * np.sin(2 * np.pi * f * tt + 2 * f) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.21 * tt + f))
bed_env = env([(0, 0.0), (0.2, 0.35), (2.0, 0.35), (2.05, 0.14), (9.0, 0.22), (12.3, 0.4), (19.0, 0.34), (25.6, 0.5), (27.0, 0.18), (27.4, 0.0), (28.7, 0.0), (29.2, 0.14), (31.0, 0.1), (31.5, 0)])
bright_env = env([(0, 0.0), (2.0, 0.0), (5.0, 0.0), (11.5, 0.6), (13, 0.5), (24, 0.8), (25.6, 1.0), (27.0, 0.2), (27.4, 0.0), (29.2, 0.1), (31.5, 0)])
bed = (pad * bed_env + bright * bright_env * 0.9)
mix[0] += bed * 0.5; mix[1] += np.roll(bed, 220) * 0.5

# ---------------- fold ticks
fold_times = []
for f in range(1, 104):
    # time at which the counter reaches f
    if f <= 7: t = 2.0 + (f - 0.35) / 7 * (4.9 - 2.0)
    else:
        lo, hi = 4.9, 40.0
        for _ in range(40):
            mid = (lo + hi) / 2
            if n_of(mid) < f: lo = mid
            else: hi = mid
        t = hi
    fold_times.append((f, t))
for f, t in fold_times:
    if t > 25.7: continue
    if f <= 7:  # paper crinkle + soft thud
        n = int(0.09 * SR); x = noise_lp(n, 5200) - noise_lp(n, 700); x *= np.exp(-t_arr(n) * 55) * np.hanning(n) ** 0.2
        add(x, t, 0.42 + 0.02 * f, pan=-0.2)
        th = np.sin(2 * np.pi * (90 + 6 * f) * t_arr(int(0.12 * SR))) * np.exp(-t_arr(int(0.12 * SR)) * 28); add(th, t + 0.02, 0.35, pan=-0.2)
    else:  # glassy blip climbing with the folds
        fr = 520 * 2 ** (min(f, 103) / 24.0 % 3.0) * (1.0 if f < 60 else 1.12)
        n = int(0.16 * SR); tx = t_arr(n); x = (np.sin(2 * np.pi * fr * tx) + 0.35 * np.sin(2 * np.pi * fr * 2.01 * tx)) * np.exp(-tx * 24)
        add(x, t, 0.13 if f < 60 else 0.11, pan=((f * 37) % 11 - 5) / 12)
        if f % 5 == 0:
            k = np.sin(2 * np.pi * 70 * t_arr(int(0.2 * SR))) * np.exp(-t_arr(int(0.2 * SR)) * 14); add(k, t, 0.22)

# ---------------- hits and whooshes
def boom(t0, g=1.0, dur=1.6):
    n = int(dur * SR); tx = t_arr(n); f = 70 * np.exp(-tx * 1.6) + 28
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tx * 2.1)
    x += 0.5 * noise_lp(n, 900) * np.exp(-tx * 7)
    add(x, t0, g)
def whoosh(t0, dur, g=0.5, up=True):
    n = int(dur * SR); tx = t_arr(n); u = tx / dur
    x = rng.standard_normal(n); out = np.zeros(n)
    # swept band-pass via two low-passes
    for k, fc in enumerate(np.geomspace(300, 7000, 14)):
        seg = lp(x, fc); out += seg * (np.exp(-((u - (k / 13 if up else 1 - k / 13)) ** 2) / 0.03))
    out *= np.sin(np.pi * u) ** 1.2
    add(out / (np.max(np.abs(out)) + 1e-9), t0, g)
whoosh(1.45, 0.6, 0.45, True); boom(2.0, 0.9, 1.0)          # cut from the hook to the desk
whoosh(10.5, 1.5, 0.55, True)                                  # through the clouds
boom(12.3, 1.0); whoosh(12.3, 1.2, 0.3, False)                 # 30 folds
boom(19.0, 0.8, 1.4)                                           # 69 folds
whoosh(24.6, 1.0, 0.4, True); boom(25.6, 1.25, 2.4)           # 103 folds
# shimmer after the last fold
n = int(2.2 * SR); tx = t_arr(n)
sh = sum(np.sin(2 * np.pi * f * tx + i) * np.exp(-tx * (1.3 + 0.2 * i)) * 0.08 for i, f in enumerate([880, 1318.5, 1760, 2637, 3520]))
add(sh, 25.65, 1.0)
# the record line lands in silence: a single low note
n = int(1.8 * SR); tx = t_arr(n); note = np.sin(2 * np.pi * 110 * tx) * np.exp(-tx * 1.7) * 0.5
add(note, 27.5, 0.7)

# ---------------- master
for c in range(2): mix[c] = lp(mix[c], 12500)
peak = np.max(np.abs(mix)); mix = mix / peak * 0.89
fade = np.ones(N); nf = int(0.35 * SR); fade[-nf:] = np.linspace(1, 0, nf); mix *= fade
import wave
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('wrote', sys.argv[1], round(N / SR, 2), 's')
