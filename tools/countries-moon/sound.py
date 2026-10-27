"""How many countries fit on the Moon: sound. python3 sound.py events.json out.wav

Same palette as the India size-ladder reel. Hard sub-hit on frame one, the India sheet stamps on, every India is a bright stamp; each new
country arrives on a wipe whoosh, its tiles tick in faster and higher than the last (the ladder you can hear), and its number lands on a hit.
Nepal's "same size" beat gets a beat of silence and a single hit; Bhutan a deep boom with a long tail; then the music cuts, one tick, loop.
"""
import json
import sys

import numpy as np
import soundfile as sf
from scipy import signal

EV = json.load(open(sys.argv[1]))
SR = 48000; DUR = EV['dur']; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(29)
LIB = __file__.rsplit('/', 2)[0] + '/sfxlib/'


def load(name):
    x, sr = sf.read(LIB + name); x = x if x.ndim == 1 else x.mean(1)
    if sr != SR: x = signal.resample_poly(x, SR, sr)
    return x / (np.abs(x).max() + 1e-9)
def bp(x, lo, hi, o=2): return signal.sosfilt(signal.butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def env(pts): ts, vs = zip(*pts); return np.interp(t, ts, vs)
def dec(n, tau): return np.exp(-np.arange(n) / SR / tau)
def place(bus, x, at, g=1.0):
    i = int(round(at * SR))
    if i >= N or i + len(x) <= 0: return
    if i < 0: x = x[-i:]; i = 0
    x = x[: N - i]; bus[i:i + len(x)] += g * x


def boom(f0=170, f1=48, dur=1.8, crack=0.6, sub=0.8, drive=2.5):
    n = int(dur * SR); k = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-k / 0.07)
    body = np.tanh(drive * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-k / 0.42)
    return body + hp(rng.standard_normal(n), 2500) * np.exp(-k / 0.016) * crack + np.sin(2 * np.pi * 46 * k) * np.exp(-k / 0.8) * sub
def bell(f0, dur=2.5, parts=((1, 1, 1.6), (2.0, .35, 1.0), (2.76, .3, .7), (5.4, .12, .4))):
    n = int(dur * SR); k = np.arange(n) / SR; x = np.zeros(n)
    for r, a, d in parts: x += a * np.sin(2 * np.pi * f0 * r * k + rng.uniform(0, 6)) * np.exp(-k / d)
    return x * (1 - np.exp(-k / 0.002))
def swell(dur=0.6, lo=300, hi=5000):
    n = int(dur * SR); k = np.linspace(0, 1, n); x = bp(rng.standard_normal(n), lo, hi) * k ** 3
    return x / np.abs(x).max()
def stamp(f0):          # an India pressed onto the surface: soft thud + glassy ring
    n = int(.5 * SR); k = np.arange(n) / SR
    return (np.tanh(2 * np.sin(2 * np.pi * (f0 / 8 + 40 * np.exp(-k / .03)) * k)) * np.exp(-k / .07) * .7
            + np.sin(2 * np.pi * f0 * k) * np.exp(-k / .25) * .35 + np.sin(2 * np.pi * f0 * 2.01 * k) * np.exp(-k / .12) * .15
            + hp(rng.standard_normal(n), 3000) * np.exp(-k / .004) * .3)
def tap(f0):
    n = int(.12 * SR); k = np.arange(n) / SR
    return np.sin(2 * np.pi * f0 * k) * np.exp(-k / .035) * .8 + bp(rng.standard_normal(n), 600, 2600) * np.exp(-k / .008) * .5
def grain(f0):
    n = int(.08 * SR); k = np.arange(n) / SR
    return np.sin(2 * np.pi * f0 * k) * np.exp(-k / .02) * .6 + hp(rng.standard_normal(n), 5000) * np.exp(-k / .003) * .4
def pulse(f0):
    n = int(.3 * SR); k = np.arange(n) / SR
    return np.tanh(2 * np.sin(2 * np.pi * (f0 + 50 * np.exp(-k / .04)) * k)) * np.exp(-k / .08) + lp(rng.standard_normal(n), 500) * np.exp(-k / .02) * .4


hit, sfx, bed, tone, free = (np.zeros(N) for _ in range(5))
expl = load('814046__qubodup__explosion-from-another-dimension.wav')
woosh = load('649445__audiopapkin__cinematic-woosh-sfx-015.wav')
subby = load('238375__stewdio2003__cp_subby_whoosh.aiff')
END = EV['end']

