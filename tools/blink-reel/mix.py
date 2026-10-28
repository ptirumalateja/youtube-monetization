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
D = 22.0; N = int(D * SR)
# V3 timeline (matches scene_dark.js): eye hook, lock-in, counter montage, 20:00, lifetime, eye push, brain, mirror, CTA
BLINKS = [3.3, 4.75, 5.9, 6.85, 7.8, 8.65, 9.05, 9.3, 9.5, 9.66, 9.8, 9.9, 12.4, 18.6, 19.75]
EYEBLINKS = [1.2, 13.45]; BRAINBLINKS = [15.5, 16.35]
SHOTS = [0.0, 2.4, 3.9, 5.4, 6.4, 7.4, 8.4, 9.3, 11.2, 13.0, 14.6, 17.0]
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
def heart(g=1.0):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    k = lambda t0, a: np.where(tt >= t0, np.sin(2 * np.pi * 52 * (tt - t0)) * np.exp(-(tt - t0) / 0.07) * a, 0)
    return lp(k(0, 1.0) + k(0.16, 0.7), 300) * g
def chime(g=1.0):
    n = int(1.6 * SR); tt = np.arange(n) / SR
    return sum(a * np.sin(2 * np.pi * f * tt) for f, a in [(880, 1), (1318.5, 0.5), (1760, 0.25)]) * np.exp(-tt / 0.5) * np.minimum(1, tt / 0.005) * 0.25 * g
def pad(dur):
    n = int(dur * SR); tt = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f * tt + p) for f, a, p in [(220, 1, 0), (277.2, 0.7, 1), (329.6, 0.6, 2), (440, 0.35, 0.5), (554.4, 0.2, 1.4)])
    return y * (0.7 + 0.3 * np.sin(2 * np.pi * 0.7 * tt)) * np.minimum(1, tt / 0.4) * np.minimum(1, (dur - tt) / 0.3) * 0.12

