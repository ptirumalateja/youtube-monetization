# The Voice in Your Head V2: fully synthesised sound (numpy only, no samples, no credits).
# python3 sfx.py <out.wav>   -> 48 kHz stereo 16-bit, 20.0 s, cue times match scene.js
import sys, wave
import numpy as np

SR = 48000
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(7)

def buf(): return np.zeros((N, 2))
def tt(d): return np.arange(int(d * SR)) / SR
def place(bus, x, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if x.ndim == 1: x = np.stack([x * np.sqrt((1 - pan) / 2), x * np.sqrt((1 + pan) / 2)], 1) * np.sqrt(2)
    j = min(N, i + len(x))
    if j > i: bus[i:j] += x[:j - i] * gain

def fft_filter(x, lo=None, hi=None):
    """Brick-ish band filter with soft edges, applied per channel in the frequency domain."""
    n = len(x); f = np.fft.rfftfreq(n, 1 / SR); m = np.ones_like(f)
    if lo: m *= 1 / (1 + (lo / np.maximum(f, 1)) ** 4)
    if hi: m *= 1 / (1 + (f / hi) ** 4)
    if x.ndim == 1: return np.fft.irfft(np.fft.rfft(x) * m, n)
    return np.stack([np.fft.irfft(np.fft.rfft(x[:, c]) * m, n) for c in range(x.shape[1])], 1)

def env(n, a, d, curve=1.0):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.arange(n - na) / SR / max(d, 1e-3)) ** curve
    return e

def bell(f, d=2.5, partials=((1, 1), (2.76, .45), (5.4, .22), (8.93, .1)), a=.002):
    x = tt(d); s = sum(g * np.sin(2 * np.pi * f * p * x + p) * np.exp(-x * (1.2 + p * .9) / d * 2) for p, g in partials)
    return s * env(len(x), a, d)

def pluck(f, d=.6):
    x = tt(d); s = np.sin(2 * np.pi * f * x) + .35 * np.sin(4 * np.pi * f * x) + .15 * np.sin(6 * np.pi * f * x)
    return s * env(len(x), .003, d / 5)

def pop(d=.09, bright=4000):
    x = tt(d); f = np.linspace(1400, 380, len(x))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(x), .001, .02)
    n = fft_filter(rng.standard_normal(len(x)), lo=bright) * env(len(x), .0005, .006) * .5
    return s + n

