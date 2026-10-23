"""V3 mix: the V2 sound re-timed for the drama edit (wall, whistle, run-up, celebration). python3 sound3.py meta.json out.wav
Synth layers plus CC0 Freesound files from tools/sfxlib (qubodup, AudioPapkin, lucabia, stewdio2003,
sleepCircle: CC0, no credit needed). Contrast is the design: silence around the rewind and bullet time
so the two goals hit hardest."""
import json, sys
import numpy as np
import soundfile as sf
from scipy import signal

SR = 48000; DUR = 22.4; N = int(SR * DUR)
rng = np.random.default_rng(97)
t = np.arange(N) / SR
LIB = __file__.rsplit('/', 2)[0] + '/sfxlib/'

meta = json.load(open(sys.argv[1]))
NF = int(DUR * 30); S = np.array([meta[str(f)]['S'] for f in range(NF)])
H3, R3, BT0, BT1, CEL0, CEL1 = 3.0, 4.3, 10.0, 13.9, 17.1, 17.9   # must match index3.html
T_GOAL = 1.2855
def when(s_target, lo, hi):
    for f in range(max(1, int(lo * 30)), min(NF, int(hi * 30) + 1)):
        if S[f - 1] < s_target <= S[f]: return (f - 1 + (s_target - S[f - 1]) / (S[f] - S[f - 1])) / 30
T_HIT1 = when(T_GOAL, 0, H3); T_KICK = when(0.0, 6.5, 9.5); T_HIT2 = when(T_GOAL, BT1, CEL0)
print('hit1', T_HIT1, 'kick', T_KICK, 'hit2', T_HIT2)

def load(name, sr_to=SR):
    x, sr = sf.read(LIB + name); x = x if x.ndim == 1 else x.mean(1)
    if sr != sr_to: x = signal.resample_poly(x, sr_to, sr)
    return x / (np.abs(x).max() + 1e-9)
def bp(x, lo, hi, o=2): return signal.sosfilt(signal.butter(o, [lo, hi], 'bandpass', fs=SR, output='sos'), x)
def lp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'lowpass', fs=SR, output='sos'), x)
def hp(x, f, o=2): return signal.sosfilt(signal.butter(o, f, 'highpass', fs=SR, output='sos'), x)
def place(bus, x, at, g=1.0):
    i = int(round(at * SR)); j0 = 0
    if i < 0: j0, i = -i, 0
    if i >= N: return
    j = min(N, i + len(x) - j0); bus[i:j] += g * x[j0:j0 + j - i]
def ramp(pts): ts, vs = zip(*pts); return np.interp(t, ts, vs)
def pitch(x, f):  # resample-based pitch/time shift
    n = int(len(x) / f); return np.interp(np.linspace(0, len(x) - 1, n), np.arange(len(x)), x)
def fade(x, a=0.005, r=0.05):
    x = x.copy(); na, nr = int(a * SR), int(r * SR); x[:na] *= np.linspace(0, 1, na); x[-nr:] *= np.linspace(1, 0, nr); return x
def seg(x, a, b): return fade(x[int(a * SR):int(b * SR)])

hit, sfx, bed, amb = (np.zeros(N) for _ in range(4))

# ---------------------------------------------------------------- crowd (murmur -> roar), many band voices + vowel layer
def crowd(n, seed):
    r = np.random.default_rng(seed); x = np.zeros(n); k = np.arange(n) / SR
    for _ in range(18):
        lo = r.uniform(220, 900); x += bp(r.standard_normal(n), lo, lo * r.uniform(1.5, 2.8)) * (0.55 + 0.45 * np.sin(2 * np.pi * r.uniform(0.07, 0.5) * k + r.uniform(0, 6)))
    return x / np.abs(x).max()
mur = crowd(N, 3)
vow = np.zeros(N)
for _ in range(30):
    f0 = rng.uniform(160, 360); vib = 1 + 0.015 * np.sin(2 * np.pi * rng.uniform(4, 7) * t + rng.uniform(0, 6))
    vow += signal.sawtooth(2 * np.pi * np.cumsum(f0 * vib) / SR) * rng.uniform(0.4, 1)