def main(out):
    t = np.arange(N) / SR; bus = new_buses(N)
    # lids: the room goes muffled while they are shut (screen blinks, the two real-lid blinks, the loop close)
    lid = np.zeros(N)
    def lid_one(b):
        u = t - b; return np.where((u >= 0) & (u <= 0.22), np.where(u < 0.06, u / 0.06, np.where(u < 0.13, 1, 1 - (u - 0.13) / 0.09)), 0)
    for b in BLINKS + EYEBLINKS: lid = np.maximum(lid, lid_one(b))
    lid = np.maximum(lid, np.clip(1 - (t - 0.03) / 0.11, 0, 1) * (t < 0.14)); lid = np.maximum(lid, np.clip((t - 21.82) / 0.08, 0, 1))
    room_on = (((t >= 2.4) & (t < 13.0)) | (t >= 17.0)).astype(float); room_on = lp(room_on, 6)
    held = curve(N, [(0, 1), (9.74, 1), (9.8, 0.05), (9.9, 0.05), (9.93, 1), (D, 1)])
    duck = held * (1 - 0.75 * lid)
    room_g = (0.11 * room_on + 0.05) * (1 - 0.6 * lid)
    drone_g = curve(N, [(0, 0.34), (2.4, 0.2), (5.4, 0.14), (9.7, 0.34), (9.8, 0.0), (9.9, 0.0), (10.4, 0.22), (11.2, 0.2), (13.0, 0.28), (14.6, 0.2), (17.0, 0.24), (20.5, 0.3), (D, 0.34)])
    bed(bus, room_g, drone_g, duck)
    # hook: a hit on frame 0 as the lid opens, the real blink at 1.2 is wet and loud
    place(bus['hit'], thud(3, 55, 0.35, 0.9), 0.02, 1.0, 0.0)
    place(bus['air'], whoosh(0.4, 300, 2200, 0.5), 0.0, 1.0, 0.0)
    n = int(0.25 * SR); wet = lambda: bp(noise(n), 900, 1.6) * np.exp(-np.arange(n) / SR / 0.05) * 0.6
    for e in EYEBLINKS: place(bus['fol'], wet(), e - 0.01, 1.0, 0.0); place(bus['fol'], thup(int(e * 10), 1.0), e + 0.04, 1.0, 0.0)
    for tb in (0.5, 1.55, 2.25): place(bus['hit'], heart(0.7), tb, 1.0, 0.0)                              # hook pulse
    tb = 17.2
    while tb < 21.6: place(bus['hit'], heart(0.5), tb, 1.0, 0.0); tb += 0.85                               # mirror pulse
    # clock in the flat; a heartbeat that speeds up under the counter
    for k in range(22):
        tk = k + 0.5
        if 2.4 <= tk < 5.4 or tk >= 17.0: place(bus['fol'], tick(k, 0.35), tk, 0.6, 0.35)
    tb = 5.45
    while tb < 9.7: place(bus['hit'], heart(0.55), tb, 1.0, 0.0); tb += 0.75 - 0.4 * (tb - 5.4) / 4.3
    # every screen blink: a low thup (quieter in the rapid run)
    for i, b in enumerate(BLINKS):
        place(bus['fol'], thup(i, 0.55 if 9.0 < b < 10.0 else 0.85), b + 0.02, 1.0, 0.0)
    for s0 in SHOTS[1:8]: place(bus['air'], whoosh(0.35, 400, 2600, 0.35), s0 - 0.18, 1.0, 0.0)
    place(bus['fol'], page(0.45, 0.5), 4.2, 1.0, -0.2)
    for k in range(5): place(bus['air'], chirp(30 + k), 5.5 + k * 0.17, 0.35, 0.4)                      # 7 AM birds
    for k in range(10): place(bus['fol'], key_click(50 + k), 6.5 + k * 0.085, 0.35, 0.25)                 # 1 PM keys
    for k in range(3): place(bus['fol'], key_click(70 + k) * 0.6, 7.55 + k * 0.22, 0.3, 0.3)              # 6 PM phone
    place(bus['fol'], page(0.4, 0.45), 8.55, 1.0, -0.2)                                                    # 11 PM page
    # rehook 1: held breath, then the hit on 20:00
    place(bus['hit'], sub_boom(2.5), 9.9, 0.9, 0.0); place(bus['hit'], thud(611, 48, 0.3, 1.0), 9.9, 0.9, 0.0)
    # lifetime: days flash past (ticks accelerate), then the biggest hit on "~1 YEAR"
    tk, k = 11.25, 0
    while tk < 12.95: place(bus['fol'], tick(200 + k, 0.4), tk, 0.6, 0.3 * np.sin(k)); tk += max(0.035, 0.22 * (1 - (tk - 11.25) / 1.4)); k += 1
    place(bus['air'], riser(1.0), 10.5, 0.6, 0.0); place(bus['hit'], sub_boom(3.0), 11.45, 1.0, 0.0); place(bus['hit'], thud(612, 40, 0.45, 1.2), 11.45, 1.0, 0.0)
    # eye: whoosh in, riser into the pupil, whoomp into the brain
    place(bus['air'], whoosh(0.5, 300, 1800, 0.45), 12.8, 1.0, 0.0)
    place(bus['air'], riser(0.65), 13.95, 0.8, 0.0); place(bus['hit'], thud(130, 60, 0.25, 0.8), 14.6, 1.0, 0.0)
    # brain: pad and crackle, both cut dead on each blink
    place(bus['air'], pad(2.4), 14.6, 1.0, 0.0)
    for k in range(180):
        tk = 14.65 + R.random() * 2.3; place(bus['air'], bp(noise(int(0.01 * SR)), 3000 + 3000 * R.random(), 2.0) * 0.25, tk, 1.0, R.random() * 2 - 1)
    cut = np.ones(N)
    for b in BRAINBLINKS: cut *= 1 - 0.95 * np.clip(1 - np.abs(t - (b + 0.12)) / 0.2, 0, 1)
    bus['air'] *= np.where((t > 14.6) & (t < 17.0), cut, 1)[None]
    for b in BRAINBLINKS: place(bus['fol'], thup(140 + int(b * 10), 0.8), b, 1.0, 0.0)
    # mirror: a breath as he leans in; the CTA chime; the loop closes on a hit
    place(bus['fol'], breath(0.8, 'in', 3, 0.35), 17.3, 1.0, -0.2)
    place(bus['air'], chime(0.8), 20.5, 1.0, 0.0)
    place(bus['fol'], thup(99, 1.0), 21.84, 1.0, 0.0); place(bus['hit'], thud(700, 50, 0.2, 0.9), 21.84, 1.0, 0.0)
    mix = finish(bus, duck)
    write_wav(mix, out); print('wrote', out)

if __name__ == '__main__': main(sys.argv[1])
