"""How many Indias fit on the Moon: sound. python3 sound.py events.json out.wav

Same palette as the size-ladder reel (synth layers + CC0 Freesound files in tools/sfxlib). Contrast plan: hard sub-hit on frame one,
the India sheet lands with a stamp, every Moon India is a bright stamp, the half India gets a two-note "half" chime; each body drops on a
whoosh and lands on a boom after 0.25 s of silence; the waves are tick streams that follow the counter (Earth taps, Jupiter grains,
Sun pulses); the biggest hit is the payoff, then a warm chord under the prompt and a rising rush that hands back into frame one.
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


hit, sfx, bed, tone = (np.zeros(N) for _ in range(4))
expl = load('814046__qubodup__explosion-from-another-dimension.wav')
woosh = load('649445__audiopapkin__cinematic-woosh-sfx-015.wav')
subby = load('238375__stewdio2003__cp_subby_whoosh.aiff')
wind = load('22331__sleepcircle__wind.ogg')
LAND = {k: v[1] for k, v in EV['drops'].items()}
HITS = [LAND['M'], LAND['E'], LAND['J'], EV['pay']]

# ---- hook: payoff-first sub hit on frame one, the sheet floats down and stamps on at 1.0
place(hit, boom(160, 46, 1.2, .35, .7) * .6, 0.03)
place(tone, bell(1975.5, 1.6), .03, .1)
place(sfx, swell(.9, 400, 6000), EV['sheet'] - .9, .25)
place(hit, stamp(880) * 1.1, EV['sheet'])
place(hit, boom(120, 45, .9, .3, .6, 1.8) * .45, EV['sheet'])
place(tone, bell(1318.5, 2.2), EV['sheet'] + .02, .13)

# ---- Moon Indias: a bright stamp each, pitch climbing; the half India gets a soft two-note chime
notes = [988, 1047, 1175, 1319, 1397, 1568, 1760, 1976, 2093, 2349]
for k, ta in enumerate(EV['moon'][1:-1]):
    place(hit, stamp(notes[k % len(notes)]) * .55, ta)
place(hit, stamp(1175) * .35, EV['moon'][-1]); place(tone, bell(2349, 1.2), EV['moon'][-1] + .02, .12); place(tone, bell(1760, 1.2), EV['moon'][-1] + .14, .1)

# ---- drone that grows with every scale, dropping out for the silences
silence_pts = [(0, 1)]
for h in HITS: silence_pts += [(h - .27, 1), (h - .25, .04), (h - .005, .04), (h + .01, 1)]
silence = env(silence_pts + [(DUR, 1)])
drone_g = env([(0, 0), (1.0, .4), (5.6, .7), (9.2, .9), (12.8, 1.1), (16.0, 1.2), (18.0, .9), (21.0, .5), (DUR, .3)])
dr = sum(a * np.sin(2 * np.pi * f * t + ph) for f, a, ph in ((55, 1, 0), (82.5, .5, 1), (110.2, .35, 2), (36.7, .8, 3)))
tone += lp(dr * (1 + .12 * np.sin(2 * np.pi * .35 * t)), 500) * drone_g * .12

# ---- drops: whoosh on the fall, boom on the landing (bigger every time)
for i, key in enumerate(('M', 'E', 'J')):
    a, b = EV['drops'][key]
    place(sfx, woosh[: int(1.2 * SR)] * dec(int(1.2 * SR), .6), a - .05, .55)
    place(sfx, subby[: int(1.4 * SR)], a + .1, .5)
    place(sfx, swell(.45, 200, 5000 + 2500 * i), b - .45, .45)
    place(hit, boom(170 + 25 * i, 46 - 4 * i, 1.6 + .5 * i, .6, .9, 2.4) * (.55 + .1 * i), b)
    place(hit, expl[: int((.8 + .5 * i) * SR)] * dec(int((.8 + .5 * i) * SR), .25 + .2 * i), b, .4 + .15 * i)
    place(tone, bell([987.8, 659.3, 440][i], 2.6), b + .1, .12)

# ---- waves: tick streams that follow the counter, plus a riser under each
for key, fn, fs, g in (('E', tap, [392, 440, 494, 587, 659], .32), ('J', grain, [1800, 2100, 2400, 2800], .25), ('S', pulse, [70, 78, 87, 98], .3)):
    for k, tk in enumerate(EV['tick_' + key]):
        place(sfx, fn(fs[k % len(fs)] * (1 + .01 * rng.standard_normal())), tk, g * rng.uniform(.75, 1.0))
    a, b = EV['waves'][key]
    seg = env([(0, 0), (a, 0), (a + .3, 1), (b - .2, .9), (b + .4, 0), (DUR, 0)])
    bed += bp(rng.standard_normal(N), 300 if key != 'S' else 80, 2500 if key != 'S' else 900) * seg * .07
    f = np.interp(t, [a, b], [180, 1400 if key != 'S' else 900])
    bed += np.sin(2 * np.pi * np.cumsum(f) / SR) * env([(0, 0), (a, 0), (b, .5), (b + .15, 0), (DUR, 0)]) * .12

# ---- payoff: hard silence, the biggest hit, then a warm chord through the prompt
p = EV['pay']
place(hit, boom(200, 38, 3.0, .8, 1.0, 2.8) * .85, p)
place(hit, expl[: int(2.2 * SR)] * dec(int(2.2 * SR), .8), p, .7)
place(tone, bell(440, 3.0), p + .12, .16)
chord_g = env([(0, 0), (p + .1, 0), (p + .8, 1), (EV['prompt'] + 1.8, .9), (DUR - .5, .5), (DUR, .3)])
chord = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (1 + .004 * np.sin(2 * np.pi * 5 * t))
            for f, a in ((110, .5), (164.8, .4), (220, .45), (277.2, .35), (329.6, .35), (440, .2), (554.4, .12)))
tone += lp(chord, 2200) * chord_g * .12
w = np.tile(wind, int(np.ceil(N / len(wind))) + 1)[int(2 * SR):int(2 * SR) + N]
bed += hp(w, 300) * env([(0, 0), (p + .5, 0), (p + 1.0, .25), (EV['prompt'] + 1.5, .2), (DUR, 0)]) * .4

# ---- the push back in: a whoosh as each body falls away, and a rush that lands on frame one
for key in ('J', 'E', 'M'):
    a, b = EV['lifts'][key]; place(sfx, woosh[: int(1.1 * SR)][::-1] * .8, a, .35)
rush = bp(rng.standard_normal(N), 300, 7000) * env([(0, 0), (EV['prompt'] + .5, 0), (DUR - .05, 1), (DUR, 1)]) ** 2.2
bed += rush * .22
f = np.interp(t, [EV['prompt'], DUR], [120, 900])
tone += np.sin(2 * np.pi * np.cumsum(f) / SR) * env([(0, 0), (EV['prompt'], 0), (DUR, .5)]) * .1

mix = 1.0 * hit * silence + .85 * sfx * silence + .7 * bed * silence + 1.0 * tone * np.maximum(silence, .3)
side = hp(bed * silence, 250) * .25
st = np.stack([mix + side, mix - side], 1)
st = np.tanh(st * 1.4) / np.tanh(1.4)
st *= .89 / np.abs(st).max()
sf.write(sys.argv[2], st.astype(np.float32), SR)
print('peak', float(np.abs(st).max()))
