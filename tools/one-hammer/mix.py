"""He Moved a Mountain: sound mix (numpy buses). No music: the user adds a track with its drop on the break (16.60 s).

python3 mix.py timing.json out.wav
Sound family "iron and stone" (new for this reel, all synthesised here): a hammer-on-chisel ping with a rock
thunk on every strike, which blurs into a metallic whir while the years fly by; a canyon-sized first strike;
a low drone and wind under the work; a camera rush and crickets at dusk; a held breath with a creaking crack;
the break (rock burst, debris rattle, sub); dawn birds and a warm chord under the reveal; a struck-stone
(lithophone) note under the end line; a reversed whir for the rewind, and a rising tone into frame 0.
"""
import json, sys, wave
import numpy as np
from scipy.signal import lfilter

SR = 48000
timing = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
DUR = timing['dur']
DROP = timing['drop']
NS = int(DUR * SR)
rng = np.random.default_rng(11)
t = np.arange(NS) / SR
strikes = np.array(timing['strikes'])


def place(bus, x, at, g=1.0):
    i = int(round(at * SR))
    if i >= NS or i + len(x) <= 0:
        return
    a, b = max(0, i), min(NS, i + len(x))
    bus[a:b] += g * x[a - i:b - i]


def lpf(x, fc):
    """one-pole low-pass"""
    a = np.exp(-2 * np.pi * fc / SR)
    return lfilter([1 - a], [1, -a], x)


def hp(x, fc):
    return x - lpf(x, fc)


def sstep(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1)
    return u * u * (3 - 2 * u)


def env(n, attack, decay):
    k = np.arange(n) / SR
    return np.minimum(1, k / max(attack, 1e-4)) * np.exp(-k / decay)


def reverb(x, sec=2.4, wet=0.3, bright=4500):
    n = int(sec * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir = lpf(ir, bright)
    ir /= np.sqrt((ir ** 2).sum())
    L = len(x) + n
    y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L))[:len(x)]
    return x + wet * y


# ---------- sources ----------
def ping(scale=1.0, length=0.32):
    """hammer on a chisel: inharmonic metal partials + a click"""
    n = int(length * SR); k = np.arange(n) / SR
    parts = [(1870, 1.0, 0.11), (2953, 0.6, 0.07), (4410, 0.4, 0.05), (6320, 0.25, 0.03), (1188, 0.35, 0.16)]
    y = sum(a * np.sin(2 * np.pi * f * scale * k + rng.random() * 6) * np.exp(-k / d) for f, a, d in parts)
    click = rng.standard_normal(n) * np.exp(-k / 0.0025)
    y = y + 0.6 * hp(click, 3000)
    return y / np.abs(y).max()


def thunk(length=0.22, f0=190):
    """the chisel biting rock: a short pitch-dropping body + gritty noise"""
    n = int(length * SR); k = np.arange(n) / SR
    body = np.sin(2 * np.pi * np.cumsum(f0 * (1 - 0.45 * np.minimum(1, k / 0.06))) / SR) * np.exp(-k / 0.045)
    grit = hp(lpf(rng.standard_normal(n), 3200), 700) * np.exp(-k / 0.05)
    y = body + 0.7 * grit
    return y / np.abs(y).max()


def boom(length=1.6, f0=120, f1=55, dec=0.45):
    n = int(length * SR); k = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-k / 0.12)
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.003, dec)
    return y


pings = [ping(s) for s in (0.97, 1.0, 1.03, 1.06)]
thunks = [thunk(f0=f) for f in (175, 190, 205)]

# ---------- buses ----------
metal = np.zeros(NS); rock = np.zeros(NS); bed = np.zeros(NS); wind = np.zeros(NS)
hit = np.zeros(NS); air = np.zeros(NS); nat = np.zeros(NS)

# every strike has a sound; fast strikes blur into a whir that climbs a little as the years pass
gaps = np.diff(np.concatenate([[-1.0], strikes]))
for i, (st, gap) in enumerate(zip(strikes, gaps)):
    if i == len(strikes) - 1:
        continue  # the last strike belongs to the break
    slow = float(np.clip((gap - 0.05) / 0.3, 0, 1))
    p = pings[i % 4]
    if slow < 0.5:  # whir: short, pitched-up pings
        r = 1.0 + 0.5 * (i / len(strikes))
        p = np.interp(np.arange(0, int(0.05 * SR) * r, r), np.arange(len(p)), p)
        p *= np.exp(-np.arange(len(p)) / SR / 0.015)
    g = 0.9 * slow + 0.5 * (1 - slow)
    place(metal, p, st, g)
    if slow > 0.05:
        place(rock, thunks[i % 3], st + 0.002, 0.8 * slow)
