# Sound for "Three Answers to One Fall": fully synthesised in numpy (no samples, no licences needed).
# Sound family "clockwork and grain": stem snap + tape-stop freeze, Newton brass swell + rising fall whistle + strobe plucks,
# Einstein polyrhythm of clock ticks (lower clocks tick slower, pitched by height) + glass sweep for the bending light,
# quantum granular fizz, held breath, one big hit on the twist, a lone pendulum tick, rising link tone into frame 0.
# python3 mix.py out.wav   (sync times mirror index.html)
import sys, math, numpy as np
from scipy.signal import fftconvolve, butter, sosfilt
OUT = sys.argv[1] if len(sys.argv) > 1 else "three_answers_mix.wav"
SR = 48000; T = 22.0; N = int(SR * T)
rng = np.random.default_rng(1915)
# ---- sync constants (from index.html)
G = 2.6; APPLE_TOP = 9.0; GROUND = 0.55 * 0.92
HOOK_Y = APPLE_TOP - 0.5 * G * 0.55 ** 2
N_T0 = 3.0; N_LAND = N_T0 + math.sqrt(2 * (HOOK_Y - GROUND) / G)
E_T0 = 8.9; E_LAND = E_T0 + math.sqrt(2 * (APPLE_TOP - GROUND) / G)
RING_Y = [8.2, 7.1, 6.0, 4.9, 3.8, 2.7, 1.6]; EIN_T0 = 8.0
OMEGA = [2 * math.pi * (0.22 + 0.78 * y / 8.2) / 1.15 for y in RING_Y]
HIT = 17.8
def bus(): return np.zeros((2, N))
hit, sfx, bed, tick, air = bus(), bus(), bus(), bus(), bus()
def tt(n): return np.arange(n) / SR
def place(b, t0, x, gain=1.0, pan=0.0):
    i = int(round(t0 * SR));
    if x.ndim == 1: x = np.vstack([x * math.cos((pan + 1) * math.pi / 4), x * math.sin((pan + 1) * math.pi / 4)]) * math.sqrt(2)
    j0 = max(i, 0); k0 = j0 - i; n = min(N - j0, x.shape[1] - k0)
    if n > 0: b[:, j0:j0 + n] += gain * x[:, k0:k0 + n]
def env(n, a, r, shape=4.0):
    e = np.ones(n); na = max(int(a * SR), 1); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-shape * np.maximum(tt(n) - a, 0) / max(r, 1e-3)); return e
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], btype='band', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, btype='high', fs=SR, output='sos'), x)
def lp(x, f, order=2): return sosfilt(butter(order, f, btype='low', fs=SR, output='sos'), x)
def noise(n): return rng.standard_normal(n)
def sweep_sine(f0, f1, dur, curve=1.0):
    n = int(dur * SR); k = (tt(n) / dur) ** curve; f = f0 * (f1 / f0) ** k; return np.sin(2 * np.pi * np.cumsum(f) / SR)
def boom(size=1.0, f0=300, f1=62, dur=2.6):
    n = int(dur * SR); t = tt(n)
    f = f1 + (f0 - f1) * np.exp(-t * 7); body = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-t * 2.2)
    crack = hp(noise(n), 2200) * np.exp(-t * 38) * 0.9
    gong = sum(np.sin(2 * np.pi * fr * t + p) * np.exp(-t * d) * a for fr, d, a, p in [(147, 1.3, 0.35, 0), (233.5, 1.8, 0.25, 1), (352, 2.4, 0.18, 2), (521, 3.1, 0.12, 3)])
    sub = np.sin(2 * np.pi * np.cumsum(48 + 30 * np.exp(-t * 5)) / SR) * np.exp(-t * 2.8) * 0.8
    return (body * 0.9 + crack + gong + sub) * size
def thud(size=1.0):
    n = int(0.6 * SR); t = tt(n); f = 70 + 120 * np.exp(-t * 30)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) + lp(noise(n), 900) * np.exp(-t * 40) * 0.5) * size
