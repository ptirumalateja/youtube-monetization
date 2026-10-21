# The Ship Never Moves (v2, 24 s): sound mix.
# Recorded cinematic hits and whooshes from ../sfxlib (Freesound, CC0 / CC BY, credits in the .md), an ElevenLabs
# warp-field hum for the bed, and a synthesised pulse score (bass ostinato + low drum) that drives the flight.
# Every sound has a visual cause; hit times come from index.html's timeline.
# python3 mix_warp.py out.wav [elevenlabs_hum.mp3]
import sys, subprocess, numpy as np
SR = 48000; T = 24.0; N = int(SR * T)
LIB = "../sfxlib/"
HUM = sys.argv[2] if len(sys.argv) > 2 else None
rng = np.random.default_rng(1994)
t = np.arange(N) / SR
def sstep(a, b, x): k = np.clip((x - a) / (b - a), 0, 1); return k * k * (3 - 2 * k)
def env_at(a, b, fi, fo): return sstep(a, a + fi, t) * (1 - sstep(b - fo, b, t))
def filt(x, fn):
    X = np.fft.rfft(x); fr = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X * fn(np.maximum(fr, 1e-3)), len(x))
def lp(x, fc): return filt(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** 4))
def hp(x, fc): return filt(x, lambda f: (f / fc) ** 2 / np.sqrt(1 + (f / fc) ** 4))
def bp(x, f0, q): return filt(x, lambda f: 1 / (1 + q * q * (f / f0 - f0 / f) ** 2))
def load(name, speed=1.0):
    path = name if name.startswith('/') else LIB + name
    raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", path, "-af", f"asetrate={int(SR * speed)},aresample={SR}" if speed != 1 else "anull",
                          "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).astype(float); return x / (np.max(np.abs(x)) + 1e-9)
def peak_time(x):  # time of the loudest 20 ms block
    e = np.convolve(np.abs(x), np.ones(960) / 960, 'same'); return np.argmax(e) / SR
def place(bus, sig, at, gain=1.0, fade_out=None):
    sig = sig.copy()
    if fade_out: n = int(fade_out * SR); sig[-n:] *= np.linspace(1, 0, n) if len(sig) > n else 1
    i = int(round(at * SR)); s0 = 0
    if i < 0: s0 = -i; i = 0
    j = min(N, i + len(sig) - s0)
    if j > i: bus[i:j] += sig[s0:s0 + j - i] * gain
def place_peak(bus, sig, at, gain=1.0, pre=None, post=None, fade_out=None):  # line the sample's loudest moment up with `at`
    p = peak_time(sig); a = 0 if pre is None else max(0, int((p - pre) * SR)); b = len(sig) if post is None else int((p + post) * SR)
    place(bus, sig[a:b], at - (p - a / SR), gain, fade_out)
def punch(seed, size):  # transient crack + pitch-drop body + sub, to give a sample hit a hard front edge
    r = np.random.default_rng(seed); n = int(1.2 * SR); x = np.arange(n) / SR
    fr = 60 + 200 * np.exp(-x * 14); body = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(fr) / SR)) * np.exp(-x * 4.5)
    return (hp(r.standard_normal(n), 2500) * np.exp(-x * 45) * 0.7 + body + np.sin(2 * np.pi * 42 * x) * np.exp(-x * 2.5) * 0.6) * size

# timeline (matches index.html)
T_IGN, T_FULL, T_SLOW, T_ARR, T_TWIST, T_STOP, T_BLAST, T_COLL, T_GONE = 1.6, 2.6, 11.8, 14.0, 14.7, 17.8, 17.9, 18.0, 18.8
T_PL, T_LIGHT = 5.7, 10.0
def vraw(x):
    v = sstep(T_IGN, T_FULL, x); v = np.where(x > T_SLOW, v * (1 + (0.2 - 1) * sstep(T_SLOW, T_ARR, x)), v)
    v = np.where(x > 16.6, v * (1 - sstep(16.6, T_STOP, x)), v); return np.where(x < T_IGN, 0, v)
