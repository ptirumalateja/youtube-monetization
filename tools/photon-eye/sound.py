"""The Photon That Made Your Eye: sound. python3 sound.py events.json out.wav

Synth layers plus CC0 Freesound files from tools/sfxlib (no credit needed): qubodup explosion-from-another-dimension,
AudioPapkin cinematic-woosh-sfx-015, stewdio2003 cp_subby_whoosh, lucabia sword-in-air, sleepCircle wind.
Everything sits on a circular buffer as long as the reel so tails wrap and the loop is seamless.
Contrast: breathing hum on the dot, muffled plasma rumble with a tick on every scatter inside the Sun,
an explosion then 0.4 s of hard silence at the escape, a jet roar, a tight click when the photon lands in the eye,
and the biggest hit (boom + gong + warm chord) on the sunset (events 'punch').
"""
import json
import sys

import numpy as np
import soundfile as sf
from scipy import signal

EV = json.load(open(sys.argv[1]))
SR = 48000; DUR = EV.get('dur', 12.0); N = int(SR * DUR)
t = np.arange(N) / SR
rng = np.random.default_rng(11)
LIB = __file__.rsplit('/', 2)[0] + '/sfxlib/'
T_TRAP, T_ESC, T_EYE, T_PUNCH = (EV['cuts'][k] for k in ('trap', 'escape', 'eye', 'punch'))


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
    i = int(round(at * SR)) % N
    idx = (i + np.arange(len(x))) % N
    np.add.at(bus, idx, g * x)


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


def gong(f0=92, dur=3.5):
    return bell(f0, dur, ((1, 1, 2.2), (2.01, .5, 1.6), (2.76, .45, 1.3), (4.07, .3, .9), (5.4, .2, .6)))


def swell(dur=0.6, lo=300, hi=5000):
    n = int(dur * SR); k = np.linspace(0, 1, n)
    x = bp(rng.standard_normal(n), lo, hi) * k ** 3
    return x / np.abs(x).max()


def tick(f0):
    n = int(0.09 * SR); k = np.arange(n) / SR
    return (hp(rng.standard_normal(n), 3500) * np.exp(-k / 0.0025) * .8 + np.sin(2 * np.pi * f0 * k) * np.exp(-k / 0.05) * .6)


hit, sfx, bed, tone = (np.zeros(N) for _ in range(4))
expl = load('814046__qubodup__explosion-from-another-dimension.wav')
sword = load('276871__lucabia__sword-in-air.wav')
woosh = load('649445__audiopapkin__cinematic-woosh-sfx-015.wav')
subby = load('238375__stewdio2003__cp_subby_whoosh.aiff')
wind = load('22331__sleepcircle__wind.ogg')

# ---------------------------------------------------------------- the hum: breathes with the dot, the frame-0 sound (wraps)
hum_g = env([(0, .9), (T_TRAP - .1, .9), (T_TRAP + .05, .25), (T_ESC, .25), (T_ESC + .05, 0), (T_EYE + .3, 0), (T_EYE + .8, .35),
             (T_PUNCH - .5, .35), (T_PUNCH - .1, 0), (DUR - .7, 0), (DUR - .1, .9), (DUR, .9)])
hum = sum(a * np.sin(2 * np.pi * f * t + ph) for f, a, ph in ((55, 1, 0), (82.5, .5, 1), (110.2, .35, 2), (164.8, .15, 3)))
hum *= 1 + .18 * np.sin(2 * np.pi * 1.4 * t)          # the dot breathes at 1.4 Hz
tone += lp(hum, 600) * hum_g * .16

# ---------------------------------------------------------------- 0.0 ignition (also the loop point)
place(hit, boom(150, 48, 1.4, .35, .6) * .55, 0.0)
place(tone, bell(1975.5, 1.8), 0.0, .16)                  # glassy tink
place(sfx, swell(.25, 2000, 9000), DUR - .25, .25)       # the sun sets into the dot

# ---------------------------------------------------------------- 1.5 into the Sun
place(sfx, swell(.35, 200, 4000), T_TRAP - .35, .45)
place(sfx, subby[: int(1.6 * SR)], T_TRAP - .12, .7)
place(hit, boom(120, 42, 1.4, .25, .9, 2.0) * .7, T_TRAP)

# plasma rumble: muffled, opening up as the years roll
rum_g = env([(0, 0), (T_TRAP, 0), (T_TRAP + .2, 1), (T_ESC - .05, 1.15), (T_ESC, 0), (DUR, 0)])
noise = rng.standard_normal(N)
u = np.clip((t - T_TRAP) / (T_ESC - T_TRAP), 0, 1)             # the low-pass opens as the years roll
l1, l2, l3 = lp(noise, 260), lp(noise, 700), lp(noise, 1800)
rumble = np.where(u < .5, l1 * (1 - 2 * u) + l2 * 2 * u, l2 * (2 - 2 * u) + l3 * (2 * u - 1)) * (1 + 1.5 * u)
rumble += .6 * lp(np.tanh(2 * np.sin(2 * np.pi * 38 * t) * (1 + .4 * np.sin(2 * np.pi * .7 * t))), 200)
w = np.tile(wind, int(np.ceil(N / len(wind))) + 1)[int(2 * SR):int(2 * SR) + N]
bed += (.5 * rumble + .35 * bp(w, 200, 2500)) * rum_g

