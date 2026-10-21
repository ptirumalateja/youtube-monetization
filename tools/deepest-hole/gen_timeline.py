# Writes timeline.json for "The Deepest Hole": stroke times/depths for the well, the stops of the log-zoom, events and text.
# Scene (index.html), overlay (overlay.py) and sound (mix.py) all read this one file. usage: python3 gen_timeline.py
import json
T = 22.0
R = 6371000.0                                     # mean Earth radius (m)
strokes = [[0.00, 0.10], [0.62, 0.24], [1.24, 0.40]]          # surface
n = 12; t = 2.05
for i in range(n):                                # time-lapse: down to the water table at 10.0 m
    d = 0.40 + (10.0 - 0.40) * ((i + 1) / n) ** 1.05
    strokes.append([round(t, 3), round(d, 2)]); t += 0.27 - 0.03 * i / (n - 1)
for a, b in zip(strokes, strokes[1:]): assert b[0] > a[0] and b[1] > a[1]
# holes, placed side by side (x in m), real depths. drill = [t0, t1] while the line grows to full depth (the counter follows it)
holes = {
    'well':   {'x': 0.0,     'w': 1.0,  'depth': 10.0},
    'wood':   {'x': 14.0,    'w': 1.8,  'depth': 391.6, 'drill': [6.0, 8.0]},     # Woodingdean Water Well, hand-dug 1858-1862
    'mine':   {'x': -320.0,  'w': 6.0,  'depth': 4000.0, 'drill': [8.9, 10.9]},  # Mponeng gold mine, about 4 km
    'kola':   {'x': 1500.0,  'w': 0.23, 'depth': 12262.0, 'drill': [11.6, 13.9]},# Kola Superdeep Borehole SG-3, 1989
}
# camera stops: [time, frame height S (m), centre x, centre y]; zoom between stops is logarithmic and anchored
cam = [[0.0, 5.0, 0.10, 0.70], [1.9, 5.0, 0.10, 0.70], [2.6, 4.6, 0.10, None], [5.3, 4.8, 0.15, -8.7], [5.9, 4.8, 0.15, -8.7],
       [8.0, 720.0, 8.0, -330.0], [8.7, 760.0, 8.0, -340.0], [10.9, 7000.0, -180.0, -2900.0], [11.5, 7300.0, -150.0, -3000.0],
       [13.9, 17500.0, 650.0, -8300.0], [14.6, 17800.0, 650.0, -8400.0], [17.4, 1.9e7, 0.0, -R + 2.4e6], [19.9, 1.9e7, 0.0, -R + 2.4e6],
       [21.6, 5.0, 0.10, 0.70], [22.0, 5.0, 0.10, 0.70]]
TL = {
    'T': T, 'fps': 30, 'R': R, 'water': 10.0, 'strokes': strokes, 'holes': holes, 'cam': cam,
    'events': {
        'dive': [1.9, 2.6], 'water_hit': strokes[-1][0], 'held': [13.95, 14.6], 'reveal': 14.6,
        'earth_hold': [17.4, 19.9], 'reset': 18.0, 'plunge': [19.9, 21.6],
    },
    'text': {
        'tag': {'s': 'SLOW LIGHT', 't0': 0.0, 't1': 0.3, 'out': [19.6, 19.9]},
        'hook': {'s': 'HOW DEEP HAVE WE EVER DUG?', 't0': 0.0, 't1': 1.0, 'out': [2.7, 3.1]},
        'caption': {'s': 'OUR DEEPEST HOLE IS 0.2% OF THE WAY TO THE CENTRE.', 't0': 15.3, 't1': 16.4, 'out': [19.4, 19.8]},
    },
    # chips: name (red) + one cream line, anchored to a point on the face
    'chips': [
        {'name': 'A WELL', 'line': '10 M · DUG BY HAND', 'at': [0.55, -10.0], 't': [strokes[-1][0] + 0.15, 6.2]},
        {'name': 'DEEPEST HAND-DUG WELL', 'line': '392 M · ENGLAND, 1862', 'at': [14.0, -391.6], 't': [7.6, 9.4]},
        {'name': 'DEEPEST MINE', 'line': 'ABOUT 4 KM · SOUTH AFRICA', 'at': [-320.0, -4000.0], 't': [10.5, 12.1]},
        {'name': 'DEEPEST HOLE EVER', 'line': '12,262 M · 23 CM WIDE · 1989', 'at': [1500.0, -12262.0], 't': [13.5, 15.2]},
        {'name': 'ALL OF THEM ARE HERE', 'line': 'CENTRE: 6,371 KM DOWN', 'at': [0.0, 0.0], 't': [16.2, 19.6]},
    ],
}
json.dump(TL, open('timeline.json', 'w'), indent=1)
print(len(strokes), 'strokes; last', strokes[-1])
