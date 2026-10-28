"""Sound for One Came (20 s), all synthesised: rain on the window, phone buzzes, card ticks, a low room drone, three knocks,
the warm door swell, footsteps, the phone flipped onto the quilt, and a soft piano that only arrives once someone came.
The face-down buzz at 19.75 s is the loop seam back to frame 0.   python3 mix.py OUT.wav"""
import sys, wave, numpy as np
SR = 48000; T = 20.0; N = int(SR * T); t = np.arange(N) / SR
rng = np.random.default_rng(7)
def db(x): return 10 ** (x / 20)
def lp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** 4), len(x))
def hp(x, fc):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); r = (f / fc) ** 2; return np.fft.irfft(X * r / np.sqrt(1 + r ** 2), len(x))
def env_ad(n, a, d): e = np.exp(-np.arange(n) / SR / d); k = int(a * SR); e[:k] *= np.linspace(0, 1, k) if k else 1; return e
def add(bus, x, at, g=0.0, pan=0.0):
    a = int(at * SR); x = x[:max(0, N - a)]; n = len(x)
    bus[a:a + n, 0] += x * db(g) * (1 - max(0, pan)); bus[a:a + n, 1] += x * db(g) * (1 + min(0, pan))
def curve(points):  # piecewise-linear gain in dB over time
    xs, ys = zip(*points); return db(np.interp(t, xs, ys))
out = np.zeros((N, 2))

# rain: two decorrelated filtered-noise layers + random drops on the glass; it cuts out for the knock, comes back softer
rain = np.zeros((N, 2))
for ch in range(2):
    n = rng.standard_normal(N); rain[:, ch] = hp(lp(n, 5200), 400) * 0.22 + lp(rng.standard_normal(N), 900) * 0.10
drops = np.zeros(N)
for at in rng.uniform(0, T, 520):
    k = int(at * SR); L = int(0.03 * SR); seg = rng.standard_normal(L) * env_ad(L, 0.0005, 0.006)
    drops[k:k + L] += seg[:max(0, N - k)] * rng.uniform(0.05, 0.25)
rain += hp(drops, 1500)[:, None] * 0.6
out += rain * curve([(0, -20), (8.9, -19), (9.0, -40), (9.6, -40), (10.2, -24), (15, -26), (18, -30), (20, -21)])[:, None]

# room drone (lonely part only): low fifth with slow beating
dr = (np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 82.6 * t) + 0.3 * np.sin(2 * np.pi * 110.4 * t)) * (0.8 + 0.2 * np.sin(2 * np.pi * 0.23 * t))
out += (dr * curve([(0, -30), (6.5, -27), (8.9, -24), (9.0, -60), (20, -60)]))[:, None]

# phone buzz: 175 Hz rattle in 2 pulses
def buzz(muffle=False):
    L = int(0.42 * SR); tt = np.arange(L) / SR
    sq = np.sign(np.sin(2 * np.pi * 175 * tt)) * 0.5 + np.sin(2 * np.pi * 350 * tt) * 0.3
    gate = ((tt < 0.16) | ((tt > 0.22) & (tt < 0.38))).astype(float); gate = lp(gate, 60)
    x = lp(sq * gate, 900 if muffle else 3000); return x / np.abs(x).max()
BUZZ = [0.0, 1.25] + [2.6 + i * 0.6 for i in range(6)]
for i, b in enumerate(BUZZ): add(out, buzz(), b, -18 if i < 2 else -20, pan=0.2)
add(out, buzz(True), 19.75, -14, pan=0.2)
# card pop: a soft glassy tick on each message
for i in range(6):
    L = int(0.12 * SR); tt = np.arange(L) / SR
    add(out, np.sin(2 * np.pi * (1800 + 120 * i) * tt) * env_ad(L, 0.001, 0.03), 2.62 + i * 0.6, -24, pan=0.15)

# three knocks: a wooden thump (low sine drop + filtered noise click)
def knock():
    L = int(0.35 * SR); tt = np.arange(L) / SR
    body = np.sin(2 * np.pi * (95 + 60 * np.exp(-tt / 0.02)) * tt) * env_ad(L, 0.001, 0.09)
    click = lp(rng.standard_normal(L), 2500) * env_ad(L, 0.0005, 0.012)
    return body + click * 0.6
for k, at in enumerate([9.0, 9.2, 9.42]): add(out, knock(), at, -4 + (k == 2) * 1, pan=0.45)
# door opens: a warm air swell
sw = lp(rng.standard_normal(int(1.6 * SR)), 700) * np.sin(np.linspace(0, np.pi, int(1.6 * SR))) ** 2
add(out, sw / np.abs(sw).max(), 9.45, -22, pan=0.4)
# footsteps behind the bed, then the mattress takes his weight
for k, at in enumerate([10.55, 10.9, 11.25]):
    L = int(0.2 * SR); add(out, lp(rng.standard_normal(L), 400) * env_ad(L, 0.004, 0.05), at, -12, pan=0.35 - k * 0.1)
L = int(0.5 * SR); add(out, lp(rng.standard_normal(L), 250) * env_ad(L, 0.02, 0.15), 11.8, -16, pan=0.1)
# the phone turned face down onto the quilt: a soft clack
L = int(0.15 * SR); add(out, lp(rng.standard_normal(L), 1800) * env_ad(L, 0.001, 0.02), 13.32, -16, pan=0.15)

# piano: additive tones with hammer and decay; one note when he sits, one when the phone goes down, then the chords
def piano(f, dur=4.0):
    L = int(dur * SR); tt = np.arange(L) / SR; x = np.zeros(L)
    for h, a in enumerate([1, 0.45, 0.22, 0.12, 0.06], 1): x += a * np.sin(2 * np.pi * f * h * tt * (1 + 0.0004 * h)) * np.exp(-tt * (0.9 + 0.6 * h))
    x *= np.minimum(1, tt / 0.004); return x / 1.8
def note(n): return 440 * 2 ** ((n - 69) / 12)
for at, ns, g in [(11.9, [64], -18), (13.35, [62], -19), (15.4, [53, 57, 60, 64], -17), (16.9, [48, 55, 60, 64], -16), (18.4, [45, 52, 57, 60, 64], -16)]:
    for j, n in enumerate(ns): add(out, piano(note(n), 4.5), at + j * 0.035, g, pan=(j - len(ns) / 2) * 0.12)
# warm pad under the payoff (detuned saws, low-passed), fading out before the loop buzz
pad = np.zeros(N)
for n in [53, 57, 60, 48, 55, 64]:
    for d in (-0.15, 0.15): pad += ((t * note(n) * (1 + d / 100)) % 1 * 2 - 1)
pad = lp(pad, 1100) / 12
out += (pad * curve([(0, -80), (15.0, -80), (16.5, -26), (19.2, -27), (19.7, -60), (20, -80)]))[:, None]

out = out / np.abs(out).max() * 0.9
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype('<i2').tobytes())