V = vraw(t)
amp = np.where(t < T_COLL, sstep(T_IGN, T_IGN + 0.7, t), 1 - sstep(T_COLL, T_GONE, t))
inside = env_at(6.5, 9.2, 0.3, 0.35)

hit = np.zeros(N); sfx = np.zeros(N); bed = np.zeros(N); score = np.zeros(N); tick = np.zeros(N)

# ------------------------------------------------ hits (sized: blast > twist > ignition > frame 0)
accent = load("869757__mikiko850__dark-suspense-accent.wav")
place(hit, accent[int(peak_time(accent) * SR) - int(0.01 * SR):], 0.0, 0.55)              # frame 0
gate = load("768664__berkup__portal-gate-opening.wav"); place_peak(sfx, gate, T_IGN + 0.15, 0.55)   # bubble forms
warp = load("735062__gammagool__fast-warp-in.wav"); place_peak(hit, warp, T_IGN, 0.7); place(hit, punch(1, 0.5), T_IGN)
plasma = load("850262__cvltiv8r__orbiting-plasma-burst-and-trail-fx.wav"); place_peak(sfx, plasma, T_IGN + 0.05, 0.45)
braam = load("722633__chakong__cinematic-braaam.wav"); place_peak(hit, braam, T_TWIST, 0.9, pre=0.05, post=3.0, fade_out=1.2); place(hit, punch(2, 0.7), T_TWIST)          # negative energy
place_peak(hit, accent, T_TWIST, 0.35)
implo = load("814047__qubodup__fantasy-implosion.wav"); place_peak(sfx, implo, T_BLAST - 0.02, 0.6, pre=1.2, post=0.05)     # sucks in...
boom = load("814046__qubodup__explosion-from-another-dimension.wav"); place_peak(hit, boom, T_BLAST + 0.05, 1.0, pre=0.08, post=2.6, fade_out=1.6); place(hit, punch(3, 0.9), T_BLAST)  # ...the blast

# ------------------------------------------------ movement: whooshes with a visual cause
jet = load("115555__vartioh__synth_jet.wav"); place_peak(sfx, jet, T_PL, 0.55)                     # planet roars past
woosh = load("649445__audiopapkin__cinematic-woosh-sfx-015.wav"); place_peak(sfx, woosh, T_PL + 0.1, 0.5)
subw = load("238375__stewdio2003__cp_subby_whoosh.aiff")
place_peak(sfx, subw, 2.35, 0.45)                                                                 # pull back after ignition
gw = load("752034__bachsambora__sci-fi-gateway.wav"); place_peak(sfx, gw, 6.55, 0.5)              # through the wall, in
place_peak(sfx, subw, 9.45, 0.5)                                                                  # and out
place_peak(sfx, woosh, 14.85, 0.35)                                                               # swing to the ring
place_peak(sfx, subw, 18.15, 0.35)
zap = load("19487__halleck__jacobsladdersingle2.flac"); place_peak(sfx, zap, T_LIGHT + 0.02, 0.5)   # light beam fires
sparks = load("849772__mikiko850__electric-sparks.wav"); place(sfx, sparks[:int(2.6 * SR)], 15.1, 0.22, fade_out=0.6)  # unstable ring
# light falls behind: a bright tone that drops in pitch
n = int(1.8 * SR); x = np.arange(n) / SR; ph = 2 * np.pi * np.cumsum(2400 * 0.5 ** (x / 1.1)) / SR
place(sfx, np.sin(ph) * np.exp(-x * 1.4) * np.clip(x * 80, 0, 1), T_LIGHT + 0.05, 0.12)

