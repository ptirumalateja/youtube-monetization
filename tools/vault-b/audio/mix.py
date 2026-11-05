"""Hook mix from real CC0 Freesound SFX: coin pour (TheWoodlandNomad #363089) 0-2.5 s,
hard cut to silence, bass impact (Kievinay #512389) at 2.85 s with a stone-room tail
and a quiet synthesized crack/ring layer so the hit reads on phone speakers.
python3 mix.py OUT.wav
"""
import sys, os, wave, subprocess
import numpy as np
from sfx import SR, fftconv, reverb_ir, hit as synth_hit

HERE = os.path.dirname(os.path.abspath(__file__))
TOTAL, CUT, HIT = 5.0, 2.5, 2.85


def load(name):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'src', name), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).astype(np.float64)


def seg(x, a, b):
    return x[int(a * SR):int(b * SR)].copy()


def ramp(n, up=True):
    r = np.linspace(0, 1, n)[:, None]
    return r if up else 1 - r


def hook(TOTAL=TOTAL, tail_fade=.25):
    """0-TOTAL s hook bed (stereo float array, unnormalised)."""
    N = int(TOTAL * SR); mix = np.zeros((N, 2))
    coins = load('coins-pour-363089.wav')
    # densest run is 1.45-3.85 s, then a short gap; splice in the heavy section at 4.15 s with a 60 ms crossfade
    a, b = seg(coins, 1.45, 3.85), seg(coins, 4.15, 4.6)
    xf = int(.06 * SR)
    a[-xf:] = a[-xf:] * ramp(xf, False) + b[:xf] * ramp(xf)
    c = np.concatenate([a, b[xf:]])[:int(CUT * SR)]
    c[:int(.02 * SR)] *= ramp(int(.02 * SR))
    c[-int(.004 * SR):] *= ramp(int(.004 * SR), False)      # hard cut, 4 ms declick
    ir = reverb_ir(.9, .22, .5)
    wet = np.stack([fftconv(c[:, k], ir)[:len(c)] for k in range(2)], 1)
    c = c + .25 * wet
    c[-int(.004 * SR):] *= ramp(int(.004 * SR), False)
    mix[:len(c)] += c / np.abs(c).max() * .8
    hit = load('bass-impact-512389.mp3')[:int((TOTAL - HIT) * SR)]
    ir2 = reverb_ir(2.2, .7, .85)
    wet = np.stack([fftconv(hit[:, 0], ir2)[:len(hit)], np.roll(fftconv(hit[:, 1], ir2)[:len(hit)], 240)], 1)
    hit = hit + .5 * wet
    hit = hit / np.abs(hit).max()
    # phone speakers drop the sub: layer the synthesized hit's crack and metal ring underneath
    sl, sr_ = synth_hit(TOTAL - HIT)
    syn = np.stack([sl, sr_], 1)[:len(hit)]
    hit = hit + .35 * syn / np.abs(syn).max()
    i = int(HIT * SR)
    mix[i:i + len(hit)] += hit / np.abs(hit).max() * .95
    mix[-int(tail_fade * SR):] *= ramp(int(tail_fade * SR), False)
    return mix


def write(out, mix):
    mix = mix / np.abs(mix).max() * .93
    with wave.open(out, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((mix * 32767).astype('<i2').tobytes())
    print('wrote', out)


if __name__ == '__main__':
    write(sys.argv[1], hook())
