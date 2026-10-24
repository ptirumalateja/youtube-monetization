"""Check Your Friend's Bag: sound mix (numpy buses).

python3 mix.py timing.json out.wav
"Breath and piano" family, linked to Part 1 by its wind and stone sounds: Part 1's wind cuts out on
frame 0 and a soft piano comes back; the friend's heavy breathing and a heartbeat under the X-ray;
a descending chime as each white step lights on the way down; small cloth taps; the first stone clink
for the blue friend; rising clinks through the time-lapse; a held breath; one warm hit for the bridge;
a D major close with a bell. Stone thuds and the impact are the ElevenLabs files from One Step a Day;
everything else is synthesised here.
"""
import json, os, subprocess, sys, wave
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(sys.argv[1]))
OUT = sys.argv[2]
DUR = TL['dur']
NS = int(DUR * SR)
t = np.arange(NS) / SR
rng = np.random.default_rng(11)


def load(name):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f'{HERE}/sfx/{name}.mp3', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).astype(np.float64)
    i = max(0, int(np.argmax(np.abs(x) > 0.25 * np.abs(x).max())) - int(0.004 * SR))
    x = x[i:].copy()
    f = int(0.03 * SR)
    x[-f:] *= np.linspace(1, 0, f)
    return x / (np.abs(x).max() + 1e-9)


def place(bus, x, at, g=1.0):
    i = int(at * SR)
    if i >= NS or i + len(x) <= 0:
        return
    a, b = max(0, i), min(NS, i + len(x))
    bus[a:b] += g * x[a - i:b - i]


def lp(x, fc):
    """one-pole low-pass; fc may vary per sample"""
    a = np.exp(-2 * np.pi * np.broadcast_to(np.asarray(fc, float), x.shape) / SR)
    y = np.empty_like(x)
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def hp(x, fc):
    return x - lp(x, fc)


def sstep(a, b, x):
    u = np.clip((x - a) / (b - a), 0, 1)
    return u * u * (3 - 2 * u)


def reverb(x, sec=2.2, wet=0.3, seed=3):
    n = int(sec * SR)
    r = np.random.default_rng(seed)
    ir = r.standard_normal(n) * np.exp(-np.linspace(0, 7, n))
    ir = lp(ir, 4500)
    ir /= np.sqrt((ir ** 2).sum())
    y = np.fft.irfft(np.fft.rfft(x, len(x) + n) * np.fft.rfft(ir, len(x) + n))[:len(x)]
    return x + wet * y


def note(f, dur=3.0, vel=1.0):
    """soft felt-piano note: slightly stretched partials, hammer thump, two-stage decay"""
    n = int(dur * SR)
    tt = np.arange(n) / SR
    y = np.zeros(n)
    for k, a in enumerate([1, 0.45, 0.22, 0.12, 0.06, 0.03], 1):
        fk = f * k * (1 + 0.0004 * k * k)
        dec = 1.6 / (1 + 0.5 * k)
        y += a * np.sin(2 * np.pi * fk * tt + k) * (0.7 * np.exp(-tt / (dec * 0.35)) + 0.3 * np.exp(-tt / (dec * 2.5)))
    y *= np.minimum(1, tt / 0.006)
    thump = rng.standard_normal(int(0.02 * SR)) * np.exp(-np.linspace(0, 8, int(0.02 * SR)))
    y[:len(thump)] += 0.08 * lp(thump, 900)
    y[-int(0.05 * SR):] *= np.linspace(1, 0, int(0.05 * SR))
    return lp(y, 2600) * vel


def hz(name):
    names = {'C': -9, 'D': -7, 'E': -5, 'F': -4, 'F#': -3, 'G': -2, 'A': 0, 'Bb': 1, 'B': 2}
    return 440 * 2 ** ((names[name[:-1]] + 12 * (int(name[-1]) - 4)) / 12)


