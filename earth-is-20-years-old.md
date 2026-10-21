# Earth Is 20 Years Old (galactic years): reel spec, facts and publish copy

Reel #4 of the reference remakes (`ref-remakes-plan.md`). Ref: "Earth's Evolution Measured in Galactic Years" (33 s, Sun orbiting a particle Milky Way with life-history icons). We take the topic only. Built in `tools/galactic-years/` with the three.js `renderAt(t)` pipeline, rendered natively at 1080x1920, 30 fps, 24.0 s.

Final files in the project files (not in git): `final-reels/earth-is-20-years-old.mp4` (share encode, 23.9 MB, 7.8 Mb/s two-pass H.264 + AAC 192k) and `final-reels/earth-is-20-years-old_master.mp4` (CRF 17 master, 89.7 MB). Measured after AAC: -14.2 LUFS integrated, true peak -2.3 dBFS. Counter monotonic (asserted), ends at 19.7.

## 1. Concept

One idea: measured in laps of the Sun around the galaxy, Earth is only about 20 "years" old, and everything we think of as ancient happened in the last lap.

- **Hook (frame 0):** we are already riding with the Sun along its orbit, stars streaming past, hit on frame 0. Typed: "EARTH IS / **20 YEARS OLD.**" + "IN GALACTIC YEARS".
- **Monotonic quantity:** "EARTH'S AGE IN GALACTIC YEARS" counter 0.0 to 19.7, plus a strip of 20 lap bars that fill gold. One milestone chip per stop.
- **Paradox beat:** "DINOSAURS DIED LESS THAN ONE ORBIT AGO." The last 66 million years are drawn on the orbit as a red arc (0.29 of a lap). Then: "ALL OF MODERN HUMANITY: THE LAST HALF DEGREE."
- **Close / loop:** "WE JUST GOT HERE." while the camera dives back into the chase shot of frame 0 (the Sun's position at the end is exactly 20 laps after frame 0, so the frames match).
- Tag "THOUGHT EXPERIMENT · NOT TO SCALE" (the galaxy is compressed, the Sun bead is enormous, the spiral pattern is held still while the Sun laps it).

## 2. New visual designs (not reused from other reels)

- **Galaxy:** a barred spiral seen from about 53° above its plane: gold bar and bulge, two major and two minor trailing log-spiral arms (17° pitch), teal-white young-star knots, dark dust lanes on the inner edges of the major arms (normal-blended dark points, a first for the channel), a soft warm disc glow. Different from the Scale Ladder procedural Milky Way (colour-tinted points with differential rotation) and from the Night Sky Andromeda plate.
- **Sun:** a small gold-white bead with a halo and a gold light trail along its orbit; the trail grows with speed, so the fast laps draw a full glowing ring. A dashed cream orbit path flashes on each completed lap.
- **Red markers only:** Sun marker ring, milestone notches on the lap strip, the 66-million-year arc, the 0.5° human arc, chips.
- Grade: soft clamp, bloom 0.55, teal shadows and warm highlights, vignette, fine grain. 3-sub-frame motion blur (1/60 s shutter).

## 3. Shot plan (video seconds, `tools/galactic-years/timeline.json` is the source of truth)

| Time | Camera | What the viewer reads |
|---|---|---|
| 0-1.9 | Chase: behind and above the Sun, the galactic disc as a band ahead | hook typed (done by about 1.0 s), "IN GALACTIC YEARS" |
| 1.9-3.4 | Snap: pull back (log distance) to the whole galaxy | "1 GALACTIC YEAR = 1 LAP ≈230 MILLION YEARS"; red ring + "THE SUN" |
| 3.4 | Overview, slow drift | counter 0.0, chip EARTH FORMS / 4.54 BILLION YEARS AGO |
| 5.2 | | 0.6 FIRST OCEANS / ~4.4 BILLION YEARS AGO |
| 7.4 | | 4.6 OLDEST FOSSIL LIFE / ~3.5 BILLION YEARS AGO |
| 9.6 | | 9.3 OXYGEN FILLS THE AIR / ~2.4 BILLION YEARS AGO |
| 12.2 | laps at their fastest between here and the last stop | 17.4 ANIMALS EXPLODE / ~539 MILLION YEARS AGO |
| 13.9 | | 18.7 FIRST DINOSAURS / ~231 MILLION YEARS AGO |
| 15.4 | | 19.4 DINOSAURS DIE OUT / 66 MILLION YEARS AGO |
| 16.6 | Sun arrives at today and stops | 19.7 TODAY; held breath to 17.1 |
| 17.1-19.6 | Push to the Sun's recent arc | biggest hit; red arc draws on; "DINOSAURS DIED / LESS THAN ONE / ORBIT AGO." + "66 MILLION YEARS = 0.29 OF A LAP" |
| 19.6-21.4 | Close over the Sun from above | "ALL OF MODERN HUMANITY: / THE LAST HALF DEGREE." + tiny red arc "~300,000 YEARS" |
| 21.4-24.0 | Dive back into the chase pose of frame 0 | "WE JUST GOT HERE." typed, fades before the loop |

Lap position between stops is eased (slow at each milestone so the chip can be read, fast between). The overlay asserts the counter never goes backwards.

## 4. Facts and sources (checked 21 Oct 2026)

| Claim on screen | Value used | Source / note |
|---|---|---|
| 1 galactic year ≈ 230 million years | 230 My | Live Science "How long is a galactic year?" gives 220-230 My; NRAO "Orbital period of the Sun" gives about 226 My (8 kpc, 230 km/s). Other estimates run 220-250 My. |
| Earth is about 20 galactic years old | 4.54 Gy / 230 My = 19.7 | Earth's age 4.54 ± 0.05 billion years (USGS, Dalrymple). With 220-250 My the answer is 18-21, so the hook says "20" and the counter ends at 19.7. (Live Science's own "16" uses a different period; we do not use it.) |
| First oceans ~4.4 billion years ago | lap 0.6 | Jack Hills zircons show liquid water at the surface by about 4.4 Ga (Wilde et al., Nature 2001). |
| Oldest fossil life ~3.5 billion years ago | lap 4.6 | Dresser Formation stromatolites, Pilbara, about 3.48 Ga. Wording is "oldest fossil life", not "first life" (life may be older). |
| Oxygen fills the air ~2.4 billion years ago | lap 9.3 | Great Oxidation Event, about 2.4-2.3 Ga. |
| Animals explode ~539 million years ago | lap 17.4 | Base of the Cambrian, 538.8 Ma (ICS chart). |
| First dinosaurs ~231 million years ago | lap 18.7 | Earliest dinosaurs (e.g. Eoraptor, Herrerasaurus), about 231-233 Ma. |
| Dinosaurs died out 66 million years ago | lap 19.45 | K-Pg extinction, 66.0 Ma (non-avian dinosaurs). 66/230 = 0.29 of a lap, so "less than one orbit ago" is true (even the first dinosaurs were only 0.8 of an orbit ago). |
| Modern humans: the last half degree | 300,000 / 230 My × 360° = 0.47° | Homo sapiens about 300,000 years (Jebel Irhoud, Hublin et al., Nature 2017). Say "modern humans/humanity", never just "humans". |

