"""Sound for Payday to Payday: minimal but heavy, series kit (../slow-light-dark-common/sld_sound.py).

Bed = CC0 wind room tone + the lamp's 120 Hz hum + a 55 Hz drone. Foley with a visible cause for every sound (all synthesised in
numpy): leather wallet, paper whooshes and slaps as the bundles land, footsteps of the strangers, cloth, breath, a paper slide
and a small thud for every bundle taken. A held-breath silence just before the balance hits zero, then the only big hit
(sub_boom + the CC0 qubodup explosion read two octaves down). Then near silence, then the routine: the lamp is the sun, so the room tone
swells at night and thins by day, one low knock per day, his footsteps to work and back. Salary day comes round again at the loop point.

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


def chair_scrape(seed, gain=1.0):
    n = int(0.45 * SR); x = np.random.default_rng(seed).standard_normal(n); t = np.arange(n) / n
    return (bp(x, 600, 1.0) * 0.6 + bp(x, 1700, 1.8) * 0.3) * np.sin(np.pi * t) ** 0.8 * gain


def main(meta_path, out_path):
    import overlay
    M = json.load(open(meta_path)); D = TL['duration']; N = int(D * SR); t = np.arange(N) / SR
    bus = new_buses(N); zero = TL['zero']
    light = np.interp(t, *zip(*TL['light']))                       # the lamp is the sun
    # silence as a beat: the last bundle is taken at 8.80, everything drops away and the boom lands as the counter hits 0
    duck = curve(N, [(0, 1), (zero - 0.32, 1), (zero - 0.26, 0.0), (zero - 0.01, 0.0), (zero, 0.6), (zero + 1.2, 1), (D, 1)])
    quiet = curve(N, [(0, 1), (zero + 0.3, 1), (zero + 0.4, 0.2), (TL['routine0'], 0.2), (TL['routine0'] + 0.8, 1), (D, 1)])   # near silence after the boom
    night = 1 - light
    room_g = curve(N, [(0, 0.11), (3, 0.12), (zero - 0.3, 0.14), (D, 0.11)]) * duck * (quiet * 0.55 + 0.45) * (1 + 0.8 * night * (t > TL['routine0']))
    drone_g = curve(N, [(0, 0.2), (3, 0.3), (zero - 0.3, 0.7), (zero - 0.25, 0.0), (zero, 0.0), (zero + 1.5, 0.35), (D, 0.2)]) * (1 + 0.5 * night * (t > TL['routine0']))
    bed(bus, room_g, drone_g, duck)

    # frame 0: he draws the wallet from his pocket and lays it on the table
    place(bus['fol'], cloth(0.5, 1, 0.6), 0.02, 1.0, -0.4)
    place(bus['fol'], leather(0.6, 2, 0.5), 0.1, 1.0, -0.1)
    place(bus['hit'], thud(3, 62, 0.14, 0.55), 0.62, 1.0, -0.1)
    place(bus['fol'], paper_slap(4, 0.25), 0.62, 1.0, -0.1)
    # salary day: five bundles whoosh in from the dark and land in the wallet, each heavier than the last; he cheers
    for k, key in enumerate(ORDER_LAND := ['PARTY', 'FOOD', 'GROCERIES', 'EMI', 'RENT']):
        L = TL['land'][key]
        place(bus['air'], whoosh(0.75, 500, 3800, 10 + k, 0.8), L - 0.75, 1.0, -0.6 + 0.12 * k)
        place(bus['hit'], thud(20 + k, 70 - 3 * k, 0.12 + 0.02 * k, 0.45 + 0.1 * k), L, 1.0, 0.2)
        place(bus['fol'], paper_slap(30 + k, 0.5 + 0.12 * k), L, 1.0, 0.2)
    place(bus['fol'], breath(0.6, 'in', 40, 0.45), 0.95, 1.0, -0.5)                  # happy intake as the fists go up
    place(bus['fol'], cloth(0.6, 41, 0.6), 1.0, 1.0, -0.4)
    place(bus['fol'], breath(0.6, 'out', 42, 0.35), 2.55, 1.0, -0.5)
    # strangers: footsteps from the scene's foot plants, cloth on the reach, a paper slide and a thud per bundle taken
    for s in M['steps']:
        if s['who'] != 't': continue
        g = 0.05 + 0.06 * min(1.0, max(0.0, (s['z'] + 3.2) / 2.6)) * s['a']
        place(bus['fol'], lp(thud(int(s['t'] * 977), 85, 0.07, 1.0), 1100), s['t'], g, float(np.clip((s['x'] - 0.1) / 1.4, -0.6, 0.6)))
    for i, it in enumerate(TL['items']):
        g = it['grab']; big = 0.6 + 0.1 * i
        place(bus['fol'], cloth(0.5, 60 + i, 0.7), g - 0.5, 1.0, 0.3)
        place(bus['fol'], paper_slide(0.28, 70 + i, 0.9), g - 0.05, 1.0, 0.2)
        place(bus['hit'], thud(80 + i, 58, 0.2, 0.5 * big), g + 0.08, 1.0, 0.0)
        place(bus['fol'], breath(0.55, 'out', 90 + i, 0.5 + 0.12 * i), g + 0.1, 1.0, -0.45)      # he takes it a little harder every time
    # ghost hands: a breathy whisper swell as each arm reaches out of the dark, a second softer one for the hands that miss
    for i, it in enumerate(TL['items']):
        place(bus['air'], bp(noise(int(0.7 * SR)), 2600, 1.2) * np.sin(np.pi * np.arange(int(0.7 * SR)) / int(0.7 * SR)) ** 1.5 * 0.35, it['grab'] - 0.75, 1.0, 0.35)
        place(bus['air'], bp(noise(int(0.5 * SR)), 3400, 1.5) * np.sin(np.pi * np.arange(int(0.5 * SR)) / int(0.5 * SR)) * 0.18, it['grab'] - 0.5, 1.0, -0.3)
        place(bus['air'], bp(noise(int(0.6 * SR)), 1800, 1.0) * np.sin(np.pi * np.arange(int(0.6 * SR)) / int(0.6 * SR)) ** 0.8 * 0.3, it['grab'] + 0.2, 1.0, 0.0)   # dragged away into the dark
    # rain: hiss in the 2-9 kHz band whose level follows the scene's rain curve (down beat on day 5, and every night of the routine)
    rn = hp(lp(noise(N), 9000), 2200) * np.interp(t, *zip(*TL['rain'])) * 0.05
    for c in range(2): bus['air'][c] += rn * (1.0 + 0.1 * c)
    # the twist: the balance hits zero on day 5
    place(bus['hit'], sub_boom(), zero, 1.25, 0.0)
    ex = load('814046__qubodup__explosion-from-another-dimension.wav', SR * 4)     # read at 4x rate = 2 octaves down
    ex = lp(ex, 900)[:int(4.5 * SR)]; ex /= np.abs(ex).max()
    place(bus['hit'], ex * env(len(ex), 0.01, 1.3), zero, 0.35, 0.0)
    # near silence: the wallet goes back in his pocket, he slides down to the floor in the rain, a long breath out
    place(bus['fol'], breath(1.6, 'out', 120, 0.5), TL['floor0'] + 0.3, 1.0, -0.45)
    place(bus['hit'], thud(125, 50, 0.2, 0.45), TL['floor0'] + 0.4, 1.0, -0.4)
    place(bus['fol'], chair_scrape(126, 0.6), TL['floor0'], 1.0, -0.4)
    place(bus['fol'], cloth(0.5, 121, 0.6), TL['pick0'] - 0.1, 1.0, -0.2)
    place(bus['fol'], leather(0.7, 122, 0.7), TL['pick0'] + 0.1, 1.0, 0.0)
    place(bus['hit'], thud(124, 55, 0.12, 0.3), TL['pocket'], 1.0, -0.4)
    # the routine: one low knock per day (they come faster and faster), the chair scrapes, his steps to work and back
    prev = 5
    for f in range(round(TL['routine0'] * TL['fps']), round(D * TL['fps'])):
        tt = f / TL['fps']; d = overlay.day_at(tt)
        if d > prev:
            place(bus['hit'], thud(300 + d, 52 + d * 0.4, 0.1, 0.22), tt, 1.0, 0.0); prev = d
    for k, c in enumerate(TL['cycles']):
        place(bus['fol'], breath(0.5, 'in', 400 + k, 0.35), c + 0.2, 1.0, -0.4)
        place(bus['fol'], chair_scrape(410 + k, 0.7), c + 0.35, 1.0, -0.4)
        place(bus['hit'], thud(420 + k, 60, 0.12, 0.3), c + 2.45, 1.0, -0.4)                       # drops into the chair, tired
        place(bus['fol'], breath(0.7, 'out', 430 + k, 0.5), c + 2.5, 1.0, -0.4)
    for s in M['steps']:
        if s['who'] != 'h': continue
        place(bus['fol'], lp(thud(int(s['t'] * 733), 95, 0.07, 1.0), 1200), s['t'], 0.2, float(np.clip((s['x'] - 0.0) / 1.2, -0.7, 0.7)))
    # the loop: he sits up, a rising breath into frame 0
    place(bus['fol'], breath(0.8, 'in', 500, 0.5), TL['salaryAgain'] + 0.2, 1.0, -0.4)
    place(bus['air'], whoosh(1.2, 300, 2400, 501, 0.4), D - 1.3, 1.0, 0.0)

    write_wav(finish(bus, duck), out_path); print('wrote', out_path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
