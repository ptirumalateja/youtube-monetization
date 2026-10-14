# Slow Light "What If" #3: The Scale Ladder (about 19 s, no voiceover)

Idea: one continuous pull-back through four jumps in scale. Each time the camera pulls back, the thing that filled the frame becomes a dot. Ends on "YOU ARE HERE." and loops to the Earth dot.
Format: 9:16, ~19 s, loops. Visual wonder + sound design, a few words of text, a "x times wider" counter. Same palette (charcoal, cream, gold/teal, red accent only for the "you are here" marker).
Lessons carried over: premise in the first second, dark opening with a hit on frame 0, a different camera behaviour and shape at each stop, near-silent gap before the biggest hit, last frame matches frame 0.

## Rungs and numbers (each ratio = how many times wider than the previous stop)
| Stop | What it is | Ratio vs previous | Check |
|---|---|---|---|
| 1. Earth | 12,742 km across | start | |
| 2. Sun | 1.39 million km across | **109x wider** than Earth (1.3 million Earths fit inside by volume) | 1,392,700 / 12,742 = 109 |
| 3. Solar System (out to Neptune's orbit) | ~9 billion km across (Neptune orbit diameter, ~60 AU) | **~6,500x wider** than the Sun | 8.99e9 / 1.39e6 = 6,455 |
| 4. Milky Way | ~100,000 light-years across (estimates run higher; say "~") | **~100 million x wider** than the Solar System | 9.46e17 km / 8.99e9 km = 1.05e8 |
| 5. Observable universe | ~93 billion light-years across | **~930,000x wider** than the Milky Way | 93e9 / 1e5 = 9.3e5 |
- Always label stop 3 "to Neptune's orbit" (the Solar System has no single edge).
- "Observable universe" never "the universe".
- Avoid contested numbers (largest star, galaxy counts); the ladder only uses the five rows above.

## Hook variants for the A/B (same video, only the text differs)
- **A:** "EARTH IS A DOT." (4 words, pairs with the ending "YOU ARE HERE.")
- **B:** "1.3 MILLION EARTHS FIT INSIDE THE SUN." (number-led, concrete)
Both are on screen by about 0.7 s, fully typed (not slow).

## Timeline (19 s)
| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0.0 | Near-dark frame, a small Earth lit by a flare, hit on frame 0 | hook (A or B) typed 0.35-0.8 s | Hit: sub boom + transient, explosion layer, low pulse |
| 0.5-1.5 | Snap pull-back from Earth; the Sun swells into frame behind it, Earth is now a speck against it | | Reverse whoosh into the pull, implosion + sub hit |
| 1.5-4.5 | **Stop 2: the Sun.** Plasma plate rotating with outward particles. Camera slow, huge | `109x` + `SUN` chip | Fire roar, crackle, deep boom |
| 4.5-5.0 | Pull-back: the Sun shrinks to a dot with orbit rings appearing | | Vacuum then whip |
| 5.0-8.0 | **Stop 3: Solar System.** Orbits as concentric rings (circle language), planets as points, Neptune's ring highlighted | `6,500x` + `SOLAR SYSTEM · TO NEPTUNE'S ORBIT` | Orbital shimmer, glass pings per ring, light sub |
| 8.0-8.5 | Pull-back: the whole system collapses to a dot | | Vacuum then whip |
| 8.5-12.0 | **Stop 4: Milky Way.** Face-on spiral plate, the solar system dot marked | `100 million x` + `MILKY WAY · ~100,000 LIGHT-YEARS` | Choir/pad swell, rising shimmer |
| 12.0-12.4 | Held breath: motion nearly stops | | Near-silence (like the night-sky reel) |
| 12.4-15.5 | Pull-back burst to **Stop 5: the cosmic web.** Filaments and the Milky Way a dot | `930,000x` + `OBSERVABLE UNIVERSE · ~93 BILLION LIGHT-YEARS` | Biggest hit: sub wall with controlled decay, tonal body |
| 15.5-16.0 | Hard cut to black | | Silence |
| 16.0-19.0 | Back to the Earth dot (frame 0) with a red marker | `YOU ARE HERE.` (typed, held ~1.5 s), fades to the dark Earth | Wind/air returns, one bell ping, crackle, hard stop |

## Shape language (kept meaningful)
- Earth: thin circle. Sun: circle + 4-point cross (same callback as the night-sky reel). Solar System: concentric orbit rings. Milky Way: spiral arms. Universe: web of filaments. Colour stays gold/teal/cream; red only for the YOU ARE HERE marker.

## Build plan (RunPod + local, no Higgsfield)
1. Plates (Qwen + Wan + SeedVR2): Earth (reuse existing), Sun (reuse the rotating Sun plate), Milky Way face-on spiral (new), cosmic web (new, or procedural 3D in three.js).
2. Solar System and orbit rings: procedural (three.js or numpy), drawn crisply.
3. Pull-back transitions: per-frame compositing in Python/ffmpeg, exponential zoom-out around each object's position.
4. Text, counter and impact layer: PIL overlay (same system as the night-sky reel), two hook variants.
5. Sound: library files (already downloaded) + synth layers via `tools/night-sky/mix*.py`, new cue sheet per stop.
6. Same checks as the night-sky reel: facts, loop match, loudness -14 to -15 LUFS with TP below -1, licence table.

## Quality gate
1. First frame: hit + a clear premise within 1 s.
2. Every on-screen ratio matches the table above.
3. A different camera behaviour at each stop (not one repeated zoom).
4. Near-silence before the final reveal; the last frame matches frame 0.
5. Text inside the Shorts safe zone; ruler/labels readable on a phone.
6. Sound licences confirmed before posting.

## v2: true 3D fly-back (26 s) - built
- Scene: `tools/scale-ladder/index.html` (three.js, procedural H-alpha Sun, orbit-ring Solar System, 200k-point Milky Way, Voronoi-boundary cosmic web). Camera orbits (yaw/tilt) around each stop for parallax; 2-sample temporal blend per frame.
- Timeline: 0-2 hook (Earth pulls back, Sun limb arrives) | 2.0-5.4 Sun (109x) | 5.4-7.6 pull-back | 7.6-11.0 Solar System to Neptune's orbit (6,500x) | 11-13 pull-back | 13-17 Milky Way (100 million x) | 17-18 held breath | 18-20 burst | 20-23 cosmic web (930,000x) | 23.0-23.8 black | 23.8-26 Earth, "YOU ARE HERE."
- Render: `render.js` (4 parallel workers, 720x1280, upscaled to 1080x1920). Overlay: `overlay26.py A|B` (needs `proj.json` from `proj.js`). Sound: `mix_ladder26.py`. Audio chain: volume +3 dB, alimiter 0.62, AAC -> about -15.0 LUFS, -2.2 dBTP.
- Sound credits needed if the same files are used: Electric Sparks (mikiko850, CC BY 4.0), 5 Everyday Whooshes (Tomlija, CC BY 3.0), synth_jet (vartioh, CC BY 4.0). JacobsLadder (Halleck) is loaded in the script but not placed in this cue sheet.
- Not yet auditioned by ear.

## v2.1: plunge match-cut + dense dust (final cut files `scale_ladder_3d_v2_A/B.mp4`)
- Black gap removed. From 22.5 s the camera plunges back down the ladder (web, Milky Way, Solar System, Sun, Earth) in about 1.6 s with a corkscrew orbit, landing on Earth at 24.1 s with a soft flash; "YOU ARE HERE." types at 24.5 s. Loops to frame 0 (Earth pulling back).
- Dense scale-free dust: 14 camera-wrapped, world-fixed lattice layers (about 126k particles) fade in and out by scale, so particles slide past at different depths.
- Audio: gain +4.5 dB, alimiter 0.48 gives about -15.1 LUFS and -3.5 dBTP after AAC. Plunge sound: rising sweep, riser, one whoosh per scale crossing, thud on landing.
