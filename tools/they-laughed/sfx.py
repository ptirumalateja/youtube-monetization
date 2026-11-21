"""Action-synced SFX bed for the They Laughed reel (no music: Teja adds a trending song).
Usage: python3 sfx.py out.wav   Times mirror the timeline constants in scene.html."""
import json, subprocess, sys
import numpy as np

SR = 48000; DUR = 17.5
FF = 0.8; SLIP = 5.75; EDGE_T = 7.7; PULL = (8.05, 8.65); STAND = (8.75, 9.25)
CLAP_T = 10.15; WALK = (11.95, 12.25); LIFT = (12.3, 12.85); THROW = (12.95, 13.15); LOOKUP_T = 13.35; IMPACT = 14.0
NOW_T = 9.9; END_T = 15.0
out = np.zeros((int(SR * (DUR + 0.5)), 2), np.float32)


def load(n):
    x = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', f'sfx/{n}.mp3', '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'],
                                     capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
    return x / (np.abs(x).max() or 1)


S = {n: load(n) for n in ['laugh', 'laugh2', 'grip', 'pebbles', 'gasp', 'wind', 'applause', 'lift', 'whoosh', 'smash', 'groan',
                          'dust', 'dizzy', 'thud', 'tumble', 'step1', 'step2']}


def put(n, t, g=1.0, pan=0.0, fade_in=0.0, fade_out=0.0, length=None, start=0.0):
    x = S[n][int(start * SR):].copy()
    if length: x = x[:int(length * SR)]
    if fade_in: k = min(len(x), int(fade_in * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fade_out: k = min(len(x), int(fade_out * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
    x[:, 0] *= 1 - max(pan, 0); x[:, 1] *= 1 + min(pan, 0)
    i = int(t * SR); j = min(len(out), i + len(x))
    if j > i: out[i:j] += x[:j - i] * g


# summit wind under everything
for t0 in (0.0, 5.6, 11.2):
    put('wind', t0, 0.12, 0.0, fade_in=0.6, fade_out=0.6)
# hook: the crowd close-up is already laughing on frame 0
put('laugh2', 0.0, 0.95, -0.1, fade_out=0.3)
put('laugh', 1.6, 0.5, -0.4, fade_out=0.8)
# every hand/foot landing on a hold (events exported by `node render.js events events.json`): grip scrape + grit
for e in json.load(open(sys.argv[2] if len(sys.argv) > 2 else 'events.json')):
    if e.get('big') or e['t'] < 2.0: continue
    put('grip', e['t'] - 0.02, 0.5 if e['foot'] else 0.4, 0.2)
    if e['foot']: put('pebbles', e['t'], 0.18, 0.2, length=0.45, fade_out=0.25)
# slip rehook: pebbles, a gasp from him, the crowd laughs harder
put('pebbles', SLIP, 0.9, 0.2); put('thud', SLIP + 0.1, 0.35, 0.2)
put('laugh2', SLIP + 0.2, 0.9, -0.2, start=0.3, length=1.0, fade_out=0.4)
# summit: grab the edge, pull up, stand
put('grip', EDGE_T, 0.7, 0.2); put('grip', PULL[0] + 0.05, 0.7, 0.2)
put('step1', PULL[1], 0.5, 0.2); put('step2', STAND[0] + 0.1, 0.45, 0.2)
# crowd goes quiet, then claps
put('gasp', 9.55, 0.4, -0.4)
put('applause', CLAP_T, 0.7, -0.4, fade_in=0.15)
put('applause', 11.0, 0.8, -0.1, length=1.5, fade_out=0.6)
# the boulder
put('step1', WALK[0] + 0.05, 0.4, 0.3); put('step2', WALK[0] + 0.2, 0.4, 0.3)
put('lift', LIFT[0], 0.9, 0.25)
put('whoosh', THROW[1] - 0.05, 0.9, 0.0)
put('gasp', LOOKUP_T, 0.8, -0.1)
put('smash', IMPACT - 0.02, 1.0, 0.0); put('thud', IMPACT, 0.9, 0.0)
put('tumble', IMPACT + 0.05, 0.35, 0.0)
put('groan', IMPACT + 0.45, 0.6, -0.1)
put('dizzy', IMPACT + 0.7, 0.3, 0.0, fade_out=0.6)
# end: hero dusts his hands, question lands
put('dust', 14.9, 0.55, 0.3); put('dust', 15.4, 0.45, 0.3, length=0.5)
put('thud', END_T, 0.45); put('thud', END_T + 0.45, 0.55)
put('dizzy', 15.9, 0.16, 0.0, fade_in=0.3, fade_out=0.8)
out = out[:int(SR * DUR)]
out /= max(1e-6, np.abs(out).max()) / 0.8
out.astype('<f4').tofile('/tmp/_bed.f32')
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '/tmp/_bed.f32',
                '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ar', str(SR), sys.argv[1]], check=True)
