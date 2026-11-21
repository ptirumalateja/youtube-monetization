"""Synthesised sound bed for "You Can't Inspire Change" (Slow Light restyle).
Usage: python3 sound.py times.json out.wav
times.json comes from times.js (video-time of every event)."""
import json, sys, wave
import numpy as np

SR = 48000
ev = json.load(open(sys.argv[1]))
DUR = ev['dur'] + 0.3
N = int(DUR * SR)
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(7)


def place(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    n = min(len(sig), N - i)
    gl, gr = gain * np.sqrt(0.5 * (1 - pan)), gain * np.sqrt(0.5 * (1 + pan))
    L[i:i + n] += sig[:n] * gl; R[i:i + n] += sig[:n] * gr


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for k in range(len(x)): s = (1 - a) * x[k] + a * s; y[k] = s
    return y


def bandnoise(n, lo, hi):
    X = np.fft.rfft(rng.standard_normal(n)); f = np.fft.rfftfreq(n, 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    y = np.fft.irfft(X, n); return y / (np.abs(y).max() + 1e-9)


def chime(freq, dur=2.2, bright=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for mult, amp, dec in [(1, 1.0, 1.4), (2.0, 0.35, 0.8), (2.76, 0.45 * bright, 0.6), (5.4, 0.2 * bright, 0.25), (8.9, 0.08 * bright, 0.12)]:
        y += amp * np.sin(2 * np.pi * freq * mult * t + rng.random() * 6) * np.exp(-t / dec)
    y *= np.minimum(1, t / 0.003)
    return y / np.abs(y).max()


def pour(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    base = bandnoise(n, 900, 6000)
    gl = 0.55 + 0.45 * np.sin(2 * np.pi * (9 + 3 * np.sin(2 * np.pi * 1.3 * t)) * t)  # glug flutter
    sparkle = np.zeros(n)
    for k in range(int(dur * 26)):
        i = int(rng.random() * n); f = 2600 + rng.random() * 3200; m = int(0.05 * SR)
        tt = np.arange(min(m, n - i)) / SR
        sparkle[i:i + len(tt)] += 0.25 * np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.02)
    e = np.minimum(1, t / 0.06) * np.minimum(1, (dur - t) / 0.12)
    return (0.5 * base * gl + sparkle) * e


def slam():
    n = int(1.2 * SR); t = np.arange(n) / SR
    thud = np.sin(2 * np.pi * (95 * np.exp(-t * 6) + 45) * t) * np.exp(-t / 0.18)
    clank = sum(a * np.sin(2 * np.pi * f * t) * np.exp(-t / d) for f, a, d in [(612, 0.5, 0.25), (1377, 0.35, 0.18), (2290, 0.25, 0.12), (3480, 0.15, 0.08)])
    hit = bandnoise(n, 200, 5000) * np.exp(-t / 0.03)
    y = 1.0 * thud + 0.45 * clank + 0.5 * hit
    return y / np.abs(y).max()


def knock():
    n = int(0.35 * SR); t = np.arange(n) / SR
    y = np.sin(2 * np.pi * 420 * t) * np.exp(-t / 0.05) + 0.5 * np.sin(2 * np.pi * 1130 * t) * np.exp(-t / 0.03) + 0.6 * bandnoise(n, 300, 3000) * np.exp(-t / 0.012)
    return y / np.abs(y).max()


def strain(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 180 + 40 * np.sin(2 * np.pi * 7 * t)
    sq = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.3
    y = onepole_lp(sq, 900) + 0.3 * bandnoise(n, 1500, 4000) * (0.5 + 0.5 * np.sin(2 * np.pi * 11 * t))
    return y * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.1)


def sigh_tone():
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 392 * (2 ** (-np.minimum(t / 0.6, 1) * 5 / 12))
    y = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.04, 0.35)
    return y


def whoosh_rev(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    y = bandnoise(n, 300, 7000) * (t / dur) ** 2.2
    return y


def pad(dur, notes, gain=0.12):
    n = int(dur * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for k, f in enumerate(notes):
        for det in (-0.25, 0.25):
            y += np.sin(2 * np.pi * (f + det) * t + k) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.2 * t + k))
    y = onepole_lp(y, 1800)
    return gain * y / np.abs(y).max()


# --- note ladder: each new light rings one step higher (C major pentatonic)
penta = [523.25, 587.33, 659.25, 783.99, 880.0, 1046.5, 1174.66, 1318.5, 1568.0, 1760.0, 2093.0]

# hook: the pour is already flowing at frame 0, lid slams at slamHook
place(pour(0.5), 0.0, 0.32, 0.1)
place(slam(), ev['slamHook'], 0.95, 0.2)
place(chime(311.1, 1.4, 0.3), ev['slamHook'] + 0.02, 0.18, 0.2)  # sour bell under the slam
# rewind
place(whoosh_rev(0.42), 1.53, 0.42, 0.0)
# pours
for f, to, s0, s1, refused in ev['pours']:
    if s0 > DUR: continue
    place(pour(max(0.2, s1 - s0 + 0.15)), s0, 0.26 if not refused else 0.2, -0.1)
# lights -> rising chimes
for k, (i, t) in enumerate(ev['lit']):
    if t > DUR: continue
    note = penta[min(k, len(penta) - 1)]
    big = i in (3, 5)
    g = 0.55 if big else 0.42
    if t > ev['cta']: g *= 0.6
    place(chime(note, 2.4, 1.0), t, g, -0.3 + 0.06 * k)
    if big:
        place(chime(note * 1.5, 2.4, 0.6), t + 0.01, 0.25, 0.3)
# refusal in story
place(slam(), ev['slam'], 0.85, 0.2)
place(chime(311.1, 1.4, 0.3), ev['slam'] + 0.02, 0.16, 0.2)
for kt in ev['knocks']:
    place(knock(), kt, 0.75, 0.25)
place(strain(ev['twist'][1] - ev['twist'][0]), ev['twist'][0], 0.28, 0.2)
place(sigh_tone(), ev['sigh'], 0.22, -0.1)
# warm pad: low under the story, swelling into the ending chord
place(pad(ev['cta'] + 0.5, [130.81, 196.0, 261.63, 329.63], 0.10), 0.0, 1.0)
end = pad(DUR - ev['cta'] + 0.2, [130.81, 196.0, 261.63, 329.63, 392.0, 587.33], 0.2)
end *= np.minimum(1, np.arange(len(end)) / SR / 0.6)
place(end, ev['cta'] - 0.2, 1.0)

# master: soft clip + fade out
mix = np.stack([L, R], 1)
mix = np.tanh(mix * 1.1) / np.tanh(1.1)
fade = np.minimum(1, (DUR - np.arange(N) / SR) / 0.6)[:, None]
mix *= fade
mix *= 0.89 / np.abs(mix).max()
with wave.open(sys.argv[2], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', DUR)
