#!/usr/bin/env python3
"""Synthesised sound design for "Why can't you tickle yourself?" (cut v3, 23.2 s). All cues are numpy-generated (no licences).
Idea carried by ear: EXPECTED touches are low-passed, soft and short; the UNEXPECTED touch (15.3 s) is bright, wide and full.
Phones can't reproduce < ~90 Hz: body energy lives at 90-400 Hz, the sub exists only on the hit bus.
usage: python3 sfx_tickle.py <out_sfx.wav>   -> stereo 48 kHz float32 wav (no voice)"""
import sys, numpy as np
from scipy import signal
from scipy.io import wavfile
SR = 48000; DUR = 23.2; N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
def t_of(n): return np.arange(n) / SR
def add(sig, t0, pan=0.0, gain=1.0):
    i0 = int(t0 * SR); n = len(sig); a = max(0, -i0); b = min(n, N - i0)
    if b <= a: return
    g = gain; l = g * np.sqrt(0.5 * (1 - pan)); r = g * np.sqrt(0.5 * (1 + pan))
    L[i0 + a:i0 + b] += sig[a:b] * l * np.sqrt(2) / np.sqrt(2); R[i0 + a:i0 + b] += sig[a:b] * r
def env(n, a, d, shape=3.0):  # attack/decay envelope, seconds
    t = t_of(n); e = np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / max(d, 1e-4)); return e
def lp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=4): return signal.sosfilt(signal.butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, f1, f2, o=3): return signal.sosfilt(signal.butter(o, [f1, f2], 'band', fs=SR, output='sos'), x)
def noise(n): return rng.standard_normal(n)
def tone(n, f, harm=((1, 1.0),), detune=0.0):
    t = t_of(n); y = np.zeros(n); ph = rng.uniform(0, 6.28)
    for h, a in harm: y += a * np.sin(2 * np.pi * f * h * (1 + detune * (h - 1)) * t + ph * h)
    return y
def bell(f, dur, bright=1.0, root_harm=(1, 2.01, 2.76, 4.07, 5.4)):
    n = int(dur * SR); t = t_of(n); y = np.zeros(n)
    for k, h in enumerate(root_harm): y += (0.6 ** k) * np.sin(2 * np.pi * f * h * t) * np.exp(-t / (dur * (0.45 / (1 + 0.7 * k)))) * (bright if k else 1.0)
    return y * np.minimum(t / 0.002, 1)
def whoosh(dur, f1, f2, up=True, q=1.0):  # swept band noise
    n = int(dur * SR); t = t_of(n); x = noise(n); y = np.zeros(n); blocks = 24
    for i in range(blocks):
        s, e = i * n // blocks, (i + 1) * n // blocks; fc = np.exp(np.interp(i / (blocks - 1), [0, 1], [np.log(f1), np.log(f2)] if up else [np.log(f2), np.log(f1)]))
        seg = bp(x[s:e], max(60, fc * 0.7), min(SR / 2 - 100, fc * 1.4), 2); y[s:e] = seg
    return y * np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5
def thump(f0=130, dur=0.35, drop=0.5, click=0.3):  # soft body hit, low-passed = "expected"
    n = int(dur * SR); t = t_of(n); f = f0 * (1 - drop * (1 - np.exp(-t / 0.06))); ph = 2 * np.pi * np.cumsum(f) / SR
    y = np.sin(ph) * np.exp(-t / 0.09) + click * lp(noise(n), 1800) * np.exp(-t / 0.012); return y
def sparkle(dur, f_lo=2500, f_hi=9000, rate=60):  # fine glassy ticks
    n = int(dur * SR); y = np.zeros(n); k = int(dur * rate)
    for _ in range(k):
        i = rng.integers(0, n - 200); f = rng.uniform(f_lo, f_hi); tt = t_of(200); y[i:i + 200] += np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.0015) * rng.uniform(0.2, 1)
    return y