def clink(f0=1900, g=1.0, body=0.0):
    """stone on stone: a few inharmonic modes + a short low knock"""
    n = int(0.6 * SR)
    tt = np.arange(n) / SR
    y = sum(a * np.sin(2 * np.pi * f0 * r * tt) * np.exp(-tt / d) for r, a, d in [(1, 1, 0.09), (1.47, 0.6, 0.06), (2.09, 0.4, 0.04), (2.76, 0.25, 0.03)])
    knock = np.sin(2 * np.pi * 180 * tt * (1 - 0.3 * tt)) * np.exp(-tt / 0.05)
    nz = lp(rng.standard_normal(n), 6000) * np.exp(-tt / 0.008)
    return g * (0.5 * y + body * knock + 0.25 * nz)


thudA, thudB, hitA = load('el_thud2'), load('el_thud3'), load('el_hit1')
piano = np.zeros(NS); breath = np.zeros(NS); heart = np.zeros(NS); sfx = np.zeros(NS)
wind = np.zeros(NS); hit = np.zeros(NS); air = np.zeros(NS)

# ---------- 0-3 s: Part 1's wind cuts out, the piano comes back ----------
n = rng.standard_normal(NS)
gust = 0.6 + 0.4 * np.sin(2 * np.pi * 0.37 * t + 1)
w = hp(lp(n, 700 + 500 * gust), 150) * gust
wind += w * (1 - sstep(0.04, 0.32, t)) * 0.9             # Part 1's wind, stopping
wind += w * 0.18 * sstep(17.8, 19.0, t)                  # outside air again on the payoff
# Part 1's lamp hum carries across the join (soft, inside the phone band)
hum = np.sin(2 * np.pi * 110 * t) + 0.3 * np.sin(2 * np.pi * 220 * t)          # Part 1's hum (sound.py: 110 + 220 Hz)
# Part 1's D major pad, carried over and released in the first 1.5 s
pad = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate([110, 146.8, 185, 220, 293.7]))
air += 0.012 * lp(pad, 2500) * (1 - sstep(0.1, 1.5, t))
air += 0.006 * hum * (0.85 + 0.15 * np.sin(2 * np.pi * 5.3 * t)) * (1 - 0.7 * sstep(6.0, 7.0, t))
for at, nm, v in [(0.2, 'D4', 0.9), (0.2, 'A3', 0.5), (1.25, 'F4', 0.75), (2.3, 'E4', 0.6), (2.3, 'A3', 0.4)]:
    place(piano, note(hz(nm), 3.5, v), at)

# the friend's breathing: heavy, slow, under everything until he is helped
def breath_cycle(period, strength):
    n = int(period * SR)
    tt = np.arange(n) / SR / period
    env = np.where(tt < 0.4, np.sin(np.pi * tt / 0.8) ** 2, np.exp(-(tt - 0.4) * 6) * 1.0)
    src = rng.standard_normal(n)
    inh = hp(lp(src, 1800), 500) * (tt < 0.4)
    exh = hp(lp(src, 1100), 250) * (tt >= 0.4)
    return strength * env * (0.7 * inh + 1.0 * exh)
bt = 0.1
while bt < 13.5:
    per = 1.9 if bt < 5.5 else (1.4 if bt < 6.3 else 2.3)
    s = 0.25 + 0.75 * sstep(2.9, 3.6, bt) - 0.55 * sstep(10.3, 12.5, bt)
    place(breath, breath_cycle(per, s), bt)
    bt += per

