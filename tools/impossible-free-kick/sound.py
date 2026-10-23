"""Synthesised sound for the free-kick reel (no samples, nothing to license).
Usage: python3 sound.py meta.json out.wav
meta.json maps frame -> {S: scene time, ...} from the renderer; cue times come from it."""
import json, sys
import numpy as np
from scipy import signal

SR = 48000
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(1997)
t = np.arange(N) / SR

meta = json.load(open(sys.argv[1]))
frames = sorted(int(k) for k in meta)
S = np.interp(np.arange(600), frames, [meta[str(f)]['S'] for f in frames])
T_GOAL = 1.2855


def when(s_target, after=0.0):
    """first video time (s) where scene time crosses s_target"""
    for f in range(1, 600):
        if f / 30 >= after and S[f - 1] < s_target <= S[f]:
            u = (s_target - S[f - 1]) / (S[f] - S[f - 1])
            return (f - 1 + u) / 30
    return None


T_KICK = when(0.0)
T_POST = when(T_GOAL, after=10)
print('kick', T_KICK, 'post', T_POST)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], 'bandpass', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def lp(x, f, order=2):
    sos = signal.butter(order, f, 'lowpass', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def hp(x, f, order=2):
    sos = signal.butter(order, f, 'highpass', fs=SR, output='sos'); return signal.sosfilt(sos, x)
def env(a, d, n=None):
    n = n or int((a + d) * SR); k = np.arange(n) / SR
    return np.where(k < a, k / max(a, 1e-4), np.exp(-(k - a) / max(d, 1e-4)))
def place(bus, x, at, gain=1.0):
    i = int(at * SR);
    if i >= N: return
    j = min(N, i + len(x)); bus[i:j] += gain * x[:j - i]
def ramp(points):  # [(time, value), ...] piecewise linear gain curve
    ts, vs = zip(*points); return np.interp(t, ts, vs)

hit, sfx, bed, air, tick = (np.zeros(N) for _ in range(5))

# ---------------------------------------------------------------- crowd bed (murmur), roar after the goal
def crowd(n, seed):
    r = np.random.default_rng(seed); x = np.zeros(n)
    for k in range(14):  # many voices, each a band of noise with its own slow swell
        lo = r.uniform(250, 900); x += bp(r.standard_normal(n), lo, lo * r.uniform(1.6, 3.0)) * (0.6 + 0.4 * np.sin(2 * np.pi * r.uniform(0.05, 0.4) * np.arange(n) / SR + r.uniform(0, 6)))
    return x / np.abs(x).max()
mur = crowd(N, 3)
roar = crowd(N, 5) + 0.6 * bp(rng.standard_normal(N), 500, 2600)
# vowel "ooo" layer for the roar: detuned saws with vibrato
vow = np.zeros(N)
for k in range(24):
    f0 = rng.uniform(170, 330); vib = 1 + 0.012 * np.sin(2 * np.pi * rng.uniform(4, 6.5) * t + rng.uniform(0, 6))
    ph = np.cumsum(f0 * vib) / SR; vow += signal.sawtooth(2 * np.pi * ph) * rng.uniform(0.5, 1)
vow = bp(vow, 300, 1400) / 24
roar = roar / np.abs(roar).max() + 0.8 * vow / np.abs(vow).max()
crowd_g = ramp([(0, 0.32), (2.9, 0.42), (3.1, 0.5), (4.4, 0.42), (4.9, 0.05), (14.2, 0.05), (14.4, 0.0), (15.0, 0.0), (15.3, 0.25), (T_POST - 0.4, 0.42), (DUR, 0.42)])
# during the freeze the crowd is a muffled, low-passed hush
muffled = lp(mur, 380)
freeze_mix = ramp([(0, 0), (4.6, 0), (4.95, 1), (14.9, 1), (15.2, 0), (DUR, 0)])
bed += (mur * (1 - freeze_mix) + muffled * 1.8 * freeze_mix) * crowd_g
roar_g = ramp([(0, 0), (T_POST, 0), (T_POST + 0.25, 1.0), (18.4, 1.0), (18.6, 0.75), (DUR, 0.5)])
bed += roar * roar_g * 0.9

# ---------------------------------------------------------------- hits
def boom(f0=150, f1=48, dur=1.6, crack=0.6, sub=0.8):
    n = int(dur * SR); k = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-k / 0.09); ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.tanh(2.2 * np.sin(ph)) * np.exp(-k / 0.45)
    cr = hp(rng.standard_normal(n), 2200) * np.exp(-k / 0.02) * crack
    sb = np.sin(2 * np.pi * 42 * k) * np.exp(-k / 0.7) * sub
    return body + cr + sb