# ------------------------------------------------ bed: ElevenLabs warp-field hum (looped with crossfades), muffled inside the bubble
if HUM:
    h = load(HUM); L = len(h); xf = int(0.8 * SR); loop = np.zeros(N); pos = 0
    w = np.ones(L); w[:xf] = np.linspace(0, 1, xf); w[-xf:] = np.linspace(1, 0, xf)
    while pos < N: place(loop, h * w, pos / SR); pos += L - xf
    hum_env = amp * (0.55 + 0.45 * V) * (1 - 0.97 * env_at(14.0, 14.72, 0.15, 0.02))
    bed += (loop * (1 - inside) + lp(loop, 700) * inside) * hum_env * 0.28
# flowing-space rush follows the speed
noise = rng.standard_normal(N)
bed += (bp(noise, 650, 0.6) * 0.5 + bp(noise, 2400, 1.0) * 0.2) * V ** 1.3 * (1 - 0.8 * inside) * 0.09

# ------------------------------------------------ pulse score: 120 BPM bass ostinato (A), low drum on 1 and 3, opens up with the speed
BPM = 120; beat = 60 / BPM; e8 = beat / 2
bass = np.zeros(N); drum = np.zeros(N)
notes = [55.0, 55.0, 65.41, 55.0, 55.0, 73.42, 65.41, 49.0]                       # A1 A1 C2 A1 A1 D2 C2 G1
def bass_note(f, dur, bright):
    n = int(dur * SR); x = np.arange(n) / SR; ph = 2 * np.pi * f * x
    saw = sum(np.sin(k * ph) / k for k in range(1, 14)); sq = np.sin(ph) + 0.6 * np.sin(2 * ph)
    s = (saw * bright + sq * (1 - bright)) * np.exp(-x * 5.5) * np.clip(x * 400, 0, 1); return s
def kick(seed):
    n = int(0.5 * SR); x = np.arange(n) / SR; fr = 48 + 130 * np.exp(-x * 22); ph = 2 * np.pi * np.cumsum(fr) / SR
    r = np.random.default_rng(seed); return np.tanh(2.5 * np.sin(ph)) * np.exp(-x * 7) + hp(r.standard_normal(n), 1500) * np.exp(-x * 60) * 0.35
k = 0; tt = T_IGN
while tt < T_ARR - 0.01:                                                     # the flight
    b = float(np.interp(tt, [T_IGN, 6, 11.5], [0.3, 0.7, 1.0]))
    place(bass, bass_note(notes[k % 8] * (2 if tt > 9.5 and k % 4 == 3 else 1), e8 * 1.6, b), tt, 0.5 if not 6.5 < tt < 9.2 else 0.28)
    if k % 4 == 0: place(drum, kick(k), tt, 0.9 if not 6.5 < tt < 9.2 else 0.45)
    if k % 8 == 6 and tt > 4: place(drum, kick(k + 99), tt, 0.5)
    k += 1; tt += e8
tt = T_TWIST + beat                                                          # twist: half-time, darker
while tt < T_STOP - 0.3:
    place(bass, bass_note(41.2 if int((tt - T_TWIST) / beat) % 2 else 43.65, beat * 1.2, 0.8), tt, 0.55)
    place(drum, kick(int(tt * 10)), tt, 0.8); tt += beat
score += bass * 0.38 + drum * 0.42
# riser into the arrival (12.0 -> 14.0), cut into the held breath
n = int(2.0 * SR); x = np.arange(n) / SR; fr = 220 * 2 ** (x * 1.5); ph = 2 * np.pi * np.cumsum(fr) / SR
riser = (np.sin(ph) + 0.5 * np.sin(1.5 * ph)) * (x / 2.0) ** 2 + bp(rng.standard_normal(n), 1500, 0.5) * (x / 2.0) ** 3 * 0.8
place(sfx, riser, 12.0, 0.16)
# arrival pad: warm open fifth that swells as the star fills the frame
pad = sum(np.sin(2 * np.pi * f * t + i) for i, f in enumerate([220, 329.6, 440, 554.4]))
bed += lp(pad, 1800) * env_at(12.6, 14.05, 0.9, 0.08) * 0.05

