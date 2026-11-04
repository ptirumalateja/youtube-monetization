"""Sound for Their Words Became His Wall (Slow Light Dark, V2 of They Threw Words). No music and no voices (Teja, 3 Nov: just brick-throwing sounds); every sound has a visible cause.

  python3 mix.py OUT.wav

- Bed: the series room tone (CC0 wind), lamp hum and a 55 Hz drone that rises slowly as he climbs.
- Each throw: a recorded whoosh (CC0 tomlija 175183, one of its five takes per throw) peaking mid-flight.
- Each catch: a stone slap into his hands (low thud + grit). Each placement: stone set on stone, a heavy clack,
  and a short dry ember crackle as the word burns into the face (no tone, no chime). Each step up: a footfall.
- Red brick: bigger whoosh, everything ducks for the held breath, then the only big hit: it slams into the wall's face
  in front of him (sub_boom + the CC0 qubodup 814046 explosion two octaves down + stone on stone), dust, and it drops
  back on the floor in front of the men. One slow exhale from him, safe behind his wall.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_sound as K
from sld_sound import SR, lp, hp, bp, env, noise, place, curve, thud, breath, sub_boom, write_wav

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
DUR = TL['duration']; N = int(DUR * SR); t = np.arange(N) / SR
C = TL['catches']; FL = TL['flight']; PL = TL['place']; RR, RC, RL = TL['redRelease'], TL['redHit'], TL['redLand']


def stone_hit(seed, weight=1.0, bright=1.0):
    """Stone on stone: crack + body + pitch-drop thump + sub + crumble (from The 100th Hit's kit)."""
    r = np.random.default_rng(seed); n = int(1.2 * SR); tt = np.arange(n) / SR
    crack = hp(noise(n), 2400) * env(n, 0.0003, 0.005) * 1.1 * bright
    body = (bp(noise(n), 380 * (0.9 + 0.2 * r.random()), 1.1) * env(n, 0.0008, 0.05) * 1.5
            + bp(noise(n), 1000, 1.4) * env(n, 0.0005, 0.025) * 0.6 * bright)
    f = 60 + 70 * np.exp(-tt / 0.025); thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.13) * 1.3 * weight
    sub = np.sin(2 * np.pi * (38 + 14 * np.exp(-tt / 0.05)) * tt) * env(n, 0.003, 0.22) * 0.55 * weight
    crumble = np.zeros(n)
    for _ in range(int(4 + 8 * r.random())):
        i = int((0.02 + r.exponential(0.08)) * SR)
        if i < n - 2000:
            crumble[i:i + 1800] += bp(noise(1800), 2000 + 2500 * r.random(), 2.0) * env(1800, 0.0002, 0.006) * (0.08 + 0.2 * r.random())
    return np.tanh((crack + body + thump + sub + crumble) * 0.9)


def gravel_rain(dur, rate, seed, gain=1.0):
    r = np.random.default_rng(seed); n = int((dur + 0.4) * SR); y = np.zeros(n); tt = 0.0
    while tt < dur:
        m = 1500 + int(4000 * r.random()); i = int(tt * SR)
        g = bp(noise(m), 900 + 3200 * r.random(), 1.6) * env(m, 0.0003, 0.004 + 0.02 * r.random()) * (0.15 + 0.85 * r.random() ** 2)
        k = min(m, n - i); y[i:i + k] += g[:k]
        tt += r.exponential(1 / (rate * np.exp(-tt / (dur * 0.45))))
    return y * gain


def sizzle(dur, seed, gain=1.0):
    """Dry ember crackle (word burning into stone): sparse noise ticks, no pitch."""
    r = np.random.default_rng(seed); n = int(dur * SR); y = np.zeros(n); i = 0
    while i < n - 2000:
        m = 200 + int(900 * r.random()); y[i:i + m] += bp(noise(m), 3000 + 4000 * r.random(), 2.5) * env(m, 0.0002, 0.003) * r.random() ** 1.5
        i += int(r.exponential(0.012) * SR)
    return y * np.exp(-np.arange(n) / SR / (dur * 0.4)) * gain


# recorded whooshes: five takes in the CC0 file; each is trimmed and its loudest point lined up with mid-flight
WH_RAW = K.load('175183__tomlija__5-everyday-whooshes.wav')
WH = []
for a, b in [(3.0, 4.6), (7.45, 9.5), (12.0, 14.8), (16.7, 19.2), (21.5, 23.5)]:
    s = WH_RAW[int(a * SR):int(b * SR)].copy(); s /= np.abs(s).max()
    e = np.convolve(s ** 2, np.ones(1200) / 1200, 'same'); WH.append((s, int(np.argmax(e))))


def whoosh(bus, k, t_peak, gain, pan):
    s, pk = WH[k % len(WH)]; place(bus, hp(s, 160), t_peak - pk / SR, gain, pan)


PAN = {0: -0.5, 1: -0.65, 2: -0.8, 3: -0.4}

bus = K.new_buses(N)
room_g = curve(N, [(0, 0.45), (RC, 0.45), (RC + 0.6, 0.55), (DUR, 0.55)])
drone_g = curve(N, [(0, 0.12), (2, 0.2), (C[-1], 0.7), (RR, 0.85), (RC, 0.85), (RL + 2.0, 0.35), (DUR, 0.25)])
duck = curve(N, [(0, 1), (TL['silence0'], 1), (TL['silence0'] + 0.05, 0.04), (RC - 0.01, 0.04), (RC, 1), (DUR, 1)])
K.bed(bus, room_g, drone_g, duck)

