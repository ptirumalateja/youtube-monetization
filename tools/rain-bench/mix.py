"""Sound for Sit In The Rain. No music, no voice: every sound has a visible cause.
  python3 mix.py EVENTS_JSON OUT.wav
Foley = ElevenLabs sound effects (sfx/*.mp3, sfx/gen.sh). Cue times come from window.events in scene.js.
Bed: steady rain that never stops (they can't stop it), a little lower once he leans in."""
import json, subprocess, sys, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000
ev = json.load(open(sys.argv[1])); DUR = ev['dur']; N = int(DUR * SR)
mixb = np.zeros((N, 2))
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
def onset(s):  # shift so the first transient lands on the cue
    return int(np.argmax(np.abs(s) > 0.2))
for e in ev['events']:
    s = load(e['s'], e.get('rate', 1.0)); g = e['g'] * (0.55 if e.get('panel') == 'bot' else 1.0)
    if e['s'] in ('brick1', 'brick2', 'step', 'ping'): place(s, e['t'] - onset(s) / SR, g, e['pan'])
    else: place(s, e['t'], g, e['pan'])
# wind bed (looped with a crossfade), louder as distance grows, ducked under the swell
w = load('rain'); tt = np.arange(N) / SR
bed = np.resize(w, N + SR)[:N]
gain = np.interp(tt, [0, 0.3, 5.6, 6.4, 8.5, DUR], [0.55, 0.45, 0.42, 0.3, 0.3, 0.25])
mixb[:, 0] += bed * gain * 0.9; mixb[:, 1] += np.roll(bed, 2400) * gain * 0.9
fade = np.interp(tt, [0, 0.03, DUR - 0.7, DUR], [0, 1, 1, 0]); mixb *= fade[:, None]
mixb *= 0.89 / (np.abs(mixb).max() + 1e-9)
import wave
with wave.open(sys.argv[2], 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mixb * 32767).astype('<i2').tobytes())
print('ok', sys.argv[2])
