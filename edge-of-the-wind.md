# The Edge of the Wind (reel 13, 22 s, no voiceover)

Remake of the reference "This Is the Bubble That Shields Our Solar System" (32 s, a heliosphere bubble flying through a galaxy, cluttered labels), rebuilt from the brief in `ref-remakes-plan.md`. Ours rides Voyager 1 outward through the Sun's wind, crosses the two real boundaries it measured, then pulls out to show the whole bubble.

Files: `edge-of-the-wind.mp4` (share size, 28 MB, about 9.8 Mbps) and `edge-of-the-wind-hq.mp4` (67 MB, 24 Mbps, use this for the YouTube upload). Both (9:16, 1080x1920, 30 fps, 22.0 s, loops: the last frame dives back into the Sun shot that opens the reel). Final copy lives in the project folder `final-reels/`; renders are not in git.
Source: `tools/edge-of-wind/` (`index.html` scene, `render.js`, `proj.js`, `overlay.py`, `mix.py`, `shot.js`). Rebuild steps at the end.

## Concept
- **One idea:** the Sun blows a wind, the wind blows a bubble, and we live inside it. Voyager 1 is the only way we know where the bubble ends.
- **Hook (frame 0):** a hit on frame 0 over a close, moving Sun spraying wind past Voyager; "THE SUN HAS A **WIND.**" is typed by 1.7 s.
- **Monotonic device:** one AU odometer with the matching year under it (1977, 2004, 2012), and a left ladder SUN / NEPTUNE / SHOCK / HELIOPAUSE whose red marker climbs with the distance. Both only go up (the overlay asserts it frame by frame).
- **Paradox beat:** at the termination shock the wind does not stop, it slams on the brakes. The fast gold streaks turn into a slow, churning teal plasma, and the sound collapses from a roar to a rumble.
- **Reveal:** held breath, then the heliopause. The streaks flip to violet interstellar gas pouring the other way. The camera pulls out to the whole bubble with Voyager a red-ringed dot on its nose.
- **Thesis:** "WE LIVE **INSIDE IT.**" with a ring on the Sun, then a plunge back to frame 0.

### What makes it ours (vs the reference)
- A ride, not a flyover: the viewer stays with one craft, and both boundaries are crossed on screen with a label at the moment of crossing.
- Every boundary is target-first: the shock arc and the heliopause arc slide down into frame before Voyager reaches them.
- The flow itself tells the story: three particle regimes drawn from one velocity field (fast radial wind, slow turbulent heliosheath, interstellar gas deflected around the heliopause).
- New hero designs that no other Slow Light reel uses: a golden granulated Sun with an eclipse-style streamer corona; a procedural Voyager 1 (dish, gold bus, magnetometer boom, RTG boom, science platform); boundaries as glowing conic shells. No galaxy plate, no ring tunnel, no H-alpha Sun.
- Original sound family built from scratch in numpy (no samples): plasma-wind roar, telemetry pings, a plasma whistle after the heliopause.

## Shot plan (video seconds)
| Time | Shot | On screen |
|---|---|---|
| 0.0-2.0 | Close on the Sun (corona streamers), wind streaks spray past Voyager just above it; frame-0 hit | "THE SUN HAS A WIND." |
| 2.0 | Snap: camera surges outward with the wind | odometer appears: VOYAGER 1 · 1977, 1.x AU |
| 2.0-5.6 | Riding the wind; planet orbits fall away below | SOLAR WIND · "400 KM/S · CROSSES EARTH IN 32 SECONDS" · tag VOYAGER 1 |
| 6.15-8.1 | Past Neptune's orbit (30 AU); wind streaks lengthen | PAST NEPTUNE · "AND THE WIND KEEPS BLOWING" |
| 8.0-9.6 | Teal shock arc slides down to Voyager (target first) | odometer climbs to 94 AU |
| 9.6 | Crossing: medium hit; gold streaks die at the line, slow teal turbulence beyond | TERMINATION SHOCK · 94 AU · 2004 · "THE WIND SUDDENLY SLOWS" |
| 9.6-13.4 | Heliosheath: stagnant, swirling plasma; heliopause arc appears ahead (about 12 s) | odometer 94 to 118 AU |
| 13.4-14.0 | Held breath (near silence) | |
| 14.05 | Crossing: biggest hit; violet interstellar gas streams down past the craft | HELIOPAUSE · 121 AU · 2012 · "THE SUN'S WIND STOPS." (odometer and ladder fade at 15.4 as the camera pulls out) |
| 14.6-18.8 | Pull-out to about 1,000 AU: both shells, radial wind inside, interstellar gas flowing around the nose and down the tail; Voyager a red-ringed dot | 15.2-16.8 "INTERSTELLAR SPACE / BEGINS HERE.", then 16.9-19.2 "THE SUN'S WIND BLOWS A BUBBLE / AROUND EVERY PLANET." |
| 19.2-21.0 | Hold on the bubble, red ring on the Sun | "WE LIVE INSIDE IT." |
| 20.9-22.0 | Plunge back to the Sun close-up (match to frame 0) | |

