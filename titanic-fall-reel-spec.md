# Slow Light: "It Fell" (Titanic, 3.8 km descent) | v1 locked spec

**Decision date:** 2026-10-24
**Status:** Concept, timeline, hook and visual bar agreed (angle 1: "It fell for 3.8 km"). **Nothing is built yet.** Facts marked *verify* must be checked against the listed source before the overlay is rendered.
**Format:** 9:16, 1080x1920, 30 fps, **24.0 s**, wordless (visuals, sound design and a few words of on-screen text), loops.
**Camera grammar:** a new third language, **C. Descent (one vertical axis)**. It follows the Night Sky rules (one axis, target first, one label per stop, monotonic counter) turned 90° to point down.
**Visual bar:** this reel is the showcase for three.js. Every shot has to stand up as a still frame (see §4 and gate G1). If a frame looks like a game engine demo, it fails.

Read `slow-light-design-playbook.md` first. Everything there applies unless this spec overrides it.

---

## 1. The idea in one line

People picture the Titanic going under the surface and stopping. In fact the bow fell **3.8 km** through the dark, a depth of **14 Titanics stood end to end**, and it stayed there unseen for **73 years**.

What the audience should take away, in order:
1. "That's the Titanic going under, at night."
2. "We're following it down."
3. "The light is going: first the colours, then everything."
4. "It's still falling. How deep is this?"
5. "It hit the bottom: 3,800 m."
6. "That's 14 Titanics deep."
7. "Nobody saw it again for 73 years. It's still down there."

## 2. Accuracy and respect rules (hard)

- **The ship broke in two at the surface.** Underwater we follow the **bow section** (about 2/3 of the ship, with a torn aft end), not a whole ship. The opening shows the stern, which went under last, near vertical. The ghost ruler in §3 uses the whole ship's length (269 m) and says so.
- The forward funnel fell before the break, and the others tore off on the way down: the falling bow has **no funnels**, only the openings and the stubs where they stood. The foremast stays upright until impact, then folds back against the deck (as found on the wreck).
- 1912 paint: black hull, white superstructure, gold band, **red antifouling below the waterline**. The red is the colour-loss beat in §3 (red is the first colour water absorbs).
- **The sky that night:** moonless and starry, with a glassy flat calm sea (survivor accounts). Show it that way: no waves, no storm, no moon.
- **No people.** No figures, lifeboats with occupants, bodies, belongings or debris that reads as personal. Lights go out before frame 0 so there are no lit windows to imply people. The tone is awe and scale, never spectacle.
- No clips, stills or score from the 1997 film, nothing that sounds like its theme, and no mention of the 2023 Titan submersible.
- **Tag:** `DEPTHS TO SCALE · TIME COMPRESSED` (the descent takes about 10 s on screen, not the real minutes). The fall time is not shown on screen.

## 3. Shot table (frozen plan; check every build against it)

World: the vertical axis is Y, the surface is at y=0, and **1 world unit = 1 m**. Depths are true. The camera falls along the axis beside the bow, and the bow stays near the frame centre.

