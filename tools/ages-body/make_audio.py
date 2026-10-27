"""Mix narration + synthesised sound design -> film_audio.wav (44.1 kHz stereo). Needs film_timeline.json."""
import json, subprocess, sys, numpy as np
SR = 44100
NARR = '/mnt/project-files/ages-1-to-100/narration'
tl = json.load(open('film_timeline.json')); total = tl['total']
N = int((total + 1) * SR); t = np.arange(N) / SR
rng = np.random.default_rng(7)

def load(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', p, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).astype(np.float64)
def env(x, a, b):  # 0..1 ramp
    return np.clip((x - a) / max(b - a, 1e-6), 0, 1)
def sm(x): return x * x * (3 - 2 * x)
def lp(x, fc):  # one-pole lowpass
    a = np.exp(-2 * np.pi * fc / SR); y = np.empty_like(x); s = 0.0
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)
def put(buf, x, at, gain=1.0):
    i = int(at * SR); n = min(len(x), len(buf) - i)
    if n > 0 and i >= 0: buf[i:i + n] += x[:n] * gain

B = {b['id']: b for b in tl['beats']}
# ------------------------------------------------------------------ narration
vo = np.zeros(N)
for b in tl['beats']:
    put(vo, load(f"{NARR}/{b['vo']}"), b['start'] + b['lead'])
vo_env = lp(np.abs(vo), 6.0); vo_env = np.clip(vo_env / (vo_env.max() + 1e-9) * 6, 0, 1)

# ------------------------------------------------------------------ pad (slow chord per beat, crossfaded)
CH = [[110.0, 164.81, 220.0, 261.63], [87.31, 130.81, 174.61, 220.0], [130.81, 196.0, 261.63, 329.63], [98.0, 146.83, 196.0, 246.94]]
order = ['lineup', 'age1', 'age35', 'age10', 'age18', 'age25', 'age30', 'rehook', 'age40', 'age50', 'age60', 'age70', 'age80']
pad = np.zeros(N)
for i, bid in enumerate(order):
    b = B[bid]; a0, a1 = b['start'] - 1.5, b['start'] + b['dur'] + 1.5
    g = sm(env(t, a0, a0 + 2.5)) * (1 - sm(env(t, a1 - 2.5, a1)))
    if not g.any(): continue
    seg = np.zeros(N)
    for f in CH[i % 4]:
        for det in (-0.6, 0.0, 0.7):
            seg += np.sin(2 * np.pi * (f + det * 0.5) * t + det) * 0.5 + np.sin(2 * np.pi * f * 2.0 * t + det) * 0.12
    pad += seg * g
pad = lp(pad, 900) * 0.06
pad *= 0.55 + 0.45 * np.sin(2 * np.pi * t / 17.0) ** 2
# music level: swells in the gaps, ducks under narration; gone at age 100
pad_gain = (0.5 + 0.5 * (1 - vo_env)) * (1 - sm(env(t, B['age100']['start'] + 0.2, B['age100']['start'] + 1.2))) * (1 - 0.0)
pad_gain *= (1 - sm(env(t, B['end']['start'] + B['end']['dur'] - 3, B['end']['start'] + B['end']['dur'])))
pad_gain *= env(t, B['lineup']['start'] - 0.5, B['lineup']['start'] + 2)  # silent hook
# the tree: pad returns warm after one note
pad_gain += (sm(env(t, B['tree']['start'] + 3.0, B['tree']['start'] + 6.0))) * (t > B['tree']['start']) * 0.0
music = pad * pad_gain

# ------------------------------------------------------------------ heartbeat
BPM = {'lineup': 60, 'age1': 130, 'age35': 100, 'age10': 88, 'age18': 76, 'age25': 72, 'age30': 66, 'rehook': 66, 'age40': 68, 'age50': 68, 'age60': 68, 'age70': 68, 'age80': 62}
VOL = {'lineup': 0.35, 'age1': 0.55, 'age35': 0.35, 'age10': 0.3, 'age18': 0.35, 'age25': 0.3, 'age30': 1.0, 'rehook': 0.0, 'age40': 0.4, 'age50': 0.4, 'age60': 0.4, 'age70': 0.7, 'age80': 0.45}
def thump(f0, dur, amp):
    n = int(dur * SR); x = np.arange(n) / SR
    return np.sin(2 * np.pi * (f0 * (1 + 1.2 * np.exp(-x * 40))) * x) * np.exp(-x * 14) * amp