def whoosh(d, f0, f1, rev=False):
    x = tt(d); n = rng.standard_normal(len(x)); out = np.zeros_like(n); win = 2048
    # sweep a band through the noise in overlapping blocks
    for k in range(0, len(n), win // 2):
        seg = n[k:k + win]; c = f0 + (f1 - f0) * (k / len(n))
        out[k:k + len(seg)] += fft_filter(seg * np.hanning(len(seg)), lo=c * .6, hi=c * 1.6)
    e = np.sin(np.pi * np.linspace(0, 1, len(x))) ** 2
    if rev: e = np.linspace(0, 1, len(x)) ** 3
    return out * e

def hit(t_body=1.6, big=1.0):
    x = tt(t_body)
    crack = fft_filter(rng.standard_normal(len(x)), lo=2500) * env(len(x), .0005, .012)
    f = 320 * np.exp(-x * 9) + 88
    body = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * env(len(x), .002, .35)
    gong = sum(g * np.sin(2 * np.pi * fr * x) * np.exp(-x * dk) for fr, g, dk in ((147, .5, 1.6), (233, .35, 2.2), (371, .25, 2.8), (589, .15, 3.4)))
    sub = np.sin(2 * np.pi * 46 * x) * env(len(x), .004, .45)
    return (crack * .9 + body * .9 + gong * .6) * big, sub * big

def reverb(x, d=2.2, mix=.25):
    ir_n = int(d * SR); ir = rng.standard_normal((ir_n, 2)) * np.exp(-np.arange(ir_n) / SR / (d / 6.9))[:, None]
    ir = fft_filter(ir, hi=6000); ir /= np.sqrt((ir ** 2).sum(0))
    n = len(x) + ir_n; F = lambda a: np.fft.rfft(a, n)
    wet = np.stack([np.fft.irfft(F(x[:, c]) * F(ir[:, c]), n)[:len(x)] for c in range(2)], 1)
    return x * (1 - mix) + wet * mix * 3

def note(m): return 440 * 2 ** ((m - 69) / 12)

hitbus, subbus, sfx, bed, voice, ticks = buf(), buf(), buf(), buf(), buf(), buf()

# V2 cue sheet (times match scene.js): hook 0, pull-out 2.2, timer 3.2-8.2, snap to silence 9.0, hit 10.0, loop 19.3-20
# ---- 0.00 frame-0 hit: "HELLO" heard inside the head, two falling gold notes with echoes ----
h, s = hit(1.4, .7); place(hitbus, h, 0); place(subbus, s, 0, .7)
for k, (tt0, m) in enumerate([(0, 79), (.16, 76)]):
    for e in range(4):
        place(voice, bell(note(m), 1.6), tt0 + e * .33, .6 * .5 ** e, pan=(-.5 if e % 2 else .5) * (e > 0))

# ---- room tone + warm pad; everything is cut dead at the 9.0 snap ----
x = np.arange(N) / SR
room = fft_filter(rng.standard_normal((N, 2)), lo=120, hi=900) * .035
pad_f = [note(57), note(64), note(69)]
pad = sum(np.sin(2 * np.pi * f * x + i) * (1 + .3 * np.sin(x * .4 + i)) for i, f in enumerate(pad_f)) * .045
cut = np.interp(x, [0, 8.995, 9.0, 9.95, 10.0, 20], [1, 1, 0, 0, 1, 1])
bed += room * cut[:, None] * np.interp(x, [0, 10, 10.01, 20], [1, 1, 1, 1])[:, None]
bed += (pad * np.interp(x, [0, 2.2, 2.7, 3.2, 8.2, 8.995, 9.0, 20], [1, 1, .4, .5, .9, 1, 0, 0]))[:, None]

# ---- 2.2 pull out; 2.85 eyes close (a breath out) ----
place(sfx, whoosh(.4, 3500, 600), 2.15, .55)
place(sfx, whoosh(.9, 500, 250) * .6, 2.85, .35)
def typing(t0, chars, cps, g=.07):
    for i in range(chars): place(ticks, pop(.03, 6000) * .5, t0 + i / cps, g, pan=rng.uniform(-.3, .3))
typing(2.25, 17, 40); typing(2.5, 20, 40); typing(10.1, 17, 32, .05); typing(10.6, 14, 30, .05); typing(15.3, 19, 34, .05); typing(15.85, 15, 30, .05)

# ---- 3.2-8.2 the five seconds: clock ticks, heartbeat, rising mind chatter ----
for k in range(6):
    place(ticks, bell(2400 if k < 5 else 1800, .25, ((1, 1), (2.1, .3))), 3.2 + k, .2)
for tb in np.cumsum([3.3] + [60 / b for b in np.linspace(70, 120, 10)]):
    if tb > 8.95: break
    lub = np.sin(2 * np.pi * 62 * tt(.16)) * env(int(.16 * SR), .004, .05)
    place(subbus, lub, tb, .4); place(subbus, lub, tb + .18, .25)
    place(sfx, fft_filter(lub, lo=95, hi=400) * 3, tb, .14)
cht = np.zeros((N, 2)); t_ = 3.5
while t_ < 9.0:
    d = rng.uniform(.06, .16); seg = rng.standard_normal(int(d * SR))
    f1 = rng.uniform(350, 900); f2 = rng.uniform(1100, 2400)
    syl = fft_filter(seg, lo=f1 * .8, hi=f1 * 1.25) + .6 * fft_filter(seg, lo=f2 * .85, hi=f2 * 1.2)
    syl *= np.sin(np.pi * np.linspace(0, 1, len(syl))) ** 1.5
    place(cht, syl, t_, 1, pan=rng.uniform(-.7, .7))
    t_ += d + max(.012, .22 - (t_ - 3.5) * .04) * rng.uniform(.5, 1.4)
cht *= np.interp(x, [3.5, 5, 8, 8.99, 9.0], [.15, .5, 1.1, 1.4, 0])[:, None]
voice += cht * .55
dr = np.interp(x, [3.2, 8.2, 8.995, 9.0], [0, 1, 1.4, 0])
ph = 2 * np.pi * np.cumsum(np.interp(x, [3.2, 9.0], [110, 165])) / SR
bed += (np.tanh(1.5 * (np.sin(ph) + .5 * np.sin(1.5 * ph + .3))) * dr * .05)[:, None]

# ---- a gold pop per intrusive thought, pitch climbing ----
BUB = [3.70, 4.30, 5.00, 5.70, 5.86, 6.50, 7.10, 7.55, 7.85]
scale = [69, 72, 74, 76, 79, 81, 84, 86, 88]
for i, tb in enumerate(BUB):
    place(voice, pluck(note(scale[i]), .5), tb, .36, pan=rng.uniform(-.6, .6)); place(sfx, pop(), tb, .3)
    if tb == 7.55: place(voice, bell(note(79), 1.2), tb, .4); place(voice, bell(note(76), 1.2), tb + .16, .34)
place(sfx, whoosh(.25, 1500, 4000), 5.05, .55); place(sfx, pop(.12, 3000), 5.42, .7)   # the swat
place(voice, bell(note(93), 2.0), 8.2, .45); place(voice, bell(note(81), 2.0), 8.2, .3)    # 5.0 s
# hands over ears 7.0: muffled thump
place(sfx, fft_filter(pop(.15, 800), hi=600) * 2, 7.0, .4)

# ---- 9.0 SNAP: a tape-stop zip, then dead silence; reverse suck into the 10.0 hit ----
zp = tt(.12); zip_ = np.sin(2 * np.pi * np.cumsum(np.linspace(900, 60, len(zp))) / SR) * np.linspace(1, 0, len(zp))
place(sfx, zip_, 8.88, .5)
place(sfx, whoosh(.38, 300, 2600, rev=True), 9.6, .55)
h, s = hit(2.2, 1.0); place(hitbus, h, 10.0); place(subbus, s, 10.0, 1.0)

# ---- 10-18 two minds: calm open fifths, glass notes for pictures, plucks for A's words ----
calm = sum(np.sin(2 * np.pi * f * x + i) for i, f in enumerate([note(50), note(57), note(64), note(69)])) * .045
calm *= np.interp(x, [10.0, 10.5, 15, 17.9, 19.4, 20], [0, 1, 1, .8, .3, .1])
bed += calm[:, None]
glass = ((1, 1), (2.0, .3), (3.01, .12))
for i, t0 in enumerate([10.25, 10.55, 10.9]):
    k = 0
    while t0 + 1.6 * k < 17.6:
        place(voice, bell(note([76, 81, 83, 86, 88][(i * 2 + k) % 5]), 2.2, glass, a=.02), t0 + 1.6 * k, .2 if k == 0 else .13, pan=.4); k += 1
for i in range(3):
    k = 0
    while 10.2 + (k - i * .55 / 1.65) * 1.65 < 17.6:
        tb = 10.2 + k * 1.65 - i * .55
        if tb >= 10.2: place(voice, pluck(note([69, 72, 76][i]), .35), tb, .14, pan=-.4)
        k += 1
place(ticks, pop(.05, 2000), 12.9, .55)   # the red chip lands
place(voice, bell(note(79), 1.8), 15.3, .32, -.4); place(voice, bell(note(76), 1.8), 15.46, .27, -.4)
place(voice, bell(note(88), 2.6, glass, a=.03), 15.85, .28, .4)

# ---- 17.9-20 push back into A's head; HELLO re-forms (19.3) and resolves on the frame-0 hit ----
rise = np.interp(x, [17.9, 19.85, 19.95], [0, 1, 0]) ** 2
ph = 2 * np.pi * np.cumsum(np.interp(x, [17.9, 19.95], [220, 392])) / SR
bed += ((np.sin(ph) + .3 * np.sin(2 * ph)) * .12 * rise)[:, None]
place(sfx, whoosh(1.0, 400, 3000, rev=True), 18.95, .3)
place(voice, bell(note(79), 1.0), 19.3, .2)

# ---- mix ----
hitbus = reverb(hitbus, 2.4, .3); voice = reverb(voice, 1.8, .22)
mix = hitbus * 1.0 + sfx * .9 + voice * 1.0 + ticks * .8
mix = fft_filter(mix, lo=90)                     # phones: keep weight in the audible band
bed = fft_filter(bed, lo=80)
# duck the bed under the two hits
duck = np.ones(N)
for th in (0, 10.0): duck *= 1 - .6 * np.exp(-np.maximum(0, x - th) / .35) * (x >= th)
mix += bed * duck[:, None] + fft_filter(subbus, hi=140)
# the silence beat: hard gate 9.0-9.6 so no reverb tail leaks; the reverse suck comes in after
mix *= np.interp(x, [8.995, 9.02, 9.58, 9.6], [1, .003, .003, 1])[:, None]
mix = np.tanh(mix * 1.3) / 1.3
mix /= np.abs(mix).max() / .89
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'sfx.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