Camera grammar: one axis. Voyager flies straight up the frame along the heliosphere's nose direction, the camera tracks it from the side (log-keyed distance 3 to 24 AU, slight orbit for parallax), boundaries are arcs crossing the frame. The pull-out is the only break from the axis.

## Facts and sources
| On screen | Fact | Source |
|---|---|---|
| Solar wind 400 km/s | Typical (slow) solar wind near Earth is about 300-500 km/s; fast wind reaches about 750 km/s. 400 km/s is the standard round figure. | NASA Solar System Exploration, "Sun: Facts" / NASA Parker Solar Probe mission pages |
| Crosses Earth in 32 seconds | Earth's diameter 12,742 km / 400 km/s = 31.9 s. | arithmetic |
| Termination shock, 94 AU, 2004 | Voyager 1 crossed the termination shock on 16 Dec 2004 at about 94 AU. | Stone et al., "Voyager 1 Explores the Termination Shock Region and the Heliosheath Beyond", Science 309 (2005), https://resolver.caltech.edu/CaltechAUTHORS:20140826-084449577 ; UMD Physics, "After a 27-year Journey, Voyager 1 Enters the Heliosheath", https://physics.umd.edu/news/photon/iss45/researchspotlight.htm |
| The wind suddenly slows | At the shock the solar wind drops from supersonic to subsonic. Voyager 1's plasma instrument stopped working in 1980, so for Voyager 1 the slowdown was inferred from its particle and magnetic-field instruments; Voyager 2 measured it directly at its own crossing in 2007. Deeper in, Voyager 1 found the outward wind speed fell to about zero (Krimigis et al., Nature 2011). | Stone et al. 2005; Krimigis et al., Nature 474 (2011) |
| Heliopause, 121 AU, 2012 | Voyager 1 entered interstellar space on 25 Aug 2012 at about 121 AU (18 billion km). | NASA JPL, "Interstellar Voyager", https://www.jpl.nasa.gov/interstellarvoyager/ ; Univ. of Iowa (Gurnett), https://now.uiowa.edu/node/22441 |
| Year under the odometer | Launch 5 Sep 1977; the year is interpolated between the two real crossings, so it lands on 2004 at 94 AU and 2012 at 121 AU. | as above |
| The bubble surrounds every planet | Neptune orbits at about 30 AU; the termination shock in Voyager 1's direction is at 94 AU, so all planets are deep inside the heliosphere. | NASA |
| Plasma whistle in the sound | After the crossing, Voyager 1's plasma-wave instrument recorded electron plasma oscillations at about 2.6 kHz (density about 0.08 per cm³). The mix uses a faint narrow band near that frequency; it is a nod, not a recording. | Gurnett et al., "In Situ Observations of Interstellar Plasma With Voyager 1", Science 341 (2013) |

