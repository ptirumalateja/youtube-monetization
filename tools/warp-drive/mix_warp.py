# The Ship Never Moves: sound, fully synthesised in numpy (no samples, so no licences to credit).
# Sound family "clockwork and stretched space": a steady ship's clock tick runs through the whole reel
# (proper time never changes), a membrane shimmer for the bubble, a flowing-space rush that follows the
# bubble's speed, a light "ping" that falls away in pitch, a sized hit at frame 0 / ignition / twist.
# python3 mix_warp.py out.wav
import sys, numpy as np
SR = 48000; T = 22.0; N = int(SR * T)
rng = np.random.default_rng(1994)
t = np.arange(N) / SR
def sstep(a, b, x): k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def env_at(a, b, fi, fo): return sstep(a, a + fi, t) * (1 - sstep(b - fo, b, t))
def lp_fast(x, fc):  # FFT filters on the whole bus (no scipy needed)
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); X /= np.sqrt(1 + (fr / fc) ** 4); return np.fft.irfft(X, len(x))
def hp_fast(x, fc):
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); X *= (fr / fc) ** 2 / np.sqrt(1 + (fr / fc) ** 4); return np.fft.irfft(X, len(x))
def bp_fast(x, f0, q):
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); X *= 1 / (1 + q * q * (fr / f0 - f0 / np.maximum(fr, 1)) ** 2); return np.fft.irfft(X, len(x))
def place(bus, sig, at, gain=1.0):
    i = int(at * SR); j = min(N, i + len(sig))
    if i < 0: sig = sig[-i:]; j = min(N, len(sig)); i = 0
    bus[i:j] += sig[:j - i] * gain

# speed profile copied from index.html (vraw), normalised 0..1
def vraw(x):
    v = sstep(1.95, 3.2, x); v = np.where(x > 15.3, v * (1 + (0.22 - 1) * sstep(15.3, 16.2, x)), v)
    v = np.where(x > 16.2, v * (1 - sstep(16.8, 19.3, x)), v); return np.where(x < 1.95, 0, v)
V = vraw(t)
amp = np.where(t < 18.6, sstep(1.95, 2.85, t), 1 - sstep(18.6, 19.3, t))

hit = np.zeros(N); sfx = np.zeros(N); bed = np.zeros(N); tick = np.zeros(N); air = np.zeros(N)

# ------------------------------------------------ hits (sized: twist > ignition > frame 0)
def make_hit(dur, f0, f1, crack, sub, gong, seed):
    r = np.random.default_rng(seed); n = int(dur * SR); x = np.arange(n) / SR
    fr = f1 + (f0 - f1) * np.exp(-x * 9); ph = 2 * np.pi * np.cumsum(fr) / SR
    body = np.tanh(2.2 * np.sin(ph)) * np.exp(-x * 3.2)
    cr = hp_fast(r.standard_normal(n), 2200) * np.exp(-x * 38) * crack
    sb = np.sin(2 * np.pi * 46 * x) * np.exp(-x * 2.2) * sub * np.clip(x * 80, 0, 1)
    g = sum(np.sin(2 * np.pi * f * x + r.random() * 6) * np.exp(-x * d) * a for f, d, a in [(196, 1.2, 0.35), (311, 1.6, 0.25), (467, 2.1, 0.18), (622, 2.8, 0.12)]) * gong
    return body * 0.9 + cr + sb + g
def swell(dur, seed):  # reversed noise "suck" into a hit
    r = np.random.default_rng(seed); n = int(dur * SR); x = np.arange(n) / SR
    return bp_fast(r.standard_normal(n), 900, 0.7) * (x / dur) ** 3
place(hit, make_hit(2.2, 260, 70, 0.55, 0.5, 0.25, 1), 0.0, 0.62)                    # frame 0
place(sfx, swell(0.7, 2), 1.95 - 0.7 - 0.06, 0.55); place(hit, make_hit(3.0, 300, 62, 0.8, 0.8, 0.5, 3), 1.95, 0.85)   # ignition
place(sfx, swell(0.5, 4), 16.2 - 0.5 - 0.08, 0.45); place(hit, make_hit(4.5, 340, 52, 1.0, 1.0, 0.9, 5), 16.2, 1.0)   # twist (biggest)
place(hit, make_hit(1.6, 180, 60, 0.25, 0.6, 0.2, 6), 19.3, 0.45)                      # collapse thump

