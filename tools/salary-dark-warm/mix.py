"""Sound for the dark-warm Salary Loop: room tone and lamp hum, a bell + buzz for the salary notification (wraps over the loop seam),
a paper slide, slap and sigh for every bill, a held-breath silence and one sub-boom at zero, keyboard and a ticking clock during the work,
a slow calendar page, then the next bell. Synthesised in numpy (series kit) plus the two CC0 files the kit already uses.
  python3 mix.py OUT.wav
"""
import json, os, sys
import numpy as np
MY = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(MY, '..', 'slow-light-dark-common')); sys.path.insert(0, os.path.join(MY, '..', 'salary-loop'))
from sld_sound import *
import mix as base                      # helper sources from the first Salary Loop mix (bell, buzz, paper_slap, paper_slide, key_click, tick, coin_ting, leather, cloth)
TL = json.load(open(os.path.join(MY, 'timeline.json'))); D = TL['duration']; N = int(D * SR); Z = TL['zero']; W0, W1 = TL['work']
def main(out):
    bus = new_buses(N)
    duck = curve(N, [(0, 1), (Z - 0.34, 1), (Z - 0.28, 0.0), (Z - 0.01, 0.0), (Z, 0.6), (Z + 1.0, 1), (D, 1)])
    room_g = curve(N, [(0, 0.12), (Z - 0.3, 0.14), (D, 0.12)]) * duck
    drone_g = curve(N, [(0, 0.12), (Z - 0.3, 0.4), (Z - 0.25, 0.0), (Z, 0.0), (Z + 1.5, 0.28), (W1, 0.2), (D, 0.12)])
    bed(bus, room_g, drone_g, duck)
    # notification: bell + buzz at 0.15 s, and again at TL['next'] (its tail wraps onto frame 0, so the loop has no seam)
    for tt in (0.15, TL['next']):
        base.place_wrap(bus['air'], base.bell(), tt, 1.0, 0.0); bz = base.buzz(0.5); bz *= np.linspace(1, 0, len(bz)) ** 0.8; base.place_wrap(bus['fol'], bz, tt, 0.5, 0.2)
    place(bus['fol'], breath(0.7, 'out', 3, 0.45), TL['next'] + 0.5, 1.0, -0.4)
    for i, b in enumerate(TL['bills']):
        t = b['t']
        place(bus['fol'], base.paper_slide(0.4, 10 + i, 0.8), t - 0.05, 1.0, 0.3)
        place(bus['fol'], base.paper_slap(500 + i, 0.5 + 0.08 * i), t + 0.3, 1.0, -0.2); place(bus['hit'], thud(520 + i, 62 - 2 * i, 0.16, 0.45 + 0.06 * i), t + 0.33, 1.0, 0.0)
        for j in range(5): place(bus['air'], base.coin_ting(530 + 6 * i + j, 0.6), t + 0.05 + j * 0.03, 0.3, 0.3)
        place(bus['fol'], breath(0.45, 'out', 90 + i, 0.4 + 0.1 * i), t + 0.45, 1.0, -0.4)
    place(bus['hit'], sub_boom(), Z, 1.25, 0.0)
    ex = load('814046__qubodup__explosion-from-another-dimension.wav', SR * 4); ex = lp(ex, 900)[:int(4.5 * SR)]; ex /= np.abs(ex).max(); place(bus['hit'], ex * env(len(ex), 0.01, 1.3), Z, 0.35, 0.0)
    place(bus['fol'], breath(1.1, 'out', 320, 0.5), Z + 0.6, 1.0, -0.4)
    place(bus['fol'], base.cloth(0.5, 321, 0.5), W0 - 0.5, 1.0, -0.3); place(bus['fol'], base.leather(0.3, 322, 0.4), W0 - 0.3, 1.0, 0.2)       # he reaches for the laptop
    rr = np.random.default_rng(5); tc = W0 + 0.1
    while tc < W1 - 0.1: place(bus['fol'], base.key_click(int(tc * 1000)), tc, 0.4, 0.2); tc += rr.exponential(0.12) + 0.02
    k = 0; tt = W0
    while tt < W1 + 0.4: place(bus['fol'], base.tick(400 + k), tt, 0.3 + 0.12 * (k / 14), 0.45); tt += 0.34; k += 1
    place(bus['air'], base.whoosh(2.2, 300, 3200, 742, 0.35), W0 + 1.2, 0.6, 0.0)                                                          # the clock racing
    place(bus['fol'], breath(1.2, 'out', 741, 0.5), W0 + 3.4, 1.0, -0.4)
    place(bus['fol'], base.paper_slide(0.7, 77, 0.9), TL['flipPage'][0] + 0.1, 1.0, 0.1); place(bus['fol'], base.paper_slap(555, 0.4), TL['flipPage'][1] - 0.1, 1.0, 0.1)   # the page turns
    sw = int(3.0 * SR); ts = np.arange(sw) / SR; ramp = (ts / 3.0) ** 2
    swell = sum(np.sin(2 * np.pi * f * ts + 0.3 * i) * a for i, (f, a) in enumerate([(196, 1.0), (294, 0.7), (392, 0.55), (588, 0.3)])) * ramp * 0.07 * (1 + 0.3 * np.sin(2 * np.pi * 5 * ts))
    place(bus['drone'], swell, W1 - 0.4, 1.0, 0.0)
    write_wav(finish(bus, duck), out); print('wrote', out)
if __name__ == '__main__': main(sys.argv[1])
