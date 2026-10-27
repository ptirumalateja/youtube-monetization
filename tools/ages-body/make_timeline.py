"""Build film_timeline.json: beat start/duration from the narration clips (estimated when a clip is missing).
Usage: python3 make_timeline.py [narration_dir]
"""
import json, os, subprocess, sys

NARR = sys.argv[1] if len(sys.argv) > 1 else '/mnt/project-files/ages-1-to-100/narration'
WORDS = {  # words per beat, used only when the mp3 is missing
    'age25': 52, 'rehook': 24, 'age80': 45, 'age100': 40, 'tree': 18,
}
# id, mp3 name, lead-in before VO, tail after VO
BEATS = [
    ('hook',   'beat01_hook.mp3',    0.35, 0.7),
    ('lineup', 'beat02_promise.mp3', 0.5, 1.0),
    ('age1',   'beat03_age1.mp3',    0.6, 1.2),
    ('age35',  'beat04_age3_5.mp3',  0.6, 1.2),
    ('age10',  'beat05_age10.mp3',   0.6, 1.2),
    ('age18',  'beat06_age18.mp3',   0.6, 1.2),
    ('age25',  'beat07_age25.mp3',   0.6, 1.2),
    ('age30',  'beat08_age30.mp3',   0.6, 1.4),
    ('rehook', 'beat09_rehook.mp3',  0.8, 1.6),
    ('age40',  'beat10_age40.mp3',   0.6, 1.2),
    ('age50',  'beat11_age50.mp3',   0.6, 1.2),
    ('age60',  'beat12_age60.mp3',   0.6, 1.2),
    ('age70',  'beat13_age70.mp3',   0.6, 1.2),
    ('age80',  'beat14_age80.mp3',   0.6, 1.2),
    ('age100', 'beat15_age100.mp3',  0.6, 1.6),
    ('tree',   'beat16_close.mp3',   1.2, 3.4),
    ('end',    'beat17_cta.mp3',     0.8, 6.0),
]

def dur(path):
    out = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path], capture_output=True, text=True)
    return float(out.stdout.strip())

t = 0.0
tl = []
for bid, mp3, lead, tail in BEATS:
    p = os.path.join(NARR, mp3)
    have = os.path.exists(p)
    vo = dur(p) if have else WORDS.get(bid, 45) * 0.36 + 0.8
    d = lead + vo + tail
    tl.append(dict(id=bid, start=round(t, 3), dur=round(d, 3), vo=mp3 if have else None, vo_dur=round(vo, 3), lead=lead, estimated=not have))
    t += d
json.dump(dict(total=round(t, 3), fps=24, beats=tl), open(os.path.join(os.path.dirname(__file__), 'film_timeline.json'), 'w'), indent=1)
print(f'total {t:.1f}s ({t/60:.2f} min)')
for b in tl: print(f"{b['start']:7.1f} {b['dur']:5.1f} {b['id']:7s} {'EST' if b['estimated'] else 'ok '}")