ROOT = 196.0   # prediction chime family (G3); the Ladder uses 106 Hz, Night Sky its own palette
def chime(t0, pan=0.0, g=0.5): add(bell(ROOT * 2, 1.4), t0, pan, g); add(bell(ROOT * 3, 1.0, 0.7), t0, pan * 0.5, g * 0.5)
def pulse_tick(t0, f=ROOT * 1.5, pan=0.0, g=0.3, soft=True):
    n = int(0.09 * SR); t = t_of(n); y = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.018); add(lp(y, 2500) if soft else y, t0, pan, g)
# ======================= CUE SHEET (edit time, seconds) =======================
# 0.0 low pulse + air: the held ghost fingertip appears
add(lp(tone(int(1.8 * SR), 92, ((1, 1.0), (2, 0.4))), 400) * env(int(1.8 * SR), 0.5, 0.9), 0.0, 0.0, 0.5)
add(hp(whoosh(1.5, 600, 3600, True), 300) , 0.1, -0.3, 0.16)
# ghost glides ahead (0.3-1.65): glassy shimmer sweeping L->R, then prediction chime on arrival
for k in range(18): add(sparkle(0.35, 3000, 9000, 70), 0.3 + k * 0.075, -0.6 + 1.2 * k / 17, 0.05 + 0.07 * k / 17)
chime(1.65, 0.35, 0.42)
# real hand arrival (2.25): EXPECTED = soft muted tap + tiny damped ripple
add(thump(120, 0.4, 0.45, 0.2), 2.25, 0.0, 0.7); add(lp(bell(ROOT, 0.9, 0.3), 1200), 2.27, 0.0, 0.25)
pulse_tick(2.3, ROOT * 3, 0.0, 0.3)          # headline tick
add(whoosh(1.1, 300, 2400, True), 3.0, 0.0, 0.22)   # push-in rise
add(whoosh(0.5, 2500, 300, False), 3.85, 0.0, 0.2)  # dip to the palm
# PALM 1 (4.4-6.2): ghost shimmer, chime at 5.7, real touch at 6.2 (muted), macro push 6.3
for k in range(14): add(sparkle(0.3, 3000, 9000, 60), 4.45 + k * 0.07, -0.5 + 1.0 * k / 13, 0.05 + 0.06 * k / 13)
chime(5.7, 0.2, 0.4)
add(thump(110, 0.45, 0.45, 0.15), 6.2, 0.0, 0.6); add(lp(bell(ROOT, 1.2, 0.3), 1000), 6.22, 0.0, 0.22)
add(whoosh(0.9, 400, 1800, True), 6.3, 0.0, 0.18)
# BRIDGE (7.0-8.8): a travelling pulse that rises in pitch with the line head, ticks accelerating
for k in range(26):
    u = k / 25; tk = 7.05 + 1.75 * u ** 0.9; pulse_tick(tk, 330 + 520 * u, -0.7 + 1.4 * u, 0.22)
add(hp(whoosh(1.8, 500, 5000, True), 250), 7.0, 0.0, 0.18)
# BRAIN (8.8-12.0): command = slow soft thumps; prediction = fast bright ticks that arrive FIRST (10.4) with a chime; command arrives 11.2 (muted)
for k in range(10): add(thump(95, 0.22, 0.3, 0.05), 8.9 + k * 0.26, -0.35, 0.28 + 0.03 * k)
for k in range(24):
    u = k / 23; pulse_tick(9.5 + 0.9 * u ** 1.3 * 1.0, 700 + 1200 * u, 0.4, 0.14 + 0.1 * u, False)