# the 3 slow night strikes ring out longer in the dark
for st in strikes[(strikes > 14.9) & (strikes < DROP - 0.01)]:
    place(metal, reverb(np.concatenate([pings[1], np.zeros(SR)]), 2.4, 0.6)[: int(1.3 * SR)], st, 0.45)
# hook: a canyon-sized first strike on frame 2
T1 = strikes[0]
place(hit, boom(1.8, 130, 52, 0.5), T1, 0.85)
place(hit, thunks[1], T1, 0.9)
place(hit, pings[1], T1, 0.9)
metal = hp(metal, 400)
rock = hp(rock, 90)

# bed: a low A drone kept inside the phone band, opening up through the work; a soft shepard riser for the years
f0 = 110.0
drone = sum(a * np.sin(2 * np.pi * f0 * m * t + ph) for m, a, ph in [(1, 1, 0), (1.5, 0.5, 1), (2, 0.45, 2), (3, 0.2, 0.5), (1.004, 0.6, 3)])
drone = lpf(drone, 900)
bed += drone * (0.02 + 0.05 * sstep(3, 14, t)) * (1 - 0.9 * sstep(14.6, 15.4, t)) * (1 - sstep(23.5, 24.0, t))
sh = np.zeros(NS)
for i in range(3):
    ph_ = (((t - 3.8) / 3.6) + i / 3) % 1
    fr = 196 * 2 ** ph_
    sh += np.sin(np.pi * ph_) * np.sin(2 * np.pi * np.cumsum(fr) / SR)
bed += 0.035 * sh * sstep(3.8, 6.0, t) * (1 - sstep(13.8, 14.5, t))

# wind through the cut, with gusts; quieter at night
n = rng.standard_normal(NS)
gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.31 * t + 1) * np.sin(2 * np.pi * 0.11 * t)
wind += hp(lpf(n, 650), 160) * gust * (0.35 + 0.35 * sstep(3, 12, t)) * (1 - 0.7 * sstep(15.0, 15.6, t) * (1 - sstep(DROP, DROP + 0.5, t)))

# the rush in at dusk (14.3-15.4)
rush = hp(lpf(rng.standard_normal(NS), 2500), 300) * sstep(14.2, 14.9, t) * (1 - sstep(14.95, 15.5, t))
air += 0.25 * rush
# crickets at night (15.2-16.0), gone for the held breath
cr = np.zeros(NS)
for c0 in np.arange(15.15, 16.0, 0.27):
    for k in range(3):
        n_ = int(0.018 * SR); kk = np.arange(n_) / SR
        place(cr, np.sin(2 * np.pi * 4400 * kk) * np.sin(np.pi * kk / 0.018), c0 + k * 0.035 + rng.random() * 0.02, 0.5)
nat += cr * 0.08 * (1 - sstep(15.85, 15.98, t))

# held breath 16.0-16.6: near silence, a creaking crack that grows with the light in the wall, 50 ms vacuum
crk = np.zeros(NS)
for k in range(140):
    at = 16.0 + 0.6 * (k / 140) ** 0.6 + rng.random() * 0.01
    n_ = int(0.004 * SR)
    place(crk, rng.standard_normal(n_) * np.exp(-np.arange(n_) / SR / 0.001), at, 0.15 + 0.6 * (k / 140))
crk = hp(crk, 1500) * (t < DROP - 0.05)
air += 0.25 * crk
hold = 1 - 0.96 * sstep(15.95, 16.05, t) * (1 - sstep(DROP - 0.001, DROP, t))

