"""Sound for Snake and the Saw: ElevenLabs VO (vo/vo.wav) + ElevenLabs foley (sfx/*.mp3) at window.events cue times.
House rules: no SFX in the hook (0-3.5 s) or in the closing rule + CTA (after 52 s); no music.
  python3 mix.py EVENTS_JSON OUT.wav"""
import json, subprocess, sys, os, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000
ev = json.load(open(sys.argv[1])); DUR = ev['dur']; N = int(DUR * SR); tt = np.arange(N) / SR
def dec(path, af=None):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, *(['-af', af] if af else []), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)
vo = dec(os.path.join(HERE, 'vo', 'vo.wav'))[:N]; vo = np.pad(vo, (0, N - len(vo)))
# VO activity envelope for ducking the foley
env = np.convolve(np.abs(vo), np.ones(4800) / 4800, 'same'); act = np.clip(env / (env.max() * 0.15), 0, 1)
duck = 1 - 0.45 * act
fx = np.zeros((N, 2)); cache = {}
def load(n, rate=1.0):
    k = (n, rate)
    if k not in cache:
        s = dec(os.path.join(HERE, 'sfx', n + '.mp3'), None if rate == 1 else f'asetrate={int(SR*rate)},aresample={SR}'); s /= np.abs(s).max() + 1e-9
        f = int(0.02 * SR); s[-f:] *= np.linspace(1, 0, f); cache[k] = s
    return cache[k]
for e in ev['events']:
    if e['t'] < 3.5 or e['t'] > 52.2: continue
    s = load(e['s'], e.get('rate', 1.0)); i = int(e['t'] * SR); s = s[:max(0, N - i)]
    l, r = np.sqrt((1 - e['pan']) / 2), np.sqrt((1 + e['pan']) / 2)
    fx[i:i + len(s), 0] += s * e['g'] * l; fx[i:i + len(s), 1] += s * e['g'] * r
room = load('room'); bed = np.tile(room, N // len(room) + 1)[:N] * 0.05 * np.interp(tt, [0, 3.6, 4.2, 51.5, 52.5, DUR], [0, 0, 1, 1, 0, 0])
fx *= (duck * 0.55)[:, None]
mix = fx + (vo * 0.9)[:, None] + bed[:, None]
mix *= np.interp(tt, [0, 0.01, DUR - 0.4, DUR], [0, 1, 1, 0])[:, None]
mix *= 0.9 / (np.abs(mix).max() + 1e-9)
with wave.open(sys.argv[2], 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mix * 32767).astype('<i2').tobytes())
print('ok', sys.argv[2])
