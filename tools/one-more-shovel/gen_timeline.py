# Writes timeline.json: shovel impact times + shaft depth after each stroke, story events and on-screen text.
# Scene (index.html), overlay (overlay.py) and sound (mix.py) all read this one file. usage: python3 gen_timeline.py
import json

T = 14.0
WATER = 10.0                                      # water table depth (m); he stops at 9.8 m, one shovel short
strokes = [[0.00, 0.10], [0.62, 0.22], [1.22, 0.36], [1.78, 0.55]]   # surface: slow, deliberate
n = 15; t = 2.15
for i in range(n):                                # time-lapse montage: strokes speed up, depth climbs to 8.0 m
    d = 0.55 + (8.0 - 0.55) * ((i + 1) / n) ** 1.08
    strokes.append([round(t, 3), round(d, 2)]); t += 0.30 - 0.05 * i / (n - 1)
strokes += [[6.55, 8.55], [7.12, 9.05], [7.74, 9.45], [8.40, 9.80]]  # fatigue: each stroke slower, each gain smaller
for a, b in zip(strokes, strokes[1:]): assert b[0] > a[0] and b[1] > a[1]   # monotonic depth counter

TL = {
    'T': T, 'fps': 30, 'water': WATER, 'strokes': strokes,
    'events': {
        'last_stroke': strokes[-1][0],
        'rest': [8.62, 8.92],         # straightens, leans on the shovel
        'look_up': [8.92, 9.30],      # looks up at the circle of sky
        'drop': [9.18, 9.46],         # lets the shovel fall; it clatters against the wall at 9.46
        'reach': [9.30, 9.70],        # hands to the rope
        'silence': [9.46, 9.80],      # held breath
        'hit_reveal': 9.80,           # he starts climbing; the 20 CM bracket lands
        'push': [9.80, 10.90],        # camera pushes in on the gap
        'seep': [10.4, 11.8],         # water beads up through the floor he left
        'whoosh': [11.90, 12.80],     # camera rides the shaft back to the surface
        'out': 12.40,                 # he is out of the shaft, walking away
    },
    'text': {
        'tag': {'s': 'SLOW LIGHT', 't0': 0.0, 't1': 0.3, 'out': [13.75, 13.95]},
        'hook': {'s': "HE'S DIGGING FOR WATER.", 't0': 0.0, 't1': 0.85, 'out': [2.5, 2.9]},
        'reveal': {'s': 'THE WATER WAS ONE SHOVEL AWAY.', 't0': 9.95, 't1': 10.65, 'out': [11.75, 12.05]},
        'end': {'s': 'KEEP DIGGING.', 't0': 12.75, 't1': 13.2, 'out': [13.75, 13.95]},
        'chip': {'s': '20 CM', 't0': 9.86, 't1': 10.0, 'out': [11.75, 11.95]},
    },
}
json.dump(TL, open('timeline.json', 'w'), indent=1)
print(len(strokes), 'strokes; last', strokes[-1])
