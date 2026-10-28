"""Sound for You Were Blind for 20 Minutes Today. Room tone + lamp hum (CC0 sleepCircle wind via sld_sound.bed), a soft clock tick in the flat,
and every blink is heard as the room going muffled for a moment with a low "thup". The day montage has one foley cue per time of day, the
rehook gets a held breath and the only big hit, the eye gets a wet blink and a riser into the pupil, the brain crackles and goes quiet on each
blink. Everything else is synthesised in numpy.

  python3 mix.py OUT.wav
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sld_sound import *
D = 19.0; N = int(D * SR)
BLINKS = [0.95, 3.1, 5.2, 6.45, 7.5, 8.45, 9.5, 10.05, 10.3, 10.52, 10.72, 10.9, 11.06, 16.75, 17.85]
SHOTS = [0.0, 6.0, 7.0, 8.0, 9.0, 10.0, 12.0, 13.8, 16.0]
R = np.random.default_rng(7)

def thup(seed, g=1.0):
    """The sound of the lid: a low, soft, closed-mouth knock."""
    n = int(0.3 * SR); tt = np.arange(n) / SR
    return lp(np.sin(2 * np.pi * (72 + 40 * np.exp(-tt / 0.02)) * tt) * np.exp(-tt / 0.07) + 0.25 * bp(noise(n), 400, 1.4) * np.exp(-tt / 0.02), 900) * g
def tick(seed, g=1.0):
    n = int(0.06 * SR); tt = np.arange(n) / SR; return bp(noise(n), 3200, 2.0) * np.exp(-tt / 0.004) * g
def whoosh(dur, f0, f1, g=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; return bp(noise(n), np.sqrt(f0 * f1), 0.7) * np.sin(np.pi * tt / dur) ** 2 * g
def chirp(seed):
    r = np.random.default_rng(seed); n = int(0.18 * SR); tt = np.arange(n) / SR; f = 3400 + 900 * r.random()
    return np.sin(2 * np.pi * (f + 700 * np.sin(2 * np.pi * 16 * tt)) * tt) * np.exp(-((tt - 0.07) / 0.04) ** 2) * 0.5
def key_click(seed):
    n = int(0.03 * SR); tt = np.arange(n) / SR; return bp(np.random.default_rng(seed).standard_normal(n), 2400, 1.5) * np.exp(-tt / 0.006)
def page(dur=0.45, g=1.0):
    n = int(dur * SR); tt = np.arange(n) / SR; return bp(noise(n), 2200, 0.8) * np.sin(np.pi * tt / dur) ** 1.5 * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt)) * g
def riser(dur):
    n = int(dur * SR); tt = np.arange(n) / SR; x = noise(n)
    lo = bp(x, 500, 1.0); hi = bp(x, 2500, 1.0); u = tt / dur; return (lo * (1 - u) + hi * u) * u ** 2 * 0.9
def pad(dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * tt + p) for f, a, p in [(220, 1, 0), (277.2, 0.7, 1), (329.6, 0.6, 2), (440, 0.35, 0.5), (554.4, 0.2, 1.4)])
    return y * (0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * tt)) * np.minimum(1, tt / 0.4) * np.minimum(1, (dur - tt) / 0.3) * 0.12

def main(out):
    t = np.arange(N) / SR; bus = new_buses(N)
    # lids: the room goes muffled while they are shut
    lid = np.zeros(N)
    def lid_one(b):
        u = t - b; return np.where((u >= 0) & (u <= 0.22), np.where(u < 0.06, u / 0.06, np.where(u < 0.13, 1, 1 - (u - 0.13) / 0.09)), 0)
    for b in BLINKS: lid = np.maximum(lid, lid_one(b))
    lid = np.maximum(lid, np.clip(1 - (t - 0.03) / 0.11, 0, 1) * (t < 0.14)); lid = np.maximum(lid, np.clip((t - 18.8) / 0.08, 0, 1))
    room_on = ((t < 12.0) | (t >= 16.0)).astype(float); room_on = lp(room_on, 6)
    held = curve(N, [(0, 1), (10.74, 1), (10.8, 0.05), (10.9, 0.05), (10.93, 1), (D, 1)])
    duck = held * (1 - 0.75 * lid)
    room_g = (0.11 * room_on + 0.02) * (1 - 0.6 * lid)
    drone_g = curve(N, [(0, 0.08), (6, 0.12), (10.7, 0.32), (10.8, 0.0), (10.9, 0.0), (11.4, 0.22), (12, 0.12), (13.8, 0.2), (16, 0.08), (D, 0.08)])
    bed(bus, room_g, drone_g, duck)
    # clock: one soft tick a second in the flat
    for k in range(19):
        if (k < 12 or k >= 16): place(bus['fol'], tick(k, 0.35), k + 0.5, 0.6, 0.35)
    # every blink: a low thup (quieter in the rapid run, none inside the held breath)
    for i, b in enumerate(BLINKS):
        g = 0.55 if 10.0 < b < 11.1 else 0.8
        place(bus['fol'], thup(i, g), b + 0.02, 1.0, 0.0)
    place(bus['fol'], thup(99, 0.8), 18.82, 1.0, 0.0)
    # reading: a page turn; montage cuts and time-of-day foley
    place(bus['fol'], page(0.45, 0.5), 4.0, 1.0, -0.2)
    for s in SHOTS[1:6]: place(bus['air'], whoosh(0.35, 400, 2600, 0.35), s - 0.18, 1.0, 0.0)
    for k in range(5): place(bus['air'], chirp(30 + k), 6.15 + k * 0.17, 0.35, 0.4)                     # 7 AM: birds at the window
    for k in range(10): place(bus['fol'], key_click(50 + k), 7.1 + k * 0.085, 0.35, 0.25)                 # 1 PM: keyboard
    for k in range(3): place(bus['fol'], key_click(70 + k) * 0.6, 8.2 + k * 0.22, 0.3, 0.3)               # 6 PM: phone taps
    place(bus['fol'], page(0.4, 0.45), 9.2, 1.0, -0.2)                                                     # 11 PM: a page
    # rehook: held breath, then the only big hit
    place(bus['hit'], sub_boom(3.0), 10.9, 1.0, 0.0)
    place(bus['hit'], thud(611, 48, 0.3, 1.0), 10.9, 0.9, 0.0)
    # eye: whoosh in, a wet blink, riser into the pupil, whoomp into the brain
    place(bus['air'], whoosh(0.5, 300, 1800, 0.45), 11.8, 1.0, 0.0)
    n = int(0.25 * SR); wet = bp(noise(n), 900, 1.6) * np.exp(-np.arange(n) / SR / 0.05) * 0.5; place(bus['fol'], wet, 12.86, 1.0, 0.0); place(bus['fol'], thup(120, 0.7), 12.9, 1.0, 0.0)
    place(bus['air'], riser(0.65), 13.15, 0.8, 0.0)
    place(bus['hit'], thud(130, 60, 0.25, 0.8), 13.8, 1.0, 0.0)
    # brain: a shimmering pad and synaptic crackle, both cut on each blink (14.55, 15.45)
    p = pad(2.2); place(bus['air'], p, 13.8, 1.0, 0.0)
    for k in range(160):
        tk = 13.85 + R.random() * 2.1; place(bus['air'], bp(noise(int(0.01 * SR)), 3000 + 3000 * R.random(), 2.0) * 0.25, tk, 1.0, R.random() * 2 - 1)
    cut = np.ones(N)
    for b in (14.55, 15.45): cut *= 1 - 0.9 * np.clip(1 - np.abs(t - (b + 0.12)) / 0.2, 0, 1)
    bus['air'] *= np.where((t > 13.8) & (t < 16.0), cut, 1)[None]
    for b in (14.55, 15.45): place(bus['fol'], thup(140 + int(b), 0.7), b, 1.0, 0.0)
    # mirror: a breath as he leans in
    place(bus['fol'], breath(0.8, 'in', 3, 0.35), 16.3, 1.0, -0.2)
    mix = finish(bus, duck)
    write_wav(mix, out); print('wrote', out)

if __name__ == '__main__': main(sys.argv[1])