for k, c in enumerate(C):
    rel = c - FL; th = TL['throwers'][k]
    # the throw: wind-up cloth swish, release footfall, the block's whoosh
    place(bus['air'], bp(noise(int(0.25 * SR)), 1200, 1.0) * np.sin(np.pi * np.arange(int(0.25 * SR)) / int(0.25 * SR)) ** 2 * 0.12, max(0.0, rel - 0.3), 1.0, PAN[th])
    whoosh(bus['air'], k, rel + FL * 0.55, (0.62 if k == 0 else 0.3 + 0.015 * k), PAN[th] * 0.4)   # brick 0 is already flying on frame 0: loud from the start
    place(bus['fol'], thud(400 + k, f=75, dec=0.08, gain=0.3), rel, 1.0, PAN[th])
    # catch: slap into the hands
    place(bus['fol'], thud(10 + k, f=78 + 14 * k, dec=0.09, gain=0.6), c, 1.0, 0.25)   # signature thunk, rising in pitch as the wall grows
    place(bus['fol'], bp(noise(int(0.05 * SR)), 1800, 1.5) * env(int(0.05 * SR), 0.0005, 0.01) * 0.25, c, 1.0, 0.25)
    # placement: stone set into the wall, heavier as it grows; the word burns in
    place(bus['hit'], stone_hit(100 + k, 0.8 + 0.04 * k, bright=0.8), c + PL, 0.55 + 0.025 * k, 0.3)
    place(bus['air'], sizzle(0.7, 200 + k, 0.3), c + PL + 0.1, 1.0, 0.3)
    # a shuffle step to the next column
    place(bus['fol'], thud(300 + k, f=90, dec=0.05, gain=0.16), c + PL + 0.3, 1.0, 0.3)

# the red brick: the throw, the held breath, the slam into the wall in front of him, the drop back in front of them
whoosh(bus['air'], 2, RR + (RC - RR) * 0.5, 0.6, -0.1)
place(bus['fol'], thud(500, f=70, dec=0.1, gain=0.3), RR, 1.0, PAN[3])
boom = sub_boom(4.0) * 1.1
ex = K.load('814046__qubodup__explosion-from-another-dimension.wav'); ex = np.interp(np.arange(0, len(ex) - 1, 0.25), np.arange(len(ex)), ex)
ex = lp(ex, 2200) / np.abs(ex).max(); ne = int(3.0 * SR)
place(bus['hit'], boom, RC, 1.0, 0.3)
place(bus['hit'], ex[:ne] * env(ne, 0.002, 1.0)[:len(ex[:ne])], RC, 0.55, 0.3)
place(bus['hit'], stone_hit(999, 1.7), RC, 1.0, 0.3)
place(bus['hit'], stone_hit(997, 1.3), RC + 0.006, 0.7, 0.35)
place(bus['fol'], gravel_rain(1.2, 90, 4, 0.5), RC + 0.03, 1.0, 0.3)
place(bus['hit'], stone_hit(998, 1.1), RL, 0.55, -0.1)          # it drops back in front of them
place(bus['fol'], gravel_rain(1.4, 70, 5, 0.4), RL + 0.05, 1.0, -0.1)
# the hop up onto the wall: push-off scuff, then feet landing on stone, then one slow exhale up there
place(bus['fol'], thud(610, f=85, dec=0.05, gain=0.3), TL['hop0'] + 0.1, 1.0, 0.35)
place(bus['hit'], stone_hit(611, 0.9, bright=0.6), TL['hopLand'], 0.6, 0.35)
place(bus['fol'], thud(612, f=70, dec=0.12, gain=0.7), TL['hopLand'], 1.0, 0.35)
place(bus['fol'], breath(1.3, 'out', 61, 0.22), TL['hopLand'] + 0.45, 1.0, 0.35)

# frame 0 hook: a brick is already in the air, so the sound starts loud: a throw thud + a fast close swish over the first 0.45 s
n0 = int(0.45 * SR); sw = bp(noise(n0), 900, 0.8) * np.sin(np.pi * np.arange(n0) / n0) ** 1.2
place(bus['air'], sw * 0.55, 0.0, 1.0, -0.2)
place(bus['fol'], thud(401, f=75, dec=0.08, gain=0.5), 0.0, 1.0, -0.5)
# the dodge: a close whoosh right past his head, then it smashes on the floor behind him
whoosh(bus['air'], 3, TL['dodgeAt'], 0.75, 0.3)
DL = TL['dodgeRel'] + 1.21                                           # landing time (same flat arc as dodgeState in scene.js)
place(bus['hit'], stone_hit(620, 1.3), DL, 0.85, 0.45)
place(bus['fol'], gravel_rain(0.8, 80, 6, 0.4), DL + 0.02, 1.0, 0.45)
mix = K.finish(bus, duck)
# seamless loop: the last loopXfade seconds fade out while the head's first second is already loud
xf = int(TL['loopXfade'] * SR); mix[:, -xf:] *= np.linspace(1, 0, xf) ** 1.5
write_wav(mix, sys.argv[1])
def db(a, b):
    s = mix[:, int(a * SR):int(b * SR)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12)
print(f'rms build 2-10 s {db(2, 10):.1f} dB | held breath {db(TL["silence0"] + 0.08, RC - 0.02):.1f} dB | slam {db(RC, RC + 0.8):.1f} dB | tail {db(DUR - 2, DUR):.1f} dB')
