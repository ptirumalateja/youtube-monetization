# Night Sky v8: frozen shot plan (one build, checked against this table before delivery)

Status: APPROVED and BUILT as `night_sky_past_v8_A.mp4` (18.6 s). Scripts in `tools/night-sky-v8/` (scene8_*.js are assembled by build.py as keep + streak + andro + grade + main).
One deviation from the table: because the Moon fills about 65% of the frame while we hold on it, the Sun is revealed at the centre as the Moon slides away (about 4.45 s) instead of being visible behind it from 4.0 s.

## Why v7 was still hard to read (root causes)
1. The camera path and the objects were not on one axis. The Moon sat off to the right, and the camera "looked at" each object through a blend, so the object slid across the frame instead of growing at the centre.
2. Every object had its own gate placed along the path tangent, not along the line to the object. The camera skimmed the ring edges instead of flying through the opening.
3. A second star (Proxima's glow and burst) was visible while the Sun was still the subject, and the Sun's flare competed with its own shape.
4. The Andromeda halo rings were switched on about 0.5 s before the reveal and drawn at their own scale, so they looked like a pasted transition asset.
5. The look-back galaxy was a procedural bar-and-arms disc seen face-on. It read as a shuriken, not as "our galaxy".

## Camera grammar (one rule for every transition)
- Everything sits on ONE forward axis. The camera looks straight down that axis the whole time. Field of view never changes. No roll, no look-at blending. A 3 degree bank is allowed only while passing an object.
- TARGET FIRST: the next object is visible as a small point at the exact centre of frame before the camera accelerates toward it.
- RINGS: only circular rings, always centred on the axis. The vanishing point is the centre of the frame. The camera flies through the openings one by one and the rings sweep out to the frame edges. Ring colour = colour of the target.
- The previous object slides out of frame sideways and shrinks as the camera passes it. The next object is already ahead.
- ONE LABEL PER OBJECT, appearing when that object is recognisable (at least about 40% of frame width). The counter ticks up from 0 to its value while a light ripple travels from the object to the viewer, so the viewer sees "this object sent this light this long ago".
- No white-outs. Maximum flash 12%. Palette stays deep navy-black, warm gold, one red accent (chips, marker, ring).

## Shot table (new timeline)
| Time | Camera | What the viewer sees (angle, size, light) | Text and counter | Sound |
|---|---|---|---|---|
| 0.0-2.1 | Plate | Stargazer under the Milky Way, star flares, ring closes round the star | `YOU'RE SEEING THE PAST.` typed 0.35-1.9 | Hit on frame 0, typing ticks, spark charge-up, riser + suck |
| 2.1-2.9 | Straight in through the star's ring, centred | The star's light expands into ring 1 (no white-out). At 2.5 a small silver disc appears at the centre inside the ring (the Moon, target first) | none | One snap at 2.1, then whoosh through the ring |
| 2.9-4.4 MOON | Dead ahead, 4 silver rings pass through the centre 2.9-3.5, then a slow glide | Moon grows from a disc to about 65% of frame width, centred, lit from the right, craters visible. Hold 3.5-4.4 | at 3.3: `THE LIGHT YOU SEE LEFT` / counter 0 to `1.3 SECONDS AGO` / chip `THE MOON` / `MOONLIGHT TAKES 1.3 SECONDS TO ARRIVE`. Ladder marker at MOON | Airy glass pings on the ring crossings, soft whoosh, light ripple tone as the counter ticks |
| 4.4-4.95 | Slight bank right, Moon slides left and shrinks | A small gold disc (the Sun) already sits at the centre ahead since 4.0 | label fades | Whoosh |
| 4.95-6.3 SUN | Dead ahead through 3 gold rings, then glide | Sun is a clear round golden disc with a soft corona, about 60% of width, centred. Flare and streak reduced to a quarter of v7 so the shape stays readable | at 5.2: counter 0 to `8 MIN 20 SEC AGO` / `THE SUN` / `IF IT VANISHED NOW, YOU'D STILL SEE IT` | Warm fire-crackle bed, rising air, ripple tone |
| 6.3-6.85 | Sun slides out; all Sun glow, streak and halo are at zero by 6.5 | Exactly ONE target ahead: a small red-orange star at the centre. No other bright object on screen | label fades | Whoosh |
| 6.85-8.2 PROXIMA | Dead ahead through 3 red rings | Proxima is a red-orange sphere, about 35% of width, soft red halo, a quiet flare. Nothing else bright | at 7.1: counter 0 to `4.2 YEARS AGO` / `PROXIMA CENTAURI` / `THE NEAREST STAR AFTER THE SUN` | Cold thin pings, light sparks |
| 8.2-10.0 HYPERDRIVE | Dead ahead, speed ramps | A true ring tunnel on the axis: rings stream through the centre and sweep to the edges, colour drifts red to blue-white. At 9.3 a faint gold and blue oval glow appears at the vanishing point (Andromeda, target first) | counter climbs `4.2 YEARS` to `2,500,000 YEARS AGO` | Accelerating pulse, riser, stutter |
| 10.0-10.5 | Almost stops | Andromeda is a small bright oval at the exact centre, rings stopped. No double halo, no ring overlay | label holds the last number | Near-silence (held breath) |
| 10.5-12.6 ANDROMEDA | Straight in along the axis | A soft light bloom (no shockwave ring), then the galaxy opens: tilted, gold core, blue arms, dust lanes, companions. Structure is kept (no white core). It fills the frame by about 12.0 | `2.5 MILLION YEARS AGO` / `ANDROMEDA GALAXY` / `BEFORE MODERN HUMANS EXISTED` | The single big hit (braaam), then a wide spacious tail |
| 12.6-14.4 PULL-BACK | The camera swings out sideways and up in one arc | Andromeda shrinks to a bright node on the right. Our galaxy is a small node on the left. A thin light beam joins them and a light pulse runs along it. Red ring on our node. Both are glowing points, no spiral detail, so no shuriken | `FROM THERE, THEY'D SEE EARTH AS IT WAS 2.5 MILLION YEARS AGO. NO MODERN HUMANS YET.` (shown not to scale) | Slow choir hush, low pulses, one soft ping |
| 14.4-15.6 FALL HOME | Dive along the beam into our node | Stars flood past, then a single star dead ahead at the centre (our star) | ring on our spot grows and fades | Riser, whoosh, suck |
| 15.6-16.0 | Dissolve (no flash) | The star carries over to the same position in the stargazer plate | none | Soft landing thud |
| 16.0-19.0 | Plate | Stargazer under the Milky Way, the landscape settles | `YOU'RE LOOKING AT THE PAST.` typed 16.15, holds, loops to frame 0 | Wind, bell, crackle re-ignition, rise into frame 0 |

Persistent UI (kept, you liked it): vertical time ladder on the left, NOW at the bottom, rungs MOON / SUN / PROXIMA / ANDROMEDA, red marker climbing. Tag `THOUGHT EXPERIMENT · NOT TO SCALE` stays.

## Removed from v7
Betelgeuse, chained gates, the Andromeda double halo before the reveal, the shockwave ring, the pinwheel look-back galaxy, the second competing star during Sun to Proxima, look-at blending, banking between stops.

## What the audience should perceive (check list)
1. "I started on Earth." 2. "Moon: its light is 1.3 seconds old." 3. "Sun: 8 minutes." 4. "Proxima: 4 years." 5. "Faster and faster, the age climbs." 6. "Andromeda: 2.5 million years." 7. "Someone there sees our past." 8. "I am always looking at the past."

## Sound plan (different family from the Scale Ladder)
- Scale Ladder keeps the brass-and-sub family: chakong braaam, bass drop, harmonic pings on a 106 Hz root.
- Night Sky uses a time-and-glass family: tick or odometer pulse tied to the counter, glass pings, electric sparks, portal and warp whooshes from the library (portal gate opening, fast warp in, sci-fi gateway, sword in air), circuits hum under the hyperdrive, long impact and screaming echo (Uppbeat) as the single Andromeda hit, wind at the ends. The chakong braaam is NOT used here.
- Hits only at 0 s, 2.1 s, 10.5 s and the soft landing. Everything else is a continuous bed with whooshes and pings.
- Helpful new files if available (all optional): a slow mechanical clock tick loop, bowed or glass harmonic drones, a clean choir or pad swell.

## v8.1 correction pass (`night_sky_past_v81_A.mp4`, 19.2 s)
Feedback: counter jumped backwards, ladder and caption too small, Sun close-up too bright, a diffuse bright field before the stargazer, and the v8 sound was not the v4 sound.
- Sound: the v4 cue sheet (`mix4.py`) is reused as-is up to the Proxima pass (its timings already match the ring crossings at 3.0 / 5.0 / 7.0 s); the hyperdrive riser, jet, pulses and ticks are re-fitted to the 1.65 s tunnel, the hero hit moves to 10.5 s, and the dive home uses v4's own reverse-whoosh pre-roll, riser slice and warp-in followed by v4's 0.3 s silence before the wind returns (`tools/night-sky-v81/mix_night81.py`). Every sample is a v4 sample; the v8 glass/tick/shepard sounds are gone. Loudness: -15.2 LUFS, -3.0 dB peak after AAC (a soft-clip on the single hero transient keeps AAC from overshooting).
- Counter: one odometer that only goes up across the whole video (0 to 1.3 s, then 8 min 20 s, then 4.2 years, then 2.1 million, then 2.5 million years); the overlay asserts monotonicity frame by frame at build time and pluralises correctly.
- Ladder: names only (NOW / MOON / SUN / PROXIMA / ANDROMEDA) at 36 px, active rung lit at 42 px, larger red marker with pulsing ring. Caption: 54 px, three lines plus a red chip "NO MODERN HUMANS YET.", held about 0.5 s longer (slow-motion window 14.0-15.0 s in the scene clock).
- Sun: camera passes farther out, Sun and its glows are dimmed while we pass, Sun fades out earlier; only Proxima is left ahead. Dive home: node glow and points fade with distance, Andromeda is removed once we turn back, dust capped, so the last frames are a dark-blue sky with one star and ring, dissolved into the plate.