# ---------- 3-6 s: the drop and the X-ray ----------
dr = lp(rng.standard_normal(NS), 400 + 3500 * sstep(2.95, 3.3, t) * (1 - sstep(3.3, 3.6, t)))
air += 0.35 * hp(dr, 180) * sstep(2.95, 3.2, t) * (1 - sstep(3.35, 3.6, t))
# X-ray switch: a glassy shimmer up and a low swell
xs = TL['xray']
sh = sum(np.sin(2 * np.pi * f * t) for f in (1320, 1980, 2640)) * sstep(xs - 0.02, xs + 0.06, t) * np.exp(-np.clip(t - xs, 0, None) / 0.5)
air += 0.03 * sh
# heartbeat: lub-dub, speeding up to the collapse, gone once he is helped
hb = 3.5
while hb < 10.4:
    bpm = 72 + 30 * sstep(3.5, 5.0, hb) - 25 * sstep(6.0, 9.0, hb)
    g = (0.6 + 0.4 * sstep(3.5, 4.2, hb)) * (1 - 0.6 * sstep(6.0, 6.5, hb)) * (1 - sstep(9.5, 10.4, hb))
    for k, (off, a) in enumerate([(0, 1.0), (0.17, 0.65)]):
        n_ = int(0.18 * SR); tt = np.arange(n_) / SR
        beat = np.sin(2 * np.pi * (62 if k == 0 else 72) * tt * (1 - 0.6 * tt)) * np.exp(-tt / 0.05) + 0.4 * np.sin(2 * np.pi * 130 * tt) * np.exp(-tt / 0.02)
        place(heart, beat * a * g, hb + off)
    hb += 60 / bpm
# the bag jiggles: small stone rattles
for k in range(26):
    at = 3.7 + k * 0.065 + rng.random() * 0.03
    if at < 5.4:
        place(sfx, clink(1100 + 500 * rng.random(), 0.12, 0.3), at)
# he drops to his knees
place(sfx, thudA * 0.9, TL['collapse'][1] - 0.12)
place(sfx, thudB * 0.6, TL['collapse'][1] - 0.02)

# ---------- 6-10 s: down his own stairs, each step lights with a chime ----------
desc = ['A5', 'F#5', 'E5', 'D5', 'B4', 'A4', 'F#4']
for i, p in enumerate(TL['flares']):      # step 7 lights as he sets off, then 6..1 as he lands on each
    if i:
        place(sfx, thudB * 0.32, p - 0.01)
    place(piano, note(hz(desc[i]), 1.8, 0.33), p)
for at, nm, v in [(6.4, 'D3', 0.5), (8.7, 'B2', 0.45)]:
    place(piano, note(hz(nm), 4.0, v), at)
for k in range(4):  # footsteps to his friend
    place(sfx, lp(rng.standard_normal(int(0.08 * SR)) * np.exp(-np.linspace(0, 9, int(0.08 * SR))), 900), TL['walk'][0] + 0.15 + k * 0.27, 0.35)

# ---------- 10-14 s: the help ----------
for k in range(2):  # two light taps on the shoulder
    place(sfx, lp(rng.standard_normal(int(0.05 * SR)) * np.exp(-np.linspace(0, 10, int(0.05 * SR))), 1500), TL['tap'][0] + 0.32 + k * 0.29, 0.5)
ru = lp(rng.standard_normal(NS), 2500) * sstep(TL['bagOff'][0], TL['bagOff'][0] + 0.1, t) * (1 - sstep(TL['bagOff'][1] - 0.1, TL['bagOff'][1] + 0.1, t))
sfx += 0.10 * hp(ru, 600)
place(sfx, thudB * 0.4, TL['bagOff'][1])
sc = lp(rng.standard_normal(NS), 1400) * sstep(TL['lift'][0], TL['lift'][0] + 0.05, t) * (1 - sstep(TL['lift'][1] - 0.1, TL['lift'][1], t))
sfx += 0.07 * hp(sc, 300)
for at, nm, v in [(10.35, 'G3', 0.5), (10.35, 'D4', 0.45), (11.0, 'B4', 0.5), (12.15, 'A4', 0.45), (12.15, 'E4', 0.35)]:
    place(piano, note(hz(nm), 3.5, v), at)
# the first clink for the blue guy (step 1, ALONE)
p1 = TL['place'][0]
place(hit, clink(1760, 1.0, 0.8), p1)
place(hit, thudA * 0.7, p1)
for nm, v in [('D3', 0.55), ('A3', 0.5), ('D4', 0.5), ('F#4', 0.45)]:
    place(piano, note(hz(nm), 4.0, v), p1 + 0.02)

