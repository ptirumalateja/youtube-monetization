"""Sound for the Vault B fact cut (v2), timed from timeline_v2. Leaves headroom for a voiceover bus (VO_WAV env).
python3 mix_v2.py OUT.wav
"""
import sys, os
import numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import timeline_v2 as T
from sfx import SR, fftconv, reverb_ir, hit as synth_hit
import mix as M
import block2 as B
import full as F

rng = np.random.default_rng(44)


def main():
    out = sys.argv[1]
    st, c = T.starts(); S = {k: v / 24 for k, v in st.items()}
    TOTAL = S['end']; N = int(TOTAL * SR); mx = np.zeros((N, 2))
    at = lambda s: int(s * SR)
    def put(x, s, g, d=0):
        x2 = x if x.ndim == 2 else F.mono2(x, d)
        i = at(s); L = min(len(x2), N - i)
        if L > 0: mx[i:i + L] += x2[:L] * g
    # gold: real coin pour for the whole shot, hard cut at the door
    coins = M.load('coins-pour-363089.wav')
    a, b = M.seg(coins, 1.45, 3.85), M.seg(coins, 4.15, 5.45); xf = int(.06 * SR)
    a[-xf:] = a[-xf:] * M.ramp(xf, False) + b[:xf] * M.ramp(xf)
    cc = np.concatenate([a, b[xf:]])[:at(S['door'])]
    cc[:at(.02)] *= M.ramp(at(.02)); cc[-at(.004):] *= M.ramp(at(.004), False)
    put(cc / np.abs(cc).max(), 0, .7)
    # door: silence, then the hit with the line
    hit = M.load('bass-impact-512389.mp3'); ir2 = reverb_ir(2.2, .7, .85)
    hw = hit + .5 * np.stack([fftconv(hit[:, k], ir2)[:len(hit)] for k in range(2)], 1); hw /= np.abs(hw).max()
    sl, sr_ = synth_hit(3.0); syn = np.stack([sl, sr_], 1)[:len(hw)]; hw[:len(syn)] += .35 * syn / np.abs(syn).max()
    th = T.raw_to_cut('door', 9); L = at(S['gopuram'] + 0.8 - th)
    seg = hw[:L] * F.env(L, .002, 1.0)[:, None]; put(seg / np.abs(seg).max(), th, .9)
    # gopuram: bell + drone + air
    g = S['gopuram']; dur = S['vaults'] - g
    bl = B.bell(5.0); put(bl / np.abs(bl).max(), g + .12, .38)
    d = B.drone(dur + .3, 55.0) * B.env(at(dur + .3), .6, .3); put(d / np.abs(d).max(), g, .15)
    ai = B.air(dur) * B.env(at(dur), .4, .05); put(ai / np.abs(ai).max(), g, .04)
    # vaults: low drone, a hit + coin shimmer per door
    v = S['vaults']; vd = S['lamp'] - v
    d2 = B.drone(vd, 41.2) * B.env(at(vd), .05, .05); put(d2 / np.abs(d2).max(), v, .18)
    sh = M.load('bass-impact-512389.mp3')[:at(1.1)]; sh = sh * B.env(len(sh), .002, .5); sh /= np.abs(sh).max()
    for k, rf in enumerate([3, 13, 22, 31, 40]):
        t = T.raw_to_cut('vaults', rf); put(sh, t, .5 + .07 * k)
        cs = M.seg(coins, 2.0 + k * .35, 2.0 + k * .35 + .7); cs = cs * B.env(len(cs), .08, .35); put(cs / np.abs(cs).max(), t + .12, .2)
    mx[at(S['lamp']) - at(.03):at(S['lamp'])] *= np.linspace(1, 0, at(.03))[:, None]
    mx[at(S['lamp']):] = 0      # hard cut to silence for the rehook
    # lamp -> eyes: room tone under everything
    room = F.lp(F.lp(F.lp(rng.standard_normal(N), 300), 300), 300); room /= np.abs(room).max()
    rl = N - at(S['lamp']); put(room[:rl] * F.env(rl, .8, .5), S['lamp'], .05, 800)
    put(F.heartbeat(), S['lamp'] + .35, .7)
    hs = F.lp(rng.standard_normal(at(1.2)), 3) * F.env(at(1.2), .3, .6); put(hs / np.abs(hs).max(), S['lamp'] + .2, .012, 300)
    br = F.breath(1.6); put(br / np.abs(br).max(), S['heads'] + .1, .05, 500)
    ir = reverb_ir(2.0, .6, .8); cr = F.creak(.9); put(cr + .5 * fftconv(cr, ir)[:len(cr)], S['heads'] + 1.0, .22, 200)
    ch = F.chant(S['hand'] - S['seam'] + .4); ch = ch + .8 * fftconv(ch, reverb_ir(3.0, 1.2, .9))[:len(ch)]; put(ch / np.abs(ch).max(), S['seam'], .2, 900)
    stop = T.raw_to_cut('hand', 30); t = S['hand'] + .1; gap = .7
    while t < stop - .15:
        put(F.heartbeat(.8 + (t - S['hand']) * .2), t, .75); t += gap; gap *= .85
    hb = M.load('bass-impact-512389.mp3'); tb = TOTAL - .6
    hb = hb[:at(TOTAL - tb)]; hb = hb / np.abs(hb).max() * F.env(len(hb), .002, .12)[:, None]; put(hb, tb, .95)
    vo = os.environ.get('VO_WAV')
    if vo:
        import wave
        with wave.open(vo) as w:
            x = np.frombuffer(w.readframes(w.getnframes()), '<i2').reshape(-1, w.getnchannels()) / 32767.0
        if x.shape[1] == 1: x = np.repeat(x, 2, 1)
        mx *= .55; put(x / np.abs(x).max(), float(os.environ.get('VO_AT', '0.15')), 1.0)
    mx[-at(.01):] *= np.linspace(1, 0, at(.01))[:, None]
    M.write(out, mx)


if __name__ == '__main__':
    main()
