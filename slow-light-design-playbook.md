# Slow Light: video design playbook (science reels)

Living record of how the Slow Light science reels are designed and built: the goals, the design decisions and why we took them, the depth / motion / camera grammar, the sound design, the pipeline, and the mistakes that taught us something. Update it whenever a decision changes.

Scope: the wordless "light and scale" reels (Red Sprites, The Sun Vanishes, Night Sky, Scale Ladder). The Abhimanyu story project has its own rules in `claude.md`.

---

## 1. What we are making

- **Channel:** Slow Light, "Stories worth slowing down for." Vertical 9:16 Shorts / Reels for YouTube Shorts, then Instagram and Facebook reposts. The channel owner posts manually.
- **Format for these reels:** 14-26 s, no voiceover, pure visuals + sound design + a few words of on-screen text. Each reel is one idea, loops cleanly, and carries a "thought experiment / not to scale" tag where distances or sizes are compressed.
- **Feeling we want:** the visual equivalent of travelling through an impossible universe: Pandora-level awe, depth you can feel, motion that is "smooth AF", and a small paradox or twist that makes the idea hit.
- **Production rules:** no Higgsfield for images or video. We use RunPod (Qwen Image Edit, Wan 2.2 I2V, SeedVR2 upscale) for plates, and local code (three.js headless render, PIL, numpy, ffmpeg) for everything else.
- **Retention evidence we design against:**
  - Red Sprites Short: 29.2% stayed to watch, 70.8% swiped away (small sample, directional only).
  - Sun reel: good average watch time but early drops in the first 2-3 s.
  - Rule that came out of it: the premise and a hit must land in the first 1-2 s, and something must change every 1-1.5 s early on.
  - The metric to compare across reels is "stayed to watch" at 2 s, then average view duration, completion (loops can exceed 100%), shares.

## 2. Reel catalogue and status

| Reel | Idea | Final files | Status |
|---|---|---|---|
| Red Sprites | Lightning above storms | posted YouTube Short | live; copy in `red-sprites-publish-copy.md` |
| The Sun Vanishes | Light and gravity both take 8 min 20 s | `sun_vanishes_v3_yt.mp4` (14 s, YouTube recut with stronger sound) | posted IG/FB; YouTube copy in `sun-vanishes-reel.md` |
| Night Sky "the past" | Every light you see is old; Andromeda sees our past | v4 approved (19 s, sound reference); **v8.1 final** `night_sky_past_v81_A.mp4` (19.2 s) | copy ready: `night-sky-v81-publish-copy.md` |
| Scale Ladder | Earth to the observable universe, ends "YOU ARE HERE." | **`scale_ladder_3d_v4_A/B.mp4`** (26 s, hooks A and B) | copy ready: `scale-ladder-publish-copy.md` |
| Birthday Paradox | 23 people = 50.7% chance of a shared birthday; count the pairs (253), not the people | `birthday-paradox-21.5s.mp4` (21.5 s, loops) | copy ready: `birthday-paradox-publish-copy.md`; build in `tools/birthday-paradox/` |
| Proton Laps Earth | An LHC proton could circle Earth 7.48 times in 1 s; light still wins by 2.85 m | `proton-laps-earth.mp4` (22.5 s, loops) | copy ready: `proton-laps-publish-copy.md`; build in `tools/proton-laps/` |

Specs and notes per reel: `night-sky-past-reel.md` (v1-v4), `night-sky-v5-notes.md` (v5-v7), `night-sky-v8-spec.md` (v8 frozen plan + v8.1 pass), `scale-ladder-reel.md`.

## 3. The design system (decisions that now apply to every reel)

### 3.1 Hook and structure
1. Frame 0 is already moving and a hit lands on frame 0.
2. The hook line is typed fast (done by about 1.9 s) and states the premise ("YOU'RE SEEING THE PAST." / "EARTH IS A DOT."). A/B hook variants are overlay-only changes.
3. A pattern interrupt arrives about 2 s in (the "snap" into the 3D world).
4. A near-silent "held breath" (about 0.5-1 s) sits before the biggest reveal; the reveal gets the biggest hit.
5. The last frame matches frame 0 so the reel loops (Earth dot; stargazer sky).
6. The closing line is short and is the thesis ("YOU ARE HERE." / "YOU'RE LOOKING AT THE PAST.").

