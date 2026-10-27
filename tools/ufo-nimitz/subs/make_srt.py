"""English / Hindi / Telugu SRTs timed to the English narration.
python3 subs/make_srt.py -> subs/en.srt, hi.srt, te.srt
Each beat's cues are spread over its vo/<beat>.wav by text length, with every cut snapped to a pause."""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ROOT]
from cues import CUES
from edit import VO

def silences(path):
    err = subprocess.run(['ffmpeg', '-i', path, '-af', 'silencedetect=noise=-36dB:d=0.12', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', err)]
    en = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', err)]
    dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                               capture_output=True, text=True).stdout)
    return list(zip(st, en)), dur

def ts(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f'{h:02}:{m:02}:{s:02},{ms:03}'

def wrap(s, w):
    if len(s) <= w: return s
    sp = [i for i, ch in enumerate(s) if ch == ' ']                # two balanced lines
    cut = min(sp, key=lambda i: abs(i - len(s) / 2))
    return s[:cut] + '\n' + s[cut + 1:]

def spoken_len(s):
    """rough time-weight of a line as read aloud: numbers are said as words, punctuation is a pause"""
    s = re.sub(r'\b(19|20)\d\d\b', 'x' * 17, s)
    s = re.sub(r'[\d,]*\d', lambda m: 'x' * (5 * len(re.sub(r'\D', '', m.group()))), s)
    return len(s) + 3 * len(re.findall(r'[,:;]', s)) + 7 * len(re.findall(r'[.?!]|\.\.\.', s))

timed = []
for k, cues in CUES.items():
    sil, dur = silences(os.path.join(ROOT, 'vo', f'{k}.wav'))
    lens = [spoken_len(c[0]) for c in cues]; tot = sum(lens)
    wants = [dur * sum(lens[:i + 1]) / tot for i in range(len(cues) - 1)]
    # pick one pause per cut, in order, closest to its text-length target; longer pauses (sentence ends) score better
    # where the speech runs on without a pause, a cut may sit right at its target (fixed penalty)
    sil = sorted(sil + [(w, w) for w in wants])
    cost = lambda p, w: 2.5 if p[0] == p[1] else 2 * (((p[0] + p[1]) / 2 - w) ** 2) - 2 * min(p[1] - p[0], .5)
    INF = float('inf'); n, m = len(wants), len(sil)
    best = [[INF] * (m + 1) for _ in range(n + 1)]; back = [[0] * (m + 1) for _ in range(n + 1)]
    best[0] = [0.] * (m + 1)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            for jj in range(i - 1, j):
                if i == 1: v = cost(sil[j - 1], wants[0]) if jj == 0 else INF
                elif jj and sil[jj - 1][1] + .5 < sil[j - 1][0]: v = best[i - 1][jj] + cost(sil[j - 1], wants[i - 1])
                else: v = INF
                if v < best[i][j]: best[i][j], back[i][j] = v, jj
    if n and m >= n:
        j = min(range(n, m + 1), key=lambda j: best[n][j]); cuts = []
        for i in range(n, 0, -1): cuts.append(sil[j - 1]); j = back[i][j]
        cuts.reverse()
    else:
        cuts = [(w, w) for w in wants]
        if n: print('not enough pauses in', k)
    starts = [0.] + [c[1] for c in cuts]; ends = [c[0] for c in cuts] + [dur]
    for c, a, b in zip(cues, starts, ends):
        timed.append((VO[k] + a, VO[k] + b + .25, c))

# keep each cue on screen at least until just before the next one, but never overlapping
for i in range(len(timed) - 1):
    a, b, c = timed[i]; nxt = timed[i + 1][0]
    timed[i] = (a, min(max(b, a + 1.2), nxt - .05), c)

for li, (lang, w) in enumerate([('en', 42), ('hi', 40), ('te', 38)]):
    out = []
    for n, (a, b, c) in enumerate(timed, 1):
        txt = c[li].replace('वॉर डॉट गव स्लैश UFO', 'war.gov/UFO').replace('వార్ డాట్ గవ్ స్లాష్ UFO', 'war.gov/UFO')
        out.append(f'{n}\n{ts(a)} --> {ts(b)}\n{wrap(txt, w)}\n')
    open(os.path.join(HERE, f'{lang}.srt'), 'w', encoding='utf-8').write('\n'.join(out))
    print(lang, len(out), 'cues')