# ------------------------------------------------ ship's clock: a soft tick every second (it never changes); alone in the held breath
def tk(seed):
    r = np.random.default_rng(seed); n = int(0.1 * SR); x = np.arange(n) / SR
    return bp(r.standard_normal(n), 3000, 3) * np.exp(-x * 150) * 1.3 + np.sin(2 * np.pi * 1900 * x) * np.exp(-x * 60) * 0.3 + np.sin(2 * np.pi * 760 * x) * np.exp(-x * 80) * 0.4
for s_ in range(24):
    g = 0.35 + 0.65 * float((6.5 < s_ < 9.3) or (14.0 <= s_ < 14.7)) if s_ not in (14,) else 1.0
    place(tick, tk(s_), float(s_), g)
place(tick, tk(140), 14.35, 0.8)

# ------------------------------------------------ end: wind + glass bell, loop-link rise into frame 0
wind = load("22331__sleepcircle__wind.ogg"); place(bed, wind[:int(5.5 * SR)] * np.minimum(1, np.arange(int(5.5 * SR)) / SR / 1.2), 18.7, 0.07, fade_out=1.5)
n = int(3.0 * SR); x = np.arange(n) / SR
bell = sum(a * np.sin(2 * np.pi * f * x) * np.exp(-x * d) for f, a, d in [(880, 1, 1.2), (1320.5, 0.5, 1.6), (1760, 0.35, 2.2), (2637, 0.2, 3)])
place(sfx, bell, 20.8, 0.12); place(sfx, bell, 22.2, 0.07)
rise = np.sin(2 * np.pi * np.cumsum(330 + 330 * sstep(23.0, 24.0, t)) / SR) * env_at(23.0, 24.0, 0.7, 0.05) * 0.05
bed += rise

# ------------------------------------------------ held breath (14.0-14.7): everything but the clock drops away
hold = 1 - 0.97 * env_at(14.02, 14.7, 0.12, 0.02)
for b_ in (bed, score, sfx): b_ *= hold
hit *= 1 - 0.97 * env_at(14.02, 14.69, 0.12, 0.01)

# ------------------------------------------------ buses: sub only on hit/score; phone-friendly high-pass elsewhere
sfx[:] = hp(sfx, 90); bed[:] = hp(bed, 70); tick[:] = hp(tick, 300); score[:] = hp(score, 35)
hit = lp(0.9 * np.tanh(hit / 0.9), 12000)
duck = 1 - 0.55 * np.clip(lp(np.abs(hit), 6) * 2.2, 0, 1)
mix = hit * 0.95 + (sfx * 0.9 + bed + score) * duck + tick * 0.6
rv = np.zeros(N)
for d, g in [(0.031, 0.35), (0.047, 0.3), (0.071, 0.25), (0.113, 0.2), (0.173, 0.15), (0.251, 0.1)]:
    k_ = int(d * SR); rv[k_:] += (hit + sfx * 0.5)[:-k_] * g
mix += lp(rv, 3000) * 0.4
st = np.stack([mix, mix], 1)
k_ = int(0.012 * SR); st[k_:, 1] += (sfx + bed * 0.5)[:-k_] * 0.15; st[:, 0] += (sfx + bed * 0.5) * 0.15
st = np.tanh(st * 1.3) / np.tanh(1.3)
st = np.stack([lp(st[:, c], 15000) for c in (0, 1)], 1)
def true_peak(x):
    n = len(x); X = np.fft.rfft(x); Y = np.zeros(2 * n + 1, complex); Y[:len(X)] = X; return np.max(np.abs(np.fft.irfft(Y, 4 * n))) * 4
tp = max(true_peak(st[:, 0]), true_peak(st[:, 1]))
GAIN_DBTP = float(sys.argv[3]) if len(sys.argv) > 3 else -4.9   # pre-AAC true-peak target; tuned so the AAC file lands near -15 LUFS
st *= 10 ** (GAIN_DBTP / 20) / tp
import wave
w = wave.open(sys.argv[1], 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(st, -1, 1) * 32767).astype('<i2').tobytes()); w.close(); print('ok', sys.argv[1])
