# Fully synthesised sound for The Higher He Got (no samples, so no credits). Sync points come from the scene:
# coin landing times and the parting time are read from output/meta.json (written by `node render.cjs meta`).
# python3 sound.py  -> output/sound.wav (48 kHz stereo, normalised to about -15 LUFS by measure.sh-style ffmpeg pass)
import json, os, subprocess, re
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'output')
TL = json.load(open(os.path.join(ROOT, 'timeline.json'))); EV = json.load(open(os.path.join(OUT, 'meta.json')))['events']
SR = 48000; DUR = TL['duration']; N = int(SR * DUR); rng = np.random.default_rng(8)
LAND = [t for t in EV['land'] if t >= -0.01]; PART = EV['part']; HIT = TL['hit']; D0, D1 = TL['dive']
tt = np.arange(N) / SR

def bus(): return np.zeros((2, N))
def place(b, sig, t0, gain=1.0, pan=0.0):
    i0 = int(round(t0 * SR)); s0 = max(0, -i0); i0 = max(0, i0); n = min(len(sig) - s0, N - i0)
    if n <= 0: return
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    b[0, i0:i0 + n] += sig[s0:s0 + n] * gain * l * 1.414; b[1, i0:i0 + n] += sig[s0:s0 + n] * gain * r * 1.414
def env_exp(n, tau): return np.exp(-np.arange(n) / (tau * SR))
def fft_filter(x, lo=None, hi=None, order=2):
    X = np.fft.rfft(x, axis=-1); f = np.fft.rfftfreq(x.shape[-1], 1 / SR); g = np.ones_like(f)
    if lo: g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    if hi: g *= 1 / np.sqrt(1 + (f / hi) ** (2 * order))
    return np.fft.irfft(X * g, n=x.shape[-1], axis=-1)
def sweep_noise(n, f_of_u, bw=0.6, seed=0):            # noise band whose centre follows f_of_u(u), overlap-add STFT
    r = np.random.default_rng(seed); x = r.standard_normal(n + 4096); out = np.zeros(n + 4096); win = np.hanning(2048); hop = 512
    f = np.fft.rfftfreq(2048, 1 / SR)
    for s in range(0, n, hop):
        fc = f_of_u(s / n); g = np.exp(-0.5 * (np.log2(np.maximum(f, 1) / fc) / bw) ** 2)
        out[s:s + 2048] += np.fft.irfft(np.fft.rfft(x[s:s + 2048] * win) * g) * win
    return out[:n] / 1.5
def midi(m): return 440.0 * 2 ** ((m - 69) / 12)

# ---------------------------------------------------------------- voices
def clink(f0, amp=1.0, dur=0.22):
    n = int(SR * (dur * 3)); t = np.arange(n) / SR; s = np.zeros(n)
    for ratio, a, dk in [(1, 1, 1), (2.32, 0.55, 0.7), (4.25, 0.4, 0.5), (6.63, 0.25, 0.32), (9.38, 0.15, 0.22)]:
        s += a * np.sin(2 * np.pi * f0 * ratio * t + rng.uniform(0, 6)) * np.exp(-t / (dur * dk))
    click = rng.standard_normal(n) * np.exp(-t / 0.0015) * 0.6
    body = np.sin(2 * np.pi * rng.uniform(190, 260) * t) * np.exp(-t / 0.035) * 0.9      # the "stack" thunk, audible on phones
    return (s * 0.5 + click + body) * amp
def bell(f, dur=1.6, amp=1.0, detune=0.0):          # music-box / celesta voice
    n = int(SR * dur * 2.2); t = np.arange(n) / SR; fr = f * (1 + detune * np.sin(2 * np.pi * 5.3 * t))
    ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.sin(ph) * np.exp(-t / dur) + 0.35 * np.sin(2 * ph) * np.exp(-t / (dur * 0.5)) + 0.12 * np.sin(4.02 * ph) * np.exp(-t / (dur * 0.25))
    return s * np.minimum(1, t / 0.003) * amp
def pad(freqs, n, cutoff_u, seed=1):                 # detuned saw pad with a time-varying low-pass done in chunks
    r = np.random.default_rng(seed); t = np.arange(n) / SR; x = np.zeros(n)
    for f in freqs:
        for d in (-0.004, 0.0, 0.005):
            ph = (f * (1 + d) * t + r.uniform()) % 1.0; x += (2 * ph - 1) / len(freqs)
    out = np.zeros(n); hop = 2048; win = np.hanning(hop * 2); fr = np.fft.rfftfreq(hop * 2, 1 / SR); xp = np.concatenate([x, np.zeros(hop * 2)]); op = np.zeros(n + hop * 2)
    for s in range(0, n, hop):
        fc = cutoff_u(s / n); g = 1 / np.sqrt(1 + (fr / fc) ** 4); op[s:s + hop * 2] += np.fft.irfft(np.fft.rfft(xp[s:s + hop * 2] * win) * g) * win
    return op[:n] / 1.5
