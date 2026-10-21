# mix.py OUT_WAV : fully synthesized sound for "The Jam Is Made of Phones" (no samples, no licences needed).
# Family: "night signal" - city hum, data pings (one per phone), tape-stop slowdown, sonar route search, pluck arpeggio.
import sys, numpy as np
import json, os
SR = 48000
_tm = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timemap.json')))
DUR = _tm['vdur']; N = int(SR * DUR)
_S, _V = np.array(_tm['s']), np.array(_tm['v'])
def S2V(s): return float(np.interp(s, _S, _V))  # cue times are written on the scene clock
rng = np.random.default_rng(611)
bus = {k: np.zeros((2, N)) for k in ['hit', 'sfx', 'bed', 'ping', 'tick']}
def T(n): return np.arange(n) / SR
def put(b, x, t, pan=0.0, g=1.0):
    i = int(S2V(t) * SR); x = np.asarray(x) * g
    if i >= N: return
    n = min(len(x), N - i); l = np.cos((pan + 1) * np.pi / 4); r = np.sin((pan + 1) * np.pi / 4)
    bus[b][0, i:i + n] += x[:n] * l * 1.414; bus[b][1, i:i + n] += x[:n] * r * 1.414
def env(n, a, d, curve=1.0):
    e = np.ones(n); ai = max(1, int(a * SR)); e[:ai] = np.linspace(0, 1, ai)
    e[ai:] = np.exp(-np.arange(n - ai) / (d * SR)) ** curve; return e
