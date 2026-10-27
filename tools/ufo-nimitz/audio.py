"""Synthesised score + sound design + VO mix for the Tic Tac film (no stock audio).
python3 audio.py -> out/film_audio.wav (48 kHz stereo). Cue times match edit.py.
DUB=hi|te python3 audio.py -> out/film_audio_<lang>.wav, narration from vo_<lang>/ fitted to the English beats."""
import numpy as np, subprocess, os
from edit import VO, END
from timeline import T, D, R, R_end, CARD_AT, CARD
SR = 48000
N = int(END * SR)
rng = np.random.RandomState(7)
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def t_(d): return np.arange(int(d * SR)) / SR
def env(n, a, r):
    e = np.ones(n); A = int(a * SR); R = int(r * SR)
    if A: e[:A] = np.linspace(0, 1, A)
    if R: e[-R:] *= np.linspace(1, 0, R)
    return e
def lp(x, fc):
    """one-pole low-pass (fc may be an array)"""
    fc = np.broadcast_to(np.asarray(fc, float), x.shape)
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.
    for i in range(len(x)): s = a[i] * s + (1 - a[i]) * x[i]; y[i] = s
    return y
def lp_fast(x, fc):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, fc, 'low', fs=SR, output='sos'), x)
def hp_fast(x, fc):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, fc, 'high', fs=SR, output='sos'), x)
def bp_fast(x, f1, f2):
    from scipy.signal import butter, sosfilt
    return sosfilt(butter(2, [f1, f2], 'band', fs=SR, output='sos'), x)
IR = None
def reverb(x, dur=2.5, mix=.3):
    global IR
    if IR is None:
        n = int(dur * SR); IR = rng.normal(0, 1, n) * np.exp(-np.arange(n) / SR * 3.2); IR /= np.sqrt((IR ** 2).sum())
    from scipy.signal import fftconvolve
    return x * (1 - mix) + fftconvolve(x, IR)[:len(x)] * mix * 2

music = np.zeros(N); sfx = np.zeros(N)
def put(buf, start, x, g=1.):
    i = int(start * SR); j = min(N, i + len(x))
    if i < N: buf[i:j] += x[:j - i] * g

# ---------------- elements
def boom(d=3.0, f0=70, f1=28):
    t = t_(d); f = f1 + (f0 - f1) * np.exp(-t * 6)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.exp(-t * 1.6)
    n = lp_fast(rng.normal(0, 1, len(t)), 900) * np.exp(-t * 9) * .6
    return np.tanh((x + n) * 1.6) * .9
def hit(d=1.6):  # sharper impact
    t = t_(d)
    x = np.sin(2 * np.pi * (55 + 120 * np.exp(-t * 30)) * t) * np.exp(-t * 3)
    x += hp_fast(rng.normal(0, 1, len(t)), 1500) * np.exp(-t * 25) * .5
    return np.tanh(x * 1.8) * .8
def whoosh(d=1.2, up=True):
    t = t_(d); n = rng.normal(0, 1, len(t))
    fc = 300 + 5000 * (t / d if up else 1 - t / d) ** 2
    x = bp_fast(n, 200, 7000) * np.sin(np.pi * t / d) ** 2
    return lp(x, fc) * .9
def rewind(d=2.15):
    t = t_(d); f = 200 + 1800 * (t / d) ** .5 + 120 * np.sin(2 * np.pi * 17 * t)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sign(np.sin(ph)) * .3 + np.sin(ph * 2) * .3) * env(len(t), .05, .1)
    return lp_fast(x, 4000) * .5
def ping():
    t = t_(1.6); x = np.sin(2 * np.pi * 1320 * t) * np.exp(-t * 7) + .4 * np.sin(2 * np.pi * 2640 * t) * np.exp(-t * 11)
    return reverb(x * .35, 1.5, .4)
def snap():
    t = t_(.4); return hp_fast(rng.normal(0, 1, len(t)), 2500) * np.exp(-t * 30) * .5 + np.sin(2 * np.pi * 900 * t) * np.exp(-t * 20) * .3