# ------------------------------------------------ the ship's clock: one soft mechanical tick per second, never changes
def make_tick(seed, accent):
    r = np.random.default_rng(seed); n = int(0.12 * SR); x = np.arange(n) / SR
    click = bp_fast(r.standard_normal(n), 3200, 3.0) * np.exp(-x * 160)
    ping = np.sin(2 * np.pi * (2350 if accent else 1980) * x) * np.exp(-x * 55) * 0.35
    wood = np.sin(2 * np.pi * 820 * x) * np.exp(-x * 90) * 0.4
    return (click * 1.4 + ping + wood)
for k in range(22):
    place(tick, make_tick(100 + k, k % 2 == 0), float(k), 0.5)

# ------------------------------------------------ bubble membrane shimmer (detuned cluster, tremolo), follows amp
mem = np.zeros(N)
for f, a in [(392, 0.5), (395.5, 0.5), (587, 0.3), (590.8, 0.3), (784, 0.16), (1176, 0.08)]:
    mem += a * np.sin(2 * np.pi * f * t + rng.random() * 6)
trem = 0.75 + 0.25 * np.sin(2 * np.pi * 5.3 * t)
flick = np.where((t > 16.2) & (t < 19.3), 0.55 + 0.45 * np.sign(np.sin(t * 47) * np.sin(t * 13)), 1.0)
bed += mem * trem * amp * flick * 0.07

# ------------------------------------------------ stretched-space drone: two detuned low voices whose beating speeds up with V
ph1 = 2 * np.pi * np.cumsum(110 + 6 * V) / SR; ph2 = 2 * np.pi * np.cumsum(110.6 + 9 * V) / SR
drone = (np.tanh(1.6 * np.sin(ph1)) + np.tanh(1.6 * np.sin(ph2)) + 0.5 * np.sin(1.5 * ph1)) * (0.25 + 0.75 * amp)
inside = env_at(8.75, 11.35, 0.25, 0.35)                 # muffled while the camera is inside the bubble
bed += lp_fast(drone, 900) * 0.055 * amp * (1 - 0.6 * inside)

# ------------------------------------------------ flowing-space rush: filtered noise, brightness and level follow V
noise = rng.standard_normal(N)
rush = bp_fast(noise, 700, 0.6) * 0.6 + bp_fast(noise, 2600, 1.2) * 0.25
rush_env = V ** 1.3 * (1 - 0.75 * inside) * (1 - sstep(15.3, 15.6, t) * 0.92)
air += rush * rush_env * 0.10
# grid lines passing: soft periodic "flutter" at the rate grid lines cross under the ship (~VMAX lines/s)
lines_ph = np.cumsum(13.16 * V) / SR
flutter = (0.5 + 0.5 * np.cos(2 * np.pi * lines_ph)) ** 6
air += bp_fast(noise, 1400, 2) * flutter * V * 0.03 * (1 - inside)

# ------------------------------------------------ camera passes the bubble wall: whoosh in (8.6) and out (11.3)
def whoosh(dur, seed, up=True):
    r = np.random.default_rng(seed); n = int(dur * SR); x = np.arange(n) / SR
    e = np.sin(np.pi * x / dur) ** 2; s = bp_fast(r.standard_normal(n), 1200, 0.8)
    return s * e
place(sfx, whoosh(0.9, 7), 8.2, 0.35); place(sfx, (mem[:int(0.6 * SR)] * np.exp(-np.arange(int(0.6 * SR)) / SR * 5)), 8.65, 0.5)
place(sfx, whoosh(1.0, 8), 11.0, 0.40)
place(sfx, whoosh(1.1, 9), 2.2, 0.30)                    # pull-back after ignition

