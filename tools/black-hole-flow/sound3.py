"""Calm, fully synthesised sound bed for the Google Flow black hole cut (no samples, nothing to credit).

usage: sound3.py out.wav DURATION CUT1,CUT2,...
Layers: a deep drone with slow beating, a breathing filtered-noise 'wind', drifting glass
partials, a soft sub swell on frame 0 and a gentle rise into the loop point.
The tail is crossfaded into the head so the loop is seamless.
"""
import sys
import wave
import numpy as np

out, DUR = sys.argv[1], float(sys.argv[2])
SR = 48000
X = 1.5                                  # loop crossfade length (s)
n = int((DUR + X) * SR)
t = np.arange(n) / SR
rng = np.random.default_rng(3)


def bandnoise(lo, hi, seed):
    r = np.random.default_rng(seed)
    spec = np.fft.rfft(r.standard_normal(n))
    f = np.fft.rfftfreq(n, 1 / SR)
    spec *= ((f > lo) & (f < hi)) * (1 / np.maximum(f, 1)) ** 0.5
    y = np.fft.irfft(spec, n)
    return y / np.abs(y).max()


L = np.zeros(n)
R = np.zeros(n)
# drone: A1 + E2 + A2, each with slightly detuned twins (slow beating)
for f, a in [(55.0, 0.30), (82.4, 0.14), (110.0, 0.10), (164.8, 0.04)]:
    for det, pan in [(-0.07, 0.35), (0.07, 0.65)]:
        ph = rng.uniform(0, 2 * np.pi)
        s = a * np.sin(2 * np.pi * (f + det) * t + ph + 0.4 * np.sin(2 * np.pi * 0.05 * t))
        L += s * (1 - pan)
        R += s * pan
# breathing space wind
wl, wr = bandnoise(180, 1800, 1), bandnoise(180, 1800, 2)
breath = 0.55 + 0.45 * np.sin(2 * np.pi * t / 9.0 - np.pi / 2)
L += 0.10 * wl * breath
R += 0.10 * wr * breath
# glass partials: slow fades, drifting pan
for k, f in enumerate([880.0, 1318.5, 1760.0, 2217.5, 2637.0]):
    ph = rng.uniform(0, 2 * np.pi)
    env = np.clip(np.sin(2 * np.pi * t / rng.uniform(7, 13) + ph), 0, 1) ** 3
    s = 0.018 * env * np.sin(2 * np.pi * f * t + rng.uniform(0, 6))
    pan = 0.5 + 0.4 * np.sin(2 * np.pi * t / 11 + k)
    L += s * (1 - pan)
    R += s * pan
# gentle rise over the last seconds (falling deeper)
rise = np.clip((t - (DUR - 6)) / 6, 0, 1) ** 2 * (t < DUR + 0.01)
riser = 0.10 * rise * bandnoise(300, 5000, 9)
L += riser
R += riser * 0.9

# loop: the extra X seconds at the end are crossfaded into the head
def looped(x):
    y = x[:int(DUR * SR)].copy()
    m = int(X * SR)
    w = np.linspace(0, 1, m)
    y[:m] = y[:m] * np.sqrt(w) + x[int(DUR * SR):int(DUR * SR) + m] * np.sqrt(1 - w)
    return y


L, R = looped(L), looped(R)
# soft sub swell on frame 0 (added after looping so the crossfade cannot mute it)
tt = t[:len(L)]
sub = 0.55 * np.sin(2 * np.pi * 38 * tt) * np.exp(-tt / 1.6) * (1 - np.exp(-tt / 0.01))
L += sub
R += sub
# a soft sub swell on every cut, each a little deeper than the last
for k, tcut in enumerate(float(x) for x in sys.argv[3].split(",")):
    tc = np.clip(tt - tcut, 0, None)
    f0 = 36.0 - 2.0 * k
    hit = (tt >= tcut) * (0.35 + 0.05 * k) * np.sin(2 * np.pi * f0 * tc) * np.exp(-tc / 1.5) * (1 - np.exp(-tc / 0.008))
    L += hit
    R += hit
peak = max(np.abs(L).max(), np.abs(R).max())
g = 0.70 / peak
st = np.stack([L * g, R * g], 1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open(out, "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
