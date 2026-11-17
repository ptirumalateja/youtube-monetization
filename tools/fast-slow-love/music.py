# Soft felt-piano bed for the remake (procedural, no samples). 13.6 s, 48 kHz mono -> music.wav
# Warm major progression while both fires burn; drops to a lonely low note at day 30 ("You've changed");
# resolves on a warm chord at "I love you." (12.0 s).
import numpy as np, wave, sys
SR = 48000; DUR = 13.6
N = int(SR * DUR); out = np.zeros(N)

def note(f, t0, dur=2.6, vel=.5):
    n = int(SR * dur); t = np.arange(n) / SR
    s = np.zeros(n)
    for h, a in [(1, 1), (2, .42), (3, .18), (4, .08), (5, .04)]:
        detune = 1 + .0006 * (h - 1)
        s += a * np.sin(2 * np.pi * f * h * detune * t) * np.exp(-t * (1.6 + h * .9))
    att = np.minimum(1, t / .012)
    s *= att * vel
    # felt hammer thump
    s[:200] += np.random.RandomState(int(f)).randn(200) * .02 * vel * np.exp(-np.arange(200) / 40)
    i = int(t0 * SR); j = min(N, i + n)
    if i < N: out[i:j] += s[:j - i]

m = lambda k: 440 * 2 ** ((k - 69) / 12)
# key of D major, 80 bpm feel (0.75 s per beat)
prog = [  # (start, bass, chord notes)
    (0.0, 50, [62, 66, 69]),   # D
    (1.5, 47, [62, 66, 71]),   # Bm
    (3.0, 43, [62, 67, 71]),   # G
    (4.5, 45, [61, 64, 69]),   # A
    (6.0, 50, [62, 66, 69]),   # D (fire already shrinking)
]
mel = [(0.0, 74), (.75, 73), (1.5, 71), (2.25, 74), (3.0, 79), (3.75, 78), (4.5, 76), (5.25, 73), (5.5, 81), (6.0, 78), (6.75, 76)]
for t0, b, ch in prog:
    note(m(b), t0, 3.0, .55)
    for k, c in enumerate(ch): note(m(c), t0 + .02 * k, 2.4, .22)
for t0, k in mel: note(m(k), t0, 2.0, .30)
# day 27-30: falling, sparse
note(m(47), 7.2, 3.0, .45); note(m(71), 7.2, 2.2, .2); note(m(66), 7.6, 2.0, .18)
# "YOU'VE CHANGED." : one low lonely note + minor second rub
note(m(38), 8.0, 4.0, .6); note(m(62), 8.05, 3.2, .16); note(m(63), 8.35, 3.0, .10)
# fast-forward: ticking high notes, gentle, accelerating 9.35 -> 11.45
ts = 9.35; gap = .32
while ts < 11.4:
    note(m(86), ts, .6, .08); ts += gap; gap = max(.09, gap * .86)
# day 365 bottom: warm return, "I LOVE YOU." resolve
note(m(43), 11.5, 3.0, .45); [note(m(c), 11.52, 2.6, .18) for c in (62, 67, 71)]
note(m(50), 12.0, 3.0, .55); [note(m(c), 12.0 + .03 * k, 2.8, .22) for k, c in enumerate((62, 66, 69, 74))]
note(m(78), 12.05, 2.6, .3)

# soft room reverb (feedback comb + allpass-ish smear)
def reverb(x):
    y = x.copy()
    for d, g in [(1601, .5), (2213, .45), (2803, .4), (3517, .35)]:
        # vectorised comb via repeated shifts (4 taps)
        for r in range(1, 6):
            sh = d * r
            if sh < len(x): y[sh:] += x[:-sh] * (g ** r) * .35
    return y
out = reverb(out)
fade = np.ones(N); fi = int(13.1 * SR); fade[fi:] = np.linspace(1, 0, N - fi); out *= fade
out /= np.max(np.abs(out)) + 1e-9; out *= .8
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((out * 32767).astype(np.int16).tobytes())
