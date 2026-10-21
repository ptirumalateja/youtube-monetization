# Procedural sound for "One More Shovel" (earth and water family; no samples, so no licence credits).
# Shovel impacts on every stroke (taken from timeline.json, the same times the scene uses), dirt tosses, a descending earth
# drone, glassy water plinks that grow as the camera nears the water, tired breaths, the shovel clatter, held-breath silence,
# one underwater reveal boom, rope creaks, the seep, a whoosh up the shaft, wind and footsteps, a loop-link rise.
# usage: python3 mix.py out.wav
import json, sys, wave, numpy as np
SR = 48000; TL = json.load(open('timeline.json')); T = TL['T']; N = int(SR * T); EV = TL['events']; ST = TL['strokes']
rng = np.random.default_rng(16)
def db(g): return 10 ** (g / 20)
def tt(d): return np.arange(int(d * SR)) / SR
def keys(k, t): k = np.array(k, float); return np.interp(t, k[:, 0], k[:, 1])
def lp(x, fc, order=2): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * order)), n=len(x))
def hp(x, fc, order=2): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); r = (f / fc + 1e-9) ** (2 * order); return np.fft.irfft(X * np.sqrt(r / (1 + r)), n=len(x))
def bp(x, lo, hi): return hp(lp(x, hi), lo)
def noise(d): return rng.standard_normal(int(d * SR))
buses = {k: np.zeros(N) for k in ['hit', 'fx', 'bed', 'water', 'air']}
def place(bus, x, at, g=0.0):
    a = int(at * SR)
    if a < 0: x = x[-a:]; a = 0
    x = x[:max(0, N - a)]; buses[bus][a:a + len(x)] += x * db(g)
def reverb(x, rt=1.6, mix=0.3, tone=3500):
    n = int(rt * SR); ir = noise(rt) * np.exp(-tt(rt) * 6.9 / rt); ir = lp(ir, tone); ir[:int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
    L = len(x) + n; y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L); y *= np.abs(x).max() / (np.abs(y).max() + 1e-9)
    out = np.zeros(L); out[:len(x)] = x * (1 - mix); return out + y * mix

def body(a, b, d, k=22):
    t = tt(d); f = b + (a - b) * np.exp(-t * 14); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * k); return x + 0.35 * np.tanh(2.5 * x)
def ring(fs, d, k):
    t = tt(d); return sum(a * np.sin(2 * np.pi * f * t + i) * np.exp(-t * k * (1 + 0.4 * i)) for i, (f, a) in enumerate(fs))
def shovel(big=0.0, tired=0.0):
    """blade into earth: scrape + soil thud + a short metal ring"""
    d = 0.5; t = tt(d)
    scr = bp(noise(d), 1400, 6000) * np.exp(-t * (55 - 20 * tired)) * 0.7
    thud = body(150 + 80 * big, 62, d, 18 - 6 * big) * (0.8 + 0.6 * big)
    met = ring([(1870, 1.0), (2740, 0.6), (3960, 0.35)], d, 26) * 0.18
    grit = bp(noise(d), 300, 1500) * np.exp(-t * 30) * 0.4
    return scr + thud + met + grit
def toss(d=0.22):
    t = tt(d); sw = bp(noise(d), 600, 3500) * np.sin(np.pi * t / d) ** 2 * 0.35
    pk = np.zeros(int(0.5 * SR))
    for i in range(9):
        a = int(rng.uniform(0.12, 0.45) * SR); c = hp(noise(0.012), 2500) * np.exp(-tt(0.012) * 300) * rng.uniform(0.1, 0.3); pk[a:a + len(c)] += c[:len(pk) - a]
    out = np.zeros(int(0.5 * SR)); out[:len(sw)] += sw; return out + pk

# ---- strokes: impact + toss; the counter tick rides on the impact
for i, (ts, dv) in enumerate(ST):
    nxt = ST[i + 1][0] if i + 1 < len(ST) else ts + 0.8
    tired = float(np.clip((ts - 6.2) / 2.2, 0, 1)); mont = 2.1 < ts < 6.2
    if i == 0: continue                                 # frame 0 is the big hit below
    g = -11 if mont else -8
    place('fx', shovel(0.0 if mont else 0.4, tired), ts, g + 2 * tired)
    place('fx', toss(), ts + 0.45 * (nxt - ts) - 0.08, (-14 if mont else -10) - 6 * tired)
    tick = np.sin(2 * np.pi * 3200 * tt(0.03)) * np.exp(-tt(0.03) * 160); place('fx', tick, ts + 0.005, -20)

