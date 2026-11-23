#!/usr/bin/env python3
"""Sound for the 'revenge is a waste of time' door reel (10 s): muffled crowd shouting, door slam, silence, creak, birds + warm pad, footsteps. All synthesized.
usage: audio_door.py OUT.wav"""
import sys, subprocess, wave
import numpy as np
SR = 44100; DUR = 10.0; N = int(SR * DUR); t = np.arange(N) / SR
rng = np.random.RandomState(7); out = np.zeros(N, np.float32)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N or i0 < 0: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
def bp(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x)).astype(np.float32)
# crowd: formant-filtered noise, syllable-modulated, 5 voices, cut when the door slams
crowd = np.zeros(N, np.float32)
for v in range(6):
    f0 = rng.uniform(95, 190); syl = rng.uniform(3.2, 6.0)
    src = np.sign(np.sin(2 * np.pi * f0 * t + 3 * np.sin(2 * np.pi * rng.uniform(4, 7) * t))) * 0.5 + rng.randn(N) * 0.25
    vo = bp(src.astype(np.float32), 300, 1900) + 0.6 * bp(src.astype(np.float32), 800, 1500)
    am = np.clip(np.sin(2 * np.pi * syl * t + rng.uniform(0, 6)) + 0.4, 0, 1) ** 1.5
    crowd += vo * am * rng.uniform(0.5, 1.0)
crowd /= np.abs(crowd).max() + 1e-6
env = np.interp(t, [0, 0.25, 3.6, 4.2, 4.3, 4.5, 4.9], [0.0, 0.9, 1.0, 1.0, 0.25, 0.08, 0.0])
cm = crowd * env; cm_muf = bp(crowd, 80, 500) * np.interp(t, [4.2, 4.3, 4.6, 5.2], [0, 0.55, 0.25, 0])
out += (cm * 0.55 + cm_muf * 0.5).astype(np.float32)
# storm bed + thunder-like rumble before the slam
rum = bp(rng.randn(N).astype(np.float32), 30, 140) * np.interp(t, [0, 3, 4.2, 4.4, 5.0], [0.5, 0.9, 1.0, 0.2, 0.0])
out += rum * 0.9
# door slam at 4.25: sub thud + wood crack + room reverb tail
L = int(1.6 * SR); tt = np.arange(L) / SR
thud = np.sin(2 * np.pi * (88 * np.exp(-tt * 3.2)) * tt) * np.exp(-tt / 0.3) * 1.2
crack = bp(rng.randn(L).astype(np.float32), 300, 4000) * np.exp(-tt / 0.045) * 0.9
tail = bp(rng.randn(L).astype(np.float32), 80, 900) * np.exp(-tt / 0.5) * 0.25
add(np.tanh((thud + crack + tail) * 1.4).astype(np.float32), 4.22, 1.0)
# calm: soft room tone + one slow breath at ~4.9
room = bp(rng.randn(N).astype(np.float32), 60, 400) * np.interp(t, [4.3, 5.0, 6.4, 6.6], [0, 0.10, 0.10, 0.0]); out += room
L = int(1.0 * SR); tt = np.arange(L) / SR
add((bp(rng.randn(L).astype(np.float32), 400, 2600) * np.sin(np.pi * tt) ** 2 * 0.22), 4.75)
# door creak (6.5-7.4): swept sawtooth + tremolo
L = int(1.0 * SR); tt = np.arange(L) / SR; fr = 150 + 120 * tt + 25 * np.sin(2 * np.pi * 9 * tt)
creak = np.sign(np.sin(2 * np.pi * np.cumsum(fr) / SR)) * 0.5; creak = bp(creak.astype(np.float32), 250, 2200) * (0.6 + 0.4 * np.sin(2 * np.pi * 14 * tt)) * np.sin(np.pi * tt / 1.0) ** 0.7
add(creak.astype(np.float32), 6.5, 0.5)
# warm pad (Cmaj add9) swelling from the door opening + birds
pad = np.zeros(N, np.float32)
for f, a in ((130.8, 1.0), (196.0, 0.7), (261.6, 0.6), (329.6, 0.45), (392.0, 0.35), (587.3, 0.2)):
    pad += a * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * (1 + 0.15 * np.sin(2 * np.pi * rng.uniform(0.2, 0.5) * t))
out += pad * 0.05 * np.interp(t, [6.4, 7.6, 9.3, 10.0], [0, 0.7, 1.0, 0.0])
for tb in (7.05, 7.5, 8.1, 8.6, 9.1):
    L = int(0.25 * SR); tt = np.arange(L) / SR; f = 3300 + 900 * np.sin(2 * np.pi * 14 * tt) + rng.uniform(-300, 300)
    add((np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / 0.25) ** 2 * 0.05).astype(np.float32), tb, 1.0)
wind = bp(rng.randn(N).astype(np.float32), 200, 1400) * np.interp(t, [6.4, 7.4, 9.5, 10], [0, 0.06, 0.05, 0]); out += wind
# footsteps 7.4-9.7 (soft), slowing to nothing as he shrinks
for k in range(10):
    ts = 7.5 + k * 0.263; a = max(0.0, 1.0 - k / 11.0)
    L = int(0.18 * SR); tt = np.arange(L) / SR
    add(((np.sin(2 * np.pi * 70 * tt) * np.exp(-tt / 0.05) + bp(rng.randn(L).astype(np.float32), 500, 2500) * np.exp(-tt / 0.02) * 0.3)).astype(np.float32), ts, 0.45 * a)
# heartbeat-ish tension under the shouting
tb = 0.4
while tb < 4.1:
    for off, a in ((0, 1.0), (0.23, 0.6)):
        L = int(0.3 * SR); tt = np.arange(L) / SR; add((np.sin(2 * np.pi * (64 - 20 * tt / 0.3) * tt) * np.exp(-tt / 0.075) * a).astype(np.float32), tb + off, 0.25 + 0.15 * tb / 4)
    tb += 0.95 - 0.1 * tb / 4
out = np.tanh(out * 1.1) * 0.9
tmp = "/tmp/door_raw.wav"
with wave.open(tmp, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.2:LRA=9,aformat=channel_layouts=stereo", "-ar", "44100", sys.argv[1]], check=True)
print("wrote", sys.argv[1])
