"""v7 timeline: cuts come from the AUDIO itself (silence-split utterance runs), not the alignment (which was off by up to 0.4 s).
Every milestone fold lands on its number word, then the folding PAUSES (hold) while the thing is named and compared; then folds resume."""
import wave, subprocess, numpy as np
TAKES = {'v4': '/mnt/project-files/paper-fold/vo4/take.mp3', 'v5': '/mnt/project-files/paper-fold/vo4/take5.mp3'}
def runs(path, thr_rel=0.06, gap=0.16):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', path, '-ar', '16000', '-ac', '1', '/tmp/_a.wav'], check=True)
    with wave.open('/tmp/_a.wav') as w: x = np.frombuffer(w.readframes(w.getnframes()), '<i2') / 32768.
    hop = 80; env = np.array([np.sqrt(np.mean(x[i:i + 240] ** 2)) for i in range(0, len(x) - 240, hop)])
    thr = thr_rel * np.percentile(env, 98); on = env > thr; out = []; i = 0; n = len(on)
    while i < n:
        if on[i]:
            j = i
            while j < n:
                if on[j]: j += 1; continue
                k = j
                while k < n and not on[k]: k += 1
                if (k - j) * 0.005 < gap and k < n: j = k; continue
                break
            if (j - i) * 0.005 > 0.08: out.append((i * 0.005, j * 0.005))
            i = j
        else: i += 1
    return out
RUNS = {k: runs(v) for k, v in TAKES.items()}
assert len(RUNS['v5']) == 32 and len(RUNS['v4']) == 24, (len(RUNS['v5']), len(RUNS['v4']))
# beat: name -> (take, [run indices], tempo, gap between runs)
BEATS = {'B0': ('v4', [0, 1], 1.08, 0.30), 'B2': ('v5', [2], 1.15, 0), 'N10': ('v5', [3, 4], 1.2, 0.10), 'N14': ('v5', [5, 6], 1.2, 0.10), 'N16': ('v5', [7, 8], 1.2, 0.10),
 'N20': ('v5', [9, 10], 1.2, 0.10), 'N22': ('v5', [11, 12], 1.2, 0.10), 'N23': ('v5', [13, 14], 1.2, 0.10), 'N27': ('v5', [15, 16], 1.2, 0.10), 'N30': ('v5', [17, 18], 1.2, 0.10),
 'N42': ('v5', [19, 20], 1.2, 0.10), 'N51': ('v5', [21, 22], 1.2, 0.10), 'N69': ('v5', [23, 24], 1.2, 0.10), 'N83': ('v5', [25, 26], 1.2, 0.10), 'N103': ('v5', [27, 28], 1.2, 0.12), 'REC': ('v5', [29, 30, 31], 1.1, 0.12)}
PRE, POST = 0.03, 0.06
def pieces(name):
    key, idx, tempo, gap = BEATS[name]; out = []
    for ii in idx:
        a, b = RUNS[key][ii]; out.append((key, max(0, a - PRE), b + POST))
    return out
def seg_dur(key_a_b, tempo): return (key_a_b[2] - key_a_b[1]) / tempo
def dur(name):
    _, idx, tempo, gap = BEATS[name]; ps = pieces(name); return sum(seg_dur(p, tempo) for p in ps) + gap * (len(ps) - 1)
def starts(name):
    """new-timeline offsets (from beat start) of each piece"""
    _, idx, tempo, gap = BEATS[name]; ps = pieces(name); t = 0; o = []
    for p in ps: o.append(t); t += seg_dur(p, tempo) + gap
    return o
def cw(name): return P[name] + starts(name)[1]          # second piece = the thing's name
T_D = 0.0
P = {'B0': 0.15, 'B2': 0.15 + dur('B0') + 0.25}
PER_G, PER_S = 0.28, 0.15
EXTRA = {15: 0.6, 32: 0.9, 56: 0.9, 88: 0.9}   # unnarrated holds (hoop, ISS, Neptune, Andromeda)
seq = ['N10', 'N14', 'N16', 'N20', 'N22', 'N23', 'N27', 'N30', 'N42', 'N51', 'N69', 'N83', 'N103']
FOLD = {n: int(n[1:]) for n in seq}
LAND = [(0, 0.9)]
L10 = 9.0; t = L10; P['N10'] = L10 - 0.02 
HOLD_END = {}
for k, n in enumerate(seq):
    f = FOLD[n]; P[n] = t - 0.02; LAND.append((f, t))
    d = dur(n); ds = starts(n)
    hold_end = max(t + d + 0.25, P[n] + ds[1] + 0.95); HOLD_END[n] = hold_end; LAND.append((f, hold_end))
    t = hold_end
    if k + 1 < len(seq):
        nf = FOLD[seq[k + 1]]; per = PER_G if f < 30 else PER_S
        for g in range(f + 1, nf):
            t += per
            if g in EXTRA: LAND.append((g, t)); t += EXTRA[g]; LAND.append((g, t))
        t += per      # the milestone fold itself
LAND = [x for x in LAND]
T_103 = [b for a, b in LAND if a == 103][0]
# plateau segments: duplicates are fine; drop duplicate landing times for the first reach
P['REC'] = HOLD_END['N103'] + 0.7
END_VO = P['REC'] + dur('REC'); DUR = END_VO + 1.9
