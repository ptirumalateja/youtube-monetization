# Friends in Every Group (Slow Light Dark)

12.0 s, 1080x1920, 30 fps. Copy: `publish-copy/friends-in-every-group.md`. Look: `storyboards/slow-light-dark/style-sheet.md` (lamp, void, rig, palette), with two owner-approved departures for this format: simple faces, and a gold ki aura / full-body glow on the friend being named. `sld.js` is a copy of `../slow-light-dark-common/sld.js`; Python imports `sld_text` / `sld_sound` from `../slow-light-dark-common/`.

```
cd tools/friends-in-every-group && npm install                  # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                         # meta.json: per-frame number tags (head positions through the camera; tags only ever add up)
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 360 frames
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=1.9,3.3,5.9,9.5 node render.cjs stills
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver              # master (-15 LUFS, true peak checked after AAC) + _music-ready (silent, for a trending sound in-app)
```

- `timeline.json`: hook "FRIENDS IN EVERY GROUP" (0-1.05 s), six beats of 1.3 s (late, photo, laugh, asleep, food, never pays), end card "WHICH ONE ARE YOU? / COMMENT YOUR NUMBER" at 8.9 s.
- `scene.js`: table along z, three seats a side, camera high at the near end. Each seat has an idle (talk, lean, laugh) and its beat action; the named friend glows gold with rising flame particles while the others dim toward slate and turn to look at them; faces are canvas decals cheated two-thirds toward the camera; props: the red bill (the one red object), the photographer's phone and flash, the stolen fry.
- `overlay.py`: hook, captions, numbered tags over heads (the named one is bigger, red-ringed), shake lines on the laugher, Z z z on the sleeper, end card.
- `mix.py`: six chattering voices, a ki power-up whoosh per beat, a rising pop as each number lands, footsteps and chair, camera shutter, a big laugh, snoring, fry crunch, the bill sliding, a warm low hit on the end card.
