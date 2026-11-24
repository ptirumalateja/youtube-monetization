"""Sound for Born Rich (Slow Light Dark). ElevenLabs sound effects (sfx/gen.sh) over the series bed.

  python3 mix.py META.json OUT.wav

- Frame 0: the lamp clunks on (series hum under everything); the start: shoes scuff off the line.
- The race: an all-out sprint (Motivation) that dies at the burnout, two runners sprinting (Discipline and Ego), Ego's surge
  whoosh as Motivation fades, Motivation's panting,
  Ego's short whoop when he starts celebrating. A low drone creeps up.
- The car: engine roar rising from the dark (sound first, picture second), a nitro pop, the pass aligned to the line,
  the tape snapping, a tyre skid, then a low idle.
- The freeze: everything else stops dead; only the idle and the room are left (held breath).
- The question: one deep boom under WAS IT EVER A FAIR RACE?, drone swell, room tone to the end.
CC0 wind room tone from ../sfxlib (sleepCircle 22331); everything else is ElevenLabs.
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_sound as K
from sld_sound import SR, lp, hp, place, curve, write_wav, new_buses, bed, finish

meta = json.load(open(sys.argv[1])); E = meta['events']
DUR = E['duration']; N = int(DUR * SR); t = np.arange(N) / SR
TF, TC, CARD = E['freeze'], E['carCross'], E['card']


def sfx(name):
    x = K.load(os.path.join(HERE, 'sfx', name + '.mp3')); return x / (np.abs(x).max() + 1e-9)


def peak_at(x, win=0.05):
    """Time (s) of the loudest moment of x (envelope over win seconds)."""
    e = np.convolve(np.abs(x), np.ones(int(win * SR)) / int(win * SR), 'same'); return np.argmax(e) / SR


def fade(x, a=0.01, b=0.05):
    x = x.copy(); na, nb = int(a * SR), int(b * SR)
    if na: x[:na] *= np.linspace(0, 1, na)
    if nb: x[-nb:] *= np.linspace(1, 0, nb)
    return x


def cut(x, dur, rel=0.06):
    n = min(len(x), int(dur * SR)); y = x[:n].copy(); r = min(n, int(rel * SR)); y[n - r:] *= np.linspace(1, 0, r); return y


bus = new_buses(N)
# ---- bed: room (wind, CC0) + lamp hum + a drone that creeps up across the race and swells under the question
room = curve(N, [(0, 0.55), (TF, 0.55), (TF + 0.05, 0.35), (DUR, 0.45)])
drone = curve(N, [(0, 0.1), (5.0, 0.35), (TC, 0.9), (TF, 0.25), (CARD, 0.4), (CARD + 1.0, 1.4), (DUR, 1.1)])
duck = curve(N, [(0, 1), (TF - 0.02, 1), (TF + 0.04, 0.35), (CARD - 0.05, 0.35), (CARD + 0.1, 1), (DUR, 1)])
bed(bus, room, drone, duck)

# ---- frame 0 and the start
place(bus['hit'], sfx('lamp_on'), 0.0, 0.55, 0.0)
place(bus['fol'], sfx('start'), E['go'] - 0.04, 0.9, 0.0)

# ---- the race (cut dead at the freeze)
sp = sfx('sprint'); sp = cut(sp, E['burnout1'] - E['go'] - 0.2) * np.linspace(1, 0.15, int(min(len(sp), (E['burnout1'] - E['go'] - 0.2) * SR)))
place(bus['fol'], fade(sp), E['go'] + 0.15, 0.75, -0.45)
jog = sfx('pack'); jg = np.tile(jog, 2)[:int((TF - E['go'] - 0.3) * SR)]
place(bus['fol'], fade(jg, 0.2, 0.03), E['go'] + 0.3, 0.55, 0.15)
place(bus['fol'], fade(sfx('pant')), E['burnout1'] - 0.1, 0.65, -0.5)
place(bus['fol'], fade(sfx('pant')[: int(1.4 * SR)], 0.05, 0.4), E['burnout1'] + 2.4, 0.4, -0.5)
place(bus['fol'], fade(sfx('cheer')), E['celebrate'] + 0.15, 0.32, 0.35)
place(bus['fol'], fade(sfx('surge')), E['egoBoost'] - 0.1, 0.8, 0.3)

# ---- the car: roar first (from the dark), the pass on the line, nitro, tape, skid, idle
eng = sfx('engine'); pk = peak_at(eng)
place(bus['hit'], fade(cut(eng, pk + 0.55, 0.25), 0.4, 0.25), TC - pk, 0.95, 0.4)
place(bus['hit'], fade(sfx('nitro')), TC - 0.45, 0.6, 0.35)
place(bus['fol'], fade(sfx('tape')), TC - 0.02, 0.8, 0.3)
sk = sfx('skid'); place(bus['hit'], fade(cut(sk, TF - TC + 0.1, 0.2), 0.005, 0.2), TC + 0.04, 0.75, 0.2)
idle = sfx('idle'); idl = np.tile(idle, 3)[:int((DUR - TC - 0.4) * SR)]
place(bus['hit'], fade(lp(idl, 900), 0.5, 0.6) * curve(len(idl), [(0, 0.35), (TF - TC - 0.4, 0.2), (CARD - TC - 0.4, 0.16), (DUR - TC - 0.4, 0.1)]), TC + 0.4, 0.5, 0.2)

# ---- the question
boom = sfx('boom'); place(bus['hit'], fade(boom, 0.003, 0.3), CARD + 0.12, 1.0, 0.0)

mix = finish(bus, duck)
write_wav(mix, sys.argv[2])


def db(a, b):
    s = mix[:, int(a * SR):int(b * SR)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12)
print(f'rms race 2-6 s {db(2, 6):.1f} dB | car pass {db(TC - 0.3, TC + 0.3):.1f} dB | freeze {db(TF + 0.2, CARD - 0.1):.1f} dB | boom {db(CARD + 0.1, CARD + 1.2):.1f} dB')