# the break at DROP: rock burst, crumble, debris rattle, sub; the beat drop for the music
place(hit, boom(2.4, 160, 46, 0.7), DROP, 1.0)
place(hit, thunks[0], DROP, 1.0)
place(hit, pings[2], DROP - 0.004, 0.7)
nb = int(2.2 * SR); kb = np.arange(nb) / SR
burst = lpf(rng.standard_normal(nb), 1800) * env(nb, 0.002, 0.35)
place(hit, hp(burst, 120), DROP, 1.4)
deb = np.zeros(NS)
for k in range(260):
    at = DROP + 0.05 + rng.exponential(0.55)
    n_ = int(0.012 * SR)
    place(deb, rng.standard_normal(n_) * np.exp(-np.arange(n_) / SR / 0.003), at, (0.2 + rng.random() * 0.5) * np.exp(-(at - DROP) / 1.3))
place(hit, hp(lpf(deb, 5000), 250), 0, 0.9)
hit = reverb(hit, 2.8, 0.35)

# dawn: birds and a warm chord under the reveal (kept low; the music sits on top)
for k in range(16):
    at = DROP + 0.9 + rng.random() * 5.5
    n_ = int(0.11 * SR); kk = np.arange(n_) / SR
    fch = 3200 + 1300 * np.sin(2 * np.pi * (9 + rng.random() * 5) * kk) + 900 * (1 - kk / 0.11)
    place(nat, np.sin(2 * np.pi * np.cumsum(fch) / SR) * np.sin(np.pi * kk / 0.11) ** 2, at, 0.12 + 0.1 * rng.random())
cl = int(6.5 * SR); tc = np.arange(cl) / SR
chord = sum(a * np.sin(2 * np.pi * f * tc + i) for i, (f, a) in enumerate([(110, 1), (164.8, 0.7), (220, 0.6), (277.2, 0.45), (329.6, 0.35), (493.9, 0.2)]))
chord *= sstep(0, 1.6, tc) * (1 - sstep(4.0, 6.5, tc))
place(bed, lpf(chord, 1500) / 5, DROP + 0.8, 0.13)
# the routes draw in: a soft rising shimmer
shim = np.sin(2 * np.pi * np.cumsum(660 * 2 ** (sstep(19.9, 21.4, t))) / SR) * sstep(19.9, 20.3, t) * (1 - sstep(21.2, 21.6, t))
air += 0.03 * shim
# end line: a struck-stone note (lithophone partials)
ln = int(3.0 * SR); tl = np.arange(ln) / SR
litho = sum(a * np.sin(2 * np.pi * 392 * r * tl) * np.exp(-tl / d) for r, a, d in [(1, 1, 0.9), (2.76, 0.5, 0.45), (5.40, 0.25, 0.25), (8.93, 0.12, 0.12)])
place(air, reverb(litho * 0.35, 2.0, 0.5), 21.75, 0.5)

# rewind (23.6-25): the whir played backwards and pitched up, a reverse whoosh, a rising tone into frame 0
seg = metal[int(5.0 * SR):int(13.5 * SR)][::-1]
L = int((DUR - 23.6) * SR)
rw = np.interp(np.linspace(0, len(seg) - 1, L), np.arange(len(seg)), seg)
place(air, rw * sstep(0, 0.3, np.arange(L) / SR / 1.4) * 0.6, 23.6, 1.0)
wh = hp(lpf(rng.standard_normal(NS), 3000), 300) * sstep(23.5, 24.7, t) ** 2 * (1 - sstep(24.85, 24.99, t))
air += 0.18 * wh
rise = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (sstep(24.3, 25.0, t))) / SR) * sstep(24.35, 25.0, t) ** 2
air += 0.07 * rise

# ---------- master ----------
duckD = 1 - 0.6 * np.exp(-np.clip(t - DROP, 0, None) / 0.7) * (t >= DROP)
duck1 = 1 - 0.5 * np.exp(-np.clip(t - T1, 0, None) / 0.4)
mix = (metal * 0.42 + rock * 0.5) * hold + (bed + wind * 0.3) * hold * duckD * duck1 + nat + air + hit * 0.9
mix = hp(mix, 35)
st = np.stack([mix, mix], 1)
w2 = lpf(wind, 2500) * 0.06 * hold
st[:, 0] += w2; st[:, 1] -= w2
st /= np.abs(st).max()
st = np.tanh(st * 1.5) / np.tanh(1.5)
st *= 0.89
e = int(0.002 * SR); st[:e] *= np.linspace(0, 1, e)[:, None]; st[-e:] *= np.linspace(1, 0, e)[:, None]
w = wave.open(OUT, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print('wrote', OUT, DUR)
