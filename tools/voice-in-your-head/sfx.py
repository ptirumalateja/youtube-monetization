# The Voice in Your Head: fully synthesised sound (numpy only, no samples, no credits).
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

# ---- 0.00 frame-0 hit: "HELLO" heard inside the head, two falling gold notes with echoes ----
h, s = hit(1.4, .55); place(hitbus, h, 0); place(subbus, s, 0, .6)
for k, (tt0, m) in enumerate([(0, 79), (.16, 76)]):
    for e in range(4):
        place(voice, bell(note(m), 1.6), tt0 + e * .33, .55 * .5 ** e, pan=(-.5 if e % 2 else .5) * (e > 0))

# ---- room tone + warm pad (tonic A minor-ish, gold) ----
x = np.arange(N) / SR
room = fft_filter(rng.standard_normal((N, 2)), lo=120, hi=900) * .035
pad_f = [note(57), note(64), note(69)]
pad = sum(np.sin(2 * np.pi * f * x + i) * (1 + .3 * np.sin(x * .4 + i)) for i, f in enumerate(pad_f)) * .045
padenv = np.interp(x, [0, 2, 2.5, 3, 8, 9.4, 9.45, 10.08, 20], [1, 1, .4, .5, .9, 1, 0, 0, 0])
bed += room * np.interp(x, [0, 9.4, 9.45, 10.0, 10.08, 20], [1, 1, .02, .02, 1, 1])[:, None]
bed += (pad * padenv)[:, None]

# ---- 2.05 snap out; 2.45 eyes close (a breath out) ----
place(sfx, whoosh(.35, 3500, 600), 1.95, .5)
place(sfx, whoosh(.9, 500, 250) * .6, 2.45, .35)

# ---- typing ticks for each typed line (soft, high) ----
def typing(t0, chars, cps, g=.08):
    for i in range(chars): place(ticks, pop(.03, 6000) * .5, t0 + i / cps, g, pan=rng.uniform(-.3, .3))
typing(0, 11, 14); typing(.78, 13, 16); typing(2.1, 16, 26); typing(2.4, 20, 30)
typing(8.05, 20, 34); typing(10.15, 11, 26, .06); typing(10.6, 15, 26, .06); typing(15.3, 9, 22, .06); typing(15.75, 8, 22, .06)

# ---- 3.0-8.0 the five seconds: clock ticks, heartbeat, rising mind chatter ----
for k in range(6):
    tk = 3.0 + k; place(ticks, bell(2400 if k < 5 else 1800, .25, ((1, 1), (2.1, .3))), tk, .18)
for k, tb in enumerate(np.cumsum([3.2] + [60 / b for b in np.linspace(70, 112, 9)])):
    if tb > 9.4: break
    lub = np.sin(2 * np.pi * 62 * tt(.16)) * env(int(.16 * SR), .004, .05)
    place(subbus, lub, tb, .35); place(subbus, lub, tb + .18, .22)
    place(sfx, fft_filter(lub * 1.0, lo=95, hi=400) * 3, tb, .12)
# chatter: formant-filtered noise bursts like muffled syllables, density and level rising
cht = np.zeros((N, 2))
t_ = 3.3
while t_ < 9.4:
    d = rng.uniform(.06, .16); seg = rng.standard_normal(int(d * SR))
    f1 = rng.uniform(350, 900); f2 = rng.uniform(1100, 2400)
    syl = fft_filter(seg, lo=f1 * .8, hi=f1 * 1.25) + .6 * fft_filter(seg, lo=f2 * .85, hi=f2 * 1.2)
    syl *= np.sin(np.pi * np.linspace(0, 1, len(syl))) ** 1.5
    place(cht, syl, t_, 1, pan=rng.uniform(-.7, .7))
    t_ += d + max(.015, .22 - (t_ - 3.3) * .04) * rng.uniform(.5, 1.4)
cht *= np.interp(x, [3.3, 5, 8, 9.35, 9.42], [.15, .5, 1, 1.2, 0])[:, None]
voice += cht * .5
# tension drone (rising) under the five seconds
dr = np.interp(x, [3, 8, 9.4, 9.42], [0, 1, 1.2, 0])
freq = np.interp(x, [3, 9.4], [110, 147]); ph = 2 * np.pi * np.cumsum(freq) / SR
bed += (np.tanh(1.5 * (np.sin(ph) + .5 * np.sin(1.5 * ph + .3))) * dr * .045)[:, None]

