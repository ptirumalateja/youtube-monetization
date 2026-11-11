"""Synth sound bed for the year-left reel (no samples, no licences).
120 BPM grid; every hit has a visual cause in index.html. Usage: python3 sound.py out.wav"""
import sys, wave
import numpy as np

SR = 48000
DUR = 18.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR


def buf():
    return np.zeros(N)


def place(dst, sig, t0, gain=1.0):
    i = int(t0 * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    if i < 0:
        sig = sig[-i:]; i = 0; j = min(N, len(sig))
    dst[i:j] += sig[: j - i] * gain


def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def lp(x, fc):
    # zero-phase 2-pole-like low-pass in the frequency domain
    n = len(x)
    if n < 2:
        return x
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    return np.fft.irfft(X / (1 + (f / fc) ** 2), n)


def hp(x, fc):
    return x - lp(x, fc)


def noise(sec):
    return rng.standard_normal(int(sec * SR))


def kick(gain=1.0):
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 50 + 120 * np.exp(-t / 0.03)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.12)
    click = hp(rng.standard_normal(n), 3000) * np.exp(-t / 0.004) * 0.3
    return np.tanh((body + click) * 1.6) * gain


def hat(gain=1.0, d=0.03):
    n = int(0.12 * SR)
    return hp(rng.standard_normal(n), 7000) * env(n, 0.0005, d) * gain


def tick(freq=3200, gain=1.0, d=0.012):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * freq * t) * env(n, 0.0003, d) * gain


def pluck(freq, sec=0.24, gain=1.0, bright=1600):
    n = int(sec * SR); t = np.arange(n) / SR
    saw = 2 * ((freq * t) % 1) - 1
    saw2 = 2 * ((freq * 1.005 * t) % 1) - 1
    x = (saw + saw2) * 0.5 * env(n, 0.003, sec * 0.45)
    return lp(x, bright) * gain


def impact(gain=1.0, size=1.0):
    n = int((0.9 + 1.2 * size) * SR); t = np.arange(n) / SR
    crack = hp(rng.standard_normal(n), 2500) * np.exp(-t / 0.02) * 0.6
    f = 70 + 230 * np.exp(-t / 0.06)
    body = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t / (0.25 * size + 0.1)) * 0.9
    sub = np.sin(2 * np.pi * 48 * t) * np.exp(-t / (0.35 * size)) * 0.5
    tail = lp(rng.standard_normal(n), 900) * np.exp(-t / (0.5 * size)) * 0.35
    return (crack + body + sub + tail) * gain


def suck(sec=0.4, gain=1.0):
    n = int(sec * SR); t = np.arange(n) / SR
    x = hp(rng.standard_normal(n), 1500) * (t / sec) ** 3
    return x * gain


def whoosh(sec, f0=400, f1=4000, gain=1.0):
    n = int(sec * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # sweeping band: low-pass at sweeping cutoff approximated by segments
    out = np.zeros(n); seg = 2400
    for i in range(0, n, seg):
        fc = f0 * (f1 / f0) ** (i / n)
        out[i:i + seg] = lp(x[i:i + seg], fc) * (fc / 1000) ** 0.3
    shape = np.sin(np.pi * t / sec) ** 2
    return hp(out, 150) * shape * gain


def riser(sec, gain=1.0):
    n = int(sec * SR); t = np.arange(n) / SR
    f = 200 * (2000 / 200) ** (t / sec)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4
    nz = hp(rng.standard_normal(n), 2000) * 0.5
    return (tone + nz) * (t / sec) ** 2 * gain


def bell(freq, sec=2.5, gain=1.0):
    n = int(sec * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * freq * r * t) * np.exp(-t / (sec * d))
            for r, a, d in [(1, 1, .5), (2.01, .5, .3), (2.76, .35, .2), (5.4, .2, .1)])
    return x * env(n, 0.002, 10) * gain


# ---------------------------------------------------------------- buses
drums, bass, sfx, hits = buf(), buf(), buf(), buf()
BEAT = 0.5
ROOTS = [55.0, 43.65, 65.41, 49.0]  # A F C G per 2 s bar


