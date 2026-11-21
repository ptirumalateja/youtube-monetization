"""Action-synced SFX bed for the Respect This Woman replica (no music: a trending song goes on top).
Usage: python3 sfx.py out.wav   (reads events.json exported from scene.html EVENTS)"""
import json, subprocess, sys
import numpy as np

SR = 48000; DUR = 27.6
out = np.zeros((int(SR * (DUR + 0.5)), 2), np.float32)
rs = np.random.default_rng(3)


def load(n):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'sfx/{n}.mp3', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
    return x / (np.abs(x).max() or 1)


S = {n: load(n) for n in ['hammer1', 'hammer2', 'hammer3', 'hammer4', 'thud', 'glint', 'step1', 'step2', 'tumble']}


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(t / max(a, 1e-4), 1) * np.exp(-t / d)


def lp(x, k):  # crude one-pole low-pass, k in (0,1]
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)): acc += k * (x[i] - acc); y[i] = acc
    return y


def synth(kind):
    if kind == 'rumble':  # boulder rolling in
        n = int(0.9 * SR); x = lp(rs.standard_normal(n).astype(np.float32), 0.02) * 6
        x *= np.sin(np.linspace(0, np.pi, n)) ** 0.7
        return np.stack([x, x], 1)
    if kind == 'boom':  # heavy slam
        n = int(1.1 * SR); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * (55 - 20 * t) * t) * env(n, 0.003, 0.28) + lp(rs.standard_normal(n), 0.05) * env(n, 0.002, 0.12) * 2
        return np.stack([x, x], 1).astype(np.float32)
    if kind == 'shatter':
        n = int(1.4 * SR); x = np.zeros(n, np.float32)
        for k in range(40):
            i = int(rs.uniform(0, 0.5) ** 1.6 * SR); m = int(0.12 * SR)
            if i + m > n: continue
            g = rs.standard_normal(m) * env(m, 0.001, rs.uniform(0.01, 0.05)) * rs.uniform(0.3, 1)
            x[i:i + m] += g
        t = np.arange(n) / SR
        x += np.sin(2 * np.pi * 48 * t) * env(n, 0.002, 0.35) * 1.2
        return np.stack([x, x * 0.9], 1).astype(np.float32)
    if kind == 'pop':  # heart pop
        n = int(0.25 * SR); t = np.arange(n) / SR
        x = np.sin(2 * np.pi * (520 + 900 * np.exp(-t * 40)) * t) * env(n, 0.002, 0.05)
        return np.stack([x, x], 1).astype(np.float32)
    if kind == 'whoosh':
        n = int(0.45 * SR); x = rs.standard_normal(n).astype(np.float32)
        x = lp(x, 0.15) * np.sin(np.linspace(0, np.pi, n)) ** 2 * 2.5
        return np.stack([x, x], 1)
    if kind == 'chime':  # warm resolve after the shatter
        n = int(2.6 * SR); t = np.arange(n) / SR; x = np.zeros(n)
        for f, g in [(523.25, 1), (659.25, 0.7), (783.99, 0.6), (1046.5, 0.35)]:
            x += g * np.sin(2 * np.pi * f * t) * env(n, 0.01, 1.1)
        return np.stack([x, x], 1).astype(np.float32) * 0.5


for k in ['rumble', 'boom', 'shatter', 'pop', 'whoosh', 'chime']:
    s = synth(k); S[k] = s / (np.abs(s).max() or 1)


def put(n, t, g=1.0, pan=0.0):
    x = S[n].copy(); x[:, 0] *= 1 - max(pan, 0); x[:, 1] *= 1 + min(pan, 0)
    i = int(t * SR); j = min(len(out), i + len(x))
    if j > i: out[i:j] += x[:j - i] * g


H = ['hammer1', 'hammer2', 'hammer3', 'hammer4']
for k, (_, t) in enumerate(json.load(open('events.json'))):
    put(H[k % 4], t - 0.01, 0.45 + 0.1 * (t > 11), 0.15)
put('glint', 0.25, 0.25, 0.2)
put('whoosh', 1.95, 0.4); put('thud', 2.3, 0.35, 0.15)                 # jump into the pit
put('rumble', 2.6, 0.55, -0.4); put('boom', 2.98, 0.6, -0.4)            # Family boulder
put('step1', 2.7, 0.2, -0.2); put('step2', 2.85, 0.2, -0.2)
put('step1', 6.95, 0.18, 0.4); put('step2', 7.15, 0.18, 0.4)            # rich man
put('rumble', 7.95, 0.7, -0.5); put('boom', 8.23, 0.95, -0.5)          # Trust slams in
put('glint', 12.8, 0.6, 0.1); put('glint', 13.1, 0.35, 0.1)            # diamond found
put('step1', 13.9, 0.18, 0.4); put('step2', 14.1, 0.18, 0.4)           # other woman
put('whoosh', 14.55, 0.25, 0.3); put('pop', 15.0, 0.35, 0.2)           # heart caught
put('whoosh', 17.75, 0.3, 0.3); put('thud', 18.55, 0.15, 0.3)          # heart thrown back
put('whoosh', 20.45, 0.45, -0.1); put('thud', 21.0, 0.35, -0.2)        # climbs out
put('glint', 21.7, 0.4, -0.2)                                          # gives the diamond
put('shatter', 24.25, 1.0, -0.3); put('boom', 24.25, 0.6, -0.3)
put('chime', 25.2, 0.35)

pk = np.abs(out).max(); out *= 0.89 / pk
p = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', sys.argv[1]], input=out.astype(np.float32).tobytes())
