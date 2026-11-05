"""0-10 s Vault B master: hook (mix.hook) + block 2.
5.0 s  gopuram at dawn: temple bell strike, low drone, soft morning air; the hook's hit rings out under it.
7.5 s  vault corridor: drone drops an octave; one heavy door hit as each of A C D E F starts to swing,
       each followed by a little coin shimmer as gold slides over the threshold.
python3 block2.py OUT.wav
"""
import sys
import numpy as np
from sfx import SR, fftconv, reverb_ir
import mix as M

TOTAL = 10.0
GOP, VAULT = 5.0, 7.5
DOOR_STARTS = [3, 13, 22, 31, 40]          # frames in vaults.py
rng = np.random.default_rng(12)


def bell(dur, f0=620.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for r, a, d in [(0.5, .5, 3.2), (1.0, 1.0, 2.4), (1.19, .55, 1.8), (1.5, .45, 1.5), (2.0, .4, 1.2), (2.52, .3, .9), (2.98, .22, .7), (4.07, .15, .5)]:
        f = f0 * r
        beat = 1 + 0.12 * np.sin(2 * np.pi * (1.3 + r * .4) * t)    # slow shimmer between near-degenerate modes
        x += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.3)) * np.exp(-t / d) * beat
    strike = rng.standard_normal(n) * np.exp(-t / .004) * .5
    x = x + strike
    ir = reverb_ir(3.0, 1.1, .7)
    wet = fftconv(x, ir)[:n]
    return np.stack([x + .6 * wet, x + .6 * np.roll(wet, 300)], 1)


def drone(dur, f):
    n = int(dur * SR); t = np.arange(n) / SR
    x = sum(a * np.sin(2 * np.pi * f * h * t + p) for h, a, p in [(1, 1, 0), (2, .35, 1), (3, .12, 2), (1.005, .6, 3)])
    lfo = 0.85 + 0.15 * np.sin(2 * np.pi * .3 * t)
    return np.stack([x * lfo, np.roll(x, 400) * lfo], 1)


def air(dur):
    n = int(dur * SR)
    x = rng.standard_normal((n, 2))
    k = np.ones(200) / 200                      # soft lowpassed morning air
    return np.stack([np.convolve(x[:, i], k, 'same') for i in range(2)], 1) * 3


def env(n, a, r):
    e = np.ones((n, 1)); ia, ir_ = int(a * SR), int(r * SR)
    e[:ia, 0] = np.linspace(0, 1, ia); e[-ir_:, 0] = np.linspace(1, 0, ir_); return e


def main():
    out = sys.argv[1]
    N = int(TOTAL * SR); mx = np.zeros((N, 2))
    h = M.hook(TOTAL=6.2, tail_fade=1.0)           # hit at 2.85 rings out under the gopuram
    mx[:len(h)] += h / np.abs(h).max() * .95
    # gopuram
    g0 = int(GOP * SR)
    b = bell(5.0); mx[g0 + int(.12 * SR):g0 + int(.12 * SR) + len(b)][:len(b)] += (b / np.abs(b).max() * .42)[:N - g0 - int(.12 * SR)]
    d = drone(VAULT - GOP + .3, 55.0) * env(int((VAULT - GOP + .3) * SR), .6, .3)
    mx[g0:g0 + len(d)] += d / np.abs(d).max() * .16
    a_ = air(VAULT - GOP) * env(int((VAULT - GOP) * SR), .4, .05)
    mx[g0:g0 + len(a_)] += a_ / np.abs(a_).max() * .05
    # vault corridor
    v0 = int(VAULT * SR); vd = TOTAL - VAULT
    d2 = drone(vd, 41.2) * env(int(vd * SR), .05, .2)
    mx[v0:v0 + len(d2)] += d2 / np.abs(d2).max() * .2
    hit = M.load('bass-impact-512389.mp3')[:int(1.1 * SR)]
    hit *= env(len(hit), .002, .5)
    hit = hit / np.abs(hit).max()
    coins = M.load('coins-pour-363089.wav')
    for k, st in enumerate(DOOR_STARTS):
        i = v0 + int(st / 24 * SR)
        gain = .55 + .08 * k
        L = min(len(hit), N - i); mx[i:i + L] += hit[:L] * gain
        c = M.seg(coins, 2.0 + k * .35, 2.0 + k * .35 + .7); c *= env(len(c), .08, .35)
        j = i + int(.12 * SR); L = min(len(c), N - j); mx[j:j + L] += (c / np.abs(c).max() * .22)[:L]
    mx[-int(.03 * SR):] *= np.linspace(1, 0, int(.03 * SR))[:, None]
    M.write(out, mx)


if __name__ == '__main__':
    main()
