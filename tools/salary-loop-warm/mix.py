"""Sound for The Salary Loop (warm): a notification bell and phone buzz that run across the loop seam, a place-specific foley bed for every set
(door, bank, market, bills, restaurant, pump, street, office, bedroom), a held-breath silence and one sub-boom when the balance reaches zero, then near
silence, an alarm, footsteps, keyboard and clock, a rising swell into the next bell and a knock at the door. Everything is synthesised in numpy except two
CC0 Freesound files (sleepCircle wind as room tone, qubodup explosion pitched down).

  python3 mix.py OUT.wav
"""
import json, os, sys
import numpy as np
MYDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(MYDIR, '..', 'slow-light-dark-common')); sys.path.insert(0, os.path.join(MYDIR, '..', 'salary-loop'))
from sld_sound import *
import mix as base                                   # helper sources from the previous Salary Loop mix (whoosh, bell, buzz, tick, key_click, beep, leather, cloth, paper_slap, coin_ting)
TL = json.load(open(os.path.join(MYDIR, 'timeline.json'))); D = TL['duration']; N = int(D * SR); items = TL['items']; zero = TL['zero']
def env_(n, a, d): return env(n, a, d)
def knock(seed, g=1.0):
    n = int(0.25 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * (170 + 60 * np.exp(-tt / 0.01)) * tt) * np.exp(-tt / 0.05) + lp(noise(n), 3000) * np.exp(-tt / 0.006) * 0.7) * g
def murmur(dur, seed, g=1.0):
    n = int(dur * SR); x = bp(np.random.default_rng(seed).standard_normal(n), 380, 0.9) * 0.7 + bp(np.random.default_rng(seed + 1).standard_normal(n), 900, 1.1) * 0.4
    am = 0.55 + 0.45 * np.sin(2 * np.pi * np.cumsum(np.full(n, 3.2)) / SR + np.cumsum(np.random.default_rng(seed + 2).standard_normal(n)) * 0.0004)
    return x * am * np.minimum(1, np.arange(n) / (0.2 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.3 * SR)) * g
def chirp(seed):
    r = np.random.default_rng(seed); n = int(0.22 * SR); tt = np.arange(n) / SR; f = 3200 + 1200 * r.random(); return np.sin(2 * np.pi * (f + 900 * np.sin(2 * np.pi * 14 * tt)) * tt) * np.exp(-((tt - 0.1) / 0.06) ** 2) * 0.3
def clink(seed):
    r = np.random.default_rng(seed); n = int(0.4 * SR); tt = np.arange(n) / SR; f = 2600 + 1200 * r.random(); return (np.sin(2 * np.pi * f * tt) + 0.6 * np.sin(2 * np.pi * f * 2.3 * tt)) * np.exp(-tt / 0.08) * 0.25
def glug(dur):
    n = int(dur * SR); tt = np.arange(n) / SR; f = 180 + 60 * np.sin(2 * np.pi * 7 * tt); return (np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + bp(noise(n), 700, 1.0) * 0.4) * np.minimum(1, tt / 0.1) * np.minimum(1, (dur - tt) / 0.1)
