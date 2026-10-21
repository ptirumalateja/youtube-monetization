# One More Shovel (14.0 s, v1, no voiceover): spec, build and publish copy

Reel #16 from `ref-remakes-plan.md` ("You never know how close you are to where you want to be", a 12 s two-stickmen-and-a-rock clip). We keep the theme and nothing else: our own stickman rig (from `tools/shadow-stickman/`), our own world (a cross-section of the ground at night), our own text, our own procedural sound. Built in three.js (`tools/one-more-shovel/`).

## Concept
A stickman digs a well under a wooden tripod and a hanging lantern. We watch in cross-section, so we can see what he can't: under the layers of soil, clay, sand and stone, the water table glows teal in the gravel. The depth counter climbs with every shovel. He slows, stops at 9.8 m, looks up at the sky and climbs out. The water was 20 cm below his feet. Closing line: KEEP DIGGING.

Why it works: the viewer sees the water coming for 2-3 s while he tires (tension, "keep going!"), the stop is a perception gut-punch, the 20 CM chip makes it measurable, and it works on mute.

## Look
- Night: navy sky with stars, dry cracked ground, a three-leg wooden tripod, rope and lantern lowered with him.
- Cut face of the earth, softly lit by a cool fill plus the lantern's warm spill. Strata (top down): topsoil with root lines, banded clay, sand with gold glints, stones in a dark matrix, dense blue clay that darkens with damp near the bottom, then the aquifer: gravel with teal water glowing in the pores (shimmering) and a bright water-table line. A cream outline traces the shaft and the ground line like a diagram.
- Stickman: thick cream round-capped tubes (same rig family as the Shadow reel), IK hands on the shovel, IK feet.
- Red only for the 20 CM bracket and chip. Bloom, teal-shadow/warm-highlight grade, vignette, grain.

## Shot plan (timeline.json is the single source of truth)
| Time | Shot | Sound |
|---|---|---|
| 0.00 | Hit: the first shovel bites the ground at the surface; hook typed by 0.85 s: HE'S DIGGING FOR WATER. Counter DEPTH 0.1 M | big shovel hit, wind |
| 0.6-1.8 | Two more deliberate strokes at the surface, clods fly | shovel chunks, tosses |
| 1.15-2.05 | Camera dives through the ground line into the cross-section (pattern interrupt) | wind drops away, earth drone |
| 2.1-6.0 | Time-lapse: 15 fast strokes, the camera rides down with him through clay, sand, stones; counter 0.9 -> 8.0 M | fast chunks + counter ticks, drone darkens |
| 6.0-8.4 | Four slow, tired strokes (8.6, 9.1, 9.5, 9.8 M); camera eases back and the glowing water rises into the bottom of frame. We see it; he doesn't | heavier strokes, tired breaths, water plinks grow |
| 8.6-9.3 | He straightens, leans on the shovel, looks up at the circle of sky | long exhale |
| 9.18-9.46 | He lets the shovel fall; it clatters against the wall | clang, cut short |
| 9.46-9.80 | Held breath: hands on the rope | near silence, reverse suck, 50 ms vacuum |
| 9.80 | Reveal hit: he starts climbing; red bracket between his floor and the water table; chip 20 CM; caption THE WATER WAS ONE SHOVEL AWAY. | underwater boom, bubbles, teal glass chord |
| 9.8-11.9 | Camera pushes in on the 20 cm gap; he climbs out of frame; water beads up through the floor he left | rope creaks, seep trickle, plinks |
| 11.9-12.8 | Whoosh back up the shaft to the frame-0 composition | rising sweep |
| 12.8-14.0 | Surface: he walks away into the dark, head down. End line KEEP DIGGING. Everything clears by 13.95 | wind, footsteps, bell, rising tone into frame 0 |
| 14.0 -> 0.0 | Loop: back to the first shovel | frame-0 hit |

Counter: one odometer, DEPTH in metres, steps on each impact, script-asserted monotonic (0.1 -> 9.8 M). Small tag under it: A PARABLE · NOT TO SCALE.

## Facts and sources
The reel is a parable, so the only numbers on screen are its own (9.8 m dug, water table at 10.0 m, gap 20 cm). The picture of the ground is drawn to be honest:
- Groundwater is not an underground lake. It fills the pores and cracks of soil, sand, gravel and rock below the water table (the top of the saturated zone). That is why the aquifer is drawn as gravel with water glowing between the stones, and the clay above it darkens with damp near the water table. Source: USGS Water Science School, "What is groundwater?" https://www.usgs.gov/water-science-school/science/groundwater-what-groundwater and USGS FAQ https://www.usgs.gov/faqs/what-groundwater
- Dug wells are the oldest kind of well and are shallow, reaching only the upper part of the water table; that is why a ~10 m hand-dug shaft is a plausible setting. Source: USGS Water Science School, "Groundwater wells" https://www.usgs.gov/water-science-school/science/groundwater-wells
- Layer thicknesses, the shaft width and the time-lapse are compressed (hence "not to scale").

## Sound
Procedural in numpy (`mix.py`), no samples, so no licence credits are needed. Family: earth and water (new for this reel; nothing reused from Night Sky, Scale Ladder or Shadow). Hits only at frame 0 and the 9.80 s reveal; energy kept in the 90-400 Hz band for phones. Delivered at -15.1 LUFS, true peak -3.1 dBFS after AAC (mix.py has a look-ahead limiter and a soft attack on the cracks; an earlier pass clipped AAC on the frame-0 transient).

## Build (tools/one-more-shovel/)
- `gen_timeline.py` -> `timeline.json` (stroke times and depths, events, text).
- `index.html` (scene, `window.renderAt(t)`), `shot.js` (test stills), `render.js` (frames), `proj.js` (chip anchor positions), `overlay.py`, `mix.py`, `build.sh`.
- Rebuild: `npm i`, `python3 -m http.server 8790 &`, then 4 workers `node render.js 720 1280 $FRAMES $i 420 4` (i = 0..3), then `FRAMES=$FRAMES OUT=one-more-shovel.mp4 ./build.sh`. About 25 min on 4 CPUs (SwiftShader).
- Output: `final-reels/one-more-shovel.mp4` in the project files (1080x1920, 30 fps, 14.0 s, 21 MB, H.264 CRF 20 + AAC 192k).

## Publish copy
**YouTube Shorts title:** He Stopped 20 cm From Water #shorts

**Description:**
He dug 9.8 metres for water. Then he gave up.
The water was one shovel away.

You can't see how close you are. Keep digging.

A parable, not to scale. Groundwater fills the gaps between grains of sand and gravel, not underground lakes (USGS).

#shorts #motivation #neverquit #keepgoing #stickman #mindset #slowlight

**Instagram / Facebook caption:**
9.8 metres down. 20 cm to go. He never saw it. 💧
Tag someone who needs to hear "one more shovel."
#keepdigging #motivation #neverquit #mindset #stickman #reels #slowlight

**Pinned comment:** Where would you have stopped? 👇

**Upload checklist:** AI/synthetic label on (rendered 3D); no music credits needed (procedural sound); loop-friendly, so leave as a Short (no end screen).
