# Procedural sound for "The Ball That Never Falls": heartbeat from the scene's own bpm curve, held-breath silence,
# one big reveal hit, creaks, riser/whoosh, loop-link tone. No samples are used, so no licence credits are needed.
# usage: python3 mix.py out.wav
import json, sys, wave, numpy as np
from cut import CUT, old_of_new, new_of_old
SR = 48000; TL = json.load(open('timeline.json')); T = CUT['T']; N = int(SR * T)
EVO = TL['events']   # master (20 s) times; EV is the same events on the 16 s cut
EV = {k: (new_of_old(np.array(v)).tolist() if isinstance(v, list) else float(new_of_old(v))) for k, v in EVO.items()}
rng = np.random.default_rng(7)
def db(g): return 10 ** (g / 20)
def tt(d): return np.arange(int(d * SR)) / SR
def keys(k, t):
    k = np.array(k, float); return np.interp(t, k[:, 0], k[:, 1])
def lp(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); return np.fft.irfft(X / np.sqrt(1 + (f / fc) ** (2 * order)), n=len(x))
def hp(x, fc, order=2):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); r = (f / fc + 1e-9) ** (2 * order); return np.fft.irfft(X * np.sqrt(r / (1 + r)), n=len(x))
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

# ---- heartbeat: beat times from the same bpm keys the scene uses
def beat_times():
    out, ph, last = [], 0.0, -1
    for i in range(int(TL['T'] * 600) + 1):
        ph += keys(TL['hb_bpm'], i / 600) / 60 / 600
        if int(ph) > last: last = int(ph); out.append(i / 600)
    return out
def thump(f0, d, g):
    t = tt(d); f = f0 * (1 + 1.6 * np.exp(-t * 38)); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 17)
    return (x + 0.25 * np.tanh(3 * x)) * g
sil0, sil1 = EVO['silence']
for b in beat_times():
    if sil0 <= b < sil1 or b > 12.0 and b < 16.2: continue
    bo, b = b, float(new_of_old(b))
    gain = keys([[0, -13], [9, -5], [11.3, -2], [12, -14], [20, -13]], bo)
    place('beat', thump(86, 0.38, 1.0), b, gain)
    place('beat', thump(64, 0.34, 0.8), b + 0.2 - 0.04 * min(1, bo / 10), gain - 4)
    place('beat', hp(noise(0.02), 1500) * np.exp(-tt(0.02) * 200), b, gain - 14)

# ---- drone bed: low harmonics (90-400 Hz so phones play it) that rise in pitch toward the reveal
def drone():
    t = tt(T); to = old_of_new(t); f = keys([[0, 62], [8, 66], [11.3, 76], [12.5, 55], [20, 62]], to); ph = 2 * np.pi * np.cumsum(f) / SR
    x = sum(np.sin(k * ph + k) * a for k, a in [(2, 1.0), (3, 0.7), (4, 0.45), (6, 0.25)]) + 0.5 * np.sin(ph)
    x = x * (1 + 0.18 * np.sin(2 * np.pi * 0.23 * t)); a = keys([[0, 0.5], [6, 0.8], [9.7, 1.0], [10.5, 0.0], [11.3, 0.0], [12.5, 0.55], [16, 0.5], [20, 0.5]], to)
    return hp(x, 85) * a
place('bed', drone() * 0.35, 0, -3)
# anxiety shimmer: rising sine pair with tremolo, only before the held breath, plus a thin high tone
t = tt(T); to = old_of_new(t); fr = keys([[0, 520], [9.7, 1650], [20, 520]], to); sh = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.sin(2 * np.pi * keys([[0, 3], [9.7, 11]], to) * t) ** 2
sh *= keys([[0, 0.0], [1.5, 0.0], [4, 0.2], [9.5, 0.55], [9.7, 0.0], [20, 0.0]], to); place('air', sh * 0.12, 0, -8)

# ---- creaks as the ball inches forward
def creak(d, f0, g=1.0):
    t = tt(d); f = f0 * (1 + 0.5 * np.sin(2 * np.pi * 9 * t) * np.exp(-t * 3)) * (1 + 0.8 * t); ph = 2 * np.pi * np.cumsum(f) / SR
    x = (np.sign(np.sin(ph)) * 0.4 + np.sin(2 * ph) * 0.3) * (0.6 + 0.4 * noise(d)) * np.sin(np.pi * t / d) ** 2
    return bp(x, 220, 2400) * g
