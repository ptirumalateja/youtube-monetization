"""Sound for Normal People vs Me: no music. Recorded clips only (Teja's ElevenLabs set in sfx/, plus one sfxlib hit), a quiet
night room tone with a clock tick, and hard silence as a beat (before the rooster, on the 3:00 slam).

  python3 mix.py OUT.wav
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import sld_sound as S
from sld_sound import SR, place, write_wav
DUR = 19.9
SFX = os.path.join(HERE, 'sfx')

def clip(name):
    x = S.load(os.path.join(SFX, name + '.wav')) if not name.startswith('lib:') else S.load(name[4:])
    return x
def rms_db(x):
    e = np.sqrt(np.convolve(x ** 2, np.ones(2400) / 2400, 'same')); act = x[e > 0.1 * e.max()]
    return 20 * np.log10(np.sqrt(np.mean(act ** 2)) + 1e-9)
def at_level(x, db):
    return x * 10 ** ((db - rms_db(x)) / 20)
def peak_t(x):
    e = np.convolve(np.abs(x), np.ones(480) / 480, 'same'); return int(np.argmax(e))
def cut(x, a, b, fade=0.06):
    y = x[int(a * SR):int(b * SR)].copy(); n = int(fade * SR)
    if n and len(y) > 2 * n: y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n)
    return y
def put(bus, x, t, align='start', pan=0.0):
    """Place x so its start (or its loudest point, align='peak') lands at time t."""
    off = peak_t(x) / SR if align == 'peak' else 0.0
    place(bus, x, t - off, 1.0, pan)
def speedup(x, r0, r1):
    """Play x with the rate ramping r0 -> r1 (taps get faster and a little higher)."""
    n = len(x); rate = np.linspace(r0, r1, n); pos = np.cumsum(rate); pos = pos[pos < n - 1]
    return np.interp(pos, np.arange(n), x)

def build():
    fx = np.zeros((2, int(DUR * SR) + SR)); bed = np.zeros_like(fx)
    # room tone: the night bed, looped; it drops out for the hard silences
    rt = at_level(clip('room_tone'), -44); rt = np.concatenate([rt, rt])[:bed.shape[1]]; bed[0] += rt; bed[1] += rt
    hit = S.load('822420__audiopapkin__riser-hit-sfx-120.wav'); hp = peak_t(hit); hit = at_level(hit[max(0, hp - int(0.02 * SR)):hp + int(1.6 * SR)], -15)
    flop = at_level(clip('flop_on_bed'), -18); swish = at_level(cut(clip('blanket_kick'), 0.3, 1.1), -26)
    # NORMAL: flop, blanket up, one snore
    put(fx, flop, 0.36, 'peak'); put(fx, swish, 0.75, 'peak', 0.2); put(fx, at_level(clip('snore'), -24), 1.85, 'start')
    # ME: the same flop; then the eyes snap open into silence
    put(fx, flop, 2.4 + 0.36, 'peak'); put(fx, swish, 2.4 + 0.75, 'peak', 0.2)
    # the three turns
    put(fx, at_level(clip('roll_over'), -20), 4.0, 'start', -0.15)
    put(fx, at_level(clip('pillow_groan'), -18), 5.02, 'start')
    put(fx, at_level(clip('blanket_kick'), -17), 6.06, 'peak', 0.2)
    # the buzz on the nightstand, then the grab and the scrolling (speeding up through the time-lapse)
    put(fx, at_level(clip('phone_buzz'), -19), 6.5, 'start', 0.45)
    put(fx, at_level(cut(clip('blanket_kick'), 0.35, 0.9), -27), 7.1, 'start', 0.3)
    scr = at_level(clip('phone_scrolling'), -25); scr2 = speedup(np.concatenate([scr, scr, scr]), 1.0, 1.9)
    put(fx, cut(scr, 0.2, 1.5), 7.45, 'start'); put(fx, cut(scr2, 0, 2.1, 0.03), 8.4, 'start')
    # 3:00 slam: the hit, then dead silence for a beat; the laugh, then hand over the mouth
    put(fx, hit, 10.5, 'start')
    put(fx, at_level(cut(clip('big_laugh'), 0.0, 1.3, 0.04), -13), 10.62, 'start')
    put(fx, at_level(cut(clip('muffled_laugh'), 0.0, 1.25, 0.08), -17), 11.68, 'start')
    # silence ... the crow
    put(fx, at_level(cut(clip('rooster'), 0.0, 1.2, 0.05), -11), 13.42, 'start', -0.2)
    # 5:00: shock, then the phone lands on his face
    put(fx, hit * 0.8, 14.6, 'start'); put(fx, at_level(clip('shock_gasp'), -14), 14.64, 'start')
    put(fx, at_level(cut(clip('phone_buzz'), 0.0, 0.58, 0.03), -15), 15.05, 'start', 0.1)   # the alarm screen, seen from his eyes
    put(fx, at_level(clip('phone_on_face'), -13), 15.82, 'peak')
    # bolt upright, the alarm line holds in near silence; he flops back and the loop's first flop lands at 0.36
    put(fx, at_level(cut(clip('blanket_kick'), 0.3, 1.1), -20), 16.12, 'peak', 0.1)
    put(fx, at_level(cut(clip('roll_over'), 0.0, 1.0), -24), 19.0, 'start')
    # hard silences: room tone out before the crow and right on the slam
    g = np.ones(bed.shape[1]); t = np.arange(bed.shape[1]) / SR
    for a, b in [(10.48, 10.62), (12.85, 13.42)]:
        g *= 1 - np.clip(np.minimum((t - a) / 0.04, (b - t) / 0.04), 0, 1)
    bed *= g
    fxg = np.ones_like(g)
    fxg *= 1 - np.clip(np.minimum((t - 12.88) / 0.05, (13.40 - t) / 0.02), 0, 1)   # the laugh tail is cut to nothing before the crow
    fx *= fxg
    room = S.convolve(fx[0] + fx[1], S.reverb_ir(0.45, 5000, 3)) * 0.06
    mix = fx + bed + np.stack([room, room])[:, :fx.shape[1]]
    return mix[:, :int(DUR * SR)]

if __name__ == '__main__':
    write_wav(build() * 0.9, sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'output', 'mix.wav'))