# a tick on every scatter, climbing a pentatonic ladder as the years go by
scale = [392, 440, 523.3, 587.3, 659.3, 784, 880, 1046.5, 1174.7, 1318.5]
for i, at in enumerate(EV['scatter']):
    place(sfx, tick(scale[min(i * len(scale) // len(EV['scatter']), len(scale) - 1)]), at, .30 + .25 * i / len(EV['scatter']))
# the near-escape (year 51,000): a rising swell as it nears the surface, then a thud as it is knocked back in
NEAR = EV.get('near', T_TRAP + 2.8)
place(sfx, swell(1.1, 300, 6000), NEAR - 1.1, .5)
place(sfx, sword, NEAR - .05, .45)
place(hit, boom(110, 45, .8, .2, .6, 1.6) * .6, NEAR)

# ---------------------------------------------------------------- 6.0 the escape: explosion, then hard silence
place(sfx, swell(.3, 400, 8000), T_ESC - .3, .55)
place(hit, boom(200, 44, 2.0, .9, 1.0, 3.0) * .75, T_ESC)
place(hit, expl[: int(.5 * SR)] * dec(int(.5 * SR), .12), T_ESC, .7)
place(sfx, woosh[: int(.4 * SR)] * dec(int(.4 * SR), .1), T_ESC - .02, .5)
silence = env([(0, 1), (T_ESC + .14, 1), (T_ESC + .17, .0), (T_ESC + .55, 0), (T_ESC + .62, 1), (DUR, 1)])
place(tone, np.sin(2 * np.pi * 3520 * np.arange(int(.4 * SR)) / SR) * np.linspace(1, 0, int(.4 * SR)) * .02, T_ESC + .16)  # ear ring
# jet roar rising out of the silence
jet_g = env([(0, 0), (T_ESC + .55, 0), (T_ESC + .7, .9), (T_EYE - .3, 1.1), (T_EYE, 0), (DUR, 0)])
jf = np.interp(t, [T_ESC, T_EYE], [500, 2600])
roar = bp(rng.standard_normal(N), 150, 5000) * .6 + np.sin(2 * np.pi * np.cumsum(jf * .25) / SR) * .25
bed += lp(roar, 3000) * jet_g * .75
for k in np.sort(rng.uniform(T_ESC + .6, T_EYE - .2, 60)):    # ejecta crackle
    n = int(.02 * SR)
    place(sfx, hp(rng.standard_normal(n), 2500) * dec(n, .004), k, rng.uniform(.05, .18))

# ---------------------------------------------------------------- 8.0 the beam lands in the eye
place(sfx, swell(.25, 1500, 10000), T_EYE - .25, .5)
place(sfx, sword, T_EYE - .1, .5)
place(hit, boom(140, 50, .9, .4, .5, 1.8) * .5, T_EYE)
hitT = EV['beam_hit']
n = int(.05 * SR)
place(hit, hp(rng.standard_normal(n), 1800) * dec(n, .004) * 1.2 + np.sin(2 * np.pi * 900 * np.arange(n) / SR) * dec(n, .01) * .5, hitT, .8)   # the pupil click
place(tone, bell(1318.5, 1.6), hitT, .12)
for at in (hitT + .45, hitT + 1.05):                         # two heartbeats
    place(hit, boom(70, 42, .35, 0, .6, 1.4) * .28, at)
    place(hit, boom(70, 42, .30, 0, .5, 1.4) * .18, at + .22)
place(sfx, swell(.45, 150, 3000), T_PUNCH - .45, .6)          # the pupil swallows the frame
pre = env([(0, 1), (T_PUNCH - .08, 1), (T_PUNCH - .06, .15), (T_PUNCH, .15), (T_PUNCH + .01, 1), (DUR, 1)])

# ---------------------------------------------------------------- 10.0 the biggest hit + the warm chord
place(hit, boom(210, 42, 2.8, 1.0, 1.1, 3.4), T_PUNCH)
place(hit, expl[: int(2.0 * SR)] * dec(int(2.0 * SR), .6), T_PUNCH, .55)
place(hit, gong(87.3), T_PUNCH, .35)
place(hit, lp(rng.standard_normal(int(2.4 * SR)), 110) * dec(int(2.4 * SR), .8) * 4, T_PUNCH, .5)
chord_g = env([(0, 0), (T_PUNCH, 0), (T_PUNCH + .25, 1), (DUR - .7, .9), (DUR - .05, 0), (DUR, 0)])
chord = sum(a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (1 + .004 * np.sin(2 * np.pi * 5 * t)) for f, a in
            ((110, .5), (164.8, .4), (220, .45), (277.2, .35), (329.6, .35), (440, .2), (554.4, .12)))
tone += lp(chord, 2200) * chord_g * .11
place(tone, bell(659.3, 2.2), T_PUNCH + .4, .14)               # lands with the gold line
bed += hp(w, 300) * env([(0, 0), (T_PUNCH, 0), (T_PUNCH + .4, .25), (DUR - .4, .25), (DUR, 0)]) * .4   # evening wind

# ---------------------------------------------------------------- mix
mix = (1.0 * hit * silence + .8 * sfx * silence + .7 * bed * silence + 1.0 * tone * np.maximum(silence, .3)) * pre
side = hp(bed * silence, 250) * .25
st = np.stack([mix + side, mix - side], 1)
st = np.tanh(st * 1.4) / np.tanh(1.4)
st *= .89 / np.abs(st).max()
sf.write(sys.argv[2], st.astype(np.float32), SR)
print('peak', float(np.abs(st).max()))
