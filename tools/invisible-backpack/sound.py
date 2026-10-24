# Fully synthesised sound for The Invisible Backpack (no samples, so no credits). Sync points come from the scene:
# footsteps, rock focus times, the thud, every rock set down and stepped on, read from output/meta.json (`node render.cjs meta`).
# python3 sound.py  -> output/sound.wav (48 kHz stereo, about -15 LUFS, soft-clipped transients)
import json, os, re, subprocess, wave
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'output')
TL = json.load(open(os.path.join(ROOT, 'timeline.json'))); EV = json.load(open(os.path.join(OUT, 'meta.json')))['events']
SR = 48000; DUR = TL['duration']; N = int(SR * DUR); rng = np.random.default_rng(11)
CY = EV['cycles']; FOCUS = EV['focus']; STEPS = [t for t in EV['steps'] if t < 2.4]; THUD = EV['thud']; HIT = EV['hit']; CHORD = EV['chord']; FLASH = EV['flash']
tt = np.arange(N) / SR

def bus(): return np.zeros((2, N))
def place(b, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR)); s0 = max(0, -i0); i0 = max(0, i0); n = min(len(sig) - s0, N - i0)
    if n <= 0: return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    b[0, i0:i0 + n] += sig[s0:s0 + n] * gain * l * 1.414; b[1, i0:i0 + n] += sig[s0:s0 + n] * gain * r * 1.414
def fft_filter(x, lo=None, hi=None, order=2):
    X = np.fft.rfft(x, axis=-1); f = np.fft.rfftfreq(x.shape[-1], 1 / SR); g = np.ones_like(f)
    if lo: g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    return np.fft.irfft(X * g, n=x.shape[-1], axis=-1)
def band(n, fc_of_u, bw=0.6, seed=0):                  # noise band whose centre follows fc_of_u(u), overlap-add STFT
    r = np.random.default_rng(seed); x = r.standard_normal(n + 4096); out = np.zeros(n + 4096); win = np.hanning(2048); f = np.fft.rfftfreq(2048, 1 / SR)
    for s in range(0, n, 512):
        g = np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc_of_u(s / max(1, n))) / bw) ** 2)
        out[s:s + 2048] += np.fft.irfft(np.fft.rfft(x[s:s + 2048] * win) * g) * win
    return out[:n] / 1.5
def ar(n, a, r): t = np.arange(n) / SR; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / r)
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)
def reverb(x, secs=1.8, mix=0.25, seed=3):
    r = np.random.default_rng(seed); n = int(SR * secs); t = np.arange(n) / SR
    ir = r.standard_normal((2, n)) * np.exp(-t * 6.9 / secs); ir[:, :int(0.012 * SR)] = 0; ir = fft_filter(ir, lo=200, hi=7000, order=1); ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    L = x.shape[1] + n; Y = np.fft.irfft(np.fft.rfft(x, n=L) * np.fft.rfft(ir, n=L), n=L)[:, :x.shape[1]]
    return x + mix * Y

body, breath, sfx, chime, music, hitb, air = bus(), bus(), bus(), bus(), bus(), bus(), bus()

# ---------------------------------------------------------------- 0-7 s: heartbeat (lub-dub) and heavy breathing
def beat(amp):
    n = int(0.45 * SR); t = np.arange(n) / SR; f = 95 * (52 / 95) ** np.clip(t / 0.09, 0, 1)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.07) + 0.5 * np.sin(2 * np.pi * 170 * t) * np.exp(-t / 0.025)   # 170 Hz so phones hear it
    return np.tanh(1.6 * s) * amp
tb, k = 0.0, 0
while tb < 7.3:
    a = 0.9 if tb < 6.6 else 0.9 * (1 - (tb - 6.6) / 0.7); a *= 1.25 if k == 0 else 1.0
    place(body, beat(a), tb); place(body, beat(a * 0.6), tb + 0.27)
    tb += 0.83 - 0.12 * np.exp(-((tb - 2.2) / 0.8) ** 2); k += 1          # quickens around the reveal
def breath_cycle(seed, inh=0.85, exh=1.0, amp=1.0):
    ni, ne = int(inh * SR), int(exh * SR)
    i = band(ni, lambda u: 900 + 900 * u, 0.9, seed) * np.sin(np.linspace(0, np.pi, ni)) ** 1.5
    e = band(ne, lambda u: 700 - 250 * u, 0.9, seed + 1) * np.sin(np.linspace(0, np.pi, ne)) ** 0.8 * np.exp(-np.linspace(0, 1, ne))
    return np.concatenate([i * 0.6, e]) * amp
