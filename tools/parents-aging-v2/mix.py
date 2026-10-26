"""Sound for Parents V2 (series kit ../slow-light-dark-common/sld_sound.py).

A soft synthesised piano under the three ages (warm at 8, thinner at 25) that cuts into the 0.2 s of black. Spoons on
steel and morning birds at 8; at 18 the chair shoved back, his footsteps going away, Mom's receiver and his phone; at 25
the laptop keys far away, her call buzzing out unanswered and the clock. Then the empty chair: one ring of the red phone
at 15 s and dead silence (room tone included) from 16 s to the end. Synthesised in numpy plus the kit's CC0 room tone
(sleepCircle "wind.ogg", Freesound 22331).

  python3 mix.py META.json OUT.wav
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_sound import *

meta = json.load(open(sys.argv[1])); EV = meta['events']; SCN = EV['scenes']
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


# ---------------------------------------------------------------- the piano: warm and sparse, thins at 25, stops at the black
NOTE = lambda name: 440 * 2 ** ((name - 69) / 12)
bar = 1.9; prog = [[50, 57, 62, 66], [47, 54, 59, 62], [43, 50, 55, 59], [45, 52, 57, 61]]  # D, Bm, G, A
end_piano = SCN[3] - 0.1
tt = 0.0; bi = 0
while tt < end_piano:
    ch = prog[bi % 4]; thin = np.interp(tt, [0, SCN[2], end_piano], [1.0, 0.8, 0.5])
    place(bus['mus'], piano(NOTE(ch[0]), 3.6, 0.55 * thin), tt, 0.5, -0.2)
    for k, nn in enumerate([ch[2], ch[3], ch[1] + 12]):
        tn = tt + bar * (0.33 + 0.27 * k)
        if tn < end_piano and (k < 2 or thin > 0.7):
            place(bus['mus'], piano(NOTE(nn + 12), 2.6, 0.42 * thin), tn, 0.35, 0.25 - 0.2 * k)
    tt += bar; bi += 1
place(bus['mus'], piano(NOTE(74), 2.5, 0.5), EV['call18'][0] + 0.6, 0.35, 0.1)          # he picks up at 18
# hard cut of the piano into the black (a short release, not a click)
mfade = np.clip((SCN[3] - T) / 0.12, 0, 1); bus['mus'] *= mfade[None]

# ---------------------------------------------------------------- 8: morning birds, spoons on steel, the ladle, Dad's laugh
for k, tb in enumerate(np.arange(0.15, SCN[1], 0.6)):
    place(bus['air'], chirp(10 + k), tb + 0.2 * R.random(), 0.14, R.uniform(-0.7, 0.7))
for k, tc in enumerate([0.55, 1.15, 1.85, 2.45, 3.1, 3.6]):
    place(bus['fol'], chink(20 + k, 2300 + 300 * R.random()), tc, 0.18, R.uniform(-0.3, 0.3))
place(bus['fol'], chink(30, 1700) + chink(31, 2100), EV['serve'][0] + 1.1, 0.25, 0.15)
# ---------------------------------------------------------------- 18: the chair shoved back, the bag, his footsteps going away; Mom's call
place(bus['fol'], scrape(0.4, 4, 0.6), EV['stand'][0], 0.5, 0.0)
place(bus['fol'], rustle(0.5, 5), EV['stand'][1] - 0.2, 0.3, 0.1)
tw = EV['leave'][0] + 0.3; k = 0
while tw < SCN[2] - 0.1:
    place(bus['fol'], thud(30 + k, 85, 0.07, 0.55), tw, np.interp(tw, [EV['leave'][0], SCN[2]], [0.8, 0.25]), 0.2 + 0.06 * k); tw += 0.5; k += 1
place(bus['fol'], clack(40), EV['call18'][0] + 0.1, 0.4, -0.25)
place(bus['fol'], buzz(0.45, 1), EV['call18'][0] + 0.15, 0.5, 0.4)
place(bus['fol'], clack(41, 0.8), EV['call18'][1] - 0.1, 0.35, -0.25)
# ---------------------------------------------------------------- 25: laptop keys far away, her call, his phone buzzing out unanswered, the clock
lap = lp(hp(noise(N), 3000), 6000) * 0.006 * ((T > SCN[2]) & (T < SCN[3]))
bus['air'][1] += lap
tk = SCN[2] + 0.1
while tk < SCN[3] - 0.1:
    place(bus['fol'], click(int(tk * 100), 3200, 0.12), tk, 0.15, 0.45); tk += 0.09 + 0.12 * R.random()
place(bus['fol'], clack(42), EV['call25'][0] + 0.1, 0.45, -0.25)
place(bus['fol'], buzz(EV['call25'][1] - EV['call25'][0] - 0.6, 2), EV['call25'][0] + 0.3, 0.42, 0.45)
place(bus['fol'], clack(43, 0.7), EV['call25'][1] - 0.15, 0.35, -0.25)
tc = SCN[2] + 0.25; k = 0
while tc < SCN[3] - 0.05:
    place(bus['fol'], tick(k) * (1.0 if k % 2 else 0.8), tc, np.interp(tc, [SCN[2], SCN[3]], [0.12, 0.3]), -0.1); tc += 0.5; k += 1
# ---------------------------------------------------------------- the end: black (a breath of nothing), the empty chair, one ring, silence
place(bus['hit'], bell_ring(0.75, 99), EV['ring'], 0.9, -0.05)
place(bus['hit'], thud(98, 60, 0.3, 0.6), EV['ring'], 0.5, 0.0)

# ---------------------------------------------------------------- bed and master
room_g = np.interp(T, [0, SCN[2], SCN[3], SCN[3] + 0.01, DUR], [0.2, 0.26, 0.28, 0.0, 0.0])
room_g = np.where((T >= SCN[4]) & (T < EV['silence']), 0.2, room_g)
drone_g = np.interp(T, [0, SCN[2], SCN[3], SCN[3] + 0.01, DUR], [0.0, 0.2, 0.4, 0.0, 0.0])
duck = np.clip(1 - (T - EV['silence'] + 0.25) / 0.25, 0, 1)
bed(bus, room_g, drone_g, np.ones(N))
mus = bus.pop('mus')
for c in range(2):
    mus[c] = hp(mus[c], 60, 2)
ir = [reverb_ir(2.6, 3000, 11), reverb_ir(2.6, 3000, 12)]
mus = mus * 0.7 + np.stack([convolve(mus[c], ir[c]) for c in range(2)]) * 0.45 * np.clip((SCN[3] + 0.6 - T) / 0.6, 0, 1)[None]
bus['air'] += mus * 0.55
mix = finish(bus, duck)
mix *= duck[None]          # the last three seconds are dead air
write_wav(mix, sys.argv[2])
print('mix ok', mix.shape, 'silence from', EV['silence'])
