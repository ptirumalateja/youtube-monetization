# Slow Light "What If" #4: The Black Hole Ladder (Scale Ladder Part 2, ~26 s, no voiceover)

Idea: Part 1 ended on the biggest thing we can see. Part 2 asks how big the biggest *dark* thing gets. One continuous orbiting log-zoom through four black holes. Each time the camera pulls back, the previous event horizon becomes a dot beside the next one. Ends with our whole Solar System as a red-marked speck inside the last shadow, then plunges back down to the first black hole so it loops.
Format: 9:16, 1080x1920, ~26 s, loops. Same palette and info layer as the Scale Ladder (charcoal, cream, gold/teal, red only for the marker). Wordless, thought experiment / not to scale.
Link to Part 1: pin Part 2 in Part 1's comments and end-screen; pin Part 1 in Part 2's.

## Production: no RunPod, no Higgsfield
Everything is procedural and runs in this container (RunPod credits are not needed, because there are no AI plates):
- Scene: three.js r0.170 headless (playwright-core + Chromium, SwiftShader), new file `tools/black-hole-ladder/index.html`, same harness as `tools/scale-ladder/` (`render.js`, `shot.js`, `proj.js`).
- Black hole: analytic lensing, not ray-marching (SwiftShader is CPU only). Full-screen fragment shader warps a starfield and the accretion disc around the shadow (deflection ~ r_s / r), plus a thin photon ring. Disc is a tilted additive ring with Doppler brightening on the approaching side.
- Overlay: PIL (`overlay_bh.py A|B`, copy of `overlay26.py`). Sound: numpy synth plus `tools/sfxlib/` files already in git (`mix_bh.py`, copy of `mix_ladder27.py`).
- Risk: the lensing shader at 720x1280 with 2-sub-frame blend is the slowest part. Spike one 2 s test render first and extrapolate; 4 workers are available (4 cores, 15 GB). If too slow, drop to 540x960 and upscale (SeedVR2 is not available, so use lanczos as before).

## Rungs and numbers
Event-horizon diameter = 2 x (2GM/c^2) = 5.906 km x (M / M_sun). Checked in Python.
| Stop | Mass | Horizon diameter | Ratio vs previous | Comparator drawn |
|---|---|---|---|---|
| 1. Stellar-mass | ~10 suns (typical; range ~5-20) | ~60 km | start | city-scale street-grid lights and a 60 km scale bar |
| 2. Sagittarius A* | ~4.3 million suns | ~25 million km (0.17 AU) | **~430,000x wider** | Mercury's orbit ring around it; about 18 Suns side by side fit across it |
| 3. M87* | ~6.5 billion suns | ~38 billion km (~257 AU) | **~1,500x wider** | Neptune's orbit (60 AU across) as a small teal ring; the shadow is ~4x wider |
| 4. TON 618 | ~66 billion suns (estimates run ~40-66 billion; say "up to ~66 billion") | ~390 billion km (~2,600 AU) | **~10x wider** | Solar System to Neptune's orbit is a speck, ~43x narrower |
- Extra fact for the end card or description: light takes ~15 days to cross TON 618's horizon (3.9e11 km / 299,792 km/s = 1.3 million s) versus ~8 hours to cross the Solar System out to Neptune's orbit.
- Optional description line: the average density inside TON 618's horizon is about 0.000004 g/cm3 (lower than air). Label it "average density" and keep it out of the video.
- Rules: say "event horizon" (not "the black hole's size"); say "up to ~66 billion" and "one of the most massive ever measured", never "the biggest" or "king" (the record is contested and the mass is an estimate); no Phoenix A or other disputed numbers; "to Neptune's orbit" every time; do not call TON 618 a "supermassive black hole you can see" (what we see is the quasar glow around it).

## Hook variants for the A/B (overlay-only difference)
- **A:** "A BLACK HOLE THE SIZE OF A CITY." (31 chars, matches frame 0)
- **B:** "LIGHT NEEDS 15 DAYS TO CROSS THIS." (34 chars, number-led, pays off at the end)
Both fully typed by about 0.8 s. Recommendation: A on YouTube, B on Instagram/Facebook, same A/B method as Part 1.

