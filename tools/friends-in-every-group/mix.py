"""Sound for Friends in Every Group v6 (warm cafe). Every effect sits on the action it belongs to (times from timeline.json).

Cafe room tone and a low crowd murmur; frame 0: plates and glasses clinking and the friends laughing into the selfie,
the shutter on the flash. Late: the door, the bell, his footsteps, the minute ticks, a bonk at 47, the bench. Photo:
a shutter on every flash, a groan at "one more". Hungry: a grab and a crunch on every bite. Pays: the bill thud, his
ringtone, his footsteps out, a comic wah-wah. End: the shutter, a pop as each number lands, a bright chord.
All synthesised in numpy plus the kit's CC0 room tone (sleepCircle, Freesound 22331).

  python3 mix.py META.json OUT.wav
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_sound import *

meta = json.load(open(sys.argv[1])); EV = meta['events']
DUR = EV['duration']; N = int(DUR * SR); T = np.arange(N) / SR
R = np.random.default_rng(6)
bus = new_buses(N)

def mixs(*sig):
    y = np.zeros(max(len(x) for x in sig))
    for x in sig: y[:len(x)] += x
    return y
def tone(f, dur, dec, harm=(1, 0.5, 0.25)):
    n = int(dur * SR); t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(harm)) * np.exp(-t / dec) * np.minimum(1, t / 0.003)
def clink(seed, f0=2800, dec=0.25):
    r = np.random.default_rng(seed); n = int(dec * 4 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for m, a in [(1, 1), (1.62, 0.6), (2.37, 0.4), (3.1, 0.25)]: y += a * np.sin(2 * np.pi * f0 * m * (0.97 + 0.06 * r.random()) * t) * np.exp(-t / (dec / m ** 0.5))
    return lp(y + hp(noise(n), 4000) * env(n, 0.0015, 0.004) * 0.5, 9000) * np.minimum(1, t / 0.0015)
def plate(seed):
    n = int(0.5 * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    y = sum(np.sin(2 * np.pi * f * (0.95 + 0.1 * r.random()) * t) * np.exp(-t / d) for f, d in [(1650, 0.12), (2900, 0.08), (4300, 0.05)])
    return lp(y + bp(noise(n), 2000, 1.2) * env(n, 0.002, 0.02), 8000) * np.minimum(1, t / 0.0015)
def shutter(seed):
    n = int(0.14 * SR); t = np.arange(n) / SR
    c = hp(noise(n), 2500) * (env(n, 0.0015, 0.005) + 0.7 * np.exp(-((t - 0.05) / 0.005) ** 2))
    return lp(c + np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.01) * 0.3, 8000) * np.minimum(1, t / 0.0015)
def step(seed, g=1.0):
    n = int(0.8 * SR); return (thud(seed, 90, 0.06, 0.9) + bp(noise(n), 1900, 1.2) * env(n, 0.002, 0.025) * 0.3) * g
def pop(f0):
    n = int(0.3 * SR); t = np.arange(n) / SR; f = f0 * (1 + 0.6 * np.exp(-t / 0.02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07) * np.minimum(1, t / 0.002)
def crunch(seed):
    r = np.random.default_rng(seed); n = int(0.35 * SR); y = np.zeros(n)
    for k in range(10):
        a = int(r.random() * 0.25 * SR); m = int(0.012 * SR)
        y[a:a + m] += bp(r.standard_normal(m), 2400 + 1500 * r.random(), 1.0) * np.exp(-np.arange(m) / (0.004 * SR))
    return y
def laugh(seed, f0=230, k=6, rate=5.2):
    r = np.random.default_rng(seed); n = int((k / rate + 0.3) * SR); t = np.arange(n) / SR
    f = f0 * (1 - 0.12 * t); src = np.diff(np.floor(np.cumsum(f) / SR), prepend=0.0); src = lp(src, 1700, 1) + 0.3 * lp(hp(r.standard_normal(n), 900), 4000)
    v = sum(bp(src, fc, q) / (1 + i * 0.8) for i, (fc, q) in enumerate([(750, 4), (1250, 5), (2600, 6)]))
    e = np.zeros(n)
    for j in range(k):
        a = int(j / rate * SR); m = int(0.11 * SR)
        if a + m < n: e[a:a + m] += np.sin(np.pi * np.arange(m) / m) ** 2 * (1 - 0.06 * j)
    return v * e
def groan(seed, f0=150, dur=0.7):
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (1 - 0.25 * t / dur); src = np.diff(np.floor(np.cumsum(f) / SR), prepend=0.0); src = lp(src, 1200, 1)
    v = bp(src, 520, 3) + bp(src, 900, 4) * 0.6
    return v * np.sin(np.pi * t / dur) ** 0.7
def ringtone(dur=0.9):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for j, f in enumerate([1318, 1568, 1318, 1975, 1760, 1568]):
        a = int(j * 0.14 * SR); m = int(0.12 * SR)
        if a + m < n: y[a:a + m] += np.sin(2 * np.pi * f * np.arange(m) / SR) * np.sin(np.pi * np.arange(m) / m)
    return y
def wahwah():
    out = []
    for f, d in [(392, 0.32), (370, 0.32), (349, 0.32), (330, 0.75)]:
        n = int(d * SR); t = np.arange(n) / SR; vib = 1 + 0.012 * np.sin(2 * np.pi * 6 * t) * (t > 0.25)
        saw = 2 * ((np.cumsum(f * vib) / SR) % 1) - 1
        k = np.sin(np.pi * np.minimum(1, t / d)); wah = bp(saw, 650, 2.0) * (1 - k) + bp(saw, 1300, 2.0) * k
        out.append(wah * np.minimum(1, t / 0.02) * np.minimum(1, (d - t) / 0.06))
    return np.concatenate(out)
def bell():
    return mixs(*[np.pad(tone(f, 1.2, 0.5, (1, 0.3, 0.1)), (int(k * 0.07 * SR), 0)) for k, f in enumerate([2093, 2637, 2093, 2637])])

L, Hh, Py = EV['late'], EV['hungry'], EV['pays']

# ---- cafe murmur: a few soft voices far off (low-passed noise bursts with syllable rhythm)
mur = np.zeros(N)
for k in range(6):
    r = np.random.default_rng(100 + k); x = r.standard_normal(N); rate = 3.5 + r.random() * 2
    e = np.maximum(0, np.sin(2 * np.pi * rate * T + r.random() * 6)) ** 2 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.3 * T + k))
    mur += (bp(x, 500 + 200 * k, 3) + bp(x, 1400 + 150 * k, 4) * 0.5) * e
mur = lp(mur, 2500) / np.abs(mur).max()
for c in range(2): bus['fol'][c] += mur * 0.07

# ---- the late one's message: a soft two-note ping as the banner drops in
place(bus['air'], mixs(tone(1319, 0.25, 0.12, (1, 0.2)), np.pad(tone(1760, 0.3, 0.15, (1, 0.2)), (int(0.09 * SR), 0))), EV['ping'], 0.16, 0.0)

# ---- frame 0: plates and glasses clinking, the friends laughing into the selfie, the shutter on the flash
for j, t0 in enumerate([0.0, 0.05, 0.12, 0.2, 0.28, 0.33]):
    place(bus['fol'], clink(10 + j, 2400 + 500 * (j % 3)) if j % 2 == 0 else plate(20 + j), t0, 0.32 if j < 2 else 0.22, [-0.5, 0.4, -0.2, 0.5, 0.0, -0.4][j])
for j, (f0, pn) in enumerate([(240, -0.4), (300, 0.0), (200, 0.4)]):
    place(bus['fol'], laugh(30 + j, f0, 5), 0.05 + 0.08 * j, 0.22, pn)
place(bus['hit'], shutter(1), EV['flash0'], 0.5, 0.0)
place(bus['hit'], lp(sub_boom(1.0), 220), EV['flash0'], 0.15, 0.0)
place(bus['fol'], laugh(40, 260, 6), EV['flash0'] + 0.15, 0.25, 0.1)

# ---- #1 late: door, bell, footsteps, minute ticks, a bonk at 47, the bench
place(bus['fol'], bp(noise(int(0.5 * SR)), 600, 2) * np.sin(np.pi * np.arange(int(0.5 * SR)) / int(0.5 * SR)) * 0.6, L['door'] - 0.05, 0.25, 0.6)   # door creak
place(bus['fol'], bell(), L['door'], 0.2, 0.6)
for j, ts in enumerate(np.arange(L['door'] + 0.2, L['sit0'], 0.36)):
    place(bus['fol'], step(200 + j), ts, 0.22, 0.6 - 0.15 * j)
for j, ts in enumerate(np.cumsum(np.geomspace(0.22, 0.05, 14)) + L['min0']):
    if ts < L['min1']: place(bus['air'], tone(2200, 0.05, 0.01, (1,)), ts, 0.1, 0.0)
place(bus['hit'], mixs(tone(110, 0.6, 0.15, (1, 0.6, 0.3)), thud(5, 120, 0.06, 1.0)), L['min1'], 0.28, 0.0)                      # bonk: 47 MIN LATE
place(bus['fol'], thud(210, 70, 0.12, 1.0), L['sit1'] - 0.05, 0.3, 0.3)

# ---- #2 photo: a shutter on every flash, the group groans at "one more"
for j, ft in enumerate(EV['photoFlashes']):
    place(bus['fol'], shutter(300 + j), ft, 0.4, -0.1)
place(bus['fol'], mixs(groan(50, 140), groan(51, 180), groan(52, 120)), EV['oneMore'] - 0.1, 0.35, 0.0)

# ---- #3 hungry: a fork tap on the friend's plate + crunch on every bite, a gasp from the others
for j, g in enumerate(Hh['grabs']):
    place(bus['fol'], plate(610 + j), g, 0.18, [-0.3, 0.4, -0.5][j])   # fork taps the friend's plate (no whooshes)
    place(bus['fol'], crunch(600 + j), g + Hh['toMouth'], 0.42, 0.1)
place(bus['fol'], mixs(bp(noise(int(0.35 * SR)), 1800, 1.5) * np.sin(np.pi * np.arange(int(0.35 * SR)) / int(0.35 * SR))), Hh['grabs'][0] + 0.15, 0.12, 0.0)

# ---- #4 pays: bill thud, ringtone, footsteps out, wah-wah
place(bus['hit'], mixs(thud(700, 140, 0.05, 1.0), plate(701) * 0.4), Py['billLand'], 0.4, -0.1)
place(bus['fol'], ringtone(), Py['ring'], 0.22, -0.3)
for j, ts in enumerate(np.arange(Py['stand1'], Py['walk1'], 0.34)):
    place(bus['fol'], step(800 + j), ts, 0.22 * (1 - 0.1 * j), -0.3 - 0.1 * j)
place(bus['air'], wahwah(), Py['stand1'] + 0.1, 0.16, 0.0)

# ---- end: shutter, a pop per number, a bright chord
place(bus['hit'], shutter(900), EV['flashEnd'], 0.5, 0.0)
for n in range(1, 5): place(bus['air'], pop(392 * 2 ** ((n - 1) * 4 / 12)), EV['endCard'] + 0.15 * n, 0.2, [-0.5, -0.15, 0.15, 0.5][n - 1])
place(bus['air'], mixs(tone(523, 1.6, 0.6), tone(659, 1.6, 0.6), tone(784, 1.6, 0.6)), EV['endCard'] + 0.75, 0.12, 0.0)
place(bus['fol'], laugh(60, 250, 6), EV['flashEnd'] + 0.1, 0.22, 0.0)

room_g = np.interp(T, [0, DUR], [0.3, 0.3]); drone_g = np.zeros(N); duck = np.ones(N)
bed(bus, room_g, drone_g, duck)
mix = finish(bus, duck)
write_wav(mix, sys.argv[2])
print('mix ok', sys.argv[2])
