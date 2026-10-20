# The Ball That Never Falls (20 s, no voiceover): spec

Source concept: `psychological_topics.md` #1 (top pick), built as a seamless loop. Dark, psychological, anxiety-paced; all visuals in three.js (`tools/ball-never-falls/`), sound is synthesised in numpy (no samples, no credits, no AI audio tools needed).

## Idea
A cream ball creeps toward the rim of a bottomless pit under a shrinking spotlight, a heartbeat accelerating with it. After a held breath it lurches, the camera swings, and the pit is revealed as a **flat anamorphic painting on the floor**. The ball was resting on solid ground the whole time. The camera glides back, the illusion re-forms and the ball rolls back to frame 0, so the loop is continuous.

## How the illusion works (why it is real, not a gimmick)
The floor is one shader. For every floor point P it ray-casts a virtual shaft (rim 3.2 x 3.2, depth 9, teal grid on the walls, depth fade) from a viewpoint V and paints what that ray would see. From V it is a true pit. V rides the dolly path, so the illusion holds while the camera creeps in, then V stays on that path while the camera leaves it: the grid shears into a flat decal. The ball is a real sphere at floor height; the shadow and contact darkening are applied only outside the pit, so nothing betrays it.

## Timeline
| Time | Beat |
|---|---|
| 0.0 | Hit on frame 0 (ball already on the rim, stopwatch running, hook types: THIS BALL IS ABOUT TO FALL.) |
| 0-9.7 | Ball inches over the rim (centre ends 0.4 m past it), cone narrows, heartbeat 54 -> 92 bpm, creaks, rising shimmer, slow dolly in |
| 9.7-10.5 | Held breath: heartbeat and bed drop out |
| 10.5 | Lurch (light stutter, small thud) |
| 11.3 | Reveal hit (biggest), camera swings out and up; 10% max flash |
| 12.7 | Label flips ON THE EDGE -> ON THE FLOOR; captions THERE IS NO HOLE. / IT IS PAINTED ON THE FLOOR. |
| 15.4-18.4 | Camera returns, illusion re-forms, ball rolls back, small landing hit at 18.4; end line YOUR BRAIN FILLED IN THE DEPTH. |
| 19.0-20.0 | Rising tone and crackle into frame 0; all text clears by 19.8 |

Single source of truth for timings: `tools/ball-never-falls/timeline.json` (read by the scene, overlay and mixer).

## Playbook compliance
Frame 0 moving with a hit; hook done by 1.9 s; held-breath silence before the biggest hit; hits only at 0 / lurch / reveal / landing; wordless, no voiceover; monotonic stopwatch (asserted in `overlay.py`); palette charcoal/navy, cream text, teal grid, gold ball dot, red only on the label chip; last frame matches frame 0; tagged "optical illusion / anamorphic floor painting". Visuals are 3D-rendered, no AI-generated imagery.

## Rebuild
```
cd tools/ball-never-falls && ln -s <dir with three@0.170.0 and playwright-core>/node_modules node_modules
python3 -m http.server 8777 &
for o in 0 1 2 3; do node render.js 720 1280 $FRAMES $o 600 4 & done; wait      # 600 frames, ~25 min on 4 CPUs (SwiftShader)
FRAMES=$FRAMES OUT=ball_never_falls.mp4 ./build.sh
```
`node shot.js W H dir t...` renders test stills. Frames and videos are not committed.