# ---- a gold pop each time a word bubble appears; pitch climbs as they pile up ----
BUB = [3.40, 3.95, 4.50, 5.05, 5.55, 5.72, 6.15, 6.60, 6.92, 7.18, 7.38, 7.52, 7.66, 7.80, 7.90, 7.97]
scale = [69, 72, 74, 76, 79, 81, 84, 86, 88, 91]
for i, tb in enumerate(BUB):
    m = scale[min(len(scale) - 1, i * len(scale) // len(BUB))]
    place(voice, pluck(note(m), .5), tb, .32, pan=rng.uniform(-.6, .6))
    place(sfx, pop(), tb, .25)
    if tb == 6.15:  # the HELLO bubble returns: the same two notes as frame 0
        place(voice, bell(note(79), 1.2), tb, .35); place(voice, bell(note(76), 1.2), tb + .16, .3)
# 5.36 the swat: whoosh + pop
place(sfx, whoosh(.22, 1500, 4000), 5.14, .5); place(sfx, pop(.12, 3000), 5.36, .6)
# 8.0 the timer reaches 5.0: a clear ding
place(voice, bell(note(93), 2.0), 8.0, .4); place(voice, bell(note(81), 2.0), 8.0, .25)

# ---- 9.40 every bubble pops at once, then held breath until the 10.08 hit ----
for k in range(16): place(sfx, pop(.08, rng.uniform(2500, 5000)), 9.40 + k * .011 + rng.uniform(0, .02), .35, pan=rng.uniform(-.8, .8))
place(sfx, whoosh(.32, 300, 2500, rev=True), 9.70, .45)   # reverse suck into the hit
h, s = hit(2.2, 1.0); place(hitbus, h, 10.08); place(subbus, s, 10.08, 1.0)

# ---- 10.1-15 calm teal world: open fifths, glass notes for each picture bubble ----
calm = sum(np.sin(2 * np.pi * f * x + i) for i, f in enumerate([note(50), note(57), note(64), note(69)])) * .045
calm *= np.interp(x, [10.08, 10.6, 15, 17.5, 19.6, 20], [0, 1, 1, .8, .3, .1])
bed += calm[:, None]
glass = ((1, 1), (2.0, .3), (3.01, .12))
for tb, m in [(10.25, 76), (10.7, 81), (11.2, 83), (11.75, 88)]:
    place(voice, bell(note(m), 2.6, glass, a=.03), tb, .26, pan=rng.uniform(-.4, .4))
place(ticks, pop(.05, 2000), 12.5, .5)   # the red chip lands
# each picture bubble redraws every 1.7 s: a quiet glass note per new picture
pent = [76, 79, 81, 83, 86, 88]
for i, t0 in enumerate([10.25, 10.7, 11.2, 11.75]):
    k = 1
    while t0 + 1.7 * k < 17.4:
        place(voice, bell(note(pent[(i * 2 + k) % len(pent)]), 2.2, glass, a=.02), t0 + 1.7 * k, .16, pan=rng.uniform(-.6, .6)); k += 1
# 15.3 which one are you: the gold notes and a teal glass note together
place(voice, bell(note(79), 1.8), 15.3, .3, -.4); place(voice, bell(note(76), 1.8), 15.46, .25, -.4)
place(voice, bell(note(88), 2.6, glass, a=.03), 15.75, .26, .4)

# ---- 17.6-20 rising tone into the loop (resolves on the frame-0 hit) ----
rise = np.interp(x, [17.6, 19.85, 19.95], [0, 1, 0]) ** 2
fr = np.interp(x, [17.6, 19.95], [220, 392]); ph = 2 * np.pi * np.cumsum(fr) / SR
bed += ((np.sin(ph) + .3 * np.sin(2 * ph)) * .12 * rise)[:, None]
place(sfx, whoosh(1.0, 400, 3000, rev=True), 18.95, .3)

# ---- mix ----
hitbus = reverb(hitbus, 2.4, .3); voice = reverb(voice, 1.8, .22)
mix = hitbus * 1.0 + sfx * .9 + voice * 1.0 + ticks * .8
mix = fft_filter(mix, lo=90)                     # phones: keep weight in the audible band
bed = fft_filter(bed, lo=80)
# duck the bed under the two hits
duck = np.ones(N)
for th in (0, 10.08): duck *= 1 - .6 * np.exp(-np.maximum(0, x - th) / .35) * (x >= th)
mix += bed * duck[:, None] + fft_filter(subbus, hi=140)
# held breath: near silence 9.48-10.0 (only the reverse suck and room tail)
mix = np.tanh(mix * 1.3) / 1.3
mix /= np.abs(mix).max() / .89
pcm = (mix * 32767).astype(np.int16)
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'sfx.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('ok')