| Time | Camera | What the viewer sees | Text / counter / ladder | Sound |
|---|---|---|---|---|
| 0.0-1.9 HOOK | Low at sea level, about 300 m away, slow push-in (moving on frame 0) | Starfield over a black glassy sea, stars reflected. The stern's dark silhouette, near vertical, slides under. Ring ripples spread across the reflections. No lit windows | `IT DIDN'T JUST SINK.` typed 0.15-0.9, then `IT FELL.` 1.1-1.6 (Hook A) | Frame-0 hit: a deep hull groan + water hit. Water hiss, rising pressure tone |
| 1.9-2.5 SNAP | The camera tips down 90° and plunges through the surface where the stern went | Breaks through the surface: bubble burst, then from below, the **Snell's window** (a bright circle of night sky, with mirror-dark water outside it) shrinks overhead. Below, at the exact centre: a dark sliver, the bow (target first) | Hook clears. Counter appears at `0 M`. The ladder slides in | Snap: crack + underwater "whump" (low-passed), then everything muffled |
| 2.5-5.6 SUNLIGHT ZONE (0-200 m) | Falls fast, catches up with the bow, then falls beside it, looking slightly down at the bow's starboard side, bank ≤3° | **Night version of this zone:** starlight is too faint to light the water, so the scene is lit only as a thought-experiment "what this depth would look like": faint god rays and caustics flicker on the hull. The hull's red bottom paint dims to brown, then grey (red absorbed first). Bubbles stream from the hull openings | Counter 0 → `200 M`. Rung `SUNLIGHT ENDS` lights at 200 m. Small line: `RED IS THE FIRST COLOUR THE SEA TAKES` (5.0-5.6) | Bubble streams, hull creaks, a low drone rising |
| 5.6-8.4 TWILIGHT ZONE (200-1,000 m) | The same lateral tracking. A slow 20° orbit around the bow shows its depth (parallax on the bow's flare, deck and foremast) | The blue light fades toward black. Marine snow drifts past in three depth layers. The first **bioluminescent sparks** flare where the hull passes through them (disturbance-triggered, as in nature) | Counter → `1,000 M`. Rung `LAST LIGHT` at 1,000 m | Muffled pings when the sparks flare, the drone thinning, bubble streams fading |
| 8.4-11.2 MIDNIGHT ZONE (1,000-3,700 m) | The camera's own light switches on (a soft cool spotlight cone, the honest viewpoint, like a submersible). The camera falls slightly below the bow and looks up at its prow | Total black except what the light cone reaches: the bow's prow sliding past, anchor and rivet lines, the marine snow lit in the cone, bioluminescent trails curling in the bow's wake. Bubbles have stopped | Counter → `3,700 M` (speeds up, never jumps). `IT KEPT FALLING` (9.0-10.5) | Shepard-style descending pitch (falling, not rising), pressure creaks getting deeper, pulses getting faster |
| 11.2-11.9 HELD BREATH | The camera slows, the bow drifts on past it into the black | The seabed comes out of the dark at the bottom edge of the light cone: soft grey silt ripples | Counter holds at `3,700 M` | Near silence (-40 dB), one faint metal tick |
| 11.9-14.2 IMPACT | Low wide shot at the seabed, a little to the side | The bow ploughs into the silt at a shallow angle. A silt wave rolls out and up into the light (no white-out, structure kept). The foremast folds back. The silt hangs | Counter → `3,800 M` and locks. Red chip `THE WRECK`. Line `NORTH ATLANTIC · 1912` | **The single biggest hit:** a deep iron impact with a long subsea rumble tail |
| 14.2-18.6 THE RULER | A log-spaced vertical **pull-up** along the axis from the wreck to the surface, a slow corkscrew orbit so it never looks flat | A glowing outline of the whole ship (cream, thin, 269 m) appears lying vertically, nose down on the wreck, then a second on top, then more, each one lit as we pass it: **14 stacked hull outlines from the seabed to the surface**. The real wreck stays small and lit at the bottom | Ghost count ticks `×1 … ×14` (its own monotonic counter, beside the depth counter, which holds 3,800). End: `14 TITANICS DEEP` | One soft tone per outline, rising in pitch, accelerating; the rumble tail dies away |
| 18.6-21.4 THE PARADOX | Still rising, slower; the column of outlines below fades | Dark water with marine snow, Snell's window growing overhead | `IT LAY IN THE DARK` / `FOR 73 YEARS` / `BEFORE ANYONE SAW IT AGAIN.` (three lines, 54 px) | A distant sonar-like ping (1985 search), wind starting above |
| 21.4-24.0 HOME / LOOP | Breaks back up through the surface; settles into exactly the frame-0 camera | The same moonless starfield and glassy sea, rings of ripples at the spot where it went down, then calm | End line `IT'S STILL DOWN THERE.` typed at 21.8 (70 px), chip red. Last frame = frame 0 framing (stern about to slip under) | Wind, faint water lap, the pressure tone rises again into frame 0 |

**Hook B** (overlay-only A/B): `14 TITANICS DEEP.` (premise as a number). Hook A goes on YouTube, B on IG/FB, matching the Scale Ladder practice.

**Persistent UI**
- **Left depth ladder, to scale** (x=64, the top of the ladder is the surface, the bottom is 3,800 m): rungs `SURFACE`, `SUNLIGHT ENDS · 200 M`, `LAST LIGHT · 1,000 M`, `WRECK · 3,800 M`. A red marker falls down it in sync with the counter. A little tick at the top marks `269 M = 1 SHIP` so the ruler beat is set up before it lands. Ladder names 36 px, active rung 42 px.
- **One depth counter**, top centre, 92 px, monotonic, asserted per frame (playbook §3.2). Units always `M`, with a thousands comma.
- Tag `DEPTHS TO SCALE · TIME COMPRESSED`, small, below the counter.
- The palette rules hold: navy-black, cream text, **red only** for the marker, chips and the end-line chip. The hull's red paint is the one exception and it is gone by 200 m, so it never competes with the UI red.

## 4. three.js visual spec (the "top notch" bar)

