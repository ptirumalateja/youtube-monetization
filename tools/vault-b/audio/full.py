"""Vault B full 20 s master: block2.wav (0-10 s) + blocks 3-4.
10.0  hard cut to near-silence on the lamp; one heartbeat; the flames hiss as they lean   ("THEN THEY REACHED B.")
11.5  cobra heads: a slow breath, a stone creak                                             ("No handle. No lock.")
13.25 door seam: a distant low chant-like hum                                               ("They say only a chant can open it.")
15.0  shadow of a hand: heartbeat speeding up, stops dead at 16.25 when the hand stops
16.75 eyes: silence, room tone; one deep boom at 19.55 that hands over to the loop
python3 full.py OUT.wav   (needs ../output/anim/block2.wav from block2.py)
"""
import sys, os, wave
import numpy as np
from sfx import SR, fftconv, reverb_ir
import mix as M

HERE = os.path.dirname(os.path.abspath(__file__))
TOTAL = 20.0
rng = np.random.default_rng(31)


def mono2(x, d=0):
    return np.stack([x, np.roll(x, d)], 1)


def env(n, a, r):
    e = np.ones(n); ia, ir_ = max(1, int(a * SR)), max(1, int(r * SR))
    e[:ia] = np.linspace(0, 1, ia); e[-ir_:] = np.minimum(e[-ir_:], np.linspace(1, 0, ir_)); return e


def lp(x, k):
    return np.convolve(x, np.ones(k) / k, 'same')


def thump(f=52, dur=.28, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    fr = f * (1 + .6 * np.exp(-t / .02))
    return amp * np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t / .07) * (1 - np.exp(-t / .003))


def heartbeat(amp=1.0):
    a = thump(55, .3, amp); b = thump(48, .3, amp * .7)
    x = np.zeros(int(.5 * SR)); x[:len(a)] += a; j = int(.14 * SR); x[j:j + len(b)] += b[:len(x) - j]; return x


def breath(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = lp(x, 6) - lp(x, 60)                      # crude band-pass ~ 800 Hz - 8 kHz
    e = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 2
    return x * e * .5


def creak(dur):
    n = int(dur * SR); x = np.zeros(n); t = 0.0
    while t < dur:
        rate = 30 + 25 * np.sin(t * 3.1)
        t += 1 / rate * rng.uniform(.7, 1.3); i = int(t * SR)
        if i < n: x[i] += rng.uniform(.4, 1)
    res = np.zeros(int(.03 * SR)); tt = np.arange(len(res)) / SR
    for f, a in [(310, 1), (520, .6), (870, .35)]:
        res += a * np.sin(2 * np.pi * f * tt) * np.exp(-tt / .006)
    y = fftconv(x, res)[:n]
    return y * env(n, .2, .3)


def chant(dur, f0=98.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for f in (f0, f0 * 1.5, f0 * 2.003):
        for h in range(1, 18):
            fh = f * h
            w = np.exp(-((fh - 320) / 140) ** 2) + .45 * np.exp(-((fh - 800) / 220) ** 2) + .15 / h
            vib = 1 + .004 * np.sin(2 * np.pi * 5.1 * t + h)
            x += w * np.sin(2 * np.pi * fh * np.cumsum(vib) / SR) / h ** .3
    return x * env(n, .6, .5)


def main():
    out = sys.argv[1]
    N = int(TOTAL * SR); mx = np.zeros((N, 2))
    import wave as wv
    with wv.open(os.path.join(HERE, '..', 'output', 'anim', 'block2.wav')) as w:
        b2 = np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, 2) / 32767.0
    mx[:len(b2)] += b2
    at = lambda s: int(s * SR)
    def put(x, s, g, d=0):
        x2 = x if x.ndim == 2 else mono2(x, d)
        i = at(s); L = min(len(x2), N - i); mx[i:i + L] += x2[:L] * g
    room = lp(lp(lp(rng.standard_normal(N), 300), 300), 300); room /= np.abs(room).max()
    put(room[:at(10)] * env(at(10), 1.0, 1.0), 10.0, .05, 800)
    ir = reverb_ir(2.0, .6, .8)
    # 10-11.5 lamp: one heartbeat, flame hiss as they lean
    put(heartbeat(), 10.38, .7)
    hiss = lp(rng.standard_normal(at(1.0)), 3) * env(at(1.0), .3, .6)
    put(hiss / np.abs(hiss).max(), 10.2, .012, 300)
    # 11.5-13.25 heads: breath + stone creak
    br = breath(1.4); put(br / np.abs(br).max(), 11.6, .05, 500)
    cr = creak(.9); put(cr + .5 * fftconv(cr, ir)[:len(cr)], 12.3, .22, 200)
    # 13.25-15 seam: distant chant hum with long reverb
    ch = chant(2.0); ch = ch + .8 * fftconv(ch, reverb_ir(3.0, 1.2, .9))[:len(ch)]
    put(ch / np.abs(ch).max(), 13.25, .2, 900)
    # 15-16.75 hand: heartbeat speeding up, stops dead when the hand stops (16.25)
    t = 15.0; gap = .62
    while t < 16.2:
        put(heartbeat(.8 + (t - 15) * .3), t, .75); t += gap; gap *= .82
    # 16.75-20 eyes: room tone only, then the hit
    hit = M.load('bass-impact-512389.mp3')[:at(TOTAL - 19.55)]
    hit = hit / np.abs(hit).max() * env(len(hit), .002, .12)[:, None]
    put(hit, 19.55, .95)
    mx[-at(.01):] *= np.linspace(1, 0, at(.01))[:, None]
    M.write(out, mx)


if __name__ == '__main__':
    main()
