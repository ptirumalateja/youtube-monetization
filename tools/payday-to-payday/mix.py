"""Sound for Payday to Payday: minimal but heavy, series kit (../slow-light-dark-common/sld_sound.py).

Bed = CC0 wind room tone + the lamp's 120 Hz hum + a 55 Hz drone. Foley with a visible cause for every sound (all synthesised in
numpy): leather wallet, paper whooshes and slaps as the bundles land, footsteps of the strangers, cloth, breath, a paper slide
and a small thud for every bundle taken. A held-breath silence just before the balance hits zero, then the only big hit
(sub_boom + the CC0 qubodup explosion read two octaves down). Then near silence until the wallet goes back in his pocket.

  python3 mix.py META.json OUT.wav        (META.json from `node render.cjs meta`)
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'slow-light-dark-common'))
from sld_sound import *

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'timeline.json')))


def whoosh(dur, f0, f1, seed, gain=1.0):
    """Paper/air whoosh: band noise swept from f0 to f1 with a rise-and-fall envelope."""
    n = int(dur * SR); r = np.random.default_rng(seed).standard_normal(n); t = np.arange(n) / n
    out = np.zeros(n); k = 6
    for i in range(k):  # sweep by crossfading fixed bands (cheap, zero-phase)
        fc = f0 * (f1 / f0) ** ((i + 0.5) / k); w = np.exp(-0.5 * ((t - (i + 0.5) / k) / (0.9 / k)) ** 2)
        out += bp(r, fc, 1.1) * w
    return out * np.sin(np.pi * t) ** 1.4 * gain * 0.6


def paper_slap(seed, gain=1.0):
    n = int(0.5 * SR); t = np.arange(n) / SR
    s = lp(noise(n), 3500) * env(n, 0.0008, 0.05) * 0.7 + np.sin(2 * np.pi * (110 + 60 * np.exp(-t / 0.02)) * t) * env(n, 0.002, 0.08) * 0.9
    return s * gain


def paper_slide(dur, seed, gain=1.0):
    n = int(dur * SR); x = np.random.default_rng(seed).standard_normal(n); t = np.arange(n) / n
    return (bp(x, 3200, 1.3) * 0.6 + hp(x, 5000) * 0.25) * np.sin(np.pi * t) ** 0.7 * gain


def leather(dur, seed, gain=1.0):
    """Wallet leather: a soft low rub and a small flap."""
    n = int(dur * SR); x = np.random.default_rng(seed).standard_normal(n); t = np.arange(n) / n
    return (bp(x, 700, 1.0) * 0.8 + bp(x, 1800, 1.6) * 0.3) * np.sin(np.pi * t) ** 0.9 * gain


def cloth(dur, seed, gain=1.0):
    n = int(dur * SR); x = np.random.default_rng(seed).standard_normal(n); t = np.arange(n) / n
    return lp(x, 1500) * np.sin(np.pi * t) ** 1.2 * gain * 0.5


def main(meta_path, out_path):
    M = json.load(open(meta_path)); D = TL['duration']; N = int(D * SR); t = np.arange(N) / SR
    bus = new_buses(N)
    zero = TL['zero']
    # silence as a beat: the last bundle is taken at 8.10, everything drops away 8.15-8.45 and the boom lands as the counter hits 0
    duck = curve(N, [(0, 1), (zero - 0.32, 1), (zero - 0.26, 0.0), (zero - 0.01, 0.0), (zero, 0.6), (zero + 1.2, 1), (D, 1)])
    room_g = curve(N, [(0, 0.11), (3, 0.12), (zero - 0.3, 0.14), (zero + 0.3, 0.0), (zero + 2.0, 0.025), (TL['push1'], 0.03), (TL['pocket'] - 0.3, 0.05), (TL['pocket'] + 0.6, 0.1), (D, 0.11)]) * duck
    drone_g = curve(N, [(0, 0.2), (3, 0.3), (zero - 0.3, 0.7), (zero - 0.25, 0.0), (zero, 0.0), (zero + 1.5, 0.35), (TL['push1'], 0.55), (TL['pocket'], 0.35), (D, 0.2)])
    bed(bus, room_g, drone_g, duck)

    # frame 0: he draws the wallet from his pocket and lays it on the table
    place(bus['fol'], cloth(0.5, 1, 0.6), 0.02, 1.0, -0.4)
    place(bus['fol'], leather(0.6, 2, 0.5), 0.1, 1.0, -0.1)
    place(bus['hit'], thud(3, 62, 0.14, 0.55), 0.62, 1.0, -0.1)
    place(bus['fol'], paper_slap(4, 0.25), 0.62, 1.0, -0.1)
    # the salary: five bundles whoosh in from the dark and land in the wallet, each heavier than the last
    for k, key in enumerate(['FRIENDS', 'MOM', 'FOOD', 'EMI', 'RENT']):
        L = TL['land'][key]
        place(bus['air'], whoosh(0.75, 500, 3800, 10 + k, 0.8), L - 0.75, 1.0, -0.6 + 0.12 * k)
        place(bus['hit'], thud(20 + k, 70 - 3 * k, 0.12 + 0.02 * k, 0.45 + 0.1 * k), L, 1.0, 0.2)
        place(bus['fol'], paper_slap(30 + k, 0.5 + 0.12 * k), L, 1.0, 0.2)
    place(bus['fol'], breath(0.6, 'in', 40, 0.4), 1.9, 1.0, -0.5)                  # a small relieved breath
    # strangers: footsteps from the scene's foot plants, cloth on the reach, a paper slide and a thud per bundle taken
    for s in M['steps']:
        g = 0.05 + 0.06 * min(1.0, max(0.0, (s['z'] + 3.2) / 2.6)) * s['a']
        place(bus['fol'], lp(thud(int(s['t'] * 977), 85, 0.07, 1.0), 1100), s['t'], g, float(np.clip((s['x'] - 0.1) / 1.4, -0.6, 0.6)))
    for i, it in enumerate(TL['items']):
        g = it['grab']; big = 0.6 + 0.12 * i
        place(bus['fol'], cloth(0.5, 60 + i, 0.7), g - 0.5, 1.0, 0.3)
        place(bus['fol'], paper_slide(0.28, 70 + i, 0.9), g - 0.05, 1.0, 0.2)
        place(bus['hit'], thud(80 + i, 58, 0.2, 0.5 * big), g + 0.08, 1.0, 0.0)
        place(bus['fol'], breath(0.55, 'out', 90 + i, 0.55 + 0.12 * i), g + 0.1, 1.0, -0.45)      # he takes it a little harder every time
        if i < 4: place(bus['fol'], lp(clank(0.3, 100 + i, 0.2), 1400), g + 0.3, 0.05, 0.1)
    # the twist: the balance hits zero
    place(bus['hit'], sub_boom(), zero, 1.25, 0.0)
    ex = load('814046__qubodup__explosion-from-another-dimension.wav', SR * 4)     # read at 4x rate = 2 octaves down
    ex = lp(ex, 900)[:int(4.5 * SR)]; ex /= np.abs(ex).max()
    place(bus['hit'], ex * env(len(ex), 0.01, 1.3), zero, 0.35, 0.0)
    # near silence: one long slow breath out as the camera pushes in, then the wallet goes back in his pocket
    place(bus['fol'], breath(1.6, 'out', 120, 0.5), 10.6, 1.0, -0.45)
    place(bus['fol'], cloth(0.5, 121, 0.6), TL['pick0'] - 0.1, 1.0, -0.2)
    place(bus['fol'], leather(0.7, 122, 0.7), TL['pick0'] + 0.1, 1.0, 0.0)
    place(bus['fol'], leather(0.55, 123, 0.7), TL['pick0'] + 0.7, 1.0, -0.2)
    place(bus['hit'], thud(124, 55, 0.12, 0.3), TL['pocket'], 1.0, -0.4)
    place(bus['fol'], breath(0.7, 'in', 125, 0.5), TL['pocket'] + 0.35, 1.0, -0.4)               # he sits up: the month starts again
    place(bus['fol'], cloth(0.8, 126, 0.6), TL['pocket'] + 0.4, 1.0, -0.4)

    write_wav(finish(bus, duck), out_path); print('wrote', out_path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
