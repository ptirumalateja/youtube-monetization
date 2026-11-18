# Action-synced SFX only (no music, no ambient bed). Event times mirror scene.js. -> sfx.wav (stereo)
import numpy as np, wave, sys
SR = 48000; HOOK = .7; DUR = 14.8 + HOOK; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N)
rs = np.random.RandomState(5)

def biquad(x, kind, f, q=.7):
    w = 2 * np.pi * f / SR; a = np.sin(w) / (2 * q); c = np.cos(w)
    if kind == 'lp': b = [(1 - c) / 2, 1 - c, (1 - c) / 2]
    elif kind == 'hp': b = [(1 + c) / 2, -(1 + c), (1 + c) / 2]
    else: b = [a, 0, -a]
    A = [1 + a, -2 * c, 1 - a]; b = [v / A[0] for v in b]; a1, a2 = A[1] / A[0], A[2] / A[0]
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        v = b[0] * x[i] + b[1] * x1 + b[2] * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x[i], y1, v; y[i] = v
    return y

def place(sig, t, gain=1., pan=0.):
    i = int((t + HOOK) * SR); j = min(N, i + len(sig))
    if i >= N or j <= max(i, 0): return
    s = sig[:j - i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414; R[i:j] += s * np.sqrt((1 + pan) / 2) * 1.414

def env(n, att, dec):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(att, 1e-4)) * np.exp(-t / dec)

def whoosh(d=.32, f=900):
    n = int(d * SR); x = biquad(rs.randn(n), 'bp', f, .8)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2.5
    return x * e * 1.2

def thunk(f=170, d=.22):  # wood landing
    n = int(d * SR); t = np.arange(n) / SR
    body = (np.sin(2 * np.pi * f * t) + .5 * np.sin(2 * np.pi * f * 2.3 * t) + .25 * np.sin(2 * np.pi * f * 3.9 * t)) * env(n, .001, .045)
    click = biquad(rs.randn(n), 'bp', 2200, 1.2) * env(n, .0005, .006)
    return body * .8 + click * .6

def fwoomp(d=.7, big=1.):  # fire catching the new wood
    n = int(d * SR); t = np.arange(n) / SR
    x = biquad(rs.randn(n), 'lp', 500 + 400 * big)
    e = np.minimum(1, t / .05) * np.exp(-t / (.18 + .25 * big))
    sub = np.sin(2 * np.pi * (55 + 30 * np.exp(-t * 8)) * t) * np.exp(-t / .25) * .6 * big
    return (x * 2.2 + sub) * e

def roar(d=1.6):  # big flare when the seat log goes in
    n = int(d * SR); t = np.arange(n) / SR
    x = biquad(rs.randn(n), 'lp', 900) * 2.5 + biquad(rs.randn(n), 'bp', 2500, .7) * .5
    e = np.minimum(1, t / .12) * np.exp(-np.maximum(0, t - .25) / .45)
    sub = np.sin(2 * np.pi * 48 * t) * np.exp(-t / .5) * .9
    return (x + sub) * e

def pop(f0=1100, f1=520, d=.06):  # speech bubble
    n = int(d * SR); t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t * 60)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .018)

def tick(f=2600, d=.025):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * .6 + biquad(rs.randn(n), 'hp', 3000) * .4) * env(n, .0003, .004)

def sizzle(d=1.1):  # fire going out
    n = int(d * SR); t = np.arange(n) / SR
    x = biquad(rs.randn(n), 'hp', 3500) * .7 + biquad(rs.randn(n), 'bp', 1200, .9) * .5
    e = np.minimum(1, t / .03) * np.exp(-t / .35)
    return x * e

def low_hit(d=2.2):  # "you've changed" weight
    n = int(d * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * 44 * t) + .4 * np.sin(2 * np.pi * 88 * t + .3)
    return s * np.minimum(1, t / .01) * np.exp(-t / .6)

def pile_tick():  # a log added to the pile
    return thunk(260, .12) * .5

FIRE_PAN = .55
# ---- top lane (louder, it's the story)
picksA, picksB = [.15, .62, 1.08], [.0, .45, .9]
for t0 in picksA + picksB:
    place(whoosh(.3, 800 + rs.rand() * 300), t0 + .2, .35, .1)
    place(thunk(150 + rs.rand() * 60), t0 + .6, .55, FIRE_PAN)
    place(fwoomp(.7, .6), t0 + .6, .55, FIRE_PAN)
place(thunk(110, .3), 4.38, .5, 0)            # seat log lifted
place(whoosh(.45, 600), 4.8, .55, .3)         # heave
place(thunk(95, .35), 5.08, .9, FIRE_PAN)     # lands
place(roar(1.7), 5.05, 1.0, FIRE_PAN)         # flare (day 7)
place(sizzle(1.2), 7.35, .55, FIRE_PAN)       # fire dies (day 30)
place(low_hit(2.4), 7.98, .8, 0)              # YOU'VE CHANGED
for tb, pn in [(2.05, -.1), (3.08, .1), (8.0, -.35), (8.3, .35)]:
    place(pop(), tb, .45, pn)
# ---- bottom lane (quieter, steady care)
for land in [.3, 2.65, 3.95, 5.25, 7.35, 10.45]:
    place(thunk(200 + rs.rand() * 40, .16), land, .3, FIRE_PAN)
    place(fwoomp(.5, .3), land, .28, FIRE_PAN)
for ta in [2.6, 6.2, 9.6, 11.3, 4.0, 7.2, 9.0, 11.8]:
    place(pile_tick(), ta, .5, -.4 if ta in (2.6, 6.2, 9.6, 11.3) else .3)
place(pop(980, 600, .08), 11.95, .5, 0)       # I LOVE YOU.
# ---- DAY counter
for td in [1.9, 2.95, 5.25, 6.4, 6.95, 7.45]:
    place(tick(2200), td, .35)
def day(t):
    k = min(1, max(0, (t - 9.35) / 2.1)); return round(30 + 335 * (k * k * (1.4 - .4 * k)))
last = -1; prev = 30
for f in range(int(9.35 * 30), int(11.5 * 30)):
    t = f / 30; d = day(t)
    if d != prev and t - last > .055:
        place(tick(2600 + 400 * (t - 9.35) / 2.1), t, .28); last = t
    prev = d
place(tick(1800, .04), 11.45, .45)
place(pop(900, 450, .09), 13.45, .55, 0)  # question card
place(roar(1.2), -HOOK, .8, FIRE_PAN)  # hook: the day-7 bonfire
place(thunk(90, .3), -.02, .7, 0)      # hard cut to the split
st = np.stack([L, R], 1)
fi = int((14.4 + HOOK) * SR); st[fi:] *= np.linspace(1, 0, N - fi)[:, None]
st /= np.max(np.abs(st)) + 1e-9; st *= .89
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'sfx.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
