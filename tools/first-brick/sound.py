"""Audio for First Brick: SFX only (no music): brick clacks synced to the wall build, trowel taps,
level ticks, exit steps.
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

# no music (Teja: SFX only)

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

NC = 9
COURSE_END = [-1, 1.0, 2.0, 2.9, 3.7, 4.5, 5.2, 5.9, 6.9]
times = []
for c in range(NC):
    items = 3 if c % 2 == 0 else 4
    t0 = -3 if c == 0 else COURSE_END[c - 1]; t1 = COURSE_END[c]
    for i in range(items):
        T = t0 + (t1 - t0) * (i + 1) / items
        if c == 1 and i == 0: T = -1
        times.append(T)
times.sort()
for k, T in enumerate(times):
    if T <= 0: continue
    prev = times[k - 1]
    side = 1 if k % 2 else -1
    # builder grabs from a side pile (soft knock), then sets it (clack + trowel tap); all up on the wall, right of centre
    add(clack(1.25) * 0.45, prev + 0.3 * (T - prev), 0.16, 0.2 + 0.25 * side)
    add(clack(0.85 + 0.3 * rng.random()), T, 0.34, 0.3 + 0.1 * rng.random())
    if rng.random() < 0.6: add(tick() * 0.6, T + 0.07, 0.10, 0.3)

# perfectionist fussing (mirrors fuss()/tapWave() in scene3d.html): taps on the level, scrapes on each nudge
def wk(t):
    ss = lambda x: (lambda y: y * y * (3 - 2 * y))(min(1, max(0, x)))
    if t < 2.45: return 1 - ss((t - 2.2) / 0.25)
    if 3.9 < t < 6.05: return ss((t - 3.9) / 0.3) * (1 - ss((t - 5.8) / 0.25))
    if 7.2 < t < 9.45: return ss((t - 7.2) / 0.3) * (1 - ss((t - 9.2) / 0.25))
    if t > 12.1: return ss((t - 12.1) / 0.3)
    return 0
def fw(t, k):
    ph = (t * 0.62) % 3
    d = min(abs(ph - k - 0.5), abs(ph - k - 0.5 + 3), abs(ph - k - 0.5 - 3))
    x = min(1, max(0, (0.62 - d) / 0.25)); return x * x * (3 - 2 * x)
def scrape():
    n = int(0.09 * SR); t = np.arange(n) / SR
    z = rng.standard_normal(n); z = z - np.convolve(z, np.ones(6) / 6, 'same')
    return z * np.sin(np.pi * t / t[-1]) * 0.5
for j in range(int(DUR * 2.6)):
    t = (j + 0.25) / 2.6
    g = fw(t, 0) * wk(t)
    if g > 0.3: add(tick(), t, 0.2 * g, -0.45)
for j in range(int(DUR * 7 / np.pi)):
    t = (j + 0.5) * np.pi / 7
    g = fw(t, 2) * wk(t)
    if g > 0.3: add(scrape(), t - 0.04, 0.12 * g, -0.45)
# level lifted / set back down
add(clack(1.6) * 0.5, 3.86, 0.18, -0.4); add(clack(1.6) * 0.5, 7.15, 0.18, -0.4)
# perfectionist steps up onto his bricks and kneels back down
add(step(), 9.9, 0.22, -0.4); add(step(), 12.0, 0.2, -0.4)
# builder: steps down behind the wall, walks out right
add(step() * 0.6, 9.6, 0.15, 0.45); add(step() * 0.7, 9.9, 0.18, 0.5)
for k, tt in enumerate([10.2, 10.55, 10.9, 11.25]): add(step(), tt, 0.25 * (1 - 0.15 * k), 0.75)

mix = np.stack([L, Rr], 1)
fade = np.ones(N); fn = int(0.5 * SR); fade[-fn:] = np.linspace(1, 0, fn)
mix *= fade[:, None]
mix /= np.max(np.abs(mix)) / 0.89
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((mix * 32767).astype(np.int16).tobytes())
print('ok')
