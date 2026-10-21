# The Moon Never Loops (v1)

- **Video:** `/mnt/project-files/final-reels/moon-never-loops.mp4` (not in git). 21.0 s, 1080x1920 rendered natively, 30 fps, loops, wordless (no voiceover).
- **Brief:** reel #3 in `ref-remakes-plan.md` (ref: "Cosmic Geometry - The Moon's Secret Path", a 33 s green wireframe that draws the Moon's path around the Sun as loops). We take the topic only and correct the ref's exaggerated loops.
- **Build:** `tools/moon-never-loops/` (three.js r0.170 `renderAt(t)`, headless Chromium, ffmpeg). Rebuild: `npm ci && node sound.mjs && RENDER_W=1080 node render.cjs` (add `--stills` for review frames). The render script asserts the counters are monotonic and that the true Moon path curves toward the Sun at every point.

## Concept
Most diagrams draw the Moon's path around the Sun as a spirograph of loops. Shrink the Moon's orbit to its true size (389 times smaller than Earth's) and the loops unwind: the Moon just rides along Earth's orbit, weaving across it 12.4 times a year. Because the Sun pulls the Moon 2.2 times harder than Earth does, the path always bends toward the Sun. It never loops and never goes backwards.

## Shot plan
| Time | Shot |
|---|---|
| 0-2.4 | Top view of a new Sun design (a dotted globe of gold latitude rings in a soft corona). The loopy "usual drawing" (Moon orbit shown at 0.24 AU) is traced by a bright head, one year in 2.4 s. Hook typed: "THE MOON'S PATH / AROUND THE SUN?", red chip "THIS IS WRONG." at 1.45 s. |
| 2.4-5.0 | "AT TRUE SCALE": the Moon's orbit shrinks on a log curve to its real 384,400 km. Loops become cusps, then waves, then a clean circle on top of Earth's teal orbit. "NO LOOPS." |
| 5.0-7.0 | Log plunge from the whole orbit to a chase camera just ahead of Earth, looking back down the track. Year clock starts. |
| 7.0-15.6 | One year: DAYS 0 to 365 and LUNAR MONTHS 0 to 12.4 (monotonic). Earth (lit blue sphere) and Moon (white sphere) with labels; gold edge marker points to the Sun. Moon trail (gold) weaves around Earth's trail (teal); both curve toward the Sun. 8.0-11.2: "THE SUN PULLS THE MOON / 2.2× HARDER THAN EARTH." with two arrows on the Moon (gold "SUN 2.2×", teal "EARTH 1×"). 11.5-15.4: "SO ITS PATH ALWAYS / BENDS TOWARD THE SUN." |
| 15.6-16.2 | Held breath. |
| 16.2-19.6 | Hit. Pull back to an oblique view of the whole true-scale orbit. "IT NEVER / GOES BACKWARDS." then "12.4 GENTLE WAVES A YEAR · ZERO LOOPS". |
| 19.6-21.0 | The orbit grows back to the usual drawing and the camera returns to the top view: last frame matches frame 0. |

Tags on screen: "THE USUAL DRAWING" over the myth; "DISTANCES TO SCALE · SUN, EARTH, MOON ENLARGED" over the true-scale shots.

## Facts and sources
- Earth-Sun mean distance 149.6 million km (1 AU); Earth-Moon mean distance 384,400 km. Ratio 389. [NASA Moon fact sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/moonfact.html), [NASA Earth fact sheet](https://nssdc.gsfc.nasa.gov/planetary/factsheet/earthfact.html).
- Sidereal month 27.3217 d; synodic month 29.5306 d; year 365.256 d. 365.256 / 29.5306 = 12.37 lunar months (new-Moon to new-Moon) per year, shown as 12.4. Source: NASA Moon fact sheet.
- Sun's pull on the Moon vs Earth's: GM_sun / (1 AU)² = 5.93 mm/s²; GM_earth / (384,400 km)² = 2.70 mm/s²; ratio 2.20. Computed from the fact-sheet GM values.
- The Moon's path around the Sun is convex (always curves toward the Sun, never loops): [Wikipedia, Orbit of the Moon](https://en.wikipedia.org/wiki/Orbit_of_the_Moon), [Wolfram demonstration, convexity of the lunar orbit about the Sun](https://www.wolframcloud.com/objects/demonstrations/EpicyclesRevisitedConvexityOfLunarOrbitAboutTheSun-source.nb), [Discover, "The Moon that went up a Hill but came down a planet"](https://www.discovermagazine.com/the-moon-that-went-up-a-hill-but-came-down-a-planet-20889). Checked numerically in `window.convexCheck()`: the minimum curvature of the true path is 0.58 of Earth's orbital curvature (positive everywhere).
- The Moon's speed relative to the Sun stays between about 28.8 and 30.8 km/s (Earth 29.8 ± Moon 1.0), so it never moves backwards.
- Simplifications (said in the copy, not on screen): circular orbits in one plane (the real lunar orbit is tilted 5.1° and slightly elliptical; neither changes the convexity). Body sizes are enlarged; distances and the path are true.

## Sound
Fully synthesised (`sound.mjs`, no credits). New family "orbital glass": a spirograph warble whose vibrato runs at the myth's loop rate; during the shrink the vibrato depth collapses into one pure tone (the loops unwinding you can hear); a falling plunge whoosh; a low pad with one glass ping per lunar month climbing a minor scale (12 pings); two tones for the two pulls; held breath; a glass-bowl hit on "IT NEVER GOES BACKWARDS"; the warble returns into frame 0 for the loop. After AAC encoding: -17.1 LUFS integrated, true peak -1.4 dBFS.

## Publish copy

### YouTube Shorts
**Title:** The Moon Never Loops Around the Sun #shorts
**Alt title:** Every Diagram of the Moon's Path Is Wrong

**Description:**
You've probably seen the Moon's path around the Sun drawn as a ring of loops. At true scale there are no loops at all.
The Moon's orbit is 389 times smaller than Earth's, so it simply rides along Earth's orbit, weaving across it about 12.4 times a year. And because the Sun pulls on the Moon 2.2 times harder than Earth does, its path always bends toward the Sun. It never goes backwards.
Did you picture loops too?

Distances to scale; Sun, Earth and Moon enlarged. Orbits drawn circular and in one plane.

#space #moon #astronomy #science #physics #mindblown #shorts

**Tags:** moon orbit, moon path around the sun, moon orbit around sun, does the moon loop, astronomy facts, space facts, solar system, gravity, slow light

**Pinned comment:** The Sun pulls the Moon harder than Earth does. So what is the Moon really orbiting? 👀

### Instagram / Facebook Reels
Everyone draws the Moon's path with loops. 🌙
At true scale there are none.
The Sun pulls the Moon 2.2× harder than Earth, so its path always bends toward the Sun.
It never goes backwards.
#moon #space #astronomy #science #mindblown #slowlight

**Alt text:** Animation: a loopy drawing of the Moon's path around the Sun shrinks to true scale and becomes a smooth circle; a camera then rides with Earth and the Moon for a year while counters show days and lunar months.

## Upload checklist
AI/synthetic content label on. Loop on. No third-party audio or footage.

## QA (v1)
- Render checks passed: counters monotonic over all 630 frames; true Moon path curvature positive everywhere (min 0.58 of Earth's).
- 2 fps contact sheet reviewed: myth, morph, ride, twist and loop frames all read; the 16.2 s flash is 12% for about 0.2 s (playbook limit).
- Audio after AAC: -17.1 LUFS integrated, true peak -1.4 dBFS. File 13.2 MB.
