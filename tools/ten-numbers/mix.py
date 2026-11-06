"""Sound for Ten Numbers: python3 mix.py OUT.wav. Recorded foley only (ElevenLabs sound-effects in sfx/), no music.
Every time comes from timeline.json (the same file the scene reads). Silence is a beat: the room tone drops when the phone dies."""
import json, os, subprocess, sys, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); TL = json.load(open(os.path.join(HERE, 'timeline.json')))
SR = 48000; D = TL['duration']; N = int(D * SR); S = os.path.join(HERE, 'sfx')
rng = np.random.default_rng(7)

def load(name):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(S, name), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype=np.float32).reshape(-1, 2).copy()

def speed(x, k):
    n = int(len(x) / k); idx = np.arange(n) * k; i0 = np.floor(idx).astype(int).clip(0, len(x) - 2); f = (idx - i0)[:, None]
    return x[i0] * (1 - f) + x[i0 + 1] * f

mix = np.zeros((N, 2), dtype=np.float32)
def put(x, t, g=1.0, k=1.0, maxlen=None, fade=0.03):
    if k != 1.0: x = speed(x, k)
    if maxlen: x = x[:int(maxlen * SR)]
    x = x * g; nf = min(len(x), int(fade * SR)); x[-nf:] *= np.linspace(1, 0, nf)[:, None]
    i = int(t * SR); j = min(N, i + len(x))
    if i < N and j > i: mix[i:j] += x[:j - i]

room = load('room.mp3'); room = np.tile(room, (int(np.ceil(N / len(room))), 1))[:N]
tt = np.arange(N) / SR
env = np.ones(N, dtype=np.float32)
duck = (tt > TL['deadAt'] - 0.05) & (tt < TL['setDown'] + 0.2)
ramp = np.clip((tt - (TL['deadAt'] - 0.05)) / 0.15, 0, 1) * np.clip(((TL['setDown'] + 0.2) - tt) / 0.8, 0, 1)
env = (1 - 0.88 * ramp).astype(np.float32)
mix += room * 0.12 * env[:, None]

put(load('thump.mp3'), 0.0, 0.35)                                  # a felt low hit on frame 0
for (t0, k, amp) in TL['pullsIntro'] + TL['pullsEnd']:
    put(load('dial1.mp3'), t0 - 0.06, 0.5, k=1 + (k - 4) * 0.012, maxlen=0.95, fade=0.08)
pick = load('pickup.mp3'); cradle = load('cradle.mp3')
put(pick, TL['recv1'][0] + 0.12, 0.55); put(cradle, TL['recv1'][1] + 0.35, 0.5)
put(pick, TL['recv2'][0] + 0.12, 0.55)
put(load('ping.mp3'), TL['phoneIn'] + 0.05, 0.5)
tap = load('tap.mp3')
t = TL['phoneIn'] + 0.9
while t < TL['flickerFrom']: put(tap, t, 0.22 * rng.uniform(0.7, 1.1), k=rng.uniform(0.95, 1.1), maxlen=0.2, fade=0.04); t += rng.uniform(0.3, 0.5)
t = TL['shake'][0]
while t < TL['shake'][1]: put(tap, t, 0.34, k=rng.uniform(0.95, 1.1), maxlen=0.2, fade=0.04); t += 0.18
tick = load('tick.mp3')
for i, (n, d) in enumerate(TL['depart']): put(tick, d + TL['fly'] - 0.03, 0.5, k=0.8 + 0.08 * i, maxlen=0.4)
put(load('powerdown.mp3'), TL['deadAt'] - 0.15, 0.6, maxlen=1.1)
put(load('thump.mp3'), TL['payoffIn'] - 0.02, 0.7)
put(load('tick.mp3'), TL['hookQ'], 0.45, k=0.9, maxlen=0.4)                      # the question lands
put(load('ring.mp3'), TL['ringAt'][0], 0.55, maxlen=TL['answer'] - TL['ringAt'][0] + 0.05, fade=0.12)
put(load('answer.mp3'), TL['answer'], 0.5)
fade_out = np.clip((D - tt) / 0.5, 0, 1)[:, None]; mix *= fade_out
mix = np.tanh(mix * 1.1) / 1.1
pcm = (np.clip(mix, -1, 1) * 32767).astype('<i2')
with wave.open(sys.argv[1], 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('mix ok', sys.argv[1])
