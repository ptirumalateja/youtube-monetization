# Procedural sound for "The Deepest Hole" (earth, iron and heat; no samples, so no licence credits).
# Shovel impacts from timeline.json, the water break-through, then one identity per hole as the camera pulls back
# (pick clinks echoing in a brick shaft for the hand-dug well, cage cable and drills for the mine, a rising grinding drill
# and heat hiss for Kola), held-breath silence, one big reveal boom with a warm molten pad for the planet, the plunge
# home and a rising tone into frame 0. usage: python3 mix.py out.wav
import json, sys, wave, numpy as np
SR = 48000; TL = json.load(open('timeline.json')); T = TL['T']; N = int(SR * T); EV = TL['events']; ST = TL['strokes']; HO = TL['holes']
rng = np.random.default_rng(23)
def db(g): return 10 ** (g / 20)
def tt(d): return np.arange(int(d * SR)) / SR
def keys(k, t): k = np.array(k, float); return np.interp(t, k[:, 0], k[:, 1])
def lp(x, fc, order=2): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * order)), n=len(x))
def hp(x, fc, order=2): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); r = (f / fc + 1e-9) ** (2 * order); return np.fft.irfft(X * np.sqrt(r / (1 + r)), n=len(x))
def bp(x, lo, hi): return hp(lp(x, hi), lo)
def noise(d): return rng.standard_normal(int(d * SR))
buses = {k: np.zeros(N) for k in ['hit', 'fx', 'bed', 'tone', 'air']}
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
def crack(d=0.25): return lp(hp(noise(d), 2000), 9000) * np.exp(-tt(d) * 28) * (1 - np.exp(-tt(d) * 400))
def shovel(big=0.0):
    d = 0.5; t = tt(d)
    return (lp(bp(noise(d), 1400, 6000), 9000) * np.exp(-t * 55) * (1 - np.exp(-t * 500)) * 0.7 + body(150 + 80 * big, 62, d, 18 - 6 * big) * (0.8 + 0.6 * big)
            + ring([(1870, 1.0), (2740, 0.6), (3960, 0.35)], d, 26) * 0.18 + bp(noise(d), 300, 1500) * np.exp(-t * 30) * 0.4)
def toss(d=0.22):
    t = tt(d); return bp(noise(d), 600, 3500) * np.sin(np.pi * t / d) ** 2 * 0.35
def hit(at, big, g, low=55):
    d = 3.4 if big else 1.4; x = np.zeros(int(d * SR)); c = crack(); x[:len(c)] += c * 0.55
    b = body(240 if big else 200, low, 1.6 if big else 0.8, 7 if big else 16); x[:len(b)] += b
    if big: x += ring([(98, 1.0), (147, 0.6), (196, 0.45), (294, 0.25), (392, 0.15)], d, 0.9)[:len(x)] * 0.3
    place('hit', reverb(x, 2.8 if big else 1.2, 0.32)[:int(d * SR * 1.6)], at, g)
def sweep(d, f0, f1, g=1.0):
    t = tt(d); n0 = noise(d); out = np.zeros(len(t)); fc = np.geomspace(f0, f1, 6)
    for i in range(6):
        s = slice(int(i / 6 * len(t)), int((i + 1) / 6 * len(t))); out[s] = bp(n0, fc[i] * 0.6, fc[i] * 1.7)[s]
    return lp(out, 9000) * np.sin(np.pi * t / d) ** 1.5 * g

# ---- the well: frame-0 hit, strokes, the dive, the water break-through
hit(0.0, False, -3); place('fx', shovel(1.0), 0.0, -4)
for i, (ts, dv) in enumerate(ST):
    if i == 0: continue
    nxt = ST[i + 1][0] if i + 1 < len(ST) else ts + 0.7; mont = ts > 1.9
    place('fx', shovel(0.0 if mont else 0.4), ts, -11 if mont else -7)
    if i < len(ST) - 1: place('fx', toss(), ts + 0.45 * (nxt - ts) - 0.08, -14 if mont else -10)