# ---- frame-0 hit: the first shovel, big (also the loop landing)
def hit(at, big, g, low=55):
    d = 3.0 if big else 1.4; x = np.zeros(int(d * SR))
    c = lp(hp(noise(0.25), 2000), 9000) * np.exp(-tt(0.25) * 28) * (1 - np.exp(-tt(0.25) * 400)); x[:len(c)] += c * 0.55
    b = body(240 if big else 200, low, 1.4 if big else 0.8, 9 if big else 16); x[:len(b)] += b
    if big: x += ring([(130, 1.0), (196, 0.5), (301, 0.35), (392, 0.2)], d, 1.4)[:len(x)] * 0.25
    place('hit', reverb(x, 2.6 if big else 1.2, 0.3)[:int(d * SR * 1.6)], at, g)
hit(0.0, False, -3); place('fx', shovel(1.0), 0.0, -4)

# ---- earth drone: descends and darkens with depth (energy kept in 90-400 Hz for phones)
t = tt(T); f = keys([[0, 98], [1.2, 96], [6.2, 74], [9.4, 70], [9.8, 62], [11.9, 66], [12.8, 98], [T, 98]], t); ph = 2 * np.pi * np.cumsum(f) / SR
x = sum(np.sin(k * ph + k) * a for k, a in [(1, 0.6), (2, 1.0), (3, 0.55), (4, 0.35), (5, 0.18)]) * (1 + 0.15 * np.sin(2 * np.pi * 0.18 * t))
env = keys([[0, 0.25], [1.2, 0.35], [2.1, 0.6], [6.2, 0.8], [8.4, 1.0], [9.46, 1.0], [9.5, 0], [9.8, 0], [9.9, 0.7], [11.9, 0.6], [12.8, 0.15], [T, 0.15]], t)
place('bed', hp(x, 85) * env * 0.3, 0, -4)
# wind at the surface
wd = bp(noise(T), 250, 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t + 1)) * keys([[0, 1], [1.2, 1], [2.0, 0.1], [11.9, 0.0], [12.8, 1.0], [T, 1.0]], t)
place('air', wd * 0.16, 0, -3)

# ---- water: glassy plinks, density grows as the camera nears the water table; a low bubbling under it
def plink(f0):
    d = 0.35; t = tt(d); f = f0 * (1 + 0.9 * np.exp(-t * 45)); return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * (1 - np.exp(-t * 900))
pt = 5.4
while pt < T:
    dens = keys([[5.4, 1.2], [8.0, 4.5], [9.4, 6.0], [9.46, 0], [9.8, 0], [9.9, 7], [11.8, 5], [12.0, 0.5], [T, 0.3]], pt)
    if dens > 0.4 and not (9.46 <= pt < 9.8):
        place('water', plink(rng.choice([988, 1175, 1319, 1480, 1760, 1976]) * rng.uniform(0.98, 1.02)), pt, -18 + rng.uniform(-4, 0) + 3 * min(1, (pt - 5.4) / 3))
    pt += rng.exponential(1 / max(dens, 0.3))
bub = bp(noise(T), 120, 700) * (0.5 + 0.5 * np.sin(2 * np.pi * 7 * t) * np.sin(2 * np.pi * 0.7 * t)) * keys([[0, 0], [6.0, 0], [8.4, 0.5], [9.46, 0.6], [9.5, 0], [9.8, 0], [9.85, 1.0], [11.8, 0.6], [12.4, 0], [T, 0]], t)
place('water', bub * 0.22, 0, -6)

# ---- tired breaths between the slow strokes, then the long exhale when he stops
def breath(d, g, f=(500, 2600)):
    t = tt(d); return bp(noise(d), *f) * np.sin(np.pi * t / d) ** 1.5 * g
for at, d, g in [(6.85, 0.35, 0.5), (7.45, 0.4, 0.6), (8.05, 0.45, 0.7), (8.65, 0.75, 0.9), (9.05, 0.35, 0.5)]: place('fx', breath(d, g), at, -11)

# ---- the shovel falls and clatters against the wall (9.46), then held breath
d = 1.0; tc = tt(d); clang = ring([(523, 1.0), (1377, 0.7), (2213, 0.5), (3311, 0.3)], d, 9) * 0.5 + hp(noise(d), 1500) * np.exp(-tc * 50) * 0.5
place('fx', reverb(clang, 1.4, 0.35)[:int(0.14 * SR)] * np.linspace(1, 0, int(0.14 * SR)), EV['drop'][1], -6)       # cut short: the silence takes over
place('fx', clang[:int(0.06 * SR)] * 0.4, EV['drop'][1] + 0.09, -14)

# ---- reveal: reverse suck, 50 ms vacuum, the underwater boom, a teal glass chord
h = EV['hit_reveal']; d = 0.32; sk = bp(noise(d), 300, 4000) * np.linspace(0, 1, int(d * SR)) ** 3; place('hit', sk * 0.6, h - d - 0.05, -12)
hit(h, True, 0, low=48)
bb = np.zeros(int(1.2 * SR))
for i in range(14):
    a = int(rng.uniform(0.02, 0.9) * SR); f0 = rng.uniform(260, 700); dd = 0.08; tb = tt(dd)
    c = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.5 * tb / dd)) / SR) * np.sin(np.pi * tb / dd); bb[a:a + len(c)] += c[:len(bb) - a] * rng.uniform(0.1, 0.3)
