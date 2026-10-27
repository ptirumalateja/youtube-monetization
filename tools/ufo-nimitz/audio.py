"""Synthesised score + sound design + VO mix for the Tic Tac film (no stock audio).
python3 audio.py -> out/film_audio.wav (48 kHz stereo). Cue times match edit.py.
DUB=hi|te python3 audio.py -> out/film_audio_<lang>.wav, narration from vo_<lang>/ fitted to the English beats."""
import numpy as np, subprocess, os
from edit import VO, END
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

put(music, 0.0, pad(9.0, [D2, A2, D3], .10))
put(music, 11.3, pad(18.4, [D2, A2, F3], .11))
put(music, 11.3, pulse(18.0, 90, g=.25))
put(music, 29.2, pad(23.5, [D2, F2, A2, E3], .10, 420))
put(music, 52.3, pad(22.6, [Bb2, F3, D3], .10, 420))
put(music, 74.8, pad(24.4, [D2, A2, C3, E3], .11, 600))
put(music, 85.8, riser(13.2), .55)
put(music, 99.0, pad(11.0, [D2, A2, D3, F3], .12, 700))
put(music, 99.0, pulse(10.5, 120, g=.32))
put(music, 112.0, pad(8.0, [D2, A2], .07, 300))
put(music, 120.2, pad(10.4, [D2, F2, A2], .09))
put(music, 130.4, pad(40.6, [D2, A2, D3, E3], .09, 450))
put(music, 130.4, pulse(40.0, 76, g=.18))
put(music, 171.0, pad(29.0, [Bb2, D3, F3], .06, 380))
put(music, 200.0, pad(17.2, [C3, E3, G3], .09, 600))
put(music, 217.2, pad(15.8, [D2, A2, D3, F3, A3], .11, 900))
put(music, 217.2, pulse(15.8, 104, g=.32))
put(music, 233.0, pad(16.4, [D2, A2, D3, F3], .13, 1200))
put(music, 233.0, pulse(16.4, 124, g=.5))
put(music, 249.4, pad(23.0, [D2, F2, A2, C3], .10, 500))
put(music, 272.4, pad(14.0, [D2, Bb2, E3], .07, 300))
put(music, 286.4, pad(19.8, [D2, A2, E3], .09, 450))
put(music, 306.2, pad(22.0, [D2, F2, A2, D3, F3, A3], .12, 900))
put(music, 328.2, pad(7.8, [D2, A2, D3, F3], .12, 700))

# ---------------- sound design
put(sfx, 0.0, lp_fast(rng.normal(0, 1, int(8.9 * SR)), 180) * .25)    # sensor hum
put(sfx, 8.9, boom(3.0), .95)
put(sfx, 9.15, rewind(), .8)
put(sfx, 26.3, whoosh(.8), .6)
for s, d in ((37.4, 14.9), (70.4, 4.4)):
    k = 0.0
    while k < d:
        put(sfx, s + k + .2, ping(), .5); k += 2 * np.pi / 1.6
put(sfx, 52.3, jet_rumble(13.3), .45)
put(sfx, 55.5, whoosh(.9), .7)            # catapult shot
put(sfx, 130.4, jet_rumble(4.4), .45)
put(sfx, 130.3, whoosh(.9), .6)
put(sfx, 33.7, whoosh(.6), .4)
put(sfx, 70.4, hit(), .7)
put(sfx, 74.8, jet_rumble(11.0), .3)
put(sfx, 79.8, wind(19.2), 1.0)
put(sfx, 99.0, jet_rumble(10.0), .35)
put(sfx, 99.0, heartbeat(10.0, 70), .5)
put(sfx, 109.4, whoosh(1.0), .9)
put(sfx, 110.2, boom(3.5, 90, 25), 1.0)
put(sfx, 112.0, wind(6.0), .8)
put(sfx, 121.8, snap(), .7)
put(sfx, 124.6, hit(), .85)
put(sfx, 160.8, hit(1.2), .5)
put(sfx, 199.6, whoosh(1.0), .6)
put(sfx, 206.0, hit(), .6)
for s in (225.4, 228.4, 230.4): put(sfx, s, hit(), .7)
put(sfx, 232.6, whoosh(.6), .7)
for s in (233.0, 235.8, 237.9, 241.2, 245.2): put(sfx, s, hit(1.0), .5)
put(sfx, 249.0, whoosh(.8), .6)
put(sfx, 262.0, hit(), .6)
put(sfx, 266.4, hit(), .6)
put(sfx, 272.4, wind(14.0), .6)
put(sfx, 289.6, hit(), .8)
put(sfx, 292.2, hit(), .8)
put(sfx, 298.4, boom(2.5), .6)
put(sfx, 328.2, boom(3.0, 60, 30), .4)

# ---------------- real cockpit audio from GOFAST (U.S. Navy, public domain)
def load(path, ss=0, d=None):
    cmd = ['ffmpeg', '-v', 'error', '-ss', str(ss), '-i', path] + (['-t', str(d)] if d else []) + ['-f', 'f32le', '-ac', '1', '-ar', str(SR), '-']
    return np.frombuffer(subprocess.run(cmd, capture_output=True).stdout, np.float32).astype(np.float64)
go = load('src/gofast.mp4', 0, 29.0)
go_env = np.ones(len(go)); go_env[int(3.0 * SR):] = .28   # duck under narration after 3 s
put(sfx, 171.0, go * go_env, 1.4)

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
mix_l = reverb(music, 3.0, .35) * duck * .9 + sfx * (1 - .35 * venv) + vo * 1.0
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
