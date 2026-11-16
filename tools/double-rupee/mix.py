"""Sound for "₹1 crore or ₹1 doubled?". No music, no voice: every sound has a visible cause.
  python3 mix.py EVENTS_JSON OUT.wav
Foley = ElevenLabs sound effects (sfx/*.mp3, sfx/gen.sh). Cues come from window.events / window.TL in scene.js.
Energy only climbs: a low room bed, coin ticks that rise in pitch, heavier note bundles, a heartbeat under the
catch-up, then a boom on day 24 and a rise-and-boom per landmark."""
import json, subprocess, sys, os, wave
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
def bed(name):
    s = load(name); n = len(s); xf = int(0.3 * SR); o = np.zeros(N + n); pos = 0; ramp = np.linspace(0, 1, xf)
    while pos < N:
        seg = s.copy(); seg[:xf] *= ramp; seg[-xf:] *= ramp[::-1]; o[pos:pos + n] += seg; pos += n - xf
    return o[:N]
def env(keys): return np.interp(tt, [k[0] for k in keys], [k[1] for k in keys])
FL, END = TL['T_FLIP'], TL['T_END']
room = bed('room'); rg = env([(0, 0.25), (FL, 0.45), (FL + 0.1, 0.6), (DUR, 0.5)])
mixb[:, 0] += room * rg * 0.5; mixb[:, 1] += np.roll(room, 6000) * rg * 0.5
for e in ev['events']:
    s = load(e['s'], e.get('rate', 1.0)) * e['g']; i = int(e['t'] * SR); s = s[:max(0, N - i)]
    if i < 0: s = s[-i:]; i = 0
    s = s.copy(); te = e['t'] + np.arange(len(s)) / SR
    if e['s'] == 'heart': s *= np.clip((FL - te) / 0.02, 0, 1)        # heartbeat cut dead by the day-24 boom
    if e['s'] == 'rise': s *= np.clip((te - e['t']) / 0.25, 0, 1)
    p = e.get('pan', 0); l, r = np.sqrt((1 - p) / 2), np.sqrt((1 + p) / 2)
    mixb[i:i + len(s), 0] += s * l; mixb[i:i + len(s), 1] += s * r
fade = env([(0, 1), (DUR - 0.6, 1), (DUR, 0.25)]); mixb *= fade[:, None]
mixb *= 0.89 / (np.abs(mixb).max() + 1e-9)
with wave.open(sys.argv[2], 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mixb * 32767).astype('<i2').tobytes())
print('ok', sys.argv[2])