# ---- hook: sub hit on frame one, the sheet stamps on
place(hit, boom(160, 46, 1.2, .35, .7) * .6, 0.03)
place(tone, bell(1975.5, 1.6), .03, .1)
place(sfx, swell(.8, 400, 6000), EV['sheet'] - .8, .25)
place(hit, stamp(880) * 1.1, EV['sheet']); place(hit, boom(120, 45, .9, .3, .6, 1.8) * .45, EV['sheet'])
place(tone, bell(1318.5, 2.2), EV['sheet'] + .02, .13)
notes = [988, 1047, 1175, 1319, 1397, 1568, 1760, 1976, 2093, 2349]
for k, ta in enumerate(EV['moon'][1:-1]): place(hit, stamp(notes[k % len(notes)]) * .55, ta)
place(hit, stamp(1175) * .35, EV['moon'][-1]); place(tone, bell(2349, 1.2), EV['moon'][-1] + .02, .12); place(tone, bell(1760, 1.2), EV['moon'][-1] + .14, .1)
place(hit, boom(150, 44, 1.4, .4, .8, 2.2) * .4, EV['moon'][-1] + .05)

# ---- each country: wipe whoosh, a tick stream that climbs in pitch and density, a hit when the number lands
for k, ((a, b, hold), ticks) in enumerate(zip(EV['seq'][1:], EV['ticks'])):
    place(sfx, woosh[: int(1.0 * SR)] * dec(int(1.0 * SR), .5), a - .35, .5)
    place(sfx, subby[: int(1.2 * SR)], a - .2, .35)
    base = 300 * 1.22 ** k
    for j, tk in enumerate(ticks):
        place(sfx, tap(base * (1 + .5 * j / len(ticks)) * (1 + .01 * rng.standard_normal())), tk, .3 * rng.uniform(.75, 1.))
    if k == 2:      # Nepal: silence, then one hit on "same size"
        place(hit, boom(190, 42, 2.0, .7, .9, 2.6) * .7, EV['same']); place(tone, bell(659.3, 2.4), EV['same'] + .05, .14)
    elif k == 4:    # Bhutan: deep boom, long tail
        place(hit, boom(140, 34, 3.2, .5, 1.0, 2.6) * .85, b); place(hit, expl[: int(2.5 * SR)] * dec(int(2.5 * SR), .9), b, .6)
        place(tone, bell(440, 3.2), b + .1, .15)
    else:
        place(hit, boom(170 + 15 * k, 46 - 2 * k, 1.4, .5, .8, 2.2) * (.5 + .05 * k), b); place(tone, bell([987.8, 880, 784, 698.5, 659.3][k], 2.0), b + .05, .11)
    seg = env([(0, 0), (a, 0), (a + .2, 1), (b, .8), (b + .4, 0), (DUR, 0)])
    bed += bp(rng.standard_normal(N), 300, 2500 + 400 * k) * seg * .06

# ---- silences: before the Nepal hit, and the music cut at the end
silence = env([(0, 1), (EV['same'] - .3, 1), (EV['same'] - .28, .04), (EV['same'] - .005, .04), (EV['same'] + .01, 1),
               (END - .02, 1), (END, .03), (DUR - .9, .03), (DUR - .6, .6), (DUR, 1)])
drone_g = env([(0, 0), (1.0, .4), (6, .6), (10, .75), (14, .85), (18, .95), (22.5, 1.1), (END, 1.1), (END + .02, 0), (DUR, 0)])
dr = sum(a * np.sin(2 * np.pi * f * t + ph) for f, a, ph in ((55, 1, 0), (82.5, .5, 1), (110.2, .35, 2), (36.7, .8, 3)))
tone += lp(dr * (1 + .12 * np.sin(2 * np.pi * .35 * t)), 500) * drone_g * .12
# "...and India was just 11.5": one tick in the silence, then the sheet re-forms on a soft rise into frame one
place(free, stamp(880) * .5, END + .35)       # not gated by the silence
rise = bp(rng.standard_normal(N), 400, 7000) * env([(0, 0), (DUR - 1.2, 0), (DUR, 1)]) ** 2.5
bed += rise * .25

mix = 1.0 * hit * silence + .85 * sfx * silence + .7 * bed * np.maximum(silence, (t > DUR - 1.3)) + 1.0 * tone * np.maximum(silence, .2) + free
side = hp(bed, 250) * .2
st = np.stack([mix + side, mix - side], 1)
st = np.tanh(st * 1.4) / np.tanh(1.4)
st *= .89 / np.abs(st).max()
sf.write(sys.argv[2], st.astype(np.float32), SR)
print('peak', float(np.abs(st).max()))