# ---------- 14-18 s: building together ----------
lo = TL['load']
for k in range(16):  # rocks fly into the white bag
    place(sfx, clink(1300 + 900 * rng.random(), 0.16, 0.2), lo[0] + 0.05 + k * (lo[1] - lo[0]) / 16)
scale = ['E5', 'F#5', 'A5', 'B5', 'D6', 'E6']
for i, p in enumerate(TL['place'][1:]):
    place(sfx, clink(1700 * 2 ** (i / 14), 0.8, 0.6), p)
    place(sfx, thudA * 0.35, p)
    place(piano, note(hz(scale[i]), 1.6, 0.32), p)
for at, nm in [(14.45, 'D3'), (15.3, 'B2'), (16.2, 'G2'), (17.05, 'A2')]:
    place(piano, note(hz(nm), 3.0, 0.45), at)
    place(piano, note(hz(nm) * 2, 3.0, 0.25), at)

# ---------- 18 s: held breath, then the bridge ----------
B = TL['bridge']
hold = 1 - 0.93 * sstep(B - 0.6, B - 0.5, t) * (1 - sstep(B - 0.02, B, t))
swell = lp(rng.standard_normal(NS), 1500 + 4000 * sstep(B - 0.55, B, t)) * sstep(B - 0.5, B - 0.01, t) ** 2 * (t < B)
air += 0.08 * hp(swell, 400)
place(hit, clink(1500, 1.1, 1.0), B)
place(hit, hitA * 0.75, B)
gl = int(4.5 * SR); tg = np.arange(gl) / SR
gong = sum(a * np.sin(2 * np.pi * f * tg) * np.exp(-tg / d) for f, a, d in [(146.8, 0.8, 1.5), (220, 0.6, 1.3), (293.7, 0.9, 1.4), (370, 0.5, 1.1), (587, 0.25, 0.7)])
gong *= np.minimum(1, tg / 0.004)
place(hit, gong / np.abs(gong).max(), B, 0.55)
sub = np.sin(2 * np.pi * 52 * tg[:int(1.0 * SR)]) * np.exp(-tg[:int(1.0 * SR)] / 0.3)
place(hit, sub, B, 0.45)
for nm, v in [('D3', 0.6), ('A3', 0.5), ('D4', 0.55), ('F#4', 0.5), ('A4', 0.45), ('D5', 0.4)]:
    place(piano, note(hz(nm), 3.5, v), B + 0.03)
# the empty bag lands below (fall time from the scene: 0.5 s after the drop)
place(sfx, lp(thudB, 600) * 0.5, TL['bagLand'])
# end card bell
bl = int(2.5 * SR); tb = np.arange(bl) / SR
bell = sum(a * np.sin(2 * np.pi * f * tb) * np.exp(-tb / d) for f, a, d in [(1174.7, 1, 0.9), (1761, 0.4, 0.6), (2349, 0.25, 0.4)])
place(air, reverb(bell * 0.25, 2, 0.5), 19.45, 0.5)

# ---------- master ----------
piano = reverb(piano, 2.8, 0.45, 5)
hit = reverb(hit, 2.4, 0.35, 7)
duck = 1 - 0.45 * np.exp(-np.clip(t - B, 0, None) / 0.5) * (t >= B)
mix = (piano * 0.5 + breath * 0.4 + heart * 1.1 + sfx * 0.6 + wind * 0.22) * hold * duck + air + hit * 0.85
mix = hp(mix, 40)
st = np.stack([mix, mix], 1)
st[:, 0] += 0.06 * lp(wind, 2000) + 0.05 * piano
st[:, 1] -= 0.06 * lp(wind, 2000) - 0.05 * piano
st /= np.abs(st).max()
st = np.tanh(st * 1.3) / np.tanh(1.3) * 0.89
e = int(0.002 * SR); st[:e] *= np.linspace(0, 1, e)[:, None]; st[-e:] *= np.linspace(1, 0, e)[:, None]
wv = wave.open(OUT, 'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
wv.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes()); wv.close()
print('wrote', OUT, DUR)