vow = bp(vow, 280, 1500); vow /= np.abs(vow).max()
roar = 0.7 * crowd(N, 5) + 0.5 * bp(rng.standard_normal(N), 450, 3000) / 3 + 0.9 * vow
roar /= np.abs(roar).max()
mur_g = ramp([(0, 0.35), (T_HIT1 - 0.3, 0.55), (T_HIT1, 0.0), (R3, 0.0), (R3 + 0.15, 0.45), (5.4, 0.4), (5.7, 0.12), (T_KICK - 0.6, 0.3), (T_KICK, 0.35), (BT0 - 0.2, 0.25), (BT0 + 0.2, 0.05), (BT1, 0.05), (BT1 + 0.3, 0.4), (T_HIT2, 0.0), (DUR, 0.0)])
roar_g = ramp([(0, 0), (T_HIT1, 0), (T_HIT1 + 0.12, 1.0), (H3, 1.0), (H3 + 0.001, 0), (T_HIT2, 0), (T_HIT2 + 0.15, 1.15), (CEL1, 1.1), (20.5, 0.6), (DUR, 0.3)])
bed += mur * mur_g + roar * roar_g
# rewind: the first eruption played backwards (the stadium sucks back in)
r0 = int(T_HIT1 * SR); rr = roar[r0:r0 + int(0.9 * SR)] * 1.0
rr = pitch(rr[::-1], 0.6)[: int(1.45 * SR)]
place(bed, fade(rr * np.linspace(0.2, 1, len(rr)) ** 2, 0.01, 0.1), H3 + 0.02, 0.9)

# ---------------------------------------------------------------- samples
expl = load('814046__qubodup__explosion-from-another-dimension.wav')
impl = load('814047__qubodup__fantasy-implosion.wav')
sword = load('276871__lucabia__sword-in-air.wav')
woosh = load('649445__audiopapkin__cinematic-woosh-sfx-015.wav')
subby = load('238375__stewdio2003__cp_subby_whoosh.aiff')
riser = load('822420__audiopapkin__riser-hit-sfx-120.wav')
wind = load('22331__sleepcircle__wind.ogg')

def boom(f0=160, f1=45, dur=1.6, crack=0.6, sub=0.9):
    n = int(dur * SR); k = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-k / 0.08)
    body = np.tanh(2.5 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-k / 0.4)
    return body + hp(rng.standard_normal(n), 2500) * np.exp(-k / 0.018) * crack + np.sin(2 * np.pi * 44 * k) * np.exp(-k / 0.7) * sub
def kick_thump():  # leather on boot: short click, hollow 180-300 Hz body
    n = int(0.6 * SR); k = np.arange(n) / SR
    return (np.sin(2 * np.pi * (300 * np.exp(-k / 0.03) + 95) * k) * np.exp(-k / 0.09) * 1.2 + hp(rng.standard_normal(n), 1800) * np.exp(-k / 0.006) * 0.9
            + bp(rng.standard_normal(n), 200, 900) * np.exp(-k / 0.03) * 0.6)
def post_ping(dur=2.6):
    n = int(dur * SR); k = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * f * k + rng.uniform(0, 6)) * np.exp(-k / d) * a for f, d, a in
            [(587, 1.1, 1), (1312, 0.8, 0.8), (2247, 0.55, 0.6), (3390, 0.3, 0.45), (4870, 0.16, 0.3), (6600, 0.08, 0.2)])
    return x + hp(rng.standard_normal(n), 2500) * np.exp(-k / 0.008) * 1.2
def net_snap():
    n = int(1.0 * SR); k = np.arange(n) / SR
    sw = bp(rng.standard_normal(n), 900, 7000) * np.minimum(1, k / 0.015) * np.exp(-k / 0.16)
    return sw + 0.6 * bp(rng.standard_normal(n), 120, 600) * np.exp(-k / 0.05)

def heartbeat(at, g, f=56):
    n = int(0.4 * SR); k = np.arange(n) / SR
    hb = np.sin(2 * np.pi * f * k) * np.exp(-k / 0.09) + 0.6 * np.sin(2 * np.pi * (f * 1.7) * k) * np.exp(-k / 0.055)
    place(hit, hb, at, g); place(hit, hb, at + 0.18, 0.6 * g)
