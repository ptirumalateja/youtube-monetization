"""Last 1%: procedural sound design ("battery and rain" family, new for this reel). No samples, no credits.

python3 mix.py timing.json out.wav
Everything is synthesised in numpy and synced to the scene: foot contacts and leaps come from the hero's
path, the light-off clunks from the beats, the relight tinks from the lamp positions, the drop from T_PLUG.
The drop at T_PLUG (16.4 s) is left clean so music can be cut to it.
"""
import json, sys, wave
import numpy as np

T = json.load(open(sys.argv[1]))
out = sys.argv[2]
SR = 48000
DUR = T['DUR']
N = int(DUR * SR)
R = np.random.default_rng(7)
t_all = np.arange(N) / SR


def bus():
    return np.zeros((2, N))


def lp_fast(x, fc):
    # one-pole low-pass response applied in the frequency domain
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    return np.fft.irfft(X / (1 + 1j * f / fc), len(x))


def band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = 1 / (1 + 1j * f / hi) * (1j * f / lo) / (1 + 1j * f / lo)
    return np.fft.irfft(X * g, len(x))


def place(b, sig, t0, gain=1.0, pan=0.0):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    if i0 < 0:
        sig = sig[-i0:]
        i0 = 0
    n = min(len(sig), N - i0)
    l, r = np.sqrt(0.5 * (1 - pan)), np.sqrt(0.5 * (1 + pan))
    b[0, i0:i0 + n] += sig[:n] * gain * l
    b[1, i0:i0 + n] += sig[:n] * gain * r


def env(n, a, d):
    e = np.ones(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    e *= np.exp(-np.arange(n) / SR / d)
    return e


def tone(f0, f1, dur, a=0.004, d=0.2, shape='sin'):
    n = int(dur * SR)
    f = np.geomspace(f0, f1, n)
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) if shape == 'sin' else np.sign(np.sin(ph)) * 0.6 + np.sin(ph) * 0.4
    return s * env(n, a, d)


def noise(dur):
    return R.standard_normal(int(dur * SR))


# ---------- sounds ----------
def chirp(low=False):
    # phone low-battery chirp: two short descending beeps
    f = 0.82 if low else 1.0
    a = tone(1480 * f, 1400 * f, 0.09, 0.003, 0.05)
    b = tone(990 * f, 940 * f, 0.13, 0.003, 0.07)
    s = np.zeros(int(0.3 * SR))
    s[:len(a)] += a
    s[int(0.11 * SR):int(0.11 * SR) + len(b)] += b
    return s


def thump(f0=150, f1=48, dur=0.5):
    return np.tanh(2.2 * tone(f0, f1, dur, 0.002, 0.16)) + 0.3 * band(noise(dur), 2000, 9000) * env(int(dur * SR), 0.001, 0.012)


def power_down():
    return 0.7 * tone(420, 55, 0.5, 0.005, 0.22, 'sq') + 0.25 * band(noise(0.5), 60, 300) * env(int(0.5 * SR), 0.002, 0.12)


def clunk():
    n = noise(0.25)
    return band(n, 120, 1800) * env(len(n), 0.001, 0.035) * 1.2 + 0.4 * tone(90, 60, 0.25, 0.001, 0.06)


def step(soft):
    d = 0.16
    body = band(noise(d), 180, 1400) * env(int(d * SR), 0.001, 0.018)
    splash = band(noise(d), 2500, 11000) * env(int(d * SR), 0.004, 0.045) * 0.5
    return (body * (1.0 if not soft else 1.4) + splash) * 0.9


def whoosh(dur, lo=300, hi=3000):
    n = int(dur * SR)
    x = noise(dur)
    e = np.sin(np.linspace(0, np.pi, n)) ** 2
    return band(x, lo, hi) * e


def splash():
    d = 0.7
    n = int(d * SR)
    return band(noise(d), 1200, 12000) * env(n, 0.003, 0.16) * 1.1 + band(noise(d), 200, 900) * env(n, 0.002, 0.05)


def clack():
    d = 0.12
    return band(noise(d), 2500, 14000) * env(int(d * SR), 0.0005, 0.008) * 2 + tone(1900, 1700, d, 0.0005, 0.02) * 0.4


