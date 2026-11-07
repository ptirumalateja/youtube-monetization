"""v5 sound: tense VO beats (one take, cut + sped), heartbeat, recorded sfx (tools/sfxlib), paper ticks locked to fold landings, silence before the record line.
python3 sound4.py take.mp3 sfxdir out.wav"""
import sys, math, subprocess, wave, numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import tl6 as tl5
from make5 import t_of, DUR, T_D
SR = 44100; N = int(SR * (DUR + 0.3)); rng = np.random.default_rng(3)
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
def load(path, mono=True, af=None):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-i', path] + (['-af', af] if af else []) + ['-ar', str(SR), '-ac', '1', '-f', 'wav', '/tmp/_l.wav']
    subprocess.run(cmd, check=True)
    with wave.open('/tmp/_l.wav') as w: return np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768.
def sfx_at_peak(name, t_peak, g, maxlen=None, af=None):
    x = load(f'{sys.argv[2]}/{name}', af=af); pk = int(np.argmax(np.abs(x))); sig = x
    add(sig, t_peak - pk / SR, g)
TAKES = {'v4': '/mnt/project-files/paper-fold/vo4/take.mp3', 'v5': sys.argv[1]}
# ---- voice beats
for name, (parts, tempo) in tl5.PARTS.items():
    pieces = []
    for (key, a, b) in parts:
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', f'{a:.3f}', '-t', f'{b - a:.3f}', '-i', TAKES[key], '-af', f'atempo={tempo},highpass=f=90,acompressor=threshold=-20dB:ratio=3:attack=5:release=60', '-ar', str(SR), '-ac', '1', '/tmp/_p.wav'], check=True)
        with wave.open('/tmp/_p.wav') as w: x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768.
        fi = min(len(x) // 2, int(.012 * SR)); x = x.copy(); x[:fi] *= np.linspace(0, 1, fi); fo = min(len(x) // 2, int(.05 * SR)); x[-fo:] *= np.linspace(1, 0, fo)
        pieces += [x, np.zeros(int(.03 * SR))]
    x = np.concatenate(pieces[:-1]); i = int(tl5.P[name] * SR); j = min(N, i + len(x)); vo[i:j] += x[:j - i]
vo = vo / (np.abs(vo).max() + 1e-9) * 0.95
duck = np.clip(np.convolve((np.abs(vo) > 0.02).astype(float), np.ones(int(.2 * SR)) / int(.2 * SR), 'same') * 1.6, 0, 1); duck = 1 - 0.45 * duck
L30, L103, PR = t_of(30), tl5.T_103, tl5.P['REC']
# ---- heartbeat: starts in the hook, quickens through the folds, stops dead before the record line
hb = []; t = 0.3
while t < L103 + .05:
    if t < T_D - .3 or t > T_D + .2:
        u = 0.0 if t < T_D else min(1, (t - T_D) / (L103 - T_D)); bpm = 62 + 108 * u ** 1.5; hb.append(t)
    else: bpm = 62
    t += 60 / bpm
hbl = np.zeros((2, N)); store = mix; mix = hbl
for t in hb:
    u = min(1, max(0, (t - T_D) / (L103 - T_D))) if t > T_D else 0.25
    for off, g in [(0, 1.0), (.15 * 60 / 80, .55)]:
        n = int(.2 * SR); x = T(n); k = np.sin(2 * np.pi * (60 * np.exp(-x * 16) + 36) * x) * np.exp(-x * 17); add(k, t + off, (.5 + .4 * u) * g)
mix = store; mix += hbl * duck
# ---- paper: crinkle + thud on desk folds, soft glass ticks later, all on the landing frame
for f in range(1, 104):
    tl = t_of(f)
    if f <= 10:
        n = int(.1 * SR); x = lp(rng.standard_normal(n), 5200) - lp(rng.standard_normal(n), 700); x *= np.exp(-T(n) * 50); add(x, tl - .012, .55, -.2)
        add(np.sin(2 * np.pi * (90 + 6 * f) * T(int(.12 * SR))) * np.exp(-T(int(.12 * SR)) * 26), tl, .32, -.2)
    else:
        frq = 520 * 2 ** (f / 24. % 3.) * (1 if f < 60 else 1.12); n = int(.1 * SR)
        add((np.sin(2 * np.pi * frq * T(n)) + .3 * np.sin(2 * np.pi * frq * 2.01 * T(n))) * np.exp(-T(n) * 30), tl, .06, ((f * 37) % 11 - 5) / 12)
# ---- recorded impacts
sfx_at_peak('822420__audiopapkin__riser-hit-sfx-120.wav', L30, .9)          # into space
sfx_at_peak('722633__chakong__cinematic-braaam.wav', L103, 1.0)              # 103rd fold
sfx_at_peak('869757__mikiko850__dark-suspense-accent.wav', PR + .1, .55)     # the record line
for f in [14, 22, 23, 42, 51, 69, 83]:
    n = int(.6 * SR); x = T(n); add(np.sin(2 * np.pi * (70 * np.exp(-x * 5) + 36) * x) * np.exp(-x * 5), t_of(f), .5)
# silence beat: kill everything except the VO between the 103 payoff tail and the record line
gate = np.ones(N); a, b = int((L103 + 2.2) * SR), int((PR - .05) * SR)
if b > a: gate[a:b] = 0.0
mix *= gate
for c in range(2): mix[c] = lp(mix[c], 12500)
mix = mix / np.abs(mix).max() * .7
mix += vo * 0.95
mix = np.tanh(mix * 1.1) / np.tanh(1.1) * .93
fd = np.ones(N); nf = int(.4 * SR); fd[-nf:] = np.linspace(1, 0, nf); mix *= fd
with wave.open(sys.argv[3], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((mix.T * 32767).astype('<i2').tobytes())
print('wrote', sys.argv[3], round(N / SR, 2))
