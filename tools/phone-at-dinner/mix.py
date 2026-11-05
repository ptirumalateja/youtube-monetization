"""Sound for The Phone at Dinner: minimal but heavy (series kit ../slow-light-dark-common/sld_sound.py).

Her voice across the table (a synthesised murmur that talks, laughs, then thins out and stops as she fades), his thumb
on the screen (small dry ticks, a soft notification blip now and then), the years going by (a faint run of cutlery ticks
that speeds up with the DINNER counter), a held breath, then one cold low hit when he looks up and the phone goes face
down on the wood. No warm tone. Everything synthesised in numpy plus the kit's CC0 room tone (sleepCircle, Freesound 22331).

  python3 mix.py META.json OUT.wav
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_sound import *

meta = json.load(open(sys.argv[1])); EV = meta['events']; FR = meta['frames']
DUR = EV['duration']; FPS = EV['fps']; N = int(DUR * SR); T = np.arange(N) / SR
R = np.random.default_rng(11)
sst = lambda a, b, x: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
per_frame = lambda key: np.interp(T, np.arange(len(FR)) / FPS, [f[key] for f in FR])
LOOK = EV['lookUp'][1]

def mixs(*sig):
    y = np.zeros(max(len(x) for x in sig))
    for x in sig: y[:len(x)] += x
    return y

bus = new_buses(N)

# ---------------------------------------------------------------- her voice: talks and laughs, then stops; dims with her
VOW = {'a': [(750, 4), (1250, 5), (2600, 6)], 'e': [(450, 4), (1850, 6), (2550, 6)], 'o': [(500, 4), (900, 5), (2400, 6)]}

def formant(x, fs, scale):
    return sum(bp(x, f * scale, q) * (1.0 / (1 + k * 0.8)) for k, (f, q) in enumerate(fs))

def voice(seed, f0, t_end, energy):
    r = np.random.default_rng(seed); n = min(N, int((t_end + 0.6) * SR)); t = np.arange(n) / SR
    # intonation + jitter; glottal pulses with spectral tilt
    f = f0 * (1 + 0.08 * np.sin(2 * np.pi * (0.3 + 0.4 * r.random()) * t + r.random() * 6) + 0.012 * np.cumsum(r.standard_normal(n)) / np.sqrt(SR))
    ph = np.cumsum(f) / SR; src = np.diff(np.floor(ph), prepend=0.0)
    src = lp(src, 1400, 1) + 0.04 * r.standard_normal(n)
    sc = 1 + 0.12 * (f0 - 140) / 140
    vs = {k: formant(src, v, sc) for k, v in VOW.items()}
    # phrases with syllables; vowel colour changes per syllable
    talk = np.zeros(n); wts = {k: np.zeros(n) for k in VOW}; tt = r.random() * 1.5 - 0.5
    while tt < t_end:
        ln = 0.8 + 2.2 * r.random(); a, b = int(max(tt, 0) * SR), int(min(tt + ln, t_end) * SR)
        if b > a:
            seg = t[a:b] - tt; rate = 4 + 2.5 * r.random()
            talk[a:b] = np.maximum(0, np.sin(2 * np.pi * rate * seg + r.random() * 6)) ** 1.5 * np.minimum(1, seg / 0.08) * np.minimum(1, (ln - seg) / 0.15)
            syl = np.floor(seg * rate).astype(int); cols = r.integers(0, 3, syl.max() + 1)
            for i, k in enumerate(VOW): wts[k][a:b] = (cols[syl] == i)
        tt += ln + 0.4 + 1.8 * r.random()
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

talk = per_frame('herTalk'); alpha = per_frame('herAlpha')
v = voice(5, 205, 8.2, lambda t: float(np.interp(t, [0, 3, 6], [0.9, 0.6, 0.0])))
v = v / (np.abs(v).max() + 1e-9)
g = np.zeros(N); g[:len(v)] = 1.0
g *= (0.25 + 0.75 * talk) * alpha            # after she goes quiet only a few words leak out
bright, dull = lp(hp(v, 150), 4200), lp(hp(v, 150), 1500)
k = np.clip(np.interp(np.arange(len(v)) / SR, [0, 5, 8], [0, 0.4, 1.0]), 0, 1)
vv = np.zeros(N); vv[:len(v)] = bright * (1 - k) + dull * k
place(bus['fol'], vv * g, 0.0, 0.62, 0.35)    # she sits screen right
place(bus['fol'], breath(1.4, 'out', 77, 1.0), EV['quiet'] + 0.1, 0.06, 0.35)       # the sigh when she stops
place(bus['fol'], breath(1.0, 'out', 78, 1.0), EV['grey'][1] - 0.4, 0.04, 0.35)


# ---------------------------------------------------------------- his phone: thumb ticks, a blip now and then
def tick(seed, f=3600, g=1.0):
    n = int(0.05 * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    return (np.sin(2 * np.pi * f * (0.9 + 0.2 * r.random()) * t) * np.exp(-t / 0.004) + hp(noise(n), 4000) * env(n, 0.0002, 0.002)) * g

def blip(seed):
    n = int(0.35 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1320 * t) * np.exp(-t / 0.05) + 0.6 * np.sin(2 * np.pi * 1980 * t) * np.exp(-t / 0.035)) * np.minimum(1, t / 0.002)

t0 = 0.15
while t0 < EV['lookUp'][0]:
    place(bus['fol'], tick(int(t0 * 100)), t0, 0.05, -0.4); t0 += 0.35 + 0.5 * R.random()
for t0 in [1.7, 5.9, 9.1, 11.6]:
    place(bus['fol'], blip(int(t0 * 10)), t0, 0.05, -0.4)


# ---------------------------------------------------------------- the years: cutlery ticks, one per few dinners, quickening with the counter
def cutlery(seed):
    n = int(0.12 * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed); y = np.zeros(n)
    for m in [1.0, 2.7, 4.1]: y += np.sin(2 * np.pi * 2600 * m * (0.95 + 0.1 * r.random()) * t) * np.exp(-t / (0.02 / m))
    return y
d = np.array([f['dinner'] for f in FR]); last = 1
for f in range(1, len(FR)):
    if d[f] >= last + max(1, (d[f] - d[f - 1]) // 2) and f / FPS < EV['counterOut']:
        n_new = min(3, d[f] - last); last = d[f]
        for j in range(n_new):
            place(bus['fol'], cutlery(f * 7 + j), f / FPS + j / FPS / 3, 0.02 + 0.03 * f / len(FR), R.uniform(-0.3, 0.5))


# ---------------------------------------------------------------- the look-up: held breath, one cold hit, the phone face down
place(bus['hit'], lp(sub_boom(4.0), 240), LOOK, 0.32, 0.0)
cold = np.sin(2 * np.pi * 55 * np.arange(int(4.5 * SR)) / SR) + 0.5 * np.sin(2 * np.pi * 82.4 * np.arange(int(4.5 * SR)) / SR)   # A1 + E2: open, cold
cold *= (1 - np.exp(-np.arange(len(cold)) / SR / 0.3)) * np.exp(-np.arange(len(cold)) / SR / 2.2)
place(bus['hit'], np.tanh(1.3 * cold) * 0.5, LOOK + 0.05, 0.14, 0.0)
place(bus['fol'], mixs(thud(91, 140, 0.05, 1.0), tick(92, 2200, 0.8)), EV['phoneDown'][1] - 0.05, 0.3, -0.3)   # phone on wood, face down


# ---------------------------------------------------------------- bed, the held breath, master
room_g = np.interp(T, [0, 3, 12.5, LOOK, DUR], [0.3, 0.32, 0.36, 0.3, 0.34])
drone_g = np.interp(T, [0, 3, 10, 12.55, LOOK, LOOK + 0.5, DUR], [0.1, 0.15, 0.4, 0.6, 0.0, 0.3, 0.25])
duck = 1 - 0.96 * ((T > 12.6) & (T < LOOK)); duck = lp(duck, 30)
bed(bus, room_g, drone_g, duck)
mix = finish(bus, duck)
write_wav(mix, sys.argv[2])
print('mix ok', sys.argv[2])
