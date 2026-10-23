# mix3.py OUT_WAV : v3 sound for "The Jam Is Made of Phones" - sound tells the story, no constant drone, all synthesized.
# Beats: alert + impact on the red road (0), empty-street silence and footsteps, wagon wheels + tightening pulse,
# one ping multiplying into 99, held breath, rising data pulses, heavy impact on the map, route search, silence,
# one notification, swell into the loop hit.
import sys, numpy as np, wave
from scipy.signal import butter, sosfilt, fftconvolve
SR = 48000; DUR = 22.0; N = int(SR * DUR)
rng = np.random.default_rng(23)
bus = {k: np.zeros((2, N)) for k in ['hit', 'sfx', 'bed', 'ping', 'tick', 'fol']}
def T(n): return np.arange(n) / SR
def put(b, x, t, pan=0.0, g=1.0):
    i = int(t * SR); x = np.asarray(x) * g
    if i >= N or i < 0: return
    n = min(len(x), N - i); l = np.cos((pan + 1) * np.pi / 4) * 1.414; r = np.sin((pan + 1) * np.pi / 4) * 1.414
    bus[b][0, i:i + n] += x[:n] * l; bus[b][1, i:i + n] += x[:n] * r
def env(n, a, d):
    e = np.ones(n); ai = max(1, int(a * SR)); e[:ai] = np.linspace(0, 1, ai); e[ai:] = np.exp(-np.arange(n - ai) / (d * SR)); return e
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)
def lpf(x, f, o=2): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def sweep(f0, f1, dur, shape=1.0):
    n = int(dur * SR); k = np.linspace(0, 1, n) ** shape; f = f0 * (f1 / f0) ** k; return np.sin(2 * np.pi * np.cumsum(f) / SR)