def click_tone(freq, dur=0.12):
    n = int(dur * SR); t = tt(n)
    return (hp(noise(n), 3000) * np.exp(-t * 400) * 0.6 + np.sin(2 * np.pi * freq * t) * np.exp(-t * 45) + 0.35 * np.sin(2 * np.pi * freq * 2.76 * t) * np.exp(-t * 70))
def pluck(freq, dur=0.5):
    n = int(dur * SR); t = tt(n); return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * env(n, 0.003, dur, 5)
def pad(freqs, dur, a=0.6, r=0.8, det=0.003):
    n = int(dur * SR); t = tt(n); x = np.zeros(n)
    for f in freqs:
        for dd in (-det, 0, det): x += np.sin(2 * np.pi * f * (1 + dd) * t + rng.random() * 6.28)
    e = np.minimum(1, t / a) * np.minimum(1, np.maximum(dur - t, 0) / r); return x * e / (3 * len(freqs))
def saw_swell(freqs, dur, a, r, cutoff=1200):
    n = int(dur * SR); t = tt(n); x = np.zeros(n)
    for f in freqs:
        for dd in (-0.004, 0.004): ph = (f * (1 + dd) * t) % 1.0; x += 2 * ph - 1
    x = lp(x, cutoff, 2); e = np.minimum(1, t / a) ** 2 * np.minimum(1, np.maximum(dur - t, 0) / r); return x * e / (2 * len(freqs))
def whoosh(dur, lo=300, hi=3000, rev=False):
    n = int(dur * SR); t = tt(n); x = noise(n); f = np.linspace(lo, hi, 8); out = np.zeros(n)
    for i in range(7):
        seg = bp(x, f[i], f[i + 1]); w = np.exp(-((t / dur - (i + 0.5) / 7) ** 2) / 0.03); out += seg * w
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2; out *= e
    return out[::-1] if rev else out

# ---------------- 0.0  stem snap + release hit, fall whoosh, tape-stop freeze, suspended shimmer
place(hit, 0.0, boom(0.55, 260, 70, 1.8))
place(sfx, 0.0, hp(noise(int(0.05 * SR)), 1800) * np.exp(-tt(int(0.05 * SR)) * 120), 0.9, -0.2)
place(sfx, 0.02, whoosh(0.55, 400, 2400), 0.5)
ts_n = int(0.45 * SR); ts = np.sin(2 * np.pi * np.cumsum(np.linspace(520, 40, ts_n)) / SR) * np.linspace(1, 0, ts_n) ** 1.5
place(sfx, 0.55, ts, 0.35)
place(bed, 0.6, pad([587.3, 880, 1174.7], 1.8, 0.4, 0.6), 0.6)           # held, glassy suspension during the hook
hd = int(1.75 * SR); place(bed, 0.5, (np.sin(2 * np.pi * 98 * tt(hd)) + 0.6 * np.sin(2 * np.pi * 147 * tt(hd))) * (0.6 + 0.4 * np.sin(2 * np.pi * 6 * tt(hd))) * np.minimum(1, tt(hd) / 0.3) * np.minimum(1, (1.75 - tt(hd)) / 0.3), 0.35)
place(sfx, 1.55, whoosh(0.65, 300, 3500), 0.55)                          # carries the hook into the first answer
# ---------------- NEWTON 2.2-7.4: brass swell under the arrow, strobe plucks, rising whistle that accelerates, landing thud, rewind
place(bed, 2.2, saw_swell([73.4, 110, 146.8, 220], 5.2, 0.6, 0.8, 900), 0.55)
place(hit, 2.2, thud(0.6))
for i in range(9):
    tg = N_T0 + i * 0.3
    if tg < N_LAND: place(tick, tg, pluck(392 * 2 ** (-i / 12), 0.45), 0.32, -0.4 + 0.1 * i)
