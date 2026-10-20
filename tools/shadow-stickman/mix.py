# Procedural sound for "The Shadow That Stops Copying". Heartbeat from the scene's bpm curve, drone, footsteps whose shadow
# echo arrives late (sound follows the shadow's lag), lamp-stutter crackle, held-breath silence, one big reveal hit, loop tone.
# No samples, so no licence credits. usage: python3 mix.py out.wav
import json, sys, wave, numpy as np
SR = 48000; TL = json.load(open('timeline.json')); T = TL['T']; N = int(SR * T); EV = TL['events']
rng = np.random.default_rng(11)
def db(g): return 10 ** (g / 20)
def tt(d): return np.arange(int(d * SR)) / SR
def keys(k, t): k = np.array(k, float); return np.interp(t, k[:, 0], k[:, 1])
def lp(x, fc, order=2): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * order)), n=len(x))
def hp(x, fc, order=2): X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); r = (f / fc + 1e-9) ** (2 * order); return np.fft.irfft(X * np.sqrt(r / (1 + r)), n=len(x))
def bp(x, lo, hi): return hp(lp(x, hi), lo)
def noise(d): return rng.standard_normal(int(d * SR))
buses = {k: np.zeros(N) for k in ['hit', 'beat', 'bed', 'sfx', 'air']}
def place(bus, x, at, g=0.0):
    a = int(at * SR)
    if a < 0: x = x[-a:]; a = 0
    x = x[:max(0, N - a)]; buses[bus][a:a + len(x)] += x * db(g)
def reverb(x, rt=2.2, mix=0.35):
    n = int(rt * SR); ir = noise(rt) * np.exp(-tt(rt) * 6.9 / rt); ir = lp(ir, 3500); ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    L = len(x) + n; y = np.fft.irfft(np.fft.rfft(x, L) * np.fft.rfft(ir, L), L)[:len(x)]; y *= np.abs(x).max() / (np.abs(y).max() + 1e-9)
    return x * (1 - mix) + y * mix

# heartbeat
def beat_times():
    out, ph, last = [], 0.0, -1
    for i in range(int(T * 600) + 1):
        ph += keys(TL['hb_bpm'], i / 600) / 60 / 600
        if int(ph) > last: last = int(ph); out.append(i / 600)
    return out
def thump(f0, d, g):
    t = tt(d); f = f0 * (1 + 1.6 * np.exp(-t * 38)); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 17); return (x + 0.25 * np.tanh(3 * x)) * g
s0, s1 = EV['silence']; c0, c1 = EV['cut_ambience']
for b in beat_times():
    if s0 <= b < c1: continue                      # held breath, hit, then the ambience stays cut until 10.4
    g = keys([[0, -13], [8, -6], [10.4, -7], [14, -4], [15.8, -2], [16, -2]], b)
    place('beat', thump(86, 0.38, 1.0), b, g); place('beat', thump(64, 0.34, 0.8), b + 0.2, g - 4); place('beat', hp(noise(0.02), 1500) * np.exp(-tt(0.02) * 200), b, g - 14)

# drone bed (90-400 Hz) + rising anxiety shimmer before the held breath
t = tt(T); f = keys([[0, 58], [8, 64], [9.0, 74], [10, 52], [16, 58]], t); ph = 2 * np.pi * np.cumsum(f) / SR
x = sum(np.sin(k * ph + k) * a for k, a in [(2, 1.0), (3, 0.7), (4, 0.45), (6, 0.25)]) + 0.5 * np.sin(ph); x *= 1 + 0.2 * np.sin(2 * np.pi * 0.21 * t)
x = hp(x, 85) * keys([[0, 0.5], [6, 0.8], [8.2, 1.0], [8.3, 0.0], [10.4, 0.0], [11.2, 0.6], [14, 0.8], [15.7, 1.0], [15.8, 0.0], [16, 0.0]], t); place('bed', x * 0.35, 0, -3)
fr = keys([[0, 480], [8.2, 1500], [16, 480]], t); sh = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(2 * np.pi * keys([[0, 3], [8.2, 11]], t) * t) ** 2
sh *= keys([[0, 0], [1.5, 0], [3.5, 0.2], [8.0, 0.55], [8.2, 0], [16, 0]], t); place('air', sh * 0.12, 0, -8)

