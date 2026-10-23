"""Alien Perspective sound: synth layers + CC0 Freesound files from tools/sfxlib. python3 sound.py out.wav
CC0 files (no credit needed): qubodup explosion-from-another-dimension, lucabia sword-in-air,
AudioPapkin cinematic-woosh-sfx-015, stewdio2003 cp_subby_whoosh, sleepCircle wind.
Everything is placed on a circular 12 s buffer so tails wrap and the loop is seamless.
Contrast: crickets + wind on Earth, alien drone + heartbeat in the eye, riser + ticks on the beam,
a held breath at 8.0-8.55 s, the biggest hit at 8.6 s, bell + warm pad for today."""
import sys
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000; DUR = 12.0; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)
LIB = __file__.rsplit('/', 2)[0] + '/sfxlib/'
T_EYE, T_BEAM, T_REVEAL, T_FLIP = 2.3, 4.6, 8.6, 10.0


def load(name):
    x, sr = sf.read(LIB + name); x = x if x.ndim == 1 else x.mean(1)
    if sr != SR: x = signal.resample_poly(x, SR, sr)
    return x / (np.abs(x).max() + 1e-9)
def bp(x, lo, hi, o=2): return signal.sosfilt(signal.butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def env(pts): ts, vs = zip(*pts); return np.interp(t, ts, vs)
def fade(x, a=0.005, r=0.05):
    x = x.copy(); na, nr = max(1, int(a * SR)), max(1, int(r * SR)); x[:na] *= np.linspace(0, 1, na); x[-nr:] *= np.linspace(1, 0, nr); return x
def place(bus, x, at, g=1.0):
    """circular placement: anything past 12 s wraps to the start (seamless loop)."""
    i = int(round(at * SR)) % N
    idx = (i + np.arange(len(x))) % N
    np.add.at(bus, idx, g * x)


hit, sfx, bed, tone = (np.zeros(N) for _ in range(4))
expl = load('814046__qubodup__explosion-from-another-dimension.wav')
sword = load('276871__lucabia__sword-in-air.wav')
woosh = load('649445__audiopapkin__cinematic-woosh-sfx-015.wav')
subby = load('238375__stewdio2003__cp_subby_whoosh.aiff')
wind = load('22331__sleepcircle__wind.ogg')


def boom(f0=170, f1=48, dur=1.8, crack=0.6, sub=0.8, drive=2.5):
    n = int(dur * SR); k = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-k / 0.07)
    body = np.tanh(drive * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-k / 0.42)
    return body + hp(rng.standard_normal(n), 2500) * np.exp(-k / 0.016) * crack + np.sin(2 * np.pi * 46 * k) * np.exp(-k / 0.8) * sub


def gong(f0=98, dur=3.5):
    n = int(dur * SR); k = np.arange(n) / SR; x = np.zeros(n)
    for r, a, d in ((1, 1, 2.2), (2.01, .5, 1.6), (2.76, .45, 1.3), (4.07, .3, .9), (5.4, .2, .6)):
        x += a * np.sin(2 * np.pi * f0 * r * k + rng.uniform(0, 6)) * np.exp(-k / d)
    return x * (1 - np.exp(-k / 0.004))


def swell(dur=0.6, lo=300, hi=5000):   # reversed-noise suck into a hit
    n = int(dur * SR); k = np.linspace(0, 1, n)
    x = bp(rng.standard_normal(n), lo, hi) * k ** 3
    return x / np.abs(x).max()


def bell(f0, dur=2.5):
    n = int(dur * SR); k = np.arange(n) / SR; x = np.zeros(n)
    for r, a, d in ((1, 1, 1.6), (2.0, .35, 1.0), (2.76, .3, .7), (5.4, .12, .4)):
        x += a * np.sin(2 * np.pi * f0 * r * k) * np.exp(-k / d)
    return x * (1 - np.exp(-k / 0.002))


# ---------------------------------------------------------------- Earth: crickets + wind (0-2.3 and 8.6-12)
earth_g = env([(0, .9), (2.2, .9), (2.32, 0), (T_REVEAL + 0.25, 0), (T_REVEAL + 0.9, .9), (12, .9)])
cr = np.zeros(N)
for v in range(5):
    f = rng.uniform(4200, 5200); per = rng.uniform(0.55, 0.9); ph = rng.uniform(0, per)
    gate = ((t + ph) % per < 0.16).astype(float) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 32 * t)))
    cr += np.sin(2 * np.pi * f * t) * lp(gate, 300) * rng.uniform(.3, .6)
w = np.tile(wind, int(np.ceil(N / len(wind))) + 1)[int(3 * SR):int(3 * SR) + N]
bed += (0.10 * cr + 0.55 * hp(w, 120)) * earth_g

# ---------------------------------------------------------------- frame 0 hit (loop) + reveal hit (biggest)
place(hit, boom(160, 50, 1.6, 0.55, 0.6) * 0.75, 0.0)
place(hit, expl[: int(1.2 * SR)] * np.exp(-np.arange(int(1.2 * SR)) / SR / 0.35), 0.0, 0.35)
place(sfx, swell(0.55), 12.0 - 0.55, 0.45)                     # suck back into frame 0
place(tone, fade(np.sin(2 * np.pi * np.cumsum(np.linspace(180, 420, int(0.5 * SR))) / SR) * np.linspace(0, 1, int(0.5 * SR)) ** 2), 11.5, 0.12)

