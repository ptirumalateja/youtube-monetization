"""Sound for What Are You Carrying (Slow Light Dark). ElevenLabs sound effects (sfx/gen.sh) over the series bed.

  python3 mix.py META.json OUT.wav

- The climb: strained breathing and grunts, slow heavy footsteps on gravel; the slip all the way back down (long scrape).
- He kneels: the sack drops with a deep thud and the rocks clunk inside.
- Each stone: a rummage in the sack, a throw whoosh, then the stone tumbling far down the hill, panned left as it rolls
  away into the dark. The strain fades as the sack empties.
- LET IT GO: one long relieved breath. Then light, quick footsteps up the slope, a warm swell as he steps into the lamp,
  and a radiant shimmer for the enlightenment (with the flag flapping softly beside him).
- The question: one deep boom under WHAT ARE YOU STILL CARRYING?
CC0 wind room tone from ../sfxlib (sleepCircle 22331); everything else is ElevenLabs.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_sound as K
from sld_sound import SR, lp, place, curve, write_wav, new_buses, bed, finish

meta = json.load(open(sys.argv[1])); E = meta['events']
DUR = E['duration']; N = int(DUR * SR)
THROWS = E['throws']; CARD = E['card']


def sfx(name):
    x = K.load(os.path.join(HERE, 'sfx', name + '.mp3')); return x / (np.abs(x).max() + 1e-9)


def fade(x, a=0.01, b=0.05):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nb: x[-nb:] *= np.linspace(1, 0, nb)
    return x


def cut(x, dur, rel=0.08):
    n = min(len(x), int(dur * SR)); y = x[:n].copy(); r = min(n, int(rel * SR)); y[n - r:] *= np.linspace(1, 0, r); return y


bus = new_buses(N)
room = curve(N, [(0, 0.5), (DUR, 0.5)])
drone = curve(N, [(0, 0.5), (E['kneel0'], 0.8), (THROWS[-1], 0.35), (E['arrive'], 0.2), (CARD, 0.6), (CARD + 1.0, 1.2), (DUR, 1.0)])
duck = np.ones(N)
bed(bus, room, drone, duck)

# ---- the climb (frame 0 is already mid-step), the slip, the sack drop
place(bus['fol'], fade(sfx('strain'), 0.02, 0.4), 0.0, 0.85, 0.0)
place(bus['fol'], fade(cut(sfx('strain'), 2.6, 0.6), 0.2, 0.6), 3.4, 0.6, 0.0)
place(bus['fol'], fade(cut(sfx('steps_heavy'), E['slip0'] + 0.1, 0.2)), 0.0, 0.6, 0.0)
place(bus['fol'], fade(sfx('slide_long'), 0.01, 0.2), E['slip0'] - 0.02, 0.9, -0.2)
place(bus['hit'], fade(sfx('sack_drop'), 0.003, 0.2), E['sackDrop'] + 0.15, 0.85, 0.1)

# ---- the stones
for i, T in enumerate(THROWS):
    place(bus['fol'], fade(sfx('rummage')), T - 0.65, 0.55, 0.15)
    place(bus['fol'], fade(sfx('throw')), T - 0.06, 0.7, -0.1)
    r = fade(sfx('roll'), 0.005, 0.8); pan = np.linspace(-0.2, -0.85, len(r))
    seg = np.zeros((2, len(r))); seg[0] = r * np.cos((pan + 1) * np.pi / 4) * 1.414; seg[1] = r * np.sin((pan + 1) * np.pi / 4) * 1.414
    i0 = int((T + 0.3) * SR); n = min(len(r), N - i0)
    bus['hit'][:, i0:i0 + n] += seg[:, :n] * (0.7 - 0.05 * i)

# ---- letting go, walking up light, arriving in the light
place(bus['fol'], fade(sfx('exhale')), E['stand0'] - 0.1, 0.8, 0.0)
place(bus['fol'], fade(cut(sfx('steps_light'), E['arrive'] - E['walk0'] + 0.1, 0.15)), E['walk0'], 0.65, 0.1)
place(bus['air'], fade(sfx('arrive'), 0.3, 0.8), E['bloom0'] - 0.2, 0.8, 0.0)
place(bus['air'], fade(sfx('shimmer'), 0.4, 1.0), E['glow0'] - 0.1, 0.75, 0.0)
place(bus['fol'], fade(sfx('flag'), 0.6, 0.8), E['glow0'] - 0.6, 0.3, 0.3)

# ---- the question
place(bus['hit'], fade(sfx('boom'), 0.003, 0.3), CARD + 0.15, 0.9, 0.0)

mix = finish(bus, duck)
write_wav(mix, sys.argv[2])
