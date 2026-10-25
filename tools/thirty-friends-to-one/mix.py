"""Sound for 30 Friends to 1: minimal but heavy (series kit ../slow-light-dark-common/sld_sound.py).

A crowded table at 20 (thirty synthesised voices murmuring and laughing, glass clinks on the toast) that thins out with
every departure: a chair shoved back, a chair pushed in, footsteps fading into the dark. A slow clock tick takes over as the
table empties. At 60: the tick, a glass slid across the wood, a held breath, then the one toast: a warm heavy clink and a
soft low warm tone. Everything is synthesised in numpy, plus the kit's CC0 room tone (sleepCircle "wind.ogg", Freesound 22331).

Sync comes from the scene: META.json (render.cjs meta) holds every departure time (td, speed sp) and the story times.

  python3 mix.py META.json OUT.wav
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_sound import *

meta = json.load(open(sys.argv[1])); EV = meta['events']; DEPS = EV['deps']
DUR = EV['duration']; N = int(DUR * SR); T = np.arange(N) / SR
R = np.random.default_rng(30)
sst = lambda a, b, x: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
left_at = {d['id']: d['td'] + 0.62 / d['sp'] for d in DEPS}
CLINK = EV['clink']

def mixs(*sig):
    """Sum signals of different lengths."""
    y = np.zeros(max(len(x) for x in sig))
    for x in sig: y[:len(x)] += x
    return y

bus = new_buses(N)
bus['crowd'] = np.zeros((2, N))


# ---------------------------------------------------------------- voices: 30 friends + the hero talking and laughing (memory-muffled)
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

energy = lambda t: float(np.interp(t, [0, 2.5, 8.5, 10], [0.95, 0.85, 0.35, 0.2]))
for i in range(31):   # 30 friends + the hero (30); from 35 to 60 only the two of them still talk, quietly
    t_end = left_at.get(i, 13.0) if i not in (0, 30) else 12.6
    f0 = 95 + 90 * R.random()
    y = voice(100 + i, f0, t_end, energy)
    pan = float(np.clip(R.uniform(-0.8, 0.8), -1, 1))
    place(bus['crowd'], y / (np.abs(y).max() + 1e-9), 0.0, 0.17, pan)
# the room swallows them as it empties: crowd low-passed harder over the years
crowd_g = np.interp(T, [0, 2.8, 6, 9, 12.5, 13.4], [1.0, 0.95, 0.7, 0.5, 0.4, 0.0])
for c in range(2):
    x = bus['crowd'][c]; bright, dull = lp(hp(x, 140), 3200), lp(hp(x, 140), 1100)
    k = np.interp(T, [0, 4, 11], [0, 0.3, 1.0]); bus['crowd'][c] = (bright * (1 - k) + dull * k) * crowd_g


# ---------------------------------------------------------------- glass: clinks on the toast at 20, the slide and the toast at 60
def glass_tick(seed, f0=3100, dec=0.18, gain=1.0):
    r = np.random.default_rng(seed); n = int((dec * 4 + 0.05) * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for m, a in [(1.0, 1.0), (1.62, 0.6), (2.37, 0.4), (3.11, 0.25)]:
        y += a * np.sin(2 * np.pi * f0 * m * (0.97 + 0.06 * r.random()) * t + r.random() * 6) * np.exp(-t / (dec / m ** 0.5))
    return (y + hp(noise(n), 4000) * env(n, 0.0002, 0.003) * 0.8) * gain

for j in range(26):   # the frame-0 toast: glasses meeting all along the table
    t0 = 0.35 + 1.1 * R.random() ** 1.3
    place(bus['fol'], glass_tick(500 + j, 2500 + 1600 * R.random(), 0.12 + 0.1 * R.random()), t0, 0.05 + 0.05 * R.random(), R.uniform(-0.8, 0.8))
for j in range(10):   # a few later clinks while they still drink together
    t0 = 1.8 + 6.5 * R.random()
    if R.random() < energy(t0): place(bus['fol'], glass_tick(600 + j, 2800 + 1200 * R.random(), 0.1), t0, 0.03, R.uniform(-0.7, 0.7))


# ---------------------------------------------------------------- departures: chair shoved back, chair pushed in, footsteps fading
def chair_scrape(dur, seed, gain=1.0, pitch=1.0):
    """A wooden chair dragged on concrete: stick-slip grain through two wood resonances + a low leg thump."""
    r = np.random.default_rng(seed); n = int(dur * SR); x = r.standard_normal(n)
    grain = np.repeat(r.random(n // 160 + 1), 160)[:n] ** 4
    chatter = (np.sin(2 * np.pi * np.cumsum(55 * pitch + 25 * r.random() + 15 * np.sin(np.arange(n) / SR * 9)) / SR) > 0.7).astype(float)
    y = bp(x * (0.25 + grain) + chatter * 0.5, 420 * pitch, 1.4) + bp(x * grain, 1300 * pitch, 2.2) * 0.6 + lp(chatter, 300) * 0.4
    e = np.minimum(1, np.arange(n) / (0.03 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.08 * SR))
    return y * e * gain

def wood_knock(seed, gain=1.0):
    n = int(0.4 * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    y = sum(np.sin(2 * np.pi * f * (0.95 + 0.1 * r.random()) * t) * np.exp(-t / d) for f, d in [(180, 0.08), (410, 0.05), (950, 0.025)])
    return (y + lp(noise(n), 2000) * env(n, 0.0005, 0.01)) * gain

def step(seed, gain=1.0):
    """A footstep on concrete: heel weight + scuff."""
    n = int(0.8 * SR); r = np.random.default_rng(seed)
    return thud(seed, 85 + 20 * r.random(), 0.07, 0.9) * gain + bp(noise(n), 1800, 1.2) * env(n, 0.002, 0.03) * 0.25 * gain

for d in DEPS:
    td, sp, pan = d['td'], d['sp'], d['pan'] * 0.8
    far = 1 - 0.55 * d['seat'] / 14          # far seats are quieter
    lone = 1 + 0.4 * d['k'] / 28              # each departure is a little heavier as the table empties
    g = 0.17 * far * lone
    place(bus['fol'], chair_scrape(0.32 / sp, 700 + d['id'], 1.0, 1 + 0.15 * R.random()), td + 0.02 / sp, g, pan)
    place(bus['fol'], chair_scrape(0.38 / sp, 800 + d['id'], 0.7, 0.9), td + 0.86 / sp, g * 0.8, pan)
    place(bus['fol'], wood_knock(900 + d['id']), td + 1.24 / sp, g * 0.6, pan)
    # footsteps: real speed 1.15*sp m/s, a step every 0.65 m, fading with the figure (tt 1.5 -> 3.3)
    tt = 1.36; s = 0
    while tt < 3.4:
        a = 1 - np.clip((tt - 1.5) / 1.8, 0, 1) ** 1.2
        place(bus['fol'], step(1000 + d['id'] * 10 + s, 1.0), td + tt / sp, g * 0.85 * a, pan * (1 + 0.15 * (tt - 1.3)))
        tt += 0.65 / 1.15 if tt > 1.75 else 0.42; s += 1


# ---------------------------------------------------------------- the clock: creeps in as the table empties, alone at 60
def tick(seed, tock=False):
    n = int(0.25 * SR); t = np.arange(n) / SR; f = 2300 if not tock else 1900
    y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.008) * 0.6 + np.sin(2 * np.pi * (f * 0.41) * t) * np.exp(-t / 0.02) * 0.5
    y += np.sin(2 * np.pi * 520 * t) * np.exp(-t / 0.04) * 0.35   # the wooden case
    return y + hp(noise(n), 3500) * env(n, 0.0002, 0.002) * 0.7

for k, t0 in enumerate(np.arange(7.0, 15.6, 1.0)):
    g = float(np.interp(t0, [7, 10, 12.5, 13.5, 15], [0.03, 0.08, 0.16, 0.26, 0.24]))
    place(bus['fol'], tick(k, k % 2 == 1), t0, g, 0.35)


# ---------------------------------------------------------------- at 60: the slide, the take, the held breath, the toast
n = int((EV['slideStop'] - EV['slideGo'] + 0.05) * SR); ts = np.arange(n) / SR; u = ts / ts[-1]
vel = 2.2 * (1 - u) ** 1.2   # matches the glass's ease-out in scene.js
slide = (bp(noise(n), 1700, 1.3) * 0.6 + bp(noise(n), 620, 2.0) * 0.5) * vel / 2.2 * np.minimum(1, ts / 0.02)
place(bus['fol'], slide, EV['slideGo'], 0.22, 0.1)
place(bus['fol'], mixs(glass_tick(1500, 1900, 0.06, 0.6), wood_knock(1501, 0.5)), EV['slideGo'] - 0.02, 0.12, 0.1)    # fingers on the glass
place(bus['fol'], wood_knock(1502, 0.6), EV['slideStop'], 0.14, 0.15)                                          # it stops in front of him
place(bus['fol'], mixs(glass_tick(1503, 2100, 0.05, 0.5), wood_knock(1504, 0.4)), EV['take'] + 0.1, 0.12, 0.2)      # he takes it
place(bus['fol'], breath(0.9, 'in', 1600, 1.0), CLINK - 1.05, 0.05, 0.0)

def toast(seed):
    """Two heavy tumblers meeting: low glass modes + a bright ring + a short body knock (warm, heavy)."""
    r = np.random.default_rng(seed); n = int(3.0 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for f, a, d in [(1180, 0.9, 0.55), (1930, 0.7, 0.8), (2870, 0.55, 1.1), (3460, 0.4, 0.9), (4710, 0.3, 0.6), (6120, 0.15, 0.4)]:
        for det in (1.0, 1.004 + 0.003 * r.random()):   # two glasses, slightly detuned: a beating ring
            y += a * np.sin(2 * np.pi * f * det * t + r.random() * 6) * np.exp(-t / d) * 0.5
    body = np.sin(2 * np.pi * (150 + 80 * np.exp(-t / 0.01)) * t) * env(n, 0.002, 0.05) * 0.9
    crack = lp(hp(noise(n), 2500), 7000) * env(n, 0.0015, 0.006) * 0.5   # soft-edged: a 0.2 ms crack read +3.5 dBTP after AAC
    return (y * 0.5 + body + crack) * np.minimum(1, t / 0.0015)

def warm_tone(dur=4.2):
    """The soft low warm tone under the toast: D2 / A2 / D3 / F#3, slow bloom, gently saturated."""
    n = int(dur * SR); t = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) for f, a in [(73.4, 1.0), (110.0, 0.55), (146.8, 0.5), (185.0, 0.22), (220.0, 0.12)])
    e = (1 - np.exp(-t / 0.35)) * np.exp(-t / 1.9)
    return np.tanh(1.5 * y * e) * 0.7

place(bus['hit'], toast(1700), CLINK, 0.55, 0.05)
place(bus['hit'], warm_tone(), CLINK + 0.04, 0.16, 0.0)
place(bus['hit'], lp(sub_boom(3.0), 160), CLINK, 0.07, 0.0)    # weight under the clink, not a boom


# ---------------------------------------------------------------- bed, the held breath, master
room_g = np.interp(T, [0, 3, 13, 15.8, 16.2, 18], [0.32, 0.34, 0.4, 0.35, 0.3, 0.3])
drone_g = np.interp(T, [0, 3, 12.8, 13.4, 15.8, 16.2, 18], [0.12, 0.18, 0.45, 0.25, 0.22, 0.0, 0.0])
duck = 1 - 0.96 * ((T > 15.85) & (T < CLINK)) ; duck = lp(duck, 30)
bed(bus, room_g, drone_g, duck)
crowd = bus.pop('crowd'); bus['fol'] += crowd * 0.9
mix = finish(bus, duck)
write_wav(mix, sys.argv[2])
print('mix ok', sys.argv[2])
