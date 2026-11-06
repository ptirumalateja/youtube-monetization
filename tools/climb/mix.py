"""Sound for Build It As You Climb (Slow Light Dark), v2. No music, no voice; every sound has a visible cause.

  python3 mix.py OUT.wav

All foley is generated with the ElevenLabs sound-effects API (`sfx/*.mp3`, made by sfx/gen.sh) and cut to the
picture: the peak of each sample is lined up with the frame of the visible event (hammer blow, tape lock, step...).
- Action taker: plank pulled off the bundle, two hammer blows per plank (right nail, left nail), a footstep per step.
- Perfectionist: sandpaper while he sands, tape pulled out and locked / snapped back on every measurement, the click
  of his one perfect rung, the sit-down thud.
- The light: ElevenLabs swell + the CC0 riser-hit (audiopapkin 822420) through the hatch. Bed: room tone, lamp hum, drone.
"""
import json, os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
import sld_sound as K
from sld_sound import SR, lp, hp, curve, place, write_wav

TL = json.load(open(os.path.join(HERE, 'timeline.json')))
DUR = TL['duration']; N = int(DUR * SR)
T, BU, START, FAST, WH = TL['cycle'], TL['buildFrac'], TL['start'], TL['fastStep'], TL['hitW']
NB = TL['rungsTotal'] - TL['rungsStart']; BEND = START + NB * T
P = TL['pPlace']


def samp(name, hpf=60):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'sfx', name + '.mp3'), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    s = np.frombuffer(raw, np.float32).astype(np.float64); s = hp(s, hpf); s /= np.abs(s).max() + 1e-9
    e = np.convolve(s ** 2, np.ones(int(0.004 * SR)) / int(0.004 * SR), 'same'); return s, int(np.argmax(e))


def at_peak(bus, name, t_peak, gain, pan, trim=None):
    s, pk = samp(name)
    if trim: s = s[:int(trim * SR)] * np.linspace(1, 0, min(len(s), int(trim * SR)))[:len(s[:int(trim * SR)])] ** 0.5
    place(bus, s, t_peak - pk / SR, gain, pan)


def at_start(bus, name, t0, gain, pan, off=0.0, dur=None):
    s, _ = samp(name); s = s[int(off * SR):]
    if dur: s = s[:int(dur * SR)]; f = int(0.03 * SR); s[:f] *= np.linspace(0, 1, f); s[-f:] *= np.linspace(1, 0, f)
    place(bus, s, t0, gain, pan)


bus = K.new_buses(N)
room_g = curve(N, [(0, 0.4), (DUR, 0.4)])
drone_g = curve(N, [(0, 0.12), (BEND, 0.6), (TL['flareT'], 0.9), (TL['flareT'] + 1.0, 0.3), (DUR, 0.2)])
duck = curve(N, [(0, 1), (P - 0.45, 1), (P - 0.4, 0.06), (P - 0.01, 0.06), (P, 1), (DUR, 1)])
K.bed(bus, room_g, drone_g, duck)
PA, PP = 0.35, -0.45
rng = np.random.default_rng(3)
# camera leaves the ground: ground sounds get quieter as the frame rises; climber sounds stay present
gnd = lambda t: float(np.interp(t, [0, 6, 10, 12, 16, 17], [1.0, 0.8, 0.35, 0.0, 0.0, 1.0]))

for k in range(NB):
    t0 = START + k * T
    at_start(bus['fol'], 'plank_grab', t0 + BU * T * 0.12, 0.35, PA, off=0.0, dur=0.45)
    for i, wh in enumerate(WH):
        th = t0 + BU * T * wh
        at_peak(bus['hit'], f'hammer{(2 * k + i) % 4 + 1}', th, 0.8 + 0.12 * rng.random(), PA, trim=0.5)
    v0 = t0 + BU * T
    if k >= 3:
        for q in (0.42, 0.88):
            at_peak(bus['fol'], 'step1' if q < 0.5 else 'step2', v0 + (1 - BU) * T * q, 0.35, PA, trim=0.35)
for j in range(4):
    for q, nm in ((0.42, 'step1'), (0.88, 'step2')):
        ts = BEND + j * FAST + FAST * q
        if ts < TL['flareT'] + 0.1: at_peak(bus['fol'], nm, ts, 0.3, PA, trim=0.35)
# perfectionist: tape and sanding
ins = TL['inspect']
for a, b in ins:
    at_start(bus['fol'], 'tape_out', max(0.0, a - 0.15) if a < 1 else a + 0.05, 1.0 * gnd(a), PP, dur=1.3, off=0.0 if a >= 1 else 0.1)
    at_start(bus['fol'], 'tape_back', b - 0.75, 0.75 * gnd(b), PP, dur=1.0)
gaps = [(0.0, 0.2)] + [(ins[i][1], ins[i + 1][0]) for i in range(len(ins) - 1)] + [(ins[-1][1], TL['pStand'] - 0.4)]
for a, b in gaps:
    t = a
    while t < b - 0.15:
        d = min(3.8, b - t); at_start(bus['fol'], 'sand', t, 0.5 * gnd(t) + 0.05 * (t > 9), PP, off=rng.random() * 0.2, dur=d); t += d - 0.12
# the light
at_peak(bus['air'], 'light', TL['flareT'] + 0.35, 0.8, 0.0)
rh = K.load('822420__audiopapkin__riser-hit-sfx-120.wav'); rh /= np.abs(rh).max()
e = np.convolve(rh ** 2, np.ones(2400) / 2400, 'same'); pk = int(np.argmax(e))
place(bus['hit'], rh, TL['flareT'] + 0.1 - pk / SR, 0.55, 0.2)
# end: his one rung
at_start(bus['fol'], 'step1', TL['pStand'] + 0.25, 0.3, PP, dur=0.35)
at_peak(bus['hit'], 'click', P + 0.02, 0.9, PP, trim=0.7)
at_peak(bus['fol'], 'thud', TL['pSit'] + 0.8, 0.8, PP, trim=0.8)
mix = K.finish(bus, duck)
xf = int(TL['loopXfade'] * SR); mix[:, -xf:] *= np.linspace(1, 0, xf) ** 1.5
write_wav(mix, sys.argv[1])
def db(a, b):
    s = mix[:, int(a * SR):int(b * SR)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12)
print(f'rms 0-0.5 {db(0, 0.5):.1f} | build 3-10 {db(3, 10):.1f} | flare {db(TL["flareT"], TL["flareT"] + 0.8):.1f} | held breath {db(P - 0.38, P - 0.02):.1f} | click {db(P, P + 0.3):.1f} dB')
