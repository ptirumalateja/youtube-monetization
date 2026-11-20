"""Action-synced SFX bed for the Born Rich climb reel (no music: Teja adds a trending song).
Usage: python3 sfx.py out.wav   Times mirror the timeline constants in scene.html."""
import subprocess, sys
import numpy as np

SR = 48000; DUR = 16.6
AT_P, AT_C = 0.6, 14; P_FIRST, P_P = 2.5, 0.8
BLAST = 9.6; AT_FALL = (9.78, 10.62); PF_FALL = (9.95, 10.8)
GLINT, SHUT, GRAB, CTA = 12.55, 13.25, 14.85, 13.55
out = np.zeros((int(SR * (DUR + 0.3)), 2), np.float32)


def load(n):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'sfx/{n}.mp3', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
    pk = np.abs(x).max() or 1
    return x / pk


S = {n: load(n) for n in ['hammer1', 'hammer2', 'hammer3', 'hammer4', 'step1', 'step2', 'plank_grab', 'rung', 'rope', 'level_ding',
                          'heli_far', 'heli_land', 'wood_snap', 'tumble', 'thud', 'planks_rain', 'dizzy', 'door_slam', 'glint']}


def put(n, t, g=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, length=None):
    x = S[n].copy()
    if length: x = x[:int(length * SR)]
    if fade_in: k = min(len(x), int(fade_in * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fade_out: k = min(len(x), int(fade_out * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x[:, 0] *= 1 - max(pan, 0); x[:, 1] *= 1 + min(pan, 0)
    i = int(t * SR); j = min(len(out), i + len(x))
    if j > i: out[i:j] += x[:j - i] * g


H = ['hammer1', 'hammer2', 'hammer3', 'hammer4']
# perfectionist: obsessive taps on the first box, the level, then plank / tap tap / step
put('hammer1', 0.02, 0.9, -0.3)
for k in range(1, 6): put(H[k % 4], k / 4.2, 0.75, -0.3)
put('level_ding', 1.9, 0.45, -0.3)
put('step1', 2.3, 0.35, -0.3)
k = 0
while P_FIRST + k * P_P < PF_FALL[0]:
    t0 = P_FIRST + k * P_P
    put('rung', t0 + 0.24, 0.5, -0.35)
    for d in (0.40, 0.56):
        if t0 + d < PF_FALL[0]: put(H[(k + int(d * 10)) % 4], t0 + d, 0.55, -0.35)
    if t0 + 0.69 < PF_FALL[0]: put('step2', t0 + 0.69, 0.3, -0.35)
    k += 1
# action taker: rung slap + rope + two steps per cycle, slightly louder as he gets higher (the race heats up)
for c in range(AT_C):
    t0 = c * AT_P; g = 0.55 + 0.25 * c / AT_C
    put('rung', t0 + 0.2, g, 0.35)
    put('rope', t0 + 0.25, 0.35 * g, 0.35, length=0.35)
    put('step1', t0 + AT_P * 0.68, 0.3, 0.3); put('step2', t0 + AT_P * 0.92, 0.3, 0.3)
put('step1', 8.6, 0.35, 0.3)
# the helicopter: far, then on top of us
put('heli_far', 5.6, 0.55, 0.4, fade_in=2.0)
put('heli_land', BLAST - 0.75, 1.0, 0.15, fade_in=0.5, fade_out=1.8)
put('wood_snap', AT_FALL[0] - 0.02, 1.0, 0.25)
put('tumble', AT_FALL[0] + 0.05, 0.6, 0.3); put('tumble', PF_FALL[0], 0.55, -0.3)
put('planks_rain', 10.15, 0.6, 0.2)
put('thud', AT_FALL[1], 0.95, 0.35); put('thud', PF_FALL[1], 0.9, -0.35)
put('dizzy', 10.95, 0.28, 0.0, fade_out=0.6)
put('glint', GLINT, 0.5, 0.0)
put('door_slam', SHUT - 0.03, 1.0, 0.0)
put('dizzy', 13.6, 0.18, 0.0, fade_in=0.3, fade_out=0.8, length=1.6)
put('plank_grab', GRAB, 0.7, 0.3)
out = out[:int(SR * DUR)]
out /= max(1e-6, np.abs(out).max()) / 0.8
out.astype('<f4').tofile('/tmp/_bed.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '/tmp/_bed.f32',
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', str(SR), sys.argv[1]], check=True)