def groove(t0, t1, energy=1.0):
    t = t0
    while t < t1 - 1e-6:
        b = round((t - t0) / BEAT)
        place(drums, kick(0.9 * energy), t)
        place(drums, hat(0.25 * energy), t + BEAT / 2)
        place(drums, hat(0.1 * energy, 0.015), t + BEAT / 4)
        place(drums, hat(0.1 * energy, 0.015), t + 3 * BEAT / 4)
        root = ROOTS[int(t // 2) % 4]
        for e in range(2):  # 8th-note bass plucks
            place(bass, pluck(root * 2, 0.22, 0.5 * energy, 900), t + e * BEAT / 2)
        if b % 2 == 1:
            place(drums, hp(noise(0.18), 1200) * env(int(0.18 * SR), 0.001, 0.05) * 0.35 * energy, t)  # clap
        t += BEAT


groove(0.0, 9.9)
groove(14.0, 16.0, 1.15)

# bar hits + scramble glitches
for tt in [0.0, 2.0, 4.0, 6.0, 8.0]:
    place(hits, impact(0.55 if tt else 0.7, 0.6), tt)
    if tt:
        for k in range(10):
            place(sfx, tick(2000 + 3000 * rng.random(), 0.25, 0.008), tt + k * 0.026)

# day-fill ticks: one per filled day, thinned (accelerating)
fill_T0 = 315
prev = 0
for i in range(1, 58):
    tt = i / 30.0
    k = min(1, tt / 1.92)
    n = int(fill_T0 * (0.04 * k + 0.96 * k ** 2.3))
    if n > prev:
        place(sfx, tick(2600 + 1400 * k, 0.22 + 0.15 * k, 0.01), tt)
    prev = n

place(sfx, whoosh(0.75, 300, 5000, 0.35), 3.3)          # dots fly to digits
for k in range(50):                                     # dots land into digits
    place(sfx, tick(1800 + 2500 * rng.random(), 0.12, 0.008), 3.55 + 0.45 * rng.random())
for k in range(50):                                     # dots pour into the week grid
    place(sfx, tick(1500 + 2500 * rng.random(), 0.13, 0.01), 5.6 + 0.5 * rng.random())
place(sfx, whoosh(0.6, 2000, 400, 0.25), 5.5)
for r in range(7):                                      # weekends light row by row
    place(sfx, tick(880 * 2 ** (r / 12 * 2), 0.35, 0.05), 8.05 + r / 8 * 0.7)
place(sfx, whoosh(0.6, 400, 3000, 0.35), 9.4)           # tilt into the road

# breakdown: clock ticks + typed words, held breath before DON'T
for k in range(8):
    place(sfx, tick(1200 if k % 2 else 1500, 0.35, 0.02), 10.0 + k * 0.25)
place(sfx, suck(0.45, 0.25), 11.45)
place(hits, impact(1.0, 1.4), 12.0)                     # DON'T.
place(sfx, hp(noise(0.7), 4000) * np.linspace(1, 0, int(0.7 * SR)) ** 2 * 0.18, 12.95)  # disintegrate
place(sfx, riser(0.85, 0.35), 13.15)                    # spark up the road
for k in range(16):
    place(sfx, tick(2500 + 2000 * rng.random(), 0.15, 0.006), 13.15 + 0.8 * rng.random())
place(hits, impact(0.95, 1.2), 14.0)                    # START
place(sfx, whoosh(1.95, 200, 6000, 0.4), 14.0)
place(sfx, suck(0.35, 0.3), 15.65)
place(hits, impact(1.0, 1.0), 16.0)                     # TODAY.
place(sfx, bell(659.25, 2.0, 0.22), 16.0)
place(sfx, bell(987.77, 1.6, 0.1), 16.02)

# master before the rewind
def master(d, b, s, h):
    x = hp(d, 40) * 0.9 + hp(b, 60) * 0.8 + hp(s, 120) * 0.9 + h * 1.0
    return x


mix = master(drums, bass, sfx, hits)
# fade everything after 16.95, then rewind
cut = int(16.95 * SR)
mix[cut:] *= np.exp(-(np.arange(N - cut) / SR) / 0.08)

# rewind: replay 0..11.9 s backwards following the same time warp as the picture
def eio(k):
    return np.where(k < .5, 4 * k ** 3, 1 - (-2 * k + 2) ** 3 / 2)


i0 = int(17.0 * SR)
u = np.clip((np.arange(i0, N) / SR - 17.0) / 1.0, 0, 1)
src = 11.9 * (1 - eio(u)) * SR
pre = master(drums, bass, sfx, hits)
rew = np.interp(src, np.arange(N), pre)
rew = lp(rew, 3500) * 0.45 * np.minimum(1, (np.arange(N - i0) / SR) / 0.05)
mix[i0:] += rew
place(mix, whoosh(1.0, 3000, 300, 0.25), 17.0)

# loudness: soft clip and normalise near -1 dBFS peak
mix = np.tanh(mix * 1.3)
mix *= 0.89 / np.max(np.abs(mix))
st = np.stack([mix, np.roll(mix, 12) * 0.98], 1)
out = (st * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok')
