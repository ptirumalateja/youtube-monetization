# Original synthwave bed + count-up ticks + landing stabs + whooshes for "by the numbers" reels.
# usage: python3 mix.py <timeline.json> <out.wav>
import json, sys, subprocess, numpy as np
SR = 48000
tl = json.load(open(sys.argv[1])); T = tl['dur'] + 0.2; N = int(SR * T)
LIB = __file__.rsplit('/', 1)[0] + '/../sfxlib/'
out = np.zeros((N, 2), np.float32)
t = np.arange(N) / SR
rng = np.random.default_rng(3)

def add(x, at, g=1.0, pan=0.0):
    a = int(at * SR)
    if a >= N: return
    x = x[:N - a]
    if x.ndim == 1: x = np.stack([x * (1 - max(pan, 0)), x * (1 + min(pan, 0))], 1)
    out[a:a + len(x)] += x * g

def env(n, a=0.005, r=0.2):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / (r * SR)); return e

def load(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", LIB + f, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()

BPM = 118; beat = 60 / BPM
def note(m): return 440 * 2 ** ((m - 69) / 12)
# chords: Am F C G (one bar each)
prog = [(57, [57, 60, 64]), (53, [53, 57, 60]), (48, [55, 60, 64]), (55, [55, 59, 62])]
nb = int(T / beat) + 1
for b in range(nb):
    tb = b * beat; bar = (b // 4) % 4; root, ch = prog[bar]
    # kick every beat
    n = int(0.35 * SR); tt = np.arange(n) / SR
    k = np.sin(2 * np.pi * (45 + 120 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9)
    add(k, tb, 0.55)
    # snare on 2 and 4
    if b % 2 == 1:
        n = int(0.25 * SR); s = rng.standard_normal(n) * env(n, 0.001, 0.06) * 0.35
        s += np.sin(2 * np.pi * 190 * np.arange(n) / SR) * env(n, 0.001, 0.05) * 0.3
        add(s, tb, 0.5)
    # hats on offbeats (16ths light)
    for q in range(4):
        n = int(0.05 * SR); h = rng.standard_normal(n); h = np.diff(np.concatenate([[0], h])) * env(n, 0.001, 0.012)
        add(h, tb + q * beat / 4, 0.09 if q % 2 else 0.05, pan=0.3 if q % 2 else -0.3)
    # bass: 8th-note octave pulse
    for e8 in range(2):
        n = int(beat / 2 * SR); tt = np.arange(n) / SR; f = note(root - 12 + (12 if e8 else 0))
        saw = 2 * ((f * tt) % 1) - 1; lp = np.convolve(saw, np.ones(18) / 18, 'same')
        add(lp * env(n, 0.003, 0.12) * 0.3, tb + e8 * beat / 2)
    # arp (16ths) over chord, quieter
    for q in range(4):
        m = ch[(b * 4 + q) % 3] + 12; n = int(beat / 4 * SR); tt = np.arange(n) / SR
        sq = np.sign(np.sin(2 * np.pi * note(m) * tt)) * 0.5 + np.sin(2 * np.pi * note(m) * tt) * 0.5
        add(sq * env(n, 0.002, 0.05) * 0.06, tb + q * beat / 4, pan=0.4 * np.sin(b))
# pad (whole bars)
for bar in range(int(T / (4 * beat)) + 1):
    root, ch = prog[bar % 4]; n = int(4 * beat * SR); tt = np.arange(n) / SR
    p = sum(np.sin(2 * np.pi * note(m) * tt + 0.3 * np.sin(2 * np.pi * 5 * tt)) for m in ch)
    e = np.minimum(1, tt / 0.4) * np.minimum(1, (4 * beat - tt) / 0.4)
    add(np.stack([p * e, np.roll(p, 300) * e], 1) * 0.035, bar * 4 * beat)

bed = out.copy(); out[:] = 0
# sfx
wh = load('649445__audiopapkin__cinematic-woosh-sfx-015.wav')
for s in tl['scenes']:
    t0 = s['t0']; inst = s.get('instant', False)
    if t0 > 0: add(wh[:int(0.9 * SR)], t0 - 0.3, 0.45)
    if s['type'] == 'stat':
        c0, c1 = (0.0, 0.6) if inst else (0.15, 1.0)
        k = 0; tk = c0
        while tk < c1:  # count-up ticks, accelerating
            n = int(0.02 * SR); tt = np.arange(n) / SR
            add(np.sin(2 * np.pi * (2400 + 300 * k % 3) * tt) * env(n, 0.0005, 0.006), t0 + tk, 0.12)
            tk += max(0.035, 0.09 - k * 0.006); k += 1
        land = t0 + (0.6 if inst else 1.0)
        n = int(0.8 * SR); tt = np.arange(n) / SR  # bright landing stab
        st = sum(np.sin(2 * np.pi * note(m) * tt) for m in (76, 81, 88)) * env(n, 0.002, 0.25)
        st += rng.standard_normal(n) * env(n, 0.001, 0.03) * 0.4
        add(st * 0.22, land)
        if s.get('chip'):
            n = int(0.25 * SR); tt = np.arange(n) / SR
            add(np.sin(2 * np.pi * note(84) * tt) * env(n, 0.002, 0.08) * 0.15, land + 0.75)
    if s['type'] == 'vs':
        n = int(1.0 * SR); tt = np.arange(n) / SR  # rising tone as GTA bar grows
        add(np.sin(2 * np.pi * (300 + 500 * tt) * tt) * np.minimum(1, tt / 0.2) * np.exp(-np.maximum(0, tt - 0.8) * 20) * 0.08, t0 + 1.1)
        n = int(0.8 * SR); tt = np.arange(n) / SR
        add(sum(np.sin(2 * np.pi * note(m) * tt) for m in (72, 79, 84)) * env(n, 0.002, 0.3) * 0.22, t0 + 2.0)
mix = bed * 0.8 + out
fi = int(0.004 * SR); mix[:fi] *= np.linspace(0, 1, fi)[:, None]
fo = int(0.6 * SR); mix[-fo:] *= np.linspace(1, 0, fo)[:, None]
mix = np.tanh(mix * 1.4) / np.tanh(1.4)
mix *= 0.89 / np.abs(mix).max()
import wave
w = wave.open(sys.argv[2], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print('ok', T)
