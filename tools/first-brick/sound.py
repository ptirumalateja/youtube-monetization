"""Audio for First Brick: original nylon-guitar waltz-ish bed in A minor (stands in for the
ref's licensed song), hummed lead, brick clacks synced to the wall build, level taps, exit steps.
Usage: python3 sound.py out.wav"""
import sys, wave, numpy as np

SR = 44100
DUR = 13.93
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); Rr = np.zeros(N)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i]
    l = gain * np.cos((pan + 1) * np.pi / 4); r = gain * np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * l * 1.414; Rr[i:i + len(sig)] += sig * r * 1.414

def hz(n):  # midi -> hz
    return 440 * 2 ** ((n - 69) / 12)

def pluck(f, dur=2.2, bright=0.5):
    n = int(dur * SR); p = int(SR / f)
    buf = rng.uniform(-1, 1, p)
    # soften the excitation (nylon)
    for _ in range(2): buf = 0.5 * (buf + np.roll(buf, 1))
    out = np.zeros(n); idx = 0; damp = 0.996
    b = buf.copy()
    for k in range(n):
        v = b[idx]; nxt = b[(idx + 1) % p]
        b[idx] = damp * (bright * v + (1 - bright) * 0.5 * (v + nxt))
        out[k] = v; idx = (idx + 1) % p
    env = np.minimum(1, np.arange(n) / (0.003 * SR))
    return out * env * np.exp(-np.arange(n) / SR * 1.2)

def hum(f, dur, vib=5.2):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = 2 * np.pi * np.cumsum(f * (1 + 0.006 * np.sin(2 * np.pi * vib * t) * np.minimum(1, t / 0.35))) / SR
    s = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.12 * np.sin(3 * ph)
    env = np.minimum(1, t / 0.09) * np.minimum(1, (dur - t) / 0.18).clip(0, 1)
    return s * env

# ---------- music ----------
BEAT = 60 / 78
T0 = 0.78
chords = [  # (bass, chord tones) midi
    (45, [52, 57, 60, 64]),  # Am
    (50, [53, 57, 62, 65]),  # Dm
    (40, [52, 56, 59, 64]),  # E
    (45, [52, 57, 60, 64]),  # Am
    (41, [53, 57, 60, 65]),  # F
]
pattern = [0, 2, 1, 3, 2, 1, 3, 2]  # eighth-note arpeggio over chord tones
for bar, (bass, tones) in enumerate(chords):
    tb = T0 + bar * 4 * BEAT
    if tb > DUR: break
    add(pluck(hz(bass), 3.0, 0.35), tb, 0.55, -0.1)
    for k, ix in enumerate(pattern):
        t = tb + k * BEAT / 2
        if t < DUR: add(pluck(hz(tones[ix]), 1.8, 0.45), t, 0.28 + 0.04 * (k % 2 == 0), 0.15)
# soft pickup before the downbeat (ref is quiet for the first 0.75 s)
add(pluck(hz(64), 1.5, 0.4), 0.05, 0.12, 0.2)
add(pluck(hz(69), 1.5, 0.4), 0.42, 0.12, 0.2)
# hummed lead (original line)
mel = [(76, 2), (72, 1), (74, 1), (77, 1.5), (76, .5), (74, 2), (71, 1), (72, 1), (74, 1), (76, 1), (69, 3.5), (72, .5), (77, 2), (76, 2)]
t = T0
for n, b in mel:
    if t >= DUR - .05: break
    d = min(b * BEAT, DUR - t)
    add(hum(hz(n), d + 0.05), t, 0.11, -0.05)
    t += b * BEAT

# simple reverb on the music
def reverb(x, secs=1.1, mix=0.22):
    n = int(secs * SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n) / SR * 4.2)
    ir[0] = 0
    from numpy.fft import rfft, irfft
    m = len(x) + n; F = 1 << (m - 1).bit_length()
    y = irfft(rfft(x, F) * rfft(ir, F), F)[: len(x)]
    return x + mix * y / np.max(np.abs(y) + 1e-9) * np.max(np.abs(x))
L = reverb(L); Rr = reverb(Rr)

# ---------- sfx (timings mirror scene.html) ----------
def clack(pitch=1.0):
    n = int(0.12 * SR); t = np.arange(n) / SR
    noise = rng.standard_normal(n) * np.exp(-t * 90)
    # crude band-pass: difference of smoothed versions
    k1 = np.convolve(noise, np.ones(3) / 3, 'same'); k2 = np.convolve(noise, np.ones(14) / 14, 'same')
    click = (k1 - k2) * 1.4
    thump = np.sin(2 * np.pi * 150 * pitch * t) * np.exp(-t * 45)
    wood = np.sin(2 * np.pi * 820 * pitch * t) * np.exp(-t * 70) * 0.4
    return click + 0.7 * thump + wood

def tick():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2900 * t) * 0.6 + rng.standard_normal(n) * 0.3) * np.exp(-t * 160)

def step():
    n = int(0.16 * SR); t = np.arange(n) / SR
    return (rng.standard_normal(n) * np.exp(-t * 40) * 0.5 + np.sin(2 * np.pi * 90 * t) * np.exp(-t * 30))

BL, NC = 72, 9
COURSE_END = [-1, 1.0, 2.0, 2.9, 3.7, 4.5, 5.2, 5.9, 6.9]
for c in range(NC):
    rown = 4
    t0 = -3 if c == 0 else COURSE_END[c - 1]; t1 = COURSE_END[c]
    for i in range(rown):
        T = t0 + (t1 - t0) * (i + 1) / rown
        if c == 1 and i < 1: T = -1
        if T > 0: add(clack(0.85 + 0.3 * rng.random()), T, 0.34, 0.25 + 0.1 * rng.random())
        if T > 0.1 and rng.random() < 0.6:  # trowel tap after setting
            add(tick() * 0.6, T + 0.07, 0.10, 0.3)
# perfectionist's tiny level adjustments (left side)
for tt in [0.35, 1.15, 1.7, 2.2, 4.1, 4.75, 5.3, 5.85, 7.4, 7.95, 8.6, 9.2, 12.3, 12.9, 13.5]:
    add(tick(), tt, 0.16, -0.45)
# level lifted / set back down
add(clack(1.6) * 0.5, 3.86, 0.18, -0.4); add(clack(1.6) * 0.5, 7.15, 0.18, -0.4)
# exit footsteps
for k, tt in enumerate([10.2, 10.45, 10.7, 10.95]):
    add(step(), tt, 0.25 * (1 - 0.15 * k), 0.6)

mix = np.stack([L, Rr], 1)
fade = np.ones(N); fn = int(0.5 * SR); fade[-fn:] = np.linspace(1, 0, fn)
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) / 0.89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok')
