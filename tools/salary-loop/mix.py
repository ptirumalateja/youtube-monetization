"""Sound for The Salary Loop: minimal but heavy, series kit (../slow-light-dark-common/sld_sound.py).

A notification chime and a phone buzz that run straight across the loop seam (the end of the file wraps into frame 0), accelerating
debit sounds (gold coin shimmer + one heavy foley per bill: stone, metal, paper bags, cables, plates, a draining gauge), then the
twist: silence, and one sub-boom the moment the balance reaches zero. Then near silence, a wallet, a mote, a ticking clock and an
alarm, then rhythmic footsteps on the treadmill, keyboard taps, a clock, and a rising golden swell into the next chime.
Everything is synthesised in numpy except two CC0 Freesound files (sleepCircle wind as room tone, qubodup explosion pitched down).

  python3 mix.py META.json OUT.wav        (META.json from `node render.cjs meta`)
"""
import json, os, sys
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'slow-light-dark-common'))
from sld_sound import *

HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(HERE, 'timeline.json')))
D = TL['duration']; N = int(D * SR)


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




def place_wrap(bus, sig, t, gain=1.0, pan=0.0):
    """Like place() but whatever runs past the end of the file wraps round to the start (the loop seam)."""
    place(bus, sig, t, gain, pan); i = int(round(t * SR)); over = i + len(sig) - bus.shape[1]
    if over > 0: place(bus, sig[len(sig) - over:], 0.0, gain, pan)


def chime(dur=2.4, f0=1318.5):
    n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for m, a, d in [(1, 1.0, 0.7), (1.5, 0.55, 0.55), (2.0, 0.4, 0.5), (3.0, 0.2, 0.3)]: y += a * np.sin(2 * np.pi * f0 * m * t) * np.exp(-t / d)
    t2 = np.clip(t - 0.16, 0, None); y2 = sum(a * np.sin(2 * np.pi * f0 * 1.5 * m * t2) * np.exp(-t2 / d) for m, a, d in [(1, 1, 0.8), (2, 0.4, 0.5)]) * (t > 0.16)   # second note: the fifth up
    return (y * 0.5 + y2 * 0.4) * np.minimum(1, t / 0.002) * 0.35


def buzz(dur, rate=40.0, f=150.0):
    n = int(dur * SR); t = np.arange(n) / SR; carrier = np.tanh(3 * np.sin(2 * np.pi * f * t)) * 0.6 + hp(noise(n), 2500) * 0.08
    return carrier * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * rate * t))) * 0.5


def coin_ting(seed, g=1.0):
    r = np.random.default_rng(seed); n = int(0.35 * SR); t = np.arange(n) / SR; f = 2300 + 1500 * r.random()
    return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t)) * np.exp(-t / (0.05 + 0.05 * r.random())) * 0.3 * g


def rumble(dur, seed, f=110):
    n = int(dur * SR); x = lp(np.random.default_rng(seed).standard_normal(n), f); t = np.arange(n) / n
    return x / (np.abs(x).max() + 1e-9) * np.sin(np.pi * t) ** 0.7


def key_click(seed):
    n = int(0.05 * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    return (hp(r.standard_normal(n), 2500) * np.exp(-t / 0.004) * 0.6 + np.sin(2 * np.pi * (700 + 300 * r.random()) * t) * np.exp(-t / 0.01) * 0.35)


def beep(dur=0.12, f=1760):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sign(np.sin(2 * np.pi * f * t)) * 0.4 + np.sin(2 * np.pi * f * t) * 0.4) * np.minimum(1, t / 0.003) * np.minimum(1, (dur - t) / 0.01)


def tick(seed, f=1900):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006) + hp(np.random.default_rng(seed).standard_normal(n), 4000) * np.exp(-t / 0.003) * 0.5) * 0.5


