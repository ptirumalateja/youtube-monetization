"""Sound for I'm Fine: minimal but heavy (Slow Light Dark series; helpers and bus layout copied from the pilot,
tools/chain-never-locked/mix.py).

Everything is synthesised here in numpy (office murmur, distant laughter, the phone buzz and the tinny voice on the call,
breath, footsteps, the ceramic creaks and the hairline crack, the porcelain clink, the lamp flicker, the drone and the
final warm low tone), plus one CC0 Freesound file from ../sfxlib/ (sleepCircle "wind.ogg", low-passed as room tone).
No credit is required.

Sync comes from the scene: output/meta.json (render.cjs meta) holds the timeline.

  python3 mix.py META.json OUT.wav
"""
import json, os, subprocess, sys
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'sfxlib')
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- helpers
def load(name, sr=SR):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(LIB, name), '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def spec_filter(x, f):
    """Zero-phase filter: multiply the spectrum by gain(f) where f is an array of bin frequencies."""
    n = len(x); N = 1 << int(np.ceil(np.log2(n + 1)))
    X = np.fft.rfft(x, N); fr = np.fft.rfftfreq(N, 1 / SR)
    return np.fft.irfft(X * f(fr), N)[:n]


def lp(x, fc, order=2): return spec_filter(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))
def hp(x, fc, order=2): return spec_filter(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))
def bp(x, fc, q): return spec_filter(x, lambda f: np.exp(-0.5 * (np.log(np.maximum(f, 1) / fc) * q) ** 2))


def env(n, a, d, sus=0.0):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * (sus + (1 - sus) * np.exp(-t / d))


def noise(n): return rng.standard_normal(n)


def place(bus, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= bus.shape[1]: return
    if i < 0: sig = sig[-i:]; i = 0
    n = min(len(sig), bus.shape[1] - i)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[0, i:i + n] += sig[:n] * gain * l * 1.414
    bus[1, i:i + n] += sig[:n] * gain * r * 1.414


def reverb_ir(sec, damp, seed):
    r = np.random.default_rng(seed); n = int(sec * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * 6.9 / sec)
    ir = lp(ir, damp); ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.sqrt(np.sum(ir ** 2))


def convolve(x, ir):
    n = len(x) + len(ir); N = 1 << int(np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]


# ---------------------------------------------------------------- sources
def breath(dur, kind, seed, gain=1.0):
    """Unvoiced breath. kind 'in' (sharp, higher) or 'out' (heavy, lower, chesty)."""
    n = int(dur * SR); x = np.random.default_rng(seed).standard_normal(n); t = np.arange(n) / dur / SR
    if kind == 'in':
        y = bp(x, 1500, 1.4) * 0.7 + bp(x, 2900, 2.2) * 0.35; e = np.sin(np.pi * np.minimum(1, t)) ** 0.8 * (0.4 + 0.6 * t)
    else:
        y = bp(x, 520, 1.3) * 1.0 + bp(x, 1150, 1.8) * 0.5 + lp(x, 260) * 0.35; e = (1 - np.exp(-t * 18)) * np.exp(-t * 2.4)
    return y * e * gain


def thud(seed, f=70, dec=0.16, gain=1.0):
    """Body / footstep weight: low sine drop + a soft noise slap."""
    n = int(0.8 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f + 60 * np.exp(-t / 0.02)) * t) * env(n, 0.002, dec)
    return (s + lp(noise(n), 900) * env(n, 0.001, 0.025) * 0.6) * gain




def voiced(dur, f0, seed, jitter=0.03):
    """A glottal pulse train with drifting pitch (the raw material for voices)."""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    drift = np.cumsum(r.standard_normal(n)) / np.sqrt(SR) * 0.8
    f = f0 * (1 + jitter * np.sin(2 * np.pi * 0.7 * t + r.random() * 6) + 0.05 * drift)
    ph = np.cumsum(f) / SR
    return (np.sin(2 * np.pi * ph) ** 9) * 2 + 0.15 * r.standard_normal(n)