Simplifications to keep in the copy if asked: the Sun's path is not a perfect circle (it also bobs up and down through the disc), the spiral arms are a pattern that does not lap with the Sun, and the galaxy size is compressed.

## 5. Sound ("orbital clockwork" family, new)

All synthesized in `mix_gy.py` except the wind bed. Frame-0 hit (pitch-drop body + crack + gong partials) and a rush; quiet type ticks; reverse swell into a soft hit on the snap; **one wooden tick per completed lap** on a rising pentatonic scale (they accelerate with the laps: 19 ticks between 5.6 and 14.5 s); a glass FM bell per milestone (a new pitch each); a pad drone whose filter opens with lap speed; shepard riser into "today"; held breath (16.6-17.1 s: drone and wind drop out, only the TODAY bell rings, then a 0.42 s reverse swell); the biggest hit on the twist (17.1 s: body 300 to 58 Hz, crack, 73 Hz gong, 44 Hz sub, reverb); a high bell for humans; dive whoosh and a rising loop-link tone into frame 0. Bass is managed per playbook 4.1 (sub only on the hit bus, 90 Hz high-pass elsewhere). Master target about -15 LUFS, true peak checked after AAC.

Licences: wind is "wind.ogg" by sleepCircle (Freesound 22331, CC0, no credit required). No CC BY files are used, so no credit block is needed.