def main(out_path):
    t = np.arange(N) / SR; bus = new_buses(N)
    duck = curve(N, [(0, 1), (zero - 0.34, 1), (zero - 0.28, 0.0), (zero - 0.01, 0.0), (zero, 0.6), (zero + 1.0, 1), (D, 1)])
    quiet = curve(N, [(0, 1), (zero + 0.4, 1), (zero + 0.5, 0.2), (TL['alarm'] - 0.2, 0.2), (TL['alarm'], 1), (D, 1)])
    room_g = curve(N, [(0, 0.1), (3, 0.12), (zero - 0.3, 0.14), (D, 0.1)]) * duck * (quiet * 0.7 + 0.3)
    drone_g = curve(N, [(0, 0.12), (3, 0.2), (zero - 0.3, 0.4), (zero - 0.25, 0.0), (zero, 0.0), (zero + 1.5, 0.3), (D, 0.14)])
    bed(bus, room_g, drone_g, duck)
    # ---- the notification (wraps across the loop seam): bell + buzz, and the happy flinch
    bt = TL['bell']
    base.place_wrap(bus['air'], base.bell(), bt, 1.0, 0.0)
    bz = base.buzz(0.5); bz *= np.linspace(1, 0, len(bz)) ** 0.8; place(bus['fol'], bz, bt, 0.5, 0.2)
    place(bus['fol'], breath(0.6, 'in', 1, 0.45), bt + 0.3, 1.0, -0.4)                                   # he wakes
    place(bus['fol'], bp(noise(int(0.5 * SR)), 500, 1.0) * np.sin(np.pi * np.arange(int(0.5 * SR)) / int(0.5 * SR)) * 0.35, 2.4, 1.0, -0.3)   # the blanket
    place(bus['fol'], bp(noise(int(0.7 * SR)), 450, 1.0) * np.sin(np.pi * np.arange(int(0.7 * SR)) / int(0.7 * SR)) * 0.4, 3.0, 1.0, -0.3)   # the bed creaks as he sits up
    place(bus['hit'], thud(611, 80, 0.1, 0.4), 3.75, 1.0, -0.1)                                           # feet on the floor
    for k in range(5): place(bus['fol'], lp(thud(740 + k, 95, 0.06, 1.0), 1400), 4.45 + k * 0.2, 0.25, 0.0)   # first steps
    # ---- scene cuts: a soft warm whoomp at every change of place
    for s in TL['scenes'][1:]: place(bus['air'], base.whoosh(0.3, 300, 2500, int(s['t0'] * 100), 0.5), s['t0'] - 0.15, 0.5, 0.0)
    # ---- the six bills, one place each
    T0 = [it['t'] for it in items]; SC = {s['id']: s for s in TL['scenes']}
    for k, kt in enumerate([T0[0] - 0.35, T0[0] - 0.2]): place(bus['hit'], knock(100 + k, 0.8), kt, 1.0, -0.3)                                                  # RENT: knock on the door
    place(bus['fol'], murmur(0.9, 1, 0.3), SC['bank']['t0'], 1.0, 0.3); [place(bus['fol'], base.key_click(300 + k), T0[1] - 0.6 + k * 0.07, 0.4, 0.3) for k in range(8)]; place(bus['hit'], thud(110, 90, 0.05, 0.5), T0[1] - 0.05, 1.0, 0.1)   # EMI: bank keys + a stamp
    place(bus['fol'], murmur(1.0, 2, 0.5), SC['market']['t0'], 1.0, 0.0); place(bus['fol'], base.paper_slide(0.5, 12, 0.7), T0[2] - 0.2, 1.0, 0.2)         # GROCERIES: market chatter, a paper bag
    place(bus['fol'], glug(0.7), T0[3] - 0.3, 0.7, 0.2); place(bus['hit'], thud(120, 70, 0.1, 0.45), T0[3] + 0.3, 1.0, 0.3)                                      # FUEL: the pump
    place(bus['fol'], base.paper_slide(0.6, 13, 0.8), SC['bills']['t0'] + 0.1, 1.0, 0.1); place(bus['air'], np.sin(2 * np.pi * 120 * np.arange(int(0.8 * SR)) / SR) * 0.03, T0[4] - 0.3, 1.0, 0.0)   # BILLS: papers, the mains buzz
    place(bus['fol'], murmur(0.9, 3, 0.4), SC['food']['t0'], 1.0, -0.2); [place(bus['fol'], clink(400 + k), T0[5] - 0.4 + k * 0.17, 0.35, -0.3 + 0.3 * k) for k in range(4)]   # FOOD & PARTY: plates, cutlery
    for i, kt in enumerate(T0):
        place(bus['fol'], base.paper_slap(500 + i, 0.5 + 0.08 * i), kt, 1.0, 0.0); place(bus['hit'], thud(520 + i, 62 - 2 * i, 0.16, 0.45 + 0.06 * i), kt + 0.03, 1.0, 0.0)
        for j in range(6): place(bus['air'], base.coin_ting(530 + 6 * i + j, 0.6), kt + 0.02 + j * 0.03, 0.3, 0.3)
        place(bus['fol'], breath(0.45, 'out', 90 + i, 0.4 + 0.1 * i), kt + 0.15, 1.0, -0.4)                                                                           # each bill: a heavier sigh
    # ---- the twist: balance 0
    place(bus['hit'], sub_boom(), zero, 1.25, 0.0); ex = load('814046__qubodup__explosion-from-another-dimension.wav', SR * 4); ex = lp(ex, 900)[:int(4.5 * SR)]; ex /= np.abs(ex).max(); place(bus['hit'], ex * env(len(ex), 0.01, 1.3), zero, 0.35, 0.0)
    # ---- the empty wallet, a clock, then the alarm, getting dressed
    b0 = TL['scenes'][7]['t0']; place(bus['fol'], base.leather(0.7, 301, 0.6), b0 + 0.2, 1.0, -0.1); place(bus['air'], np.sin(2 * np.pi * 3100 * np.arange(int(1.6 * SR)) / SR) * np.exp(-np.arange(int(1.6 * SR)) / SR / 0.5) * 0.04, b0 + 0.6, 1.0, 0.1)
    for k in range(int((TL['alarm'] - b0 - 0.2) / 0.4)): place(bus['fol'], base.tick(310 + k), b0 + 0.2 + k * 0.4, 0.35 + 0.1 * k, 0.4)
    for k in range(5): place(bus['air'], base.beep(0.12), TL['alarm'] + k * 0.2, 0.55, 0.0)
    place(bus['fol'], breath(1.0, 'out', 320, 0.5), TL['wake'][0] - 0.1, 1.0, -0.4); place(bus['fol'], base.cloth(0.6, 321, 0.6), TL['wake'][0] + 0.1, 1.0, -0.3); place(bus['fol'], base.leather(0.4, 322, 0.5), TL['wake'][1] - 0.2, 1.0, 0.2)
    for k in range(3): place(bus['fol'], lp(thud(760 + k, 95, 0.06, 1.0), 1400), TL['wake'][1] + 0.1 + k * 0.2, 0.28, 0.0)
    # ---- the street: birds, steps, a bus far away
    s0 = SC['street']['t0']
    for k in range(5): place(bus['air'], chirp(700 + k), s0 + 0.1 + k * 0.2, 0.5, -0.6 + 0.2 * k)
    for k in range(5): place(bus['fol'], lp(thud(730 + k, 92, 0.07, 1.0), 1300), s0 + k * 0.22, 0.28, 0.0)
    place(bus['air'], lp(noise(int(1.6 * SR)), 600) * np.sin(np.pi * np.arange(int(1.6 * SR)) / int(1.6 * SR)) * 0.35, s0, 1.0, 0.0)
    # ---- the office: keys, clock, chair, coffee, a long breath, the days racing, the night
    o0, o1 = TL['office']; rr = np.random.default_rng(5); tcur = o0 + 0.2
    while tcur < o1 - 0.2: place(bus['fol'], base.key_click(int(tcur * 1000)), tcur, 0.4, 0.2); tcur += rr.exponential(0.12) + 0.02
    for k in range(int((o1 - o0) / 0.5)): place(bus['fol'], base.tick(400 + k), o0 + k * 0.5, 0.28 + 0.12 * (k / 10), 0.45)
    place(bus['fol'], base.cloth(0.5, 740, 0.4), o0 + 0.19 * (o1 - o0) + 0.1, 1.0, 0.2); place(bus['fol'], breath(0.5, 'in', 743, 0.4), o0 + 0.25 * (o1 - o0), 1.0, -0.2)    # the coffee
    place(bus['fol'], breath(1.2, 'out', 741, 0.5), o0 + 0.62 * (o1 - o0), 1.0, -0.4); place(bus['fol'], base.leather(0.4, 744, 0.4), o0 + 0.8 * (o1 - o0), 1.0, 0.2)       # rubbing eyes, the slump
    place(bus['air'], base.whoosh(1.0, 300, 3000, 742, 0.35), o0 + 0.5 * (o1 - o0), 0.6, 0.0)
    sw = int(3.2 * SR); ts = np.arange(sw) / SR; ramp = (ts / 3.2) ** 2
    swell = sum(np.sin(2 * np.pi * f * ts + 0.3 * i) * a for i, (f, a) in enumerate([(196, 1.0), (294, 0.7), (392, 0.55), (588, 0.3)])) * ramp * 0.07 * (1 + 0.3 * np.sin(2 * np.pi * 5 * ts))
    place(bus['drone'], swell, 16.6, 1.0, 0.0)
    for k in range(3): place(bus['fol'], breath(0.9, 'in' if k % 2 == 0 else 'out', 750 + k, 0.35), 18.7 + k * 0.5, 1.0, -0.3)   # asleep
    write_wav(finish(bus, duck), out_path); print('wrote', out_path)
if __name__ == '__main__': main(sys.argv[1])
