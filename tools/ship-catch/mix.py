#!/usr/bin/env python3
"""Sound for the ship-catch reel. python3 mix.py out.wav
Rocket roar = shaped noise + crackle following the render's plume timeline;
explosions from sfxlib (qubodup, CC0), modal metal clank at the catches,
reversed warp for the rewind. No music bed (Teja's rule)."""
import sys, os, subprocess, math
import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import render as R
SFX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sfx")

SR = 48000
LIB = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sfxlib')
N = int(R.END * SR) + SR // 2
rng = np.random.default_rng(3)

def load(name):
    a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(LIB, name), '-ac', '1', '-ar', str(SR),
                                      '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).copy()
    return a / (np.abs(a).max() + 1e-9)

def loadel(name):
    a = np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(SFX, name + '.mp3'), '-ac', '1', '-ar', str(SR),
                                      '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).copy()
    return a / (np.abs(a).max() + 1e-9)

def lp(x, f, o=4): return sosfilt(butter(o, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, o=2): return sosfilt(butter(o, f, 'high', fs=SR, output='sos'), x)
def bp(x, a, b, o=2): return sosfilt(butter(o, [a, b], 'band', fs=SR, output='sos'), x)

def place(buf, snd, t, g=1.0):
    i = int(t * SR)
    if i >= len(buf): return
    n = min(len(snd), len(buf) - i)
    buf[i:i + n] += snd[:n] * g

# ---- plume envelope per sample (from the render timeline)
fps_env = 200
tt = np.arange(0, R.END, 1 / fps_env)
env = np.zeros_like(tt)
for i, t in enumerate(tt):
    seg = R.segment_at(t)
    k = seg[0]
    if k in ('open',):
        env[i] = R.scene_pose(t)['plume']
    elif k == 'rewind':
        env[i] = 0.0
    elif k == 'finale':
        env[i] = R.finale_pose(t)['plume']
    else:
        fate, fl, s, d = seg
        if fate in ('stack', 'ascent', 'splash', 'blur'):
            env[i] = 0.38 if t < s + R.fail_time(fate, d) else 0.0
envS = np.interp(np.arange(N) / SR, tt, env, right=0)
# smooth attack/release
envS = lp(envS, 12, 2)
envS = np.clip(envS, 0, 1.2)
envS[:int(0.3 * SR)] = np.maximum(envS[:int(0.3 * SR)], 1.0)   # engines already burning on frame 0

# ---- roar: brown rumble + mid hiss + crackle impulses
white = rng.standard_normal(N).astype(np.float32)
brown = np.cumsum(white); brown = hp(brown, 18); brown /= np.abs(brown).max()
rumble = lp(brown, 180) * 1.6
mid = bp(white, 250, 1600) * 0.35
crk = np.zeros(N, np.float32)
idx = np.cumsum(rng.exponential(SR / 70, int(R.END * 90))).astype(int)
idx = idx[idx < N - 200]
crk[idx] = rng.uniform(0.4, 1.0, len(idx)) * rng.choice([-1, 1], len(idx))
crk = bp(crk, 400, 5000) * 3.0
am = 1 + 0.25 * lp(rng.standard_normal(N), 9, 2) / 0.05
roar = (rumble + mid + crk * np.clip(envS, 0, 1)) * envS * np.clip(am, 0.6, 1.4)

L = np.zeros(N, np.float32); Rr = np.zeros(N, np.float32)
L += roar * 0.12; Rr += roar * 0.12
# ElevenLabs roar take, tiled with crossfades and shaped by the plume envelope
_r = loadel('roar'); _xf = int(0.5 * SR); _tile = np.zeros(N + len(_r), np.float32); _p = 0
while _p < N:
    seg = _r.copy(); seg[:_xf] *= np.linspace(0, 1, _xf); seg[-_xf:] *= np.linspace(1, 0, _xf)
    _tile[_p:_p + len(seg)] += seg; _p += len(_r) - _xf
elroar = _tile[:N] * envS
L += elroar * 0.75; Rr += elroar * 0.75

# ---- explosions
booms = [loadel('boom1'), loadel('boom2')]
for fl, fate, s, d in R.SEGS:
    if fate == 'blur': continue
    ft = s + R.fail_time(fate, d)
    ln = min(1.6, 0.25 + d * 1.6)
    bb = booms[fl % 2]; ln = min(ln, len(bb) / SR); b = bb[:int(ln * SR)] * np.linspace(1, 0, int(ln * SR)) ** 1.5
    # vary pitch by resampling
    rate = 0.8 + 0.4 * ((fl * 37) % 10) / 10
    b = np.interp(np.arange(0, len(b), rate), np.arange(len(b)), b)
    g = 0.9 if fl < 4 else 0.7
    pan = 0.4 + 0.2 * ((fl * 13) % 5) / 5
    place(L, b, ft, g * (1 - pan) * 2); place(Rr, b, ft, g * pan * 2)
# blur flights: a short whoosh each
wh = load('238375__stewdio2003__cp_subby_whoosh.aiff')[:int(0.5 * SR)] * np.linspace(1, 0, int(0.5 * SR))
_bl = [s for fl, fate, s, d in R.SEGS if fate == 'blur']
place(L, wh, _bl[0], 0.6); place(Rr, wh, _bl[0], 0.6)   # one whoosh for the single 12-14 fall

# ---- metal clank (modal synthesis) at both catches
def clank(big=1.0):
    n = int(2.8 * SR); t = np.arange(n) / SR
    out = np.zeros(n)
    modes = [(87, 1.0, 1.6), (143, 0.7, 1.9), (231, 0.55, 2.4), (397, 0.4, 3.2), (612, 0.3, 4.0), (1043, 0.2, 6.0), (1690, 0.12, 8.0)]
    for f, a, dcy in modes:
        out += a * np.sin(2 * np.pi * f * t * (1 + 0.002 * np.sin(t * 7))) * np.exp(-t * dcy / big)
    hit = rng.standard_normal(n) * np.exp(-t * 60)
    out += lp(hit, 2500) * 1.5
    thump = np.sin(2 * np.pi * 45 * t) * np.exp(-t * 7) * 2.0
    out = out + thump
    return (out / np.abs(out).max()).astype(np.float32)
_ec = loadel('clank'); c1 = _ec; c2 = _ec.copy(); _th = clank(1.5); c2[:len(_th)] += 0.35 * _th[:len(c2)]
place(L, c1, R.OPEN_CATCH - 0.02, 1.3); place(Rr, c1, R.OPEN_CATCH - 0.02, 1.3)
place(L, c2, R.CONTACT - 0.02, 1.8); place(Rr, c2, R.CONTACT - 0.02, 1.8)

# ---- rewind: reversed warp + falling pitch noise
warp = loadel('rewind')
rew = R.REW_END - R.OPEN_END
place(L, warp, R.OPEN_END, 0.55); place(Rr, warp, R.OPEN_END, 0.55)
n = int(rew * SR); t = np.arange(n) / SR
sweep = np.sin(2 * np.pi * np.cumsum(lerp := (900 - 600 * t / rew)) / SR) * 0.15 * np.sin(np.pi * t / rew)
place(L, sweep.astype(np.float32), R.OPEN_END); place(Rr, sweep.astype(np.float32), R.OPEN_END)

# ---- plasma hiss on finale reentry
n = int(R.F_REENTRY * SR); t = np.arange(n) / SR
_pl = loadel('plasma'); _pl = np.pad(_pl, (0, max(0, n - len(_pl))))[:n]
hiss = _pl * np.sin(np.pi * np.clip(t / R.F_REENTRY, 0, 1)) ** 0.5 * 0.7
place(L, hiss.astype(np.float32), R.FINALE_START); place(Rr, hiss.astype(np.float32), R.FINALE_START)

# ---- crowd cheer as the little figures appear after the catch
_ch = loadel('cheer'); _ch[:int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))
place(L, _ch, R.CONTACT + 0.45, 0.42); place(Rr, _ch, R.CONTACT + 0.45, 0.42)

# ---- light reverb tail
ir_n = int(1.8 * SR); ti = np.arange(ir_n) / SR
for ch in (0, 1):
    ir = rng.standard_normal(ir_n) * np.exp(-ti * 3.2); ir[0] = 0
    ir = lp(ir, 3000) * 0.04
    if ch == 0: L = L + fftconvolve(L, ir)[:N]
    else: Rr = Rr + fftconvolve(Rr, ir)[:N]

mixd = np.stack([L, Rr], 1)
mixd = np.tanh(mixd * 1.1) / np.tanh(1.1)
mixd *= 0.89 / np.abs(mixd).max()
fade = int(0.4 * SR)
mixd[-fade:] *= np.linspace(1, 0, fade)[:, None]
out = sys.argv[1]
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', out],
               input=mixd.astype(np.float32).tobytes(), check=True)
print('wrote', out, mixd.shape[0] / SR)