place('fx', sweep(0.8, 3000, 300, 0.6), EV['dive'][0] - 0.1, -6)
hit(EV['dive'][0] + 0.55, False, -9, low=70)                      # the snap into the cross-section
w = EV['water_hit']; bb = np.zeros(int(1.4 * SR))
for i in range(22):
    a = int(rng.uniform(0.0, 1.1) * SR); f0 = rng.uniform(260, 820); dd = 0.07; tb = tt(dd)
    c = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.5 * tb / dd)) / SR) * np.sin(np.pi * tb / dd); bb[a:a + len(c)] += c[:len(bb) - a] * rng.uniform(0.1, 0.3)
place('tone', bb, w + 0.03, -7)
place('tone', reverb(ring([(659, 0.6), (988, 0.5), (1319, 0.35)], 2.4, 1.2), 2.0, 0.5) * 0.5, w + 0.05, -9)

# ---- earth drone: darker with depth, cut for the held breath
t = tt(T); f = keys([[0, 98], [2.0, 96], [5.0, 82], [8.0, 73], [11.0, 65], [13.9, 58], [14.6, 49], [19.9, 49], [21.6, 98], [T, 98]], t); ph = 2 * np.pi * np.cumsum(f) / SR
x = sum(np.sin(k * ph + k) * a for k, a in [(1, 0.6), (2, 1.0), (3, 0.55), (4, 0.35), (5, 0.18)]) * (1 + 0.15 * np.sin(2 * np.pi * 0.18 * t))
place('bed', hp(x, 85) * keys([[0, 0.25], [2.0, 0.45], [5.0, 0.6], [13.9, 0.9], [14.6, 0.0], [19.9, 0.0], [21.0, 0.3], [T, 0.2]], t) * 0.3, 0, -5)
place('air', bp(noise(T), 250, 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.23 * t + 1)) * keys([[0, 1], [1.9, 1], [2.6, 0.1], [21.0, 0.0], [21.6, 1.0], [T, 1.0]], t) * 0.16, 0, -3)

# ---- pull-back whooshes between stops
for a, b in [(5.9, 8.0), (8.7, 10.9), (11.5, 13.9)]:
    place('fx', sweep(b - a + 0.3, 250, 2400, 0.5), a - 0.1, -9)

# ---- per-hole identities
def ping(f0): return reverb(ring([(f0, 0.6), (f0 * 1.5, 0.35), (f0 * 2.0, 0.2)], 1.6, 2.2), 1.6, 0.45) * 0.4
for c, f0 in zip(TL['chips'], [784, 880, 988, 1175, 1319]): place('tone', ping(f0), c['t'][0], -11)
# hand-dug well: pick clinks echoing down a brick shaft, getting fainter and faster
d0, d1 = HO['wood']['drill']; k = 0; tc = d0
while tc < d1:
    cl = ring([(2300, 1.0), (3410, 0.5)], 0.25, 30) * 0.4; cl[:int(0.02 * SR)] += hp(noise(0.02), 2500) * np.exp(-tt(0.02) * 200) * 0.4
    place('fx', reverb(cl, 1.2, 0.55, 2500), tc, -13 - 6 * (tc - d0) / (d1 - d0)); k += 1; tc += 0.24 * (1 - 0.5 * (tc - d0) / (d1 - d0))
# mine: cage cable whine and a low machine rumble, rhythmic drill bursts
d0, d1 = HO['mine']['drill']; dm = d1 - d0 + 0.4; tm = tt(dm)
whine = np.sin(2 * np.pi * np.cumsum(keys([[0, 520], [dm, 760]], tm) * (1 + 0.01 * np.sin(2 * np.pi * 5 * tm))) / SR) * np.sin(np.pi * tm / dm) * 0.25
rum = bp(noise(dm), 90, 400) * (0.6 + 0.4 * (np.sin(2 * np.pi * 9 * tm) > 0)) * np.sin(np.pi * tm / dm) * 0.5
place('fx', whine + rum, d0, -9)
# Kola: a drill that grinds deeper and higher, heat hiss growing at the tip
d0, d1 = HO['kola']['drill']; dk = d1 - d0 + 0.05; tk = tt(dk); fk = keys([[0, 70], [dk, 150]], tk); pk = 2 * np.pi * np.cumsum(fk) / SR
grind = sum(np.sin(m * pk) / m for m in range(1, 9)) * (1 + 0.3 * np.sin(2 * np.pi * 23 * tk)) * 0.35
hiss = hp(noise(dk), 3000) * (tk / dk) ** 2 * 0.25
place('fx', hp(grind, 90) * np.minimum(1, tk / 0.3) + hiss, d0, -8)