chime(10.4, 0.35, 0.5); add(thump(105, 0.4, 0.5, 0.1), 11.2, -0.3, 0.55)
add(lp(bell(ROOT * 0.5, 1.5, 0.2), 900), 11.2, -0.3, 0.2)
pulse_tick(10.6, ROOT * 4, 0.0, 0.25)       # expected-waveform tick
# RETURN (12.0-13.4): reverse swell + teal shimmer carrying us back
sw = whoosh(1.5, 400, 2400, False); add(sw, 11.9, 0.0, 0.22)
for k in range(12): add(sparkle(0.3, 3500, 9000, 50), 12.0 + k * 0.1, 0.6 - 1.2 * k / 11, 0.05)
chime(13.3, -0.2, 0.3)
# 13.4-15.2: HELD BREATH, near silence; a barely-there tension bed rising (very quiet)
add(lp(tone(int(1.4 * SR), ROOT * 0.5, ((1, 1.0), (2, 0.3), (3, 0.2)), 0.002), 700) * np.minimum(t_of(int(1.4 * SR)) / 1.2, 1) ** 2, 13.9, 0.0, 0.13)
add(hp(whoosh(1.1, 3000, 9000, True), 2000), 14.1, 0.0, 0.06)
# 15.3: THE HIT, unexpected = dry crack + wide bright noise + pitch-drop body 90-320 Hz + sub; stereo wide; long rich tail
n = int(2.6 * SR); t = t_of(n)
crack = hp(noise(n), 2500) * np.exp(-t / 0.018) * 1.2
body_f = 320 * np.exp(-t / 0.07) + 90; body = np.sin(2 * np.pi * np.cumsum(body_f) / SR) * np.exp(-t / 0.28); body = np.tanh(2.2 * body)
sub = np.sin(2 * np.pi * 52 * t) * np.exp(-t / 0.5) * np.minimum(t / 0.01, 1) * 0.5
burst = bp(noise(n), 800, 9000) * np.exp(-t / 0.35) * 0.6
tail = bell(ROOT * 2, 2.6, 1.3) * 0.35 + bell(ROOT * 3, 2.6, 1.0) * 0.2
hit = crack + body * 0.9 + sub + burst + tail
add(hit * 1.15, 15.3, 0.0, 1.0)
add(hp(burst, 1500) * 0.6, 15.31, -0.8, 0.6); add(hp(burst, 1500) * 0.6, 15.33, 0.8, 0.6)   # width
add(whoosh(0.5, 8000, 800, False), 15.3, 0.0, 0.22)    # contours tearing
# RED BRIDGE (16.4-18.0): fast pulses, rising riser into the brain
for k in range(34):
    u = k / 33; pulse_tick(16.45 + 1.3 * u ** 0.85, 600 + 1600 * u, -0.6 + 1.2 * u, 0.2 + 0.12 * u, False)
add(whoosh(1.6, 300, 7000, True), 16.4, 0.0, 0.3)
# BRAIN FLARE (17.9): big resonant swell + low body; waveform spike at 18.55
add(thump(80, 0.9, 0.4, 0.2), 17.9, 0.0, 0.8); add(bell(ROOT, 3.0, 1.2), 17.9, 0.0, 0.34); add(bell(ROOT * 1.5, 2.6, 1.0), 17.92, 0.2, 0.2)
pulse_tick(18.45, ROOT * 3, 0.0, 0.3); add(hp(noise(int(0.3 * SR)), 2500) * np.exp(-t_of(int(0.3 * SR)) / 0.05), 18.55, 0.0, 0.25)   # spike transient
# CLOSE (20.0-23.2): pull back, quiet motif rhyming with the opening, loop-link tone rising into frame 0
add(whoosh(0.6, 3000, 300, False), 19.9, 0.0, 0.2)
add(lp(tone(int(2.8 * SR), 92, ((1, 1.0), (2, 0.4))), 400) * env(int(2.8 * SR), 0.6, 1.5), 20.3, 0.0, 0.4)
chime(20.8, 0.0, 0.3)
rise = tone(int(0.9 * SR), 196 * 2, ((1, 1.0),)) * np.minimum(t_of(int(0.9 * SR)) / 0.8, 1) ** 2; add(lp(rise, 1500), 22.3, 0.0, 0.18)
# ---- master: gentle bus compression, soft clip, normalise to about -3 dBFS peak ----
def comp(x, thr=0.35, ratio=3.0):
    y = x.copy(); a = np.abs(y); over = a > thr; y[over] = np.sign(y[over]) * (thr + (a[over] - thr) / ratio); return y
L2, R2 = np.tanh(comp(L) * 1.4), np.tanh(comp(R) * 1.4)
pk = max(np.abs(L2).max(), np.abs(R2).max()); g = 0.7 / pk
out = np.stack([L2 * g, R2 * g], 1).astype(np.float32)
wavfile.write(sys.argv[1], SR, out); print('wrote', sys.argv[1], 'peak', float(np.abs(out).max()))