# footsteps while he walks in, then the sting when the shadow keeps its arm up
def step(g=1.0): d = 0.22; t = tt(d); return (thump(110, d, 0.9) + hp(noise(d), 800) * np.exp(-t * 60) * 0.25) * g
def scrape(d=0.28): t = tt(d); return bp(noise(d), 300, 2600) * np.sin(np.pi * t / d) ** 2 * 0.5
for at in [0.35, 1.25]: place('sfx', step(), at, -10)
d = 1.6; t = tt(d); sting = (np.sin(2 * np.pi * 311 * t) + np.sin(2 * np.pi * 330 * t)) * np.exp(-t * 2.2) * 0.3 + hp(noise(d), 3000) * np.exp(-t * 40) * 0.5   # dissonant pair + tick
place('air', reverb(sting, 2.0, 0.4), EV['disobey'] - 0.02, -8)
place('sfx', scrape(0.6), 5.2, -14); place('sfx', scrape(0.8), 7.2, -13)       # it leans: wall scrape, the head turn is a soft creak
# lamp stutter crackle (8.0-9.0) and relight buzz
cr = (rng.random(int(1.0 * SR)) > 0.9975) * rng.standard_normal(int(1.0 * SR)); place('sfx', hp(cr, 1500) * np.linspace(0.3, 1, int(1.0 * SR)), EV['stutter'][0], -10)
buzz = np.sin(2 * np.pi * 120 * tt(0.9)) * np.exp(-tt(0.9) * 2.5) + 0.4 * np.sin(2 * np.pi * 240 * tt(0.9)) * np.exp(-tt(0.9) * 3); place('sfx', buzz * 0.18, EV['relight'], -10)

# hits
def crack(d=0.25): return hp(noise(d), 2000) * np.exp(-tt(d) * 28)
def body(a, b, d, k=22): t = tt(d); f = b + (a - b) * np.exp(-t * 14); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * k); return x + 0.35 * np.tanh(2.5 * x)
def gong(f, d=3.5): t = tt(d); return sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * (1.4 + m * 0.5)) for m, a in [(1, 1), (1.51, 0.5), (2.32, 0.35), (3.02, 0.2)])
def hit(at, big, g):
    d = 3.2 if big else 1.4; x = np.zeros(int(d * SR)); c = crack(); x[:len(c)] += c * 0.6
    b = body(260 if big else 190, 80, 1.2 if big else 0.7); x[:len(b)] += b
    if big: x += gong(130, d)[:len(x)] * 0.22
    place('hit', reverb(x, 2.4 if big else 1.2, 0.30), at, g)
hit(0.0, False, -3); hit(EV['hit_reveal'], True, 0)
sw = hp(noise(0.8), 300) * np.linspace(0, 1, int(0.8 * SR)) ** 2.2; place('sfx', sw * 0.5, EV['hit_reveal'] - 0.8 + 0.12, -9)
gl = sum(np.sin(2 * np.pi * f * tt(3.5)) * np.exp(-tt(3.5) * 1.3) * a for f, a in [(784, 0.6), (1175, 0.4), (1568, 0.25)]); place('air', reverb(gl, 2.5, 0.5) * 0.35, EV['relight'] + 0.1, -9)
# the shadow's deliberate step toward us (12.0-12.9), then a rising sub-swell while it looms; blackout = silence, then frame-0 hit
place('hit', body(150, 55, 1.2, 9) * 0.9, 12.3, -4); place('sfx', scrape(0.5), 12.1, -11)
d = EV['blackout'] - 13.0; t = tt(d); ri = bp(noise(d), 120, 2500) * (t / d) ** 2.4 * 0.7 + 0.5 * np.sin(2 * np.pi * np.cumsum(keys([[0, 55], [d, 150]], t)) / SR) * (t / d) ** 2; place('sfx', ri, 13.0, -10)
# master
mix = buses['bed'] + buses['beat'] + buses['sfx'] + buses['air']
duck = np.ones(N)
for ev, dd in [(0.0, 0.7), (EV['hit_reveal'], 1.6), (12.3, 0.8)]:
    a = int(ev * SR); n = int(dd * SR); env = 1 - 0.65 * np.exp(-tt(dd) * 3.0); duck[a:a + n] = np.minimum(duck[a:a + n], env[:max(0, min(n, N - a))])
mix = np.tanh((mix * duck + buses['hit']) * 0.9); mix = mix / np.abs(mix).max() * db(-1.5)
bo = int(EV['blackout'] * SR); mix[bo:] = 0; fade = np.ones(N); fade[bo - int(0.02 * SR):bo] = np.linspace(1, 0, int(0.02 * SR)); fade[:int(0.002 * SR)] = np.linspace(0, 1, int(0.002 * SR)); mix *= fade
st = np.stack([mix, mix], 1); st[:, 1] = np.roll(st[:, 1], 18); pcm = (np.clip(st, -1, 1) * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
