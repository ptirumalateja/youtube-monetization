"""Sound for paper-fold v2: pad bed (ducked under VO), fold ticks, hits, whooshes, VO.  python3 sound2.py VO_DIR out.wav"""
import sys, math, subprocess, wave, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from make2 import NODES, n_of, t_of, DUR, VO
SR = 44100; N = int(SR * (DUR + 0.3)); rng = np.random.default_rng(5)
mix = np.zeros((2, N)); vo = np.zeros(N)
def T(n): return np.arange(n) / SR
def add(sig, t0, g=1.0, pan=0.0, bus=None):
    i = int(t0 * SR)
    if i >= N: return
    j = min(N, i + len(sig)); seg = sig[:j - i] * g
    mix[0, i:j] += seg * (1 - pan) ** .5 * .9; mix[1, i:j] += seg * (1 + pan) ** .5 * .9
def lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR); y = np.zeros_like(x); s = 0.
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
tt = T(N)
def env(p): xs, vs = zip(*p); return np.interp(tt, xs, vs)
# VO
for name, t0 in VO:
    out = f'/tmp/vo_{name}.wav'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{sys.argv[1]}/{name}.wav', '-af', 'atempo=1.064', '-ar', str(SR), '-ac', '1', out], check=True)
    with wave.open(out) as w: x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768.
    i = int(t0 * SR); j = min(N, i + len(x)); vo[i:j] += x[:j - i]
vo = vo / (np.abs(vo).max() + 1e-9) * 0.95
duck = np.clip(np.convolve((np.abs(vo) > 0.02).astype(float), np.ones(int(.25 * SR)) / int(.25 * SR), 'same') * 1.6, 0, 1)
duck = 1 - 0.55 * duck
# bed
pad = np.zeros(N)
for f, a in [(55, .5), (82.4, .4), (110, .35), (164.8, .25), (220, .2), (329.6, .12)]:
    pad += a * np.sin(2 * np.pi * f * (1 + .0035 * np.sin(2 * np.pi * (.13 + f / 700) * tt)) * tt + f)
br = sum(a * np.sin(2 * np.pi * f * tt + 2 * f) for f, a in [(440, .08), (659.3, .06), (880, .05), (1318.5, .03)])
bed = pad * env([(0, 0), (.3, .3), (5, .2), (15, .34), (28, .5), (28.3, .2), (32.4, .08), (32.7, 0), (35.3, 0), (35.6, .14), (37, .1)]) + br * env([(0, 0), (8, 0), (15, .6), (28, 1), (28.4, .1), (37, 0)])
bed *= duck
mix[0] += bed * .45; mix[1] += np.roll(bed, 200) * .45
# fold ticks
for f in range(1, 104):
    t = t_of(f) if f > 7 else 0.4 + (f - .35) / 7 * 4.8
    if f > 7 and f > 98: continue
    if t > 28.4: continue
    if f <= 7:
        n = int(.09 * SR); x = lp(rng.standard_normal(n), 5200) - lp(rng.standard_normal(n), 700); x *= np.exp(-T(n) * 55)
        add(x, t, .45, -.2); add(np.sin(2 * np.pi * (90 + 6 * f) * T(int(.12 * SR))) * np.exp(-T(int(.12 * SR)) * 28), t + .02, .3, -.2)
    else:
        fr = 520 * 2 ** (f / 24. % 3.) * (1 if f < 60 else 1.12); n = int(.14 * SR); x = (np.sin(2 * np.pi * fr * T(n)) + .3 * np.sin(2 * np.pi * fr * 2.01 * T(n))) * np.exp(-T(n) * 26)
        add(x, t, .09, ((f * 37) % 11 - 5) / 12)
def boom(t0, g, d=1.4):
    n = int(d * SR); x = T(n); f = 70 * np.exp(-x * 1.6) + 28
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.1) + .5 * lp(rng.standard_normal(n), 900) * np.exp(-x * 7), t0, g)
def whoosh(t0, d, g, up=True):
    n = int(d * SR); u = T(n) / d; x = rng.standard_normal(n); o = np.zeros(n)
    for k, fc in enumerate(np.geomspace(300, 7000, 12)): o += lp(x, fc) * np.exp(-((u - (k / 11 if up else 1 - k / 11)) ** 2) / .03)
    o *= np.sin(np.pi * u) ** 1.2; add(o / (np.abs(o).max() + 1e-9), t0, g)
whoosh(4.4, .8, .4); whoosh(14.0, 1.4, .5); boom(15.3, .9, 1.0); boom(28.3, 1.2, 2.2); whoosh(27.4, .9, .4)
add(np.sin(2 * np.pi * 110 * T(int(1.8 * SR))) * np.exp(-T(int(1.8 * SR)) * 1.7) * .5, 32.55, .6)
for c in range(2): mix[c] = lp(mix[c], 12500)
mix = mix / np.abs(mix).max() * .62
mix += vo * 0.85
mix = np.tanh(mix * 1.1) / np.tanh(1.1) * .93
fade = np.ones(N); nf = int(.4 * SR); fade[-nf:] = np.linspace(1, 0, nf); mix *= fade
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('wrote', sys.argv[2])