def reverb(x, secs=1.8, mix=0.25, seed=3):
    r = np.random.default_rng(seed); n = int(SR * secs); t = np.arange(n) / SR
    ir = r.standard_normal((2, n)) * np.exp(-t * 6.9 / secs); ir[:, :int(0.012 * SR)] = 0; ir = fft_filter(ir, lo=200, hi=7000, order=1); ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    L = x.shape[1] + n; X = np.fft.rfft(x, n=L); Y = np.fft.irfft(X * np.fft.rfft(ir, n=L), n=L)[:, :x.shape[1]]
    return x + mix * Y

clinks, music, synth, hitb, air = bus(), bus(), bus(), bus(), bus()

# ---------------------------------------------------------------- coins: one clink per landing, pitch climbs as the stack grows
for i, tl in enumerate(LAND):
    u = i / max(1, len(LAND) - 1); dens = np.sum((np.array(LAND) > tl - 0.5) & (np.array(LAND) <= tl + 0.5))
    amp = (1.0 if i == 0 else 0.7) / max(1, dens / 2.5) ** 0.3
    if tl > TL['look_down'][0]: amp *= 0.35 * (1 - (tl - TL['look_down'][0]) / 0.6)      # the last few coins, almost inaudible
    f0 = 2100 + 1700 * u + rng.uniform(-180, 180)
    place(clinks, clink(f0, amp, 0.18 + 0.1 * (1 - u)), max(0, tl), 0.55, rng.uniform(-0.5, 0.5))
# shimmer bed that grows with the pour (6-11 s)
sh = sweep_noise(N, lambda u: 6500 + 2500 * u, 0.5, seed=11)
shg = np.interp(tt, [0, 5.5, 8, 10.6, 11.2, 11.35], [0, 0, 0.18, 0.45, 0.5, 0]); place(clinks, sh * shg, 0, 1.0)

# ---------------------------------------------------------------- music box: the couple's motif, warping as money pours in, broken at the parting
E = 0.326
motif = [(0, 76), (1, 81), (2, 80), (3, 76), (4, 78), (5, 73), (6, 76), (8, 71), (9, 76), (10, 81), (11, 83), (12, 81), (13, 80), (14, 78), (15, 76), (16.5, 73)]
for k, m in motif:
    t0 = k * E; wob = 0.004 * np.clip((t0 - 3.0) / 3.0, 0, 1)
    if t0 < PART - 0.2: place(music, bell(midi(m), 1.5, 0.5, wob), t0, 1.0, -0.2 + 0.4 * ((m % 5) / 4))
for m, d in [(57, 0), (64, 0.02), (69, 0.04)]: place(music, bell(midi(m), 3.0, 0.22), d, 1.0, 0)          # soft chord under frame 0
place(music, bell(midi(77), 1.8, 0.55, 0.012), PART, 1.0, 0.2); place(music, bell(midi(76), 1.8, 0.4, 0.012), PART + 0.012, 1.0, -0.2)   # the break: a minor second
# warm low drone for the bench (fades as he rises)
dr = np.sin(2 * np.pi * 110 * tt) * 0.5 + np.sin(2 * np.pi * 164.8 * tt) * 0.3 + np.sin(2 * np.pi * 220 * tt) * 0.2
place(music, dr * np.interp(tt, [0, 0.3, 4, 6.5], [0, 0.18, 0.14, 0]), 0, 1.0)

# ---------------------------------------------------------------- the climb: golden pad and rising tones, 6.3 -> 11.25
n = N; padsig = pad([110, 164.8, 220, 277.2, 329.6, 440], n, lambda u: 300 + 5200 * np.clip((u * DUR - 6) / 5.2, 0, 1) ** 1.6)
pg = np.interp(tt, [0, 5.5, 7, 10.8, 11.22, 11.3], [0, 0, 0.25, 0.6, 0.62, 0]); place(synth, padsig * pg, 0, 1.0)
for j, base in enumerate([220, 330, 440]):           # three rising sines (a shepard-like lift)
    f = base * 2 ** (np.clip((tt - 6.3) / 4.95, 0, 1) * 1.0); ph = 2 * np.pi * np.cumsum(f) / SR
    g = np.interp(tt, [0, 6.3, 8, 11.2, 11.27], [0, 0, 0.08, 0.16, 0]) * (1 - 0.3 * j)
    place(synth, np.sin(ph) * g, 0, 1.0, (-0.4, 0, 0.4)[j])

