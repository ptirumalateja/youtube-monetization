# Friends in Every Group (v7, warm café, round table)

14.0 s, 1080x1920, 30 fps. Copy: `publish-copy/friends-in-every-group.md`. This is an owner-approved departure from the Slow Light Dark void look: a warm café, four colourful friends, and English captions only. The rig, stage and text and sound kits are reused from `../slow-light-dark-common/`, and `sld.js` is a copy of the kit file. The v1-v5 dark-void build is kept as `*_v5.*` for reference. It is not runnable as-is, because `scene_v5.js` fetches `./timeline.json`.

```
cd tools/friends-in-every-group && npm install                  # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                         # meta.json: shot per frame + head positions through the camera (for the number discs)
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 420 frames
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=0.5,2.8,5.8,7.8,10.4,12.4 node render.cjs stills
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver              # master (-15 LUFS, true peak checked after AAC) + _music-ready (silent)
```

- `timeline.json`: the single source of timing. It holds the hard-cut shot list (selfie, late, photo, hungry, pays, selfieEnd), every action time, the captions and the review times. `scene.js`, `overlay.py` and `mix.py` all read it, so each sound effect lands on its action.
- `scene.js`: a round table inside a curved, horseshoe-shaped booth, open to the camera, with a café wall, a doorway, pendant bulbs and food. Poses are written in each friend's "bench frame": the frame they would have on a straight bench, facing the camera. `toW()` moves that frame onto their seat on the curve and turns them 60% of the way toward the table centre, so faces stay toward the camera. Walk paths are written in world space. Four friends, each with a colour and one prop:
  1. LATE: blue, headphones.
  2. PHOTO: yellow, red cap.
  3. HUNGRY: pink, hair bun.
  4. PAYS: green, glasses.
- What each shot does in `scene.js`:
  - #1 walks in from the door on the phone and sits with a sorry wave.
  - #2 keeps shooting while the others are bored.
  - #3 says no and then eats from three plates.
  - #4's phone rings when the bill lands, and he walks out.
  - Selfie bookends with a handheld wobble.
  - Motion blur never crosses a cut, because `renderAt` gets the shot bounds.
- `overlay.py`: the late one's "omw!! 5 min away" group-chat message dropping in at 0.15 s (the frame-0 gag); the phone-camera frame and shutter flash on the selfies; the hook "FRIENDS IN / EVERY GROUP"; one quoted caption per friend. The counters are "5 MIN AWAY" ticking to "47 MIN LATE" and "PHOTO #1" to "#47". Each friend's number disc sits beside the head, never on the face. The end card is "WHICH ONE ARE YOU? / COMMENT 1-4".
- `mix.py`: a soft ping for the message, plates and glasses clinking from frame 0, laughs, a soft camera shutter on every flash, the door, the bell and footsteps, minute ticks and a bonk at 47, fork taps and crunches, the bill thud, a ringtone and a wah-wah, number pops and a bright chord on the end card. The café murmur sits under everything. There are no whooshes.