LUB, DUB = thump(52, 0.35, 1.0), thump(64, 0.3, 0.6)
heart = np.zeros(N)
for bid in order:
    b = B[bid]; v = VOL[bid]
    if v <= 0: continue
    per = 60.0 / BPM[bid]; k = 0
    while True:
        at = b['start'] + 0.3 + k * per
        if at > b['start'] + b['dur'] - 0.2: break
        fade = sm(env(at, b['start'] + 0.3, b['start'] + 1.5)) * (1 - sm(env(at, b['start'] + b['dur'] - 0.9, b['start'] + b['dur'] - 0.1)))
        put(heart, LUB, at, v * fade); put(heart, DUB, at + 0.28 * per, v * fade * 0.8); k += 1
heart = lp(heart, 160) * 1.1

# ------------------------------------------------------------------ hook design + hits
fx = np.zeros(N)
hook = B['hook']
tone = np.sin(2 * np.pi * 55 * t) * 0.5 + np.sin(2 * np.pi * 110.4 * t) * 0.15
fx += tone * sm(env(t, 0.1, 2.5)) * (1 - sm(env(t, 6.2, 6.4))) * 0.05
room = lp(rng.standard_normal(N), 400) * sm(env(t, 0, 1.5)) * (1 - sm(env(t, 6.2, 6.6))) * 0.02
fx += room
# reverse swell 3.0 -> 6.4 and hit
sw = (t >= 3.0) & (t < 6.4); u = np.clip((t - 3.0) / 3.4, 0, 1)
noise = rng.standard_normal(N)
sweep = lp(noise, 300) * 0.0
swell = np.zeros(N)
for fc, gg in [(250, 1.0), (900, 0.8), (3000, 0.5)]:
    swell += lp(noise, fc) * gg
swell *= (u ** 2.4) * sw * 0.12
fx += swell
hit_n = int(2.2 * SR); hx = np.arange(hit_n) / SR
hit = np.sin(2 * np.pi * (38 + 40 * np.exp(-hx * 14)) * hx) * np.exp(-hx * 2.2) * 0.9 + lp(rng.standard_normal(hit_n), 700) * np.exp(-hx * 6) * 0.5
put(fx, hit, 6.4, 0.55)
# soft rise into each age change: very quiet air whoosh at beat starts
for b in tl['beats'][2:]:
    if b['id'] in ('age100',): continue
    n = int(1.6 * SR); x = np.arange(n) / SR
    w = lp(rng.standard_normal(n), 1800) * np.sin(np.pi * np.clip(x / 1.6, 0, 1)) ** 2 * 0.035
    put(fx, w, b['start'] - 0.5)
# rehook: one-second silence is natural (heart off); age100 drop: all off except narration
# the tree: one warm note
def bell(f, dur, amp):
    n = int(dur * SR); x = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * x) + 0.4 * np.sin(2 * np.pi * f * 2.0 * x) + 0.15 * np.sin(2 * np.pi * f * 3.01 * x)) * np.exp(-x * 0.7) * np.clip(x / 0.04, 0, 1) * amp
tr = B['tree']['start']
put(fx, bell(220, 9, 0.16) + bell(329.63, 9, 0.1), tr + 0.2)
# end card resolution chord
en = B['end']['start']
for f in (110, 164.81, 220, 277.18, 329.63):
    put(fx, bell(f, 12, 0.07), en + 0.2)
fx *= 1 - sm(env(t, B['end']['start'] + B['end']['dur'] - 2.5, B['end']['start'] + B['end']['dur']))

# ------------------------------------------------------------------ mix
mix = vo * 1.0 + music * 1.0 + heart * 0.55 + fx * 1.0
# duck pad+fx lightly under VO (already done for pad); soft limiter
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
peak = np.abs(mix).max(); mix = mix / peak * 0.89
mix = mix[: int((total) * SR)]
st = np.stack([mix, mix], 1)
# fake width on music: tiny delay
import wave
out = (st * 32767).astype('<i2')
with wave.open('film_audio.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())
print('audio', len(mix) / SR, 's, peak', peak)
