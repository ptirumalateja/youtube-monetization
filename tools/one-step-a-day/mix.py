"""One Step a Day: sound mix (numpy buses).

python3 mix.py timing.json out.wav
Sound family "stone and breath": real stone thuds (ElevenLabs SFX) on every step he sets down, which
blur into a ticking whir while the days fly by; ElevenLabs crowd laughter that thins out as the stair
rises; wind that grows with height; a held breath before day 365; one stone-and-gong hero hit; a
warm chord over the reveal; a dive whoosh home and a rising tone that links the loop back to frame 0.
"""
import json, os, subprocess, sys
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
timing = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
DUR = timing['dur']
NS = int(DUR * SR)
rng = np.random.default_rng(7)


def load(name):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{HERE}/sfx/{name}.mp3', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def onset(x, thr=0.25):
    return int(np.argmax(np.abs(x) > thr * np.abs(x).max()))


def trim(x, pre=0.004, length=None):
    i = max(0, onset(x) - int(pre * SR))
    y = x[i:] if length is None else x[i:i + int(length * SR)]
    fade = int(0.03 * SR)
    y = y.copy()
    y[-fade:] *= np.linspace(1, 0, fade)
    return y / (np.abs(y).max() + 1e-9)


def place(bus, x, t, g=1.0):
    i = int(t * SR)
    if i >= NS or i + len(x) <= 0:
        return
    a, b = max(0, i), min(NS, i + len(x))
    bus[a:b] += g * x[a - i:b - i]


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * np.asarray(fc) / SR)
    y = np.empty_like(x)
    s = 0.0
    if np.ndim(a) == 0:
        a = np.full(len(x), a)
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def hp(x, fc):
    return x - onepole_lp(x, fc)


def sstep(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1)
    return u * u * (3 - 2 * u)


def reverb(x, sec=2.2, wet=0.3):
    n = int(sec * SR)
    ir = rng.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir = onepole_lp(ir, 5000)
    ir /= np.sqrt((ir ** 2).sum())
    y = np.fft.irfft(np.fft.rfft(x, len(x) + n) * np.fft.rfft(ir, len(x) + n))[:len(x)]
    return x + wet * y


t = np.arange(NS) / SR
place_t = np.array(timing['place'])

# ---------- sources ----------
thudA = trim(load('el_thud2'), length=0.7)
thudB = trim(load('el_thud3'), length=0.9)
laugh4, laugh2, laugh1 = load('el_laugh4'), load('el_laugh2'), load('el_laugh1')
hitA, hitB = trim(load('el_hit1')), trim(load('el_hit3'))

# ---------- buses ----------
stone = np.zeros(NS); tick = np.zeros(NS); crowd = np.zeros(NS); bed = np.zeros(NS)
wind = np.zeros(NS); hit = np.zeros(NS); air = np.zeros(NS)

# every step set down makes a sound with a visual cause
gaps = np.diff(np.concatenate([[-1.0], place_t]))
tick_g = trim(onepole_lp(rng.standard_normal(int(0.03 * SR)) * np.exp(-np.linspace(0, 9, int(0.03 * SR))), 2500))
for k, (pt, gap) in enumerate(zip(place_t, gaps)):
    if k == len(place_t) - 1:
        continue  # day 365 belongs to the hero hit
    slow = np.clip((gap - 0.06) / 0.25, 0, 1)  # 1 = individual thuds, 0 = whir
    if slow > 0.02:
        place(stone, thudA if k % 2 == 0 else thudB, pt - 0.004, (1.5 if k == 0 else 0.9) * slow * (0.85 + 0.15 * rng.random()))
    # pitch climbs with the stair: tick resampled shorter as height grows
    rate = 1.0 + 1.4 * (k / len(place_t))
    g = np.interp(np.arange(0, len(tick_g) - 1, rate), np.arange(len(tick_g)), tick_g)
    place(tick, g, pt, 0.9 * (1 - slow) + 0.15 * slow)
stone = hp(stone, 70)

# crowd laughter: bursts on the first stones, thinning out as the stair rises (scene: laugh = 1 - sstep(3.6, 7.2))
place(crowd, laugh4, 0.06, 1.0)
place(crowd, laugh1, 0.85, 0.55)
place(crowd, laugh2, 2.2, 0.8)
place(crowd, laugh4[::-1][: int(2.5 * SR)][::-1] * np.linspace(0.2, 1, int(2.5 * SR)), 3.6, 0.55)
crowd *= 1 - sstep(3.4, 7.0, t)
crowd = hp(crowd, 110)

# bed: a slowly opening D drone, harmonics kept inside the phone band (147-600 Hz)
f0 = 146.83
lfo = 0.5 + 0.5 * np.sin(2 * np.pi * 0.21 * t)
drone = sum(a * np.sin(2 * np.pi * f0 * m * t + p) for m, a, p in [(1, 1, 0), (1.5, 0.55, 1), (2, 0.4, 2), (3, 0.18, 0.5), (1.003, 0.6, 3)])
drone = onepole_lp(drone, 300 + 2200 * sstep(1.5, 10.8, t))
bed += drone * (0.012 + 0.03 * sstep(2, 10.6, t)) * (0.85 + 0.15 * lfo)
# shepard-like riser that follows the climb (2.4 to 11.05 s)
ph = np.zeros(NS)
for i in range(3):
    fr = 220 * 2 ** ((((t - 2.4) / 4.2) + i / 3) % 1 * 1.0 + 0) * 1.0
    w = np.sin(np.pi * ((((t - 2.4) / 4.2) + i / 3) % 1))
    ph += w * np.sin(2 * np.pi * np.cumsum(fr) / SR)