def riser(d=4.0):
    t = t_(d); f = 80 * 2 ** (3 * t / d)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / d) ** 2 * .4
    x += bp_fast(rng.normal(0, 1, len(t)), 500, 6000) * (t / d) ** 3 * .25
    return x
def jet_rumble(d):
    t = t_(d); n = rng.normal(0, 1, len(t))
    return (lp_fast(n, 220) * 1.2 + bp_fast(n, 600, 2500) * .08) * env(len(t), 1.0, 1.0)
def wind(d):
    t = t_(d); n = rng.normal(0, 1, len(t))
    m = .6 + .4 * np.sin(2 * np.pi * .13 * t + 1)
    return bp_fast(n, 300, 1800) * m * .25 * env(len(t), 1.5, 1.5)
def heartbeat(d, bpm=62):
    out = np.zeros(int(d * SR)); per = 60 / bpm
    for k in range(int(d / per)):
        for off, g in ((0, 1), (.28, .7)):
            tt = t_(.3); x = np.sin(2 * np.pi * 48 * tt) * np.exp(-tt * 18) * g
            i = int((k * per + off) * SR); out[i:i + len(x)] += x[:len(out) - i]
    return out * .9

# ---------------- score: D minor drone pads with slow movement
def pad(d, notes, g=.12, bright=500):
    t = t_(d); x = np.zeros(len(t))
    for f in notes:
        for det in (-.12, .0, .13):
            x += np.sin(2 * np.pi * f * (1 + det / 100) * t + rng.uniform(0, 6)) / 3
            x += .35 * np.sin(2 * np.pi * 2 * f * (1 + det / 100) * t) / 3
    x *= (1 + .25 * np.sin(2 * np.pi * .07 * t))
    return lp_fast(x, bright) * g * env(len(t), 2.5, 2.5)
def pulse(d, bpm=96, f=36.7, g=.5):
    out = np.zeros(int(d * SR)); per = 60 / bpm
    tt = t_(per * .9)
    k = np.sin(2 * np.pi * f * tt) * np.exp(-tt * 7)
    for i in range(int(d / per)):
        j = int(i * per * SR); out[j:j + len(k)] += k[:len(out) - j]
    return out * g
D2, F2, A2, C3, D3, E3, F3, G3, A3, Bb2 = 73.4, 87.3, 110, 130.8, 146.8, 164.8, 174.6, 196, 220, 116.5

# v1 cues for the sections that carried over, moved to their v2 times (dropped where that part of v1 is cut)
def L(buf, t1, x, g=1.):
    t2 = R(t1)
    if t2 is None: return
    n = int((R_end(t1) + .8 - t2) * SR)
    if n < int(.3 * SR): return
    if len(x) > n:
        x = x[:n].copy(); f = min(int(.8 * SR), n); x[-f:] *= np.linspace(1, 0, f)
    put(buf, t2, x, g)
def at(k, f): return T[k] + f * D[k]

L(music, 0.0, pad(9.0, [D2, A2, D3], .10))
L(music, 11.3, pad(18.4, [D2, A2, F3], .11))
L(music, 11.3, pulse(18.0, 90, g=.25))
L(music, 29.2, pad(23.5, [D2, F2, A2, E3], .10, 420))
L(music, 52.3, pad(22.6, [Bb2, F3, D3], .10, 420))
L(music, 74.8, pad(24.4, [D2, A2, C3, E3], .11, 600))
L(music, 85.8, riser(13.2), .55)
L(music, 99.0, pad(11.0, [D2, A2, D3, F3], .12, 700))
L(music, 99.0, pulse(10.5, 120, g=.32))
L(music, 112.0, pad(8.0, [D2, A2], .07, 300))
L(music, 120.2, pad(10.4, [D2, F2, A2], .09))
L(music, 130.4, pad(40.6, [D2, A2, D3, E3], .09, 450))
L(music, 130.4, pulse(40.0, 76, g=.18))
L(music, 171.0, pad(29.0, [Bb2, D3, F3], .06, 380))
L(music, 200.0, pad(17.2, [C3, E3, G3], .09, 600))
L(music, 217.2, pad(15.8, [D2, A2, D3, F3, A3], .11, 900))
L(music, 217.2, pulse(15.8, 104, g=.32))
L(music, 233.0, pad(16.4, [D2, A2, D3, F3], .13, 1200))
L(music, 233.0, pulse(16.4, 124, g=.5))
L(music, 249.4, pad(23.0, [D2, F2, A2, C3], .10, 500))
L(music, 272.4, pad(14.0, [D2, Bb2, E3], .07, 300))
L(music, 286.4, pad(19.8, [D2, A2, E3], .09, 450))
L(music, 306.2, pad(22.0, [D2, F2, A2, D3, F3, A3], .12, 900))

