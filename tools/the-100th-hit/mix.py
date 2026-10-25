"""Sound for The 100th Hit (Slow Light Dark). Minimal but heavy; every sound has a visible cause.

  python3 mix.py META.json OUT.wav

- Hits 1-99: a layered stone impact (crack transient + stone body + pitch-drop thump + a little sub + gravel crumble +
  a faint iron ring from the sledge). Weight grows with the count; as the pace rises the thuds blur into a rumble.
- Under the build: the series bed (CC0 wind room tone, lamp hum, 55 Hz drone) with the drone swelling, plus an ember
  crackle that grows with the red glow (pressure building).
- Hit 99: hard stop. Everything (reverb tails included) is gated out within ~0.25 s. Then near silence: the dropped
  hammer's clunk, his slow footsteps, the other man's breathing, a strained inhale on the lift, ~0.25 s held breath.
- Hit 100: the biggest boom of the series: sub_boom + the CC0 qubodup 814046 explosion read two octaves down + a heavy
  stone burst + debris rain; a low warm swell under the gold light. Room tone comes back for the last beat.
No music. Two CC0 files from ../sfxlib (sleepCircle 22331 wind, qubodup 814046 explosion); everything else is synthesised.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_sound as K
from sld_sound import SR, lp, hp, bp, env, noise, place, curve, reverb_ir, convolve, thud, breath, sub_boom, clank, write_wav

meta = json.load(open(sys.argv[1])); E = meta['events']; HT = E['HT']
DUR = E['duration']; N = int(DUR * SR)
T99, T100 = HT[99], HT[100]


def stone_hit(seed, weight=1.0):
    """Sledge on stone: crack + stone body + thump + sub + crumble + a little iron ring."""
    r = np.random.default_rng(seed); n = int(1.2 * SR); t = np.arange(n) / SR
    crack = hp(noise(n), 2400) * env(n, 0.0003, 0.005) * 1.3
    body = (bp(noise(n), 420 * (0.9 + 0.2 * r.random()), 1.1) * env(n, 0.0008, 0.05) * 1.6
            + bp(noise(n), 1100, 1.4) * env(n, 0.0005, 0.025) * 0.7)
    f = 62 + 70 * np.exp(-t / 0.025); thump = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.001, 0.13) * 1.3 * weight
    sub = np.sin(2 * np.pi * (38 + 14 * np.exp(-t / 0.05)) * t) * env(n, 0.003, 0.22) * 0.55 * weight
    crumble = np.zeros(n)
    for k in range(int(6 + 10 * r.random())):
        i = int((0.02 + r.exponential(0.09)) * SR)
        if i < n - 2000:
            g = bp(noise(1800), 2000 + 2500 * r.random(), 2.0) * env(1800, 0.0002, 0.006) * (0.1 + 0.25 * r.random())
            crumble[i:i + 1800] += g
    ring = clank(0.6, seed, bright=0.5) * 0.06
    return np.tanh((crack + body + thump + sub + crumble) * 0.9) + ring[:n]


def gravel_rain(dur, rate, seed, gain=1.0):
    """Debris settling: many small stone ticks thinning out."""
    r = np.random.default_rng(seed); n = int((dur + 0.4) * SR); y = np.zeros(n); t = 0.0
    while t < dur:
        m = 1500 + int(4000 * r.random()); i = int(t * SR)
        g = bp(noise(m), 900 + 3200 * r.random(), 1.6) * env(m, 0.0003, 0.004 + 0.02 * r.random()) * (0.15 + 0.85 * r.random() ** 2)
        if r.random() < 0.15: g = g + thud(int(r.random() * 1e6), f=90 + 60 * r.random(), dec=0.05, gain=0.25)[:m]
        k = min(m, n - i); y[i:i + k] += g[:k]
        t += r.exponential(1 / (rate * np.exp(-t / (dur * 0.45))))
    return y * gain


def embers(n, seed):
    """Glowing-crack crackle: sparse sizzle ticks + a faint hiss."""
    r = np.random.default_rng(seed); y = np.zeros(n); i = 0
    while i < n - 3000:
        m = 300 + int(1500 * r.random()); y[i:i + m] += bp(noise(m), 2500 + 4000 * r.random(), 2.5) * env(m, 0.0002, 0.003) * r.random() ** 2
        i += int(r.exponential(0.02) * SR)
    return y + hp(noise(n), 4000) * 0.02


def octave_down2(x):
    """Read a sample at quarter speed (two octaves down, four times longer)."""
    idx = np.arange(0, len(x) - 1, 0.25); return np.interp(idx, np.arange(len(x)), x)


t = np.arange(N) / SR
A = {k: np.zeros((2, N)) for k in ['bed', 'drone', 'fol', 'hit', 'air']}   # up to hit 99 (gated out after it)
B = {k: np.zeros((2, N)) for k in ['bed', 'drone', 'fol', 'hit', 'air']}   # after hit 99

# ---- bed under the build: room + hum + drone (drone swells across the hits); embers grow with the glow
room_g = curve(N, [(0, 0.5), (2, 0.5), (T99, 0.3), (DUR, 0.3)])
drone_g = curve(N, [(0, 0.15), (2.0, 0.25), (8.0, 0.9), (T99, 2.0), (DUR, 2.0)])
K.bed(A, room_g, drone_g, np.ones(N))
# rising low drone on top (sub-octave rising 41 -> 62 Hz, audible harmonics) as the pace climbs
f = 41 + 21 * np.clip((t - 2) / (T99 - 2), 0, 1) ** 1.6; ph = 2 * np.pi * np.cumsum(f) / SR
rise = np.tanh(1.8 * (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph))) * 0.12 * np.clip((t - 3) / (T99 - 3), 0, 1) ** 1.4
for c in range(2): A['drone'][c] += rise
heat = np.clip((t - 2) / (T99 - 2), 0, 1) ** 1.5
emb = embers(N, 3) * heat * 0.5
place(A['air'], emb, 0, 1.0, -0.3); place(A['air'], embers(N, 4) * heat * 0.5, 0, 1.0, 0.3)

# ---- hits 1..99 (pan slightly left: the boulder sits left of centre)
for k in range(1, 100):
    D = HT[k] - HT[k - 1] if k > 1 else 0.9
    w = 0.8 + 0.5 * k / 99
    g = 0.95 * max(0.3, (D / 0.9) ** 0.45) * (0.7 + 0.6 * (k / 99) ** 2)   # the rumble keeps swelling to 99
    place(A['hit'], stone_hit(100 + k, w), HT[k], g, -0.25)
    # hammer wind-up whoosh on the slow swings only
    if D > 0.25:
        n = int(0.35 * SR); wh = bp(noise(n), 700, 1.0) * np.sin(np.pi * np.arange(n) / n) ** 2 * 0.25 * (D / 0.9)
        place(A['air'], wh, HT[k] - 0.3, 1.0, 0.2)
# footfall weight on the first few heavy swings
for k in range(1, 6): place(A['fol'], thud(200 + k, f=75, dec=0.12, gain=0.5), HT[k] + 0.01, 1.0, 0.25)
# lift-off of the first swing (hammer leaves the floor)
place(A['fol'], clank(0.4, 7, bright=0.6) * 0.15, 0.08, 1.0, 0.1)

# ---- after 99: near silence with a few visible causes
# the dropped hammer (top): iron on concrete, a small bounce
place(B['fol'], clank(1.2, 41, bright=0.8) * 0.55, E['land'], 1.0, 0.0)
place(B['fol'], thud(42, f=70, dec=0.15, gain=0.6), E['land'], 1.0, 0.0)
place(B['fol'], clank(0.7, 43, bright=0.6) * 0.18, E['land'] + 0.15, 1.0, 0.0)
# his footsteps, slow, fading into the dark
for i, ts in enumerate(np.arange(E['walk'] + 0.15, E['fade1'], 0.62)):
    place(B['fol'], thud(300 + i, f=85, dec=0.07, gain=0.22 * (1 - (ts - E['walk']) / (E['fade1'] - E['walk']))), ts, 1.0, 0.35)
# the other one breathes: two heavy exhales, then a long strained inhale on the lift
place(B['fol'], breath(0.9, 'out', 51, 0.3), T99 + 0.6, 1.0, 0.1)
place(B['fol'], breath(0.8, 'in', 52, 0.18), E['breath'] - 0.05, 1.0, 0.1)
place(B['fol'], breath(0.9, 'out', 53, 0.28), E['breath'] + 0.6, 1.0, 0.1)
place(B['fol'], breath(E['lift1'] - E['lift0'], 'in', 54, 0.3), E['lift0'], 1.0, 0.1)
# the hammer leaving the floor for the last lift
place(B['fol'], clank(0.4, 55, bright=0.5) * 0.12, E['lift0'] + 0.05, 1.0, 0.0)
# a faint drone creeps back under the lift, then the held breath (nothing at all) before 100
creep = np.tanh(1.6 * (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 110.4 * t))) * 0.08 * np.clip((t - E['lift0']) / (E['lift1'] - E['lift0']), 0, 1) ** 2
creep *= (t < E['strike0']).astype(float)
for c in range(2): B['drone'][c] += creep

# ---- hit 100
boom = sub_boom(4.5) * 1.3
exp = octave_down2(K.load('814046__qubodup__explosion-from-another-dimension.wav')); exp = lp(exp, 2500) / np.abs(exp).max()
place(B['hit'], boom, T100, 1.0, 0.0)
place(B['hit'], exp[:int(4.5 * SR)] * env(int(4.5 * SR), 0.002, 1.6)[:len(exp[:int(4.5 * SR)])], T100, 0.75, 0.0)
place(B['hit'], stone_hit(999, 1.5), T100, 1.0, -0.2)
place(B['hit'], stone_hit(998, 1.4), T100 + 0.012, 0.8, 0.2)
place(B['fol'], gravel_rain(2.0, 90, 5, 0.9), T100 + 0.08, 1.0, -0.3)
place(B['fol'], gravel_rain(2.0, 70, 6, 0.8), T100 + 0.1, 1.0, 0.3)
# the gold light: a low warm swell (A major, very soft), slow attack
sw = np.zeros(N); m = t >= T100; tt = t[m] - T100
for fr, a in ((55, 1.0), (110, 0.6), (138.6, 0.35), (164.8, 0.4), (220, 0.25), (277.2, 0.12)):
    sw[m] += np.sin(2 * np.pi * fr * tt + fr) * a
sw[m] *= (1 - np.exp(-tt / 0.6)) * np.exp(-np.maximum(0, tt - 1.2) / 2.5) * 0.05
for c in range(2): B['air'][c] += sw * (1 + 0.1 * np.sin(2 * np.pi * (0.2 + 0.05 * c) * t))
# room tone returns under the last beat
room_b = curve(N, [(0, 0), (T100 + 0.3, 0), (T100 + 1.5, 0.35), (DUR, 0.35)])
K.bed(B, room_b, np.zeros(N), np.ones(N))


def bus_mix(bus, hit_reverb=0.3):
    for k in bus: bus[k] = np.nan_to_num(bus[k])
    for c in range(2):
        for k in ['fol', 'air', 'bed', 'drone']: bus[k][c] = hp(bus[k][c], 90 if k in ('fol', 'air') else 75, 3)
    ir_room = [reverb_ir(1.6, 3500, 1), reverb_ir(1.6, 3500, 2)]
    ir_hall = [reverb_ir(3.4, 1800, 3), reverb_ir(3.4, 1800, 4)]
    wet_f = np.stack([convolve(bus['fol'][c], ir_room[c]) for c in range(2)])
    wet_h = np.stack([convolve(bus['hit'][c], ir_hall[c]) for c in range(2)])
    he = lp(np.abs(bus['hit']).max(0), 8); sc = 1 - 0.45 * np.clip(he / (he.max() + 1e-9) * 3, 0, 1)
    return bus['bed'] * sc + bus['drone'] * sc + bus['fol'] + wet_f * 0.22 + bus['hit'] + wet_h * hit_reverb + bus['air']


mixA = bus_mix(A, 0.22)
gate = curve(N, [(0, 1), (T99 + 0.1, 1), (T99 + 0.32, 0), (DUR, 0)])   # hard stop after 99, tails included
mixB = bus_mix(B, 0.35)
mix = mixA * gate[None] * 0.55 + mixB   # the build sits well under the hit-100 boom (biggest hit of the series)
mix = np.tanh(mix / np.abs(mix).max() * 1.4) / np.tanh(1.4)
fz = int(0.004 * SR); mix[:, :fz] *= np.linspace(0, 1, fz); mix[:, -fz:] *= np.linspace(1, 0, fz)
write_wav(mix, sys.argv[2])
# report the silence window (between the gate and the held breath) so the QA can check it
def db(a, b):
    s = mix[:, int(a * SR):int(b * SR)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12)
print(f'rms build 10-13 s {db(10, 13):.1f} dB | after-99 {db(T99 + 0.4, E["land"] - 0.02):.1f} dB | held breath {db(E["strike0"] + 0.02, T100 - 0.01):.1f} dB | boom {db(T100, T100 + 1):.1f} dB')