tb, k = 0.05, 0
while tb < 6.9:
    place(breath, breath_cycle(40 + k, amp=1.0 if tb < 6 else 0.6), tb, 1.0, 0.1); tb += 1.61; k += 1
place(breath, band(int(0.35 * SR), lambda u: 1300 + 900 * u, 0.8, 77) * np.sin(np.linspace(0, np.pi, int(0.35 * SR))) ** 2, 7.0, 0.9)   # catch of breath as he looks up
place(breath, breath_cycle(91, 0.5, 1.7, 0.75), 8.25)                                                                                     # long exhale of relief
# gritty footsteps in the dust
for ts in STEPS:
    n = int(0.22 * SR); t = np.arange(n) / SR
    g = fft_filter((rng.standard_normal(n) * np.exp(-t / 0.05))[None], lo=300, hi=2600)[0] + np.sin(2 * np.pi * 120 * t) * np.exp(-t / 0.04) * 0.6
    place(sfx, g * 0.5, ts, 1.0, -0.15)
# a dark low drone under the walk and the inventory (D minor), fading at the decision
dr = sum(a * np.sin(2 * np.pi * f * tt + p) for f, a, p in [(73.4, 0.5, 0), (110, 0.35, 1), (146.8, 0.25, 2), (174.6, 0.18, 3)])
place(music, dr * np.interp(tt, [0, 0.4, 6.8, 7.6, 8.6], [0, 0.16, 0.2, 0.08, 0]) * (1 + 0.25 * np.sin(2 * np.pi * 0.31 * tt)), 0, 1.0)

# frame-0 hit: low thump with the first heartbeat
n0 = int(0.7 * SR); t0 = np.arange(n0) / SR
place(hitb, np.tanh(2 * np.sin(2 * np.pi * np.cumsum(150 * (55 / 150) ** np.clip(t0 / 0.3, 0, 1)) / SR)) * np.exp(-t0 / 0.22) * 0.5, 0, 1.0)

# ---------------------------------------------------------------- 2.0 s: flash and x-ray (glass shimmer sweep + a cold hum while the x-ray holds)
nz = int(0.9 * SR); place(sfx, band(nz, lambda u: 9000 * (1500 / 9000) ** u, 0.5, 5) * np.exp(-np.linspace(0, 5, nz)), FLASH, 0.9)
for f, a in [(1318.5, 0.25), (1975.5, 0.18), (2637, 0.12)]:
    n = int(1.4 * SR); t = np.arange(n) / SR; place(chime, np.sin(2 * np.pi * f * t) * ar(n, 0.005, 0.5) * a, FLASH, 1.0, 0.2)
xh = (np.sin(2 * np.pi * 220 * tt) + 0.5 * np.sin(2 * np.pi * 330 * tt)) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt))
place(sfx, xh * np.interp(tt, [0, FLASH, FLASH + 0.05, FLASH + 0.5, FLASH + 0.95], [0, 0, 0.06, 0.05, 0]), 0, 1.0)
place(hitb, np.sin(2 * np.pi * 70 * t0) * np.exp(-t0 / 0.25) * 0.45, FLASH, 1.0)

# ---------------------------------------------------------------- 4-7 s: a soft tick as each rock comes into focus
for i, tf in enumerate(FOCUS):
    n = int(0.25 * SR); t = np.arange(n) / SR; f = 1500 * 2 ** (i / 24)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.045) + 0.4 * np.sin(2 * np.pi * 2.7 * f * t) * np.exp(-t / 0.02) + rng.standard_normal(n) * np.exp(-t / 0.002) * 0.3
    place(chime, s * 0.32, tf, 1.0, (-0.3, 0.3)[i % 2])

# ---------------------------------------------------------------- 8.0 s: the heavy thud as the bag hits the ground (plus dust)
nt = int(1.6 * SR); t = np.arange(nt) / SR
thud = np.tanh(2.4 * np.sin(2 * np.pi * np.cumsum(160 * (48 / 160) ** np.clip(t / 0.25, 0, 1)) / SR)) * np.exp(-t / 0.3)
crunch = fft_filter((rng.standard_normal(nt) * np.exp(-t / 0.06))[None], lo=150, hi=1800)[0]
place(hitb, thud * 1.0 + crunch * 0.45 + np.sin(2 * np.pi * 42 * t) * np.exp(-t / 0.5) * 0.6, THUD, 1.0)
place(sfx, band(int(1.2 * SR), lambda u: 1800 - 900 * u, 1.0, 9) * np.exp(-np.linspace(0, 4, int(1.2 * SR))) * 0.5, THUD + 0.03, 1.0)     # dust settling
place(hitb, band(int(0.3 * SR), lambda u: 400 + 3000 * u, 0.8, 3) * np.linspace(0, 1, int(0.3 * SR)) ** 3 * 0.25, THUD - 0.3, 1.0)       # suck into it