# ---------------- sound design
L(sfx, 0.0, lp_fast(rng.normal(0, 1, int(8.9 * SR)), 180) * .25)    # sensor hum
L(sfx, 8.9, boom(3.0), .95)
L(sfx, 9.15, rewind(), .8)
L(sfx, 26.3, whoosh(.8), .6)
for s, d in ((37.4, 14.9),):
    k = 0.0
    while k < d:
        L(sfx, s + k + .2, ping(), .5); k += 2 * np.pi / 1.6
L(sfx, 52.3, jet_rumble(13.3), .45)
L(sfx, 55.5, whoosh(.9), .7)            # catapult shot
L(sfx, 130.4, jet_rumble(4.4), .45)
L(sfx, 130.3, whoosh(.9), .6)
L(sfx, 33.7, whoosh(.6), .4)
L(sfx, 70.4, hit(), .7)
L(sfx, 74.8, jet_rumble(11.0), .3)
L(sfx, 79.8, wind(19.2), 1.0)
L(sfx, 99.0, jet_rumble(10.0), .35)
L(sfx, 99.0, heartbeat(10.0, 70), .5)
L(sfx, 109.4, whoosh(1.0), .9)
L(sfx, 110.2, boom(3.5, 90, 25), 1.0)
L(sfx, 112.0, wind(6.0), .8)
L(sfx, 121.8, snap(), .7)
L(sfx, 124.6, hit(), .85)
L(sfx, 160.8, hit(1.2), .5)
L(sfx, 199.6, whoosh(1.0), .6)
L(sfx, 206.0, hit(), .6)
for s in (225.4, 228.4, 230.4): L(sfx, s, hit(), .7)
L(sfx, 232.6, whoosh(.6), .7)
for s in (233.0, 235.8, 237.9, 241.2, 245.2): L(sfx, s, hit(1.0), .5)
L(sfx, 249.0, whoosh(.8), .6)
L(sfx, 262.0, hit(), .6)
L(sfx, 266.4, hit(), .6)
L(sfx, 272.4, wind(14.0), .6)
L(sfx, 289.6, hit(), .8)
L(sfx, 292.2, hit(), .8)
L(sfx, 298.4, boom(2.5), .6)