## Timeline (26 s, matches the Scale Ladder rhythm)
| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0.0 | Dark frame, stellar black hole over faint city lights, thin photon ring, hit on frame 0 | hook (A or B) typed to 0.8 s | Hit: sub + transient + low pulse |
| 0.5-2.0 | Snap pull-back: city shrinks to a dot, the stellar shadow becomes a dot, Sgr A*'s disc swells in behind | | Reverse whoosh, vacuum, hit 0.75 |
| 2.0-5.4 | **Stop 2: Sagittarius A\*.** Disc tilted, lensed stars bending, the real S2 orbit as a thin gold ellipse. Camera orbits slowly, parallax on the disc. Mercury's orbit ring sits well outside the shadow | `430,000x` + `SAGITTARIUS A* · ~4.3 MILLION SUNS` | Dark drone, slow rotating whirr, big slam 1.0 |
| 5.4-7.6 | Pull-back: Sgr A* collapses to a dot, orbit ring becomes a thread | | Vacuum then whip |
| 7.6-11.0 | **Stop 3: M87\*.** Orange ring (EHT-style) with a bright jet along the pole; different camera behaviour: low-angle, jet sweeping across frame. Neptune's orbit as a small teal ring beside the shadow | `1,500x` + `M87* · ~6.5 BILLION SUNS` | Descending harmonic pings on a 106 Hz root (callback to Part 1), jet hiss |
| 11.0-13.0 | Pull-back | | Whip |
| 13.0-17.0 | **Stop 4: TON 618.** Quasar glare, disc and shadow fill the frame; the Solar System appears as a speck with the Sun's cross glyph | `10x` + `TON 618 · UP TO ~66 BILLION SUNS` | Formant choir swell, rising shimmer |
| 17.0-18.0 | Held breath: motion nearly stops, the speck turns red | `LIGHT NEEDS 15 DAYS TO CROSS THIS.` (static, small) | Near-silence |
| 18.0-20.0 | Burst: the camera dives toward the speck; the whole Solar System (to Neptune's orbit) is revealed against the shadow, red marker on it | `43x NARROWER` | Biggest hit: braaam + sub wall |
| 20.0-22.5 | Hold wide: speck inside the shadow, red marker | `OUR SOLAR SYSTEM.` typed | Wind returns |
| 22.5-24.1 | Plunge match-cut down the ladder (TON 618, M87*, Sgr A*, stellar) with corkscrew orbit | | Rising sweep, one whoosh per crossing, thud |
| 24.1-26.0 | Lands on the stellar black hole over the city (frame 0) | | Bell ping, crackle, hard stop |
Counter is monotonic: one odometer showing the horizon diameter in km (60 km -> 25 million km -> 38 billion km -> 390 billion km); ratio chips ("430,000x") are separate and appear only after the object is recognisable (hold ~1 s before each label).

## Shape language (never repeat Part 1)
- Part 1: Sun globe, orbit rings, spiral, web. Part 2: black-hole shadow + photon ring (circle), tilted disc, jet (line), quasar glare. Different hero object at each stop, different disc colour: stellar = blue-white with a gas stream from a companion star; Sgr A* = dim red-gold; M87* = orange; TON 618 = hot white-gold.
- Callbacks only where meaningful: orbit rings for Mercury and Neptune (thin teal), the Sun's cross glyph for the Solar System speck, red only for the marker.

## Camera grammar
Orbiting log-zoom as in Scale Ladder 3.3 A, with a different behaviour per stop: Sgr A* slow high orbit, M87* low-angle jet sweep, TON 618 straight-on and almost still (scale is the point), final burst a dive. Pull-backs 1.5-2 s, holds 3-5 s, one held breath before the burst, plunge match-cut for the loop. Scale-free dust and 2-sub-frame motion blur as before.

## Build plan
1. Spike: lensing shader + one 2 s test render; measure render time; choose 720x1280 or 540x960.
2. Scene `tools/black-hole-ladder/index.html` (stops, comparators, camera keys); `shot.js` stills at each stop; contact sheet check.
3. `proj_bh.js` for marker positions; `overlay_bh.py A|B` with a script-asserted monotonic counter.
4. Render frames (`render.js`, 4 workers), composite, then sound mix `mix_bh.py`; measure LUFS and true peak after AAC (target about -15 LUFS, TP below -1).
5. Publish copy `black-hole-ladder-publish-copy.md` and update `audio-attribution.md` for any CC BY file used.

## Quality gate
1. First frame: hit + premise within 1 s; hook readable at 1 s.
2. Every on-screen number matches the table; counter monotonic; plurals correct.
3. One target at a time, 35-65% of frame width, held ~1 s before its label; a different camera behaviour at each stop.
4. No white-outs (flash max 12-16% for 0.1-0.2 s); disc and shadow structure visible at each label.
5. Near-silence before the burst; last frame matches frame 0.
6. Text inside the Shorts safe zone; AI/synthetic label ON; "thought experiment, not to scale" in the description; sound licences confirmed.

## Open questions
- Hook A vs B on YouTube: keep the same recommendation as Part 1 or test B there first?
- Whether to add the "lower density than air" paradox as a second on-screen beat (adds a fact to verify; default is description only).
- Not yet built or auditioned by ear.
