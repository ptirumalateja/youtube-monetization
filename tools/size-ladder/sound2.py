"""Extended cut sound (events2.json from comp2.py events). python3 sound2.py events2.json out.wav

Synth layers plus CC0 Freesound files from tools/sfxlib (qubodup explosion-from-another-dimension, AudioPapkin woosh,
stewdio2003 subby whoosh, lucabia sword-in-air, sleepCircle wind). Contrast plan: a hard sub-hit on the moon at 0.05 s, then quiet;
every unit family has its own voice (moons = glassy pops, Earths = woody taps, Jupiters = deep thumps) and the tick density follows the real fill
curve; each bowl closes on a boom with 0.3 s of hard silence before it, light ignites on a riser, the Sun's close is the biggest hit.
"""
import json
import sys

import numpy as np
import soundfile as sf
from scipy import signal

EV = json.load(open(sys.argv[1]))
SR = 48000; DUR = EV['dur']; N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(23)
LIB = __file__.rsplit('/', 2)[0] + '/sfxlib/'
HITS = EV['hit']; WAVES = EV['waves']; T4 = EV['t4']


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
    if i >= N: return
    x = x[: N - i]
    bus[i:i + len(x)] += g * x


def boom(f0=170, f1=48, dur=1.8, crack=0.6, sub=0.8, drive=2.5):
    n = int(dur * SR); k = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-k / 0.07)
    body = np.tanh(drive * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-k / 0.42)
    return body + hp(rng.standard_normal(n), 2500) * np.exp(-k / 0.016) * crack + np.sin(2 * np.pi * 46 * k) * np.exp(-k / 0.8) * sub


def bell(f0, dur=2.5, parts=((1, 1, 1.6), (2.0, .35, 1.0), (2.76, .3, .7), (5.4, .12, .4))):
    n = int(dur * SR); k = np.arange(n) / SR; x = np.zeros(n)
    for r, a, d in parts:
        x += a * np.sin(2 * np.pi * f0 * r * k + rng.uniform(0, 6)) * np.exp(-k / d)
    return x * (1 - np.exp(-k / 0.002))


def swell(dur=0.6, lo=300, hi=5000):
    n = int(dur * SR); k = np.linspace(0, 1, n)
    x = bp(rng.standard_normal(n), lo, hi) * k ** 3
    return x / np.abs(x).max()


def pop(f0):            # moon: glassy pop
    n = int(.07 * SR); k = np.arange(n) / SR
    return np.sin(2 * np.pi * f0 * k * (1 + .6 * np.exp(-k / .01))) * np.exp(-k / .02) * .7 + hp(rng.standard_normal(n), 4000) * np.exp(-k / .002) * .4
def tap(f0):            # Earth: woody tap
    n = int(.12 * SR); k = np.arange(n) / SR
    return np.sin(2 * np.pi * f0 * k) * np.exp(-k / .035) * .8 + bp(rng.standard_normal(n), 600, 2600) * np.exp(-k / .008) * .5
def thump(f0):          # Jupiter: deep thump
    n = int(.3 * SR); k = np.arange(n) / SR
    return np.tanh(2 * np.sin(2 * np.pi * (f0 + 60 * np.exp(-k / .04)) * k)) * np.exp(-k / .09) + lp(rng.standard_normal(n), 400) * np.exp(-k / .02) * .5


hit, sfx, bed, tone = (np.zeros(N) for _ in range(4))
expl = load('814046__qubodup__explosion-from-another-dimension.wav')
woosh = load('649445__audiopapkin__cinematic-woosh-sfx-015.wav')
subby = load('238375__stewdio2003__cp_subby_whoosh.aiff')
sword = load('276871__lucabia__sword-in-air.wav')
wind = load('22331__sleepcircle__wind.ogg')

# ---- hook: payoff-first hit on the moon, then a thin shimmer
place(hit, boom(160, 46, 1.2, .35, .7) * .6, 0.05)
place(tone, bell(1975.5, 1.6), .05, .12)
shim = sum(np.sin(2 * np.pi * f * t) for f in (440, 660, 880.5)) * env([(0, 0), (.3, .5), (2.0, .9), (2.35, 0), (DUR, 0)])
tone += lp(shim, 1800) * .02
place(sfx, woosh[: int(.9 * SR)] * dec(int(.9 * SR), .5), EV['fall'] - .1, .45)         # the moon drops in
place(hit, boom(110, 50, .5, .2, .4, 1.5) * .4, EV['fall'] + .88)