big = boom(190, 44, 2.6, 0.9, 1.0, 3.2)
place(hit, big, T_REVEAL, 1.0)
place(hit, expl[: int(2.4 * SR)] * np.exp(-np.arange(int(2.4 * SR)) / SR / 0.7), T_REVEAL, 0.6)
place(hit, gong(92), T_REVEAL, 0.32)
place(hit, lp(rng.standard_normal(int(2.6 * SR)), 120) * np.exp(-np.arange(int(2.6 * SR)) / SR / 0.9) * 4, T_REVEAL, 0.5)  # sub wall
place(sfx, swell(0.12, 800, 8000), T_REVEAL - 0.17, 0.5)

# ---------------------------------------------------------------- eye: snap, alien drone, heartbeat
place(sfx, sword, T_EYE - 0.12, 0.6)
place(hit, boom(120, 45, 0.7, 0.3, 0.5) * 0.6, T_EYE)
eye_g = env([(0, 0), (T_EYE, 0), (T_EYE + 0.05, 1), (T_BEAM - 0.2, 1.3), (T_BEAM, 0), (12, 0)])
drone = sum(signal.sawtooth(2 * np.pi * f * t) for f in (55, 55.6, 110.3, 164.6))
drone = lp(drone, 700) * (1 + 0.3 * np.sin(2 * np.pi * 0.8 * t))
fz = np.interp(t, [T_EYE, T_BEAM], [380, 900])
whine = np.sin(2 * np.pi * np.cumsum(fz) / SR) * (1 + 0.5 * np.sin(2 * np.pi * 6 * t))
tone += (0.10 * drone + 0.035 * whine) * eye_g
for at in (2.55, 3.15, 3.65, 4.05, 4.35):
    place(hit, boom(75, 45, 0.35, 0.0, 0.6, 1.5) * 0.55, at)
place(sfx, swell(0.4), T_BEAM - 0.4, 0.5)
place(sfx, woosh, T_BEAM - 0.05, 0.55)

# ---------------------------------------------------------------- beam: riser, ticks, pane passes, pings
riser_g = env([(0, 0), (T_BEAM, 0), (T_BEAM + 0.1, .35), (7.75, 1.0), (7.98, 1.0), (8.02, 0), (12, 0)])
fr = np.exp(np.interp(t, [T_BEAM, 8.0], [np.log(110), np.log(440)]))
ris = sum(np.sin(2 * np.pi * np.cumsum(fr * m) / SR) / m for m in (1, 1.5, 2, 3))
ris += 0.5 * bp(rng.standard_normal(N), 1500, 6000) * np.interp(t, [T_BEAM, 8.0], [0.05, 0.6])
tone += hp(ris, 90) * riser_g * 0.13
for a, b in ((5.5, 5.85), (6.4, 6.75), (7.3, 7.75)):        # odometer rolling
    for k in np.arange(a, b, 1 / 28):
        n = int(0.012 * SR)
        place(sfx, hp(rng.standard_normal(n), 3000) * np.exp(-np.arange(n) / SR / 0.002), k, 0.25)
for at, f0 in ((4.75, 660), (5.8, 784), (6.7, 988)):          # pane lands: a rising glass ping
    place(tone, bell(f0, 1.2), at, 0.13)
for at in (5.5, 6.4, 7.3):                                     # pane rushes past
    place(sfx, subby[: int(1.2 * SR)], at - 0.15, 0.45)
place(sfx, woosh, 8.3, 0.5)                                    # last pane rushes in

# ---------------------------------------------------------------- held breath 8.0-8.55: everything ducks
breath = env([(0, 1), (7.98, 1), (8.03, 0.02), (8.55, 0.02), (8.6, 1), (12, 1)])
place(tone, np.sin(2 * np.pi * 2637 * np.arange(int(0.5 * SR)) / SR) * 0.03, 8.03)

# ---------------------------------------------------------------- today: bell + warm pad
pad_g = env([(0, 0), (T_FLIP, 0), (T_FLIP + 0.4, 1), (11.5, 1), (12, 0.3)])
pad = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * a for f, a in ((220, .5), (277.2, .35), (329.6, .35), (440, .2), (110, .4)))
tone += lp(pad, 1500) * pad_g * 0.09
place(tone, bell(523.25, 2.4), T_FLIP + 0.05, 0.22)
place(tone, bell(784, 1.6), T_FLIP + 0.75, 0.10)

# ---------------------------------------------------------------- mix
mix = 1.0 * hit + 0.8 * sfx * breath + 0.7 * bed * breath + 1.0 * tone * np.maximum(breath, 0.6 * (t > 8.0) * (t < 8.6))
side = hp(bed * breath, 200) * 0.25
L, R = mix + side, mix - side
st = np.stack([L, R], 1)
st = np.tanh(st * 1.4) / np.tanh(1.4)
st *= 0.89 / np.abs(st).max()
sf.write(sys.argv[1], st.astype(np.float32), SR)
print('peak', np.abs(st).max())
