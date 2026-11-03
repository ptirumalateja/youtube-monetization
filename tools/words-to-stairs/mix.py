"""Sound for They Threw Words (Slow Light Dark). No music; every sound has a visible cause.

  python3 mix.py OUT.wav

- Bed: the series room tone (CC0 wind), lamp hum and a 55 Hz drone that rises slowly as he climbs.
- Each throw: a recorded whoosh (CC0 tomlija 175183, one of its five takes per throw) peaking mid-flight.
- Each catch: a stone slap into his hands (low thud + grit). Each placement: stone set on stone, a heavy clack,
  and a short dry ember crackle as the word burns into the face (no tone, no chime). Each step up: a footfall.
- Red block: bigger whoosh, then everything ducks for ~0.25 s, then the only big hit: a heavy stone slam on the floor
  (sub_boom + the CC0 qubodup 814046 explosion two octaves down, low-passed) and gravel settling.
- After it: room tone only, the drone thins out, one slow exhale from him.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_sound as K
from sld_sound import SR, lp, hp, bp, env, noise, place, curve, thud, breath, sub_boom, write_wav

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
DUR = TL['duration']; N = int(DUR * SR); t = np.arange(N) / SR
C = TL['catches']; FL = TL['flight']; PL = TL['place']; RR, RL = TL['redRelease'], TL['redLand']


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


bus = K.new_buses(N)
room_g = curve(N, [(0, 0.45), (RL, 0.45), (RL + 0.6, 0.55), (DUR, 0.55)])
drone_g = curve(N, [(0, 0.12), (2, 0.2), (C[-1], 0.75), (RR, 0.9), (RL, 0.9), (RL + 2.5, 0.35), (DUR, 0.25)])
duck = curve(N, [(0, 1), (TL['silence0'], 1), (TL['silence0'] + 0.06, 0.05), (RL - 0.01, 0.05), (RL, 1), (DUR, 1)])
K.bed(bus, room_g, drone_g, duck)

for k, c in enumerate(C):
    rel = c - FL; th = TL['throwers'][k]; pan_h = -0.45 if th == 0 else -0.6
    whoosh(bus['air'], k, rel + FL * 0.55, 0.32 + 0.02 * k, pan_h * 0.5)
    # catch: slap into the hands
    place(bus['fol'], thud(10 + k, f=95, dec=0.07, gain=0.45), c, 1.0, 0.1)
    place(bus['fol'], bp(noise(int(0.05 * SR)), 1800, 1.5) * env(int(0.05 * SR), 0.0005, 0.01) * 0.25, c, 1.0, 0.1)
    # placement: stone on stone, getting heavier as the stair grows
    w = 0.75 + 0.05 * k
    place(bus['hit'], stone_hit(100 + k, w, bright=0.8), c + PL, 0.55 + 0.03 * k, 0.15)
    place(bus['air'], sizzle(0.7, 200 + k, 0.35), c + PL + 0.1, 1.0, 0.2)
    # step up: lift + footfall onto the new block
    place(bus['fol'], thud(300 + k, f=80, dec=0.09, gain=0.35), c + 0.80, 1.0, 0.2)
    place(bus['fol'], thud(320 + k, f=90, dec=0.06, gain=0.22), c + 0.93, 1.0, 0.25)
    # thrower's footfall on the release
    place(bus['fol'], thud(400 + k, f=75, dec=0.08, gain=0.18), rel, 1.0, pan_h)

# the red block: the throw, the held breath, the slam
whoosh(bus['air'], 2, RR + (RL - RR) * 0.4, 0.5, -0.5)
place(bus['fol'], thud(500, f=70, dec=0.1, gain=0.25), RR, 1.0, -0.7)
boom = sub_boom(4.0) * 1.1
ex = K.load('814046__qubodup__explosion-from-another-dimension.wav'); ex = np.interp(np.arange(0, len(ex) - 1, 0.25), np.arange(len(ex)), ex)
ex = lp(ex, 2200) / np.abs(ex).max(); ne = int(3.5 * SR)
place(bus['hit'], boom, RL, 1.0, -0.1)
place(bus['hit'], ex[:ne] * env(ne, 0.002, 1.1)[:len(ex[:ne])], RL, 0.55, -0.1)
place(bus['hit'], stone_hit(999, 1.6), RL, 1.0, -0.15)
place(bus['hit'], stone_hit(998, 1.0), RL + 0.24, 0.35, -0.1)        # the small bounce
place(bus['fol'], gravel_rain(1.6, 80, 5, 0.6), RL + 0.05, 1.0, -0.2)
# afterwards: one slow exhale from him, high up in the light
place(bus['fol'], breath(1.3, 'out', 61, 0.22), TL['standTall'] + 0.1, 1.0, 0.2)

mix = K.finish(bus, duck)
write_wav(mix, sys.argv[1])
def db(a, b):
    s = mix[:, int(a * SR):int(b * SR)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12)
print(f'rms build 2-10 s {db(2, 10):.1f} dB | held breath {db(TL["silence0"] + 0.08, RL - 0.02):.1f} dB | slam {db(RL, RL + 1):.1f} dB | tail {db(15, 18):.1f} dB')