bed += 0.018 * ph * sstep(2.4, 6.0, t) * (1 - sstep(10.7, 11.05, t))

# wind grows with height; gusts; ducked to a whisper for the held breath
n = rng.standard_normal(NS)
gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.37 * t + 1) * np.sin(2 * np.pi * 0.13 * t)
w1 = onepole_lp(n, 380 + 900 * gust * sstep(4, 12, t))
w1 = hp(w1, 150)
wind += w1 * (0.05 + 0.55 * sstep(5, 11, t)) * gust
wind *= 1 - 0.85 * sstep(11.0, 11.15, t) * (1 - sstep(11.95, 12.05, t))
wind *= 1 - 0.45 * sstep(12.6, 13.6, t)
wind *= 1 - sstep(15.8, 16.6, t) * 0.7
wind *= 2.2

# held breath: everything except a thin swell drops out 11.05-12.0
hold = 1 - 0.97 * sstep(11.0, 11.12, t) * (1 - sstep(11.98, 12.0, t))
swell = onepole_lp(rng.standard_normal(NS), 1800 + 5000 * sstep(11.1, 12.0, t)) * sstep(11.15, 11.98, t) ** 2.2 * (t < 12.0)
air += 0.12 * hp(swell, 400)

# hero hit at day 365 (12.0 s): stone thud + ElevenLabs impact + synth gong + short sub, vacuum 60 ms before
T0 = place_t[-1]
place(hit, thudA, T0, 1.0)
place(hit, hitA, T0, 0.9)
place(hit, hitB, T0 + 0.01, 0.6)
gl = int(4.5 * SR); tg = np.arange(gl) / SR
gong = sum(a * np.sin(2 * np.pi * f * tg) * np.exp(-tg / d) for f, a, d in [(98, 0.5, 1.1), (196, 1.0, 1.5), (293.7, 0.6, 1.2), (392, 0.5, 1.0), (587, 0.25, 0.7), (784.7, 0.15, 0.5)])
gong *= np.minimum(1, tg / 0.004)
place(hit, gong / np.abs(gong).max(), T0, 0.8)
sub = np.sin(2 * np.pi * 50 * tg[: int(1.1 * SR)] * (1 - 0.25 * tg[: int(1.1 * SR)])) * np.exp(-tg[: int(1.1 * SR)] / 0.35)
place(hit, sub, T0, 0.6)
hit = reverb(hit, 2.6, 0.35)

# reveal chord (D major, over the top-down shot) and a bell when the end line lands
cl = int(5.5 * SR); tc = np.arange(cl) / SR
chord = sum(a * np.sin(2 * np.pi * f * tc + i) for i, (f, a) in enumerate([(146.8, 1), (220, 0.7), (293.7, 0.6), (370, 0.45), (440, 0.3)]))
chord *= sstep(0, 1.4, tc) * (1 - sstep(3.2, 5.5, tc))
place(bed, onepole_lp(chord, 1400) / 5, 12.45, 0.14)
bl = int(2.5 * SR); tb = np.arange(bl) / SR
bell = sum(a * np.sin(2 * np.pi * f * tb) * np.exp(-tb / d) for f, a, d in [(1174.7, 1, 0.9), (1761, 0.4, 0.6), (2349, 0.25, 0.4)])
place(air, reverb(bell * 0.3, 2, 0.5), 13.55, 0.5)

# dive home (15.9-17.0): falling whoosh, then a rising tone into frame 0 (the loop)
dv = (t > 15.75) & (t < 17.2)
wh = onepole_lp(rng.standard_normal(NS), 600 + 5000 * sstep(15.8, 16.5, t) * (1 - sstep(16.5, 17.1, t)))
air += 0.3 * hp(wh, 200) * sstep(15.8, 16.45, t) * (1 - sstep(16.6, 17.15, t)) * dv
rise = np.sin(2 * np.pi * np.cumsum(220 * 2 ** (sstep(16.9, 17.5, t))) / SR) * sstep(16.95, 17.5, t) ** 2
air += 0.10 * rise
# the leader's first stone lands on frame 0 of the next loop (frame-0 thud is the opening thud)

# ---------- master ----------
duck = 1 - 0.6 * np.exp(-np.clip(t - T0, 0, None) / 0.6) * (t >= T0)
mix = (stone * 0.55 + tick * 0.5 + crowd * 0.5) * hold + (bed + wind * 0.25) * hold * duck + air + hit * 0.9
mix = hp(mix, 35)
st = np.stack([mix, mix], 1)
# a little width: crowd and wind decorrelated
st[:, 0] += 0.08 * onepole_lp(wind, 2000) * hold
st[:, 1] -= 0.08 * onepole_lp(wind, 2000) * hold
st /= np.abs(st).max()
st = np.tanh(st * 1.4) / np.tanh(1.4)
st *= 0.89
# fades at the very edges only (2 ms) so the loop stays tight
e = int(0.002 * SR); st[:e] *= np.linspace(0, 1, e)[:, None]; st[-e:] *= np.linspace(1, 0, e)[:, None]
import wave
w = wave.open(OUT, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); w.close()
print('wrote', OUT, DUR)