def surge():
    d = 2.2
    n = int(d * SR)
    up = tone(70, 520, 0.9, 0.004, 0.6, 'sq') * 0.35
    sub = tone(62, 40, d, 0.002, 0.7) * 1.1
    body = np.tanh(2.5 * tone(180, 70, d, 0.002, 0.35)) * 0.8
    crack = band(noise(d), 1500, 10000) * env(n, 0.001, 0.09) * 0.9
    s = sub + body + crack
    s[:len(up)] += up
    return s


def tink(f):
    return (tone(f, f, 0.6, 0.002, 0.18) + 0.4 * tone(f * 2.76, f * 2.76, 0.6, 0.001, 0.07)) * 0.5


def bell(f):
    d = 2.5
    return sum(tone(f * m, f * m, d, 0.003, 0.9 / (k + 1)) * a for k, (m, a) in enumerate([(1, 1), (2.0, 0.5), (2.76, 0.35), (5.4, 0.15)])) * 0.5


# ---------- buses ----------
bed, sfx, hit, step_b, room = bus(), bus(), bus(), bus(), bus()
BE = T['BEATS']
TP, TS, TRES = T['T_PLUG'], T['T_SW'], T['T_RESET']

# rain + city bed; muffled once we are in the bedroom (through the window), back to street at the loop
rain = np.vstack([band(noise(DUR), 900, 9000), band(noise(DUR), 900, 9000)]) * 0.07
drops = np.zeros((2, N))
for k in range(int(DUR * 25)):
    tt = R.uniform(0, DUR)
    place(drops, band(noise(0.03), 3000, 12000) * env(int(0.03 * SR), 0.0005, 0.004), tt, R.uniform(0.02, 0.07), R.uniform(-0.8, 0.8))
city = np.vstack([band(noise(DUR), 70, 350), band(noise(DUR), 70, 350)]) * 0.08
inroom = np.clip((t_all - TS) / 0.6, 0, 1) * (1 - np.clip((t_all - (DUR - 0.9)) / 0.8, 0, 1))
street_amb = rain + drops + city
muffled = np.vstack([lp_fast(street_amb[0], 700), lp_fast(street_amb[1], 700)]) * 0.55
bed += street_amb * (1 - inroom) + muffled * inroom
# held breath before the plug: the street ambience dips to near silence
dip = 1 - 0.92 * np.clip((t_all - (TP - 0.5)) / 0.25, 0, 1) * (t_all < TP)
bed *= dip
# room tone in the bedroom
room += np.vstack([band(noise(DUR), 60, 500), band(noise(DUR), 60, 500)]) * 0.03 * inroom

# frame 0: the warning chirp (heard across the loop seam)
place(hit, chirp(), 0.0, 0.6)
place(hit, thump(170, 50, 0.6), 0.0, 0.45)
place(sfx, whoosh(0.5, 400, 2500), 0.7, 0.25, 0.3)         # he turns to the street
place(sfx, tink(1568), 0.95, 0.35, 0.5)                     # the charger pings
# beats: the windows clunk down a notch with a lower chirp each time
for i, b in enumerate(BE):
    place(sfx, chirp(low=True), b - 0.02, 0.3 * (0.9 ** i))
    for k in range(2):
        place(sfx, clunk(), b + 0.05 + k * 0.08 + R.uniform(0, 0.04), 0.25, R.uniform(-0.6, 0.6))
# every lamp that dies gets its own electrical click + fizz + a short power-down
for x, to in zip(T['lampX'], T['lampOff']):
    if to > TP:
        continue
    pan = float(np.clip((x - 30) / 40, -0.7, 0.7))
    place(sfx, clack() * 0.6, to + 0.2, 0.5, pan)
    place(sfx, band(noise(0.22), 2000, 9000) * env(int(0.22 * SR), 0.002, 0.06), to, 0.18, pan)
    place(sfx, power_down(), to + 0.2, 0.3, pan)
# footsteps: hard while sprinting, heavier as he drags
for s in T['steps']:
    soft = s > 10.3
    place(step_b, step(soft), s, 0.42 if not soft else 0.36, -0.2 if int(s * 10) % 2 else 0.2)
    if soft:
        place(step_b, thump(120, 60, 0.25), s, 0.12)
