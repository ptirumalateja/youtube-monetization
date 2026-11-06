# Friends in Every Group (Slow Light Dark)

15.0 s, 1080x1920, 30 fps. Copy: `publish-copy/friends-in-every-group.md`. Look: `storyboards/slow-light-dark/style-sheet.md` (lamp, void, rig, palette), with one owner-approved departure for this format: simple faces. The friend being named is highlighted by staying bright cream while the other five dim (a gold aura was tried and retired: too much). `sld.js` is a copy of `../slow-light-dark-common/sld.js`; Python imports `sld_text` / `sld_sound` from `../slow-light-dark-common/`.

```
cd tools/friends-in-every-group && npm install                  # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                         # meta.json: per-frame number tags (head positions through the camera; tags only ever add up)
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 450 frames
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=1.9,3.3,5.9,9.5 node render.cjs stills
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver              # master (-15 LUFS, true peak checked after AAC) + _music-ready (silent, for a trending sound in-app)
```

- `timeline.json`: hook "FRIENDS IN EVERY GROUP" (0-1.25 s), six beats of 1.9 s from 1.2 s (late, photo, laugh, asleep, food, never pays; 4-5-6 chain into one gag: the sleeper is robbed and handed the bill), end card "WHICH ONE ARE YOU? / COMMENT YOUR NUMBER" at 12.6 s. The camera glides in toward whoever is being named and back out for the end card.
- `scene.js`: table along z, three seats a side, camera high at the near end. Each seat has an idle (talk, lean, laugh) and its beat action; the named friend stays bright while the others dim toward slate and turn to look at them (the flame aura code is kept but switched off); faces are canvas decals cheated two-thirds toward the camera; props: the red bill (the one red object), the photographer's phone and flash, the stolen fry.
- `overlay.py`: hook, captions, numbered tags over heads (the named one is bigger, red-ringed), shake lines on the laugher, Z z z on the sleeper, end card.
- `mix.py`: six chattering voices (the per-beat power-up whoosh was removed), a rising pop as each number lands, footsteps and chair, camera shutter, a big laugh, snoring, fry crunch, the bill sliding, a warm low hit on the end card.
