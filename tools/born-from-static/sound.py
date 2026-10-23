"""Synthesised sound for Born From Static (no samples, so no licences).

The audio does what the picture does: static hiss is stripped away step by step
until only a chord is left, then the chord is buried in hiss again.

    python3 sound.py OUT.wav
"""
import sys
import wave
import numpy as np
from scipy.signal import butter, sosfilt

import timeline as tl
from render import CAPTIONS

SR = 48000
N = int(tl.DUR * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)


def env_from(fn):
    """Sample a per-time function at 1 kHz and interpolate (fast enough, keeps steps sharp)."""
    tk = np.arange(0, tl.DUR + 0.001, 0.001)
    v = np.array([fn(x) for x in tk])
    return np.interp(t, tk, v)


def bp(x, lo, hi, order=2):
    return sosfilt(butter(order, [lo, hi], "bandpass", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "highpass", fs=SR, output="sos"), x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "lowpass", fs=SR, output="sos"), x)


def smooth(x, ms):
    k = max(1, int(SR * ms / 1000))
    return np.convolve(x, np.ones(k) / k, mode="same")


def place(buf, sig, at):
    i = int(at * SR)
    j = min(N, i + len(sig))
    if i < N:
        buf[i:j] += sig[: j - i]


s = smooth(env_from(tl.signal_at), 6)        # signal fraction, steps softened by 6 ms
n = np.sqrt(np.clip(1 - s * s, 0, 1))

# ducking for the held breath before the reveal
duck = np.ones(N)
b0, b1 = tl.BREATH
m = (t >= b0) & (t < tl.REVEAL - 0.04)
duck[m] = 1 - 0.97 * np.clip((t[m] - b0) / 0.12, 0, 1)
duck[(t >= tl.REVEAL - 0.04) & (t < tl.REVEAL)] = 0.0
duck = smooth(duck, 4)

# ---- static bus -------------------------------------------------------------
white = rng.standard_normal(N)
hiss = 0.55 * hp(white, 1200) + 0.25 * bp(white, 250, 1200) + 0.2 * lp(white, 250)
# crackle: sparse clicks, denser when there's more noise
clicks = (rng.uniform(0, 1, N) < 0.004) * rng.standard_normal(N) * 3
clicks = hp(clicks, 2000)
static = (hiss * 0.5 + clicks * 0.35) * n ** 1.3 * duck

# ---- pad bus: D major add9, additive saws whose brightness opens with the signal --
notes = [73.42, 146.83, 220.0, 293.66, 369.99, 440.0, 659.26]
gains = [0.5, 0.8, 0.7, 0.7, 0.55, 0.45, 0.3]
cut = 250 + 5200 * s ** 2
pad = np.zeros(N)
for f, g in zip(notes, gains):
    for det in (-0.12, 0.0, 0.11):
        ff = f * (1 + det / 100 * (1 + 6 * n))   # wider detune (sourer) while it's noisy
        phase = 2 * np.pi * np.cumsum(ff) / SR + rng.uniform(0, 2 * np.pi)
        for h in range(1, 9):
            if f * h > 9000:
                break
            a = g / h / (1 + (f * h / cut) ** 4)
            pad += a * np.sin(h * phase)
pad /= np.abs(pad).max()
# tones from noise: narrow bands of the hiss at the chord notes, loudest mid-way
res = sum(bp(white, f * 0.985, f * 1.015) for f in notes[2:]) * 14
pad_bus = (pad * s ** 1.6 * 0.6 + res * (4 * s * n) * 0.12) * duck
pad_bus = hp(pad_bus, 60)

# ---- step ticks -------------------------------------------------------------
ticks = np.zeros(N)
for k, at in enumerate(tl.step_times()[:-1], start=1):
    L = int(0.03 * SR)
    tt = np.arange(L) / SR
    f = 1500 * 2 ** (k / 50)
    blip = np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.006)
    place(ticks, blip * 0.22, at)

# ---- typing clicks for the captions -----------------------------------------
typing = np.zeros(N)
for t0, t1, lines, size, cps in CAPTIONS:
    total = sum(len(x) for x in lines) - (8 if t0 == 0.0 else 1)
    for i in range(total):
        at = t0 + (i + 1) / cps
        if at >= t1:
            break
        L = int(0.012 * SR)
        c = hp(rng.standard_normal(L), 3000) * np.exp(-np.arange(L) / SR / 0.002)
        place(typing, c * 0.12, at)
typing *= duck

# ---- hits -------------------------------------------------------------------
def hit(size, dur):
    L = int(dur * SR)
    tt = np.arange(L) / SR
    crack = hp(rng.standard_normal(L), 2500) * np.exp(-tt / 0.012) * 0.9
    f = 70 + 250 * np.exp(-tt / 0.09)
    body = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-tt / (0.35 * size))
    sub = np.sin(2 * np.pi * 48 * tt) * np.exp(-tt / (0.5 * size)) * 0.35
    return (crack + body * 0.8 + sub) * size


hits = np.zeros(N)
place(hits, hit(0.55, 1.0), 0.0)
big = hit(1.0, 2.6)
L = len(big)
tt = np.arange(L) / SR
gong = sum(np.sin(2 * np.pi * f * tt) * a for f, a in [(146.8, 0.35), (293.7, 0.25), (412, 0.15), (603, 0.12), (871, 0.08)])
bell = sum(np.sin(2 * np.pi * f * tt) * a for f, a in [(1174.7, 0.08), (1760, 0.05), (2349, 0.03)])
big = big + gong * np.exp(-tt / 1.4) + bell * np.exp(-tt / 2.2)
place(hits, big, tl.REVEAL)
# reverse "suck" into the reveal
L = int(0.42 * SR)
tt = np.arange(L) / SR
suck = bp(rng.standard_normal(L), 300, 6000) * (tt / tt[-1]) ** 3 * 0.5
place(hits, suck, tl.REVEAL - 0.04 - 0.42)

# ---- loop riser: hiss sweeps up into frame 0 -----------------------------------
riser = np.zeros(N)
L = int(1.3 * SR)
sw = rng.standard_normal(L)
sweep = np.concatenate([bp(sw[i:i + L // 13], 400 + 4000 * (i / L) ** 2, 800 + 7000 * (i / L) ** 2) for i in range(0, L - L // 13 + 1, L // 13)])
sweep *= np.linspace(0, 1, len(sweep)) ** 2 * 0.45
place(riser, sweep, tl.DUR - len(sweep) / SR)

# ---- mix --------------------------------------------------------------------
mix = static * 0.55 + pad_bus * 1.3 + ticks + typing + riser
mix = hp(mix, 90)                       # phones can't play lower; sub lives on the hit bus only
mix += hits * 1.3
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
mix /= np.abs(mix).max() / 0.89
# short crossfade at the loop point so end -> start has no click
F = int(0.01 * SR)
mix[-F:] *= np.linspace(1, 0, F)
mix[:F] *= np.linspace(0, 1, F)

st = np.stack([mix, mix], 1)
# a touch of width on the static and pad
st[:, 0] += 0.08 * np.roll(pad_bus + static, 240)
st[:, 1] -= 0.08 * np.roll(pad_bus + static, 240)
st /= np.abs(st).max() / 0.89
out = sys.argv[1] if len(sys.argv) > 1 else "sound.wav"
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((st * 32767).astype(np.int16).tobytes())
print("wrote", out)
