"""Action-synced SFX bed for the Born Rich climb reel (no music: Teja adds a trending song).
Usage: python3 sfx.py out.wav   Times mirror the timeline constants in scene.html."""
import subprocess, sys
import numpy as np

SR = 48000; DUR = 15.2
AT_C, AT_T0 = 17, 1.55; AT_P = (8.45 - AT_T0) / (AT_C - 1); AT_TOP = 9.2
P_FIRST, P_P = 3.3, 0.6; PF_HIT, PF_LAND = 10.15, 11.55
BREAK = 10.12; AT_FALL = (10.12, 10.8); HELI_IN = 7.75; STARS_T = 11.85; RICH = (11.95, 12.9)
out = np.zeros((int(SR * (DUR + 0.3)), 2), np.float32)


def load(n):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'sfx/{n}.mp3', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
    pk = np.abs(x).max() or 1
    return x / pk


S = {n: load(n) for n in ['hammer1', 'hammer2', 'hammer3', 'hammer4', 'step1', 'step2', 'plank_grab', 'rung', 'rope', 'level_ding',
                          'heli_far', 'heli_land', 'wood_snap', 'tumble', 'thud', 'planks_rain', 'dizzy']}


def put(n, t, g=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, length=None):
    x = S[n].copy()
    if length: x = x[:int(length * SR)]
    if fade_in: k = min(len(x), int(fade_in * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fade_out: k = min(len(x), int(fade_out * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x[:, 0] *= 1 - max(pan, 0); x[:, 1] *= 1 + min(pan, 0)
    i = int(t * SR); j = min(len(out), i + len(x))
    if j > i: out[i:j] += x[:j - i] * g


H = ['hammer1', 'hammer2', 'hammer3', 'hammer4']
# perfectionist: rapid taps on the first crate (t*3.4 cadence), carries it, then place / tap tap / step every P_P
k = 0
while (k + 1) / 3.4 < 2.45:
    put(H[k % 4], (k + 1) / 3.4 - 0.01, 0.75, -0.35); k += 1
put('step1', 2.75, 0.3, -0.35); put('step2', 3.0, 0.3, -0.35)
k = 0
while P_FIRST + k * P_P < PF_HIT:
    t0 = P_FIRST + k * P_P
    put('rung', t0 + 0.25 * P_P - 0.02, 0.5, -0.35)
    for d in (0.5, 0.75):
        if t0 + d * P_P < PF_HIT: put(H[(k * 2 + int(d * 4)) % 4], t0 + d * P_P - 0.01, 0.55, -0.35)
    if t0 + 0.95 * P_P < PF_HIT: put('step2', t0 + 0.95 * P_P, 0.28, -0.35)
    k += 1
# action taker: first rung tied before the climb, then rung slap + rope bind + two steps per cycle, rising
put('rung', 0.85, 0.6, 0.35); put('rope', 1.0, 0.3, 0.35, length=0.35)
for c in range(1, AT_C):
    t0 = AT_T0 + (c - 1) * AT_P; g = 0.55 + 0.3 * c / AT_C
    put('rung', t0 + 0.38 * AT_P - 0.02, g, 0.35)
    put('rope', t0 + 0.42 * AT_P, 0.3 * g, 0.35, length=0.3)
    put('step1', t0 + 0.72 * AT_P, 0.28, 0.3); put('step2', t0 + 0.95 * AT_P, 0.28, 0.3)
for k, t in enumerate((8.65, 8.85, 9.05)): put(('step1', 'step2')[k % 2], t, 0.32, 0.3)
# the helicopter: far, then on top of us
put('heli_far', HELI_IN, 0.6, 0.4, fade_in=1.2)
put('heli_land', 9.35, 1.0, 0.15, fade_in=0.5, fade_out=2.0)
put('wood_snap', BREAK - 0.02, 1.0, 0.25)
put('tumble', AT_FALL[0] + 0.05, 0.6, 0.3); put('tumble', PF_HIT + 0.1, 0.55, -0.3)
put('planks_rain', 10.35, 0.6, 0.2)
put('thud', AT_FALL[1], 0.95, 0.35); put('thud', PF_LAND, 0.9, -0.35)
put('dizzy', STARS_T, 0.3, 0.0, fade_out=0.8)
for k in range(3): put(('step1', 'step2')[k % 2], RICH[0] + 0.1 + k * 0.39, 0.4, 0.15)
put('dizzy', 13.4, 0.16, 0.0, fade_in=0.3, fade_out=0.8, length=1.6)
out = out[:int(SR * DUR)]
out /= max(1e-6, np.abs(out).max()) / 0.8
out.astype('<f4').tofile('/tmp/_bed.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '/tmp/_bed.f32',
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', str(SR), sys.argv[1]], check=True)