# ---- drone that grows with the scale
drone_g = env([(0, 0), (.8, .5), (HITS[0] - .35, .8), (HITS[0] - .3, 0), (HITS[0] + .5, .7), (HITS[1] - .35, 1.0), (HITS[1] - .3, 0),
               (HITS[1] + .5, .9), (HITS[2] - .35, 1.2), (HITS[2] - .3, 0), (HITS[2] + .5, 0), (HITS[2] + 1.0, 1.0), (T4['cut'] - .1, 1.2), (T4['cut'], 0), (T4['cut'] + .5, .35), (T4['prompt'], .35), (T4['loop'] - .4, .5), (DUR, 0)])
dr = sum(a * np.sin(2 * np.pi * f * t + ph) for f, a, ph in ((55, 1, 0), (82.5, .5, 1), (110.2, .35, 2), (36.7, .8, 3)))
tone += lp(dr * (1 + .12 * np.sin(2 * np.pi * .35 * t)), 500) * drone_g * .13

# ---- the pours
voice = [(pop, [1500, 1760, 1976, 2217, 2349]), (tap, [392, 440, 494, 587, 659]), (thump, [70, 78, 87, 98, 110])]
for (fn, fs), fl, gain in zip(voice, EV['fills'], (.55, .38, .55)):
    ts = fl['t']; step = 1
    for k in range(0, len(ts), step):
        place(sfx, fn(fs[k % len(fs)] * (1 + .01 * rng.standard_normal())), ts[k], gain * 1.5 * rng.uniform(.8, 1.0))
        if fn is not pop: place(hit, boom(90 if fn is tap else 60, 38, .5 if fn is tap else .8, .05, .5, 1.2) * (.12 if fn is tap else .22), ts[k], 1.)   # weight of the impact
        # the fall itself: a rising airy rush plus a pitched whistle that swells toward the landing (matches the 0.85 s fall in the shader)
        FL = fl['fall']; wl = int(FL * SR); kk = np.arange(wl) / SR; sw = (kk / FL) ** 2.2
        f0, f1 = (500, 2800) if fn is pop else (320, 1500) if fn is tap else (180, 700)
        fw = np.linspace(f0, f1, wl) * (1 + .02 * np.sin(2 * np.pi * 9 * kk))
        rush = bp(rng.standard_normal(wl), f0 * 1.2, f1 * 1.6) * sw
        gw = .75 if fn is pop else .35 if fn is tap else .3
        place(sfx, (np.sin(2 * np.pi * np.cumsum(fw) / SR) * .5 + rush * 1.1) * sw * gw, ts[k] - FL, 1.)
    seg = env([(0, 0), (fl['a'] - .05, 0), (fl['a'] + .3, 1), (fl['b'] - .2, .8), (fl['b'] + .3, 0), (DUR, 0)])
    bed += lp(rng.standard_normal(N), 900 if fn is not pop else 2500) * seg * .06      # granular wash

# ---- each bowl closes: swell, hard silence, boom
for i, h in enumerate(HITS):
    big = i == 2
    place(sfx, swell(.45, 200, 5000 + 3000 * i), h - .45, .5)
    place(hit, boom(180 + 30 * i, 44 - 4 * i, 1.8 + .9 * i, .7, .9, 2.6) * (.85 if big else .6), h)
    place(hit, expl[: int((.9 + .9 * i) * SR)] * dec(int((.9 + .9 * i) * SR), .25 + .3 * i), h, .5 + .25 * i)
    place(tone, bell([987.8, 659.3, 440][i], 2.8), h + .12, .14)
silence = env([(0, 1)] + sum(([(h - .31, 1), (h - .29, .05), (h - .0, .05), (h + .015, 1)] for h in HITS), []) + [(T4['cut'] - .16, 1), (T4['cut'] - .14, .02), (T4['cut'] + .06, .02), (T4['cut'] + .1, 1), (DUR - .08, 1), (DUR - .04, .0), (DUR, 0)])

# ---- ignition waves: rising riser + whoosh into the reveal
for (a, b), k in zip(WAVES, (0, 1)):
    place(sfx, woosh[: int(1.6 * SR)] * dec(int(1.6 * SR), .7), a, .6 - .1 * k)
    place(sfx, subby[: int(1.6 * SR)], a + .1, .6)
    g = env([(0, 0), (a, 0), (b - .1, 1), (b + .1, 0), (DUR, 0)])
    f = np.interp(t, [a, b], [200, 2400 - 600 * k])
    bed += (bp(rng.standard_normal(N), 200, 6000) * .5 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .2) * g * .45
    place(hit, boom(120, 40, 1.2, .2, .9, 2.0) * .5, b)

