# Slow Light "Speed Ladder": how fast is fast? (17.1 s, wordless, loops)

Status: BUILT v1 (18 Oct 2026) with the recommended picks (km/s counter, long twist wording, Earth beat kept). Build notes: rendered with PIL 2-D vector sprites + parallax streaks instead of three.js (faster and clearer for flat silhouettes); the Earth is the lattice-point globe from `tools/mosquito/land.json`. Bullet label corrected to ~3,200 KM/H (0.9 km/s x 3600 = 3,240). Earth label shows 107,000 KM/H. Code: `tools/speed/render.py`, `tools/speed/mix.py`.

Format: 9:16, 1080x1920, 14 s (target band 10-15 s), 30 fps, no voiceover, loops. Visuals and sound are 100% designed in code (three.js, no AI clips, no generation credits).
Idea: a speed ladder in one unit. Five objects, each faster than the last, the previous one left behind, then a last twist that breaks the ladder. Origin: the Meta Creator Assistant's "comparison of speed" suggestion for the next space reel (bullet, jet, light, expansion of the universe). We keep the idea and fix the science (see guardrails).

## Why this version
- 14 s is the owner's 10-15 s ask; payoff (light) lands at about 9 s, the twist at about 11 s, the loop at 14 s.
- Same stop pattern as the Scale Ladder (playbook 3.2): one recognisable object, rings sweep through, label and counter, slide out, next one ahead. About 1.7 s per stop.
- One monotonic counter in one unit (km/s), so it can never jump backwards.
- "YOU, RIGHT NOW" (Earth around the Sun) is the personal beat that makes people share it.

## Fact guardrails (every number on screen)
Status key: V = checked against a source on 18 Oct 2026; TO CHECK = verify before it goes on screen or into copy.

