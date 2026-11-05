"""Procedural SFX for the Vault B hook: coin cascade (0-2.5 s), hard cut to silence, one deep door hit.
python3 sfx.py OUT.wav [total_s=5.0] [cut_s=2.5] [hit_s=2.85]
"""
import sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(7)


def fftconv(x, h):
    n = len(x) + len(h) - 1
    N = 1 << (n - 1).bit_length()
    return np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(h, N), N)[:n]


def reverb_ir(sec, decay, bright=0.6):
    n = int(sec * SR); t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / decay)
    # darken tail: one-pole lowpass with falling cutoff approximated by blending
    lp = np.copy(ir)
    a = 1 - bright
    for i in range(1, n):
        lp[i] = a * lp[i - 1] + (1 - a) * ir[i]
    ir = lp; ir[0] = 1.0
    return ir / np.abs(ir).sum() * 18


def clink(f0, dur, amp):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for r, a, d in [(1, 1, 1), (1.47, .7, .8), (2.09, .55, .6), (2.76, .4, .45), (3.51, .3, .35), (4.4, .18, .25)]:
        f = f0 * r * (1 + rng.uniform(-.01, .01))
        if f > 19000: continue
        s += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / (dur * d * .35))
    click = rng.standard_normal(n) * np.exp(-t / .0012) * .6
    return (s + click) * amp


def thud(amp):
    n = int(.12 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * (220 - 600 * t) * t) * np.exp(-t / .025) + rng.standard_normal(n) * np.exp(-t / .006) * .5) * amp


def cascade(dur):
    n = int(dur * SR); L = np.zeros(n + SR); R = np.zeros(n + SR)
    t = 0.0
    while t < dur:
        rate = 40 + 110 * min(1, t / .5)            # clinks per second, swells in
        t += rng.exponential(1 / rate)
        f0 = rng.uniform(1900, 5200)
        c = clink(f0, rng.uniform(.06, .32), rng.uniform(.15, 1) ** 1.6)
        if rng.random() < .12:
            th = thud(rng.uniform(.3, .8))
            if len(c) < len(th): c = np.pad(c, (0, len(th) - len(c)))
            c[:len(th)] += th
        p = rng.uniform(.15, .85); i = int(t * SR)
        L[i:i + len(c)] += c * np.sqrt(1 - p); R[i:i + len(c)] += c * np.sqrt(p)
    # pile shimmer bed (filtered noise)
    bed = rng.standard_normal(n + SR)
    bed = np.diff(bed, prepend=0) * .018
    L += bed; R += bed[::-1] * 1
    ir = reverb_ir(1.2, .35, .5)
    L = L + .5 * fftconv(L, ir)[:len(L)]; R = R + .5 * fftconv(R, ir[::1])[:len(R)]
    return L[:n], R[:n]


def hit(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 52 * np.exp(-t / 1.2) + 30                   # pitch-dropping sub
    ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * np.exp(-t / .9)
    body = np.sin(2 * np.pi * 110 * t) * np.exp(-t / .18) * .5
    crack = rng.standard_normal(n) * np.exp(-t / .03) * .45
    metal = sum(np.sin(2 * np.pi * fr * t) * np.exp(-t / dc) * a for fr, dc, a in [(173, .8, .12), (311, .6, .08), (467, .5, .05)])
    x = sub + body + crack + metal
    x = np.tanh(x * 1.6) / np.tanh(1.6)
    ir = reverb_ir(2.4, .8, .85)
    wet = fftconv(x, ir)[:n]
    L = x + .9 * wet; R = x + .9 * np.roll(wet, 240)
    return L, R


def main():
    out = sys.argv[1]
    total = float(sys.argv[2]) if len(sys.argv) > 2 else 5.0
    cut = float(sys.argv[3]) if len(sys.argv) > 3 else 2.5
    hit_s = float(sys.argv[4]) if len(sys.argv) > 4 else 2.85
    N = int(total * SR); L = np.zeros(N); R = np.zeros(N)
    cl, cr = cascade(cut)
    fade = np.ones(len(cl)); fade[:int(.03 * SR)] = np.linspace(0, 1, int(.03 * SR))
    fade[-int(.004 * SR):] = np.linspace(1, 0, int(.004 * SR))   # hard cut, 4 ms declick
    L[:len(cl)] += cl * fade * .55; R[:len(cr)] += cr * fade * .55
    hl, hr = hit(total - hit_s)
    i = int(hit_s * SR)
    L[i:i + len(hl)] += hl * .9; R[i:i + len(hr)] += hr * .9
    tail = np.ones(N); tail[-int(.25 * SR):] = np.linspace(1, 0, int(.25 * SR))
    st = np.stack([L * tail, R * tail], 1)
    st = st / np.abs(st).max() * 0.93
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype('<i2').tobytes())
    print('wrote', out)


if __name__ == '__main__':
    main()
