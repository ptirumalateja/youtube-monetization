"""Sound for The Salary Loop V3 (19.3 s). Every sound has a visible cause; all times come from timeline.json.
The phone buzz is the reel's motif: the salary (frame 0), every debit, the false hope, and next month's salary at the end, which wraps across
the loop seam into frame 0. Debit "dums" step down in pitch. One held breath before ₹0 and the only big hit on ₹0. Ticks follow the
calendar pages and accelerate through the time-lapse into a riser. Synthesised in numpy (sld_sound + the Salary Loop helpers) plus the two
CC0 Freesound files the series already uses (sleepCircle wind room tone, qubodup explosion pitched down).

  python3 mix_v3.py OUT.wav
"""
import json, os, sys
import numpy as np
MYDIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(MYDIR, '..', 'slow-light-dark-common')); sys.path.insert(0, os.path.join(MYDIR, '..', 'salary-loop'))
from sld_sound import *
import mix as base
TL = json.load(open(os.path.join(MYDIR, 'timeline.json'))); D = TL['duration']; N = int(D * SR)
ZERO, HIT = TL['zero'], TL['hit']


def tear(seed, g=1.0):
    """A paper page torn off a pad: a fast bright rip."""
    n = int(0.22 * SR); tt = np.arange(n) / SR; r = np.random.default_rng(seed)
    x = bp(r.standard_normal(n), 3200, 0.8) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 90 * tt))) * np.exp(-tt / 0.07)
    return x * np.minimum(1, tt / 0.004) * 0.6 * g


def dum(seed, f, g=1.0):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.22) + 0.4 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt / 0.1)) * np.minimum(1, tt / 0.004) * 0.5 * g


def step(seed, g=1.0): return lp(thud(seed, 95, 0.06, 1.0), 1400) * g


