"""Sound for Build It As You Climb (Slow Light Dark). No music; every sound has a visible cause (series rule).

  python3 mix.py OUT.wav

- Bed: room tone, lamp hum, and a 55 Hz drone that rises as he climbs toward the light.
- Action taker: per plank, the cloth swish of the reach back, a wooden knock as it lands on the rails (pitch rising
  with height), a rope-lash squeak with an ember crackle, then two footfalls on wood as he steps up.
- Perfectionist: soft sandpaper strokes, panned left, the whole time he kneels; they stop dead when he stands.
- Through the hatch: a recorded riser-hit (CC0 audiopapkin 822420) and the hall swell; then near-silence on the light.
- His one red rung: a held breath, then a single clean click into the pillars. Sitting down: one low thud, one exhale.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_sound as K
from sld_sound import SR, lp, hp, bp, env, noise, place, curve, thud, breath, creak, write_wav

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
DUR = TL['duration']; N = int(DUR * SR)
T, BF, FAST = TL['cycle'], TL['buildFrac'], TL['fastStep']
NB = TL['rungsTotal'] - TL['rungsStart']; BEND = NB * T


def wood(seed, f0=230, gain=1.0, bright=1.0):
    """A plank knocked on wood: a few short inharmonic modes + a dry click."""
    r = np.random.default_rng(seed); n = int(0.5 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k, m in enumerate([1.0, 2.6, 4.9, 7.3]):
        y += np.sin(2 * np.pi * f0 * m * (0.95 + 0.1 * r.random()) * t) * np.exp(-t / (0.05 / (1 + 0.9 * k))) / (1 + 0.6 * k)
    click = bp(noise(n), 2400, 1.2) * env(n, 0.0002, 0.004) * 0.8 * bright
    body = lp(noise(n), 500) * env(n, 0.001, 0.02) * 0.5
    return np.tanh((y * 0.9 + click + body) * 1.2) * gain


def sizzle(dur, seed, gain=1.0):
    r = np.random.default_rng(seed); n = int(dur * SR); y = np.zeros(n); i = 0
    while i < n - 2000:
        m = 200 + int(900 * r.random()); y[i:i + m] += bp(noise(m), 3000 + 4000 * r.random(), 2.5) * env(m, 0.0002, 0.003) * r.random() ** 1.5
        i += int(r.exponential(0.014) * SR)
    return y * np.exp(-np.arange(n) / SR / (dur * 0.4)) * gain


def sand_stroke(dur, seed, gain=1.0):
    n = int(dur * SR); x = np.random.default_rng(seed).standard_normal(n)
    grain = np.repeat(np.random.default_rng(seed + 1).random(n // 120 + 1), 120)[:n] ** 2
    y = bp(x, 3800, 1.0) * (0.4 + grain) + bp(x, 7000, 1.6) * 0.4
    return y * np.sin(np.pi * np.arange(n) / n) ** 1.3 * gain


def swish(dur, f=1100, gain=0.1):
    n = int(dur * SR); return bp(noise(n), f, 1.0) * np.sin(np.pi * np.arange(n) / n) ** 2 * gain


bus = K.new_buses(N)
room_g = curve(N, [(0, 0.45), (DUR, 0.45)])
drone_g = curve(N, [(0, 0.15), (BEND, 0.7), (7.3, 0.9), (8.2, 0.3), (DUR, 0.2)])
P = TL['pPlace']
duck = curve(N, [(0, 1), (P - 0.45, 1), (P - 0.4, 0.06), (P - 0.01, 0.06), (P, 1), (DUR, 1)])
K.bed(bus, room_g, drone_g, duck)

PAN_A, PAN_P = 0.35, -0.45
# frame 0: he is already reaching for a plank, the sound starts present
place(bus['air'], swish(0.3, 900, 0.3), 0.0, 1.0, PAN_A)
steps = []
for k in range(NB):
    t0 = k * T
    place(bus['air'], swish(0.22, 1300, 0.12), t0 + 0.02, 1.0, PAN_A)                        # reach back to the bundle
    place(bus['fol'], wood(30 + k, 200, 0.25, 0.5), t0 + BF * T * 0.3, 1.0, PAN_A)            # plank pulled off the bundle
    place(bus['air'], swish(0.25, 900, 0.1), t0 + BF * T * 0.35, 1.0, PAN_A)                  # lifted overhead
    tp = t0 + BF * T * 0.68
    place(bus['hit'], wood(100 + k, 210 + 9 * k, 0.75, 1.0), tp, 1.0, PAN_A)                  # it lands on the rails
    place(bus['fol'], creak(200 + k, 0.22) * 0.5, tp + 0.04, 1.0, PAN_A)                      # rope lashed tight
    place(bus['air'], sizzle(0.5, 300 + k, 0.22), tp + 0.03, 1.0, PAN_A)                      # ember glint
    v0 = t0 + BF * T
    steps += [v0 + (1 - BF) * T * 0.42, v0 + (1 - BF) * T * 0.88]
for k in range(4):
    steps += [BEND + k * FAST + FAST * 0.42, BEND + k * FAST + FAST * 0.88]
for i, ts in enumerate(steps):
    if ts > 7.4: break
    place(bus['fol'], wood(500 + i, 150, 0.22, 0.3), ts, 1.0, PAN_A)
    place(bus['fol'], thud(600 + i, f=80, dec=0.05, gain=0.25), ts, 1.0, PAN_A)
# the light: recorded riser-hit with its peak as he goes through
rh = K.load('822420__audiopapkin__riser-hit-sfx-120.wav'); rh /= np.abs(rh).max()
e = np.convolve(rh ** 2, np.ones(2400) / 2400, 'same'); pk = int(np.argmax(e))
place(bus['hit'], rh, 7.25 - pk / SR, 0.7, 0.2)
# perfectionist: sanding strokes, two per cycle of the hand motion (8.5 rad/s), silent while he inspects
per = 2 * np.pi / 8.5 / 2; ts = 0.0; i = 0
while ts < TL['pStand'] - 0.3:
    insp = any(a + 0.1 < ts < b - 0.1 for a, b in TL['inspect'])
    if not insp: place(bus['fol'], sand_stroke(per * 0.9, 700 + i, 0.09), ts, 1.0, PAN_P)
    ts += per; i += 1
place(bus['fol'], thud(800, f=90, dec=0.06, gain=0.25), TL['pStand'] + 0.3, 1.0, PAN_P)      # gets up
place(bus['fol'], breath(0.6, 'in', 81, 0.16), P - 0.55, 1.0, PAN_P)
place(bus['hit'], wood(900, 420, 0.9, 1.4), P, 1.0, PAN_P)                                   # the perfect rung clicks home
place(bus['hit'], K.chink(901, 2600) * 0.5, P + 0.005, 1.0, PAN_P)
place(bus['fol'], thud(902, f=65, dec=0.14, gain=0.6), TL['pSit'] + 0.75, 1.0, PAN_P)        # sits down
place(bus['fol'], breath(1.4, 'out', 83, 0.2), TL['pSit'] + 1.0, 1.0, PAN_P)
mix = K.finish(bus, duck)
xf = int(TL['loopXfade'] * SR); mix[:, -xf:] *= np.linspace(1, 0, xf) ** 1.5
write_wav(mix, sys.argv[1])
def db(a, b):
    s = mix[:, int(a * SR):int(b * SR)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12)
print(f'rms 0-0.5 {db(0, 0.5):.1f} | build 1-6 {db(1, 6):.1f} | flare {db(7, 7.6):.1f} | held breath {db(P - 0.38, P - 0.02):.1f} | click {db(P, P + 0.3):.1f} dB')
