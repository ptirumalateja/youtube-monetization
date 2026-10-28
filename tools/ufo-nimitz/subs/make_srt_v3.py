"""English SRT for the final cut (v3, black-triangle cold open). python3 subs/make_srt_v3.py -> subs/en_v3.srt
Text per beat is what was recorded (v1 beats from cues.py, new beats listed here). Each beat is split into cues of at most
two lines, then every cut is snapped to a pause in vo/<beat>.wav, as in make_srt.py."""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path[:0] = [HERE, ROOT]; os.chdir(ROOT)
from cues import CUES
from timeline import T, ORDER
from make_srt_lib import silences, ts, wrap, spoken_len, snap_cuts

NEW = {
 'c01': "Two government documents describe the same sighting. Federal agents, at a sensitive site in the western United States, see a matte black triangle, up to fifteen feet across. It rises above a ridge. Hovers. Then drops into a canyon. No sound. No exhaust.",
 'c02': "The first document is a memo from AARO, the Pentagon's UFO office. It says the object was in view for more than thirty seconds. The second is an FBI write-up. It says about three, and that the object looked most like a drone. Both are official. They can't both be right.",
 'c03': "A search the next morning found nothing. And nobody filmed it. Both files came out on October 23rd, in the Pentagon's seventh batch of UFO files. To see why a case with no video still gets taken seriously, you have to go back twenty-two years. To the footage everyone has seen... and what it doesn't show.",
 'c04': "It's known as FLIR1. It was recorded by a weapons systems officer named Chad Underwood, with an infrared camera locked onto a distant target. At the end, the object slips out of frame. Some see a sudden burst of speed. Skeptics say the camera simply lost its lock. The footage alone can't settle it.",
 'c05': "Sixty miles in under a minute. That's a mile every second. At least thirty-six hundred miles an hour. But there's a catch. That number came over the radio, from the ship's radar. There's no recording of it you can watch. So it's only as good as the radar track. Which makes the radar either the strongest evidence in this case... or the first thing to question.",
 'c06': "Here's what sets this case apart. Two jets. Two people in each. A pilot up front, and behind them a weapons systems officer, whose whole job is working the radar and sensors. Fravor's was Jim Slaight. Dietrich's has never been publicly named. Fravor says all four of them looked down and saw it. For about five minutes, from two cockpits, at different angles. Four trained people can still be wrong together. That happens. But they weren't the only ones looking.",
 'c12': "On the Princeton, the radar operator who sent them there was Senior Chief Kevin Day. He says that for days, he'd been watching groups of objects on his radar, sometimes ten at a time. Some, he says, dropped from twenty-eight thousand feet toward the sea in under a second. Eyes in two cockpits, and a warship's radar, all on the same thing. The one piece nobody outside the Navy has seen... is the raw radar data.",
 'c07': "So what does a video prove on its own? There's another Navy clip that shows exactly why that question matters.",
 'c08': "So a video can fool you. The Nimitz case never rested on one. It rests on people and radar. The famous video came later, and shows something else.",
 'c09': "In February 2026, the President directed the Pentagon and other agencies to start releasing their files on UFOs. Since May, the Pentagon has published seven batches, at war dot gov slash UFO. The latest, on October 23rd, was documents only. No new video.",
 'c10': "Which brings us back to that black triangle. The AARO memo says more than thirty seconds. The FBI says about three. Two reports from the same government, about the same sighting. And no footage to check them against.",
 'c11': "A Tic Tac over the Pacific. A black triangle over a ridge. Different decades, same problem. Enough to take seriously. Not enough to close.",
}
def beat_text(k):
    if k in NEW: return NEW[k]
    if k == 'b03s': return ' '.join(c[0] for c in CUES['b03'][:-1])
    return ' '.join(c[0] for c in CUES[k])

def split_cues(text, maxlen=84):
    sents = re.findall(r'.+?(?:\.\.\.|[.?!])(?:\s+|$)', text + ' ')
    sents = [s.strip() for s in sents if s.strip()]
    out = []
    for s in sents:                                   # break long sentences at a comma near the middle
        if len(s) > maxlen:
            cs = [m.end() for m in re.finditer(r',\s', s)]
            if cs:
                c = min(cs, key=lambda i: abs(i - len(s) / 2)); out += [s[:c].strip(), s[c:].strip()]; continue
        out.append(s)
    merged = []                                       # join short neighbours so cues are not tiny
    for s in out:
        if merged and len(merged[-1]) + 1 + len(s) <= maxlen and len(merged[-1]) < 40: merged[-1] += ' ' + s
        else: merged.append(s)
    return merged

timed = []
for k, _ in ORDER:
    cues = split_cues(beat_text(k).replace('war dot gov slash UFO', 'war.gov/UFO'))
    sil, dur = silences(os.path.join(ROOT, 'vo', f'{k}.wav'))
    lens = [spoken_len(c) for c in cues]; tot = sum(lens)
    wants = [dur * sum(lens[:i + 1]) / tot for i in range(len(cues) - 1)]
    cuts = snap_cuts(sil, wants)
    starts = [0.] + [c[1] for c in cuts]; ends = [c[0] for c in cuts] + [dur]
    for c, a, b in zip(cues, starts, ends): timed.append((T[k] + a, T[k] + b + .25, c))
for i in range(len(timed) - 1):
    a, b, c = timed[i]; nxt = timed[i + 1][0]
    timed[i] = (a, min(max(b, a + 1.2), nxt - .05), c)
out = [f'{n}\n{ts(a)} --> {ts(b)}\n{wrap(c, 42)}\n' for n, (a, b, c) in enumerate(timed, 1)]
open(os.path.join(HERE, 'en_v3.srt'), 'w', encoding='utf-8').write('\n'.join(out))
print(len(out), 'cues, last ends', ts(timed[-1][1]))