def main(out_path):
    bus = new_buses(N)
    hb0 = TL['buzz'][6]
    duck = curve(N, [(0, 1), (hb0 - 0.02, 1), (hb0 + 0.06, 0.0), (HIT - 0.01, 0.0), (HIT, 0.6), (HIT + 1.0, 1), (D, 1)])
    room_g = curve(N, [(0, 0.1), (4.4, 0.12), (5.6, 0.14), (15.0, 0.16), (15.8, 0.12), (D, 0.1)]) * duck
    drone_g = curve(N, [(0, 0.12), (5.6, 0.18), (hb0, 0.36), (hb0 + 0.05, 0.0), (HIT, 0.0), (HIT + 1.2, 0.26), (13.4, 0.34), (15.8, 0.16), (D, 0.12)])
    bed(bus, room_g, drone_g, duck)
    # ---- the phone: every buzz in the timeline (the last one wraps across the seam into frame 0)
    for bt in TL['buzz']:
        if bt <= 0.01: continue
        bz = base.buzz(0.5); bz *= np.linspace(1, 0, len(bz)) ** 0.8
        (base.place_wrap if bt > D - 0.6 else place)(bus['fol'], bz, bt, 0.55, 0.2)
    # ---- the hook: a soft hit + the bright two-note chime on the salary card, his inhale, the smile, the blanket, the bed
    place(bus['hit'], thud(11, 70, 0.12, 0.45), 0.0, 1.0, 0.0)
    place(bus['air'], base.chime(), 0.08, 1.0, 0.1)
    place(bus['fol'], breath(0.6, 'in', 1, 0.45), 1.05, 1.0, -0.4)
    place(bus['fol'], breath(0.5, 'out', 2, 0.5), 2.05, 1.0, -0.3)                                  # the delighted exhale
    sw = int(1.4 * SR); ts = np.arange(sw) / SR
    pad = sum(np.sin(2 * np.pi * f * ts) * a for f, a in [(262, 1.0), (330, 0.7), (392, 0.55)]) * np.sin(np.pi * ts / 1.4) * 0.05
    place(bus['drone'], pad, 1.8, 1.0, 0.0)                                                          # warm swell on the happy beat
    place(bus['fol'], base.cloth(0.5, 3, 0.6), 2.5, 1.0, -0.2); place(bus['fol'], creak(4, 0.7), 2.9, 0.5, -0.2)
    place(bus['fol'], step(5, 0.35), 3.4, 1.0, 0.0); place(bus['fol'], step(6, 0.3), 3.55, 1.0, 0.1)
    # ---- the door: the 30 comes off, keys, the bag
    place(bus['fol'], tear(20, 1.0), 3.88, 1.0, -0.2)
    for j in range(4): place(bus['air'], base.coin_ting(30 + j, 0.5), 4.22 + j * 0.035, 0.4, 0.3)
    place(bus['fol'], base.leather(0.3, 31, 0.5), 4.2, 1.0, 0.2)
    # ---- the morning street: birds, springy steps, the rent buzz stops him
    for k in range(5): place(bus['air'], lp(np.sin(2 * np.pi * (3300 + 400 * k) * np.arange(int(0.2 * SR)) / SR) * np.exp(-((np.arange(int(0.2 * SR)) / SR - 0.1) / 0.05) ** 2), 6000) * 0.12, 4.45 + k * 0.23, 1.0, -0.6 + 0.3 * k)
    for tt in [4.45, 4.72, 5.42]: place(bus['fol'], step(int(tt * 100), 0.3), tt, 1.0, 0.0)
    D0 = TL['debits']; fs = [150, 132, 118, 104, 92]
    for i, (tc, lab, amt, left) in enumerate(D0[:5]): place(bus['hit'], dum(40 + i, fs[i], 0.8 + 0.06 * i), tc, 1.0, 0.0); place(bus['fol'], breath(0.4, 'out', 50 + i, 0.3 + 0.07 * i), tc + 0.2, 1.0, -0.3)
    # ---- the desk: keys, the morning tears, the buzzes
    rr = np.random.default_rng(5); tcur = 5.7
    while tcur < 14.6:
        quiet = any(a - 0.1 < tcur < a + 1.0 for a in [hb0]) or 8.6 < tcur < 10.8
        if not quiet: place(bus['fol'], base.key_click(int(tcur * 1000)), tcur, 0.3, 0.2)
        tcur += rr.exponential(0.12) + 0.03
    for t0, n in TL['days']:
        if 5.6 < t0 < 10.0: place(bus['fol'], tear(int(t0 * 10), 0.9), t0 + 0.05, 1.0, -0.3)
    # ---- held breath, then the only big hit: ₹0
    place(bus['hit'], sub_boom(), HIT, 1.25, 0.0)
    ex = load('814046__qubodup__explosion-from-another-dimension.wav', SR * 4); ex = lp(ex, 900)[:int(4.5 * SR)]; ex /= np.abs(ex).max()
    place(bus['hit'], ex * env(len(ex), 0.01, 1.3), HIT, 0.35, 0.0)
    # ---- the reveal: a slow clock starts, then the time-lapse ticks on every page and accelerates into a riser
    for k in range(3): place(bus['fol'], base.tick(300 + k), TL['reveal'][0] + 0.1 + k * 0.32, 0.4, 0.4)
    for t0, n in TL['days']:
        if 10.7 < t0 < 13.45: place(bus["fol"], base.tick(400 + n, 1900 + 25 * (n - 7)), t0, 0.35 + 0.012 * (n - 7), 0.3); place(bus['fol'], tear(500 + n, 0.35), t0 + 0.02, 1.0, -0.3)
    rs = int(2.6 * SR); tr = np.arange(rs) / SR; ramp = (tr / 2.6) ** 2
    riser = (sum(np.sin(2 * np.pi * f * (1 + 0.25 * tr / 2.6) * tr) * a for f, a in [(220, 1.0), (330, 0.6), (440, 0.4)]) * 0.05 + hp(noise(rs), 3000) * 0.03) * ramp
    place(bus['drone'], riser, 10.8, 1.0, 0.0)
    # ---- false hope: the opening chime, detuned and cut short
    ch = base.chime(0.45, 1318.5 * 0.94); ch *= np.linspace(1, 0, len(ch)) ** 2; place(bus['air'], ch, TL['buzz'][7] + 0.08, 1.0, 0.1)
    place(bus['fol'], breath(0.8, 'out', 60, 0.5), 14.0, 1.0, -0.3)
    for t0, n in TL['days']:
        if 14.4 < t0 < 14.9: place(bus['fol'], tear(600 + n, 0.7), t0 + 0.05, 1.0, -0.3)
    place(bus['fol'], thud(61, 900, 0.02, 0.3), 14.84, 1.0, 0.1); place(bus['fol'], base.chair_scrape(62, 0.4), 14.88, 1.0, 0.0)   # laptop shut, chair
    # ---- the night street: wind, distant traffic, slow steps
    place(bus['air'], lp(noise(int(0.9 * SR)), 500) * np.sin(np.pi * np.arange(int(0.9 * SR)) / int(0.9 * SR)) * 0.4, 15.0, 1.0, 0.0)
    for tt in [15.1, 15.55]: place(bus['fol'], step(int(tt * 100), 0.25), tt, 1.0, 0.0)
    # ---- home: the bed takes his weight, a long exhale, the blanket, quiet, a slow clock, the lamp hum (in the bed)
    place(bus['fol'], creak(70, 0.9), 16.2, 0.55, -0.2); place(bus['fol'], breath(1.1, 'out', 71, 0.5), 16.5, 1.0, -0.3)
    place(bus['fol'], base.leather(0.3, 72, 0.4), 16.35, 1.0, 0.2); place(bus['fol'], base.cloth(0.6, 73, 0.5), 17.2, 1.0, -0.2)
    for k in range(3): place(bus['fol'], base.tick(800 + k), 17.9 + k * 0.4, 0.25, 0.4)
    write_wav(finish(bus, duck), out_path); print('wrote', out_path)


if __name__ == '__main__': main(sys.argv[1])