### 3.2 Decodability (the lesson of Night Sky v5-v8)
The audience must be able to say what each stop is. Smooth, beautiful and clear are different things; v5-v7 were smooth but unreadable.
- One target on screen at a time, recognisable by shape and colour: silver cratered Moon, gold granulated Sun disc, one red-orange sphere for Proxima, a tilted gold-and-blue galaxy for Andromeda.
- The object fills about 35-65% of frame width and is held long enough to read (about 1 s) before its label lands.
- One label per object, shown when the object is recognisable. Never change the counter while the viewer is still working out what they are seeing.
- Pattern per stop, always the same: **target (small, centred) -> rings sweep through the camera -> target grows -> label and counter -> target slides out and the next one is already ahead.** About 1.5-2 s per stop.
- Facts on screen must be unmistakably about the object ("THE LIGHT YOU SEE LEFT" + big age + red name chip + one-line meaning), and the numbers must be right (see 3.7).
- The counter is **monotonic**: one odometer that only ever goes up across the whole video (0 -> 1.3 s -> 8 min 20 s -> 4.2 years -> 2.1 million -> 2.5 million years). It showed us a backwards jump once (the Andromeda label restarted from 0); the overlay build now asserts monotonicity frame by frame.

### 3.3 Camera grammar
Two camera languages, chosen by what the reel says.

**A. Ladder (scale up): orbiting log-zoom.** Used when the idea is "everything fits inside the next thing."
- Camera distance Z follows a log spline; the focus point follows its own spline; azimuth and elevation orbit slowly (keys in `index.html`, `OK`), so every stop shows true parallax (the Sun is a globe, the orbit rings tilt open, the galaxy swings edge-on to face-on).
- Pull-backs are fast (about 1.5-2 s); holds are 3-5 s; one held breath (17-18 s) before the burst.
- The ending is a **plunge match-cut**: from the cosmic web the camera falls back down the whole ladder (log-spaced distances, corkscrew orbit) and lands on Earth, so the loop closes with no black gap.

**B. Axis (travel through time): one forward axis.** Used for Night Sky.
- Everything sits on one axis; the camera looks straight down it for the whole flight, field of view constant, no roll, no look-at blending. A slight lateral bank is allowed only while passing an object, and the previous object slides out sideways.
- **Target first:** the next object is already a small point at the exact centre before the camera accelerates toward it.
- **Rings are always circles centred on the axis.** The vanishing point is the frame centre; the camera flies through the openings one by one and the rings sweep out to the frame edges. Ring colour = colour of the target. No hexagons, no cross spokes (they read as wireframe).
- The finale breaks the axis once, on purpose: the camera swings out sideways and up (frame rolled so the beam is vertical) to show two glowing nodes joined by a light beam with a pulse (Andromeda and our galaxy), then dives back along the beam to our star.
- Scene time can be warped smoothly (Catmull on `new->old` time keys) to speed up or hold part of a move without re-authoring the camera; a slow-motion window (scene clock lags video clock by 0.5 s) is used to hold the two-node view.

### 3.4 Depth, parallax and motion
- **Scale-free dust:** 14 camera-wrapped lattice layers (about 126k points), world-fixed so they give true parallax; each layer fades in and out by scale, so particles keep sliding past at different depths at every zoom level.
- **Motion blur:** every frame is the average of 2-6 sub-frames (shutter 1/60 s normal, 1/30 s above 600 units/s) accumulated on a 2D canvas.
- **Layered galaxy:** the approved Andromeda plate is turned into a depth-bulged point cloud (positions sampled by luminance, brighter pixels pushed toward the camera) plus a soft plate plane, so camera movement shows depth in a 2D image.
- **Distinct hero object per reel:** do not reuse a Sun, galaxy or ring motif across reels (see 3.6).
- **Grade (Night Sky):** teal shadows, warm highlights, vignette and fine grain on the whole 3D section so the shots read as one film.