# ---------------------------------------------------------------- 9-14 s: each rock lifted, set down (knock) and stepped on (clink); D major, rising
SCALE = [74, 76, 78, 81, 83, 86, 88]                       # D5 E5 F#5 A5 B5 D6 E6
def clink(f0, amp):
    n = int(1.6 * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for ratio, a, d in [(1, 1, 0.9), (2.76, 0.45, 0.35), (5.40, 0.25, 0.15), (8.93, 0.12, 0.07)]:
        s += a * np.sin(2 * np.pi * f0 * ratio * t + rng.uniform(0, 6)) * np.exp(-t / d)
    knock = np.sin(2 * np.pi * 210 * t) * np.exp(-t / 0.03) * 0.9 + rng.standard_normal(n) * np.exp(-t / 0.003) * 0.5
    return (s * 0.55 + knock) * amp
for k, c in enumerate(CY):
    place(chime, clink(midi(SCALE[k]), 0.55 + 0.05 * k), c['s1'] - 0.03, 1.0, -0.25 + 0.08 * k)               # step on it: clink
    n = int(0.3 * SR); t = np.arange(n) / SR
    place(sfx, (np.sin(2 * np.pi * 120 * t) * np.exp(-t / 0.06) + fft_filter((rng.standard_normal(n) * np.exp(-t / 0.03))[None], lo=200, hi=1500)[0] * 0.4) * 0.6, c['p1'], 1.0)   # set down
    if k >= 1:                                                                                                    # the rock floats up out of the bag
        nf = int((c['g1'] - c['g0']) * SR) + 1; place(air, band(nf, lambda u: 500 + 2000 * u, 0.7, 60 + k) * np.sin(np.linspace(0, np.pi, nf)) * 0.35, c['g0'], 1.0, -0.3)
# warm D major pad that opens up as he builds, held breath before the payoff
def pad(freqs, cutoff_u, seed=1):
    r = np.random.default_rng(seed); x = np.zeros(N)
    for f in freqs:
        for d in (-0.004, 0.0, 0.005): ph = (f * (1 + d) * tt + r.uniform()) % 1.0; x += (2 * ph - 1) / len(freqs)
    out = np.zeros(N + 4096); hop = 2048; win = np.hanning(hop * 2); fr = np.fft.rfftfreq(hop * 2, 1 / SR); xp = np.concatenate([x, np.zeros(hop * 2)])
    for s in range(0, N, hop):
        g = 1 / np.sqrt(1 + (fr / cutoff_u(s / N)) ** 4); out[s:s + hop * 2] += np.fft.irfft(np.fft.rfft(xp[s:s + hop * 2] * win) * g) * win
    return out[:N] / 1.5
ps = pad([73.4, 110, 146.8, 185, 220, 293.7], lambda u: 250 + 4000 * np.clip((u * DUR - 9.0) / 5.5, 0, 1) ** 1.4)
place(music, ps * np.interp(tt, [0, 8.8, 9.6, 12.0, 14.3, 14.55, 15.0, 15.3, 18], [0, 0, 0.18, 0.32, 0.45, 0.04, 0.04, 0.1, 0.08]), 0, 1.0)
for j, base in enumerate([293.7, 440]):                     # rising tones under the rise
    f = base * 2 ** (np.clip((tt - 12.0) / 2.5, 0, 1) * (7 / 12)); g = np.interp(tt, [0, 12.0, 13.0, 14.4, 14.55], [0, 0, 0.05, 0.08, 0]) * (1 - 0.3 * j)
    place(music, np.sin(2 * np.pi * np.cumsum(f) / SR) * g, 0, 1.0, (-0.35, 0.35)[j])

# ---------------------------------------------------------------- ~13 s: the hit (rock 5, the crowd below)
nh = int(3.5 * SR); th = np.arange(nh) / SR
crack = fft_filter((rng.standard_normal(nh) * np.exp(-th / 0.012) * np.minimum(1, th / 0.002))[None], lo=2000)[0]
fb = 300 * (70 / 300) ** np.clip(th / 0.5, 0, 1); hb = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(fb) / SR)) * np.exp(-th / 0.55)
gong = sum(a * np.sin(2 * np.pi * f * th) * np.exp(-th / d) for f, a, d in [(146.8, 0.5, 2.0), (220, 0.35, 1.6), (293.7, 0.25, 1.3), (440, 0.15, 0.9), (587.3, 0.1, 0.6)])
place(hitb, crack * 0.4 + hb * 0.85 + gong * 0.55 + np.sin(2 * np.pi * 46 * th) * np.exp(-th / 0.9) * 0.7, HIT, 1.0)
place(hitb, band(int(0.4 * SR), lambda u: 500 + 4000 * u, 0.8, 7) * np.linspace(0, 1, int(0.4 * SR)) ** 3 * 0.4, HIT - 0.42, 1.0)