def formant(x, f1, f2, f3=2600):
    return bp(x, f1, 2.2) * 1.0 + bp(x, f2, 2.6) * 0.6 + bp(x, f3, 3.0) * 0.25


def laughter(dur, seed, f0=210, rate=4.6):
    """One person laughing: 'ha' bursts at about 4-5 per second, falling in pitch, muffled."""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    v = formant(voiced(dur, f0, seed, 0.06), 750, 1250)
    ph = (t * rate + r.random()) % 1
    syl = np.exp(-((ph - 0.3) / 0.13) ** 2) * (0.7 + 0.3 * np.sin(2 * np.pi * 0.9 * t + r.random() * 6))
    asp = bp(noise(n), 1500, 1.2) * syl * 0.25          # the breathy 'h'
    shape = np.minimum(1, t / 0.12) * np.exp(-t / (dur * 0.7))
    return lp((v * syl + asp) * shape, 1600)


def murmur(dur, seed, voices=5):
    """Office murmur: several voices talking low, no words, far off."""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for k in range(voices):
        v = voiced(dur, 95 + 80 * r.random(), seed * 10 + k, 0.12)
        f1 = 500 + 250 * np.sin(2 * np.pi * (2.0 + r.random()) * t)            # vowels moving
        x = bp(v, 600 + 200 * r.random(), 1.8) + bp(v, 1300 + 400 * r.random(), 2.4) * 0.5
        syl = np.clip(np.sin(2 * np.pi * (3.2 + 1.5 * r.random()) * t + r.random() * 6), 0, 1) ** 0.7
        phrase = np.clip(np.sin(2 * np.pi * (0.35 + 0.3 * r.random()) * t + r.random() * 6) + 0.3, 0, 1)
        y += x * syl * phrase * (0.6 + 0.4 * r.random())
    return lp(y, 900)


def tinny_voice(dur, seed):
    """Mum on the phone: one voice through a small speaker, band-limited, quiet."""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    v = voiced(dur, 230, seed, 0.15)
    x = bp(v, 900, 1.6) + bp(v, 2100, 2.0) * 0.7
    syl = np.clip(np.sin(2 * np.pi * 4.1 * t + 1.0), 0, 1) ** 0.6 * np.clip(np.sin(2 * np.pi * 0.6 * t) + 0.5, 0, 1)
    return hp(lp(x * syl, 3200), 450)


def buzz(dur):
    """Phone vibrating on a palm: a 160 Hz rattle in two pulses."""
    n = int(dur * SR); t = np.arange(n) / SR
    g = ((t % 0.5) < 0.32).astype(float); g = lp(g, 40)
    x = np.tanh(3 * np.sin(2 * np.pi * 160 * t)) + 0.4 * bp(noise(n), 2400, 2)
    return lp(x, 2500) * g


def ceramic_creak(dur, seed, strength=1.0):
    """Porcelain under strain against the face: stick-slip ticks through stiff ceramic modes, plus a low groan."""
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    rate = 25 + 140 * strength * np.sin(np.pi * t / dur) ** 2                  # ticks speed up with the force
    ph = np.cumsum(rate) / SR; ticks = np.diff(np.floor(ph), prepend=0) > 0
    pulses = ticks * (0.5 + 0.5 * r.random(n))
    modes = np.zeros(int(0.06 * SR)); tm = np.arange(len(modes)) / SR
    for f, d, a in [(1180, 0.02, 1.0), (2730, 0.012, 0.7), (4630, 0.008, 0.45), (7100, 0.005, 0.25)]:
        modes += np.sin(2 * np.pi * f * tm) * np.exp(-tm / d) * a
    y = convolve(pulses, modes)
    groan = bp(noise(n), 260, 1.6) * np.sin(np.pi * t / dur) ** 2 * 1.5 + np.sin(2 * np.pi * (70 + 20 * t / dur) * t) * np.sin(np.pi * t / dur) ** 3 * 0.6
    return (y * 0.6 + groan * 0.35) * strength


