"""Sound for the continuous fall (fully synthesised, nothing to credit).

usage: sound4.py dives.json out.wav
Bed: deep drone + breathing wind. Each dive: a rising, accelerating whoosh with a pitch riser
that peaks as the frame goes black, a short near-silence, then a sub boom and an airy release
as the next black hole opens. The last dive lands on frame 0, so the loop is seamless.
"""
import json
import sys
import wave
import numpy as np

cfg = json.load(open(sys.argv[1]))
DUR = cfg["dur"]
SR = 48000
n = int(DUR * SR)
t = np.arange(n) / SR
rng = np.random.default_rng(4)


def band(lo, hi, seed, m=n):
    r = np.random.default_rng(seed)
    spec = np.fft.rfft(r.standard_normal(m))
    f = np.fft.rfftfreq(m, 1 / SR)
    spec *= ((f > lo) & (f < hi)) / np.maximum(f, 1) ** 0.4
    y = np.fft.irfft(spec, m)
    return y / np.abs(y).max()


def sweep_noise(t0, t1, f0, f1, seed):
    """Noise whose band centre glides f0 -> f1 between t0 and t1 (piecewise bands, crossfaded)."""
    out = np.zeros(n)
    steps = 12
    for k in range(steps):
        a = t0 + (t1 - t0) * k / steps
        b = t0 + (t1 - t0) * (k + 1) / steps
        fc = f0 * (f1 / f0) ** ((k + 0.5) / steps)
        seg = band(fc * 0.6, fc * 1.6, seed + k)
        w = np.clip(1 - np.abs((t - (a + b) / 2) / (b - a)), 0, 1)
        out += seg * w
    return out


L = np.zeros(n)
R = np.zeros(n)
# bed: drone with slow beating (the loop point is hidden under the boom on frame 0)
for f, a in [(41.2, 0.28), (61.7, 0.12), (82.4, 0.08), (123.5, 0.03)]:
    for det, pan in [(-0.06, 0.35), (0.06, 0.65)]:
        s = a * np.sin(2 * np.pi * (f + det) * t + rng.uniform(0, 6))
        L += s * (1 - pan)
        R += s * pan
wl, wr = band(150, 1500, 1), band(150, 1500, 2)
L += 0.06 * wl
R += 0.06 * wr

ends = cfg["emerges"][1:] + [DUR]
for k, (d0, d1) in enumerate(zip(cfg["dives"], ends)):
    # whoosh: accelerating, rising, peaking at the black frame
    env = np.clip((t - d0) / (d1 - d0), 0, 1) ** 2.2 * (t < d1)
    wh = sweep_noise(d0, d1, 250, 4000, 100 + 20 * k)
    L += 0.55 * env * wh
    R += 0.55 * env * np.roll(wh, 90)
    ph = 2 * np.pi * np.cumsum(60 * (1 + 5 * np.clip((t - d0) / (d1 - d0), 0, 1) ** 2)) / SR
    riser = 0.12 * env * np.sin(ph)
    L += riser
    R += riser
# boom + airy release on every emerge (frame 0 included, which is where the last dive lands)
for k, e0 in enumerate(cfg["emerges"]):
    te = np.clip(t - e0, 0, None)
    on = t >= e0
    boom = on * 0.75 * np.sin(2 * np.pi * (34 - 2 * k) * te + 6 * (1 - np.exp(-te / 0.05))) * np.exp(-te / 1.1) * (1 - np.exp(-te / 0.004))
    air = on * 0.10 * band(2000, 9000, 300 + k) * np.exp(-te / 0.5)
    L += boom + air
    R += boom + np.roll(air, 60)

peak = max(np.abs(L).max(), np.abs(R).max())
st = np.tanh(np.stack([L, R], 1) / peak * 1.3) * 0.72
with wave.open(sys.argv[2], "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
