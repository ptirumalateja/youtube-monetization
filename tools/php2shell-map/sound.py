"""Synthesised sound design for the PHP2Shell reel (no samples, so no licences to track).

usage: python3 sound.py OUT.wav
Cue sheet (s): 0.0 hit + first ping | 0-2.3 typing ticks, beacon pings | 1.2-8.5 ping crackle grows
with the spread | 2.7-4.4 and 5.4-7.9 counter ticks | 6.6-8.5 riser | 8.5-9.0 held breath
| 9.0 biggest hit, 9.65 second hit | 11.2, 13.0 glitch stutters | 14.2-15.0 reverse swell into frame 0.
"""
import sys, math
import numpy as np
from timeline import *
import render as R

SR = 48000
N = int(DUR * SR)
rng = np.random.default_rng(5)
tt = np.arange(N) / SR


def buf():
    return np.zeros((N, 2), np.float32)


def place(b, sig, t0, pan=0.0, gain=1.0):
    i0 = int(t0 * SR)
    if sig.ndim == 1:
        l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
        sig = np.stack([sig * l * 1.414, sig * r * 1.414], 1)
    n = min(len(sig), N - i0)
    if n > 0 and i0 >= 0:
        b[i0:i0 + n] += sig[:n] * gain
    # wrap overflow to the start so tails continue across the loop
    if len(sig) > N - i0 and i0 >= 0:
        rest = sig[N - i0:]
        b[:len(rest)] += rest[: N] * gain


def lp_fast(x, fc, order=2):
    # FFT brick-ish lowpass with smooth rolloff (fast for long buffers)
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / fc) ** (2 * order))
    return np.fft.irfft(X, len(x)).astype(np.float32)


def hp_fast(x, fc, order=2):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 - 1 / (1 + (f / max(fc, 1)) ** (2 * order))
    return np.fft.irfft(X, len(x)).astype(np.float32)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def hit(size=1.0):
    n = int(2.6 * SR)
    t = np.arange(n) / SR
    crack = hp_fast(rng.normal(0, 1, n).astype(np.float32), 2500) * np.exp(-t / 0.012) * 0.9
    f = 60 + (320 - 60) * np.exp(-t / 0.09)
    body = np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t / 0.35) * 0.9
    sub = np.sin(2 * np.pi * 45 * t) * np.exp(-t / 0.7) * 0.6 * np.minimum(1, t / 0.005)
    gong = sum(np.sin(2 * np.pi * fr * t + k) * np.exp(-t / (0.9 / (k + 1))) * 0.12 for k, fr in enumerate([181, 293, 447, 612]))
    noise = lp_fast(rng.normal(0, 1, n).astype(np.float32), 900) * np.exp(-t / 0.5) * 0.35
    s = (crack + body + sub + gong + noise) * size
    # stereo tail decorrelation
    d = int(0.011 * SR)
    st = np.stack([s, np.r_[np.zeros(d), s[:-d]] * 0.92 + s * 0.08], 1)
    return st.astype(np.float32)