| On screen | Fact | Status |
|---|---|---|
| Airliner about 0.25 km/s (900 km/h) | Typical jet airliner cruise, Mach 0.8-0.85, about 850-950 km/h depending on altitude | TO CHECK (aircraft maker or airline source); say "about" |
| Rifle bullet about 0.9 km/s | Muzzle velocity varies by round (roughly 0.7-1.0 km/s); 5.56 mm NATO about 0.94 km/s | TO CHECK; say "about", label "rifle bullet" |
| Earth around the Sun about 30 km/s (107,000 km/h) | Mean orbital speed 29.78 km/s (NASA Earth Fact Sheet). This is speed around the Sun, not through the galaxy | TO CHECK (NASA); label "EARTH AROUND THE SUN" |
| Parker Solar Probe about 190 km/s (692,000 km/h) | 24 Dec 2024 perihelion, about 192.22 km/s; Guinness World Records "fastest spacecraft speed"; NASA says it is the fastest human-made object. Some sources round to 191 km/s, so use "about 190" | V ([Guinness](https://www.guinnessworldrecords.com/world-records/66135-fastest-spacecraft-speed)) |
| Light 299,792 km/s | 299,792.458 km/s exactly by definition of the metre | V (definition) |
| "About 1,560x faster than Parker" | Our arithmetic: 299,792 / 192.22 = 1,559.6 | V (arithmetic) |
| "Far galaxies recede faster than light" | Standard result: beyond the Hubble sphere (distance c/H0) the recession velocity exceeds c; it is expansion of space, not motion through space, so relativity is not violated (Davis and Lineweaver 2004, "Expanding Confusion", PASA; [arXiv astro-ph/0310808](https://arxiv.org/abs/astro-ph/0310808)). Popular summary: [Universe Today](https://www.universetoday.com/articles/how-can-space-travel-faster-than-the-speed-of-light) | V (wording hedged) |

Never say: "faster than light travel", "something moves faster than light" (say "recede"), "the universe expands at X km/s" (no single speed), "warp". Never claim Earth's total speed through space: only "around the Sun". Label the reel "NOT TO SCALE" at the end.

## Shot plan (14 s)
Grammar: sideways track, one hero object centred and small, rings sweep through the camera, object grows to 35-65% of frame width, label and counter land after about 1 s, object slides out and the next is already ahead. Left ladder rungs: JET, BULLET, EARTH, PARKER, LIGHT with a red marker climbing (the Scale Ladder device). Palette: charcoal/navy, cream text, gold/teal accents, red only for markers, chips and the odometer unit chip. Safe zone y 220-1570; fonts per playbook 3.7 (Liberation Mono Bold).

| Time | Stop | Visual (designed) | Text | Counter (km/s) | Sound |
|---|---|---|---|---|---|
| 0-1.6 | **Hook** | Frame 0 is already moving: an airliner silhouette streaks across a dark sky, contrails | "HOW FAST IS [FAST]?" typed by 1.4 | 0 | Hit on frame 0 (small), rising wind-rush |
| 1.6-3.4 | **Jet** | Airliner centred, rings sweep, grows | "AIRLINER" / "900 KM/H" | 0.25 | Doppler pass-by, low |
| 3.4-5.0 | **Bullet** | Brass-and-copper rifle bullet, shock-cone, slow shimmer, passes jet | "RIFLE BULLET" / "~3,200 KM/H" | 0.9 | Crack pass-by, higher pitch |
| 5.0-6.8 | **You** | Earth with its orbit line, the camera flies along the orbit | "YOU, RIGHT NOW" / "EARTH AROUND THE SUN" | 30 | Deep sustained whoosh (not a hit) |
| 6.8-8.6 | **Parker** | Parker Solar Probe (heat shield disc, solar wings) diving past the Sun's limb, heat shimmer | "PARKER SOLAR PROBE" / "FASTEST HUMAN-MADE OBJECT" | 192 | Rising shepard sweep |
| 8.6-9.1 | **Held breath** | Hard cut to black, one thin gold line | none | frozen | Near-silence (about -40 dB) |
| 9.1-11.2 | **Light** | A single photon streak crosses the whole frame in one frame, leaving Parker as a dot; ratio chip | "LIGHT" / "~1,560X FASTER THAN PARKER" | 299,792 | HERO hit (biggest of the reel), sub wall, quiet |
| 11.2-13.5 | **Twist** | Galaxies (points of light) with a light beam crossing between them; the farthest galaxies drift away faster than the beam | "FAR GALAXIES RECEDE FASTER THAN LIGHT." then "(SPACE ITSELF STRETCHES.)" | hidden | Thin stretching tone, no hit |
| 13.5-14.0 | **Loop** | The jet from frame 0 flies back in from the left so the last frame matches frame 0 | "NOT TO SCALE" tag throughout the last beat | 0 | Rising rush into frame 0 |

The script asserts frame by frame that the counter never decreases (as overlay8 does).

## Sound plan
- New family: air-rush and Doppler pass-bys (synthesised noise and pitch-swept tones), pitch and brightness rising with speed. Not the Ladder's brass, not Night Sky's v4 palette.
- Hits only at frame 0 (small) and light (hero). Held breath before light. Everything else has a visual cause (pass-bys, ring crossings).
- Phone rules: HPF 90 Hz on all buses except the hit bus; target -15 LUFS; true peak measured after AAC; soft clip on the single loudest transient. All sounds synthesised, so no licences.

## Build plan
`tools/speed/`: `render.py` (PIL sprites, streaks, counter, ladder, chips; asserts the counter never decreases), `mix.py`. Compose: pic + mix with +2.3 dB and `alimiter ... level=disabled`, AAC 192k. Contact-sheet QA at 2 fps, true-peak check, loop check (last frame vs frame 0). No generation credits, no GPU rental.

## Publish copy (written after the build)
- Titles to test: "How fast is fast? Watch it climb", "You're moving at 30 km/s right now", "Light is not the fastest thing".
- Description: sources line (Guinness / NASA for Parker, Davis and Lineweaver 2004 for recession), "Animated explainer, not to scale". Pinned comment: "What's the fastest thing you've seen?"

## Open questions for the owner
1. Unit: one counter in km/s (consistent, my recommendation) or km/h for the first three stops (more familiar, but the counter would switch units).
2. Twist wording: "FAR GALAXIES RECEDE FASTER THAN LIGHT. (SPACE ITSELF STRETCHES.)" or the shorter "SPACE CAN STRETCH FASTER THAN LIGHT."
3. Keep the "YOU, RIGHT NOW" Earth beat as stop 3 (recommended) or swap it for a faster Voyager beat.

## v2 additions (17.1 s, built 18 Oct 2026)
- Status: BUILT v2. The 14 s v1 is kept as `tools/speed/render_v1_14s.py` and `mix_v1_14s.py`.
- Lap beat 11.7-14.4 s, after the light hit: Earth with a light beam circling its equator 7.5 times in 1.00 s (equator 40,075 km; 299,792 / 40,075 = 7.48). Lap counter 0 to 7.5 and a 0.00 to 1.00 S timer. Text: "LIGHT CIRCLES EARTH", "EQUATOR: 40,075 KM", then "IN ONE SECOND.". The equatorial circumference is TO CHECK against NASA before posting.
- Beat: 133 BPM (0.45 s grid). Kick on every beat from 1.8 s (rising level), hats from 3.6 s, claps from 5.4 s, snare roll and riser 7.2-9.0 s, near-silence 9.0-9.45 s, drop at 9.45 s (hero hit, crash, kick every beat, off-beat sub bass), one rising ping per lap, groove stops at 14.4 s into a quiet pad for the twist, rush into frame 0.
- Picture: objects pulse 3% on each kick, parallax bokeh layer, per-stop colour tint, screen shake on the drop.
- Timeline (s): hook 0-1.8, jet 1.8-3.6, bullet 3.6-5.4, Earth 5.4-7.2, Parker 7.2-9.0, held breath 9.0-9.45, light 9.45-11.7, laps 11.7-14.4, twist 14.4-16.65, loop 16.65-17.1.

## v3 (14.85 s, built 18 Oct 2026): faster hook and 15 s cut
- Hook: "HOW FAST IS [FAST]?" is fully on screen from frame 0 (no typing). 0-0.9 s is a flash montage of six unlabeled objects crossing in random directions (jet, bullet, Earth, Parker probe, light streak, galaxies), one short whoosh per object. The jet stop starts at 0.9 s instead of 1.8 s.
- Loop: the last frame matches frame 0 (jet in its frame-0 pose, hook text fades back in over the final beat).
- Trimmed by whole beats (0.45 s) so the groove stays aligned: jet and bullet 4 to 3 beats, twist 5 to 4 beats. Timeline (s): hook 0-0.9, jet 0.9-2.25, bullet 2.25-3.6, Earth 3.6-5.4, Parker 5.4-7.2, held breath 7.2-7.65, light/drop 7.65-9.9, laps 9.9-12.6, twist 12.6-14.4, loop 14.4-14.85.
- Audio: the 17.1 s mix with the same whole beats cut out (10 ms crossfades); measured arc: hook -19 dB, build -18 to -15, held breath -50, drop -11, laps -13, twist -26. 17.1 s versions kept as `render_v2_17s.py` and `mix_v2_17s.py`.

## v4 (15.3 s, built 18 Oct 2026): new hook (replaces the v3 flash montage)
- Beat 1 (0-0.45 s): "HOW FAST IS [FAST]?" on screen from frame 0, with Parker probe, Earth, bullet and airliner lined up one below another at the centre. Beat 2 (0.45-0.9 s): warp tunnel (radial speed lines, gold rings, centre glow, short flash) pulls the probe, Earth and bullet past the camera. Beat 3 (0.9-1.35 s): the airliner rises to the centre, grows and starts moving; the ladder starts with it at 1.35 s.
- Loop: the last beat re-assembles the line-up and fades the text back in, so the last frame matches frame 0.
- Timeline (s): hook 0-1.35, jet 1.35-2.7, bullet 2.7-4.05, Earth 4.05-5.85, Parker 5.85-7.65, held breath 7.65-8.1, light/drop 8.1-10.35, laps 10.35-13.05, twist 13.05-14.85, loop 14.85-15.3.
- Audio: frame-0 hit, tunnel whoosh and warp-tone sweep with three ring pings, a reverse suck into the first kick at 1.35 s; the rest is the v2 groove with whole beats removed. Measured: hook -17 dB, build -18 to -15, held breath -51, drop -11, laps -13, twist -26.
- Earlier versions kept: `render_v3_montage.py`, `mix_v3_montage.py`, `render_v2_17s.py`, `mix_v2_17s.py`, `render_v1_14s.py`, `mix_v1_14s.py`.

## v4b (option B, built 18 Oct 2026) and the new warp
- Two hook versions are rendered from the same code (`HOOK=A` line-up, `HOOK=B` bullet punch; `render.py`, `mix.py`). v4b: the warp is already running at frame 0 with a huge bullet centred (scale 1.1 growing to 2.0), gold rings, "HOW FAST IS [FAST]?" on top; the bullet punches past the camera at 0.9 s (flash, small boom, air burst) and the airliner emerges from the tunnel and starts the ladder at 1.35 s. Loop: the last beat brings the warp and bullet back.
- Warp look (both versions): a 3-D star field flying at the camera (perspective streaks, blue tails, white-hot heads, warm and cool chromatic fringe), perspective rings rushing outward, a hot core glow; intensity ramps with the beat.
- Audio: B has the warp whoosh and tone sweep from frame 0 and a punch at 0.9 s; A keeps the line-up hit and tunnel at 0.45 s. Same groove and drop afterwards. Measured: v4a -14.1 LUFS / -1.6 dBFS, v4b -13.8 LUFS / -1.7 dBFS after AAC.

## v4c (hybrid hook, built 18 Oct 2026)
- `HOOK=C`. 0-0.9 s: v4b (warp running at frame 0, huge bullet, "HOW FAST IS [FAST]?"). 0.9 s: the bullet punches past the camera (flash, boom, air burst) and the line-up (probe, Earth, bullet, airliner) pops in for one beat with three rising pings. 1.05-1.35 s: the probe, Earth and bullet are pulled into the tunnel with a whoosh; the airliner stays, rises to the centre and starts the ladder at 1.35 s. Loop: the bullet and warp re-form in the last beat. Total 15.3 s; measured -13.8 LUFS, true peak -1.6 dBFS after AAC.
- Recommendation: ship v4c if it reads well; otherwise v4b (simplest, strongest first frame).

## v5 (warp behind the whole ladder, built 18 Oct 2026)
- Reason: the hook (v4b/v4c) had the long 3-D warp streaks, but the stops after it still used short horizontal dashes and thin radar rings, so the hook looked like a different video. Reference image (line-icon tier list on a gold/blue warp) confirmed: keep solid 3D icons, use the warp background.
- Change: the warp now runs behind every stop with an intensity tied to speed (jet 0.18, bullet 0.26, Earth 0.36, Parker 0.5, drop 1.0 decaying, laps 0.3, twist 0.1); some streak heads are gold. Rings and the core glow are full-strength only in the hook and loop beat; the landing rings are halved; the horizontal dashes are a faint sideways cue. Held-breath beat stays pure black.
- Not done on purpose: line icons (looks like an infographic) and a "glowing radar circles" version (the circles compete with the object). The km/s number already sits under each object as the counter.
- Hook C audio is unchanged. Measured -13.8 LUFS, true peak -1.6 dBFS after AAC. Files: `render_v5_warp_bg.py`.

## v6 (deep-space backdrop, built 18 Oct 2026)
- Owner ask: a dark, semi-transparent space background that feels intimidating, immersive and enchanting.
- Backdrop (built once in `make_space()`, `render_v6_space.py`): dim nebula veils (teal, violet, ember) from layered noise, a faint diagonal Milky Way band with dust and dense tiny stars, 2,600 depth stars plus 46 brighter glowing stars with thin crosses, strong vignette, and a looming dark planet horizon in the lower third with a warm rim light. The canvas is 1.16x and drifts slowly so the sky is never static. Kept dim (nebula under about 30% brightness) so the objects and text still pop; the warp streaks run on top.
- The held-breath beat before the drop dims the whole backdrop to near-black so the drop hits harder. Bokeh circles are hidden in that beat.
- Output encoded at crf 22 with a 12 Mbps cap (23 MB for 15.3 s); v6 is the current build. Audio unchanged (-13.8 LUFS, true peak -1.6 dBFS).

## v7 (twisted-corridor background, built 18 Oct 2026)
- Owner pick: option A, the twisted corridor (from the grid / neon-tunnel / contour reference screenshots, "paradox: twists and plays with the mind"). `render_v7_corridor.py`.
- The corridor (`corridor_layer()`): a square corridor receding to the centre, with every ring rotated a little more than the one in front of it (a spiral staircase for the eye). Parameters change over time (`CKEYS`): twist 0.10 at the jet to 0.24 at Parker (the spiral tightens with speed), a full gold vortex on the drop (twist 0.36, fast forward motion, full brightness), slower behind the laps, violet and rolling a quarter turn through the galaxy twist ("faster than light" beat), then back to the frame-0 pose for the loop. Per-stop line colours: teal, amber, blue, gold, white-gold, violet. The held-breath beat stays black.
- The space nebula is kept but dimmed to 50% underneath. The hook keeps the 3-D star warp; the ladder no longer has the warp streaks (a short burst on the drop only), so the corridor carries the background.
- Audio unchanged: -13.8 LUFS, true peak -1.6 dBFS after AAC; 21 MB.
- Not built: contour-line (B) and dot-vortex (C) backgrounds (`bg_concepts.py` has the mockups).
- Lesson: never run two ffmpeg encodes to the same output file, and never `pkill -f ffmpeg` from the same shell (it kills the shell).

## v8 (black + vortex + magnetic aura, new sound; built 18 Oct 2026)
Owner direction after the reference images (bullet in a warp, airliner in a blue figure-8 aura, orange vortex, cyan flower aura, probe in a gold vortex): pure black, no stars or bokeh, the vortex alone carries the background, each object gets its own colour and a magnetic-field aura, new bold condensed type, smaller sizes, and sound that is the vortex rather than effects on top.
- Files: `render8.py`, `mix9.py`, `fonts/BebasNeue.ttf` (Bebas Neue, SIL Open Font Licence, from the @fontsource/bebas-neue npm package). Older builds kept (`render.py`, `mix*.py`).
- Timeline (13.05 s, beats of 0.45 s): jet 0-0.9, bullet 0.9-1.8 (hard cut), Earth 1.8-3.6, probe 3.6-5.4, held breath 5.4-5.85 (pure black), light/drop 5.85-8.1, laps 8.1-10.8, twist 10.8-12.6, loop 12.6-13.05. The ladder starts on frame 0 (no separate hook); the title "HOW FAST IS [FAST]?" sits top centre through the four stops; the object name sits under the object; the km/s counter is below that; the ladder is at the left.
- Colour = speed: jet blue, bullet orange, Earth cyan, probe gold, light white, laps gold, galaxies violet. Vortex: jet barely twisted, bullet 3x the twist, Earth faster spiral, probe full wormhole spin, light a white wormhole, twist violet and slow. Colour, twist and spin snap on each cut (0.12 s).
- Aura: nested lens-shaped field loops joining the object's nose and tail; faster object = more loops, taller, brighter, thicker, more distorted (levels 0.30, 0.52, 0.76, 1.0).
- Type: Bebas Neue, title 104 px, object name 60, sub-line 34, counter 100, red box only on FAST (top) and on the unit chip (KM/S, LAPS, the ratio chip), never anything else.
- Counter: stops snap to their exact value on the cut (0.25, 0.90, 30, 192); only the leap to 299,792 km/s rolls (0.3 s). The lap counter runs 0 to 7.5 in sync with the 0.00-1.00 S timer by design (so "5 LAPS" at 0.67 s is correct, not an error).
- Sound (`mix9.py`): no pings, drum machine or sine arpeggios. Per tier: a magnetic hum (harmonic stack, pitch jumps an octave at the bullet), a sub rumble, a whistle that follows the vortex spin (rotating pan), electric zaps from the bullet on, a dry rifle crack with a reversed-cymbal tail after 0.1 s of near-silence at the bullet cut, a bloom pad, orbital drone and 60 bpm heartbeat for Earth, a whiteout wash, metallic screech and Shepard riser for the probe, silence at the held breath with a thin 11 kHz tone creeping in, a cinematic impact on the light cut that falls away to a thin ringing tone ("light has no sound"), one whip of air per lap (7.5 per second, pitch climbing) locked by a low thump, a low unresolved drone for the twist, and a rush into frame 0. Tier loudness climbs jet -28, bullet -23, Earth -17, probe -14, drop -11 dB RMS. -14.3 LUFS, true peak -3.2 dBFS after AAC.
- Not adopted from the Meta suggestions: a pure 15 kHz tone (harsh on phones; 11-12.5 kHz at very low level instead) and a 0.5 s total silence before the light drop (the held breath is already 0.45 s).
