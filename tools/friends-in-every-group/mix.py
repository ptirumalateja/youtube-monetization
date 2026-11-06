"""Sound for Friends in Every Group: a warm, busy table and one sound per friend (series kit ../slow-light-dark-common/sld_sound.py).

Six voices chatting and laughing (synthesised), a playful pop each time a number lands (rising 1 -> 6), and each friend's
own sound: the late one's footsteps and chair, the photographer's shutter, the big laugh, the snoring, the fry crunch,
the bill sliding across the wood. End card: a warm low hit as the table goes quiet. Everything synthesised in numpy
plus the kit's CC0 room tone (sleepCircle, Freesound 22331). No music bed: the _music-ready export is for a trending
sound added in the IG/FB app.

  python3 mix.py META.json OUT.wav
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_sound import *

meta = json.load(open(sys.argv[1])); EV = meta['events']
DUR = EV['duration']; N = int(DUR * SR); T = np.arange(N) / SR
R = np.random.default_rng(21)
sst = lambda a, b, x: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
BEAT = {seat: (t0, k) for k, (t0, seat, _) in enumerate(EV['beats'])}
END = EV['endCard']
PAN = {'L0': -0.5, 'L1': -0.35, 'L2': -0.2, 'R0': 0.5, 'R1': 0.35, 'R2': 0.2}

def mixs(*sig):
    y = np.zeros(max(len(x) for x in sig))
    for x in sig: y[:len(x)] += x
    return y

bus = new_buses(N)

# ---------------------------------------------------------------- the table talking (six voices, quieter while each one is "on")
VOW = {'a': [(750, 4), (1250, 5), (2600, 6)], 'e': [(450, 4), (1850, 6), (2550, 6)], 'o': [(500, 4), (900, 5), (2400, 6)]}

def formant(x, fs, scale):
    return sum(bp(x, f * scale, q) * (1.0 / (1 + k * 0.8)) for k, (f, q) in enumerate(fs))

def voice(seed, f0, t_end, energy, start=None, gap=1.8):
    r = np.random.default_rng(seed); n = min(N, int((t_end + 0.6) * SR)); t = np.arange(n) / SR
    # intonation + jitter; glottal pulses with spectral tilt
    f = f0 * (1 + 0.08 * np.sin(2 * np.pi * (0.3 + 0.4 * r.random()) * t + r.random() * 6) + 0.012 * np.cumsum(r.standard_normal(n)) / np.sqrt(SR))
    ph = np.cumsum(f) / SR; src = np.diff(np.floor(ph), prepend=0.0)
    src = lp(src, 1400, 1) + 0.04 * r.standard_normal(n)
    sc = 1 + 0.12 * (f0 - 140) / 140
    vs = {k: formant(src, v, sc) for k, v in VOW.items()}
    # phrases with syllables; vowel colour changes per syllable
    talk = np.zeros(n); wts = {k: np.zeros(n) for k in VOW}; tt = r.random() * 1.5 - 0.5 if start is None else start
    while tt < t_end:
        ln = 0.8 + 2.2 * r.random(); a, b = int(max(tt, 0) * SR), int(min(tt + ln, t_end) * SR)
        if b > a:
            seg = t[a:b] - tt; rate = 4 + 2.5 * r.random()
            talk[a:b] = np.maximum(0, np.sin(2 * np.pi * rate * seg + r.random() * 6)) ** 1.5 * np.minimum(1, seg / 0.08) * np.minimum(1, (ln - seg) / 0.15)
            syl = np.floor(seg * rate).astype(int); cols = r.integers(0, 3, syl.max() + 1)
            for i, k in enumerate(VOW): wts[k][a:b] = (cols[syl] == i)
        tt += ln + 0.25 + gap * r.random()
    for k in wts: wts[k] = lp(wts[k], 25)
    y = sum(vs[k] * wts[k] for k in VOW) * talk
    # laughs: "ha-ha-ha" bursts, higher pitch, breathy; more of them while the table is full
    lau = np.zeros(n); tt = -0.4 + 0.8 * r.random()
    while tt < t_end:
        if r.random() < energy(tt):
            k = int(4 + 4 * r.random()); rate = 4.6 + 1.2 * r.random()
            for j in range(k):
                s0 = tt + j / rate; a = int(max(s0, 0) * SR); m = int(0.11 * SR)
                if a + m >= n: break
                seg = np.arange(m) / SR
                lau[a:a + m] += np.sin(np.pi * seg / 0.11) ** 2 * (1 - 0.5 * j / k)
        tt += 1.2 + 3.5 * r.random()
    hsrc = np.diff(np.floor(np.cumsum(f * 1.45) / SR), prepend=0.0); hsrc = lp(hsrc, 1600, 1) + 0.25 * lp(hp(r.standard_normal(n), 900), 4000)
    y += formant(hsrc, VOW['a'], sc * 1.08) * lau * 1.6
    fade = 1 - sst(t_end - 0.3, t_end + 0.5, t)
    return y * fade

for j, seat in enumerate(PAN):
    t_end = END - 0.1
    v = voice(30 + j, 120 + 25 * j + (60 if seat in ('L2', 'R0') else 0), t_end, lambda t: 0.5, start=-0.4 + 0.15 * j, gap=0.8)
    v = v / (np.abs(v).max() + 1e-9)
    g = np.ones(len(v))
    if seat == 'R1': g *= sst(BEAT['R1'][0] + 0.9, BEAT['R1'][0] + 1.3, np.arange(len(v)) / SR)   # the late one only talks once he sits
    if seat == 'L1': g *= 1 - sst(BEAT['L1'][0], BEAT['L1'][0] + 0.4, np.arange(len(v)) / SR)     # the sleeper goes quiet
    place(bus['fol'], lp(hp(v * g, 150), 3200), 0.0, 0.2, PAN[seat])


# ---------------------------------------------------------------- a playful pop as each number lands (rising 1 -> 6)
def pop(f0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    f = f0 * (1 + 0.6 * np.exp(-t / 0.02))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07) * np.minimum(1, t / 0.002) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.03)
for seat, (t0, k) in BEAT.items():
    place(bus['air'], pop(392 * 2 ** (k * 2 / 12)), t0 + 0.1, 0.16, PAN[seat] * 0.6)   # G4 up a whole tone each time


# ---------------------------------------------------------------- the ki power-up as the gold aura flares on each friend
def powerup(seed, dur=0.55):
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR; x = r.standard_normal(n)
    sweep = np.zeros(n)
    for fc in (600, 1100, 2000, 3400):   # an airy whoosh that climbs as the flames rise
        sweep += bp(x, fc, 2.0) * np.exp(-((t / dur - (np.log(fc / 600) / np.log(3400 / 600)) * 0.7 - 0.1) / 0.18) ** 2)
    crackle = hp(x, 3000) * (r.random(n) > 0.995) * 3.0 * np.exp(-t / 0.4)
    body = np.sin(2 * np.pi * (70 + 50 * np.exp(-t / 0.05)) * t) * env(n, 0.003, 0.12) * 0.8
    return (sweep * 0.6 + crackle * 0.3 + body) * np.minimum(1, (n - np.arange(n)) / (0.1 * SR))
place(bus['air'], pop(330), 0.0, 0.2, 0.0)                                  # frame 0: the hook lands on a pop
place(bus['hit'], powerup(799, 0.5), 0.0, 0.16, 0.0)
for seat, (t0, k) in BEAT.items():
    place(bus['hit'], powerup(800 + k), t0 + (0.55 if seat == 'R1' else 0.0) - 0.05, 0.22, PAN[seat] * 0.5)


# ---------------------------------------------------------------- each friend's own sound
def step(seed, g=1.0):
    n = int(0.8 * SR)
    return (thud(seed, 85, 0.07, 0.9) + bp(noise(n), 1800, 1.2) * env(n, 0.002, 0.03) * 0.25) * g
def chair(seed, dur=0.35):
    r = np.random.default_rng(seed); n = int(dur * SR); x = r.standard_normal(n); gr = np.repeat(r.random(n // 160 + 1), 160)[:n] ** 4
    e = np.minimum(1, np.arange(n) / (0.03 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.08 * SR))
    return (bp(x * (0.25 + gr), 420, 1.4) + bp(x * gr, 1300, 2.2) * 0.6) * e
t1 = BEAT['R1'][0]
for j, ts in enumerate(np.arange(0.05, t1 + 0.55, 0.42)):                   # the late one walks in out of the dark
    place(bus['fol'], step(200 + j), ts, 0.14 * min(1, 0.4 + ts / (t1 + 0.5)), 0.6)
place(bus['fol'], chair(210), t1 + 0.6, 0.22, 0.35)

def shutter(seed):
    n = int(0.12 * SR); t = np.arange(n) / SR
    c = hp(noise(n), 2500) * (env(n, 0.0003, 0.004) + 0.7 * np.exp(-((t - 0.045) / 0.004) ** 2))
    return c + np.sin(2 * np.pi * 900 * t) * np.exp(-t / 0.01) * 0.3
place(bus['fol'], shutter(300), BEAT['L2'][0] + 0.72, 0.3, PAN['L2'])

# the big laugh: a burst of "ha"s from the laugher (reuses the voice laugh model)
r = np.random.default_rng(400); n = int(1.6 * SR); t = np.arange(n) / SR
f = 230 * (1 - 0.15 * t) ; hsrc = np.diff(np.floor(np.cumsum(f) / SR), prepend=0.0); hsrc = lp(hsrc, 1700, 1) + 0.3 * lp(hp(r.standard_normal(n), 900), 4000)
burst = np.zeros(n)
for j in range(8):
    a = int(j / 5.4 * SR); m = int(0.11 * SR)
    if a + m < n: burst[a:a + m] += np.sin(np.pi * np.arange(m) / m) ** 2 * (1 - 0.06 * j)
place(bus['fol'], formant(hsrc, VOW['a'], 1.1) * burst, BEAT['R2'][0] + 0.05, 0.5, PAN['R2'])

def snore(seed, dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    flutter = 0.5 + 0.5 * np.sin(2 * np.pi * 28 * t)
    y = lp(r.standard_normal(n), 420) * flutter * np.sin(np.pi * np.minimum(1, t / (dur * 0.55))) ** 2 * (t < dur * 0.55)
    y += bp(r.standard_normal(n), 900, 1.5) * 0.25 * np.sin(np.pi * np.clip((t - dur * 0.6) / (dur * 0.35), 0, 1)) ** 2   # the breath out
    return y
for j, ts in enumerate(np.arange(BEAT['L1'][0] + 0.55, DUR - 1.0, 2.2)):
    place(bus['fol'], snore(500 + j), ts, 0.22 if ts < END else 0.3, PAN['L1'])

def crunch(seed):
    r = np.random.default_rng(seed); n = int(0.35 * SR); y = np.zeros(n)
    for k in range(9):
        a = int(r.random() * 0.25 * SR); m = int(0.012 * SR)
        y[a:a + m] += bp(r.standard_normal(m), 2400 + 1500 * r.random(), 1.0) * np.exp(-np.arange(m) / (0.004 * SR))
    return y
for dt in (0.62, 1.38, 1.92):
    place(bus['fol'], crunch(600 + int(dt * 10)), BEAT['L0'][0] + dt, 0.3, PAN['L0'])

n = int(0.55 * SR); ts = np.arange(n) / SR
slide = bp(noise(n), 1500, 1.1) * np.sin(np.pi * ts / ts[-1]) ** 1.5 + bp(noise(n), 500, 2.0) * 0.4 * np.sin(np.pi * ts / ts[-1])
place(bus['fol'], slide, BEAT['R0'][0] + 0.15, 0.2, 0.2)
place(bus['fol'], thud(700, 160, 0.04, 0.6), BEAT['R0'][0] + 0.68, 0.18, -0.2)   # it stops in front of the sleeper


# ---------------------------------------------------------------- end card: the table goes quiet, one warm low hit
n = int(3.0 * SR); t = np.arange(n) / SR
warm = sum(a * np.sin(2 * np.pi * f * t) for f, a in [(98.0, 1.0), (146.8, 0.5), (196.0, 0.35), (246.9, 0.15)])
warm = np.tanh(1.4 * warm * (1 - np.exp(-t / 0.01)) * np.exp(-t / 1.1)) * 0.6
place(bus['hit'], warm, END, 0.3, 0.0)
place(bus['hit'], lp(sub_boom(2.5), 220), END, 0.18, 0.0)
place(bus['air'], pop(784), END + 0.55, 0.14, 0.0)

room_g = np.interp(T, [0, END, END + 0.4, DUR], [0.34, 0.36, 0.26, 0.24])
drone_g = np.interp(T, [0, END, DUR], [0.05, 0.08, 0.12])
duck = 1 - 0.85 * ((T > END - 0.18) & (T < END)); duck = lp(duck, 30)
bed(bus, room_g, drone_g, duck)
mix = finish(bus, duck)
write_wav(mix, sys.argv[2])
print('mix ok', sys.argv[2])