## 6. Rebuild

```
cd tools/galactic-years
npm i three@0.170.0 playwright-core   # or symlink node_modules (gitignored)
python3 -m http.server 8777 &
for w in 0 1 2 3; do node render.js 1080 1920 OUT/f3d $w 720 4 & done; wait   # frames + proj_*.json
cd OUT && python3 .../overlay.py f3d && python3 .../mix_gy.py
ffmpeg -framerate 30 -i f3d/f%04d.jpg -i gy_overlay.mov -i gy_mix.wav -filter_complex "[0][1]overlay=format=auto,format=yuv420p" \
  -af "loudnorm=I=-15:TP=-1.5:LRA=11" -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k -movflags +faststart earth-is-20-years-old.mp4
```

## 7. Publish copy

### YouTube Shorts
**Title:** Earth Is Only 20 Years Old (in galactic years) #shorts

**Description:**
The Sun takes about 230 million years to lap the Milky Way once. That is one galactic year.
Count Earth's age that way and it is about 20 years old.
Oceans in its first year. The first fossil life by year 5. Oxygen at year 9. Animals at 17.
And the dinosaurs died less than one orbit ago. All of modern humanity fits in the last half degree.

Thought experiment, not to scale: the galaxy is compressed and the spiral arms are held still while the Sun laps them.

Facts: galactic year about 220-250 million years (NRAO, Live Science); Earth 4.54 billion years (USGS); oldest fossils about 3.5 billion years (Pilbara stromatolites); Great Oxidation Event about 2.4 billion years ago; Cambrian 539 million years ago; first dinosaurs about 231 million years ago; extinction 66 million years ago; Homo sapiens about 300,000 years.

Sound: original synthesized design, plus "wind.ogg" by sleepCircle (Freesound, CC0).

#space #galaxy #milkyway #earth #dinosaurs #science #astronomy #deeptime #slowlight

**Pinned comment:** How old would you be in galactic years? (A 30-year-old is about 0.00000013.)

### Instagram / Facebook
Earth is 20 years old. In galactic years. 🌌
One lap of the Sun around the Milky Way takes about 230 million years. The dinosaurs died less than one lap ago, and all of modern humanity fits in the last half degree.
Thought experiment, not to scale. Sound: original + CC0 wind (sleepCircle, Freesound).
#space #milkyway #galaxy #deeptime #dinosaurs #science #slowlight

### Upload checklist
- AI/synthetic content label on (rendered CGI).
- Hook A is the only hook; a hook B ("THE DINOSAURS DIED LESS THAN ONE ORBIT AGO.") would be overlay-only.

## 8. v2 (detail, depth, parallax)

Files: `final-reels/earth-is-20-years-old_v2.mp4` (share encode, 27.7 MB, 9.2 Mb/s) and `_v2_master.mp4` (CRF 17, 93.5 MB). Same timeline, overlay and sound; -14.2 LUFS, true peak -2.3 dBFS after AAC.
- Rendered at 1350x2400 and downsampled to 1080x1920 (`SS=1.25`) for sharper, anti-aliased stars.
- Galaxy: 560k stars (was 230k), sharper arm crests, 170 spurs/feathers off the arms, 900 young-star knots, a soft gas-glow layer along the arms (faded out near the camera), 60k finer dust blobs, a 3D stellar halo and 70 globular clusters above and below the disc, a mid-field star layer between camera and galaxy for parallax.
- Camera: during the laps it sweeps about 40° in azimuth and drops from about 58° to 38° above the plane (more oblique, more depth) with a slight dolly; the twist shot trucks sideways. Bloom radius tightened and grain reduced for crispness.
