"""Sound for Tug of War: minimal but heavy. Rope groan and fibre stretch, foot skids, breath and grunts, one sub-boom on the
reveal, then near silence when he lets go. Everything is synthesised in numpy (sld_sound kit) except two CC0 Freesound files
(sleepCircle wind as room tone, qubodup explosion read two octaves down under the boom).

  python3 mix.py META.json OUT.wav        META.json from `node render.cjs meta 16 30`
"""
import json, sys
import numpy as np
from sld_sound import *


def rope_groan(dur, seed, gain=1.0, f0=330):
    """Hemp under load: stick-slip pulses through a low resonance, plus fibre crackle and a slow pitch sag."""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    f = f0 * (1 + 0.18 * np.sin(2 * np.pi * (1.1 + 0.4 * r.random()) * t) - 0.12 * t / dur) + 25 * np.cumsum(r.standard_normal(n)) / np.sqrt(np.arange(1, n + 1))
    saw = (np.cumsum(f) / SR % 1.0) * 2 - 1
    y = bp(saw, 520, 1.1) * 0.9 + bp(saw, 1250, 1.8) * 0.5 + lp(saw, 260) * 0.4
    grain = np.repeat(r.random(n // 120 + 1), 120)[:n] ** 2
    fib = hp(noise(n), 3500) * grain * 0.18 + bp(noise(n), 1800, 1.5) * grain * 0.25
    e = np.sin(np.pi * np.minimum(1, t / dur)) ** 1.3
    return (y * 0.5 + fib) * e * gain


def stretch(dur, seed, gain=1.0):
    """A slow rising squeal of fibres taking the strain."""
    n = int(dur * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    f = 620 + 380 * (t / dur) ** 1.5 + 18 * np.cumsum(r.standard_normal(n)) / np.sqrt(np.arange(1, n + 1))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 23 * t))
    return bp(s, 900, 0.7) * np.sin(np.pi * t / dur) ** 2 * gain * 0.35


def skid(dur, seed, gain=1.0):
    """A shoe sliding on gritty concrete: band noise with heavy grain, falling off."""
    n = int(dur * SR); x = noise(n); t = np.arange(n) / SR
    grain = np.repeat(np.random.default_rng(seed).random(n // 160 + 1), 160)[:n] ** 2.5
    y = (bp(x, 1100, 1.0) * (0.25 + grain) + hp(x, 3500) * grain * 0.35) * np.exp(-t / (dur * 0.55)) * np.minimum(1, t / 0.01)
    return y * gain * 0.6


def grunt(dur, seed, gain=1.0, f0=96):
    """Effort grunt: a voiced pulse train through chest formants over breath noise, falling in pitch."""
    n = int(dur * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    f = f0 * (1.15 - 0.3 * t / dur) * (1 + 0.02 * r.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1)))
    ph = np.cumsum(f) / SR; src = np.sum([np.sin(2 * np.pi * ph * k) / k ** 1.1 for k in range(1, 14)], axis=0)
    v = bp(src, 560, 1.4) * 0.8 + bp(src, 1050, 2.0) * 0.35 + lp(src, 300) * 0.4
    air = bp(noise(n), 700, 1.2) * 0.35 + bp(noise(n), 1700, 2.0) * 0.12
    e = (1 - np.exp(-t / 0.03)) * np.exp(-t / (dur * 0.38))
    return (v * 0.7 + air) * e * gain


def main(meta_path, out_path):
    M = json.load(open(meta_path)); E = M['events']; D = E['duration']; N = int(D * SR)
    bus = new_buses(N)
    # bed: room tone + lamp hum + drone. Duck for 0.28 s right before the boom; near silence after he lets go.
    rev, lg = E['reveal'], E['letGo']
    duck = curve(N, [(0, 1), (rev - 0.30, 1), (rev - 0.24, 0.0), (rev - 0.005, 0.0), (rev, 0.6), (rev + 1.2, 1), (D, 1)])
    room_g = curve(N, [(0, 0.11), (6, 0.12), (rev - 0.3, 0.17), (rev + 0.2, 0.05), (12.6, 0.07), (lg, 0.05), (lg + 0.9, 0.02), (D, 0.025)]) * duck
    drone_g = curve(N, [(0, 0.28), (6, 0.35), (rev - 0.3, 0.7), (rev - 0.24, 0.0), (rev + 0.3, 0.45), (12.8, 0.5), (lg + 0.2, 0.15), (lg + 1.2, 0.0), (D, 0.0)])
    bed(bus, room_g, drone_g, duck)
    # the second lamp comes up: its own mains hum rises and settles a hair detuned (beating against the first)
    t = np.arange(N) / SR; l2 = curve(N, [(0, 0), (E['lamp2On0'], 0), (E['lamp2On1'], 1), (D, 1)])
    hum2 = lp(sum(np.sin(2 * np.pi * h * 60.4 * t + 2 * h) / h ** 1.2 for h in (2, 3, 4, 6)), 600) * 0.012 * l2 * (1 - 0.8 * curve(N, [(0, 0), (lg + 0.2, 0), (lg + 1.2, 1), (D, 1)]))
    for c in range(2): bus['bed'][c] += hum2 * duck

    HP, TP = -0.45, 0.45          # hero on the left of the stereo field, twin on the right
    # frame 0: he is already straining; a foot catches, the rope creaks
    place(bus['hit'], thud(1, 55, 0.2, 0.5), 0.0, 1.0, HP)
    place(bus['fol'], rope_groan(1.1, 3, 0.55), 0.0, 1.0, 0.0)
    place(bus['fol'], skid(0.25, 4, 0.5), 0.02, 1.0, HP)
    # heaves: breath in, strain out, rope groan, a shuffle of the planted foot
    for i, h in enumerate(E['heaves']):
        big = 1.0 if i < 5 else 0.8
        place(bus['fol'], breath(0.4, 'in', 100 + i, 0.55), h - 0.38, 1.0, HP + 0.1)
        place(bus['fol'], grunt(0.7, 110 + i, 0.5 * big), h + 0.02, 1.0, HP + 0.1)
        place(bus['fol'], rope_groan(0.95, 120 + i, 0.6 * big), h + 0.05, 1.0, -0.05)
        place(bus['fol'], stretch(0.8, 130 + i, 0.7), h + 0.1, 1.0, 0.0)
        place(bus['fol'], skid(0.18, 140 + i, 0.35), h + 0.3, 1.0, HP)
    # yanks: the other end wins a metre of rope; his shoes skid toward the pit
    for i, y in enumerate(E['yanks']):
        big = 1.25 if i == 3 else 1.0
        s = y + 0.04
        place(bus['hit'], thud(200 + i, 52, 0.26, 0.9 * big), s, 0.8, HP)
        place(bus['fol'], skid(0.5 * big, 210 + i, 1.0), s, 1.0, HP)
        place(bus['fol'], skid(0.3, 220 + i, 0.7), s + 0.06, 1.0, HP + 0.2)
        place(bus['fol'], breath(0.3, 'out', 230 + i, 0.8), s + 0.02, 1.0, HP + 0.1)
        place(bus['hit'], lp(clank(0.35, 240 + i, 0.2), 1200), s, 0.1, 0.0)           # rope jerks taut
        place(bus['fol'], hp(noise(int(0.6 * SR)), 4000) * env(int(0.6 * SR), 0.005, 0.2) * 0.05 * big, s + 0.01, 1.0, HP)   # dust hiss
    # the long middle: both of them hold, breathe, and the rope groans (the twin is on the right of the field, a little softer)
    for i, h in enumerate([7.4, 8.5, 9.2]):
        place(bus['fol'], rope_groan(1.0, 300 + i, 0.4), h, 1.0, -0.1)
        place(bus['fol'], breath(0.4, 'in', 310 + i, 0.4), h - 0.35, 1.0, HP + 0.1)
        place(bus['fol'], grunt(0.6, 320 + i, 0.3), h + 0.05, 1.0, HP + 0.1)
    for i, h in enumerate([10.35, 11.3, 12.15]):          # after the reveal the twin's strain is the one we hear
        place(bus['fol'], breath(0.4, 'in', 330 + i, 0.55), h - 0.38, 1.0, TP - 0.1)
        place(bus['fol'], grunt(0.7, 340 + i, 0.55), h + 0.02, 1.0, TP - 0.1)
        place(bus['fol'], rope_groan(1.0, 350 + i, 0.55), h + 0.05, 1.0, 0.05)
        place(bus['fol'], skid(0.18, 360 + i, 0.35), h + 0.3, 1.0, TP)
    # the reveal: the sub-boom + a CC0 explosion read two octaves down underneath
    place(bus['hit'], sub_boom(), rev, 1.25, 0.0)
    ex = load('814046__qubodup__explosion-from-another-dimension.wav', SR * 4); ex = lp(ex, 900)[:int(4.5 * SR)]; ex /= np.abs(ex).max()
    place(bus['hit'], ex * env(len(ex), 0.01, 1.3), rev, 0.35, 0.0)
    # he eases off: the rope goes slack, one long groan sagging in pitch, one long breath out
    place(bus['fol'], rope_groan(0.9, 400, 0.5, 300), E['cut'] + 0.3, 1.0, 0.0)
    place(bus['fol'], breath(1.3, 'out', 401, 0.8), lg - 0.1, 1.0, HP + 0.1)
    # the rope drops: soft thuds on the ledge, one slap against the pit wall
    for k, dt in enumerate([0.1, 0.22, 0.4]):
        place(bus['fol'], lp(thud(500 + k, 62, 0.12, 0.45), 900), lg + dt, 1.0, HP - 0.1)
    place(bus['fol'], scrape(0.5, 410, 0.35), lg + 0.15, 1.0, -0.15)
    # the twin stumbles back: skids, two heavy steps, a gasp
    st = E['stumble']
    place(bus['fol'], breath(0.35, 'in', 420, 0.8), st - 0.08, 1.0, TP)
    place(bus['fol'], skid(0.45, 421, 0.9), st, 1.0, TP)
    place(bus['hit'], thud(422, 58, 0.2, 0.7), st + 0.18, 0.7, TP)
    place(bus['hit'], thud(423, 54, 0.22, 0.55), st + 0.5, 0.7, TP)
    place(bus['fol'], skid(0.3, 424, 0.6), st + 0.4, 1.0, TP)
    place(bus['fol'], grunt(0.45, 425, 0.35), st + 0.05, 1.0, TP)
    # then almost nothing: one breath each
    place(bus['fol'], breath(1.1, 'out', 430, 0.3), 14.55, 1.0, HP + 0.1)
    place(bus['fol'], breath(1.1, 'out', 431, 0.25), 15.0, 1.0, TP - 0.1)
    write_wav(finish(bus, duck), out_path); print('wrote', out_path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