def suck(dur=0.5):
    n = int(dur * SR); k = np.arange(n) / SR
    return bp(rng.standard_normal(n), 300, 5000) * (k / dur) ** 3
place(hit, boom(170, 50, 1.8, 0.7, 0.9), 0.0, 0.9)                       # frame 0
# run-up footsteps (studs on turf): accelerate into the strike
steps = np.cumsum([0.34, 0.3, 0.27, 0.24, 0.22])[::-1]
for s in steps:
    n = int(0.12 * SR); k = np.arange(n) / SR
    fs_ = bp(rng.standard_normal(n), 120, 900) * np.exp(-k / 0.03) + 0.6 * np.sin(2 * np.pi * 85 * k) * np.exp(-k / 0.04)
    place(sfx, fs_, T_KICK - s, 0.5)
# the strike: leather thump with a slow-motion tail
place(sfx, suck(0.25), T_KICK - 0.25, 0.25)
place(hit, boom(260, 70, 1.4, 1.0, 0.6), T_KICK, 1.0)
# slow-motion whoosh as the ball leaves (pitched down)
def whoosh(dur, f_lo, f_hi, rise=0.35):
    n = int(dur * SR); k = np.arange(n) / SR
    x = rng.standard_normal(n); out = np.zeros(n); blk = 2048
    for i in range(0, n, blk):
        u = i / n; fc = f_lo + (f_hi - f_lo) * np.sin(np.pi * u) ** 2
        seg = x[max(0, i - 4096):i + blk]; y = bp(seg, max(60, fc * 0.6), fc * 1.6)[-min(blk, n - i):]
        out[i:i + len(y)] = y
    e = np.minimum(1, k / (dur * rise)) * np.minimum(1, (dur - k) / (dur * 0.5)); return out * e
place(sfx, whoosh(1.6, 180, 900), T_KICK + 0.02, 0.7)
# time slowing down into the freeze: tape-stop pitch drop on a tone cluster, then the ice crack
n = int(0.6 * SR); k = np.arange(n) / SR; f = 420 * np.exp(-k * 2.2)
place(sfx, np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 - k / 0.6) * 0.5, 4.3, 0.5)
fr = boom(320, 90, 1.2, 1.0, 0.5)
n = int(1.5 * SR); k = np.arange(n) / SR
glass = sum(np.sin(2 * np.pi * f_ * k) * np.exp(-k / d_) for f_, d_ in [(1870, 0.5), (2630, 0.35), (3410, 0.25), (4950, 0.18)])
place(hit, fr, 4.9, 0.8); place(sfx, glass * 0.12, 4.9)
# countdown ticks 3-2-1 (clock + low knock), heartbeat underneath
for i, at in enumerate([5.0, 6.0, 7.0]):
    n = int(0.25 * SR); k = np.arange(n) / SR
    tk = hp(rng.standard_normal(n), 3000) * np.exp(-k / 0.008) + np.sin(2 * np.pi * (1200 - 150 * i) * k) * np.exp(-k / 0.03) * 0.5 + np.sin(2 * np.pi * 110 * k) * np.exp(-k / 0.08) * 0.8
    place(tick, tk, at, 0.8 + 0.1 * i)
for at in np.arange(5.0, 8.0, 0.5):
    n = int(0.3 * SR); k = np.arange(n) / SR
    hb = np.sin(2 * np.pi * 58 * k) * np.exp(-k / 0.07) + 0.5 * np.sin(2 * np.pi * 95 * k) * np.exp(-k / 0.05)
    place(hit, hb, at + 0.25, 0.35); place(hit, hb, at + 0.42, 0.22)