# the cable dragging behind him: scrape noise that follows his speed
drag_amt = np.interp(t_all, [0, 1.5, 2.2, 10.3, 10.8, 11.7, 12.2, 13.0, 13.2, DUR], [0, 0, 1, 1, 0.2, 0, 0.5, 0.5, 0, 0])
scrape = band(noise(DUR), 1500, 6000) * (0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 7.3 * t_all)))
sfx += np.vstack([scrape, scrape]) * drag_amt * 0.05
lp_ = T['leaps']
place(sfx, whoosh(lp_['hurdleDown'] - lp_['hurdleUp'] + 0.1, 500, 4000), lp_['hurdleUp'], 0.5)
place(step_b, thump(140, 70, 0.3), lp_['hurdleDown'], 0.35)
place(sfx, whoosh(lp_['puddleDown'] - lp_['puddleUp'], 400, 3000), lp_['puddleUp'], 0.35)
place(sfx, splash(), lp_['puddleDown'] - 0.05, 0.55)
# the stumble: scuff, knee hits the wet pavement, heavy breaths
place(sfx, whoosh(0.3, 800, 5000), T['stumble'] - 0.4, 0.3)
place(hit, thump(130, 55, 0.4), T['stumble'], 0.4)
place(sfx, splash() * 0.5, T['stumble'], 0.3)
for k in range(3):
    place(sfx, band(noise(0.35), 400, 2500) * np.sin(np.linspace(0, np.pi, int(0.35 * SR))), T['stumble'] + 0.15 + k * 0.32, 0.12)
# tension: a rising pulse from the stumble to the reach, then the held breath (near silence)
tt = 10.9
k = 0
while tt < TP - 0.5:
    place(sfx, tone(220, 200, 0.12, 0.002, 0.05) * 0.6 + tone(110, 100, 0.12, 0.002, 0.06), tt, 0.2 + 0.2 * (tt - 10.9) / 3.0)
    tt += max(0.17, 0.5 - 0.06 * k)
    k += 1
rl = TP - 0.5 - 10.9
place(sfx, tone(160, 420, rl, 0.5, 9.0) * np.linspace(0.0, 1.0, int(rl * SR)) ** 2, 10.9, 0.16)
buzz = tone(100, 100, 0.5, 0.05, 9.0, 'sq') * np.linspace(0.1, 1, int(0.5 * SR))
place(sfx, band(buzz, 200, 4000), TP - 0.5, 0.07)
# THE DROP (the one big hit): plug clack, a tiny spark, the surge; lamps tink back on as the pulse passes
place(hit, clack(), TP - 0.01, 0.45)
place(sfx, band(noise(0.12), 3000, 12000) * env(int(0.12 * SR), 0.001, 0.02), TP, 0.25)
place(hit, surge(), TP, 0.7)
notes = [523, 587, 659, 784, 880, 988, 1047, 1175, 1319, 1397]
for i, x in enumerate(sorted(T['lampX'], key=lambda x: abs(T['PX'] - x))):
    place(sfx, tink(notes[i % len(notes)]), TP + 0.08 + abs(T['PX'] - x) / 38, 0.28, -0.5 + i * 0.1)
hum = tone(110, 110, 2.0, 0.2, 1.2) * 0.4 + tone(220, 220, 2.0, 0.2, 0.8) * 0.2
place(sfx, hum, TP + 0.2, 0.25)
place(sfx, whoosh(1.1, 200, 1800), TS - 0.6, 0.3)
# the reveal: the epic sound is cut dead at the phone, then one tiny dry tick at the connector
cut = 1 - 0.97 * np.clip((t_all - TS) / 0.12, 0, 1) * (1 - np.clip((t_all - (TRES - 0.6)) / 0.1, 0, 1))
sfx *= cut
hit *= cut
tick = band(noise(0.02), 3000, 12000) * env(int(0.02 * SR), 0.0002, 0.0025)
place(sfx, tick, 19.6, 0.5)
place(sfx, tick, 19.75, 0.25)
place(sfx, chirp(), TRES - 0.5, 0.35)                        # the real phone chirps as it dims
place(sfx, tone(300, 900, 1.6, 0.6, 9.0) * np.linspace(0, 1, int(1.6 * SR)) ** 2, DUR - 1.6, 0.14)   # rise into the loop

# side-chain the bed under the hits
hit_env = np.abs(hit).max(axis=0)
duck = 1 - 0.6 * np.clip(lp_fast(hit_env, 8) * 3, 0, 1)
mix = bed * duck + sfx + hit + step_b * (1 - inroom * 0.7) + room
# high-pass everything but the hit bus a little (phones), soft clip, normalise
mix = np.tanh(mix * 1.1)
mix /= np.abs(mix).max() / 0.9
pcm = (mix.T * 32767).astype(np.int16)
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('wrote', out, DUR)
