"""v3 running order (8 min cut, Opening A). Beat start times come from the recorded narration lengths, so a re-recorded
line moves everything after it. edit.py and audio.py both build on T (beat starts) and R (v1 time -> v2 time)."""
import os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))

# (beat, silence before it). v1 gaps are kept inside the reused 2004 sections so their shots still line up.
ORDER = [('h01', .35),                                                # 0 hook: the video everybody knows is not the encounter
         ('c04', .5), ('b02', .8),                                    # 1 the video everybody knows
         ('b03s', 1.4), ('b04', .63), ('b05', .82), ('b06', .47),     # 2 November 2004
         ('b07', 1.46), ('c05', 1.44),                                # 3 60 miles in under a minute
         ('c06', 1.2), ('c12', .8),                                   # 4 four aviators, one radar
         ('c07', 1.4), ('b09', 3.6),                                  # 5 Go Fast (3 s of cockpit audio before b09)
         ('c08', .97), ('b11', 1.2), ('c09', .33),                    # 6 the 2026 files ...
         ('c01', .9), ('c02', .6), ('c10', .6),                       #   ... and the black triangle
         ('c11', 1.2), ('b14', 1.2)]                                  # 7 still unidentified
CARD = 2.6                                                            # chapter title card, sits in the gap before its beat
CHAPTERS = {'b03s': ('02', 'NOVEMBER 2004'), 'c06': ('04', 'FOUR AVIATORS · ONE RADAR'),
            'c07': ('05', 'GO FAST'), 'b11': ('06', 'THE 2026 FILES'), 'c11': ('07', 'STILL UNIDENTIFIED')}
EST = {'c06': 30.0}                                                   # until that line is recorded
END_CARD = 16.0                                                       # long enough for YouTube end-screen elements

def _dur(k):
    p = os.path.join(HERE, 'vo', f'{k}.wav')
    if not os.path.exists(p): return EST[k]
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', p],
                                capture_output=True, text=True).stdout)
D = {k: _dur(k) for k, _ in ORDER}
T = {}; _t = 0.
CARD_AT = {}
for k, gap in ORDER:
    if k in CHAPTERS: CARD_AT[k] = round(_t + .5, 2); _t += CARD
    _t += gap; T[k] = round(_t, 2); _t += D[k]
NEXT = {k: (T[ORDER[i + 1][0]] if i + 1 < len(ORDER) else None) for i, (k, _) in enumerate(ORDER)}
NEXT['b14'] = T['b14'] + 22.0
END = round(NEXT['b14'] + END_CARD, 2)
VO = dict(T)

# v1 sections that carry over unchanged: (v1 start, v1 end, beat it is anchored to, that beat's v1 start)
SECT = [(29.2, 52.3, 'b03s', 29.2), (52.3, 74.8, 'b04', 52.3), (74.8, 99.0, 'b05', 74.8),
        (99.0, 120.2, 'b06', 99.0), (120.2, 130.4, 'b07', 120.2), (171.0, 217.2, 'b09', 174.0),
        (233.0, 249.4, 'b11', 233.6), (249.4, 272.4, 'c09', 249.4), (306.2, 336.0, 'b14', 306.2)]
def _sect(t):
    for s in SECT:
        if s[0] <= t < s[1]: return s
    return None
def R(t):
    """v1 timeline time -> v2 time (None if that part of v1 is not used)."""
    s = _sect(t)
    return None if s is None else T[s[2]] + (t - s[3])
def R_end(t):
    """v2 time where the v1 section holding t now has to end (the next beat, or the section's own end)."""
    s = _sect(t); new_end = T[s[2]] + (s[1] - s[3])
    nxt = {'b03s': T['b04'], 'c09': T['c01'], 'b07': T['c05'], 'b14': END}.get(s[2])
    return min(new_end, nxt) if nxt else new_end

if __name__ == '__main__':
    for k, _ in ORDER: print(f'{k:5s} {T[k]:7.2f}  {D[k]:5.2f}' + ('  (est)' if k in EST and not os.path.exists(os.path.join(HERE, 'vo', f'{k}.wav')) else ''))
    print('END', END, f'{int(END // 60)}:{END % 60:04.1f}')