fd = N_LAND - N_T0; fn = int(fd * SR); ft = tt(fn); fr = 220 + 900 * (ft / fd) ** 2
place(sfx, N_T0, np.sin(2 * np.pi * np.cumsum(fr) / SR) * (ft / fd) ** 1.5 * 0.25 + whoosh(fd, 200, 1500) * (ft / fd) * 0.6, 0.6)
place(hit, N_LAND, thud(1.0))
place(sfx, 6.9, whoosh(1.0, 300, 2600, rev=True), 0.45)
place(sfx, 6.9, sweep_sine(200, 900, 1.0, 1.5) * np.sin(np.pi * tt(int(1.0 * SR)) / 1.0) ** 2, 0.12)
place(hit, 7.9, thud(0.5)); place(air, 7.9, click_tone(1760, 0.6), 0.25)   # snap into the second lens
place(sfx, 7.35, whoosh(0.6, 400, 3000), 0.45)
# ---------------- EINSTEIN 7.9-13.9: warm pad, clock polyrhythm (lower = slower = lower pitch), glass sweep for the light, thud
place(bed, 7.9, pad([146.8, 220, 277.2, 329.6], 6.2, 0.7, 1.0), 0.5)
for i, (y, w) in enumerate(zip(RING_Y, OMEGA)):
    step = (2 * math.pi / 12) / w; k = 1; freq = 900 * 2 ** ((y - 1.6) / 6.6 * 1.9); pan = (-0.55 if i % 2 else 0.55) * (0.4 + 0.6 * i / 6)
    while True:
        t0 = EIN_T0 + k * step; k += 1
        if t0 > 13.7: break
        if t0 < 8.4 + i * 0.08: continue
        g = 0.20 * min(1, (t0 - 8.3) / 0.5) * (1 - max(0, (t0 - 13.2) / 0.5)) * (0.6 if (k % 3) else 1.0)
        place(tick, t0, click_tone(freq), g, pan)
