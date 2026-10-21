# The Moon Never Loops (Slow Light, 21 s, wordless, loops)

Close on Earth and the Moon, pull back to the usual loopy drawing of the Moon's path, unwind it to real scale, then fly beside Earth and the Moon for 12 lunar months: the Sun pulls the Moon harder than Earth does, so its path always curves toward the Sun. Ends "IT NEVER GOES BACKWARDS." Notes, facts and publish copy: `final-reels/moon-never-loops.md`.

```sh
npm ci
node sound.mjs                                  # output/sound.wav, fully synthesised (no samples, no credits)
node render.cjs --stills                        # review stills + monotonic-counter and convexity checks (TIMES=1,2 to pick times)
RENDER_W=1080 node render.cjs                   # output/moon-never-loops.mp4 (1080x1920 native, 30 fps); python3 gen_moon.py rebuilds the Moon textures
```

On a Mac set `CHROME_PATH` to Chrome and pass `--gpu`; the default is the container's Playwright Chromium with SwiftShader.

- `timeline.json`: duration, shot list, the fact table, the myth orbit size and review times.
- `scene.js` (v2, cinematic): one three.js scene, 1 unit = 1 million km, orbits true, bodies enlarged. Earth uses NASA Blue Marble day, night-lights and cloud maps (`assets/`, from the MIT `three-globe` package's example images) with ocean glint and an atmosphere shell; the Moon uses procedural textures from `gen_moon.py`; the Sun is an animated granulation shader with a corona. Paths are screen-space ribbons evaluated in the vertex shader (Earth teal, Moon gold, the usual loopy drawing as cream dashes whose radius morphs to real scale). The clock runs exactly 12 synodic months so the Moon's phase matches at the loop. Shots: Earth close-up, pull back to the drawing, unwind, dive, sunward ride with pull beams and a moon-phase month row, crane up, hero orbit, dive home.
- `window.convexCheck()` returns the minimum curvature of the true Moon path (in units of Earth's orbital curvature); `render.cjs` refuses to render if it is not positive.