# ---------------- v2 sections
# 0 cold open: the black triangle files
put(music, 0.0, pad(T['c02'] + 1.0, [D2, A2, E3], .09, 380))
put(sfx, 0.0, wind(T['c02'] + 1.5), .5)
put(sfx, 0.3, boom(3.0), .35)
put(sfx, at('c01', .55), whoosh(1.2, up=False), .22)              # drops into a canyon
put(sfx, at('c01', .86), hit(), .3)                               # no sound, no exhaust
put(music, T['c02'], pad(D['c02'] + 1.5, [D2, F2, A2, C3], .10, 500))
put(music, T['c02'], pulse(D['c02'], 90, g=.22))
for f in (.45, .74): put(sfx, at('c02', f), hit(1.2), .32)          # 30 s vs 3 s
put(sfx, at('c02', .84), boom(2.5), .4)                            # both can't be right
fs = at('c03', .84)
put(music, T['c03'], pad(fs - T['c03'] + 1.5, [Bb2, D3, F3], .09, 420))
put(sfx, at('c03', .13), hit(), .38)                                # no video exists
put(sfx, at('c03', .24), snap(), .38)
put(sfx, at('c03', .26), hit(1.2), .28)                             # 23 Oct 2026
put(sfx, at('c03', .53), whoosh(1.0), .25)
put(sfx, at('c03', .71), boom(3.0, 60, 30), .35)                    # 22 years earlier
put(sfx, fs, lp_fast(rng.normal(0, 1, int((R(0.0) - fs) * SR)), 180) * .25)   # sensor hum into the FLIR1 tail
# 1 FLIR1 honesty
c4 = T['b02'] - T['c04']
put(music, T['c04'], pad(c4 + 1.0, [D2, A2, D3, F3], .09, 450))
put(music, T['c04'], pulse(c4, 76, g=.18))
put(sfx, T['c04'], lp_fast(rng.normal(0, 1, int(c4 * SR)), 180) * .15)
put(sfx, at('c04', .2), snap(), .5)
put(sfx, at('c04', .5), hit(), .7)                                 # his crew never saw it
put(sfx, at('c04', .6), whoosh(1.0), .5)
put(sfx, at('c04', .9), hit(1.2), .5)
b2 = CARD_AT['b03s'] - T['b02']
put(music, T['b02'], pad(b2 + 1.0, [D2, A2, F3], .11))
put(music, T['b02'], pulse(b2, 90, g=.25))
put(sfx, at('b02', .15), jet_rumble(.7 * D['b02']), .4)
put(sfx, at('b02', .83), whoosh(.8), .6)
# split screens slide open
for t0 in (at('c04', .45), at('c04', .6), T['c07'], at('c08', .63), T['c11']): put(sfx, t0 - .2, whoosh(.6), .3)
# chapter cards
for k, ct in CARD_AT.items():
    put(sfx, ct - .6, whoosh(.8), .5); put(sfx, ct + .1, hit(1.2), .5)
    put(music, ct - .5, pad(CARD + 1.4, [D2, A2, D3], .09, 380)); put(sfx, ct - .5, wind(CARD + 1.4), .7)   # no dead air under the card
# 3 sixty miles: the maths, then the caveat
c5 = CARD_AT['c06'] - T['c05']
put(music, T['c05'], pad(c5 + 1.0, [D2, A2, D3, E3], .09, 450))
put(music, T['c05'], pulse(.36 * D['c05'], 96, g=.25))
for f in (0., .11): put(sfx, at('c05', f), snap(), .6)
put(music, at('c05', .11), riser(.1 * D['c05'] + 1.4), .5)
put(sfx, at('c05', .21) + 1.4, boom(3.0), .9)                     # counter lands on 3,600 mph
k = at('c05', .36)
while k < CARD_AT['c06'] - 1: put(sfx, k + .2, ping(), .45); k += 2 * np.pi / 1.6
put(sfx, at('c05', .57), hit(), .7)                                # no recording you can watch
# 4 four aviators, two jets, one radar
put(music, T['c06'], pad(T['c12'] - T['c06'] + 1.0, [Bb2, D3, F3], .08, 400))
put(sfx, T['c06'], jet_rumble(.55 * D['c06']), .4)
for f in (.17, .24, .27, .36): put(sfx, at('c06', f), snap(), .5)  # seats light up
put(sfx, at('c06', .57), hit(), .6)
put(sfx, at('c06', .8), whoosh(1.0), .5)
c12 = CARD_AT['c07'] - T['c12']
put(music, T['c12'], pad(c12 + 1.0, [D2, A2, C3, E3], .10, 600))
put(music, at('c12', .25), pulse(CARD_AT['c07'] - at('c12', .25), 104, g=.3))
for s, e in ((.25, .65),):
    k = at('c12', s)
    while k < min(at('c12', e), CARD_AT['c07'] - 1): put(sfx, k + .2, ping(), .45); k += 2 * np.pi / 1.6