# ---- held breath, then the planet: suck, vacuum, the biggest hit, a warm molten pad
h = EV['reveal']; d = 0.35; place('hit', bp(noise(d), 300, 4000) * np.linspace(0, 1, int(d * SR)) ** 3 * 0.6, h - d - 0.05, -12)
hit(h, True, 0, low=45)
dp = EV['earth_hold'][1] - h + 0.4; tp = tt(dp); pad = np.zeros(len(tp))
for f0 in [98, 147, 196, 247, 294]:
    for det in (-0.6, 0.0, 0.6):
        pad += np.sin(2 * np.pi * (f0 + det) * tp + rng.uniform(0, 6.28))
pad = lp(pad, 1400) * np.minimum(1, tp / 1.2) * np.minimum(1, (dp - tp) / 0.6) * 0.08
place('tone', pad, h + 0.2, -3)
place('tone', reverb(ring([(587, 0.5), (880, 0.4), (1175, 0.3)], 3.0, 0.8), 2.5, 0.5) * 0.4, 15.3, -10)     # caption lands

# ---- plunge home and the loop
p0, p1 = EV['plunge']; place('fx', sweep(p1 - p0 + 0.2, 400, 5000, 0.6), p0, -2)
d = p1 - p0; tr = tt(d); place('fx', np.sin(2 * np.pi * np.cumsum(keys([[0, 400], [d, 90]], tr)) / SR) * (tr / d) ** 1.5 * 0.25, p0, -9)
d = 0.6; tr = tt(d); place('air', np.sin(2 * np.pi * np.cumsum(keys([[0, 196], [d, 392]], tr)) / SR) * (tr / d) ** 2.5 * 0.35, T - d, -5)

# ---- master: duck under hits, held-breath silence, look-ahead limiter
mix = buses['bed'] + buses['fx'] + buses['tone'] + buses['air']
duck = np.ones(N)
for ev, dd in [(0.0, 0.6), (EV['dive'][0] + 0.55, 0.6), (h, 1.8)]:
    a = int(ev * SR); n = int(dd * SR); env = 1 - 0.6 * np.exp(-tt(dd) * 3.0); duck[a:a + n] = np.minimum(duck[a:a + n], env[:max(0, min(n, N - a))])
mix = mix * duck
s0, s1 = int(EV['held'][0] * SR), int((EV['held'][0] + 0.08) * SR); mix[s0:s1] *= np.linspace(1, 0.02, s1 - s0); mix[s1:int(h * SR)] *= 0.02
mix = mix + buses['hit']; mix[int((h - 0.05) * SR):int(h * SR)] = 0
mix = lp(hp(mix, 30), 14000)
mix = np.tanh(mix * 1.2); mix = mix / np.abs(mix).max() * db(-1.5)
need = np.minimum(1.0, db(-4.0) / (np.abs(mix) + 1e-9)); la = int(0.003 * SR); need = np.minimum.reduce([np.roll(need, -k) for k in range(la)])
g = np.empty(N); cur = 1.0; rel = np.exp(-1 / (0.08 * SR))
for i in range(N): cur = need[i] if need[i] < cur else need[i] + (cur - need[i]) * rel; g[i] = cur
mix *= g
fade = np.ones(N); fade[:int(0.002 * SR)] = np.linspace(0, 1, int(0.002 * SR)); fade[-int(0.01 * SR):] = np.linspace(1, 0, int(0.01 * SR)); mix *= fade
st = np.stack([mix, mix], 1); st[:, 1] = np.roll(st[:, 1], 14); pcm = (np.clip(st, -1, 1) * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
