# The Moon Never Loops (Slow Light, 21 s, wordless, loops)

The usual loopy drawing of the Moon's path around the Sun shrinks to true scale (Moon orbit 389× smaller than Earth's) and unwinds into a circle; then a chase camera rides one year with Earth and the Moon: the Moon's track weaves across Earth's 12.4 times and always bends toward the Sun (the Sun pulls the Moon 2.2× harder than Earth). Ends "IT NEVER GOES BACKWARDS." Notes, facts and publish copy: `final-reels/moon-never-loops.md`.

```sh
npm ci
node sound.mjs                                  # output/sound.wav, fully synthesised (no samples, no credits)
node render.cjs --stills                        # review stills + monotonic-counter and convexity checks (TIMES=1,2 to pick times)
RENDER_W=1080 node render.cjs                   # output/moon-never-loops.mp4 (1080x1920 native, 30 fps)
```

On a Mac set `CHROME_PATH` to Chrome and pass `--gpu`; the default is the container's Playwright Chromium with SwiftShader.

- `timeline.json`: duration, shot list, the fact table, the myth orbit size and review times.
- `scene.js`: one three.js scene, 1 unit = 1 million km. Sun = dotted globe of gold latitude rings in a corona (enlarged). Earth's and the Moon's paths are screen-space ribbons evaluated in the vertex shader from the day number, so the Moon's orbit radius can morph from the myth (0.24 AU) to the true 384,400 km on a log curve. Earth and Moon are lit sphere sprites with a minimum screen size. Cameras: top view, a chase camera ahead of Earth looking back down the track, and an oblique overview, joined by log-distance blends.
- `window.convexCheck()` returns the minimum curvature of the true Moon path (in units of Earth's orbital curvature); `render.cjs` refuses to render if it is not positive.