# ---------------------------------------------------------------- 15 s: one warm piano chord (D add9), wind, lamp
def piano(f, amp, dur=5.0):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n); B = 0.0004
    for h in range(1, 11):
        fh = h * f * np.sqrt(1 + B * h * h)
        if fh > 9000: break
        for det in (-0.6, 0.6): s += (1 / h ** 1.3) * np.sin(2 * np.pi * (fh + det) * t + rng.uniform(0, 6)) * np.exp(-t / (3.2 / (1 + 0.35 * h)))
    hammer = fft_filter((rng.standard_normal(n) * np.exp(-t / 0.004))[None], lo=800, hi=5000)[0] * 0.15
    return (s * 0.5 + hammer) * np.minimum(1, t / 0.003) * amp
for m, a, d in [(50, 0.55, 0.0), (57, 0.45, 0.012), (62, 0.45, 0.02), (66, 0.38, 0.028), (76, 0.3, 0.036)]:
    place(music, piano(midi(m), a), CHORD + d, 1.0, (m - 62) / 30)
wind = band(N, lambda u: 480 + 260 * np.sin(u * 19) + 120 * np.sin(u * 47), 1.0, 21)
wg = np.interp(tt, [0, 0.5, 6.5, 8.5, 14.6, 15.0, 15.6, 18], [0.04, 0.08, 0.08, 0.03, 0.03, 0.1, 0.32, 0.3]) * (1 + 0.35 * np.sin(tt * 1.3) * np.sin(tt * 0.7))
place(air, wind * wg, 0, 1.0); place(air, band(N, lambda u: 2200 + 600 * np.sin(u * 31), 0.6, 22) * wg * 0.25, 0, 1.0, 0.4)
place(sfx, (np.sin(2 * np.pi * 110 * tt) + 0.3 * np.sin(2 * np.pi * 220 * tt)) * np.interp(tt, [0, 15.0, 15.6, 18], [0, 0, 0.02, 0.02]), 0, 1.0)

# ---------------------------------------------------------------- mix
music = reverb(music, 2.6, 0.38); chime = reverb(chime, 1.8, 0.3, seed=5); hitb = reverb(hitb, 2.4, 0.22, seed=4); breath = reverb(breath, 1.0, 0.12, seed=6)
for b in (breath, sfx, chime, music, air): b[:] = fft_filter(b, lo=90, order=2)
duck = np.ones(N)
for th0, d in [(THUD, 0.55), (HIT, 0.6)]: duck *= 1 - d * np.exp(-np.clip(tt - th0, 0, None) / 0.45) * (tt >= th0)
hush = np.interp(tt, [0, 14.45, 14.6, 14.97, 15.0], [1, 1, 0.12, 0.12, 1])            # held breath before the payoff chord
mix = (body * 0.9 + breath * 0.8 + sfx * 0.9 * duck + chime * 1.0 + music * 1.0 * duck + air * 0.9) * hush + hitb * 1.1
mix /= np.max(np.abs(mix)) + 1e-9
def write(x, path):
    pcm = (np.clip(x, -1, 1).T * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])
tmp = os.path.join(OUT, 'sound_raw.wav'); write(mix * 0.5, tmp); L, P = lufs(tmp)
g = 10 ** ((-15.0 - L) / 20) * 0.5; y = np.tanh(mix * g * 1.15) / 1.15
y *= min(1.0, 10 ** (-2.0 / 20) / (np.max(np.abs(y)) + 1e-9))
write(y, os.path.join(OUT, 'sound.wav')); print('sound.wav (LUFS, peak dBFS):', lufs(os.path.join(OUT, 'sound.wav')))
