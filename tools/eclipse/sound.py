"""python3 sound.py OUT.wav   No music: recorded impacts, wind, bees, a gasp, and silence as a beat."""
import subprocess, sys
import numpy as np
SR = 48000; DUR = 21.0
L = '../sfxlib/'
def load(p):
    a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, 2).copy()
mix = np.zeros((int(SR * DUR), 2), np.float32)
def put(snd, t, gain=1., src0=0., src1=None, fi=.01, fo=.05, rate=1.):
    a = snd[int(src0 * SR): int(src1 * SR) if src1 else None]
    if rate != 1.:
        idx = np.arange(0, len(a) - 1, rate); a = np.stack([np.interp(idx, np.arange(len(a)), a[:, c]) for c in (0, 1)], 1)
    n = len(a); ramp = np.ones(n, np.float32)
    k = int(fi * SR); ramp[:k] *= np.linspace(0, 1, k) if k else 1
    k = int(fo * SR); ramp[n - k:] *= np.linspace(1, 0, k) if k else 1
    i0 = int(t * SR)
    if i0 < 0: a, ramp, i0 = a[-i0:], ramp[-i0:], 0
    n = min(len(a), len(mix) - i0)
    mix[i0:i0 + n] += a[:n] * ramp[:n, None] * gain
def db(x): return 10 ** (x / 20)

wind = load(L + '22331__sleepcircle__wind.ogg')
braam = load(L + '722633__chakong__cinematic-braaam.wav')
riser = load(L + '822420__audiopapkin__riser-hit-sfx-120.wav')
woosh = load(L + '649445__audiopapkin__cinematic-woosh-sfx-015.wav')
implo = load(L + '814047__qubodup__fantasy-implosion.wav')
plasma = load(L + '850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav')
susp = load(L + '869757__mikiko850__dark-suspense-accent.wav')
subby = load(L + '238375__stewdio2003__cp_subby_whoosh.aiff')
boom = load(L + '814046__qubodup__explosion-from-another-dimension.wav')
bees = load('sfx/bees.mp3'); gasp = load('sfx/gasp.mp3')

# HOOK: wind, then dead silence at second contact, braaam as the corona blooms (the loop seam is wind -> wind)
put(wind, 0., db(-20), 3., 3.7, fi=.0, fo=.15)
put(braam, .72 - 1.03 + .2, db(-3), .2, None, fi=.005, fo=1.2)
# LOCK-IN: cut to space, then the Moon's flight and the fit
put(subby, 2.5 - .44, db(-8), .3, None, fo=.6)
put(woosh, 5.35 - 2.55, db(-5), .8, None, fo=.4)
put(implo, 5.4, db(-6), 0., 3., fo=1.)
# BODY 1: shadow over Earth (low swell), hill: bees -> stop, wind dies, gasp
put(subby, 6.45, db(-12), 0., None, fo=1.)
put(bees, 8.2, db(-10), 0., 1.6, fi=.15, fo=.06)
put(bees, 8.2 + 1.4, db(-12), .3, .75, fi=.1, fo=.05)          # buzz runs to 10.05? no: hard stop below
mix[int(9.05 * SR):int(9.5 * SR)] *= 0                          # the bees stop: silence as a beat
put(wind, 8.2, db(-24), 10., 10.85, fi=.2, fo=.3)
put(gasp, 9.12, db(-9), 0., 1.5, fo=.4)
# REHOOK 1: short riser into one hit, then silence
put(riser, 10.0 - (6.10 - 5.5), db(-4), 5.5, 7.4, fi=.05, fo=.6)
# BODY 2: deep groan as the Moon drifts, plasma burst on the ring of fire
put(susp, 11.5, db(-9), 0., 4., fo=.8, rate=.8)
put(plasma, 12.85 - 1.68, db(-6), .8, 5.5, fi=.1, fo=1.)
# REHOOK 2: the last one; swell, then everything drops out on the flood of light
put(woosh, 16.95 - 2.55, db(-6), 1.0, 2.6, fo=.02)
put(boom, 15.05, db(-11), 0., 1.6, fo=.6)
mix[int(16.95 * SR):int(17.05 * SR)] *= 0
# CLOSE: biggest hit on the second corona bloom, then room tone and a faint gasp
put(braam, 17.05 - 1.03 + .2, db(0), .2, None, fi=.005, fo=1.5)
put(boom, 17.05, db(-8), 0., 2.5, fo=1.)
put(wind, 17.1, db(-28), 20., 22.4, fi=.4, fo=.3)
put(gasp, 18.4, db(-17), .1, 1.6, fo=.5)
# CTA: wind back in, matching frame 0 for the loop
put(wind, 19.6, db(-22), 1.6, 3.0, fi=.6, fo=.0)
mix[-int(.01 * SR):] *= np.linspace(1, 0, int(.01 * SR))[:, None]

# master: gentle limiting, loudness to about -14 LUFS
pk = np.abs(mix).max(); mix = np.tanh(mix / pk * 1.6) / np.tanh(1.6) * .89
out = sys.argv[1]
raw = out + '.raw.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', raw], input=mix.astype(np.float32).tobytes(), check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-ar', str(SR), out], check=True)
