# Original horror sound bed for v4, synthesised locally with numpy (no samples). Writes audio/sfx_bed.wav.
# Cues come from the voiceover word times (+0.2 s offset), matching timeline.js.
import json, sys, wave
import numpy as np

SR = 48000; DUR = 20.6; N = int(SR * DUR); OFF = .2
here = sys.argv[1] if len(sys.argv) > 1 else '.'
ts = json.load(open(f'{here}/audio/vo_v4_timestamps.json'))
rng = np.random.default_rng(13)
def word(w, n=0):
    return [x for x in ts['words'] if ''.join(c for c in x['word'].lower() if c.isalnum() or c == "'") == w][n]['start'] + OFF
seg = [(s['start'] + OFF, s['end'] + OFF) for s in ts['segments']]
T = dict(three=word('3'), wake=word('wake'), corner=word('corner'), dont=word("don't"), open=word('open'))
T['black'] = seg[11][1] + .04
cuts = [0, seg[1][0] - .12, seg[3][0] - .14, seg[4][0] - .12, seg[5][0] - .12, seg[6][0] - .1, seg[8][0] - .15, seg[9][0] - .1, seg[10][0] - .08, seg[11][0] - .04]
t = np.arange(N) / SR
out = np.zeros(N)

def lp(x, a):  # one-pole low-pass, a = smoothing coefficient per sample
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y
def env(t0, dur):
    return (t >= t0) & (t < t0 + dur)
def place(t0, sig):
    i0 = int(t0 * SR); i1 = min(N, i0 + len(sig))
    if i0 < N: out[i0:i1] += sig[:i1 - i0]

# drone: a sub pulse, a dissonant minor-second cluster and dark wind, swelling toward the lunge
rise = np.clip(t / T['black'], 0, 1) ** 1.5
noise = lp(rng.standard_normal(N), .01)
drone = (.5 * np.sin(2 * np.pi * 41 * t) * (1 + .3 * np.sin(2 * np.pi * .23 * t))
         + .22 * np.sin(2 * np.pi * 110 * t + .6 * np.sin(2 * np.pi * .4 * t)) + .2 * np.sin(2 * np.pi * 116.5 * t)
         + .12 * np.sin(2 * np.pi * 233.1 * t) * rise + 3.0 * noise)
out += drone * (.08 + .17 * rise)

# clock ticks during the opening, a hard beep when it turns 3:00
for k in range(3):
    place(.15 + k * .9, .25 * rng.standard_normal(600) * np.exp(-np.arange(600) / 60))
bt = np.arange(int(.25 * SR)) / SR
place(T['three'], .18 * np.sign(np.sin(2 * np.pi * 1760 * bt)) * (bt < .2))

def hit(t0, g=1., f0=90, f1=34, d=2.2):
    n = int(d * SR); x = np.arange(n) / SR; f = f1 + (f0 - f1) * np.exp(-x * 5)
    ph = 2 * np.pi * np.cumsum(f) / SR
    place(t0, g * (np.tanh(2.5 * np.sin(ph)) * np.exp(-x * 1.8) * .7 + rng.standard_normal(n) * np.exp(-x * 30) * .4))
def screech(t0, d, g=.3, f0=1900, f1=2600):  # bowed-metal string scrape: inharmonic partials gliding
    n = int(d * SR); x = np.arange(n) / SR; u = x / d
    s = sum(a * np.sin(2 * np.pi * np.cumsum((f0 + (f1 - f0) * u) * r * (1 + .004 * np.sin(2 * np.pi * 6 * x))) / SR) for r, a in ((1, 1), (1.41, .6), (2.13, .4), (2.97, .25)))
    s *= (1 + .5 * rng.standard_normal(n) * .3)
    place(t0, g * s * np.minimum(1, x / .03) * np.exp(-x * (1.5 / d)))
def swell(t0, d, g=.4):
    n = int(d * SR); x = np.arange(n) / SR; place(t0, g * lp(rng.standard_normal(n), .08) * (x / d) ** 3 * 3)

hit(0, .8)                                              # title slam
screech(T['wake'] - .02, .7, .22)                         # his eye snaps open
swell(cuts[2] - .6, .6, .25); hit(cuts[2], .5, 70, 30)    # "you can't scream"
swell(T['corner'] - 1.0, 1.0, .5); hit(T['corner'], 1.1, 120, 32, 3)   # the eyes ignite
screech(T['corner'], 1.4, .14, 600, 520)
for c in cuts[4:9]: hit(c, .45, 80, 30, 1.5)              # every cut it is closer
# heartbeat from the corner on, accelerating
b, bpm = T['corner'] - .2, 72
while b < T['black']:
    for dt, gg in ((0, 1.), (.16, .65)):
        n = int(.3 * SR); x = np.arange(n) / SR
        place(b + dt, .55 * gg * np.tanh(2 * (np.sin(2 * np.pi * 62 * x) + .5 * np.sin(2 * np.pi * 124 * x))) * np.exp(-x * 15))
    bpm = min(150, bpm * 1.045); b += 60 / bpm
# whispers: breathy band-limited noise, pulsing like breath, while it closes in
wh = lp(rng.standard_normal(N), .35) - lp(rng.standard_normal(N), .05)
br = np.clip(np.sin(2 * np.pi * .9 * t), 0, 1) ** 2
out += .35 * wh * br * np.clip((t - cuts[6]) / 1.5, 0, 1) * (t < T['dont'])
# the candle is snuffed: a short breath, then the room goes almost silent
swell(T['dont'] - .25, .25, .25)
out *= np.where((t > T['dont']) & (t < T['open'] - .05), .45, 1.)
# the lunge: rising scream of strings and noise, cut dead at black
d = T['black'] - T['open'] + .1
screech(T['open'] - .1, d, .45, 700, 2400); swell(T['open'] - .1, d, .7)
out[t >= T['black']] = 0
# in the black: the eyes open with a sub thud and one slow breath
hit(T['black'] + .3, .7, 55, 25, .8)
swell(T['black'] + .1, .4, .12)
out *= np.where(t > DUR - .04, np.clip((DUR - t) / .04, 0, 1), 1)

out = out / np.max(np.abs(out)) * .9
with wave.open(f'{here}/audio/sfx_bed.wav', 'w') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes((out * 32767).astype('<i2').tobytes())
print('ok', {k: round(v, 2) for k, v in T.items()})
