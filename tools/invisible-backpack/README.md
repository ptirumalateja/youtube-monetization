# The Invisible Backpack (Part 1 of 2): build

18 s, 1080x1920, 30 fps, wordless. three.js `renderAt(t)` scene, Playwright + SwiftShader frames, PIL overlay, numpy sound (no samples).
Shared look for Part 2: `storyboards/invisible-backpack/style-sheet.md`. Publish copy: `publish-copy/invisible-backpack.md`.

| File | What it does |
|---|---|
| `scene.js`, `index.html` | the scene: walk, x-ray reveal, inventory orbit, bag off, sit, build, rise, hero shot. Timing lives in `timeline.json` and the cycle math at the top of `scene.js` |
| `render.cjs` | `stills` (review stills, `TIMES=` to pick), `probe` (screen positions at `TIMES=`), `meta` (per-frame overlay data + event times, asserts the step counter is monotonic), `frames W N` (worker W of N) |
| `overlay.py` | text layer (hook, title, blurred-to-sharp rock labels, ROCK → STEP counter, captions, end lines) + mux; `--silent` writes the music-ready cut |
| `sound.py` | heartbeat, breathing, footsteps, x-ray shimmer, focus ticks, thud, clinks (D major, rising), hit at rock 5, piano chord at 15.0 s, wind; about -15 LUFS |

## Rebuild
```
cd tools/invisible-backpack && npm install
node render.cjs meta                                      # output/meta.json
for w in 0 1 2 3; do SUB=3 node render.cjs frames $w 4 & done; wait   # 540 frames, about 15 min on 4 CPUs
python3 sound.py                                          # output/sound.wav
python3 overlay.py invisible-backpack_master.mp4
python3 overlay.py invisible-backpack_music-ready.mp4 --silent
```
The CRF 18 master is about 130 MB (grain); make a share copy for chat with a 2-pass 10.5 Mb/s encode (about 24 MB).

## Shot plan (as built)
| Time (s) | Shot |
|---|---|
| 0-2.0 | 3/4 rear tracking, low: he walks bent, dust at each step; 3 blue stickmen stroll ahead |
| 2.0-4.0 | 16% flash, cyan x-ray for 0.45 s, the glass backpack with 7 glowing rocks; camera stops and eases to frame the bag |
| 4.0-7.0 | close orbit around the bag; each rock turns and brightens, its label sharpens (4.15 s + 0.4 s each) |
| 7.0-8.45 | front low: he looks up, shrugs the straps, the bag drops behind him (thud 8.0, dust, shake) |
| 8.45-9.0 | reverse 3/4 low: he sits beside the bag; the crowd walks on, glancing back |
| 9.0-12.0 | side / high-angle cuts every 0.8 s: rock 1 out of the bag by hand, rocks 2-3 float up to his hands; each grows into a step (shake 0.2) and he steps on (clink) |
| 12.0-15.0 | fast pull-back to wide: rocks 4-7, the bag empties, the crowd has walked back and stands below looking up; hit at 12.99 |
| 15.0-18.0 | low-angle hero shot: lamp kindles, wind, crescent moon; camera locked from 16.8 s (end-frame hold) |
