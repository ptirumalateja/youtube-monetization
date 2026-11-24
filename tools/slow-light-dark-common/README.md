# slow-light-dark-common

Shared look for the Slow Light Dark reels (pilot: `tools/chain-never-locked/`). Style sheet: `storyboards/slow-light-dark/style-sheet.md`.

| File | What |
|---|---|
| `sld.js` | `createStage({W,H})`: renderer, void, gold lamp + beam + motes, soft-mirror floor, bloom/grade, motion-blurred `renderAt`. `createRig(scene)`: stickman rig (poses, IK, gait, `setAlpha` fades). Palette, rim/dust shader helpers, IRON material, glow sprite. |
| `demo.js` + `index.html` | Starter scene (seated cream hero, red object, a slate stranger fading in and out). Copy to start a reel. |
| `render.cjs` | Headless render: `stills` (TIMES=...) and `frames WORKER N DURATION FPS`. Uses the global `playwright`. |
| `sld_text.py` | Text layer: tracked JetBrains Mono caps, halo, SLOW LIGHT watermark. |
| `sld_sound.py` | numpy sound kit: filters, clank/rattle/scrape/breath/thud/creak/sub_boom, room bed + lamp hum + drone, `finish`, `master_to_mp4` (-15 LUFS, true peak checked after AAC). |

```
cd tools/slow-light-dark-common && npm install
OUT=/tmp/x W=540 H=960 SUB=1 TIMES=0.5,2 node render.cjs stills
```
To start a reel: copy this folder to `tools/<slug>/` (or copy `sld.js`, `render.cjs`, `index.html`, `package.json` next to your scene) and import `./sld.js`. The page server only serves files inside the reel folder, so a `../` import will not resolve. If you change a look value, change it here too and tell the other reel sessions.