# ---------------------------------------------------------------- held breath, suck, HIT at 12.0
suck = sweep_noise(int(0.42 * SR), lambda u: 400 + 4000 * u, 0.8, seed=5) * np.linspace(0, 1, int(0.42 * SR)) ** 3
place(hitb, suck, HIT - 0.48, 0.5)
nh = int(3.5 * SR); th = np.arange(nh) / SR
crack = rng.standard_normal(nh) * np.exp(-th / 0.012) * np.minimum(1, th / 0.002); crack = fft_filter(crack[None], lo=2000)[0]
fb = 300 * (70 / 300) ** np.clip(th / 0.5, 0, 1); body = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(fb) / SR)) * np.exp(-th / 0.55)
gong = sum(a * np.sin(2 * np.pi * f * th) * np.exp(-th / d) for f, a, d in [(196, 0.5, 2.2), (293.7, 0.35, 1.8), (415.3, 0.25, 1.4), (587.3, 0.18, 1.0), (831, 0.1, 0.7)])
sub = np.sin(2 * np.pi * 46 * th) * np.exp(-th / 1.0)
place(hitb, crack * 0.45 + body * 0.9 + gong * 0.6 + sub * 0.8, HIT, 1.0)
# frame-0 hit (smaller): low thump under the first clink
n0 = int(0.6 * SR); t0a = np.arange(n0) / SR
place(hitb, np.sin(2 * np.pi * np.cumsum(140 * (60 / 140) ** np.clip(t0a / 0.25, 0, 1)) / SR) * np.exp(-t0a / 0.18) * 0.55, 0, 1.0)

# ---------------------------------------------------------------- after: wind at height, lonely motif, dive home
wind = sweep_noise(N, lambda u: 500 + 250 * np.sin(u * 23), 0.9, seed=21)
wg = np.interp(tt, [0, 11.9, 12.4, 16.0, 16.5, 17.6, 18], [0, 0, 0.32, 0.3, 0.12, 0.05, 0.03]) * (1 + 0.3 * np.sin(tt * 1.7)); place(air, wind * wg, 0, 1.0)
for t0, m in [(14.35, 76), (14.95, 72), (15.4, 69)]: place(music, bell(midi(m), 2.2, 0.45), t0, 1.0, 0)
place(music, bell(midi(45), 3.0, 0.25), 15.4, 1.0, 0)
nd = int((D1 - D0 + 0.3) * SR); dv = sweep_noise(nd, lambda u: 2600 * (300 / 2600) ** u, 0.7, seed=31) * np.sin(np.linspace(0, np.pi, nd)) ** 1.5
place(air, dv, D0, 0.7)
nt = int(0.5 * SR); tq = np.arange(nt) / SR; place(hitb, np.sin(2 * np.pi * 95 * tq) * np.exp(-tq / 0.12) * 0.35, D1, 1.0)
hum = (np.sin(2 * np.pi * 100 * tt) + 0.4 * np.sin(2 * np.pi * 200 * tt)) * np.interp(tt, [0, 17.4, 17.7, 18], [0, 0, 0.03, 0.03]); place(air, hum, 0, 1.0)
rv = bell(midi(76), 0.6, 0.35)[: int(0.45 * SR)][::-1]; place(music, rv, DUR - 0.45, 1.0)                 # reversed note that resolves into frame 0's first note

# ---------------------------------------------------------------- mix
music = reverb(music, 2.2, 0.35); clinks = reverb(clinks, 1.4, 0.18); hitb = reverb(hitb, 2.6, 0.22, seed=4)
for b in (clinks, music, synth, air): b[:] = fft_filter(b, lo=90, order=2)
duck = 1 - 0.6 * np.exp(-np.clip(tt - HIT, 0, None) / 0.5) * (tt >= HIT)
breath = np.interp(tt, [0, 11.28, 11.42, 11.97, 12.0], [1, 1, 0.03, 0.03, 1])      # held breath before the hit
music_g = np.interp(tt, [0, 6.5, 7.0], [0.55, 0.55, 0.9])
mix = (clinks * 0.9 * duck + music * music_g + synth * 1.7 + air * 0.8 * duck) * breath + hitb * 1.1
mix /= np.max(np.abs(mix)) + 1e-9
def write(x, path):
    pcm = (np.clip(x, -1, 1).T * 32767).astype('<i2'); import wave
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
def lufs(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r)[-1]), float(re.findall(r'Peak:\s+(-?[\d.]+) dBFS', r)[-1])
tmp = os.path.join(OUT, 'sound_raw.wav'); write(mix * 0.5, tmp); L, P = lufs(tmp)
g = 10 ** ((-15.0 - L) / 20) * 0.5; y = np.tanh(mix * g * 1.15) / 1.15                     # gain to target, soft-clip the transients
y *= min(1.0, 10 ** (-2.2 / 20) / (np.max(np.abs(y)) + 1e-9))
write(y, os.path.join(OUT, 'sound.wav')); print('sound.wav', lufs(os.path.join(OUT, 'sound.wav')))