from scipy.signal import butter, sosfilt, lfilter
def bp(x, lo, hi, o=2): return sosfilt(butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'highpass', fs=SR, output='sos'), x)
def lpf(x, f, o=2): return sosfilt(butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def sweep(f0, f1, dur, shape=1.0):
    n = int(dur * SR); k = np.linspace(0, 1, n) ** shape; f = f0 * (f1 / f0) ** k; return np.sin(2 * np.pi * np.cumsum(f) / SR)
noise = lambda n: rng.standard_normal(n)
def sst(a, b, x):
    k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
tv = T(N); t = np.interp(tv, _V, _S)   # t = scene clock per sample (for envelopes), tv = real time (for oscillators)

# ---------------- bed: night city (rumble + distant traffic wash + hum chord), ducks to near-silence in the held breath
wash = bp(noise(N), 120, 900) * 0.18 + bp(noise(N), 900, 3500) * 0.025
hum = sum(np.sin(2 * np.pi * f * tv + rng.uniform(0, 6)) * a for f, a in [(110, 0.05), (110.6, 0.04), (164.8, 0.03), (220.4, 0.02), (329.6, 0.012)])
lvl = 0.8 + 0.4 * sst(2.3, 3.0, t)            # city opens up at the snap
lvl *= 1 - 0.75 * sst(6.0, 10.0, t)            # traffic thins as the jam forms
lvl *= 1 - sst(9.95, 10.1, t) * (1 - sst(10.72, 10.8, t))  # held breath
lvl *= 1 - 0.35 * sst(10.8, 11.2, t) * (1 - sst(14.2, 14.6, t))  # close-up: quiet street
lvl *= 1 - 0.5 * sst(21.4, 22.0, t)
for c in range(2): bus['bed'][c] += (wash * (1 if c else 0.92) + hum) * lvl

# ---------------- hits
def hit(tt, size=1.0, pan=0.0, root=300):
    n = int(2.6 * SR)
    crack = hp(noise(n), 2200) * env(n, 0.0005, 0.03) * 0.9
    body = np.tanh(2.2 * np.pad(sweep(root, root * 0.3, 0.9, 0.6), (0, n - int(0.9 * SR)))) * env(n, 0.002, 0.22)
    gong = sum(np.sin(2 * np.pi * f * T(n)) * a * env(n, 0.003, d) for f, a, d in [(root * 1.0, 0.09, 0.7), (root * 2.76, 0.05, 0.4), (root * 5.4, 0.03, 0.2)])
    sub = np.sin(2 * np.pi * 52 * T(n)) * env(n, 0.004, 0.35) * 0.6
    put('hit', (crack + body * 0.8 + gong) * size, tt, pan); put('hit', sub * size, tt)
def suck(t_end, dur=0.45, g=0.6):
    n = int(dur * SR); x = hp(noise(n), 500) * np.linspace(0, 1, n) ** 3
    x = bp(x, 400, 6000); put('sfx', x * g, t_end - dur)
hit(0.0, 0.5, root=280)
suck(10.65, 0.5, 0.7); hit(10.72, 0.75, root=240)          # the reveal: biggest hit, after held breath + 70 ms vacuum

# ---------------- typing ticks (hook, captions, end line)
def ticks(t0, n, cps, g=0.18):
    for k in range(n):
        m = int(0.025 * SR); x = hp(noise(m), 3000) * env(m, 0.0003, 0.006); put('tick', x * g, t0 + k / cps, rng.uniform(-0.3, 0.3))
ticks(0.0, 11, 26); ticks(0.5, 9, 26); ticks(2.55, 15, 30, 0.12); ticks(6.3, 17, 30, 0.1); ticks(7.6, 19, 30, 0.1)
ticks(11.45, 8, 26, 0.14); ticks(12.05, 10, 26, 0.14); ticks(12.65, 10, 26, 0.14); ticks(15.3, 14, 30, 0.1); ticks(16.3, 24, 30, 0.1)
ticks(19.0, 10, 22, 0.16); ticks(19.5, 15, 22, 0.16)

# ---------------- the snap down into the avenue (1.9-2.5): reverse swell into a down-whoosh
n = int(0.55 * SR); sw = bp(noise(n), 300, 5000) * np.linspace(0, 1, n) ** 2.5; put('sfx', sw * 0.5, 1.95)
n = int(0.9 * SR); wd = noise(n) * env(n, 0.01, 0.25); wd = bp(wd, 200, 2500) * 0.6; put('sfx', wd, 2.48, 0.2)
put('hit', np.sin(2 * np.pi * 70 * T(int(0.4 * SR))) * env(int(0.4 * SR), 0.003, 0.12) * 0.5, 2.5)

# ---------------- one data ping per phone (the counter you can hear), pitch rises as the street fills
scale = [0, 2, 4, 7, 9]
for k in range(99):
    ta = 2.5 + 7.1 * (k / 98) ** 0.8
    deg = scale[rng.integers(5)] + 12 * (k // 40); f = 1046.5 * 2 ** (deg / 12)
    m = int(0.18 * SR); x = (np.sin(2 * np.pi * f * T(m)) + 0.3 * np.sin(2 * np.pi * 2 * f * T(m))) * env(m, 0.001, 0.045)
    put('ping', x * (0.10 + 0.05 * k / 98), ta, rng.uniform(-0.7, 0.7))

# ---------------- passing phones (fast whooshes early, fewer and slower as the jam builds)
tp = 2.7
while tp < 7.6:
    dur = 0.35 + 0.25 * sst(4.5, 7.5, tp); n = int(dur * SR); x = bp(noise(n), 250, 1800) * np.hanning(n)
    put('sfx', x * 0.28 * (1 - 0.6 * sst(5, 7.6, tp)), tp, rng.uniform(-0.8, 0.8)); tp += 0.28 + 0.5 * sst(4.5, 7.5, tp) + rng.uniform(0, 0.12)

# ---------------- tape-stop slowdown drone (4.5-10): pitch sinks as the phones slow
a, b = 4.4, 10.0; n = int((b - a) * SR); kk = np.linspace(0, 1, n)
fr = 196 * (1 - 0.5 * sst(0.0, 1.0, kk)); ph = 2 * np.pi * np.cumsum(fr) / SR
dr = (np.tanh(1.8 * np.sin(ph)) * 0.5 + 0.25 * np.sin(2 * ph + 0.3)) * sst(0, 0.15, kk) * (1 - sst(0.93, 1.0, kk)) * 0.22
put('sfx', lpf(dr, 1500), a)
# warning pulse as the road turns red (two low pulses)
for tt in (8.7, 9.25):
    m = int(0.35 * SR); x = np.tanh(2 * np.sin(2 * np.pi * 146.8 * T(m))) * env(m, 0.01, 0.12); put('sfx', x * 0.25, tt)

# ---------------- close-up: footsteps, wagon rattle, 99 phones humming
for k in range(30):
    ts = 10.0 + 0.625 * k
    if 10.9 < ts < 14.5:
        m = int(0.18 * SR); x = lpf(noise(m), 900) * env(m, 0.002, 0.03) + hp(noise(m), 2500) * env(m, 0.001, 0.015) * 0.3
        put('sfx', x * 0.55, ts, -0.25 if k % 2 else 0.05)
n = int(3.5 * SR); rat = bp(noise(n), 1500, 6000) * (0.4 + 0.6 * (np.sin(2 * np.pi * 7.3 * T(n)) > 0.6)) * 0.05
rat *= sst(0, 0.3, T(n)) * (1 - sst(3.0, 3.5, T(n))); put('sfx', rat, 10.85, 0.3)
n = int(3.6 * SR); ch = sum(np.sin(2 * np.pi * f * T(n) + rng.uniform(0, 6)) for f in [523.3, 659.3, 784.0, 1046.5, 1318.5]) * 0.03
ch *= (0.6 + 0.4 * np.sin(2 * np.pi * 3.1 * T(n))) * sst(0, 0.4, T(n)) * (1 - sst(3.1, 3.6, T(n))); put('bed', ch, 10.8)

# ---------------- rise to the map (14.3-15.2)
n = int(1.0 * SR); kk = np.linspace(0, 1, n); x = noise(n) * kk ** 2 * (1 - sst(0.85, 1.0, kk))
x = bp(x, 300, 7000) * 0.5; put('sfx', x, 14.25, -0.2)
put('sfx', sweep(180, 900, 1.0, 2.0) * env(int(1.0 * SR), 0.6, 0.2) * 0.06, 14.25)

# ---------------- route search: sonar sweep + echoes (15.35), then pluck arpeggio as the new route draws (16.4-17.15)
m = int(1.2 * SR); son = sweep(1500, 600, 1.2, 0.5) * env(m, 0.005, 0.35) * 0.18
for d_, g_ in [(0, 1.0), (0.18, 0.45), (0.36, 0.2)]: put('sfx', son * g_, 15.35 + d_, 0.4 * (-1) ** int(d_ * 10))
def pluck(f, tt, g=0.16, pan=0.0):
    m = int(0.9 * SR); x = sum(np.sin(2 * np.pi * f * h * T(m)) / h for h in (1, 2, 3)) * env(m, 0.002, 0.18)
    put('ping', x * g, tt, pan)
notes = [587.3, 659.3, 784.0, 880.0, 987.8, 1174.7]
for k, f in enumerate(notes): pluck(f, 16.4 + k * 0.13, 0.12, -0.5 + k * 0.2)
pluck(880.0, 17.2, 0.16); pluck(1318.5, 17.32, 0.14)

# ---------------- end: warm pad under the end line, then a rising loop tone into frame 0
n = int(4.3 * SR); pad = sum(np.sin(2 * np.pi * f * T(n) + rng.uniform(0, 6)) * a for f, a in [(146.8, 0.05), (220.0, 0.04), (293.7, 0.035), (370.0, 0.025), (440.0, 0.02)])
pad *= sst(0, 0.8, T(n)) * (1 - sst(3.4, 4.3, T(n))); put('bed', pad * 1.4, 17.6)
n = int(1.1 * SR); put('sfx', sweep(220, 880, 1.1, 2.2) * (np.linspace(0, 1, n) ** 2) * 0.08, 20.9)
n = int(0.6 * SR); sw = bp(noise(n), 400, 6000) * np.linspace(0, 1, n) ** 3; put('sfx', sw * 0.35, 21.4)

# ---------------- bus processing: bass management, ducking under hits, master
for k in ['sfx', 'bed', 'ping', 'tick']:
    for c in range(2): bus[k][c] = hp(bus[k][c], 90)
hit_env = np.abs(bus['hit']).max(0); hit_env = lpf(hit_env, 8) ; duck = 1 - 0.5 * np.clip(hit_env / (hit_env.max() + 1e-9), 0, 1)
gains = {'hit': 1.0, 'sfx': 1.0, 'bed': 1.3, 'ping': 0.9, 'tick': 0.8}
mix = sum(bus[k] * gains[k] * (1 if k == 'hit' else duck) for k in bus)
# small room on the hit bus
ir_n = int(1.2 * SR); ir = noise(ir_n) * np.exp(-T(ir_n) / 0.35) * 0.02
from scipy.signal import fftconvolve
for c in range(2): mix[c] += fftconvolve(bus['hit'][c] + bus['ping'][c] * 0.6, ir)[:N]
mix = np.tanh(mix * 1.3) / np.tanh(1.3)
# optional voiceover (already timed to video time by vo_edit.py): sound design ducks about 8 dB under the voice
if len(sys.argv) > 2:
    import subprocess
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', sys.argv[2], '-ac', '1', '-ar', str(SR), '-f', 's16le', '-'], capture_output=True).stdout
    vo = np.frombuffer(raw, np.int16).astype(np.float64)[:N] / 32768; vo = np.pad(vo, (0, N - len(vo)))
    vo = hp(vo, 80); vo /= np.abs(vo).max()
    ve = lpf(np.abs(vo), 6); ve = np.clip(ve / (np.percentile(ve, 95) + 1e-9), 0, 1)
    mix = mix / np.abs(mix).max() * 0.55 * (1 - 0.6 * ve)
    mix += vo * 0.85
mix /= np.abs(mix).max() / 0.89
import wave
out = (np.clip(mix.T, -1, 1) * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('ok')