for at, f0, d, g in [(3.4, 330, 0.9, -14), (5.6, 360, 1.1, -12), (7.2, 420, 1.0, -11), (8.6, 470, 0.8, -10), (9.3, 520, 0.5, -10)]:
    place('sfx', creak(d, f0), float(new_of_old(at)), g)

# ---- hits
def crack(d=0.25): t = tt(d); return hp(noise(d), 2000) * np.exp(-t * 28)
def body(f_hi, f_lo, d, k=22): t = tt(d); f = f_lo + (f_hi - f_lo) * np.exp(-t * 14); x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * k); return x + 0.35 * np.tanh(2.5 * x)
def gong(f, d=3.5): t = tt(d); return sum(a * np.sin(2 * np.pi * f * m * t) * np.exp(-t * (1.4 + m * 0.5)) for m, a in [(1, 1), (1.51, 0.5), (2.32, 0.35), (3.02, 0.2)])
def hit(at, size, g):
    d = 3.2 if size > 0.6 else 1.4
    x = np.zeros(int(d * SR)); c = crack(); x[:len(c)] += c * 0.6
    b = body(260 if size > 0.6 else 190, 80, 1.2 if size > 0.6 else 0.7); x[:len(b)] += b * 1.0
    if size > 0.6: gg = gong(130, d); x += gg[:len(x)] * 0.22
    place('hit', reverb(x, 2.4 if size > 0.6 else 1.2, 0.30), at, g)
hit(0.0, 0.5, -3)                                                  # frame-0 hit
hit(EV['lurch'], 0.3, -6)                                          # the lurch
hit(EV['hit_reveal'], 1.0, 0)                                      # the big one
hit(EV['landing'], 0.3, -7)                                        # settles back to the start position
# reversed swell into the reveal (the held breath is silent; the swell fills the last 0.55 s after the lurch)
sw = hp(noise(0.8), 300) * np.linspace(0, 1, int(0.8 * SR)) ** 2.2; place('sfx', sw * 0.5, EV['hit_reveal'] - 0.8, -8)
# camera swing whoosh and calm after the reveal
sw0, sw1 = EV['swing']; d = sw1 - sw0 + 0.6; t = tt(d); w = noise(d)
w = bp(w, 200, 3000) * np.sin(np.pi * np.minimum(1, t / d * 1.05)) ** 1.5 * (0.4 + 0.6 * np.exp(-t * 0.8)); place('sfx', w, sw0, -9)
gl = sum(np.sin(2 * np.pi * f * tt(3.5)) * np.exp(-tt(3.5) * 1.3) * a for f, a in [(784, 0.6), (1175, 0.4), (1568, 0.25)]); place('air', reverb(gl, 2.5, 0.5) * 0.35, float(new_of_old(12.7)), -9)
# return riser (reverse feel), landing already placed above
r0, r1 = EV['return']; d = r1 - r0; t = tt(d); ri = bp(noise(d), 400, 4500) * (t / d) ** 2.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(keys([[0, 140], [d, 520]], t)) / SR) * (t / d) ** 2; place('sfx', ri, r0, -12)
# loop link: rising tone + crackle into frame 0
l0, l1 = EV['loop_tone']; d = l1 - l0; t = tt(d); lt = np.sin(2 * np.pi * np.cumsum(keys([[0, 180], [d, 640]], t)) / SR) * (t / d) ** 2 * 0.4
cr = (rng.random(len(t)) > 0.9985) * rng.standard_normal(len(t)); lt += hp(cr, 1800) * (t / d) * 0.6; place('air', lt, l0, -10)

# ---- master: duck bed/beats under hits, bass management, soft clip
mix = buses['bed'] + buses['beat'] + buses['sfx'] + buses['air']
duck = np.ones(N)
for ev, dd in [(0.0, 0.7), (EV['lurch'], 0.5), (EV['hit_reveal'], 1.6), (EV['landing'], 0.6)]:
    a = int(ev * SR); n = int(dd * SR); env = 1 - 0.65 * np.exp(-tt(dd) * 3.0); duck[a:a + n] = np.minimum(duck[a:a + n], env[:max(0, min(n, N - a))])
mix = mix * duck + buses['hit']
mix = np.tanh(mix * 0.9)
mix = mix / np.abs(mix).max() * db(-1.5)
fade = np.ones(N); fade[-int(0.01 * SR):] = np.linspace(1, 0, int(0.01 * SR)); fade[:int(0.002 * SR)] = np.linspace(0, 1, int(0.002 * SR)); mix *= fade
st = np.stack([mix, mix], 1); st[:, 1] = np.roll(st[:, 1], 18)   # tiny Haas offset for width
pcm = (np.clip(st, -1, 1) * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