noise = lambda n: rng.standard_normal(n)
def sst(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
t = T(N)
def hit(tt, size=1.0, root=160, pan=0.0):
    n = int(2.4 * SR)
    crack = hp(noise(n), 2200) * env(n, 0.0005, 0.03) * 0.9
    body = np.tanh(2.4 * np.pad(sweep(root * 1.8, root * 0.45, 0.8, 0.6), (0, n - int(0.8 * SR)))) * env(n, 0.002, 0.24)
    gong = sum(np.sin(2 * np.pi * f * T(n)) * a * env(n, 0.003, d) for f, a, d in [(root * 1.5, 0.08, 0.7), (root * 4.1, 0.05, 0.4), (root * 8.0, 0.03, 0.2)])
    sub = np.sin(2 * np.pi * 50 * T(n)) * env(n, 0.004, 0.45) * 0.7
    put('hit', (crack + body * 0.85 + gong) * size, tt, pan); put('hit', sub * size, tt)
def suck(t_end, dur=0.4, g=0.6):
    n = int(dur * SR); x = bp(hp(noise(n), 500) * np.linspace(0, 1, n) ** 3, 400, 6000); put('sfx', x * g, t_end - dur)
def tone(f, dur, g, tt, pan=0.0, h=(1, 0.3), bus_='ping', dec=0.06):
    m = int(dur * SR); x = sum(np.sin(2 * np.pi * f * (k + 1) * T(m)) * a for k, a in enumerate(h)) * env(m, 0.001, dec); put(bus_, x * g, tt, pan)

# camera-to-walker distance (replicates the scene's dolly) for footstep loudness
def cam_z(s):
    u = min(max(s / 6.2, 0), 1); f = 1 - (1 - u) ** 1.6; wz = lambda q: -25 - 1.6 * q
    return 55 + (wz(6.2) + 5.2 - 55) * f if s < 6.2 else wz(s) + 5.2
def dist(s): return max(abs(cam_z(s) - (-25 - 1.6 * s - 2.0)), 3.0)

# ---- 0: the red road. Alert chirp + impact, then it falls away to wind
tone(1318.5, 0.25, 0.22, 0.0, 0.0, (1, 0.25), 'ping', 0.09); tone(987.8, 0.3, 0.22, 0.16, 0.0, (1, 0.25), 'ping', 0.11); tone(1318.5, 0.3, 0.18, 0.34, 0.0, (1, 0.25), 'ping', 0.12)
hit(0.0, 1.0, 150)
wind = bp(noise(N), 180, 1100) * 0.07 * (sst(0.1, 0.8, t) * (1 - sst(2.0, 3.0, t)) + 0.35 * sst(2.9, 3.6, t) * (1 - sst(6.8, 7.6, t)))
rum = lpf(noise(N), 160) * 0.18 * sst(0.0, 0.2, t) * (1 - sst(0.9, 2.2, t))
for c in range(2): bus['bed'][c] += wind * (1 if c else 0.9) + rum
# ---- 2.4-6.5: silence, isolated footsteps (louder as the camera closes in)
s_ = 2.75
while s_ < 7.0:
    d_ = dist(s_); g_ = np.clip(9.0 / d_, 0.05, 1.0) ** 1.0
    m = int(0.2 * SR); x = lpf(noise(m), 700) * env(m, 0.002, 0.035) + hp(noise(m), 2500) * env(m, 0.0008, 0.012) * 0.25
    put('fol', x * 0.5 * g_, s_, -0.15 if int((s_ - 2.75) / 0.62) % 2 else 0.1); s_ += 0.62
# wagon wheels: rolling rattle at the wheel rate that fades in as the camera nears, tick per rev
n = int(5.0 * SR); tt_ = T(n); rr = bp(noise(n), 900, 4200) * (0.35 + 0.65 * (np.sin(2 * np.pi * 6.4 * tt_) > 0.5)) * 0.09
rr *= sst(0, 2.2, tt_) * (1 - sst(4.2, 5.0, tt_)); put('fol', rr, 4.1, 0.2)
for k in range(30):
    ts = 4.4 + k / 1.6
    if ts < 8.9:
        m = int(0.03 * SR); put('fol', hp(noise(m), 1800) * env(m, 0.0004, 0.008) * 0.2 * sst(4.4, 6.2, ts), ts, 0.2)
# tightening pulse: heartbeat-like low thumps, interval shrinks 0.95 -> 0.26 s
tp = 4.9; k = 0
while tp < 8.95:
    u = (tp - 4.9) / 4.05; m = int(0.22 * SR)
    x = np.tanh(2.0 * sweep(150, 95, 0.22, 0.5)[:m]) * env(m, 0.002, 0.07); put('sfx', x * (0.18 + 0.32 * u), tp)
    tp += 0.95 - 0.69 * u ** 0.9; k += 1
# ---- 7.0-8.9: one ping becomes dozens (99 total, spacing shrinks), a shimmer bed rises under it
scale = [0, 2, 4, 7, 9]
APP = []
order = np.arange(99)
for kk in range(99):
    u = kk / 98; ta = 7.0 + 1.9 * (1 - (1 - u) ** 2.0); APP.append(ta)
    deg = scale[(kk * 7) % 5] + 12 * (kk // 33); f = 880 * 2 ** (deg / 12)
    tone(f, 0.18, 0.07 + 0.07 * u, ta, rng.uniform(-0.8, 0.8), (1, 0.3), 'ping', 0.05)
    m = int(0.012 * SR); put('tick', hp(noise(m), 4000) * env(m, 0.0003, 0.004) * 0.15, ta, rng.uniform(-0.5, 0.5))
n = int(2.2 * SR); kk_ = np.linspace(0, 1, n); sh = bp(noise(n), 2500, 9000) * kk_ ** 3 * 0.05; put('sfx', sh, 6.9)
# ---- 8.95-9.35 held breath, then the ascent: rising riser + rhythmic data pulses
n = int(4.3 * SR); kk_ = np.linspace(0, 1, n); ris = bp(noise(n), 300, 8000) * kk_ ** 2.2 * 0.22; put('sfx', ris, 9.3)
put('sfx', sweep(110, 880, 4.3, 2.5) * np.linspace(0, 1, n) ** 2 * 0.09, 9.3)
for k in range(15):
    ts = 9.6 + k * 0.27 - 0.003 * k * k; f = 1500 * 2 ** (k / 12); u = k / 14
    tone(f, 0.07, 0.05 + 0.08 * u, ts, (-1) ** k * 0.4, (1, 0.5), 'tick', 0.02)
suck(13.55, 0.45, 0.6)
# ---- 13.6: the map. Heavy impact, then routing
hit(13.6, 1.25, 120)
n = int(1.2 * SR); son = sweep(1500, 600, 1.2, 0.5) * env(n, 0.005, 0.35) * 0.16
for d_, g_ in [(0, 1.0), (0.18, 0.45), (0.36, 0.2)]: put('sfx', son * g_, 15.3 + d_, 0.4 * (-1) ** int(d_ * 10))
for kk, f in enumerate([587.3, 659.3, 784.0, 880.0, 987.8, 1174.7]): tone(f, 0.5, 0.11, 16.4 + kk * 0.13, -0.5 + kk * 0.2, (1, 0.5, 0.33), 'ping', 0.16)
tone(880.0, 0.5, 0.15, 17.2, 0, (1, 0.5, 0.33), 'ping', 0.16); tone(1318.5, 0.6, 0.13, 17.32, 0, (1, 0.5, 0.33), 'ping', 0.2)
# ---- 18.4-19.2 silence, then one notification (phone-like two-tone) and a little wind
tone(1567.98, 0.35, 0.2, 19.15, -0.1, (1, 0.35), 'ping', 0.1); tone(2093.0, 0.55, 0.2, 19.3, 0.1, (1, 0.35), 'ping', 0.18)
wind2 = bp(noise(N), 180, 900) * 0.05 * sst(19.4, 20.0, t) * (1 - sst(21.2, 21.8, t));
for c in range(2): bus['bed'][c] += wind2
# ---- descent + loop link: reverse swell, rising tone, vacuum, hit on frame 0 of the next loop is the 0.0 hit
n = int(1.7 * SR); put('sfx', bp(noise(n), 300, 7000) * np.linspace(0, 1, n) ** 3 * 0.35, 20.2)
put('sfx', sweep(200, 900, 1.7, 2.2) * np.linspace(0, 1, n) ** 2 * 0.08, 20.2)
suck(21.98, 0.3, 0.45)
# typing ticks (soft)
def ticks(t0, cnt, cps, g=0.1):
    for k in range(cnt):
        m = int(0.025 * SR); put('tick', hp(noise(m), 3000) * env(m, 0.0003, 0.006) * g, t0 + k / cps, rng.uniform(-0.3, 0.3))
ticks(0.0, 19, 30); ticks(0.55, 23, 30); ticks(2.7, 12, 26); ticks(4.7, 11, 26); ticks(7.15, 10, 18, 0.16)
ticks(10.4, 15, 28); ticks(11.2, 15, 28); ticks(14.4, 10, 26); ticks(15.1, 14, 26); ticks(19.1, 11, 22, 0.13); ticks(19.7, 10, 22, 0.13)
# ---- bus processing
for k in ['sfx', 'bed', 'ping', 'tick', 'fol']:
    for c in range(2): bus[k][c] = hp(bus[k][c], 90)
hit_env = np.abs(bus['hit']).max(0); hit_env = lpf(hit_env, 8); duck = 1 - 0.55 * np.clip(hit_env / (hit_env.max() + 1e-9), 0, 1)
silence = 1 - 0.8 * (sst(8.95, 9.05, t) * (1 - sst(9.3, 9.36, t))) - 0.85 * (sst(18.3, 18.5, t) * (1 - sst(19.1, 19.15, t)))
gains = {'hit': 1.0, 'sfx': 1.0, 'bed': 1.2, 'ping': 0.9, 'tick': 0.8, 'fol': 1.1}
mix = sum(bus[k] * gains[k] * (1 if k == 'hit' else duck) * (1 if k == 'hit' else silence) for k in bus)
ir_n = int(1.1 * SR); ir = noise(ir_n) * np.exp(-T(ir_n) / 0.3) * 0.02
for c in range(2): mix[c] += fftconvolve(bus['hit'][c] + bus['ping'][c] * 0.5, ir)[:N]
mix = np.tanh(mix * 1.3) / np.tanh(1.3); mix /= np.abs(mix).max() / 0.89
out = (np.clip(mix.T, -1, 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok')
