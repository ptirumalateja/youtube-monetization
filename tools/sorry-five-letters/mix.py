"""Sound for Sorry Is 5 Letters. No music, no voice: every sound has a visible cause.
  python3 mix.py EVENTS_JSON OUT.wav
Foley = ElevenLabs sound effects (sfx/*.mp3; sfx/gen_new.sh for slam/thud/crack/creak/rewind/release).
Bed: cold wind under the silence, gone once the sorry is sent."""
import json, subprocess, sys, os, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000
ev = json.load(open(sys.argv[1])); DUR = ev['dur']; N = int(DUR * SR)
mixb = np.zeros((N, 2)); cache = {}
def load(name, rate=1.0):
    k = (name, rate)
    if k not in cache:
        af = [] if rate == 1 else ['-af', f'asetrate={int(SR*rate)},aresample={SR}']
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'sfx', name + '.mp3'), *af, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
        s = np.frombuffer(raw, np.float32).astype(np.float64); s /= np.abs(s).max() + 1e-9; cache[k] = s
    return cache[k]
def place(s, t, g, pan):
    i = int(t * SR)
    if i < 0: s = s[-i:]; i = 0
    s = s[:max(0, N - i)]
    l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
    mixb[i:i + len(s), 0] += s * g * l; mixb[i:i + len(s), 1] += s * g * r
onset = lambda s: int(np.argmax(np.abs(s) > 0.2))
for e in ev['events']:
    s = load(e['s'], e.get('rate', 1.0))
    t = e['t'] - (onset(s) / SR if e['s'] in ('slam', 'thud', 'crack', 'brick1', 'ping', 'sub') else 0)
    place(s, t, e['g'], e['pan'])
w = load('wind'); tt = np.arange(N) / SR
bed = np.resize(w, N + SR)[:N]
gain = np.interp(tt, [0, 1.3, 1.8, 7.6, 8.7, 9.6, DUR], [0.16, 0.16, 0.08, 0.22, 0.22, 0.0, 0.0])
for e in ev['events']:  # a breath of silence right before every hit, then the boom
    if e['s'] == 'sub': gain = gain * (1 - 0.9 * np.interp(tt, [e['t'] - 0.28, e['t'] - 0.18, e['t'] + 0.02, e['t'] + 0.3], [0, 1, 1, 0], left=0, right=0))
mixb[:, 0] += bed * gain; mixb[:, 1] += np.roll(bed, 2400) * gain
fade = np.interp(tt, [0, 0.01, DUR - 0.6, DUR], [0, 1, 1, 0]); mixb *= fade[:, None]
mixb *= 0.89 / (np.abs(mixb).max() + 1e-9)
with wave.open(sys.argv[2], 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mixb * 32767).astype('<i2').tobytes())
print('ok', sys.argv[2])
