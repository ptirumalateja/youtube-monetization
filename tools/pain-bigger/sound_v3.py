"""SFX-only sound (no music) for "Everyone feels their own pain is bigger" (numpy only).
Sad string pad on the ref's progression Fm -> Db -> Ab -> Eb/G, soft sobs,
tear drips, and the blood-on-title hit at ~5.85-6.2 s. Times mirror scene.html.
Usage: python3 sound.py out.wav"""
import sys, wave
import numpy as np

SR = 44100
DUR = 11.42
N = int(DUR * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)


def tt(d): return np.arange(int(d * SR)) / SR


def place(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    n = min(len(sig), N - i)
    L[i:i + n] += sig[:n] * gain * np.sqrt(0.5 * (1 - pan))
    R[i:i + n] += sig[:n] * gain * np.sqrt(0.5 * (1 + pan))


def bandnoise(n, lo, hi):
    X = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)


def hz(name):
    names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    n, o = name[:-1], int(name[-1])
    return 440 * 2 ** ((names.index(n) + 12 * (o + 1) - 69) / 12)


def string_note(f, d, amp=1.0):
    t = tt(d)
    out = np.zeros(len(t))
    for v, det in enumerate([-0.004, 0.0, 0.005]):
        vib = 1 + 0.0035 * np.sin(2 * np.pi * (5.2 + v * 0.4) * t + rng.random() * 6)
        ph = 2 * np.pi * np.cumsum(f * (1 + det) * vib) / SR
        for k in range(1, 10):
            if f * k > 5000: break
            out += np.sin(k * ph + rng.random() * 6) / k ** 1.25
    return out * amp


CHORDS = [  # start, end, notes (gain)
    (0.0, 3.05, [('F2', .7), ('F3', 1.0), ('G#3', .5), ('C4', .55), ('F4', .5), ('G#4', .4), ('C5', .45), ('D#5', .3), ('G#5', .25)]),
    (2.85, 6.0, [('C#2', .6), ('C#3', 1.0), ('G#3', .8), ('C#4', .7), ('F4', .4), ('G#4', .6), ('A#4', .6), ('D#5', .35), ('F5', .3), ('A#5', .3)]),
    (5.85, 10.65, [('G#1', .6), ('G#2', .6), ('D#3', .55), ('G#3', 1.0), ('D#4', .45), ('G#4', .5), ('C5', .4), ('D#5', .35), ('G#5', .3), ('C6', .25)]),
    (10.5, DUR, [('G2', .5), ('G3', .9), ('A#3', .5), ('D#4', .6), ('G4', .8), ('G#4', .5), ('C5', .3), ('D#5', .4), ('A#5', .3)]),
]
pad = np.zeros(N)
for a, b, notes in CHORDS:
    d = b - a
    t = tt(d)
    env = np.minimum(1, t / (0.05 if a == 0 else 0.35)) * np.minimum(1, (d - t) / 0.3)
    seg = sum(string_note(hz(n), d, g) for n, g in notes) * env
    i = int(a * SR); pad[i:i + len(seg)] += seg[:N - i]
# gentle lowpass via FFT tilt
X = np.fft.rfft(pad); f = np.fft.rfftfreq(N, 1 / SR)
X *= 1 / (1 + (f / 2200) ** 2)
pad = np.fft.irfft(X, N)
# bow swell: slow tremolo-ish breathing
swell = 0.85 + 0.15 * np.sin(2 * np.pi * np.arange(N) / SR / 2.9)
pad *= swell
pad /= np.abs(pad).max()
# no music (Teja's rule): SFX only. The pad is built but not placed.


def sniff(d=0.32, hi=7000):
    t = tt(d); n = len(t)
    return bandnoise(n, 1800, hi) * np.sin(np.pi * t / d) ** 1.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 18 * t))


def sob(d=0.45):
    t = tt(d); n = len(t)
    breath = bandnoise(n, 400, 3500) * np.sin(np.pi * t / d) ** 2
    hitch = np.exp(-((t - d * 0.3) / 0.03) ** 2) * bandnoise(n, 900, 2500)
    return breath * 0.7 + hitch * 0.8