# swoop into bullet time
place(sfx, whoosh(1.0, 300, 2400, 0.6), 7.85, 0.6)
place(hit, boom(200, 60, 1.0, 0.4, 0.4), 8.6, 0.45)
# spinning air around the ball (whirr modulated at the visible spin rate) 8.6-12
seg_ = (t > 8.4) & (t < 12.4)
whirr = bp(rng.standard_normal(N), 500, 3500) * (0.55 + 0.45 * np.sin(2 * np.pi * 3.2 / (2 * np.pi) * 2 * t) ** 2)
wind = lp(rng.standard_normal(N), 700)
air_g = ramp([(0, 0), (8.5, 0), (9.0, 1), (11.6, 1), (12.4, 0), (DUR, 0)])
air += (0.35 * whirr / np.abs(whirr).max() + 0.5 * wind / np.abs(wind).max()) * air_g
# Magnus reveal chime at 9.6 (force arrow)
n = int(1.6 * SR); k = np.arange(n) / SR
chime = sum(np.sin(2 * np.pi * f_ * k) * np.exp(-k / 0.6) * a_ for f_, a_ in [(523, 1), (784, 0.6), (1046, 0.4), (1568, 0.2)])
place(sfx, chime * 0.25, 9.65)
# rise to the top view + riser into the held breath
place(sfx, whoosh(1.6, 200, 1800, 0.5), 11.3, 0.5)
n = int(1.9 * SR); k = np.arange(n) / SR
riser = sum(np.sin(2 * np.pi * np.cumsum(f_ * 2 ** (k * 1.1)) / SR) for f_ in [110, 165, 220.5]) * (k / 1.9) ** 2 + bp(rng.standard_normal(n), 800, 6000) * (k / 1.9) ** 3 * 0.7
place(sfx, riser * 0.35, 12.4)
# held breath 14.35-15.0: nothing. Release: reverse suck + hit
place(sfx, suck(0.35), 14.65, 0.3)
place(hit, boom(220, 55, 1.6, 0.8, 0.8), 15.0, 0.85)
place(sfx, whoosh(2.4, 150, 700), 15.05, 0.6)
# the post: metallic ping + net swish + the stadium erupts
n = int(2.5 * SR); k = np.arange(n) / SR
ping = sum(np.sin(2 * np.pi * f_ * k) * np.exp(-k / d_) * a_ for f_, d_, a_ in [(612, 0.9, 1), (1468, 0.6, 0.7), (2390, 0.4, 0.5), (3610, 0.25, 0.35), (5200, 0.12, 0.2)])
ping += hp(rng.standard_normal(n), 3000) * np.exp(-k / 0.01) * 0.8
place(sfx, ping * 0.55, T_POST)
n = int(0.9 * SR); k = np.arange(n) / SR
place(sfx, bp(rng.standard_normal(n), 1500, 9000) * np.exp(-k / 0.18) * np.minimum(1, k / 0.02), T_POST + 0.12, 0.5)
place(hit, boom(150, 45, 2.2, 0.3, 1.0), T_POST + 0.05, 0.9)
# rewind 18.5-20: chirpy tape rewind, reversed whoosh, rising into the loop hit at frame 0
n = int(1.5 * SR); k = np.arange(n) / SR
rew = bp(rng.standard_normal(n), 1500, 7000) * (0.4 + 0.6 * (np.sin(2 * np.pi * (6 + 18 * k) * k) > 0.3))
rew += 0.4 * np.sin(2 * np.pi * np.cumsum(300 + 2600 * (k / 1.5) ** 2) / SR)
place(sfx, rew * np.minimum(1, k / 0.1) * 0.35, 18.5)
place(sfx, suck(0.6), 19.4, 0.45)

# ---------------------------------------------------------------- mix
def norm(x): m = np.abs(x).max(); return x / m if m > 0 else x
hit_ = hp(hit, 35); sfx_ = hp(sfx, 90); bed_ = hp(bed, 90); air_ = hp(air, 90); tick_ = hp(tick, 90)
# duck the bed under hits
envh = lp(np.abs(hit_), 8); duck = 1 - 0.45 * norm(envh)
mix = 1.0 * hit_ + 0.8 * sfx_ + 0.42 * bed_ * duck + 0.5 * air_ + 0.7 * tick_
# held breath: near silence before the release
mix *= ramp([(0, 1), (14.3, 1), (14.45, 0.05), (14.62, 0.05), (14.7, 1), (DUR, 1)])
# loop: fade the last 40 ms, first 5 ms ramp in
mix[:240] *= np.linspace(0, 1, 240); mix[-1920:] *= np.linspace(1, 0.2, 1920)
mix = np.tanh(1.4 * mix / np.abs(mix).max()) * 0.9
st = np.stack([mix, mix], 1)
# slight stereo width on bed/air
w = hp(0.05 * (bed_ + air_), 200); st[:, 0] += w; st[:, 1] -= w
st /= np.abs(st).max() / 0.89
import soundfile as sf
sf.write(sys.argv[2], st.astype(np.float32), SR, subtype='PCM_24')
print('wrote', sys.argv[2])