### 4.1 Renderer and pipeline
- three r0.170, WebGL2, `ACESFilmicToneMapping`, sRGB output, HalfFloat render targets throughout the composer.
- **Render natively at 1080x1920** (no 720p lanczos upscale for this reel) with **6 sub-frames of motion blur per frame** (shutter 1/60 s; 8 in the snap and impact).
- **GPU rendering, not SwiftShader.** SwiftShader is too slow for volumetrics plus 6 sub-frames at full resolution. Proposal: headless Chromium with `--use-gl=egl` on a RunPod GPU pod. **Owner decision needed** (claude.md rule 2: ask first). Fallback: SwiftShader at 1080x1920 with 4 sub-frames and fewer volumetric steps, rendered overnight.
- Composer order: RenderPass → **water volume pass** (§4.3) → god-ray / light-cone pass → UnrealBloom (strength 0.35-0.5, threshold above the bioluminescence floor) → grade (teal-navy shadows, cream highlights, vignette) → fine grain last. Soft clamp `1-exp(-1.25c)` before bloom (playbook §3.5).

### 4.2 The hero: the bow section (procedural, licence-clean)
- **Built in code, not a downloaded model**, so there's no licence question and it can't look like someone else's asset. (If a CC0 or CC BY model is ever considered, check its licence and credit it as with the audio.)
- Hull lofted from about 60 cross-section stations, fitted to the real dimensions: overall length 269 m, beam 28.2 m, *verify* the bow section length (about 140-150 m). Raked straight stem, a flare at the bow, a flat-bottomed midsection, and a **torn aft end** with jagged displaced plating and exposed decks and framing.
- Detail that reads on a phone: rows of portholes (no light), the well deck and forecastle, foremast with crow's nest, the two bow anchors in their hawse pipes, the gold sheer band, the waterline paint split. Plating seams and rivet rows come from a procedural normal map; edges are bevelled. A PBR paint with roughness variation (fresh paint, not a rusted wreck, since this is 1912).
- Funnel openings with torn stubs, a few cable ends trailing and swaying in the water (vertex shader).
- LOD: full detail within 400 m of the camera, simplified for the ruler beat.

### 4.3 Water that looks like water
- **Per-channel absorption (Beer–Lambert)** on everything, by distance travelled through water, with coefficients near pure seawater (red ≈ 0.35 /m, green ≈ 0.06 /m, blue ≈ 0.015 /m, tuned for the look). Red goes first, green next, blue last, which is what makes the red paint die "correctly" and the depth feel real.
- **Downwelling light** falls off exponentially with depth (compressed for readability; the zone boundaries in the counter are true). In-scatter colour drifts from blue-cyan near the surface to navy, then to black below 1,000 m.
- **Snell's window** in the surface seen from below: a sky disc of half-angle 48.6°, total internal reflection outside it (dark mirror of the water), and edge distortion from the gentle swell.
- **God rays** (0-200 m): raymarched shafts through a slowly moving caustic texture (16-24 steps, blue-noise jitter), and animated **caustics projected onto the hull** that fade with depth.
- **The camera's light (below 1,000 m):** a spot light with a raymarched volumetric cone, a physically right cool white that turns blue-green with distance (absorption applies to it too), and soft-edged shadows of the bow.

### 4.4 Particles (all world-fixed so they give true parallax)
- **Marine snow:** 3 camera-wrapped layers, about 150k instanced flakes total, slow sinking + curl-noise drift, sizes 1-4 px, lit only by what is lighting them (rays near the top, the light cone at depth). Motion blur turns the near ones into short streaks during the fast fall.
- **Bubbles:** streams from the portholes and the torn end in the first 1,000 m, with rate falling with depth and stopping by 1,000 m. They expand as they rise and wobble.
- **Bioluminescence:** about 20k sparse points that flash only when the hull or its wake passes within a few metres (disturbance trigger), short 0.2-0.6 s flashes, cyan-blue, curling in the wake vortex below the bow. Kept dim enough that the hull silhouette stays readable.
- **Silt plume on impact:** a 200k-particle GPU simulation (curl noise + gravity + drag), lit by the light cone with self-shadowing approximated by density, hanging and slowly settling through the end of the shot.

### 4.5 Surface and sky
- Calm ocean surface: low-amplitude Gerstner swell (the sea was glassy), with a very clean mirror reflection of the stars.
- **The real sky:** stars placed from a bright-star catalogue (for example the Yale Bright Star Catalogue) for **15 April 1912, about 02:20 ship's time, at the wreck position**, magnitude-sized, with faint Milky Way. No moon. Small *verify* note: the ship's time zone and exact position are from the sources below.
- The stern silhouette (hook only): procedural, as a dark shape against the stars and their reflections, with water sheeting and spray at the waterline and no lit windows.

