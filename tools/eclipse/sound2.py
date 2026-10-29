"""python3 sound2.py OUT.wav  Helium cut: no music. Recorded hits, wind, bees that stop, a crowd gasp, hard silences."""
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
    k = min(int(fi * SR), n); 
    if k: ramp[:k] *= np.linspace(0, 1, k)
    k = min(int(fo * SR), n)
    if k: ramp[n - k:] *= np.linspace(1, 0, k)
    i0 = int(round(t * SR))
    if i0 < 0: a, ramp, i0 = a[-i0:], ramp[-i0:], 0
    n = min(len(a), len(mix) - i0)
    if n > 0: mix[i0:i0 + n] += a[:n] * ramp[:n, None] * gain
def db(x): return 10 ** (x / 20)
def gap(t0, t1): mix[int(t0 * SR):int(t1 * SR)] *= 0

wind = load(L + '22331__sleepcircle__wind.ogg')
braam = load(L + '722633__chakong__cinematic-braaam.wav')
riser = load(L + '822420__audiopapkin__riser-hit-sfx-120.wav')
woosh = load(L + '649445__audiopapkin__cinematic-woosh-sfx-015.wav')
implo = load(L + '814047__qubodup__fantasy-implosion.wav')
plasma = load(L + '850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav')
susp = load(L + '869757__mikiko850__dark-suspense-accent.wav')
subby = load(L + '238375__stewdio2003__cp_subby_whoosh.aiff')
boom = load(L + '814046__qubodup__explosion-from-another-dimension.wav')
warp = load(L + '735062__gammagool__fast-warp-in.wav')
sparks = load(L + '849772__mikiko850__electric-sparks.wav')
bees = load('sfx/bees.mp3'); gasp = load('sfx/gasp.mp3')

# HOOK: dead silence, then the yellow line ignites on a hit (loop seam is silence -> silence)
put(braam, .30, db(-4), .55, None, fi=.003, fo=1.6)                  # peak lands at ~.78 s after cut-in, onset hits at .3
put(sparks, .45, db(-30), 1., 3.4, fi=.3, fo=.6)
# LOCK-IN a: rooftop; bees then stop dead at totality, then the gasp
put(wind, 2.5, db(-30), 3., 4., fi=.05, fo=.02)
put(bees, 2.5, db(-16), .3, 1.3, fi=.05, fo=.015)
gap(3.42, 3.5)
put(gasp, 3.5, db(-14), 0., 1.5, fo=.4)
# LOCK-IN b: three hydrogen lines, soft crackles
for t0, r in ((4.62, .8), (5.05, 1.0), (5.48, 1.25)):
    put(sparks, t0, db(-12), .2, .34, fi=.004, fo=.06, rate=r)
# BODY 1: zoom whoosh onto the sodium ruler, yellow line pop, then the hit on "NOT SODIUM"
put(woosh, 8.6 - 1.75, db(-8), .8, 2.9, fi=.1, fo=.3)
put(warp, 6.62 - .33, db(-9), .12, None, fo=.3)
put(braam, 9.0 - .48, db(-8), .55, 3.2, fi=.003, fo=.9)
gap(9.95, 10.05)
# REHOOK 1: riser to the arrival at Paris, a hair of silence, one hit
put(riser, 11.12 - 1.9, db(-6), 4.2, 6.1, fi=.1, fo=.015)
gap(11.12, 11.19)
put(boom, 11.2 - .27, db(-5), 0., 3., fo=.8)
# BODY 2: the diamond ring, then a low unease under totality, a small hit on HELIUM
put(implo, 11.52 - .54, db(-4), 0., 4., fo=.8)
put(susp, 12.0, db(-14), 1.5, 4.5, fi=.5, fo=1., rate=.8)
put(boom, 13.2 - .27, db(-12), 0., 2., fo=.5)
# REHOOK 2: hard cut to a quiet lab
gap(14.95, 15.05)
put(wind, 15.05, db(-34), 10., 12.4, fi=.3, fo=.3)
# CLOSE: the tube lights, then the balloon and the biggest hit
put(plasma, 17.32 - .23, db(-10), 1.45, 4.5, fi=.01, fo=1.2)
put(sparks, 17.3, db(-18), 1.2, 2.4, fi=.05, fo=.3)
put(subby, 18.3 - .44, db(-14), .44, 2.8, fi=.01, fo=.4)
put(braam, 18.75 - .48, db(0), .55, None, fi=.003, fo=1.6)
put(boom, 18.75 - .27, db(-8), 0., 2.5, fo=.8)
put(wind, 20.0, db(-30), 16., 17., fi=.3, fo=.6)
mix[-int(.15 * SR):] *= np.linspace(1, 0, int(.15 * SR))[:, None]

pk = np.abs(mix).max(); mix = mix / pk * .84; mix = np.tanh(mix * 1.15) / np.tanh(1.15)   # near-linear: keep the contrast
out = sys.argv[1]; raw = out + '.raw.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', raw], input=mix.astype(np.float32).tobytes(), check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-ar', str(SR), out], check=True)