def crack_tick(seed):
    """The hairline crack: one dry, sharp tick and a short glassy ring."""
    n = int(0.6 * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    y = hp(noise(n), 2500) * env(n, 0.0002, 0.003) * 2.0
    for f, d in [(3120, 0.05), (5340, 0.03), (8020, 0.02)]:
        y += np.sin(2 * np.pi * f * (1 + 0.01 * r.random()) * t) * np.exp(-t / d) * 0.25
    return y + bp(noise(n), 700, 1.5) * env(n, 0.001, 0.02) * 0.6


def clink(seed):
    """Porcelain set down on a wooden table: bright ceramic modes over a soft wood knock."""
    n = int(1.5 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for f, d, a in [(1870, 0.35, 1.0), (3290, 0.22, 0.6), (5110, 0.12, 0.4), (7330, 0.07, 0.25)]:
        y += np.sin(2 * np.pi * f * t) * np.exp(-t / d) * a
    y = y * 0.35 + hp(noise(n), 3000) * env(n, 0.0002, 0.004) * 0.8
    knock = np.sin(2 * np.pi * (180 + 80 * np.exp(-t / 0.01)) * t) * env(n, 0.001, 0.05) * 0.6
    return y + knock + clink_second(n, t)


def clink_second(n, t):   # the rim settles a beat later, quieter
    y = np.zeros(n); i = int(0.11 * SR); tt = t[:n - i]
    for f, d, a in [(1890, 0.2, 0.4), (3330, 0.12, 0.25)]:
        y[i:] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / d) * a * 0.35
    return y


def cloth_pat(seed):
    """A hand patting a shoulder: two soft muffled slaps."""
    n = int(0.5 * SR); y = np.zeros(n)
    for k, dt in enumerate([0.0, 0.22]):
        i = int(dt * SR); m = int(0.12 * SR)
        y[i:i + m] += lp(noise(m), 1300) * env(m, 0.001, 0.03) * (1 - 0.3 * k) + thud(seed + k, 120, 0.04, 0.4)[:m]
    return y


def whoosh(dur, seed):
    """The camera trucking through the dark: a soft air swell."""
    n = int(dur * SR); t = np.arange(n) / SR
    x = noise(n); sw = np.sin(np.pi * t / dur) ** 2
    return (bp(x, 500, 1.0) * 0.6 + lp(x, 1200) * 0.3) * sw * 0.5


def flicker_pop(seed):
    """A filament catching: a small electric tick with a burr."""
    n = int(0.12 * SR); t = np.arange(n) / SR
    return hp(noise(n), 1800) * env(n, 0.0005, 0.01) * 0.8 + np.tanh(4 * np.sin(2 * np.pi * 120 * t)) * env(n, 0.002, 0.03) * 0.25


def warm_tone(dur):
    """The end: the sub-boom softened into a warm low chord (A, E, A, C#), slow attack, long tail."""
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a in [(55, 0.45), (110, 0.7), (164.8, 0.4), (220, 0.25), (277.2, 0.14)]:
        y += np.sin(2 * np.pi * f * t + a) * a * (1 + 0.05 * np.sin(2 * np.pi * 0.2 * t + f))
    e = np.minimum(1, t / 0.9) ** 2 * np.exp(-np.maximum(0, t - 1.2) / 3.0)
    return np.tanh(1.3 * y) * e


# ---------------------------------------------------------------- mix
def main(meta_path, out_path):
    M = json.load(open(meta_path)); E = M['events']
    D = E['duration']; N = int(D * SR); TR = E['truck']; ARR = E['ARR']; MID = E['MID']
    bus = {k: np.zeros((2, N)) for k in ['bed', 'drone', 'fol', 'amb', 'hit', 'air']}
    t = np.arange(N) / SR

    def curve(K):
        xs, ys = zip(*K); return np.interp(t, xs, ys)

    # room tone (CC0 wind, low-passed into a distant room) and the lamp's mains hum (series signature)
    w = load('22331__sleepcircle__wind.ogg'); w = np.tile(w, int(np.ceil((N + SR) / len(w))))[:N + SR]
    room = lp(hp(w, 60), 520)[:N]; room /= np.abs(room).max()
    room2 = lp(hp(w[SR // 2:SR // 2 + N], 60), 700); room2 /= np.abs(room2).max()
    hum = sum(np.sin(2 * np.pi * h * 60 * t + h) / h ** 1.2 for h in (2, 3, 4, 6)) * (1 + 0.15 * np.sin(2 * np.pi * 0.31 * t))
    hum = lp(hum, 600) * 0.012
    # drone: 55 Hz root and fifth, rising under the struggle
    dr = np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 110.4 * t) + 0.35 * np.sin(2 * np.pi * 82.6 * t) + 0.22 * np.sin(2 * np.pi * 164.7 * t)
    dr = np.tanh(1.4 * dr) * 0.09

    # silence as a beat: the bed drops out between the creaks and after the crack
    p1, p2 = E['pull1'], E['pull2']
    duck = curve([(0, 1), (p1[1], 1), (E['release1'] + 0.05, 0.12), (p2[0] - 0.05, 0.12), (p2[0] + 0.2, 0.7), (E['gasp'] + 0.1, 0.7),
                  (E['gasp'] + 0.45, 0.08), (E['flicker'][0] - 0.05, 0.08), (E['flicker'][1], 0.8), (D, 1)])
    room_g = curve([(0, 0.1), (MID[3], 0.1), (ARR[4], 0.14), (D, 0.13)]) * duck
    drone_g = curve([(0, 0.22), (MID[3], 0.2), (E['grip'], 0.35), (p2[1], 0.9), (E['gasp'] + 0.2, 0.9), (E['gasp'] + 0.5, 0.0),
                     (E['flicker'][1], 0.0), (E['look'][1], 0.25), (E['warm'][0], 0.25), (E['warm'][0] + 1.0, 0.0), (D, 0.0)])
    for c, (a, b) in enumerate([(room, room2), (room2, room)]):
        bus['bed'][c] += a * room_g + hum * duck
        bus['drone'][c] += dr * drone_g * (1 + 0.04 * np.sin(2 * np.pi * (0.13 + 0.02 * c) * t))

    # each vignette's world, heard only while its pool is on screen (cross-faded at the mid-truck switch)
    def seg_gain(k, fade=0.25):
        a = MID[k - 1]; b = MID[k] if k < len(MID) else D
        return curve([(0, 0), (max(0, a - fade), 0), (a + fade, 1), (b - fade, 1), (b + fade, 0), (D, 0)])
    office = murmur(D, 3) * 0.5; keys = np.zeros(N); r = np.random.default_rng(9)
    for k in range(40):   # a keyboard somewhere
        s = 2.0 + r.random() * 2.2; m = int(0.03 * SR); i = int(s * SR); keys[i:i + m] += hp(noise(m), 2500) * env(m, 0.0005, 0.006) * 0.25
    amb = office * seg_gain(1) + keys * seg_gain(1)
    laughs = np.zeros(N)
    for k, (f0, dt, d, g) in enumerate([(220, 0.0, 1.0, 1.0), (180, 0.15, 0.9, 0.8), (260, 0.45, 0.7, 0.6), (200, 0.7, 0.6, 0.5)]):
        place_mono = laughter(d, 40 + k, f0); i = int((E['laugh0'] + dt) * SR); laughs[i:i + len(place_mono)] += place_mono[:N - i] * g
    amb += laughs * 0.35 + murmur(D, 5, 3) * 0.25 * seg_gain(2)
    call = np.zeros(N); v = tinny_voice(E['callEnd'] - E['phone0'], 60); i = int(E['phone0'] * SR); call[i:i + len(v)] += v * 0.35
    amb += call * seg_gain(3)
    for c in range(2): bus['amb'][c] += amb * (1 + 0.1 * (c - 0.5))
    place(bus['fol'], buzz(0.9) * 0.18, E['phone0'] - 0.75, 1.0, 0.1)
    place(bus['fol'], flicker_pop(61) * 0.6, E['callEnd'], 1.0, 0.1)                      # call ends: a soft tap

    # opening: he lifts the mask (a cloth move, then porcelain settles against his face)
    place(bus['hit'], thud(1, 52, 0.3, 0.7), 0.0, 1.0, 0.0)                               # frame 0 has weight
    place(bus['fol'], breath(0.5, 'in', 2, 0.4), E['lift0'] - 0.1, 1.0, 0.0)
    place(bus['fol'], lp(noise(int(0.5 * SR)), 1600) * env(int(0.5 * SR), 0.08, 0.15) * 0.15, E['lift0'], 1.0, 0.0)
    place(bus['fol'], crack_tick(3) * 0.12, E['lift1'] - 0.05, 1.0, 0.0)                  # a light porcelain tap as it seats
    place(bus['hit'], thud(4, 70, 0.18, 0.35), E['lift1'] - 0.05, 1.0, 0.0)
    for k, (a, b) in enumerate(TR):
        place(bus['air'], whoosh(b - a + 0.3, 10 + k), a - 0.1, 0.9 if k < 3 else 0.6, 0.6 if k % 2 else -0.6)
    # pats and footsteps leaving each pool
    place(bus['fol'], cloth_pat(20), E['pat1'] + 0.05, 0.8, 0.15)
    place(bus['fol'], cloth_pat(21), E['pat2'] + 0.07, 0.8, -0.1)
    for k, t0 in enumerate([E['pat1'] + 0.55, E['pat1'] + 0.75, E['pat2'] + 0.5]):
        for j in range(4):
            place(bus['fol'], lp(thud(300 + 10 * k + j, 95, 0.06, 1.0), 1000), t0 + j * 0.42, 0.3 * (1 - 0.18 * j), 0.4 if k == 0 else -0.4)

    # night: he sits; the struggle
    place(bus['fol'], breath(0.6, 'out', 70, 0.6), E['sit'] - 0.3, 1.0, 0.0)
    place(bus['hit'], thud(71, 62, 0.22, 0.3), E['sit'], 1.0, 0.0)
    place(bus['fol'], ceramic_creak(0.35, 72, 0.25) * 0.4, E['sit'] + 0.02, 1.0, -0.1)    # the chair takes his weight
    place(bus['fol'], breath(0.45, 'in', 73, 0.6), E['grip'] - 0.1, 1.0, 0.0)
    place(bus['fol'], breath(0.5, 'out', 74, 0.8), p1[0], 1.0, 0.0)                         # strain
    place(bus['fol'], ceramic_creak(p1[1] - p1[0] + 0.1, 75, 0.7), p1[0] + 0.05, 0.35, 0.0)
    place(bus['hit'], thud(76, 60, 0.2, 0.3), E['creak1'], 1.0, 0.0)
    place(bus['fol'], breath(0.4, 'in', 77, 0.75), p2[0] - 0.25, 1.0, 0.0)
    place(bus['fol'], breath(0.7, 'out', 78, 1.1), p2[0] + 0.05, 1.0, 0.0)
    place(bus['fol'], ceramic_creak(p2[1] - p2[0] + 0.05, 79, 1.25), p2[0] + 0.05, 0.3, 0.0)
    place(bus['hit'], thud(80, 55, 0.3, 0.5), E['creak2'], 1.0, 0.0)
    place(bus['fol'], crack_tick(81), E['crack'], 0.9, -0.05)
    place(bus['fol'], breath(0.22, 'in', 82, 1.2), E['gasp'], 1.0, 0.0)                    # the breath catches
    place(bus['fol'], breath(1.3, 'out', 83, 0.7), E['slump'][0] + 0.1, 1.0, 0.0)          # gives up
    # the other lamp: filament pops on each flicker, a soft low thump when it holds
    f0, f1 = E['flicker']
    for a in [0.05, 0.26, 0.4]:
        place(bus['fol'], flicker_pop(90 + int(a * 100)), f0 + a * (f1 - f0), 0.7, 0.45)
    place(bus['hit'], thud(95, 48, 0.4, 0.6), f0 + 0.4 * (f1 - f0), 1.0, 0.3)
    place(bus['fol'], lp(noise(int(0.6 * SR)), 1400) * env(int(0.6 * SR), 0.1, 0.2) * 0.12, E['look'][0], 1.0, 0.0)   # he turns
    # the grey one takes theirs off and sets it down
    place(bus['fol'], breath(0.6, 'in', 100, 0.35), E['greyLift'][0], 1.0, 0.45)
    place(bus['fol'], ceramic_creak(0.3, 101, 0.2) * 0.4, E['greyOff'][0], 1.0, 0.45)
    place(bus['fol'], clink(102), E['clink'], 0.55, 0.4)
    # his loosens: a small soft release, then a long exhale
    place(bus['fol'], ceramic_creak(0.25, 110, 0.18) * 0.5, E['loosen'], 1.0, 0.0)
    place(bus['fol'], breath(1.6, 'out', 111, 0.8), E['lower'][0] + 0.05, 1.0, 0.0)
    place(bus['hit'], warm_tone(D - E['warm'][0] + 0.5), E['warm'][0], 0.16, 0.0)

    # bus processing (as in the pilot)
    for k in bus: bus[k] = np.nan_to_num(bus[k])
    for c in range(2):
        for k in ['fol', 'air', 'bed', 'drone', 'amb']: bus[k][c] = hp(bus[k][c], 90 if k in ('fol', 'air', 'amb') else 75, 3)
    ir_room = [reverb_ir(1.6, 3500, 1), reverb_ir(1.6, 3500, 2)]
    ir_hall = [reverb_ir(3.4, 1800, 3), reverb_ir(3.4, 1800, 4)]
    wet_f = np.stack([convolve(bus['fol'][c], ir_room[c]) for c in range(2)])
    wet_a = np.stack([convolve(bus['amb'][c], ir_hall[c]) for c in range(2)])
    wet_h = np.stack([convolve(bus['hit'][c], ir_hall[c]) for c in range(2)])
    hit_env = lp(np.abs(bus['hit']).max(0), 8); sc = 1 - 0.5 * np.clip(hit_env / (hit_env.max() + 1e-9) * 3, 0, 1)
    amb_mix = (bus['amb'] * 0.5 + wet_a * 0.5) * 0.9      # far away, behind a wall of room
    mix = (bus['bed'] * sc + bus['drone'] * sc + amb_mix + bus['fol'] + wet_f * 0.25 + bus['hit'] + wet_h * 0.3 + bus['air'] * 0.8)
    if os.environ.get('DUMP'):   # per-bus RMS (dB) per half second, for balancing
        parts = {'bed': bus['bed'] * sc, 'drone': bus['drone'] * sc, 'amb': amb_mix, 'fol': bus['fol'] + wet_f * 0.25, 'hit': bus['hit'] + wet_h * 0.3, 'air': bus['air'] * 0.8}
        for i in range(int(D * 2)):
            sl = slice(i * SR // 2, (i + 1) * SR // 2)
            print(f'{i / 2:5.1f} ' + ' '.join(f'{k}:{20 * np.log10(np.sqrt((v[0, sl] ** 2).mean()) + 1e-9):6.1f}' for k, v in parts.items()))
    mix = np.tanh(mix / np.abs(mix).max() * 1.6) / np.tanh(1.6)
    f = int(0.004 * SR); mix[:, :f] *= np.linspace(0, 1, f); mix[:, -int(0.4 * SR):] *= np.linspace(1, 0, int(0.4 * SR)) ** 2
    pcm = (np.clip(mix, -1, 1) * 0.95 * 32767).astype('<i2').T.copy()
    import wave
    with wave.open(out_path, 'wb') as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes(pcm.tobytes())
    print('wrote', out_path)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
