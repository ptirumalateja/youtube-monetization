"""v4 sound: tense VO (sentence cuts from one take) + heartbeat/drone/risers + landing hits locked to fold landings. python3 sound3.py take.mp3 out.wav"""
import sys, math, subprocess, wave, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import tl4
from make3 import t_of, DUR
SR = 44100; N = int(SR * (DUR + 0.3)); rng = np.random.default_rng(9)
mix = np.zeros((2, N)); vo = np.zeros(N)
def T(n): return np.arange(n) / SR
def add(sig, t0, g=1.0, pan=0.0):
    i = int(t0 * SR)
    if i >= N or i < 0: return
    j = min(N, i + len(sig)); seg = sig[:j - i] * g
    mix[0, i:j] += seg * (1 - pan) ** .5 * .9; mix[1, i:j] += seg * (1 + pan) ** .5 * .9
def lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR); y = np.zeros_like(x); s = 0.
    for i in range(len(x)): s = (1 - a) * x[i] + a * s; y[i] = s
    return y
tt = T(N)
def env(p): xs, vs = zip(*p); return np.interp(tt, xs, vs)
# voice
for name, (s0, s1, tp) in tl4.SRC.items():
    out = f'/tmp/s4_{name}.wav'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{max(0, s0 - 0.02):.3f}', '-t', f'{s1 - s0 + 0.12:.3f}', '-i', sys.argv[1], '-af', f'atempo={tp},highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=60', '-ar', str(SR), '-ac', '1', out], check=True)
    with wave.open(out) as w: x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768.
    fi = int(.01 * SR); x[:fi] *= np.linspace(0, 1, fi); x[-fi:] *= np.linspace(1, 0, fi)
    i = int(tl4.P[name] * SR); j = min(N, i + len(x)); vo[i:j] += x[:j - i]
vo = vo / (np.abs(vo).max() + 1e-9) * 0.95
duck = np.clip(np.convolve((np.abs(vo) > 0.02).astype(float), np.ones(int(.2 * SR)) / int(.2 * SR), 'same') * 1.6, 0, 1); duck = 1 - 0.5 * duck
L30, L103, PK = t_of(30), t_of(103), tl4.P['S11']
# dark drone: detuned low saws rising in pitch/intensity, cut before the record line
dr = np.zeros(N); fr = 41 * (1 + 0.5 * np.clip(tt / L103, 0, 1) ** 1.5)
ph = 2 * np.pi * np.cumsum(fr) / SR
for k, a in [(1, .5), (1.5, .25), (2.02, .22), (3.01, .12), (4.03, .08)]: dr += a * np.sin(k * ph + k)
dr *= env([(0, 0), (.4, .35), (L30, .6), (L103, 1.0), (L103 + .3, .2), (PK - .6, .12), (PK - .5, 0), (DUR, 0)])
# dissonant tension layer (minor second) after the hook
tn = (np.sin(2 * np.pi * 466 * tt) + np.sin(2 * np.pi * 493.9 * tt)) * env([(0, 0), (tl4.P['S1'], 0), (L30, .07), (L103, .16), (L103 + .2, 0), (DUR, 0)])
bed = (dr + tn) * duck
mix[0] += bed * .5; mix[1] += np.roll(bed, 160) * .5
# heartbeat, speeds up 70 -> 170 bpm until 103
t = 0.4; hb = []
while t < L103 + .05:
    u = min(1, t / L103); bpm = 66 + 104 * u ** 1.6; per = 60 / bpm
    hb.append(t); t += per
for t in hb:
    for off, g in [(0, 1.0), (.14 * 60 / 90, .6)]:
        n = int(.18 * SR); x = T(n); k = np.sin(2 * np.pi * (58 * np.exp(-x * 18) + 34) * x) * np.exp(-x * 20); add(k, t + off, (.55 + .35 * min(1, t / L103)) * g)
def boom(t0, g, d=1.4):
    n = int(d * SR); x = T(n); f = 72 * np.exp(-x * 1.6) + 28
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 2.1) + .5 * lp(rng.standard_normal(n), 900) * np.exp(-x * 7), t0, g)
def riser(t1, d, g):  # noise sweep ending exactly at t1
    n = int(d * SR); u = T(n) / d; x = rng.standard_normal(n); o = np.zeros(n)
    for k, fc in enumerate(np.geomspace(250, 8000, 12)): o += lp(x, fc) * np.exp(-((u - k / 11) ** 2) / .05)
    o *= u ** 2; add(o / (np.abs(o).max() + 1e-9), t1 - d, g)
# fold landings: tick/crinkle exactly at landing
for f in range(1, 104):
    tl = t_of(f)
    if f <= 10:
        n = int(.09 * SR); x = lp(rng.standard_normal(n), 5200) - lp(rng.standard_normal(n), 700); x *= np.exp(-T(n) * 55); add(x, tl - .01, .5, -.2)
        add(np.sin(2 * np.pi * (90 + 6 * f) * T(int(.12 * SR))) * np.exp(-T(int(.12 * SR)) * 28), tl, .3, -.2)
    else:
        frq = 520 * 2 ** (f / 24. % 3.) * (1 if f < 60 else 1.12); n = int(.12 * SR)
        add((np.sin(2 * np.pi * frq * T(n)) + .3 * np.sin(2 * np.pi * frq * 2.01 * T(n))) * np.exp(-T(n) * 28), tl, .075, ((f * 37) % 11 - 5) / 12)
for f in [14, 22, 23, 42, 51, 69, 83]: boom(t_of(f), .45, .7)
riser(L30 - .02, 1.1, .5); boom(L30, .9, 1.0)
riser(L103 - .02, 1.5, .6); boom(L103, 1.2, 2.0)
add(np.sin(2 * np.pi * 98 * T(int(2.2 * SR))) * np.exp(-T(int(2.2 * SR)) * 1.5) * .5, PK - .35, .6)
for c in range(2): mix[c] = lp(mix[c], 12500)
mix = mix / np.abs(mix).max() * .66
mix += vo * 0.95
mix = np.tanh(mix * 1.1) / np.tanh(1.1) * .93
fd = np.ones(N); nf = int(.4 * SR); fd[-nf:] = np.linspace(1, 0, nf); mix *= fd
with wave.open(sys.argv[2], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('wrote', sys.argv[2], round(N / SR, 2))
