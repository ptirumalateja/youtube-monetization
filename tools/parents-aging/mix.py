"""Sound for Your Parents Are Aging: soft, then empty (series kit ../slow-light-dark-common/sld_sound.py).

One soft piano (synthesised, a few warm notes per bar, never a wall), morning birds at 8, the steel tiffin, a hug, his
footsteps into the dark. The lamp click over his desk. Every call: her receiver lifted, the gold light's shimmer crossing
the dark, his phone buzzing; picked up at 18, buzzing out at 23 and 25, a short call he makes at 28 and the old bell
of the red phone. A clock takes over while they wait. The piano stops before the end: one ring of the red phone, then
a full second of dead silence (everything, room tone included, goes to zero) so the reel feels like it ended.

Everything is synthesised in numpy, plus the kit's CC0 room tone (sleepCircle "wind.ogg", Freesound 22331).

  python3 mix.py META.json OUT.wav
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_sound import *

meta = json.load(open(sys.argv[1])); EV = meta['events']
DUR = EV['duration']; N = int(DUR * SR); T = np.arange(N) / SR
R = np.random.default_rng(38)
bus = new_buses(N)
bus['mus'] = np.zeros((2, N))


# ---------------------------------------------------------------- sources
def mixs(*sig):
    """Sum signals of different lengths."""
    y = np.zeros(max(len(x) for x in sig))
    for x in sig: y[:len(x)] += x
    return y


def piano(f, dur=3.2, vel=1.0):
    """A soft felt piano note: slightly inharmonic partials, hammer thump, two-stage decay."""
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k in range(1, 9):
        fk = f * k * np.sqrt(1 + 0.00035 * k * k)
        if fk > 7000: break
        a = (1 / k ** 1.4) * (0.6 + 0.4 * vel)
        y += a * np.sin(2 * np.pi * fk * t + R.random() * 6) * (0.65 * np.exp(-t / (0.5 / k ** 0.4)) + 0.35 * np.exp(-t / (2.8 / k ** 0.6)))
    y += lp(noise(n), 900) * env(n, 0.001, 0.012) * 0.08 * vel
    y = lp(y, 2400 + 1800 * vel)
    return y * np.minimum(1, t / 0.004) * vel


def bell_ring(dur=0.75, seed=0):
    """An old landline bell: two struck gongs (about 440/480 Hz plus inharmonic modes) hammered about 20 times a second."""
    n = int(dur * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    hammer = (np.sin(2 * np.pi * 20 * t) > 0.6).astype(float)
    y = np.zeros(n)
    for f0 in (440 * (0.99 + 0.02 * r.random()), 486):
        modes = sum(np.sin(2 * np.pi * f0 * m * t) * g for m, g in [(1, 1), (2.76, 0.5), (5.4, 0.25), (8.9, 0.12)])
        y += modes * lp(hammer, 60)
    y = y * 0.25 + hp(noise(n), 2500) * lp(hammer, 200) * 0.04
    return y * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.06)


def buzz(dur, seed=0):
    """A phone vibrating on a wooden desk: 150 Hz motor + a rattle on the wood, in pulses."""
    n = int(dur * SR); t = np.arange(n) / SR
    gate = lp((np.sin(2 * np.pi * 1.6 * t - 0.4) > -0.2).astype(float), 30)
    motor = np.sign(np.sin(2 * np.pi * 152 * t)) * 0.3 + np.sin(2 * np.pi * 152 * t)
    wood = bp(noise(n), 320, 1.5) * 0.6
    return lp(motor * 0.35 + wood * np.abs(np.sin(2 * np.pi * 152 * t)), 1600) * gate


def click(seed, f=2200, g=1.0):
    n = int(0.12 * SR); t = np.arange(n) / SR
    return (hp(noise(n), 1200) * env(n, 0.0002, 0.004) + np.sin(2 * np.pi * f * t) * env(n, 0.0005, 0.012) * 0.4) * g


def clack(seed, g=1.0):
    """Plastic receiver lifted off / set on the cradle."""
    n = int(0.25 * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    y = sum(np.sin(2 * np.pi * f * (0.95 + 0.1 * r.random()) * t) * np.exp(-t / d) for f, d in [(780, 0.03), (1650, 0.015), (2900, 0.008)])
    return (y * 0.4 + bp(noise(n), 2000, 1.2) * env(n, 0.0005, 0.01) * 0.8 + thud(seed, 120, 0.04, 0.3)[:n]) * g


def chirp(seed):
    """A small morning bird: a few fast down-sweeping whistles."""
    r = np.random.default_rng(seed); out = np.zeros(int(0.6 * SR)); tt = 0.0
    for k in range(r.integers(2, 5)):
        d = 0.05 + 0.05 * r.random(); n = int(d * SR); t = np.arange(n) / SR
        f = (3600 + 1400 * r.random()) - 1500 * t / d
        s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / d) ** 2
        i = int(tt * SR); out[i:i + n] += s[:len(out) - i]; tt += d + 0.03 + 0.05 * r.random()
    return out * 0.5


def shimmer(dur, up=True):
    """The gold light crossing the dark: a soft rising (or falling) glassy glissando with sparkle."""
    n = int(dur * SR); t = np.arange(n) / SR; u = t / dur
    f = 700 * 2 ** ((u if up else 1 - u) * 1.3)
    y = sum(np.sin(2 * np.pi * np.cumsum(f * m) / SR) * g for m, g in [(1, 1), (2.01, 0.4), (3.02, 0.18)])
    sp = hp(noise(n), 5000) * (np.random.default_rng(3).random(n) > 0.997) * 2
    return (y * 0.25 + lp(sp, 9000) * 0.3) * np.sin(np.pi * np.minimum(1, u)) ** 1.2


def rustle(dur, seed):
    n = int(dur * SR); x = np.random.default_rng(seed).standard_normal(n); t = np.arange(n) / n
    return (bp(x, 1800, 1.0) * 0.5 + bp(x, 4200, 1.6) * 0.3) * np.sin(np.pi * t) ** 1.5


def tick(seed):
    n = int(0.08 * SR); t = np.arange(n) / SR
    return hp(noise(n), 1500) * env(n, 0.0002, 0.003) * 0.7 + np.sin(2 * np.pi * 3100 * t) * env(n, 0.0004, 0.006) * 0.25 + np.sin(2 * np.pi * 900 * t) * env(n, 0.001, 0.02) * 0.2


# ---------------------------------------------------------------- the piano: warm and sparse, thins with the years, stops before the ring
NOTE = lambda name: 440 * 2 ** ((name - 69) / 12)
# D major / B minor colour, low and soft; (time, midi, vel)
bar = EV.get('pianoBar', 1.9)
prog = [[50, 57, 62, 66], [47, 54, 59, 62], [43, 50, 55, 59], [45, 52, 57, 61]]  # D, Bm, G, A
end_piano = EV['narrow'][0] + 0.3
tt = 0.0; bi = 0
while tt < end_piano:
    ch = prog[bi % 4]; thin = np.interp(tt, [0, EV['cut'], EV['push'][0], end_piano], [1.0, 0.85, 0.6, 0.45])
    place(bus['mus'], piano(NOTE(ch[0]), 3.6, 0.55 * thin), tt, 0.5, -0.2)
    for k, nn in enumerate([ch[2], ch[3], ch[1] + 12]):
        tn = tt + bar * (0.33 + 0.27 * k)
        if tn < end_piano and (k < 2 or thin > 0.7):
            place(bus['mus'], piano(NOTE(nn + 12), 2.6, 0.42 * thin), tn, 0.35, 0.25 - 0.2 * k)
    tt += bar; bi += 1
# the melody note that answers each picked-up call (warm), and a lone high note on the payoff
for c in EV['calls']:
    if c['ans']:
        place(bus['mus'], piano(NOTE(74 if c['dir'] == 'in' else 78), 2.5, 0.5), c['t'] + c['dur'] * 0.68, 0.35, 0.1)
place(bus['mus'], piano(NOTE(81), 3.0, 0.45), EV['line'] + 0.05, 0.35, 0.0)

# ---------------------------------------------------------------- morning at 8: birds, the tiffin, the hug, Dad's laugh-paper
for k, tb in enumerate(np.arange(0.1, EV['grow'][0] + 0.5, 0.55) + R.random(6)[0] * 0.2):
    place(bus['air'], chirp(10 + k), tb + 0.2 * R.random(), 0.16 * np.interp(tb, [0, EV['grow'][0] + 0.5], [1, 0.2]), R.uniform(-0.7, 0.7))
place(bus['fol'], chink(5, 2600) * 1.4 + chink(6, 1900), EV['take'][1] - 0.05, 0.28, 0.1)
place(bus['fol'], chink(7, 2300), EV['take'][1] + 0.1, 0.3, 0.1)
place(bus['fol'], rustle(0.6, 2), EV['hug'][0], 0.35, 0.05)
place(bus['fol'], rustle(0.4, 3), 0.95, 0.12, -0.4)                     # paper
place(bus['fol'], scrape(0.35, 4, 0.5), EV['dadUp'][0] + 0.15, 0.4, -0.4)  # Dad's chair back
place(bus['fol'], rustle(0.5, 5), EV['release'][0], 0.3, 0.1)
# footsteps into the dark
tw = EV['walk'][0] + 0.25; k = 0
while tw < EV['cut']:
    place(bus['fol'], thud(30 + k, 85, 0.07, 0.55), tw, np.interp(tw, [EV['walk'][0], EV['cut']], [0.8, 0.35]), 0.3 + 0.08 * k); tw += 0.5; k += 1

# ---------------------------------------------------------------- the city: the lamp click, the laptop hum
place(bus['hit'], mixs(click(1, 1800, 1.0), thud(2, 90, 0.05, 0.4)), EV['lampOn'] - 0.01, 0.55, 0.3)
lap = lp(hp(noise(N), 3000), 6000) * 0.006 * np.clip((T - EV['lampOn']) / 0.2, 0, 1) * np.interp(T, [0, EV['push'][0], EV['push'][1]], [1, 1, 0.3])
bus['air'][1] += lap

# ---------------------------------------------------------------- the calls
for i, c in enumerate(EV['calls']):
    t0, d = c['t'], c['dur']
    if c['dir'] == 'in':
        place(bus['fol'], clack(40 + i), t0 + 0.06 * d, 0.45, -0.25)                 # she lifts the receiver
        place(bus['air'], shimmer(0.46 * d, True), t0 + 0.1 * d, 0.28, 0.1)
        bz = (0.18 * d) if c['ans'] else ((0.15 * d) if c.get('flip') else 0.38 * d)
        place(bus['fol'], buzz(bz, i), t0 + 0.54 * d, 0.55, 0.35)
        if c.get('flip'): place(bus['fol'], thud(60 + i, 140, 0.04, 0.5), t0 + 0.69 * d, 0.5, 0.35)
        place(bus['fol'], clack(50 + i, 0.8), t0 + (0.97 if c['ans'] else 1.08) * d, 0.4, -0.25)   # receiver back down
    else:
        place(bus['fol'], click(70 + i, 2600, 0.5), t0 + 0.02 * d, 0.3, 0.35)
        place(bus['air'], shimmer(0.38 * d, False), t0 + 0.12 * d, 0.28, -0.1)
        place(bus['fol'], bell_ring(0.14 * d, i), t0 + 0.48 * d, 0.32, -0.2)
        place(bus['fol'], clack(80 + i), t0 + 0.58 * d, 0.45, -0.25)
        place(bus['fol'], clack(90 + i, 0.8), t0 + 1.08 * d, 0.4, -0.25)

# ---------------------------------------------------------------- waiting: the clock, louder as we push in, stops with the ring
tc = EV['stick']; k = 0
while tc < EV['ring'] - 0.05:
    g = np.interp(tc, [EV['stick'], EV['push'][0], EV['push'][1], EV['ring']], [0.08, 0.14, 0.32, 0.36])
    place(bus['fol'], tick(k) * (1.0 if k % 2 else 0.8), tc, g, -0.1); tc += 0.5; k += 1

# ---------------------------------------------------------------- the end: one ring of the red phone, then nothing
place(bus['hit'], bell_ring(0.75, 99), EV['ring'], 0.9, -0.05)
place(bus['hit'], thud(98, 60, 0.3, 0.6), EV['ring'], 0.5, 0.0)

# ---------------------------------------------------------------- bed and master
room_g = np.interp(T, [0, EV['cut'], EV['push'][0], EV['ring'], DUR], [0.2, 0.28, 0.3, 0.26, 0.26])
drone_g = np.interp(T, [0, EV['cut'], EV['push'][0], EV['push'][1], EV['ring']], [0.0, 0.15, 0.25, 0.45, 0.5])
# total silence after the ring: everything (bed included) fades to zero at 'silence', a short tail before it
duck = np.clip(1 - (T - EV['silence'] + 0.25) / 0.25, 0, 1)
bed(bus, room_g, drone_g, np.ones(N))
mus = bus.pop('mus')
for c in range(2):
    mus[c] = hp(mus[c], 60, 2)
ir = [reverb_ir(2.6, 3000, 11), reverb_ir(2.6, 3000, 12)]
mus = mus * 0.7 + np.stack([convolve(mus[c], ir[c]) for c in range(2)]) * 0.45
bus['air'] += mus * 0.55
mix = finish(bus, duck)
mix *= duck[None]          # hits too: the second after the ring is dead air
write_wav(mix, sys.argv[2])
print('mix ok', mix.shape, 'silence from', EV['silence'])