### 4.6 Seabed and wreck
- A displaced plane with silt ripples, small rocks, a soft procedural albedo. It appears in the light cone first, never as a sudden full reveal.
- The impact: the bow digs in at a shallow angle and its forward part is buried in the silt (as found). The foremast folds back.

### 4.7 The ruler outlines
- Each ship outline is a thin line rendering of the whole 1912 profile (cream, additive, about 2 px at phone scale), extruded slightly so it shows parallax as the camera corkscrews past. Each lights up when it is passed, then dims to 30%. No outline may compete with the counter.

### 4.8 Look-dev gate (G1): six still frames before any animation
At native 1080x1920, judged at phone size against these questions:
1. Hook frame: do the stern, the stars and the reflections read in under 1 s?
2. Snell's window from just below the surface.
3. The bow at 100 m with rays and caustics: is the red paint visibly fading?
4. The bow at 600 m with marine snow and the first bioluminescence.
5. The prow in the light cone at 3,000 m: does it look like real deep-sea footage?
6. The impact silt plume at its peak: no white-out, the bow structure is still visible.

If a still doesn't hold up, the animation won't either. Only animate after G1 is approved.

## 5. Sound family: "iron and pressure" (new, not reused)
- Must not reuse the Night Sky v4 palette (glass, sparks, portal whooshes), the Scale Ladder brass-and-sub family, or the Deepest Hole sound. Ask the owner for a reference sound before mixing, if they have one in mind (playbook §4.2 lesson).
- Palette: deep hull groans and metal stress creaks (pitch-shifted down), water hits and an underwater "whump" for the snap, low-passed underwater ambience, bubble streams, a falling Shepard tone for the descent, muffled pings for the bioluminescence, one large iron impact with a long subsea rumble for the seabed, soft rising tones for the ruler outlines, a distant sonar-like ping for the 73-year line, then wind and water lap at the surface.
- Hits only at 0.0, 1.9 (the snap), 11.9 (the impact) and none at the surface return. All weight in 90-400 Hz for phone speakers; the sub on the hit bus only (playbook §4.1).
- -15 LUFS integrated; true peak measured after AAC. CC0 or CC BY with credit only; log every file in `audio-attribution.md` and the publish copy.

## 6. Facts and sources (verify before rendering the overlay)

| On screen | Value | Source | Status |
|---|---|---|---|
| Wreck depth | about 3,800 m (12,500 ft) | NOAA RMS Titanic pages (Office of General Counsel / Ocean Explorer); find and pin the exact URL | *verify* (some sources give 3,700-3,800 m; the counter lands on 3,800 and the copy says "about") |
| Ship length | 269 m (882 ft 9 in) | Encyclopedia Titanica / Harland & Wolff figures | *verify* |
| 14 Titanics deep | 3,800 / 269 = 14.1 | arithmetic | OK |
| Sunlight zone ends | 200 m | NOAA Ocean Service, ocean zones: https://oceanservice.noaa.gov/facts/light_travel.html | *verify* |
| Last light (twilight zone ends) | 1,000 m | NOAA, same page | *verify* |
| Red absorbed first | red is absorbed within the first few tens of metres, then green, blue last | NOAA Ocean Explorer, "light in the ocean" | *verify* the exact wording |
| Sank | 15 April 1912, about 02:20 | Encyclopedia Titanica; British and US inquiries | *verify* |
| 73 years unseen | found 1 September 1985 (Ballard, Michel; US-French expedition), 1985 − 1912 = 73 | NOAA / Woods Hole | *verify* |
| Moonless, calm night | from survivor and inquiry testimony | British Wreck Commissioner's inquiry | *verify* |
| Broke in two, bow and stern lie apart | about 600 m apart on the seabed | NOAA | *verify* (not on screen; affects the visuals only) |

Not on screen, for the pinned comment: pressure at the wreck is about 380 times the surface pressure (about 1 atm per 10 m). Pinned comment idea: "Guess how much pressure the wreck sits under 👇".

## 7. Build plan and gates
1. **G0, this spec:** owner signs off on the timeline, hook A/B and the GPU-render decision.
2. **G1, look-dev stills** (§4.8): six frames at native resolution.
3. **G2, 0-5.6 s animated** (hook, snap, sunlight zone) with temp sound. Check at a 2 fps contact sheet and at 1x phone size.
4. **G3, the full 24 s** with the overlay and the final mix. Run the playbook §7 QA list, plus: the counter is monotonic, the ghost count is monotonic, no frame is white, there are no people anywhere, and the loop closes.
5. Publish copy goes in `publish-copy/titanic-it-fell.md` with the sources table above and the sound credits.

Scripts live in `tools/titanic-fall/` (scene, render, overlay, mix), as with the other reels. Renders stay out of git.
