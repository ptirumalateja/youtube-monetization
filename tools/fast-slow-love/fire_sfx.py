# Procedural campfire audio. Envelopes mirror scene.js topFire/botFire. -> fire.wav (mono)
import numpy as np, wave, sys
SR = 48000; DUR = 13.6; N = int(SR * DUR); t = np.arange(N) / SR
rs = np.random.RandomState(3)
sm = lambda a, b, x: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
def lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); acc = 0.0
    # one-pole via cumulative filter (scipy-free)
    from itertools import accumulate
    return np.array(list(accumulate(x * (1 - a), lambda p, v: p * a + v)))
# fire size envelopes (same shape as the visuals)
lands = [0.62, 0.77, 1.07, 1.22, 1.52, 1.70]  # approximate log landings top
top = .38 + sum(.11 * sm(l, l + .2, t) for l in lands)
top = top + .85 * sm(5.0, 5.35, t) * (1 - sm(5.9, 6.6, t))
top = top * (1 - sm(6.1, 7.55, t)); top[t > 7.55] = 0
bot = .66 + .1 * sm(4, 13, t)
def fire(env, seed, rate):
    r = np.random.RandomState(seed)
    roar = lp(r.randn(N), 380) * 3.0
    hiss = lp(r.randn(N), 4000) - lp(r.randn(N), 1500)
    cr = np.zeros(N)
    k = 0
    while k < N:
        k += int(r.exponential(SR / (rate * max(env[min(k, N - 1)], .05))))
        if k >= N: break
        if env[k] < .03: continue
        L = int(SR * r.uniform(.002, .012)); amp = r.uniform(.2, 1) * (1.6 if r.rand() < .08 else 1)
        burst = r.randn(L) * np.exp(-np.arange(L) / (L / 4)) * amp
        cr[k:k + L] += burst[:N - k]
    return env * (roar * .5 + hiss * .25) + np.sqrt(np.clip(env, 0, None)) * cr * .5
a = fire(top, 11, 22) ; b = fire(bot, 23, 16) * .8
# flare whoosh at seat log landing (5.08 s)
w = np.zeros(N); i0 = int(5.0 * SR); L = int(1.2 * SR)
env = np.sin(np.linspace(0, np.pi, L)) ** 2 * np.exp(-np.linspace(0, 3, L))
w[i0:i0 + L] = lp(rs.randn(L + 0), 600)[:L] * env * 6
outp = a + b + w
outp /= np.max(np.abs(outp)) + 1e-9; outp *= .8
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'fire.wav', 'wb') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((outp * 32767).astype(np.int16).tobytes())