# ------------------------------------------------ light beam: a bright ping at 12.3 that falls away in pitch as the bubble outruns it
n = int(3.2 * SR); x = np.arange(n) / SR
fr = 2600 * (0.5 ** (x / 1.8)); ph = 2 * np.pi * np.cumsum(fr) / SR
beam = (np.sin(ph) + 0.3 * np.sin(2 * ph)) * np.exp(-x * 0.9) * np.clip(x * 60, 0, 1)
place(sfx, beam, 12.3, 0.16)
place(sfx, make_tick(77, True), 12.3, 0.6)

# ------------------------------------------------ twist: unstable crackle while the wall flickers, implosion sweep into collapse
cr_env = env_at(16.35, 18.9, 0.2, 0.3)
gate = (rng.random(N) < 0.004).astype(float); gate = lp_fast(gate, 400) * 40
air += lp_fast(hp_fast(noise, 1800), 6000) * np.clip(gate, 0, 1) * cr_env * 0.07
n = int(0.75 * SR); x = np.arange(n) / SR; fr = 900 * (0.12 ** (x / 0.75))
place(sfx, np.sin(2 * np.pi * np.cumsum(fr) / SR) * (x / 0.75) ** 1.5 * 0.5 + bp_fast(rng.standard_normal(n), 500, 0.6) * (x / 0.75) ** 2, 18.55, 0.45)

# ------------------------------------------------ end: warm pad + loop-link rising tone into frame 0
pad = np.zeros(N)
for f in [220, 277.2, 329.6, 440]:
    pad += np.sin(2 * np.pi * f * t + rng.random() * 6) + 0.3 * np.sin(2 * np.pi * f * 1.003 * t)
bed += lp_fast(pad, 1500) * env_at(19.2, 22.0, 0.8, 0.5) * 0.035
rise = np.sin(2 * np.pi * np.cumsum(330 + 330 * sstep(21.0, 22.0, t)) / SR) * env_at(21.0, 22.0, 0.6, 0.06) * 0.06
bed += rise

# ------------------------------------------------ held breath (15.3-16.2): everything but the clock drops away
hold = 1 - 0.97 * env_at(15.35, 16.2, 0.3, 0.02)
bed *= hold; air *= hold

# ------------------------------------------------ bus processing: phones can't play < ~90 Hz, so sub only on the hit bus
for b in (sfx, bed, air, tick): b[:] = hp_fast(b, 90)
hit = lp_fast(0.5 * np.tanh(hit / 0.5), 9000)                   # soft-clip the hit transients (they caused AAC overs)
duck = 1 - 0.5 * np.clip(lp_fast(np.abs(hit), 8), 0, 1)
mix = hit * 0.9 + (sfx + bed + air) * duck + tick * 1.0
# small reverb on the hit bus (sum of decaying taps)
rv = np.zeros(N)
for d, g in [(0.031, 0.35), (0.047, 0.3), (0.071, 0.25), (0.113, 0.2), (0.173, 0.15), (0.251, 0.1)]:
    k = int(d * SR); rv[k:] += hit[:-k] * g
mix += lp_fast(rv, 3000) * 0.5
st = np.stack([mix, mix], 1)
# gentle width: delay the air/sfx a touch in the right channel
k = int(0.011 * SR); st[k:, 1] += (sfx + air)[:-k] * 0.12; st[:, 0] += (sfx + air) * 0.12
st = np.tanh(st * 2.0) / np.tanh(2.0)
st = np.stack([lp_fast(st[:, c], 15000) for c in (0, 1)], 1)       # tame the clicks' top end (inter-sample overs)
def true_peak(x):  # 4x oversampled peak
    n = len(x); X = np.fft.rfft(x); Y = np.zeros(2 * n + 1, complex); Y[:len(X)] = X; return np.max(np.abs(np.fft.irfft(Y, 4 * n))) * 4
tp = max(true_peak(st[:, 0]), true_peak(st[:, 1]))
st *= 10 ** (-3.3 / 20) / tp                                       # -3.3 dBTP before AAC: lands near -15 LUFS, about -2.5 dBTP after AAC
import wave
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype('<i2').tobytes()); w.close(); print('ok', sys.argv[1])
