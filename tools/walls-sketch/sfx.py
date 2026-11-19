# Action-synced SFX only (no music bed). Event times mirror scene.js. -> sfx.wav (stereo, 48k)
import numpy as np, wave, sys
SR = 48000; DUR = 14.2; N = int(SR * DUR)
L = np.zeros(N); R = np.zeros(N); rs = np.random.RandomState(11)

def biquad(x, kind, f, q=.7):
    w = 2 * np.pi * f / SR; a = np.sin(w) / (2 * q); c = np.cos(w)
    b = [(1 - c) / 2, 1 - c, (1 - c) / 2] if kind == 'lp' else [(1 + c) / 2, -(1 + c), (1 + c) / 2] if kind == 'hp' else [a, 0, -a]
    A = [1 + a, -2 * c, 1 - a]; b = [v / A[0] for v in b]; a1, a2 = A[1] / A[0], A[2] / A[0]
    y = np.zeros_like(x); x1 = x2 = y1 = y2 = 0.0
    for i in range(len(x)):
        v = b[0] * x[i] + b[1] * x1 + b[2] * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x[i], y1, v; y[i] = v
    return y
def env(n, att, dec):
    t = np.arange(n) / SR; return np.minimum(1, t / max(att, 1e-4)) * np.exp(-t / dec)
def place(sig, t, gain=1., pan=0.):
    i = int(t * SR); j = min(N, i + len(sig))
    if i >= N or j <= i: return
    s = sig[:j - i] * gain
    L[i:j] += s * np.sqrt((1 - pan) / 2) * 1.414; R[i:j] += s * np.sqrt((1 + pan) / 2) * 1.414
def clack(f=900, d=.09):  # brick set down on brick
    n = int(d * SR); t = np.arange(n) / SR
    body = (np.sin(2 * np.pi * f * t) + .6 * np.sin(2 * np.pi * f * 2.7 * t)) * env(n, .0005, .018)
    grit = biquad(rs.randn(n), 'bp', 3200, 1.) * env(n, .0003, .01)
    thud = np.sin(2 * np.pi * 140 * t) * env(n, .001, .03)
    return body * .5 + grit * .7 + thud * .6
def crunch(d=.25):  # brick cracking
    n = int(d * SR); x = biquad(rs.randn(n), 'bp', 1800, .9)
    gate = (rs.rand(n // 240 + 1) > .55).repeat(240)[:n] * 1.0
    return x * gate * env(n, .002, .09) * 2
def rumble(d=1.4):
    n = int(d * SR); t = np.arange(n) / SR
    x = biquad(rs.randn(n), 'lp', 220) * 3 + np.sin(2 * np.pi * 42 * t) * .7
    return x * np.minimum(1, t / .06) * np.exp(-t / .5)
def plink(f=1500):  # tear drop
    n = int(.25 * SR); t = np.arange(n) / SR
    ff = f * (1 + .6 * np.exp(-t * 40))
    return np.sin(2 * np.pi * np.cumsum(ff) / SR) * env(n, .001, .06)
def step(f=110):
    n = int(.15 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * env(n, .001, .03) + biquad(rs.randn(n), 'lp', 900) * env(n, .001, .02) * .8
def swell(d=1.0):  # regret: soft low tone
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 73 * t) + .3 * np.sin(2 * np.pi * 110 * t)) * np.sin(np.pi * t / d) ** 2
# S1: one clack per new row (rows = 1 + 19.5 (t/2.85)^.9)
for r in range(2, 21):
    t = 2.85 * ((r - 1) / 19.5) ** (1 / .9)
    place(clack(800 + rs.rand() * 300), t, .55 + .02 * r, rs.uniform(-.2, .2))
place(clack(600, .14), 2.88, .9)                    # last row lands
place(plink(1450), 4.75, .45, .15)                  # girl's tear lands
place(swell(1.1), 8.05, .35)                        # anger turns to regret
place(step(), 9.12, .5, -.2); place(step(95), 9.33, .5, -.1)
place(clack(500, .12), 9.37, .7)                    # hands on the wall
for k in range(5): place(crunch(.2 + rs.rand() * .1), 9.4 + k * .11, .55, rs.uniform(-.2, .3))
place(rumble(1.5), 10.0, .9, .1)                    # collapse
for k in range(16):
    place(clack(600 + rs.rand() * 500, .1), 10.05 + .68 * (k / 16) ** .8 + rs.rand() * .03, .35 + rs.rand() * .25, rs.uniform(-.4, .5))
place(plink(1350), 11.95, .35, -.1)                 # his tear
place(step(85), 12.95, .65); place(step(75), 13.2, .55)  # knees on the ground
st = np.stack([L, R], 1)
fi = int(13.8 * SR); st[fi:] *= np.linspace(1, 0, N - fi)[:, None]
st /= np.max(np.abs(st)) + 1e-9; st *= .89
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'sfx.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