Accuracy notes (keep these in the copy or in replies to comments):
- **Thought experiment / not to scale.** The Sun and Voyager are drawn hugely oversized, flow speeds are stylised, and time is compressed (35 years in about 12 s).
- The heliosphere's true shape is still debated (comet-like tail, "croissant", or rounder). The reel draws a generic nose-and-tail bubble and never states its width.
- Voyager 1 flies roughly toward the nose, about 35° north of the planets' plane; the reel straightens the path for readability.
- Say "Voyager 1 crossed the heliopause", not "left the Solar System" (the Oort Cloud is far beyond).
- Next month (17-18 Nov 2026) Voyager 1 reaches one light-day from Earth (EarthSky, https://earthsky.org/space/voyager-1-1-light-day-from-earth-november-17-18-2026/). Good pinned-comment hook; not used on screen because it would date the reel.

## Sound (own family, fully synthesized)
Built in `tools/edge-of-wind/mix.py` with numpy only, so there are no third-party samples and no credits to paste.
- 0.0 frame-0 hit (crack + saturated pitch-drop body + bell partials + small sub), corona crackle and hiss, warm A-minor pad.
- 2.0 small snap hit; solar-wind roar from band-passed pink noise whose centre rises 220 Hz to 1.6 kHz with speed; short whooshing streak grains.
- Voyager telemetry pings every 1.6 s (2.2 kHz); after the heliopause they come back fainter, with echoes, as if farther away.
- 9.6 shock hit (medium); the roar cuts to a slow, churning low rumble with random teal plinks.
- 12.45 riser, 13.4-14.0 held breath at about -34 dB, suck swell and vacuum, 14.05 the biggest hit with gong partials and sub.
- Interstellar bed: low D drone, wide head-wind whoosh, plasma whistle near 2.6 kHz. Bell on "WE LIVE INSIDE IT." Plunge whoosh and rising tone into frame 0.
- Sub only on the hit bus; everything else high-passed at 90 Hz. Mastered to -15.5 LUFS integrated, true peak -0.6 dBFS measured on the final AAC files.

## Publish copy

### YouTube Shorts
**Title (pick one):**
1. The Sun has a wind. Voyager 1 found where it ends.
2. Where does the Sun's wind stop? 121 AU.
3. Ride with Voyager 1 to the edge of the Sun's wind

Recommended: option 1 (matches the hook).

**Description:**
> The Sun has a wind: a stream of charged particles blowing out at about 400 km/s, fast enough to cross Earth in 32 seconds.
>
> Voyager 1 launched in 1977 and rode that wind outward.
> In 2004, 94 AU from the Sun, it crossed the termination shock, where the wind suddenly slows.
> In 2012, at about 121 AU (18 billion km), it crossed the heliopause, where the Sun's wind stops and interstellar space begins.
>
> The wind blows a bubble around every planet. We live inside it.
>
> A thought experiment: sizes, speeds and time are compressed and not to scale. 3D-rendered visualisation. Sound designed from scratch.
>
> Sources: NASA JPL (Interstellar Voyager); Stone et al., Science 2005; Gurnett et al., Science 2013.

**Hashtags:** #space #voyager1 #nasa #solarwind #heliosphere #astronomy #science #shorts

**Pinned comment:**
> Next month Voyager 1 will be one light-day away: a message from Earth will take a full 24 hours to reach it. It is still sending data from interstellar space, 49 years after launch.

### Instagram / Facebook Reels
**Caption:**
> The Sun has a wind. 🌬️☀️
> Voyager 1 rode it for 35 years: termination shock at 94 AU (2004), heliopause at 121 AU (2012). Past that line, the Sun's wind stops and interstellar space begins.
> Every planet lives inside this bubble.
> (Thought experiment, not to scale.)
> #space #voyager1 #nasa #solarwind #heliosphere #science #astronomy #reels

### Upload checklist
- Turn on the altered/synthetic content label (it is a simulation of real events).
- No music or sample credits needed (all sound synthesized in-house).
- Post as is; the reel loops (last frame dives back into the opening Sun shot).

## Rebuild
From `tools/edge-of-wind/` (needs `three@0.170.0` and `playwright-core` in `node_modules`, Chromium at `/opt/pw-browsers/chromium-1194`, ffmpeg, Python 3 with numpy and Pillow):
1. `python3 -m http.server 8790` in this folder.
2. Stills: `node shot.js 540 960 out 8790 0 7 9.6 14.3 18.5`.
3. Frames (4 workers): `node render.js 1080 1920 frames K 660 4 8790` for K = 0..3 (about 2.5 s per frame per worker on 4 CPU cores, 2 motion-blur subframes).
4. Screen positions: `node proj.js proj.json 8790`; overlay: `python3 overlay.py proj.json overlay.mov`.
5. Sound: `python3 mix.py mix.wav`.
6. Composite: `ffmpeg -framerate 30 -i frames/f%04d.jpg -i overlay.mov -i mix.wav -filter_complex "[0:v][1:v]overlay=format=auto,format=yuv420p[v];[2:a]volume=-3dB,alimiter=limit=0.89[a]" -map "[v]" -map "[a]" -c:v libx264 -crf 17 -preset slow -c:a aac -b:a 192k -movflags +faststart edge-of-the-wind.mp4`, then measure loudness and true peak on the MP4 (`ebur128=peak=true`).

## Known nit
- The loop is a match on the Sun shot, but Voyager is not in the last frame (it sits at 124 AU) and is back above the Sun on frame 0; the frame-0 hit covers the change.
