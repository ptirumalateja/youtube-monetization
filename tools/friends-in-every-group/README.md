# Friends in Every Group (v6, warm café)

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
- `scene.js`: a café booth with a wall, a doorway, pendant bulbs, the table and food. Four friends, each with a colour and one prop:
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
- `overlay.py`: the phone-camera frame and shutter flash on the selfies; the hook "FRIENDS IN / EVERY GROUP"; one quoted caption per friend. The counters are "5 MIN AWAY" ticking to "47 MIN LATE" and "PHOTO #1" to "#47". Each friend's number disc sits beside the head, never on the face. The end card is "WHICH ONE ARE YOU? / COMMENT 1-4".
- `mix.py`: plates and glasses clinking from frame 0, laughs, a soft camera shutter on every flash, the door, the bell and footsteps, minute ticks and a bonk at 47, fork taps and crunches, the bill thud, a ringtone and a wah-wah, number pops and a bright chord on the end card. The café murmur sits under everything. There are no whooshes.
