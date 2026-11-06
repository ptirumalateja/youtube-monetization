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
BU, START, FAST, WH = TL['buildFrac'], TL['start'], TL['fastStep'], TL['hitW']
T0, RR = TL['T0'], TL['r']
Tk = lambda k: T0 * RR ** k
tk = lambda k: START + T0 * (1 - RR ** k) / (1 - RR)
NB = TL['rungsTotal'] - TL['rungsStart']; BEND = tk(NB)
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


def hit(bus, name, t, gain, pan, tail=0.2):
    """First transient of a sample lined up on t (onset = first 25% of peak), cut to `tail` s with a fade."""
    s, _ = samp(name); on = int(np.argmax(np.abs(s) > 0.25)); a = max(0, on - int(0.004 * SR)); c = s[a:a + int(tail * SR)].copy()
    f = int(min(len(c), 0.05 * SR)); c[-f:] *= np.linspace(1, 0, f); place(bus, c, t - 0.004, gain, pan)


bus = K.new_buses(N)
room_g = curve(N, [(0, 0.22), (DUR, 0.22)])
drone_g = curve(N, [(0, 0.15), (BEND, 0.9), (TL['flareT'], 1.0), (TL['flareT'] + 1.0, 0.3), (DUR, 0.2)])
duck = curve(N, [(0, 1), (P - 0.45, 1), (P - 0.4, 0.06), (P - 0.01, 0.06), (P, 1), (DUR, 1)])
K.bed(bus, room_g, drone_g, duck)
PA, PP = 0.35, -0.45
rng = np.random.default_rng(3)
# camera leaves the ground: ground sounds get quieter as the frame rises; climber sounds stay present
gnd = lambda t: float(np.interp(t, [0, 3, 5, 6.5, 8.5, 9.0], [1.0, 0.8, 0.3, 0.0, 0.0, 1.0]))

def pitched(name, rate, tail):
    s, _ = samp(name); on = int(np.argmax(np.abs(s) > 0.25)); c = s[max(0, on - int(0.004 * SR)):][:int(tail * rate * SR)]
    c = np.interp(np.arange(0, len(c) - 1, rate), np.arange(len(c)), c); f = int(min(len(c), 0.04 * SR)); c = c.copy(); c[-f:] *= np.linspace(1, 0, f); return c


def swish(dur, f, g):
    n = int(dur * SR); x = K.bp(K.noise(n), f, 0.9); return x * np.sin(np.pi * np.arange(n) / n) ** 2 * g


for k in range(NB):
    t0 = tk(k); T = Tk(k); prog = k / (NB - 1)
    at_start(bus['fol'], 'plank_grab', t0 + BU * T * 0.12, 0.22, PA, off=0.0, dur=min(0.4, T * 0.5))
    for i, wh in enumerate(WH):
        th = t0 + BU * T * wh
        rate = 1.0 + 0.55 * prog + (0.06 if i else 0)            # the blows climb in pitch and bite as he speeds up
        c = pitched(f'hammer{(2 * k + i) % 4 + 1}', rate, 0.2)
        place(bus['hit'], c, th - 0.004, (0.85 + 0.25 * prog) * (0.9 + 0.2 * rng.random()), PA)
        place(bus['hit'], K.thud(40 + 2 * k + i, f=95 + 70 * prog, dec=0.05, gain=0.55 + 0.3 * prog), th, 1.0, PA)   # the weight behind each blow
        place(bus['air'], swish(0.07, 1800 + 1500 * prog, 0.16), th - 0.075, 1.0, PA)                               # the arm coming down
# tension: a filtered-noise riser under the whole build, and the drone climbs with him
nn = int((BEND + 0.3) * SR); rs = K.bp(K.noise(nn), 900, 0.6) + 0.5 * K.bp(K.noise(nn), 2600, 0.8)
rs *= np.linspace(0, 1, nn) ** 3 * 0.05; place(bus['air'], rs, 0.0, 1.0, 0.0)
for j in range(4):
    for q, nm in ((0.42, 'step1'), (0.88, 'step2')):
        ts = BEND + j * FAST + FAST * q
        if ts < TL['flareT'] + 0.1: at_peak(bus['fol'], nm, ts, 0.18, PA, trim=0.3)
# perfectionist: tape and sanding
ins = TL['inspect']
for a, b in ins:
    at_start(bus['fol'], 'tape_out', max(0.0, a - 0.15) if a < 1 else a + 0.05, 1.0 * gnd(a), PP, dur=1.3, off=0.0 if a >= 1 else 0.1)
    at_start(bus['fol'], 'tape_back', b - 0.75, 0.75 * gnd(b), PP, dur=1.0)
gaps = [(0.0, 0.2)] + [(ins[i][1], ins[i + 1][0]) for i in range(len(ins) - 1)] + [(ins[-1][1], TL['pStand'] - 0.4)]
for a, b in gaps:
    t = a
    while t < b - 0.15:
        d = min(3.8, b - t); at_start(bus['fol'], 'sand', t, 0.5 * gnd(t), PP, off=rng.random() * 0.2, dur=d); t += d - 0.12
# frame-0 hook: an arm swish and a thump so the reel starts loud
place(bus['air'], swish(0.3, 1500, 0.35), 0.0, 1.0, PA)
place(bus['hit'], K.thud(77, f=90, dec=0.08, gain=0.6), 0.0, 1.0, PA)
# the light
at_peak(bus['air'], 'light', TL['flareT'] + 0.35, 1.3, 0.0)
rh = K.load('822420__audiopapkin__riser-hit-sfx-120.wav'); rh /= np.abs(rh).max()
e = np.convolve(rh ** 2, np.ones(2400) / 2400, 'same'); pk = int(np.argmax(e))
place(bus['hit'], rh, TL['flareT'] + 0.1 - pk / SR, 0.55, 0.2)
# end: his one rung
at_start(bus['fol'], 'step1', TL['pStand'] + 0.25, 0.3, PP, dur=0.35)
at_peak(bus['hit'], 'click', P + 0.02, 1.8, PP, trim=0.7)
at_peak(bus['fol'], 'thud', TL['pSit'] + 0.8, 1.4, PP, trim=0.8)
mix = K.finish(bus, duck)
xf = int(TL['loopXfade'] * SR); mix[:, -xf:] *= np.linspace(1, 0, xf) ** 1.5
write_wav(mix, sys.argv[1])
def db(a, b):
    s = mix[:, int(a * SR):int(b * SR)]; return 20 * np.log10(np.sqrt((s ** 2).mean()) + 1e-12)
print(f'rms 0-0.5 {db(0, 0.5):.1f} | build 3-10 {db(3, 10):.1f} | flare {db(TL["flareT"], TL["flareT"] + 0.8):.1f} | held breath {db(P - 0.38, P - 0.02):.1f} | click {db(P, P + 0.3):.1f} dB')
