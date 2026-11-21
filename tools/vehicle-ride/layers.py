# Adds engine, siren and rotor layers to the by-the-numbers SFX mix. usage: python3 layers.py base.wav out.wav
import sys, wave, numpy as np
w = wave.open(sys.argv[1]); SR = w.getframerate(); a = np.frombuffer(w.readframes(w.getnframes()), np.int16).reshape(-1, 2) / 32767.0
n = len(a); t = np.arange(n) / SR
# speed curve in km/h per scene (matches index.html)
K = [(0, 2, 0, 90), (2, 5.2, 90, 160), (5.2, 9, 160, 210), (9, 12.4, 210, 240), (12.4, 15.4, 240, 260), (15.4, 18.6, 260, 320)]
kmh = np.zeros(n)
for a0, a1, k0, k1 in K:
    m = (t >= a0) & (t < a1); kmh[m] = k0 + (k1 - k0) * (t[m] - a0) / (a1 - a0)
road = t < 18.6
f = 55 + kmh * 0.55; ph = 2 * np.pi * np.cumsum(f) / SR
eng = (np.sin(ph) + 0.5 * np.sign(np.sin(ph * 2)) * 0.3) * 0.05 * road
eng = np.convolve(eng, np.ones(30) / 30, 'same')
# two-tone police siren, soft, fades in
sf = np.where((t * 1.6) % 1 < 0.5, 760, 960); sph = 2 * np.pi * np.cumsum(sf) / SR
sir = np.sin(sph) * 0.035 * road * np.minimum(1, t / 1.0) * (0.6 + 0.4 * np.sin(t * 0.7) ** 2)
# rotor chop in heli scenes
rot = (np.sin(2 * np.pi * 70 * t) * np.maximum(0, np.sin(2 * np.pi * 11 * t)) ** 6) * 0.12 * (t >= 18.6) * np.clip((25.2 - t) / 1.0, 0, 1)
mix = a + np.stack([eng + sir * 0.8 + rot, eng + sir + rot], 1)
mix *= 0.89 / np.abs(mix).max()
o = wave.open(sys.argv[2], 'wb'); o.setnchannels(2); o.setsampwidth(2); o.setframerate(SR); o.writeframes((mix * 32767).astype(np.int16).tobytes()); o.close()
