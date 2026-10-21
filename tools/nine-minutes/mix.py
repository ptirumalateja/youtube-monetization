# Nine Minutes sound: an all-synthesised "wet biology" family (no samples, no credits needed).
# Buses: hit (only bus with sub), sfx, pluck, tick, bed, pad, air. Sync times come from the scene choreography (index.html).
import numpy as np, sys, wave
SR = 48000; T = 22.0; N = int(SR * T)
OUT = sys.argv[1] if len(sys.argv) > 1 else "mix.wav"; GAIN = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
rng = np.random.default_rng(9)
def z(): return np.zeros(N)
def tt(n): return np.arange(n) / SR
def env(n, a, r):  # attack/exp-release envelope
    t = tt(n); e = np.minimum(1, t / max(a, 1e-4)); return e * np.exp(-np.maximum(t - a, 0) / r)
def place(bus, x, t0, g=1.0):
    i = int(t0 * SR);
    if i < 0: x = x[-i:]; i = 0
    j = min(N, i + len(x)); bus[i:j] += g * x[:j - i]
def lp(x, fc):  # one-pole, run twice
    a = np.exp(-2 * np.pi * fc / SR); y = x.copy()
    for _ in range(2):
        out = np.empty_like(y); s = 0.0
        # vectorised one-pole via lfilter-like recursion
        from scipy.signal import lfilter
        out = lfilter([1 - a], [1, -a], y); y = out
    return y
def hp(x, fc): return x - lp(x, fc)
def bp(x, lo, hi): return lp(hp(x, lo), hi)
def sweep(f0, f1, n, curve=1.0):
    k = (np.arange(n) / n) ** curve; f = f0 * (f1 / f0) ** k; return np.sin(2 * np.pi * np.cumsum(f) / SR)
