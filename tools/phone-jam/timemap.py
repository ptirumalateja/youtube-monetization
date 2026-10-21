# timemap.py OUT_JSON : maps output video time to scene time so the scene's beats land on the voiceover.
# The scene is authored on its own 22 s clock; anchors are (scene s, video v) pairs measured from vo_edit.wav
# phrase onsets, joined with a monotone cubic so the camera never jerks at an anchor.
import json, sys, numpy as np
from scipy.interpolate import PchipInterpolator
FPS = 30
A = [(0.0, 0.0), (2.45, 2.15),      # "It sees phones."
     (6.2, 5.75),                   # "When the phones slow down"
     (7.55, 7.73),                  # "the road turns red."
     (9.6, 9.45),                   # "But in 2020, an artist in Berlin" over the red block (held breath)
     (10.72, 11.95),                # reveal hit on "pulled 99 phones in a wagon"
     (11.4, 12.5), (14.3, 15.35),   # close-up through "down an empty street."
     (15.2, 15.9),                  # map view: "Google Maps saw a traffic jam..."
     (16.4, 17.6),                  # new route draws on "and sent drivers around it."
     (18.6, 19.5), (19.0, 19.74),   # "The jam was made of phones."
     (22.0, 22.0)]                  # loop
s, v = np.array(A).T
v2s = PchipInterpolator(v, s); s2v = PchipInterpolator(s, v)
VDUR = v[-1]; n = int(round(VDUR * FPS))
ss = np.linspace(0, s[-1], 2201)
json.dump({'fps': FPS, 'vdur': n / FPS, 'frames': v2s(np.arange(n) / FPS).tolist(), 's': ss.tolist(), 'v': s2v(ss).tolist()}, open(sys.argv[1], 'w'))
print('video duration', n / FPS, 'frames', n)