place('water', bb, h + 0.05, -8)
gl = ring([(659, 0.6), (988, 0.5), (1319, 0.35), (1976, 0.2)], 3.2, 0.9); place('water', reverb(gl, 2.8, 0.55) * 0.5, h + 0.12, -9)

# ---- rope creaks as he climbs, the seep, the whoosh up the shaft
for k in range(7):
    at = h + 0.15 + k * 0.31 / (1 + 0.15 * k); d = 0.16; tq = tt(d)
    cr = bp(noise(d), 600, 1400) * (0.5 + 0.5 * np.sin(2 * np.pi * 38 * tq)) * np.sin(np.pi * tq / d) ** 2
    place('fx', cr * 0.5, at, -12 - 1.5 * k)
tr = bp(noise(1.4), 1800, 6000) * np.sin(np.pi * tt(1.4) / 1.4) ** 2 * 0.25; place('water', tr, EV['seep'][0], -12)
w0, w1 = EV['whoosh']; d = w1 - w0 + 0.25; tw = tt(d); sweep = np.zeros(len(tw))
fc = keys([[0, 300], [d, 4000]], tw); n0 = noise(d)
for a, b in [(0, 0.33), (0.33, 0.66), (0.66, 1.0)]:
    seg = slice(int(a * len(tw)), int(b * len(tw))); sweep[seg] = bp(n0, float(fc[seg].mean()) * 0.5, float(fc[seg].mean()) * 1.6)[seg]
sweep *= np.sin(np.pi * np.clip(tw / d, 0, 1)) ** 1.5; up = np.sin(2 * np.pi * np.cumsum(keys([[0, 90], [d, 360]], tw)) / SR) * (tw / d) ** 2 * np.exp(-np.maximum(tw - d * 0.85, 0) * 30)
place('fx', sweep * 0.55 + up * 0.25, w0 - 0.1, -3)

# ---- surface: footsteps on dry ground, end-line bell, a rising tone into frame 0
for k in range(3):
    at = EV['out'] + 0.4 + k * 0.806
    if at < T - 0.15: tf = tt(0.2); place('fx', body(120, 70, 0.2, 30) * 0.6 + hp(noise(0.2), 1500) * np.exp(-tf * 70) * 0.25, at, -8)
bell = ring([(784, 0.6), (1176, 0.35), (1568, 0.2)], 2.0, 1.6); place('air', reverb(bell, 2.0, 0.5) * 0.35, 12.8, -5)
d = 0.6; tr = tt(d); rise = np.sin(2 * np.pi * np.cumsum(keys([[0, 196], [d, 392]], tr)) / SR) * (tr / d) ** 2.5; place('air', rise * 0.35, T - d, -5)

# ---- master: side-chain duck under hits, held-breath silence, tanh, normalise
mix = buses['bed'] + buses['fx'] + buses['water'] + buses['air']
duck = np.ones(N)
for ev, dd in [(0.0, 0.6), (h, 1.6)]:
    a = int(ev * SR); n = int(dd * SR); env = 1 - 0.6 * np.exp(-tt(dd) * 3.0); duck[a:a + n] = np.minimum(duck[a:a + n], env[:max(0, min(n, N - a))])
mix = mix * duck
s0, s1 = int((EV['drop'][1] + 0.05) * SR), int((EV['drop'][1] + 0.14) * SR)      # held breath: everything but the suck drops out
mix[s0:s1] *= np.linspace(1, 0.02, s1 - s0); mix[s1:int(h * SR)] *= 0.02
mix = mix + buses['hit']; mix[int((h - 0.05) * SR):int(h * SR)] = 0                # 50 ms vacuum before the boom
mix = lp(hp(mix, 30), 14000)
mix = np.tanh(mix * 1.2) ; mix = mix / np.abs(mix).max() * db(-1.5)
# look-ahead peak limiter (3 ms look-ahead, 80 ms release) so AAC never overshoots, including the frame-0 transient
need = np.minimum(1.0, db(-4.0) / (np.abs(mix) + 1e-9)); la = int(0.003 * SR)
need = np.minimum.reduce([np.roll(need, -k) for k in range(la)])
g = np.empty(N); cur = 1.0; rel = np.exp(-1 / (0.08 * SR))
for i in range(N): cur = need[i] if need[i] < cur else need[i] + (cur - need[i]) * rel; g[i] = cur
mix *= g
fade = np.ones(N); fade[:int(0.002 * SR)] = np.linspace(0, 1, int(0.002 * SR)); fade[-int(0.01 * SR):] = np.linspace(1, 0, int(0.01 * SR)); mix *= fade
st = np.stack([mix, mix], 1); st[:, 1] = np.roll(st[:, 1], 14); pcm = (np.clip(st, -1, 1) * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
