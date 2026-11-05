"""Sound for the 5 s hook test. No music bed (Teja's rule): recorded impacts from tools/sfxlib, silence as a beat.
0.00  hit on frame 0 (riser-hit tail) + heartbeat-like suspense pulse under the scroll
0.35/1.05/1.70  tiny thumb flicks on the phone
1.0-2.40  riser builds, hard cut to silence when the ghost's hand reaches his shoulder
2.55-3.05  whoosh on the whip turn, biggest hit (riser-hit + braaam) as he faces them at 3.05
3.5+  soft paper ticks as the tags pop
python3 mix_hook.py OUT.wav
"""
import subprocess, sys
import numpy as np

SR = 48000
LIB = '../sfxlib/'
DUR = 5.0


def load(name, start=0.0, length=None):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', LIB + name, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
    a = int(start * SR)
    b = len(x) if length is None else a + int(length * SR)
    return x[a:b]


def fade(x, fi=0.005, fo=0.02):
    n = len(x); i = min(int(fi * SR), n); o = min(int(fo * SR), n)
    x[:i] *= np.linspace(0, 1, i)[:, None]
    if o: x[n - o:] *= np.linspace(1, 0, o)[:, None]
    return x


out = np.zeros((int(DUR * SR), 2), np.float32)


def put(x, t, gain_db=0.0):
    a = int(t * SR); x = x[:max(0, len(out) - a)]
    out[a:a + len(x)] += x * (10 ** (gain_db / 20))


RISERHIT = '822420__audiopapkin__riser-hit-sfx-120.wav'   # hit at 6.15 s
BRAAAM = '722633__chakong__cinematic-braaam.wav'         # peak ~1.1 s
PULSE = '869757__mikiko850__dark-suspense-accent.wav'    # pulses every ~1 s
WOOSH = '649445__audiopapkin__cinematic-woosh-sfx-015.wav'  # peak 2.5 s

# frame-0 impact
put(fade(load(RISERHIT, 6.10, 1.6), 0.002, 0.6), 0.0, -2)
# suspense pulse under the scroll, dies at the silence
put(fade(load(PULSE, 0.5, 1.9), 0.05, 0.08), 0.45, -9)
# riser (the build part of the riser-hit file), cut hard at 2.40
put(fade(load(RISERHIT, 6.10 - 1.4 - 1.6, 1.4), 0.3, 0.012), 1.0, 2)
# whoosh centred on the whip turn (peak at 2.85)
put(fade(load(WOOSH, 1.75, 1.5), 0.01, 0.4), 2.85 - 0.75, -1)
# biggest hit as he faces them
put(fade(load(RISERHIT, 6.12, 1.9), 0.002, 0.5), 3.05, 0)
put(fade(load(BRAAAM, 0.35, 1.9), 0.004, 0.6), 3.05 - 0.05, -4)

# thumb flicks + tag ticks (tiny, filtered noise; quiet)
rng = np.random.default_rng(3)
def tick(f0, dur, db):
    n = int(dur * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f0 * t) * 0.6 + rng.normal(0, 0.4, n)) * np.exp(-t / (dur / 5))
    return np.repeat(s[:, None], 2, 1).astype(np.float32) * (10 ** (db / 20))
for tt in (0.35, 1.05, 1.70):
    put(tick(2400, 0.05, -28), tt)
for i, tt in enumerate((3.5, 3.85, 4.2, 4.55)):
    put(tick(700 + 90 * i, 0.09, -16), tt)

# silence beat: nothing between 2.40 and 2.55 except the decaying tails
peak = np.abs(out).max()
out *= 0.89 / peak
import wave
pcm = (np.clip(out, -1, 1) * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'hook.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('peak-normalised mix written')