def main(meta_path, out_path):
    M = json.load(open(meta_path)); t = np.arange(N) / SR; bus = new_buses(N); zero = TL['zero']; items = TL['items']
    # silence as a beat: everything drops away just before the balance reaches zero; the boom lands on it
    duck = curve(N, [(0, 1), (zero - 0.34, 1), (zero - 0.28, 0.0), (zero - 0.01, 0.0), (zero, 0.6), (zero + 1.0, 1), (D, 1)])
    quiet = curve(N, [(0, 1), (zero + 0.4, 1), (zero + 0.6, 0.18), (9.2, 0.18), (9.6, 0.7), (10.2, 1), (D, 1)])             # near silence 7-9, back with the alarm
    light = np.interp(t, *zip(*TL['light'])); sc = np.interp(t, *zip(*TL['scroll'])); move = np.abs(np.gradient(sc, 1 / SR))      # world speed (m/s)
    room_g = curve(N, [(0, 0.08), (2, 0.1), (zero - 0.3, 0.12), (D, 0.1)]) * duck * (quiet * 0.7 + 0.3) * (1 + 0.12 * lp(move, 3) + 0.5 * (1 - light) * (t > 10))
    drone_g = curve(N, [(0, 0.2), (2, 0.25), (zero - 0.3, 0.6), (zero - 0.25, 0.0), (zero, 0.0), (zero + 1.5, 0.3), (9.3, 0.25), (D, 0.2)]) * (1 + 0.6 * (1 - light) * (t > 10))
    bed(bus, room_g, drone_g, duck)

    # ---- 0-2: the notification. Chime + buzz run across the loop seam (wrap), coins pour into the wallet
    for k in range(50): place(bus['air'], coin_ting(k, 0.8 + 0.2 * (k / 50)), 1.0 + k * 0.02 + 0.02, 0.5, -0.4 + 0.8 * ((k % 5) / 4))
    place(bus['fol'], breath(0.6, 'in', 1, 0.45), 1.2, 1.0, -0.4)                                                              # he wakes up to it
    bz = buzz(1.6); bz *= np.linspace(1, 0, len(bz)) ** 0.8; place(bus['fol'], bz, 0.0, 0.5, 0.2)                              # buzz at the start fades as he picks up on it
    # ---- 18.75-20: the buzz of the next salary (wraps into frame 0, where the buzz above starts at full level)
    bz2 = buzz(D - 17.45); bz2 *= np.minimum(1, np.linspace(0, 1, len(bz2)) * 6); place(bus['fol'], bz2, 17.45, 0.5, 0.2)
    place_wrap(bus['air'], chime(), 18.3, 1.0, 0.0)
    # ---- 2-6.4: six bills, faster and faster; gold shimmer + coin pull for each, one heavy object each
    foley = [lambda s: rumble(0.8, s, 90) * 0.9 + bp(noise(int(0.8 * SR)), 300, 1.0) * np.sin(np.pi * np.arange(int(0.8 * SR)) / int(0.8 * SR)) * 0.4,        # RENT: a building rising, stone grind
             lambda s: creak(s, 0.7) * 0.8 + clank(1.0, s, 0.6)[:int(0.7 * SR)] * 0.7,                                                                                            # EMI: a car lowered, metal groan, clank
             lambda s: paper_slide(0.6, s, 0.8) + bp(noise(int(0.6 * SR)), 2600, 1.0) * 0.25 * np.sin(np.pi * np.arange(int(0.6 * SR)) / int(0.6 * SR)),  # GROCERIES: bags
             lambda s: whoosh(0.6, 400, 4200, s, 1.0) + np.sin(2 * np.pi * 100 * np.arange(int(0.6 * SR)) / SR) * 0.1 * np.sin(np.pi * np.arange(int(0.6 * SR)) / int(0.6 * SR)),  # UTILITIES: cables whip + mains buzz
             lambda s: sum(np.pad(lp(clank(0.25, s * 7 + j, 1.4), 7000)[:int(0.3 * SR)], (int(j * 0.045 * SR), 0))[:int(0.6 * SR)] if False else np.zeros(int(0.6 * SR)) for j in range(1)),               # FOOD: plates (below)
             lambda s: np.sin(2 * np.pi * np.cumsum(np.linspace(900, 90, int(0.7 * SR))) / SR) * 0.35 * np.linspace(1, 0.3, int(0.7 * SR)) + bp(noise(int(0.7 * SR)), 1500, 0.8) * 0.2]  # FUEL: drains
    for i, it in enumerate(items):
        T0 = it['t']; big = 0.55 + 0.1 * i
        place(bus['hit'], foley[i](40 + i) * 0.9 if i != 4 else np.zeros(10), T0, 1.0, 0.0)
        if i == 4:
            for j in range(9): place(bus['hit'], lp(clank(0.35, 70 + j, 1.5), 8000)[:int(0.35 * SR)], T0 + j * 0.04, 0.22, -0.3 + 0.07 * j)
        place(bus['hit'], thud(60 + i, 52 - 2 * i, 0.22, 0.6 * big), T0 + 0.05, 1.0, 0.0)
        place(bus['air'], whoosh(0.45, 700, 4500, 80 + i, 0.7), T0 - 0.05, 1.0, -0.5 + 0.2 * i)                        # coins pulled out of the wallet
        for j in range(it['coins']): place(bus['air'], coin_ting(200 + 20 * i + j, 0.7), T0 + 0.02 + j * 0.014, 0.35, 0.3)
        place(bus['fol'], breath(0.4, 'out', 90 + i, 0.4 + 0.1 * i), T0 + 0.15, 1.0, -0.4)
    # ---- 6.4: the balance reaches zero. The only big hit.
    place(bus['hit'], sub_boom(), zero, 1.25, 0.0)
    ex = load('814046__qubodup__explosion-from-another-dimension.wav', SR * 4); ex = lp(ex, 900)[:int(4.5 * SR)]; ex /= np.abs(ex).max()
    place(bus['hit'], ex * env(len(ex), 0.01, 1.3), zero, 0.35, 0.0)
    # ---- 7-9.3: the empty wallet. leather, one mote, a clock begins to tick
    place(bus['fol'], leather(0.7, 301, 0.6), TL['walletUp'] - 0.35, 1.0, -0.1)
    place(bus['fol'], leather(0.5, 302, 0.7), TL['walletUp'] + 0.1, 1.0, 0.0)
    nn = int(1.6 * SR); tt = np.arange(nn) / SR; place(bus['air'], np.sin(2 * np.pi * 3100 * tt) * np.exp(-tt / 0.5) * 0.04 + np.sin(2 * np.pi * 4700 * tt) * np.exp(-tt / 0.3) * 0.02, TL['dust'], 1.0, 0.1)
    place(bus['fol'], breath(1.4, 'out', 303, 0.35), TL['dust'] + 0.2, 1.0, -0.3)
    for k in range(int((TL['alarm'] - 8.2) / 0.5)): place(bus['fol'], tick(310 + k), 8.2 + k * 0.5, 0.35 + 0.1 * k, 0.4)
    # ---- 9.3-10: the alarm
    for k in range(4): place(bus['air'], beep(0.12), TL['alarm'] + k * 0.2, 0.55, 0.0)
    bz3 = buzz(0.8); place(bus['fol'], bz3, TL['alarm'] - 0.1, 0.4, 0.2)
    # ---- 10-19: treadmill footsteps (from the scene), a ticking clock, keyboard taps in the office, the golden swell
    for s in M['steps']:
        g = 0.28 if s['t'] < 12 else 0.22
        place(bus['fol'], lp(thud(int(s['t'] * 977), 92, 0.07, 1.0), 1300), s['t'], g, float(np.clip(((s['t'] % 0.7) - 0.35) * 0.4, -0.3, 0.3)))
        place(bus['fol'], hp(lp(noise(int(0.05 * SR)), 5000), 2500) * env(int(0.05 * SR), 0.0005, 0.02) * 0.3, s['t'], 0.2, 0.0)
    rr = np.random.default_rng(5); tcur = TL['officeSit'] + 0.3
    while tcur < TL['work1']: place(bus['fol'], key_click(int(tcur * 1000)), tcur, 0.45, 0.2); tcur += rr.exponential(0.11) + 0.02
    for k in range(int((TL['work1'] - 10.3) / 0.5)): place(bus['fol'], tick(400 + k), 10.3 + k * 0.5, 0.28 + 0.12 * (k / 20), 0.45)         # a clock, louder as the day goes
    place(bus['fol'], chair_scrape := (bp(noise(int(0.4 * SR)), 650, 1.0) * np.sin(np.pi * np.arange(int(0.4 * SR)) / int(0.4 * SR)) * 0.5), TL['officeSit'], 1.0, -0.3)
    place(bus['hit'], thud(500, 58, 0.14, 0.4), TL['officeSit'] + 0.2, 1.0, -0.3)
    place(bus['fol'], breath(0.9, 'out', 501, 0.4), TL['officeSit'] + 0.3, 1.0, -0.4)
    sw = int(3.2 * SR); ts = np.arange(sw) / SR; ramp = (ts / 3.2) ** 2
    swell = sum(np.sin(2 * np.pi * f * ts + 0.3 * i) * a for i, (f, a) in enumerate([(196, 1.0), (294, 0.7), (392, 0.55), (588, 0.3)])) * ramp * 0.07 * (1 + 0.3 * np.sin(2 * np.pi * 5 * ts))
    place(bus['drone'], swell, 15.5, 1.0, 0.0)                                                                               # the golden light grows
    place(bus['air'], whoosh(1.0, 300, 3000, 600, 0.35), D - 1.15, 1.0, 0.0)                                                 # the camera rushes into the phone
    # ---- lived-in extras: the bed, the knocks, the bike, the fan and meter, the bus
    def knock(seed, g=1.0):
        n = int(0.25 * SR); tt = np.arange(n) / SR
        return (np.sin(2 * np.pi * (170 + 60 * np.exp(-tt / 0.01)) * tt) * np.exp(-tt / 0.05) + lp(noise(n), 3000) * np.exp(-tt / 0.006) * 0.7) * g
    place(bus['fol'], chair_scrape_(0.5, 600) if False else bp(noise(int(0.4 * SR)), 500, 1.0) * np.sin(np.pi * np.arange(int(0.4 * SR)) / int(0.4 * SR)) * 0.4, TL['rise'][0], 1.0, -0.4)        # bed creaks as he springs up
    place(bus['hit'], thud(601, 62, 0.14, 0.4), TL['rise'][1], 1.0, -0.2)
    for k, kt in enumerate(np.arange(TL['dance'][0], TL['dance'][1], 0.27)): place(bus['hit'], thud(610 + k, 75, 0.08, 0.35), kt, 1.0, -0.1 + 0.05 * k)    # tiny dance: happy stomps
    place(bus['fol'], breath(0.5, 'in', 620, 0.4), TL['rise'][0] - 0.1, 1.0, -0.4)
    for k, kt in enumerate(TL['knock']): place(bus['hit'], knock(630 + k, 0.8), kt, 1.0, -0.2)                                              # the landlord knocks
    for k, kt in enumerate([19.4, 19.58]): place_wrap(bus['hit'], knock(640 + k, 0.7), kt, 1.0, -0.2)                                       # ...and again before he can get up
    n_ = int(0.9 * SR); tt = np.arange(n_) / SR; place(bus['hit'], np.tanh(2 * np.sin(2 * np.pi * np.cumsum(70 + 160 * np.minimum(tt / 0.6, 1)) / SR)) * 0.35 * np.exp(-tt / 0.7), items[1]['t'], 0.7, 0.2)   # the bike's engine revs
    place(bus['air'], lp(noise(int(2.0 * SR)), 450) * np.minimum(1, np.arange(int(2.0 * SR)) / (0.8 * SR)) * 0.5, items[3]['t'], 0.6, 0.0)       # the fan spins up
    for k in range(14): place(bus['fol'], tick(650 + k, 2600), items[3]['t'] + 0.1 + k * 0.05, 0.3, 0.4)                                        # the meter whirrs
    place(bus['air'], hp(noise(int(0.8 * SR)), 3000) * env(int(0.8 * SR), 0.01, 0.3) * 0.25, TL['bus0'], 1.0, 0.3)                           # the bus air brake
    place(bus['drone'], np.tanh(2 * np.sin(2 * np.pi * 52 * np.arange(int(1.6 * SR)) / SR)) * 0.12 * np.sin(np.pi * np.arange(int(1.6 * SR)) / int(1.6 * SR)), TL['bus0'], 1.0, 0.0)   # idling diesel
    for k in range(6): place(bus['air'], bp(noise(int(0.7 * SR)), 700 + 150 * k, 0.8) * np.sin(np.pi * np.arange(int(0.7 * SR)) / int(0.7 * SR)) * 0.2, TL['board'] + k * 0.15, 1.0, -0.7 + 0.28 * k)   # traffic
    place(bus['hit'], thud(660, 52, 0.2, 0.55), TL['bed1'] - 0.15, 1.0, -0.3)                                                                  # he drops onto the bed, exhausted
    place(bus['fol'], breath(1.0, 'out', 661, 0.5), TL['bed1'] - 0.1, 1.0, -0.4)
    write_wav(finish(bus, duck), out_path); print('wrote', out_path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
