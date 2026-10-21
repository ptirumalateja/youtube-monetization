# Proton Laps: One Minute (Slow Light, 31 s, wordless, loops)

A proton at LHC speed (99.999999% of light) laps Earth's equator 7.48 times a second. This cut plays one full minute of it in 20 s of clip: playback ramps from x1 (laps countable) to x5, and the trail is a tight glowing coil and each orbit tilts and turns a little, so the 448 laps build a solid belt of spirals around a real Earth. Then the camera pulls back to the Moon, to scale: 17,987,547 km is 46 trips to the Moon.

```sh
npm ci
node fetch_textures.mjs           # NASA Blue Marble + Black Marble into tex/ (public domain)
python3 make_clouds.py            # procedural cloud layer -> tex/clouds.png
node sound.mjs                    # output/sound.wav, fully synthesised
node render.cjs --stills          # review stills + monotonic-counter check (TIMES=1,2 to pick times)
node render.cjs --frames          # output/frames/*.jpg, resumable (FROM/TO env for parallel slices)
node render.cjs                   # encode output/proton-laps-one-minute.mp4 (1080x1920, 30 fps)
```

Renders headless on Linux with SwiftShader (no GPU needed); `CHROME_PATH` overrides the Chromium path, `--gpu` uses ANGLE Metal on a Mac.

- `timeline.json`: duration, shot list, the minute's start/length and ramp, and the fact table.
- `scene.js`: one three.js scene in Earth units (radius 10). Earth shader: day texture lit by the Sun, city lights on the night side, cloud layer with soft shadows, limb haze. The lap path is one precomputed line (20 coil turns per lap, 448.85 laps, drawn three times one pixel apart for thickness) plus a soft point haze along the orbit; the shader shows it only up to the current lap and colours by age (white-gold head, orange, cooling to red). The Moon (procedural) sits at its real mean distance, 384,400 km. A second "glow" pass renders only the bright parts and is blurred on top.
- Time map: clip time u in [0, 20] -> real seconds s = u + 0.1 u^2 (60 s at u = 20), so the counters are exact at every frame.
