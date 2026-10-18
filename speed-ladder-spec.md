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