def blip(freq, dur=0.05, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(2 * np.pi * freq * 2.01 * t)
    return (s * np.minimum(1, t / 0.002) * np.exp(-t / (dur / 4)) * amp).astype(np.float32)


def tick(freq=3000, amp=1.0):
    n = int(0.012 * SR)
    t = np.arange(n) / SR
    s = rng.normal(0, 1, n) * 0.5 + np.sin(2 * np.pi * freq * t)
    return (s * np.exp(-t / 0.0025) * amp).astype(np.float32)


def glitch(dur=0.14, amp=0.5):
    n = int(dur * SR)
    x = rng.normal(0, 1, n)
    # sample-and-hold bitcrush with random stutter rate
    hold = rng.integers(20, 180)
    x = np.repeat(x[::hold], hold)[:n]
    x = np.round(x * 3) / 3
    gate = (np.sin(2 * np.pi * rng.uniform(25, 60) * np.arange(n) / SR) > 0).astype(float)
    return (hp_fast(x.astype(np.float32), 400) * gate * np.exp(-np.arange(n) / SR / (dur / 2)) * amp).astype(np.float32)


hits, sfx, bed, pings = buf(), buf(), buf(), buf()

# ---- bed: dark drone that thickens with the spread ----
lvl = np.array([spread_level(x) if x < WHO else max(0.0, 1 - (x - WHO) / 1.6) for x in tt[::480]])
lvl = np.interp(tt, tt[::480], lvl).astype(np.float32)
drone = np.zeros(N, np.float32)
for fr, a in ((55, 0.5), (55.4, 0.4), (110.3, 0.35), (164.8, 0.2), (82.6, 0.3)):
    ph = 2 * np.pi * fr * tt
    drone += (2 * ((ph / (2 * np.pi)) % 1) - 1) * a  # saw
drone = lp_fast(drone, 420) * (0.35 + 0.65 * lvl)
hum = lp_fast(hp_fast(rng.normal(0, 1, N).astype(np.float32), 150), 1400) * (0.05 + 0.18 * lvl)
pulse = (0.5 + 0.5 * np.sin(2 * np.pi * tt / 1.5 - np.pi / 2)) ** 6  # beacon throb, 1.5 s like the ring
throb = np.sin(2 * np.pi * 98 * tt) * pulse * 0.25
b = drone * 0.5 + hum + throb
# breath: duck everything 8.5-9.0
duck = np.ones(N, np.float32)
m = (tt >= BREATH) & (tt < HIT)
duck[m] = 0.03
ramp = (tt >= BREATH - 0.08) & (tt < BREATH)
duck[ramp] = np.linspace(1, 0.03, ramp.sum())
bed[:, 0] = b * duck
bed[:, 1] = np.r_[b[7:], b[:7]] * duck

# ---- riser into the breath ----
n = int((BREATH - 6.6) * SR)
t = np.arange(n) / SR
x = t / t[-1]
f = 180 * (2 ** (x * 2.6))
riser = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.25 + hp_fast(rng.normal(0, 1, n).astype(np.float32), 2000) * 0.25 * x
riser *= x ** 2
place(sfx, riser.astype(np.float32), 6.6, 0, 0.7)

# ---- hits ----
place(hits, hit(0.55), HOOK)
place(hits, hit(1.0), HIT)
place(hits, hit(0.55), HIT2)
# reverse swell into frame 0 so the loop is audible
n = int(0.75 * SR)
t = np.arange(n) / SR
place(sfx, lp_fast(rng.normal(0, 1, n).astype(np.float32), 3000) * (t / t[-1]) ** 3, DUR - 0.75, 0, 0.5)

# ---- pings: every host lighting up makes a blip; dense moments become crackle ----
order = np.argsort(R.TI)
last = -1
for i in order:
    ti = R.TI[i]
    if ti >= BREATH or (ti < 0.05 and i != R.FIRST):
        continue
    if ti - last < 0.012:
        continue
    last = ti
    tx = R.cam_at(ti)[0]
    pan = float(np.clip(((R.HOSTS[i, 0] - tx + 180) % 360 - 180) / 90, -1, 1)) * 0.8
    dens = spread_level(ti)
    fr = rng.uniform(1300, 2600) * (0.8 if i == R.FIRST else 1)
    place(pings, blip(fr, 0.06 if dens < 0.2 else 0.03, 0.35 * (1 - 0.6 * dens)), ti, pan)
# beacon pings for the first attack (hook and loop tail), synced to the 1.5 s ring
for tb in list(np.arange(0.0, SPREAD, 1.5)) + list(np.arange(WHO + 1.0 + (1.5 - (WHO + 1.0) % 1.5) % 1.5, DUR, 1.5)):
    place(pings, blip(880, 0.5, 0.45), tb, -0.2)
# arcs: soft whoosh-chirps
for (p, c) in R.ARCS[::2]:
    t0 = R.TI[c] - R.ARC_DUR
    n = int(R.ARC_DUR * SR)
    t = np.arange(n) / SR
    fch = 600 + 1800 * t / t[-1]
    s = np.sin(2 * np.pi * np.cumsum(fch) / SR) * np.sin(np.pi * t / t[-1]) ** 2 * 0.06
    place(pings, s.astype(np.float32), t0, rng.uniform(-0.6, 0.6))

# ---- typing and counter ticks ----
def typing(t0, nchars, cps):
    for k in range(nchars):
        place(sfx, tick(rng.uniform(2500, 4200), 0.22), t0 + k / cps, rng.uniform(-0.3, 0.3))

typing(0.0, 12, 30); typing(0.40, 13, 30); typing(0.95, 26, 48); typing(1.15, 26, 48)
typing(PHP, 14, 34); typing(PHP + 0.35, 4, 20)
typing(HOSTS, 11, 34); typing(HOSTS + 0.3, 10, 30)
typing(SINCE, 13, 34); typing(SINCE + 0.3, 11, 30); typing(SINCE + 0.5, 36, 60)
typing(WHO + 0.05, 6, 24); typing(WHO + 0.35, 5, 20)
for t0, t1, f0, f1 in ((PHP + 0.3, PHP + 2.0, 900, 1800), (HOSTS + 0.2, HOSTS + 2.7, 900, 2400)):
    k = 0
    tk = t0
    while tk < t1:
        x = (tk - t0) / (t1 - t0)
        place(sfx, blip(f0 + (f1 - f0) * x, 0.02, 0.16), tk, 0)
        tk += 0.07 - 0.04 * x
for tg in (2.3, HOSTS - 0.05, SINCE - 0.05, WHO - 0.05):
    place(sfx, glitch(0.14, 0.35), tg, rng.uniform(-0.4, 0.4))

# ---- mix ----
# breath: silence pings/sfx too
for bb in (pings, sfx):
    bb[(tt >= BREATH) & (tt < HIT)] *= 0.0
mix = hits * 1.0 + sfx * 0.9 + pings * 0.8 + bed * 0.55
# sidechain duck under the big hits
for th, depth in ((HIT, 0.6), (HIT2, 0.35), (HOOK, 0.3)):
    m = (tt >= th) & (tt < th + 0.6)
    g = 1 - depth * np.exp(-(tt[m] - th) / 0.18)
    mix[m] = hits[m] + (mix[m] - hits[m]) * g[:, None]
# high-pass everything except the hit bus sub at 35 Hz (rumble), keep weight in 90-400 Hz
for ch in range(2):
    mix[:, ch] = hp_fast(mix[:, ch], 32)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.abs(mix).max() / 0.89
import wave
out = sys.argv[1]
with wave.open(out, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype("<i2").tobytes())
print("wrote", out)
