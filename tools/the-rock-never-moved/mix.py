"""Sound for The Rock Never Moved. Synthesised (numpy) + the kit's CC0 room tone. Every sound sits on a timeline.json time.

- Each cut opens on the impact: a heavy body-into-stone thud + a sub kick + a forced breath out; a short clack as the
  DAY counter lands. The kicks get closer as the cuts speed up, and a low drone climbs under the montage.
- The mockers get a dry 'ha-ha' (two band-passed noise syllables) in their cuts.
- The stop: the music drops out to near silence (room tone and his breathing) under "IT NEVER MOVED."
- The lift: a rising rumble from the grip, a strained breath, then the boom (sub + hit + dust) as the rock locks out
  overhead, and a warm open chord through the end lines.

  python3 mix.py META.json OUT.wav
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_sound import SR, lp, hp, bp, env, noise, place, thud, breath, sub_boom, new_buses, curve, bed, finish, write_wav

EV = json.load(open(sys.argv[1]))['events']
DUR = EV['duration']; N = int(DUR * SR); bus = new_buses(N)


def mixs(*sig):
    y = np.zeros(max(len(x) for x in sig))
    for x in sig: y[:len(x)] += x
    return y
def tone(f, dur, dec, harm=(1, 0.5, 0.25)):
    n = int(dur * SR); t = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * (k + 1) * t) for k, a in enumerate(harm)) * np.exp(-t / dec) * np.minimum(1, t / 0.004)
def kick(f0=95, f1=42, dec=0.28):
    n = int(0.6 * SR); t = np.arange(n) / SR; f = f1 + (f0 - f1) * np.exp(-t / 0.04)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / dec) * np.minimum(1, t / 0.002)
def clack(seed):
    n = int(0.08 * SR); r = np.random.default_rng(seed)
    return lp(bp(r.standard_normal(n), 1800, 2.5), 6000) * np.exp(-np.arange(n) / SR / 0.012) * np.minimum(1, np.arange(n) / SR / 0.0015)
def haha(seed, f0):
    out = np.zeros(int(0.5 * SR)); r = np.random.default_rng(seed)
    for k in range(2):
        n = int(0.11 * SR); s = bp(r.standard_normal(n), f0 * (1 + 0.1 * k), 3) + 0.5 * bp(r.standard_normal(n), f0 * 2.6, 4)
        s *= np.sin(np.pi * np.arange(n) / n) ** 2; i = int(k * 0.17 * SR); out[i:i + n] += s
    return out / np.abs(out).max()
def rumble(dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = noise(n)
    lo = lp(x, 120) * 3; mid = bp(x, 300, 2) * (t / dur) ** 2
    return (lo + mid) * (t / dur) ** 1.5 * np.minimum(1, (dur - t) / 0.03)

cuts = EV['cuts']; lag = EV['impactLag']
# ---- the montage: an impact on every cut, harder as he grows
for i, (t0, day) in enumerate(cuts):
    ti = t0 + lag; g = 0.75 + 0.35 * i / (len(cuts) - 1)
    place(bus['hit'], mixs(thud(10 + i, 62, 0.2, 1.0), 0.5 * kick()), ti, 0.55 * g, 0.0)
    place(bus['fol'], lp(hp(noise(int(0.12 * SR)), 400), 3000) * env(int(0.12 * SR), 0.002, 0.05), ti, 0.12, 0.15)   # palms slap the stone
    place(bus['fol'], breath(0.45, 'out', 30 + i, 1.0), ti + 0.02, 0.28 * g, 0.1)
    place(bus['air'], clack(50 + i), ti + 0.01, 0.12, 0.0)
    # feet scraping back under the push
    place(bus['fol'], lp(hp(noise(int(0.3 * SR)), 900), 4000) * env(int(0.3 * SR), 0.05, 0.12), ti + 0.18, 0.05, 0.3)
    # an off-beat kick between the slow early cuts, so the pulse never stops
    t1 = cuts[i + 1][0] + lag if i + 1 < len(cuts) else None
    if t1 and t1 - ti > 0.55: place(bus['hit'], kick(80, 45, 0.18), (ti + t1) / 2, 0.22, 0.0)
for c in EV['mock']:
    place(bus['fol'], haha(70 + c, 520), cuts[c][0] + 0.15, 0.1, -0.5)
    place(bus['fol'], haha(80 + c, 380), cuts[c][0] + 0.3, 0.09, -0.35)

# ---- the stop: he steps back, breathes, looks at his arms
st = EV['stop']
place(bus['fol'], breath(0.7, 'in', 90, 1.0), st['off'] + 0.05, 0.16, 0.1)
for k, ts in enumerate([st['off'] + 0.15, st['off'] + 0.42]): place(bus['fol'], thud(95 + k, 90, 0.08, 1.0), ts, 0.12, 0.2)
place(bus['fol'], breath(1.0, 'out', 91, 1.0), st['look0'] + 0.1, 0.16, 0.1)

# ---- the lift: rumble + strain into the boom, then a warm open chord
L = EV['lift']; B = EV['boom']
place(bus['hit'], thud(120, 55, 0.25, 1.0), L['grip'], 0.4, 0.0)                    # hands lock on the stone
place(bus['air'], rumble(B - L['grip']), L['grip'], 0.22, 0.0)
place(bus['fol'], breath(0.6, 'in', 121, 1.0), L['chest0'] - 0.1, 0.22, 0.0)
place(bus['fol'], breath(0.5, 'out', 122, 1.0), L['press0'], 0.3, 0.0)
place(bus['hit'], sub_boom(3.0), B, 0.9, 0.0)
place(bus['hit'], mixs(thud(130, 48, 0.4, 1.0), kick(110, 38, 0.5)), B, 0.6, 0.0)
place(bus['fol'], lp(noise(int(1.2 * SR)), 700) * env(int(1.2 * SR), 0.01, 0.5), B + 0.02, 0.18, 0.0)   # dust
chord = sum(tone(f, DUR - B - 0.3, 2.2, (1, 0.3)) for f in (110, 164.8, 220, 277.2, 329.6))
place(bus['air'], chord * np.minimum(1, np.arange(len(chord)) / SR / 0.6), B + 0.3, 0.07, 0.0)

# ---- bed: drone climbs through the montage, drops out for the stop, returns low under the end
T = np.arange(N) / SR
pitch_g = curve(N, [(0, 0.35), (cuts[-1][0], 0.85), (st['off'], 0.9), (st['off'] + 0.15, 0.0), (L['cut'], 0.0), (B, 0.3), (DUR, 0.25)])
room_g = curve(N, [(0, 0.25), (DUR, 0.25)])
duck = curve(N, [(0, 1), (st['off'] + 0.1, 1), (st['off'] + 0.3, 0.35), (L['cut'], 0.35), (L['cut'] + 0.05, 1), (DUR, 1)])
bed(bus, room_g, pitch_g, duck)
mix = finish(bus, duck)
write_wav(mix, sys.argv[2])
print('mix ok', sys.argv[2])
