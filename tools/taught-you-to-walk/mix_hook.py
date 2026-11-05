"""Sound for the 4.6 s moving hook test. No music (Teja's rule), recorded whoosh from tools/sfxlib, small foley.
0.08/0.28 two phone taps · 0.45 snatch whoosh · 0.8 sigh (breath) · 2.40 hard cut: 0.15 s silence · 3.25 the toddler sits down hard
python3 mix_hook.py OUT.wav"""
import subprocess, sys, wave
import numpy as np

SR, DUR = 48000, 4.6
out = np.zeros((int(DUR * SR), 2), np.float32)
rng = np.random.default_rng(5)


def load(name, start, length):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', '../sfxlib/' + name, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()[int(start * SR):int((start + length) * SR)]
    n = len(x); f = min(int(0.03 * SR), n); x[-f:] *= np.linspace(1, 0, f)[:, None]; return x


def put(x, t, db=0.0):
    a = int(t * SR); x = x[:max(0, len(out) - a)]; out[a:a + len(x)] += x * 10 ** (db / 20)


def mono(s): return np.repeat(s[:, None], 2, 1).astype(np.float32)


def lp(x, k):  # one-pole low-pass
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += k * (v - acc); y[i] = acc
    return y


def tap(db):
    n = int(0.04 * SR); t = np.arange(n) / SR
    return mono((np.sin(2 * np.pi * 1800 * t) * 0.5 + rng.normal(0, 0.5, n)) * np.exp(-t / 0.006)) * 10 ** (db / 20)


def breath(dur, db):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return mono(lp(rng.normal(0, 1, n), 0.08) * env) * 10 ** (db / 20)


def thud(db):
    n = int(0.25 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (90 - 40 * t / 0.25) * t) * np.exp(-t / 0.05) + lp(rng.normal(0, 1, n), 0.2) * np.exp(-t / 0.02) * 0.5
    return mono(s) * 10 ** (db / 20)


# faint warm room so the cut to silence reads
room = mono(lp(rng.normal(0, 1, len(out)), 0.01)) * 10 ** (-38 / 20)
room[int(2.40 * SR):int(2.55 * SR)] = 0
out += room
put(tap(-14), 0.08); put(tap(-15), 0.28)
put(load('649445__audiopapkin__cinematic-woosh-sfx-015.wav', 2.25, 0.55), 0.45 - 0.25, -4)
put(breath(0.9, -10), 0.78)
put(thud(-6), 3.25)
out[int(2.40 * SR):int(2.55 * SR)] *= 0.0
out *= 0.89 / np.abs(out).max()
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'hook.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype('<i2').tobytes())
print('ok')