def whistle(dur=0.55):  # referee's pea whistle: ~2.9 kHz with the pea's fast warble
    n = int(dur * SR); k = np.arange(n) / SR
    f = 2900 + 120 * np.sin(2 * np.pi * 38 * k) * (0.6 + 0.4 * np.sin(2 * np.pi * 7 * k))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.25 * np.sin(2 * np.pi * np.cumsum(2 * f) / SR) + 0.15 * bp(rng.standard_normal(n), 2400, 4200)
    return x * np.minimum(1, k / 0.02) * np.minimum(1, (dur - k) / 0.06)
def step(g=1.0):
    n = int(0.16 * SR); k = np.arange(n) / SR
    return (bp(rng.standard_normal(n), 120, 1400) * np.exp(-k / 0.025) + 0.8 * np.sin(2 * np.pi * 75 * k) * np.exp(-k / 0.04)) * g

# ---- 0: the hook. frame-0 hit + the ball already screaming past
place(hit, boom(200, 55, 1.4, 0.8, 0.8), 0.0, 0.8)
place(hit, expl[: int(1.5 * SR)] * np.exp(-np.arange(int(1.5 * SR)) / SR / 0.4), 0.0, 0.5)
dop = pitch(sword, 0.72); pk = int(np.argmax(np.abs(dop)))
place(sfx, fade(dop), T_HIT1 - 0.25 - pk / SR, 0.75)
place(sfx, fade(woosh), 0.05 - 0.6, 0.55)
place(sfx, fade(pitch(subby, 0.9)), 0.0, 0.5)
# ---- goal 1: post ping + net snap + eruption
place(sfx, post_ping(), T_HIT1, 0.9)
place(hit, boom(240, 60, 1.6, 1.0, 1.0), T_HIT1, 0.95)
place(hit, expl, T_HIT1, 0.7)
place(sfx, net_snap(), T_HIT1 + 0.08, 0.8)
# ---- H3: dead silence, deep bass hit, tape rewind
place(hit, boom(90, 32, 2.0, 0.2, 1.3), H3, 1.0)
n = int(1.5 * SR); k = np.arange(n) / SR
tape = bp(rng.standard_normal(n), 1800, 9000) * (0.35 + 0.65 * (np.sin(2 * np.pi * (5 + 26 * k) * k) > 0.2))
tape += 0.5 * np.sin(2 * np.pi * np.cumsum(240 + 3200 * (k / 1.5) ** 1.7) / SR) * (0.4 + 0.6 * (np.sin(2 * np.pi * 31 * k) > 0))
place(sfx, fade(tape * np.minimum(1, k / 0.06), 0.01, 0.12), H3 + 0.02, 0.42)
place(sfx, fade(impl[: int(1.45 * SR)]), H3 + 0.05, 0.45)
# ---- R3: the wall. low drone, slow heartbeat; the whistle; the stadium holds its breath
place(hit, boom(70, 30, 2.4, 0.0, 1.0), R3, 0.6)
n = int((T_KICK - R3) * SR); k = np.arange(n) / SR
drone = lp(signal.sawtooth(2 * np.pi * 36.7 * k) + 0.7 * signal.sawtooth(2 * np.pi * 55.0 * k), 220) * np.minimum(1, k / 0.6) * (0.5 + 0.5 * k / k[-1])
place(bed, drone / np.abs(drone).max(), R3, 0.9)
for at in np.arange(R3 + 0.25, 5.7, 0.78): heartbeat(at, 0.55)
place(sfx, whistle(), 5.45, 0.55)
# ---- the run-up: footsteps closing in, heartbeat racing, crowd rising
at, gap = 5.95, 0.42
while at < T_KICK - 0.15:
    place(sfx, step(0.35 + 0.5 * (at - 5.95) / (T_KICK - 5.95)), at, 0.5); heartbeat(at + 0.05, 0.45, 60); at += gap; gap = max(0.27, gap * 0.93)