def drip(f=1500):
    t = tt(0.25)
    fr = f * (1 + 0.8 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / 0.045) * np.minimum(1, t / 0.002)


def splat(big=1.0):
    t = tt(0.4)
    n = bandnoise(len(t), 250, 6000) * np.exp(-t / (0.04 * big))
    thump = np.sin(2 * np.pi * (110 * np.exp(-t * 9) + 45) * t) * np.exp(-t / 0.1) * big
    return 0.6 * n + 0.8 * thump


def whoosh(d, lo, hi):
    t = tt(d); n = len(t)
    return bandnoise(n, lo, hi) * (t / d) ** 2 * np.exp(-((t - d) / 0.05) ** 2 * 0) * np.minimum(1, (d - t) / 0.03 + 0.0)


# sobs / sniffles on B's shaking (period ~0.92 s), like the ref's soft transients
for i, tm in enumerate([0.38, 0.95, 1.62, 2.3, 3.0, 3.42, 3.88, 4.55, 5.2, 6.7, 7.4, 8.25, 9.0, 9.75, 10.5]):
    if i % 3 == 1:
        place(sniff(), tm, 0.22, 0.25)
    else:
        place(sob(), tm, 0.16, 0.2)
# tear drops landing (scene: k*0.675 offsets of a 1.35 s cycle)
for n in range(0, 18):
    tm = 0.675 * n
    if 0.2 < tm < DUR:
        place(drip(1400 + 300 * (n % 3)), tm, 0.07, 0.35)
# blood drips into the pool (period 1.6, offsets 0.53)
for k in range(3):
    for m in range(8):
        tm = 1.6 * m + (1.6 - 0.53 * k) % 1.6
        if tm < DUR: place(drip(520 + 60 * k), tm, 0.045, -0.4)
# v3: wet spurt from his back at 5.62 s (the spray that flies up to the title)
t = tt(0.5)
sq = bandnoise(len(t), 300, 4500) * np.exp(-t / 0.09) * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * t))
sq += 0.6 * np.sin(2 * np.pi * (260 * np.exp(-t * 6) + 90) * t) * np.exp(-t / 0.08)
place(sq, 5.62, 0.35, -0.4)
# the blood-on-title hit: dark rising whoosh into a low boom at 5.85, splats 6.0-6.22
place(whoosh(0.5, 150, 2500), 5.35, 0.25)
t = tt(2.5)
boom = np.sin(2 * np.pi * (70 * np.exp(-t * 3) + 38) * t) * np.exp(-t / 0.6)
place(boom, 5.85, 0.55)
for x, th in [(-.5, 6.02), (0.0, 6.10), (0.1, 6.0), (0.6, 6.16), (-0.3, 6.08), (0.3, 6.22)]:
    place(splat(0.8), th, 0.22, x)

# airy room bed (the ref has a soft hiss/air layer up to ~17 kHz)
air = bandnoise(N, 2500, 16000) * (0.7 + 0.3 * np.sin(2 * np.pi * np.arange(N) / SR / 1.7))
place(air, 0, 0.005, -0.2); place(np.roll(air, 9000), 0, 0.005, 0.2)

# reverb: exponential noise IR
ir_t = tt(2.2)
ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t / 0.55); ir[0] = 0
def conv(x):
    n = len(x) + len(ir)
    return np.fft.irfft(np.fft.rfft(x, n) * np.fft.rfft(ir, n), n)[:len(x)]
wetL, wetR = conv(L), conv(R[::-1])[::-1] * 0 + conv(R)
L2 = L + 0.012 * wetL; R2 = R + 0.012 * wetR
# end fade with the picture (10.92 -> 11.42)
tt_all = np.arange(N) / SR
g = np.clip((11.42 - tt_all) / 0.5, 0, 1)
L2 *= g; R2 *= g
m = max(np.abs(L2).max(), np.abs(R2).max())
L2 *= 0.7 / m; R2 *= 0.7 / m
out = np.stack([L2, R2], 1)
with wave.open(sys.argv[1], 'w') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((out * 32767).astype(np.int16).tobytes())
print('ok', DUR)