place(hit, E_LAND, thud(0.8))
gl_n = int(1.4 * SR); glass = sum(np.sin(2 * np.pi * np.cumsum(np.full(gl_n, f) * (1 + 0.15 * (tt(gl_n) / 1.4))) / SR) for f in (1318.5, 1975.5, 2637)) / 3
place(air, 10.9, glass * env(gl_n, 0.25, 1.4, 1.5) * 0.5, 1.0, 0.0)
place(air, 10.9, whoosh(1.4, 1500, 7000), 0.25)
place(sfx, 12.7, whoosh(1.0, 300, 2600, rev=True), 0.4)
# ---------------- QUANTUM 14.0-17.2: low detuned drone, granular crackle and fizz rising with the foam
qd = 17.2 - 13.9; qn = int(qd * SR); qt = tt(qn)
J = np.clip((qt - (14.9 - 13.9)) / 1.8, 0, 1); J = J * J * (3 - 2 * J)
drone = (np.sin(2 * np.pi * 55 * qt) + np.sin(2 * np.pi * 55.7 * qt) + 0.5 * np.sin(2 * np.pi * 82.6 * qt)) * np.minimum(1, qt / 0.8)
place(bed, 13.9, drone * 0.22)
fizz = bp(noise(qn), 3000, 9000) * (0.15 + 0.85 * J) * np.minimum(1, qt / 0.6)
place(air, 13.9, np.vstack([fizz, bp(noise(qn), 3000, 9000) * (0.15 + 0.85 * J) * np.minimum(1, qt / 0.6)]), 0.12)
grains = np.zeros((2, qn)); dens = 15 + 260 * J
for i in range(qn // 64):
    j = i * 64
    if rng.random() < dens[j] * 64 / SR:
        gl = int(SR * rng.uniform(0.002, 0.012)); f = rng.uniform(600, 6000); g = np.sin(2 * np.pi * f * tt(gl)) * np.hanning(gl) * rng.uniform(0.3, 1.0)
        c = rng.random(); e = min(qn, j + gl) - j; grains[0, j:j + e] += g[:e] * c; grains[1, j:j + e] += g[:e] * (1 - c)
place(sfx, 13.9, grains, 0.5)
place(sfx, 13.6, whoosh(1.0, 200, 1800), 0.8)            # push into the lattice
place(sfx, 13.4, sweep_sine(110, 330, 0.9, 1.5) * np.sin(np.pi * tt(int(0.9 * SR)) / 0.9), 0.25)
# ---------------- held breath 17.2-17.8, reversed suck, 60 ms vacuum, THE hit at 17.8
suck = whoosh(0.5, 400, 4000)[::-1] * np.linspace(0, 1, int(0.5 * SR)) ** 2
place(sfx, HIT - 0.56, suck, 0.35)
place(hit, HIT, boom(1.0, 330, 55, 3.6))
place(sfx, HIT, whoosh(1.5, 150, 2000), 0.5)
# ---------------- twist tail: dark pad, one pendulum clock still ticking, rising link tone into frame 0
place(bed, 18.0, pad([65.4, 98, 130.8, 155.6, 196], 3.9, 0.3, 1.0), 0.9)
for k, t0 in enumerate([19.0, 20.0, 21.0]): place(tick, t0, click_tone(700, 0.25), 0.35, -0.3 if k % 2 else 0.3)
place(sfx, 21.25, sweep_sine(180, 720, 0.75, 2.0) * np.linspace(0, 1, int(0.75 * SR)) ** 2, 0.18)
place(sfx, 21.4, whoosh(0.6, 500, 3000, rev=True), 0.35)

# ---------------- mixing: bass management, reverb, ducking under hits, held-breath gate, master
def stereo(f, b): return np.vstack([f(b[0]), f(b[1])])
for b in (sfx, bed, tick, air): b[:] = stereo(lambda x: hp(x, 90), b)
def reverb(b, dur=2.2, mix=0.25, seed=7):
    r = np.random.default_rng(seed); n = int(dur * SR); t = tt(n)
    irL = r.standard_normal(n) * np.exp(-t * 6.9 / dur); irR = r.standard_normal(n) * np.exp(-t * 6.9 / dur)
    irL = lp(irL, 6000); irR = lp(irR, 6000); irL /= np.sqrt((irL ** 2).sum()); irR /= np.sqrt((irR ** 2).sum())
    wet = np.vstack([fftconvolve(b[0], irL)[:N], fftconvolve(b[1], irR)[:N]]); return b + mix * wet
hit = reverb(hit, 2.6, 0.30); tick = reverb(tick, 1.6, 0.35, 8); bed = reverb(bed, 3.0, 0.25, 9); air = reverb(air, 2.0, 0.3, 10); sfx = reverb(sfx, 1.4, 0.18, 11)
henv = np.abs(hit).max(axis=0); k = int(0.03 * SR); henv = np.convolve(henv, np.ones(k) / k, 'same')
duck = 1 / (1 + 2.5 * henv / (henv.max() + 1e-9))
mix = hit * 1.0 + (sfx * 1.0 + bed * 1.4 + tick * 1.3 + air * 1.0) * duck
t = tt(N); gate = np.ones(N)
gate *= 1 - (np.clip((t - 17.12) / 0.08, 0, 1) * (1 - np.clip((t - (HIT - 0.06)) / 0.001, 0, 1)) * 0.985)   # held breath: near silence until the hit
mix *= gate
# put the reversed suck back on top of the gate (quiet), then a 60 ms vacuum before the hit
sk = np.zeros((2, N)); place(sk, HIT - 0.56, suck, 0.08); sk[:, int((HIT - 0.06) * SR):int(HIT * SR)] = 0; mix += sk
mix = np.tanh(mix / (np.abs(mix).max() + 1e-9) * 1.6) / np.tanh(1.6)
fo = int(0.01 * SR); mix[:, :fo] *= np.linspace(0, 1, fo); mix[:, -fo:] *= np.linspace(1, 0, fo)
mix *= 0.89
import wave
pcm = (np.clip(mix.T, -1, 1) * 32767).astype('<i2')
with wave.open(OUT, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print("mix done", OUT, "N_LAND=%.3f E_LAND=%.3f" % (N_LAND, E_LAND))