n = int((T_KICK - 5.8) * SR); k = np.arange(n) / SR
place(sfx, fade(bp(rng.standard_normal(n), 300, 3000) * (k / k[-1]) ** 2), 5.8, 0.25)   # rising air
# ---- the strike
n = int(0.32 * SR); k = np.arange(n) / SR
place(sfx, bp(rng.standard_normal(n), 400, 5000) * np.minimum(1, k / 0.08) * np.exp(-k / 0.1), T_KICK - 0.22, 0.35)  # scrape
place(hit, kick_thump(), T_KICK, 1.0)
place(hit, boom(280, 70, 1.2, 0.9, 0.7), T_KICK, 0.8)
place(sfx, fade(pitch(woosh, 0.6)), T_KICK - 0.8, 0.45)
for at in np.arange(T_KICK + 0.55, BT0, 0.62): heartbeat(at, 0.4)
# ---- BT0-BT1: bullet time. spinning-air texture, deep rumble, a heartbeat that quickens, riser into the release
air_g = ramp([(0, 0), (BT0 - 0.1, 0), (BT0 + 0.4, 1), (BT1 - 0.2, 1), (BT1 + 0.3, 0), (DUR, 0)])
whirr = bp(rng.standard_normal(N), 600, 4000) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.37 * t * 6) ** 2)
amb += 2.0 * (0.35 * whirr / np.abs(whirr).max() + 0.6 * lp(np.tile(wind, 3)[:N], 1200) + 0.5 * lp(rng.standard_normal(N), 90) / 0.05 * 0.02) * air_g
place(hit, boom(120, 40, 1.8, 0.3, 0.9), BT0 + 0.05, 0.55)
at = BT0 + 0.5
while at < BT1 - 0.15:
    g = 0.5 + 0.35 * (at - BT0 - 0.5) / (BT1 - BT0 - 0.65); heartbeat(at, g, 52); at += 0.9 - 0.45 * (at - BT0 - 0.5) / (BT1 - BT0 - 0.65)
rs = riser[int(1.0 * SR):]; place(sfx, fade(rs), BT1 + 0.28 - 5.08, 0.6)
# ---- BT1-: accelerating whoosh, goal 2 (biggest), celebration roar
place(sfx, fade(woosh), BT1 + 0.2 - 2.15, 0.7)
place(sfx, fade(pitch(sword, 0.8)), T_HIT2 - 0.3 - int(np.argmax(np.abs(pitch(sword, 0.8)))) / SR, 0.7)
place(sfx, post_ping(3.0), T_HIT2, 1.0)
place(hit, boom(220, 50, 2.2, 1.0, 1.2), T_HIT2, 1.0)
place(hit, expl, T_HIT2, 0.9)
place(sfx, net_snap(), T_HIT2 + 0.1, 0.9)
place(hit, boom(160, 50, 1.4, 0.5, 0.9), CEL0, 0.5)
# ---- CEL1: the overhead. resolution chord, then a rising whoosh back into frame 0
n = int(4.6 * SR); k = np.arange(n) / SR
chord = sum(np.sin(2 * np.pi * f * k) * a for f, a in [(146.8, 1), (220, 0.8), (293.7, 0.7), (370, 0.5), (440, 0.35)])
chord = lp(chord, 2200) * np.minimum(1, k / 0.25) * np.exp(-k / 2.6)
place(sfx, chord / np.abs(chord).max(), CEL1 + 0.05, 0.35)
place(hit, boom(150, 45, 1.6, 0.4, 0.8), CEL1, 0.45)
rev = fade(pitch(subby, 1.0)[::-1]); place(sfx, rev, DUR - len(rev) / SR + 0.02, 0.6)

# ---------------------------------------------------------------- mix
def norm(x): return x / (np.abs(x).max() + 1e-9)
hit_ = hp(hit, 30); sfx_ = hp(sfx, 70); bed_ = hp(bed, 110); amb_ = hp(amb, 60)
duck = 1 - 0.5 * norm(lp(np.abs(hit_), 6))
mix = 1.0 * hit_ + 0.85 * sfx_ + 0.5 * bed_ * duck + 0.45 * amb_
mix[:200] *= np.linspace(0, 1, 200)
mix = np.tanh(1.5 * mix / np.abs(mix).max())
st = np.stack([mix, mix], 1)
w = hp(0.06 * (bed_ + amb_), 250); st[:, 0] += w; st[:, 1] -= w
st /= np.abs(st).max() / 0.89
sf.write(sys.argv[2], st.astype(np.float32), SR, subtype='PCM_24')
print('wrote', sys.argv[2])