### 3.5 Exposure discipline (no white-outs)
- Soft clamp `1-exp(-1.25c)` before bloom; bloom about 0.5 strength. Additive glow planes are faded by distance and capped; the opening star's glow is small and fades as the camera passes through it.
- Maximum overlay flash 12-16% for 0.1-0.2 s. If a frame is white, the shot is wrong, not "intense".
- Never let a large glow plane sit behind a hero object (it flattens the frame to beige); keep granulation, craters, structure visible at the moment of the label.

### 3.6 Palette and "never repeat visuals across reels"
- Charcoal / deep navy-black, warm cream for text, gold and teal accents, **red only** for markers, chips, rings and the end-line chip.
- Sun reel Sun, Ladder Sun (procedural H-alpha fibril globe), and Night Sky Sun (clear golden convective disc with small spikes) are three different designs on purpose.
- Galaxy designs differ: Ladder uses a procedural 3D Milky Way and a Voronoi-boundary cosmic web (real filament-and-void look, not a node graph); Night Sky uses the approved gold-and-blue Andromeda plate.
- Shape language is meaningful: circle rings = a gate to the next realm; a node + beam = a relationship (light between two galaxies).

### 3.7 Information layer
- Fonts: Liberation Mono Bold (counters, chips, captions), DejaVu Sans Mono (small labels). Cream text, thick black stroke, red chips (`RED=(214,62,48)`).
- Sizes at 1080x1920: counter about 92 px (auto-fit, one size for all stops), "THE LIGHT YOU SEE LEFT" 27 px spaced, red chip 46 px, one-line meaning 29 px, paradox caption 54 px over three lines, ladder names 36 px (active rung 42 px), end line 70 px.
- Safe zones: keep text out of the bottom ~18% and the top strip; the left ladder sits at x=64.
- Left time ladder (NOW at the bottom, rungs MOON / SUN / PROXIMA / ANDROMEDA, red marker climbing) is a core device: it shows order and depth at a glance. Names only on rungs; the big counter carries the time.
- Facts:
  - Moonlight about 1.3 s; sunlight 8 min 20 s (499 s); Proxima 4.24 ly (say 4.2 years); Andromeda about 2.5 million ly.
  - "From Andromeda you'd see Earth as it was 2.5 million years ago. No modern humans yet." Modern humans are about 300,000 years old; say "modern humans", never just "humans".
  - Ladder ratios: Earth to Sun 109x wide (1.3 million Earths by volume); Sun to Solar System (to Neptune's orbit) about 6,500x; Solar System to Milky Way about 100 million x; Milky Way to observable universe about 930,000x. Always say "to Neptune's orbit" and "observable universe".
  - Never say stars are "gone" or "dead"; always say the light you see left X ago. Always tag "thought experiment / not to scale".

## 4. Sound design

### 4.1 Principles
- Sound is part of the shot design, not a layer on top: every hit, whoosh and tick has a visual cause, and the sync points are taken from the real camera (ring crossing times are measured from the scene, not guessed).
- **Hits are rare and sized.** Impacts only at frame 0, the snap, the big reveal and the landing. A hit at every cut makes the film feel assembled from separate scenes; momentum (rising texture, whooshes, ticks) carries the stops.
- **Hit anatomy:** transient crack (above 2 kHz) + saturated pitch-drop body (about 88-320 Hz so phone speakers reproduce it) + gong partials + a small real sub; a reversed "suck" swell and a 40-95 ms vacuum right before the hit. Size hierarchy: the biggest hit is only the main reveal.
- **Phones cannot play below about 90 Hz.** Keep the sub on the hit bus only; high-pass other buses at 90 Hz; put the weight in the 90-400 Hz body. (A mix that was 69% sub energy felt weak; moving energy into the audible band fixed the feel.)
- **Held-breath silence** (-40 dB or near it) before the biggest hit; controlled-decay sub wall afterward; wind and a bell on the return; a crackle re-ignition and a rising tone into frame 0 so the loop is audible.

### 4.2 Sound families (do not reuse the same palette across reels)
- **Night Sky: the v4 sound is the reference and is used as-is.** Frame-0 hit (explosion + dark accent), sparks charge-up, reverse whoosh into the snap, portal-gate shimmer, per-stop identity (Moon airy glass bell, Sun fire crackle + plasma trail + sub whoosh, Proxima gateway + dark low hit), hyperdrive riser + jet pitch-up + accelerating pulses, held breath, big blast + sub wall, wind and bell on the end plate, loop-link tone. The v8.1 mix is the v4 cue sheet retimed (hyperdrive re-fitted to 1.65 s, hero hit at 10.5 s, dive home with v4's reverse whoosh / riser / warp-in then 0.3 s silence).
- **Scale Ladder:** brass-and-sub family: chakong brass braaam (92 Hz body) + bass drop + screaming-echo tail on the 18.0 s burst and the 2.0 s Sun slam, harmonic pings on a 106 Hz root for the Solar System, formant choir pad, shepard risers, fire roar, plunge whooshes.
- **Birthday Paradox:** fully synthesised music-box family (no samples): each month is a pentatonic note so birthday twins ring in unison, a drone that tightens with the odds, accelerating heartbeat, thread sparkle ticks, one big gong-partial hit on the match.
- **Proton Laps Earth:** synthesised accelerator family: speed whine rising through the slowed second, doppler pass-by each time the proton crosses the front of Earth, climbing digital lap ticks, counter chatter, falling plunge whoosh, a bright pure "zing" for light at the finish.
- Discarded: the Night Sky v8 "time and glass" tick/shepard mix (it was a replica of the Ladder's character and was rejected). Lesson: ask for the reference sound before designing a new one.

### 4.3 Loudness and delivery
- Target about -15 LUFS integrated; **check true peak after AAC encoding, not before** (a +2 dB overshoot appeared on a single transient). Fixes that worked: lower the limiter and use a soft-clip (`asoftclip tanh`) on the single loudest transient; measure with `ebur128=peak=true`.
- Mixes are built in numpy buses (hit, sfx, bed, synth, tick, riser, punch, air) with side-chain ducking under hits, bass management, reverb on the hit bus, then master tanh and peak normalisation.

### 4.4 Licences (hard rules)
- Use CC0, or CC BY with an explicit credit line (creator, title, link, licence and link, and "changes were made"). Never CC BY-NC. Confirm every licence before posting; keep a table per reel.
- Credit block pattern lives in each `*-publish-copy.md`. Tomlija's pack is CC BY 3.0 (title required); the rest of the CC BY files are 4.0.
- Files the owner supplies later (Uppbeat braams, Pixabay-style hum/explosion, chakong 722633) are noted per reel; Uppbeat free sound effects need no credit per its help centre, but check the current terms before a monetised upload. Chakong needs credit (CC BY 4.0).

## 5. Per-reel design record

### 5.1 Night Sky "The night sky is showing you the past" (v8.1)
World (axis Z, units arbitrary): star0 (0,0,-8) with a ring; Moon (0,0,-70) R 4; Sun (0,0,-320) R 18; Proxima (0,0,-900) R 6; Andromeda plate at z=-22000 (1800x3200 plate plane + 220k-point cloud).
Timeline (video seconds):

| Time | Shot |
|---|---|
| 0-2.1 | Stargazer plate, hook typed, spark charge-up, star flares, ring forms |
| 2.1-2.9 | Snap through the star's ring; a small silver disc (Moon) is already ahead |
| 2.9-4.4 | Moon: 4 silver rings, Moon grows to about 65% width and holds; counter ticks 0 -> 1.3 s |
| 4.4-6.3 | Moon slides out; Sun reveals as a gold disc; 3 gold rings; counter 1.3 s -> 8 min 20 s |
| 6.3-8.2 | Sun slides out; one red-orange target ahead (Proxima); 3 red rings; counter -> 4.2 years |
| 8.2-10.0 | Hyperdrive: 23 centred rings, counter climbs to 2.1 million years; a faint oval (Andromeda) appears at the vanishing point |
| 10.0-10.5 | Held breath |
| 10.5-12.6 | Soft bloom, galaxy opens (no white-out); counter -> 2,500,000 YEARS AGO |
| 12.6-16.0 | Camera swings out: two nodes + beam + pulse; caption; hold about 0.5 s longer |
| 14.4-16.2 | Dive along the beam to our star; star carried into the plate by a dissolve |
| 16.2-19.2 | Stargazer plate, "YOU'RE LOOKING AT THE PAST." typed once, loop |

Iteration history (why it ended up here):
- v1-v4: portal tunnel with distinct portal shapes per stop (circle / double+cross / hexagon / halo); v4 approved and is the sound reference.
- v5-v7: true 3D flight with parallax; strong shots but the audience could not decode the journey (Betelgeuse insert, chained gates, camera skimming ring edges, white-outs at joins, a pinwheel look-back galaxy).
- v8: rebuilt on one axis with centred rings and target-first (see 3.3 B). v8.1: v4 sound retimed, monotonic counter, bigger ladder and caption, Sun close-up tamed, clean dive, end-card typing bug fixed.

### 5.2 Scale Ladder (26 s, v4)
- Stops: Earth (hook, pull-back) -> Sun (2.0-5.4) -> Solar System to Neptune's orbit (7.6-11.0) -> Milky Way (13.0-17.0) -> held breath (17-18) -> burst into the cosmic web (18-20, 20-22.5) -> plunge match-cut home (22.5-24.1) -> "YOU ARE HERE." (24.1-26), loops to the Earth dot.
- Scene constants: `FOV 50`, Sun radius 70 at (80,-20,0), 8 orbit rings (200-2400), Milky Way radius 40,000 (200k points, differential rotation in the vertex shader), cosmic web 650k points sampled on Voronoi boundaries (filaments where 3 cells meet, gold knots).
- Camera: log-Z keys (e.g. Z 9 -> 128 at the Sun, 6,500-8,200 at the Solar System, 120k-146k at the Milky Way, 2.2M-3.9M at the web), orbit keys per stop, a plunge from 22.5 s to Earth at 24.1 s.
- Hooks: A "EARTH IS A DOT." (YouTube) / B "1.3 MILLION EARTHS FIT INSIDE THE SUN." (IG/FB).

## 6. Pipeline and tooling

- **Plates:** RunPod REST API (`https://rest.runpod.io/v1/pods`, send `User-Agent: curl/8.5.0`). Old pods rarely restart; create a new pod on the network volume with the saved spec. ComfyUI proxy `https://<podid>-8188.proxy.runpod.net`; scripts for Wan 2.2 I2V, SeedVR2 upscale and Qwen Image Edit. Stop pods when done.
- **3D scenes:** three.js r0.170 rendered headless (playwright-core + Chromium, SwiftShader CPU), served by `python3 -m http.server`. `shot.js` renders test stills; `render.js` renders frames (4 parallel workers, interleaved frames, 720x1280, upscaled to 1080x1920 with lanczos). `proj*.js` dumps screen positions for overlay markers. `build.py` assembles the page from parts (night-sky v8).
- **Overlay:** PIL draws text, counters, ladder and markers into an RGBA stream piped to ffmpeg (PNG .mov), composited over the base.
- **Composite:** plate segment + 3D frames + plate segment with an `xfade` dissolve (normalise timebase with `settb=1/30,fps=30,setsar=1` first), overlay, audio mux, `-movflags +faststart`. Keep each file under 30 MB for chat delivery.
- **Sound:** numpy mixer scripts (`mix*.py`) with the library in `sfxlib/`; sync times from the scene where possible.
- **Where things live:** `tools/scale-ladder/` (3D Ladder: scene, overlay26, mix_ladder26/27/28), `tools/night-sky/` (plate-era scripts, `mix4.py` = the v4 sound), `tools/night-sky-v5/`, `tools/night-sky-v8/`, `tools/night-sky-v81/` (current Night Sky scripts), `tools/portal-spike/` (first 3D spike). Scratch outputs are not committed.

## 7. QA checklist before delivery
1. First frame: hit + premise; hook text readable at 1 s.
2. Contact sheet at 2 fps: every stop recognisable; one target at a time; no frame is white or beige; labels legible at phone size.
3. Every number matches the fact table; counters are monotonic (script-asserted); plurals correct.
4. Type-on text: check the counter is never negative (a negative slice index typed the end line twice); check the loop (last frame -> frame 0).
5. Audio: measure LUFS and true peak after AAC; silence windows present; hits only where designed; credits match the files actually placed.
6. Safe zones; file size; AI/synthetic label on in the upload.

## 8. Lessons log (bugs and mistakes worth not repeating)
- **Shared shader program caches uniforms.** Several point materials with identical source shared one program and one uniform cache, so web/dust layers showed on the first render only. Fix: give every point material its own `customProgramCacheKey`.
- **Setting `material.opacity` on a ShaderMaterial does nothing** when the opacity lives in a uniform; a glow plane stayed on and flooded the hook frame.
- **Camera focus splines overshoot** when a far key is the neighbour of a near one (the Solar System stop drifted off-centre). Use explicit piecewise focus paths.
- **Glow planes and depth:** without depth testing, objects on one axis overlap; control draw order and visibility windows, and fade glows with distance.
- **Typed text:** `string[:n]` with a negative `n` slices from the end; always start typing at n >= 1.
- **AAC true peak:** loudness gain alone does not control it; use a soft-clip on isolated transients and measure after encoding.
- **Tooling hygiene:** `pkill -f` matches the invoking shell's own command line (use a bracket pattern); local test servers die between sessions (restart before blaming the scene); a `rm` with a relative glob after `cd` is blocked, use fresh directories.
- **Process:** polish passes do not fix a spatial-logic problem; when the audience cannot decode the journey, freeze the shot plan (camera, angles, what the viewer perceives) first, build once, check frames against the plan, then deliver. Ask for the reference sound when the owner says a version "was good enough".

## 9. Decision log (chronological)
| Decision | Why |
|---|---|
| Sun reel recut for YouTube: full question visible from frame 0, richer sound | early drops in the first 2-3 s |
| New formats use no voiceover, sound design carries the hook | retention analytics; reference reels |
| Night Sky as a portal tunnel with per-stop shapes (v1-v4) | decodable, brand-like; v4 approved |
| Move Night Sky to true 3D | depth, parallax, "impossible universe" feel |
| Scale Ladder rebuilt as true 3D Powers-of-Ten fly-back, 26 s, own procedural Sun | flat plates had no depth; Sun must differ from the Sun reel |
| Galaxy designs differ from Andromeda (Ladder) and from each other | never repeat visuals across reels |
| Plunge match-cut instead of a black gap | makes the loop continuous |
| Fix shared-uniform bug, rebuild cosmic web as Voronoi boundaries | web was invisible, then looked like a node graph |
| Hits sized by importance, braaam as hero on the biggest hits (Ladder) | hits all peaked at the same level and felt weak |
| Night Sky sound = v4 sound retimed | owner: v4 sounds "more than good enough" |
| Betelgeuse, chained gates, hexagons, look-back pinwheel removed | audience could not decode; wireframe look |
| One axis, target first, centred rings, previous object slides out | spatial logic fix (v8) |
| One monotonic odometer + left time ladder (kept and enlarged) | comprehension; owner loved the ladder |
| Two-node + beam pull-back instead of a face-on galaxy | avoids the "shuriken" and explains the paradox |
| Dissolve of the single star into the stargazer plate | no flash, no visual reset |
| Freeze the plan before each big build; one contact-sheet check per stage | stop endless polish loops |

## 10. Backlog and open questions
- Night Sky hook B ("THIS LIGHT IS OLD.") for v8.1 is overlay-only if we want to A/B.
- Publish and compare: Night Sky (Thu 15 Oct, 4 PM IST suggested) then Scale Ladder (Fri 16 Oct); IG/FB about 7:30 PM IST; record 2-second stayed-to-watch, average view duration, completion, shares.
- Sounds that would still improve the Ladder and Night Sky: a real cinematic gong/boom with body between 100 and 800 Hz, a clean choir or pad swell, bowed/glass harmonics, a slow mechanical clock tick.
- Verify Uppbeat free sound-effect terms and the origin and licence of the two unnamed files (circuits hum, explosion) before a monetised upload.
- Higher-resolution final renders (render 1080x1920 natively) and a 60 fps variant are possible but not needed for Shorts.
- Next reel ideas should reuse the grammar: one idea, one axis or one orbit, one label per object, a monotonic quantity, a paradox beat, a loop.