def noise(n): return rng.standard_normal(n)
def reverb(x, sec=1.6, mix=0.25):
    from scipy.signal import fftconvolve
    n = int(sec * SR); ir = noise(n) * np.exp(-tt(n) / (sec / 6.0)); ir = lp(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
    return x + mix * fftconvolve(x, ir)[:len(x)]
hit, sfx, pluck, tick, bed, pad, air = z(), z(), z(), z(), z(), z(), z()
# ---------------------------------------------------------------- hits
def big_hit(size):
    n = int(SR * 3.2); t = tt(n)
    body = np.tanh(2.5 * sweep(260 * size ** 0.2, 62, n, 0.35)) * env(n, 0.004, 0.42 * size)
    sub = np.sin(2 * np.pi * np.cumsum(np.linspace(58, 38, n)) / SR) * env(n, 0.01, 0.6 * size) * 0.8
    crack = lp(hp(noise(n), 2500), 8000) * env(n, 0.0005, 0.035) * 0.9
    wet = bp(noise(n), 300, 1400) * env(n, 0.002, 0.09) * 0.7  # "wet" mid thud
    gong = sum(np.sin(2 * np.pi * f * t + i) * env(n, 0.003, 1.1 / (1 + i * 0.4)) * a for i, (f, a) in enumerate([(196, .35), (293.7 * 1.007, .22), (466 * 0.996, .14), (622, .08)]))
    return (body * 0.9 + sub + crack + wet + gong * 0.6 * size) * size
def suck(dur):  # reversed swell into a hit
    n = int(SR * dur); x = bp(noise(n), 400, 4000) * env(n, 0.002, dur / 3); return x[::-1] * 0.5
place(hit, big_hit(0.75), 0.0)
place(sfx, suck(0.32), 8.7 - 0.32 - 0.05, 0.7); place(hit, big_hit(0.55), 8.7)
place(sfx, suck(0.5), 17.3 - 0.5 - 0.06, 1.0); place(hit, big_hit(1.0), 17.3)
# contact "lock": two dry clicks
def click(f, n=int(0.03 * SR)): return np.sin(2 * np.pi * f * tt(n)) * env(n, 0.0005, 0.006) + hp(noise(n), 3000) * env(n, 0.0002, 0.003) * 0.5
place(sfx, click(1800), 8.72, 0.6); place(sfx, click(1400), 8.80, 0.5)
# ---------------------------------------------------------------- whooshes
def whoosh(dur, lo, hi, peak=0.5):
    n = int(SR * dur); k = np.arange(n) / n; e = np.exp(-((k - peak) / 0.22) ** 2)
    x = noise(n); fc = lo * (hi / lo) ** np.sin(np.pi * k)
    y = np.zeros(n); s = 0.0
    for i0 in range(0, n, 256):  # block-wise moving band
        seg = x[i0:i0 + 256]; f = fc[i0]; a = np.exp(-2 * np.pi * f / SR); o = np.empty_like(seg)
        for i, v in enumerate(seg): s = a * s + (1 - a) * v; o[i] = s
        y[i0:i0 + 256] = o
    y = hp(y, 150); return y / (np.abs(y).max() + 1e-9) * e
place(sfx, whoosh(0.55, 300, 5000, 0.55), 2.05, 0.55)
place(sfx, whoosh(1.6, 200, 4200, 0.6), 19.45, 0.6)
place(air, whoosh(3.6, 150, 1500, 0.5), 4.9, 0.25)  # the crawl
# ---------------------------------------------------------------- receptor sprout: glassy plucks, rising
for i in range(34):
    t0 = 2.85 + 1.9 * (i / 34) + rng.uniform(-0.03, 0.03); f = 900 * 2 ** (i / 34 * 1.2) * rng.choice([1, 1.25, 1.5])
    n = int(0.5 * SR); x = (np.sin(2 * np.pi * f * tt(n)) + 0.3 * np.sin(2 * np.pi * f * 2.76 * tt(n))) * env(n, 0.001, 0.08)
    place(pluck, x, t0, 0.20 * rng.uniform(0.6, 1.0))
# sonar pings while it hunts
for t0, f in ((5.6, 1046.5), (7.15, 1174.7)):
    n = int(1.4 * SR); x = np.sin(2 * np.pi * f * tt(n)) * env(n, 0.004, 0.25)
    for k, dly in enumerate((0.0, 0.21, 0.42)): place(pluck, x, t0 + dly, 0.32 * 0.45 ** k)
# ---------------------------------------------------------------- ticks follow the timer (one per 15 timer-seconds)
TK = [(8.7, 0), (12.0, 180), (16.3, 525), (17.3, 540)]
def vt_inv(s):
    for (a, va), (b, vb) in zip(TK, TK[1:]):
        if s <= vb: return a + (b - a) * (s - va) / (vb - va)
for k, s in enumerate(range(15, 541, 15)):
    t0 = vt_inv(s); n = int(0.05 * SR); f = 2400 + 600 * (s / 540)
    x = (np.sin(2 * np.pi * f * tt(n)) * env(n, 0.0005, 0.01) + bp(noise(n), 1500, 6000) * env(n, 0.0003, 0.004) * 0.6)
    place(tick, x, t0, 0.22 if s % 60 else 0.36)
# ---------------------------------------------------------------- granules: sparkling fizz 13.5-16.4
for i in range(260):
    t0 = rng.uniform(13.5, 16.3); f = rng.uniform(2500, 6500); n = int(0.06 * SR)
    place(pluck, np.sin(2 * np.pi * f * tt(n)) * env(n, 0.001, 0.012), t0, 0.06)
# ---------------------------------------------------------------- blebs: bubbly up-sweeps, then pinch-off pops
for i in range(22):
    t0 = 17.35 + rng.uniform(0, 1.5); n = int(0.12 * SR); f0 = rng.uniform(160, 260)
    place(sfx, sweep(f0, f0 * 2.6, n, 0.6) * env(n, 0.004, 0.035), t0, 0.28)
for i in range(5):
    n = int(0.09 * SR); place(sfx, sweep(380, 900, n) * env(n, 0.002, 0.02) + np.pad(click(700), (0, n - 1440)) * 0.4, 18.7 + i * 0.15, 0.32)
# ---------------------------------------------------------------- bed: body ambience (muffled flow pulse, slows to calm at the end)
t = tt(N)
flow_rate = np.interp(t, [0, 8.7, 16.3, 17.3, 19.5, 22], [1.1, 1.25, 2.1, 0.0, 0.9, 1.1])
ph = 2 * np.pi * np.cumsum(flow_rate) / SR
puls = (0.5 + 0.5 * np.cos(ph)) ** 6
bed += lp(noise(N), 420) * (0.25 + 0.75 * puls) * 0.9
drone = np.sin(2 * np.pi * 110 * t + 0.4 * np.sin(2 * np.pi * 0.21 * t)) + 0.5 * np.sin(2 * np.pi * 165.4 * t) + 0.25 * np.sin(2 * np.pi * 220.6 * t)
bed += drone * 0.10
# tension: rising detuned cluster 5.0 -> 16.3 (filter opens), then held breath
ten = z(); pitch = np.interp(t, [5.0, 16.3], [1.0, 1.5])
for det in (0.997, 1.0, 1.004):
    ten += np.sign(np.sin(2 * np.pi * np.cumsum(146.8 * det * pitch) / SR)) * 0.25
ten = lp(ten, 900) * np.interp(t, [4.8, 6.0, 15.5, 16.3, 16.31, 22], [0, 0.35, 0.8, 0.9, 0, 0])
pad += ten
# resolve chord after the kill (A minor add9, soft) + bell on the end line
res = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(220, .3), (261.6, .22), (329.6, .2), (493.9, .12)])
pad += lp(res, 2000) * np.interp(t, [18.0, 19.2, 21.0, 22], [0, 0.35, 0.3, 0.12])
n = int(2.0 * SR); bell = sum(np.sin(2 * np.pi * f * tt(n)) * env(n, 0.002, 0.7 / (1 + i)) * a for i, (f, a) in enumerate([(880, .4), (1320 * 1.003, .2), (2210, .1)]))
place(pluck, bell, 20.15, 0.35)
# loop link: rising tone into frame 0
n = int(0.9 * SR); place(sfx, sweep(220, 880, n, 2.0) * np.linspace(0, 1, n) ** 2 * 0.35 + suck(0.9) * 0.6, 22.0 - 0.9 - 0.04)
# held breath: duck everything except a faint high tone 16.3-17.25, vacuum 17.24-17.3
duck = np.interp(t, [16.15, 16.35, 17.22, 17.24, 17.30, 17.31], [1, 0.06, 0.06, 0.0, 0.0, 1])
air += np.sin(2 * np.pi * 1760 * t) * 0.02 * np.interp(t, [16.3, 16.5, 17.2, 17.24], [0, 1, 1, 0])
# side-chain under the big hit
sc = 1 - 0.6 * np.exp(-np.maximum(t - 17.3, 0) / 0.5) * (t >= 17.3)
# ---------------------------------------------------------------- mixdown
hit_b = reverb(hit, 2.2, 0.3)
pluck_b = reverb(pluck, 1.4, 0.35)
others = hp(sfx + pluck_b + tick + bed * duck + pad * duck + air, 90)
mixm = hit_b * 1.0 + others * sc
# stereo: plucks and ticks slightly wide via short delays
L = mixm + 0.15 * np.roll(pluck_b, 240); R = mixm + 0.15 * np.roll(pluck_b, -240)
st = np.stack([L, R], 1); st /= np.abs(st).max(); st = np.tanh(1.6 * st * GAIN) / np.tanh(1.6)
st *= 0.68
with wave.open(OUT, "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
print("mix ok", OUT)
