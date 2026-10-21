# Original sound bed for the chalk reel, synthesised locally (no samples). Pure Python, writes sfx_bed.wav.
# Cue times follow the voiceover beats (VO starts at +0.35 s in the mix).
import math, random, struct, wave, json, sys
SR = 48000; DUR = 20.0; N = int(SR * DUR)
buf = [0.0] * N
random.seed(7)
here = sys.argv[1] if len(sys.argv) > 1 else '.'
ts = json.load(open(f'{here}/audio/vo_timestamps.json')); OFF = .35
def w(word):
    return next(x['start'] for x in ts['words'] if ''.join(c for c in x['word'].lower() if c.isalpha() or c == "'") == word) + OFF

def add(t0, fn, dur):
    i0 = max(0, int(t0 * SR)); i1 = min(N, int((t0 + dur) * SR))
    for i in range(i0, i1):
        buf[i] += fn((i - i0) / SR)

def hit(t0, gain=1.0, f0=95, f1=42):
    # transient crack + pitch-dropping saturated body + small sub
    ph = [0.0]
    def fn(t):
        f = f1 + (f0 - f1) * math.exp(-t * 6)
        ph[0] += 2 * math.pi * f / SR
        body = math.tanh(2.2 * math.sin(ph[0]) + .6 * math.sin(2 * ph[0])) * math.exp(-t * 2.6)
        crack = (random.random() * 2 - 1) * math.exp(-t * 38)
        return gain * (.55 * body + .35 * crack)
    add(t0, fn, 1.8)

def swell(t0, dur, gain=.25):
    lp = [0.0]
    def fn(t):
        u = t / dur
        lp[0] += (random.random() * 2 - 1 - lp[0]) * (.02 + .25 * u * u)
        return gain * lp[0] * (u ** 2.2) * 3
    add(t0, fn, dur)

def tick(t0, gain=.35):
    add(t0, lambda t: gain * (random.random() * 2 - 1) * math.exp(-t * 90) + gain * .5 * math.sin(2 * math.pi * 1900 * t) * math.exp(-t * 60), .12)

def lock(t0):
    add(t0, lambda t: .35 * (math.sin(2 * math.pi * 2600 * t) + .7 * math.sin(2 * math.pi * 3720 * t) + .4 * math.sin(2 * math.pi * 5100 * t)) * math.exp(-t * 22) + .3 * (random.random() * 2 - 1) * math.exp(-t * 120), .5)

def beat(t0, gain):
    # lub-dub at 70/140/210 Hz so phone speakers carry it
    for dt, gg in ((0, 1.0), (.17, .7)):
        add(t0 + dt, lambda t, gg=gg: gain * gg * math.tanh(1.8 * (math.sin(2 * math.pi * 70 * t) + .5 * math.sin(2 * math.pi * 140 * t) + .25 * math.sin(2 * math.pi * 210 * t))) * math.exp(-t * 16), .3)

# drone bed: two detuned low tones + breathy noise, slowly rising, cut for the loop blink
lp = 0.0
for i in range(N):
    t = i / SR
    lp += ((random.random() * 2 - 1) - lp) * .015
    rise = .35 + .65 * min(1, t / 16)
    amp = .07 * rise * (1 - max(0, (t - 19.8) / .2))
    buf[i] += amp * (math.sin(2 * math.pi * 110 * t) * .6 + math.sin(2 * math.pi * 116.5 * t) * .5 + math.sin(2 * math.pi * 165 * t + math.sin(t * .7)) * .3) + lp * .35 * rise * (1 - max(0, (t - 19.8) / .2))
    # tinnitus ring while it leans in
    if w('some') < t < w('nearly'):
        buf[i] += .012 * math.sin(2 * math.pi * 5800 * t) * min(1, (t - w('some')) / 1.0)

hit(0.0, 1.0)                                   # title slam on frame 0
tick(w('up') - .05, .4)                          # eyes snap open
swell(w('something') - .9, .9, .3); hit(w('something'), .9, 110, 38)   # it appears
t = w('standing') + .2; bpm = 66                 # heartbeat accelerates until the figure beat
while t < w('nearly') - .2:
    beat(t, .5 + .3 * min(1, (t - 4) / 10)); bpm = min(128, bpm * 1.035); t += 60 / bpm
lock(w('locked') + .25)                          # padlock snaps on the body
swell(w('spills') - .3, 1.1, .18)                # the dream pours out
hit(w('figure'), .8, 90, 36)                     # it leans in
swell(w('nearly') - .2, 1.2, .35); hit(w('ten'), .55, 120, 50)  # pull back to the ten rooms
swell(19.0, .8, .25)                              # rushing back in; the blink at 19.82 cuts everything

peak = max(abs(x) for x in buf) or 1
with wave.open(f'{here}/audio/sfx_bed.wav', 'w') as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
    f.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, x / peak * .9)) * 32767)) for x in buf))
print('ok', round(peak, 3))