put(sfx, at('c12', .67), hit(), .7)
put(sfx, at('c12', .85) + 1.3, boom(2.5), .7)                      # NOT PUBLIC stamp
# 5 Go Fast setup and payoff
put(music, T['c07'], pad(R(171.0) - T['c07'] + 1.0, [D2, F2, A2], .08))
for f in (0., .5): put(sfx, at('c07', f), snap(), .6)
c8 = CARD_AT['b11'] - T['c08']
put(music, T['c08'], pad(c8 + 1.0, [D2, A2, D3, F3, A3], .11, 900))
put(music, T['c08'], pulse(c8, 104, g=.3))
for f in (.4, .52): put(sfx, at('c08', f), hit(), .7)              # people / and radar
put(sfx, at('c08', .63), whoosh(.8), .6)
# 6 back to the black triangle
c10 = CARD_AT['c11'] - T['c10']
put(music, T['c10'], pad(c10 + 1.0, [D2, Bb2, E3], .08, 300))
put(sfx, T['c10'], wind(c10 + 1.0), .6)
for f in (.4, .6): put(sfx, at('c10', f), hit(1.2), .6)
put(sfx, at('c10', .87), boom(2.5), .7)
# 7 still unidentified, then the end screen
put(music, T['c11'], pad(T['b14'] - T['c11'] + 1.0, [D2, A2, E3], .09, 450))
put(sfx, at('c11', .47), hit(), .7)
put(sfx, at('c11', .7), boom(2.5), .6)
put(music, R(328.2), pad(END - R(328.2), [D2, A2, D3, F3], .12, 700))
put(sfx, R(328.2), boom(3.0, 60, 30), .4)

# ---------------- real cockpit audio from GOFAST (U.S. Navy, public domain)
def load(path, ss=0, d=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', path] + (['-t', str(d)] if d else []) + ['-f', 'f32le', '-ac', '1', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).astype(np.float64)
go = load('src/gofast.mp4', 0, 29.0)
go_env = np.ones(len(go)); go_env[int(3.0 * SR):] = .14   # duck well under narration after 3 s (v2: 6 dB lower than v1)
put(sfx, R(171.0), go * go_env, 1.4)

# ---------------- narration
DUB = os.environ.get('DUB', '')
vo = np.zeros(N)
if not DUB:
    for k, st in VO.items():
        x = load(f'vo/{k}.wav'); put(vo, st, x, 1.0)
else:
    # dubs run ~20% longer than English: speed each beat up (max 1.18x), then let it push the next one later
    keys = list(VO); t_free = 0.
    for i, k in enumerate(keys):
        st = max(VO[k], t_free)
        nxt = VO[keys[i + 1]] if i + 1 < len(keys) else END - 1.0
        d = len(load(f'vo_{DUB}/{k}.wav')) / SR
        tempo = min(max(d / max(nxt - st - .35, .1), 1.0), 1.18)
        x = load(f'vo_{DUB}/{k}.wav') if tempo == 1.0 else np.frombuffer(subprocess.run(
            ['ffmpeg', '-v', 'error', '-i', f'vo_{DUB}/{k}.wav', '-af', f'atempo={tempo:.4f}', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
            capture_output=True).stdout, np.float32).astype(np.float64)
        put(vo, st, x, 1.0); t_free = st + len(x) / SR + .35
        print(f'{k}: start {st:.2f} (en {VO[k]:.2f}) tempo {tempo:.2f} ends {st + len(x) / SR:.2f} / next {nxt:.2f}')
# sidechain-ish duck for music/sfx under VO
venv = lp_fast(np.abs(vo), 4.0); venv = np.clip(venv / (venv.max() * .25 + 1e-9), 0, 1)
duck = 1 - .55 * venv
sduck = np.full(N, .35); sduck[:int(T['b01'] * SR)] = .6   # cold open: effects sit further under the voice
mix_l = reverb(music, 3.0, .35) * duck * .9 + sfx * (1 - sduck * venv) + vo * 1.0
mix = np.stack([mix_l, mix_l], 1)
# a touch of stereo width on the score
mix[:, 0] += np.roll(music, 300) * duck * .12; mix[:, 1] -= np.roll(music, 300) * duck * .12
peak = np.abs(mix).max(); mix = mix / peak * .89
os.makedirs('out', exist_ok=True)
import wave
SUF = f'_{DUB}' if DUB else ''
with wave.open(f'out/film_audio{SUF}_raw.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'out/film_audio{SUF}_raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', '48000', f'out/film_audio{SUF}.wav'])
print('audio done')
