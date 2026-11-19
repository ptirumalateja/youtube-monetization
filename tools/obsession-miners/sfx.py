"""Action-synced SFX bed for the obsession miners reel (no music: Teja adds a trending song).
Usage: python3 sfx.py out.wav
Hit times mirror the swing() phase maths in scene.html."""
import subprocess, sys
import numpy as np

SR = 48000
DUR = 33.1
LIB = '../sfxlib/'
out = np.zeros((int(SR * (DUR + 0.5)), 2), np.float32)
rng = np.random.default_rng(3)


def load(name, a=0.0, b=None):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', LIB + name, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True).stdout, np.float32).reshape(-1, 2)
    x = x[int(a * SR):(int(b * SR) if b else None)].copy()
    n = min(len(x), int(0.02 * SR))
    x[-n:] *= np.linspace(1, 0, n)[:, None]
    return x


def put(x, t, g=1.0, pan=0.0):
    if x.ndim == 1:
        x = np.stack([x * (1 - max(pan, 0)), x * (1 + min(pan, 0))], 1)
    i = int(t * SR)
    if i < 0:
        x = x[-i:]; i = 0
    j = min(len(out), i + len(x))
    out[i:j] += x[:j - i] * g


def env(n, atk, dec):
    t = np.arange(n) / SR
    return np.minimum(t / max(atk, 1e-4), 1) * np.exp(-t / dec)


def clink(pitch=1.0, dur=0.22):
    n = int(dur * SR); t = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * pitch * t) for f, a in [(2380, 0.5), (3710, 0.35), (5230, 0.2), (1460, 0.25)])
    s = s * env(n, 0.001, 0.045)
    nz = rng.standard_normal(n) * env(n, 0.0005, 0.012) * 0.7
    thud = np.sin(2 * np.pi * 110 * t) * env(n, 0.001, 0.03) * 0.6
    return (s + nz + thud).astype(np.float32) * 0.6


def boom(f0=55, dur=0.9, g=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (1 + 1.5 * np.exp(-t / 0.05))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, dur / 4)
    s += rng.standard_normal(n) * env(n, 0.001, 0.03) * 0.4
    return (s * g).astype(np.float32)


def pop(f=900, dur=0.09):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * np.cumsum(f * (1 + 2 * (1 - t / dur))) / SR) * env(n, 0.001, 0.025)
    return s.astype(np.float32) * 0.6


def bonk():  # "out": descending sad blip
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 420 * np.exp(-t * 3)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, 0.12) * 0.55).astype(np.float32)


def sparkle(dur=0.8, n_notes=10, base=1800, g=0.5):
    n = int(dur * SR); s = np.zeros(n, np.float32)
    for k in range(n_notes):
        st = int(rng.uniform(0, dur * 0.6) * SR); m = int(0.25 * SR)
        t = np.arange(m) / SR; f = base * rng.choice([1, 1.25, 1.5, 2, 2.5, 3])
        seg = np.sin(2 * np.pi * f * t) * env(m, 0.002, 0.07)
        e = min(n, st + m); s[st:e] += seg[:e - st] * 0.3
    return s * g


def hits(rate, off, t0, t1):
    """times where swing phase crosses 0.78 (strike contact)"""
    res = []
    k = np.ceil(t0 * rate + off - 0.78)
    while True:
        t = (k + 0.78 - off) / rate
        if t >= t1: break
        if t >= t0: res.append(t)
        k += 1
    return res


whoosh = load('649445__audiopapkin__cinematic-woosh-sfx-015.wav', 1.4, 3.6)   # peak ~1.0 s in
braam = load('722633__chakong__cinematic-braaam.wav', 0.1, 3.0)
riser = load('822420__audiopapkin__riser-hit-sfx-120.wav', 5.4, 8.0)          # hit ~0.5 s in
accent = load('869757__mikiko850__dark-suspense-accent.wav', 0.0, 0.48)
spark = load('849772__mikiko850__electric-sparks.wav', 0.0, 0.25)

# --- digging clinks (scene time intervals where the dig is on screen) ---
vis = [(0, 11.2), (11.7, 12.2), (16.07, 23.2), (28.0, 33.1)]
def vis_g(t):
    return 1.0 if any(a <= t < b for a, b in vis) else (0.25 if 23.2 <= t < 28 else 0)
for t in hits(2.5, 0, 0.0, 10.8) + hits(4.4, 0, 10.8, 33.1):
    g = vis_g(t)
    if g: put(clink(rng.uniform(0.95, 1.08)), t, 0.55 * g, 0.1)
    if g and t >= 10.8 and t < 23.2 or t >= 28: put(spark, t, 0.25 * g)
for rate, off, a, b, pan in [(2.3, 0.1, 0, 3.5, -0.4), (2.4, 0.3, 0, 4.4, -0.2), (2.2, 0.55, 0, 18.6, 0.3), (1.2, 0.55, 18.6, 20.9, 0.3)]:
    for t in hits(rate, off, a, b):
        g = vis_g(t)
        if g: put(clink(rng.uniform(0.8, 0.9)), t, 0.22 * g, pan)

# --- beats ---
put(boom(50, 1.0, 0.9), 0.0)
put(whoosh, 1.0 - 1.0, 0.7)                       # zoom in 0.5-1.0
put(bonk(), 3.5, 0.9); put(sparkle(0.6, 6, 2000, 0.6), 4.4)
put(bonk(), 6.0, 0.9)
put(whoosh, 6.45 - 1.0, 0.55); put(whoosh[::-1].copy(), 7.5 - 1.2, 0.45)
for t in (8.9, 9.4, 10.1): put(pop(), t, 0.9)
put(whoosh, 10.7 - 1.0, 0.5)
put(braam, 10.8 - 0.15, 0.55); put(boom(45, 1.2, 0.8), 10.8)
put(riser, 11.2 - 0.5, 0.7)
put(boom(60, 0.6, 0.7), 11.7)
put(accent, 12.2, 0.8)
put(boom(48, 0.8, 0.7), 13.3)
for t in (14.2, 14.5, 14.8, 15.0): put(boom(52, 0.5, 0.85), t)
put(boom(35, 0.9, 0.6), 15.3)
put(boom(55, 0.7, 0.8), 16.07)
put(boom(60, 0.6, 0.6), 18.0)
cas = np.zeros(int(0.9 * SR), np.float32)
for k in range(28):
    st = int(rng.uniform(0, 0.7) * SR); c = clink(rng.uniform(1.15, 1.6), 0.15)
    cas[st:st + len(c)] += c[:len(cas) - st] * 0.4
put(cas, 18.0, 0.8)
put(pop(700, 0.12), 20.85, 0.7)
put(whoosh, 23.2 - 1.0, 0.6)
put(pop(1200, 0.06), 24.0, 0.6); put(boom(55, 0.6, 0.7), 24.75)
put(whoosh[::-1].copy(), 28.0 - 1.2, 0.5); put(boom(60, 0.6, 0.7), 28.0)
put(whoosh, 31.2 - 1.0, 0.55)
put(sparkle(1.8, 22, 2200, 0.7), 30.8); put(boom(45, 1.4, 0.9), 31.2)

# limiter-ish normalise
peak = np.abs(out).max()
out = np.tanh(out / peak * 1.4) * 0.89
import soundfile as sf
sf.write(sys.argv[1], out[:int(DUR * SR)], SR)
print('peak', peak)
