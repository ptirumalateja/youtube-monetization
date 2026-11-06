"""v4 timeline: one tense VO take cut into sentences (character timestamps), each placed so its number word lands with the fold."""
import json
AL = json.load(open(__file__.rsplit('/', 1)[0] + '/vo4_align.json'))['alignment']
ch, st, en = AL['characters'], AL['character_start_times_seconds'], AL['character_end_times_seconds']
TEXT = ''.join(ch)
def span(first_word_prefix, last_word_end_text):
    """source time span: start of first_word_prefix .. end of last_word_end_text (searched in order)"""
    i = TEXT.index(first_word_prefix, span.pos); j = TEXT.index(last_word_end_text, i) + len(last_word_end_text) - 1
    span.pos = j; return st[i], en[j]
span.pos = 0
# (name, first words, last words, tempo, gap after)
SEGS = [('S0', 'What if', 'times?', 1.12, 0.12), ('S1', 'Every', 'it.', 1.25, 0.08), ('S2', 'Fourteen', 'you.', 1.25, 0.10), ('S3', 'Twenty-two', 'Tower.', 1.3, 0.10),
        ('S4', 'Twenty-three', 'Khalifa.', 1.4, 0.22), ('S5', 'Thirty', 'space.', 1.25, 0.60), ('S6', 'Forty-two', 'Moon.', 1.35, 0.10), ('S7', 'Fifty-one', 'Sun.', 1.35, 0.55),
        ('S8', 'Sixty-nine', 'star.', 1.35, 0.30), ('S9', 'Eighty-three', 'galaxy.', 1.35, 0.12), ('S10', 'One hundred', 'universe.', 1.3, 0.70), ('S11', 'In real', 'twelve.', 1.2, 0.0)]
P = {}; SRC = {}; DURN = {}; t = 0.15
for name, a, b, tempo, gap in SEGS:
    s0, s1 = span(a, b); SRC[name] = (s0, s1, tempo); DURN[name] = (s1 - s0) / tempo; P[name] = t; t += DURN[name] + gap
END_VO = P['S11'] + DURN['S11']; DUR = END_VO + 1.9
def word_at(name, prefix):
    """new-timeline time at which a word (found inside this segment) starts"""
    s0, s1, tp = SRC[name]
    for i in range(len(TEXT)):
        if st[i] >= s0 - 1e-6 and TEXT.startswith(prefix, i) and st[i] <= s1: return P[name] + (st[i] - s0) / tp
    raise KeyError(prefix)
# fold-landing anchors (fold, time).  each number word starts exactly as its fold lands
LAND = [(0, 0.30), (10, P['S1'] + 0.9), (14, P['S2'] + 0.05), (22, P['S3'] + 0.05), (23, P['S4'] + 0.05), (30, P['S5'] + 0.05), (42, P['S6'] + 0.05), (51, P['S7'] + 0.05),
        (69, P['S8'] + 0.05), (83, P['S9'] + 0.05), (88, P['S9'] + DURN['S9'] * 0.7), (103, word_at('S10', 'three')) , (400, 400.0)]
LAND[-2] = (103, LAND[-2][1] + 0.1)
