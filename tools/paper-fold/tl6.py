"""v5 timeline: payoff-first hook, slower ground, VO beats cut from one take (char timestamps). Number words land with their folds."""
import json
D = __file__.rsplit('/', 1)[0]
def words(fn):
    AL = json.load(open(D + '/' + fn))['alignment']; ch, st, en = AL['characters'], AL['character_start_times_seconds'], AL['character_end_times_seconds']
    out = []; w = ''; t0 = None; pe = 0
    for c, s, e in zip(ch, st, en):
        if c in ' \n':
            if w: out.append((w, t0, pe)); w = ''; t0 = None
        else:
            if t0 is None: t0 = s
            w += c; pe = e
    if w: out.append((w, t0, pe))
    return [x for x in out if not (x[0].startswith('[') or x[0].endswith(']'))]
WS = {'v4': words('vo4_align.json'), 'v5': words('vo5_align.json')}
def find(first, last, W):
    """indices of word run starting at word 'first' (prefix) through the next word ending with 'last'"""
    i = next(k for k in range(FP[SRCK], len(W)) if W[k][0].startswith(first)); j = next(k for k in range(i, len(W)) if W[k][0].endswith(last)); FP[SRCK] = j + 1; return i, j
FP = {'v4': 0, 'v5': 0}; SRCK = 'v5'
# beat: name, first word, last word, folds (landing number, None for no landing), tempo, number-cap (s), tail-cap (s), min hold
BEATS = [('B0', 'What', 'times?', None, 1.12, 0, 0.7, 4.9), ('B2', 'Every', 'it.', None, 1.2, 0, 0.3, 1.6),
 ('N10', 'Ten', 'mug.', 10, 1.25, 0.6, 0.35, 1.5), ('N14', 'Fourteen.', 'you.', 14, 1.3, 0.9, 0.35, 2.0), ('N16', 'Sixteen.', 'giraffe.', 16, 1.3, 0.9, 0.4, 1.6),
 ('N20', 'Twenty.', 'Liberty.', 20, 1.3, 0.6, 0.45, 2.0), ('N22', 'Twenty-two.', 'Tower.', 22, 1.3, 0.9, 0.4, 1.7), ('N23', 'Twenty-three.', 'Khalifa.', 23, 1.3, 0.9, 0.45, 1.9),
 ('N27', 'Twenty-seven.', 'Everest.', 27, 1.3, 0.95, 0.45, 2.2), ('N30', 'Thirty.', 'space.', 30, 1.3, 0.5, 0.45, 2.7), ('N42', 'Forty-two.', 'Moon.', 42, 1.3, 0.95, 0.45, 2.0),
 ('N51', 'Fifty-one.', 'Sun.', 51, 1.3, 0.95, 0.45, 2.6), ('N69', 'Sixty-nine.', 'star.', 69, 1.3, 0.95, 0.45, 2.6), ('N83', 'Eighty-three.', 'galaxy.', 83, 1.3, 0.95, 0.45, 3.0),
 ('N103', 'One', 'universe.', 103, 1.25, 0.0, 0.45, 2.6), ('REC', 'In', 'twelve.', None, 1.15, 0, 0.5, 2.6)]
PARTS = {}   # name -> list of (src0, src1) cut ranges, concatenated
for name, a, b, fold, tempo, ncap, tcap, hold in BEATS:
    SRCK = 'v4' if name == 'B0' else 'v5'; W = WS[SRCK]; i, j = find(a, b, W); parts = []
    if ncap > 0 and i < j:
        s0, e0 = W[i][1], W[i][2]; parts.append((s0, min(e0, s0 + ncap)))
        if j > i + 1:
            parts.append((W[i + 1][1], W[j][1]))
        s0j = W[j][1]; parts.append((s0j, min(W[j][2], s0j + tcap)))
    else:
        s0 = W[i][1]; s1 = W[j][2]
        if j > i and tcap < (W[j][2] - W[j][1]):
            parts.append((s0, W[j][1])); parts.append((W[j][1], W[j][1] + tcap))
        else: parts.append((s0, s1))
    PARTS[name] = ([(SRCK, a_, b_) for a_, b_ in parts], tempo)
def dur(name):
    parts, tempo = PARTS[name]; return sum(b - a for _, a, b in parts) / tempo + 0.03 * (len(parts) - 1)
T_D = 0.0
P = {}; LAND = [(0, 0.9)]
P['B0'] = 0.15
P['B2'] = 5.2
L10 = 9.0; P['N10'] = L10 - 0.05
names = [b[0] for b in BEATS]; folds = {b[0]: b[3] for b in BEATS}; hold = {b[0]: b[7] for b in BEATS}
t = P['N10']; seq = ['N10', 'N14', 'N16', 'N20', 'N22', 'N23', 'N27', 'N30', 'N42', 'N51', 'N69', 'N83', 'N103', 'REC']
for k, n in enumerate(seq):
    P[n] = t
    if k + 1 < len(seq):
        nxt = seq[k + 1]; nf = folds[nxt] if folds[nxt] else 103; df = nf - folds[n]
        per = 0.34 if folds[n] < 30 else 0.20
        H = max(dur(n) + 0.2, hold[n] + 0.15, df * per); t += H
LAND += [(10, L10)]
for n in seq[1:-1]:
    LAND.append((folds[n], P[n] + 0.05))
# the 103rd fold lands on the word 'three' of the final beat
LAND[-1] = (103, P['N103'] + 0.85)
# 88 lands between 83 and 103 (Andromeda)
t83 = [b for a, b in LAND if a == 83][0]; LAND.append((88, t83 + 0.3 * (LAND[-1][1] - t83))); LAND.sort()
LAND = [(a, b) for a, b in LAND]
END_VO = P['REC'] + dur('REC'); DUR = END_VO + 1.9
T_103 = LAND[-1][1]

def cw(name):
    """new-timeline start of the last (content) word of a beat"""
    parts, tempo = PARTS[name]; tt = sum(b - a for _, a, b in parts[:-1]) / tempo + 0.03 * (len(parts) - 1)
    if len(parts) == 1:
        # single part: locate last word start inside it
        key, a, b = parts[0]; w = [x for x in WS[key] if a - 1e-6 <= x[1] <= b][-1]; return P[name] + (w[1] - a) / tempo
    return P[name] + tt
