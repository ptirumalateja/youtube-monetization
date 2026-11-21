"""Action-synced SFX bed for They Laughed v4 (ref timing, stream ending; no music: Teja adds a trending song).
Usage: node render.js events events.json && python3 sfx.py out.wav events.json   Times mirror scene.html."""
import json, subprocess, sys
import numpy as np

SR = 48000; DUR = 16.0
EDGE_T = 7.6; PULL = (8.0, 8.6); STAND = (9.0, 9.6)
CLAP_T = 10.4; PEE_T0 = 12.85; PEE_HIT = 13.15; END_T = 13.6
out = np.zeros((int(SR * (DUR + 0.5)), 2), np.float32)


def load(n):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'sfx/{n}.mp3', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
    return x / (np.abs(x).max() or 1)


S = {n: load(n) for n in ['laugh', 'laugh2', 'grip', 'pebbles', 'gasp', 'wind', 'applause', 'thud', 'step1', 'step2', 'stream', 'eww']}


def put(n, t, g=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, length=None, start=0.0):
    x = S[n][int(start * SR):].copy()
    if length: x = x[:int(length * SR)]
    if fade_in: k = min(len(x), int(fade_in * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fade_out: k = min(len(x), int(fade_out * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x[:, 0] *= 1 - max(pan, 0); x[:, 1] *= 1 + min(pan, 0)
    i = int(t * SR); j = min(len(out), i + len(x))
    if j > i: out[i:j] += x[:j - i] * g


for t0 in (0.0, 5.6, 11.2):
    put('wind', t0, 0.12, 0.0, fade_in=0.6, fade_out=0.6)
# the crowd laughs from frame 0 (louder on the 2.2 s crowd shot), fades under the climb
put('laugh2', 0.0, 0.8, -0.3, fade_out=0.3)
put('laugh', 2.2, 1.0, -0.1, fade_out=0.5)
put('laugh2', 5.0, 0.35, -0.4, fade_in=0.3, fade_out=0.8)
put('laugh', 7.4, 0.25, -0.5, length=1.8, fade_in=0.3, fade_out=0.8)
# grips + grit on every hand/foot landing (from the scene)
for e in json.load(open(sys.argv[2] if len(sys.argv) > 2 else 'events.json')):
    put('grip', e['t'] - 0.02, 0.5 if e['foot'] else 0.4, 0.2)
    if e['foot']: put('pebbles', e['t'], 0.18, 0.2, length=0.45, fade_out=0.25)
# over the lip and stand
put('grip', EDGE_T, 0.7, 0.2); put('grip', PULL[0] + 0.05, 0.7, 0.2)
put('step1', PULL[1], 0.5, 0.2); put('step2', STAND[0] + 0.1, 0.45, 0.2)
# the crowd goes quiet, then claps
put('gasp', 9.7, 0.4, -0.4)
put('applause', CLAP_T, 0.75, -0.4, fade_in=0.15)
put('applause', 12.2, 0.8, -0.1, length=1.0, fade_out=0.4)
# the stream
put('stream', PEE_T0, 0.85, 0.1, fade_in=0.15, fade_out=0.5)
put('gasp', PEE_HIT, 0.7, -0.1)
put('eww', PEE_HIT + 0.2, 1.0, -0.2)
put('eww', 15.0, 0.4, -0.4, start=0.4, fade_out=0.5)
put('thud', END_T, 0.45); put('thud', END_T + 0.45, 0.55)
out = out[:int(SR * DUR)]
out /= max(1e-6, np.abs(out).max()) / 0.8
out.astype('<f4').tofile('/tmp/_bed.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '/tmp/_bed.f32',
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', str(SR), sys.argv[1]], check=True)