# ---- tier 4: the Sun shrinks, the count runs away, the number lands, the whip reveals the star, hard cut to the starfield
chord_g = env([(0, 0), (HITS[2] + .2, 0), (HITS[2] + .8, 1), (T4['cut'] - .1, 1), (T4['cut'], 0), (DUR, 0)])
chord = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (1 + .004 * np.sin(2 * np.pi * 5 * t))
            for f, a in ((110, .5), (164.8, .4), (220, .45), (277.2, .35), (329.6, .35), (440, .2), (554.4, .12)))
tone += lp(chord, 2200) * chord_g * .1
place(sfx, woosh[: int(1.0 * SR)] * dec(int(1.0 * SR), .6), T4['shrink'] + .05, .5)                       # the Sun shrinks to a marble
tk = T4['count']; i = 0
while tk < T4['jump'] - .05:                                                                                # accelerating ticks with a climbing pitch
    place(sfx, pop(900 + 1700 * (tk - T4['count']) / (T4['jump'] - T4['count'])), tk, .5)
    tk += max(.05, .16 * (1 - (tk - T4['count']) / (T4['jump'] - T4['count'])) ** 1.2 + .035); i += 1
g = env([(0, 0), (T4['count'], 0), (T4['jump'] - .05, 1), (T4['jump'], 0), (DUR, 0)]); f = np.interp(t, [T4['count'], T4['jump']], [180, 3000])
bed += (bp(rng.standard_normal(N), 300, 7000) * .4 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .22) * g * .5
place(hit, boom(200, 36, 2.6, .8, 1., 2.8) * .95, T4['jump'])                                              # 10,000,000,000 lands
place(hit, expl[: int(2.2 * SR)] * dec(int(2.2 * SR), .5), T4['jump'], .8)
place(tone, bell(329.6, 3.0), T4['jump'] + .1, .16)
wh = int((T4['cut'] - T4['whip']) * SR); kw = np.linspace(0, 1, wh)
place(sfx, bp(rng.standard_normal(wh), 200, 9000) * kw ** 2.5 * .9 + np.sin(2 * np.pi * np.cumsum(np.linspace(90, 900, wh)) / SR) * kw ** 2 * .35, T4['whip'], .8)
place(sfx, subby[: int(1.0 * SR)], T4['whip'], .7)
# ---- payoff on the starfield: near silence, a soft low bell, then a slow riser into the loop
place(tone, bell(110, 4.0), T4['cut'] + .12, .22); place(tone, bell(164.8, 3.5), T4['cut'] + .6, .1)
sh2 = sum(np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) for f in (293.7, 440, 587.3)) * env([(0, 0), (T4['cut'] + .2, 0), (T4['cut'] + 1.2, .5), (T4['prompt'], .5), (T4['loop'] - .5, .8), (T4['loop'], 0), (DUR, 0)])
tone += lp(sh2, 1800) * .025
lw = int((T4['loop'] - T4['prompt']) * SR); kl = np.linspace(0, 1, lw)
place(sfx, bp(rng.standard_normal(lw), 150, 8000) * kl ** 3.2 * .8 + np.sin(2 * np.pi * np.cumsum(np.linspace(60, 1400, lw) ** 1.0) / SR) * kl ** 3 * .3, T4['prompt'], .7)   # the zoom home
w = np.tile(wind, int(np.ceil(N / len(wind))) + 1)[int(2 * SR):int(2 * SR) + N]
bed += hp(w, 300) * env([(0, 0), (HITS[2] + .5, 0), (HITS[2] + 1.0, .25), (T4['cut'] - .1, .25), (T4['cut'], 0), (DUR, 0)]) * .4

mix = 1.0 * hit * silence + .8 * sfx * silence + .7 * bed * silence + 1.0 * tone * np.maximum(silence, .3)
side = hp(bed * silence, 250) * .25
st = np.stack([mix + side, mix - side], 1)
st = np.tanh(st * 1.4) / np.tanh(1.4)
st *= .89 / np.abs(st).max()
sf.write(sys.argv[2], st.astype(np.float32), SR)
print('peak', float(np.abs(st).max()))
