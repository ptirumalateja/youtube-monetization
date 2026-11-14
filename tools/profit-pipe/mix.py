"""Sound for Profit Pipe. No music, no voice: every sound has a visible cause.
  python3 mix.py EVENTS_JSON OUT.wav
Foley = ElevenLabs sound effects (sfx/*.mp3, sfx/gen.sh). Cue times come from window.events / window.TL in scene.js.
Beds: the coin pour (right, loud, from frame 0) and his typing (left, quiet). Both drop to near silence for each salary
drip so the single coin's tink is the only sound: the flood vs the drip."""
import json, subprocess, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000
ev = json.load(open(sys.argv[1])); DUR = ev['dur']; N = int(DUR * SR); TL = ev['tl']
mixb = np.zeros((N, 2)); tt = np.arange(N) / SR
cache = {}
def load(name, rate=1.0):
    k = (name, rate)
    if k not in cache:
        af = [] if rate == 1 else ['-af', f'asetrate={int(SR*rate)},aresample={SR}']
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'sfx', name + '.mp3'), *af, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
        s = np.frombuffer(raw, np.float32).astype(np.float64); s /= np.abs(s).max() + 1e-9; cache[k] = s
    return cache[k]
def place(s, t, g, pan):
    i = int(t * SR); s = s[:max(0, N - i)]
    if i < 0: s = s[-i:]; i = 0
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    mixb[i:i + len(s), 0] += s * g * l; mixb[i:i + len(s), 1] += s * g * r
def bed(name, offset=0):
    s = load(name); n = len(s); xf = int(0.3 * SR); out = np.zeros(N + n); pos = 0; ramp = np.linspace(0, 1, xf)
    while pos < N:
        seg = s.copy(); seg[:xf] *= ramp; seg[-xf:] *= ramp[::-1]; out[pos:pos + n] += seg; pos += n - xf
    return np.roll(out[:N], offset)
duck = np.ones(N)
for l in TL['DRIPS']: duck *= 1 - 0.9 * np.interp(tt, [l - 0.75, l - 0.45, l + 0.55, l + 0.95], [0, 1, 1, 0])
pour = bed('pour'); pg = np.interp(tt, [0, TL['VALVE'], TL['VALVE'] + 0.2, TL['OVER'], TL['OVER'] + 0.3, DUR], [0.3, 0.3, 0.5, 0.55, 0.7, 0.7]) * duck
mixb[:, 0] += pour * pg * 0.45; mixb[:, 1] += np.roll(pour, 3000) * pg * 0.9
hum = bed('hum'); hg = 0.18 * duck; mixb[:, 0] += hum * hg * 0.7; mixb[:, 1] += hum * hg * 0.7
typ = bed('typing'); tg = 0.22 * (0.15 + 0.85 * duck)
for l in TL['DRIPS']: tg *= 1 - np.interp(tt, [l - 1.0, l - 0.8, l + 0.8, l + 1.1], [0, 1, 1, 0])
mixb[:, 0] += typ * tg * 0.9; mixb[:, 1] += typ * tg * 0.3
for e in ev['events']:
    s = load(e['s'], e.get('rate', 1.0)); g = e['g']
    if e['s'] in ('gulp', 'pile', 'choke'): g *= np.interp(e['t'], tt[::480], duck[::480])
    place(s, e['t'], g, e['pan'])
fade = np.interp(tt, [0, 0.02, DUR - 0.5, DUR], [0, 1, 1, 0.4]); mixb *= fade[:, None]
mixb *= 0.89 / (np.abs(mixb).max() + 1e-9)
import wave
with wave.open(sys.argv[2], 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mixb * 32767).astype('<i2').tobytes())
print('ok', sys.argv[2])
