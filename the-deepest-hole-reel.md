# The Deepest Hole (22.0 s, v2 of reel #16, no voiceover): spec, build and publish copy

Reel #16 from `ref-remakes-plan.md`. The ref was a "you never know how close you are" clip with two stickmen and a rock. v1 (`one-more-shovel-reel.md`) kept that moral and read as preachy, which isn't Slow Light. v2 keeps the stickman and the cross-section world but drops the moral and turns the reel into a scale reveal: how deep humans have ever dug, measured against the whole Earth. Built in three.js (`tools/deepest-hole/`). The sound is procedural.

## Idea
A stickman digs a well by lantern light, seen in cross-section. He breaks through to water at 10 m. Then the camera pulls back on a log zoom while the depth counter keeps climbing past the deepest holes people have made, placed side by side at their real depths: the deepest hand-dug well (392 m), the deepest mine (about 4 km) and the Kola Superdeep Borehole (12,262 m, 23 cm wide). After a held breath the camera bursts out to the whole Earth, cut open: crust, glowing mantle, liquid outer core, solid inner core. All of those holes sit in a hairline at the top. Caption: OUR DEEPEST HOLE IS 0.2% OF THE WAY TO THE CENTRE. Then it plunges back down to his first shovel.

Paradox beat: 12 km feels enormous (the counter takes 8 s to get there), then it vanishes at planet scale.

## Look
- Same stickman rig (IK hands on the shovel), tripod, rope and lantern as v1, night sky.
- Cross-section face: near-surface strata (topsoil, clay, sand with gold glints, stones, damp blue clay, an aquifer whose pores glow teal), then sedimentary bands (sandstone, shale, limestone), crystalline crust with gold specks, a dark-red to orange mantle with convection texture, an orange-gold outer core and a pale gold inner core. Detail is band-limited to pixel size, so each zoom level shows its own texture without aliasing.
- Holes drawn as lines at least ~1.3 px wide, colour-coded: the well teal (water), Woodingdean cream, the mine gold with its tunnel levels, Kola glowing hot orange at the tip.
- Planet: the back hemisphere behind the cut face is a dark night-side Earth with city lights and a teal rim.
- Red only for the chips, leader lines and ring markers. Bloom stays low and the cores are capped (no white-out).

## Shot plan (timeline.json is the single source of truth)
| Time | Shot | Sound |
|---|---|---|
| 0.0-1.9 | Surface, frame-0 shovel hit; hook HOW DEEP HAVE WE EVER DUG? typed by 1.0 s; counter DEPTH 0.1 M | big shovel hit, wind |
| 1.9-2.6 | Dive into the cross-section | sweep + small snap hit |
| 2.6-4.9 | Time-lapse dig; counter to 10.0 M | shovel chunks, earth drone |
| 4.9-5.9 | He breaks through: water wells up round his feet; he looks down. Chip A WELL / 10 M · DUG BY HAND | bubbles, glass chord |
| 5.9-8.7 | Log zoom out to a 720 m frame; a cream line drills down beside the well to 392 m. Chip DEEPEST HAND-DUG WELL / 392 M · ENGLAND, 1862 | pick clinks echoing in a shaft |
| 8.7-11.5 | Zoom out to a 7 km frame; the gold mine shaft and tunnel levels reach 4 km. Chip DEEPEST MINE / ABOUT 4 KM · SOUTH AFRICA | cage cable whine, machine rumble |
| 11.5-13.9 | Zoom out to 17.5 km; the Kola line drills to 12,262 m, hot at the tip. Chip DEEPEST HOLE EVER / 12,262 M · 23 CM WIDE · 1989 | grinding drill rising, heat hiss |
| 13.95-14.6 | Held breath | near silence, reverse suck, 50 ms vacuum |
| 14.6-17.4 | The biggest hit: log zoom out to the whole planet, cut open, swinging round to show its depth. Caption OUR DEEPEST HOLE IS 0.2% OF THE WAY TO THE CENTRE. Chip ALL OF THEM ARE HERE / CENTRE: 6,371 KM DOWN on a red ring at the top | boom + gong + sub, warm molten pad |
| 17.4-19.9 | Hold on the planet, slow orbit; text clears by 19.9 | pad |
| 19.9-21.6 | Plunge back down every scale to the surface (the man has been reset there, unseen) | falling whoosh |
| 21.6-22.0 | Frame-0 composition, shovel raised; loop to the first strike | rising tone into frame 0 |

Counter: one odometer in metres, 0.1 -> 10.0 -> 392 -> 4,000 -> 12,262 M, script-asserted monotonic; it fades out before the plunge. Small note under it from 6 s: REAL DEPTHS · HOLES SHOWN SIDE BY SIDE (the holes are in different countries; widths below ~1.3 px are drawn at that minimum).

## Facts and sources
- Woodingdean Water Well (Brighton, England): dug by hand from 1858 until water was struck on 16 March 1862, 391.6 m (1,285 ft), the deepest hand-dug well. Guinness World Records, "Deepest hand-dug well" https://www.guinnessworldrecords.com/world-records/761162-deepest-hand-dug-well ; https://en.wikipedia.org/wiki/Woodingdean_Water_Well
- Mponeng gold mine (near Johannesburg, South Africa): the deepest mine, operating at 3.9 km by 2012 and below 4 km since (on screen: ABOUT 4 KM). Guinness World Records, "Deepest mine" https://www.guinnessworldrecords.com/world-records/66169-deepest-mine
- Kola Superdeep Borehole SG-3 (Russia): 12,262 m true vertical depth, reached in 1989; 23 cm diameter; the deepest human-made hole. https://en.wikipedia.org/wiki/Kola_Superdeep_Borehole
- Earth's mean radius is 6,371 km, so 12.262 / 6,371 = 0.19%, rounded on screen to 0.2%. Layer boundaries used: continental crust ~35 km, core-mantle boundary at 2,891 km depth (radius 3,480 km), inner core radius ~1,221 km (standard values, e.g. USGS / PREM).
- Groundwater fills the pores of sand and gravel below the water table, so the aquifer is drawn as gravel with water between the stones. USGS https://www.usgs.gov/water-science-school/science/groundwater-what-groundwater

## Sound
Procedural in numpy (`mix.py`), no samples and no credits. Family: earth, iron and heat (new for this reel). Hits only at frame 0, the snap into the cross-section (small) and the planet reveal (biggest). Delivered at -15.4 LUFS, true peak -2.6 dBFS after AAC; 22.0 s, 1080x1920, 30 fps, about 23 MB (H.264 CRF 22, AAC 192k). Output: `final-reels/the-deepest-hole.mp4` in the project files.

## Build (tools/deepest-hole/)
`gen_timeline.py` -> `timeline.json`; `index.html` (scene, `window.renderAt(t)`); `render.js`, `shot.js`, `proj.js` (chip anchors); `overlay.py`; `mix.py`; `build.sh`.
Rebuild: `npm i`, `python3 -m http.server 8791 &`, 4 workers `node render.js 720 1280 $FRAMES $i 660 4` (i = 0..3), then `FRAMES=$FRAMES OUT=the-deepest-hole.mp4 ./build.sh`. Hook B is overlay-only: `HOOK="THE DEEPEST HOLE ON EARTH IS 23 CM WIDE." ./build.sh`.

## Publish copy
**YouTube Shorts title:** The Deepest Hole Ever Dug Is 0.2% of the Way Down #shorts

**Description:**
One man, one shovel: 10 metres.
The deepest hand-dug well: 392 m (England, 1862).
The deepest mine: about 4 km.
The Kola Superdeep Borehole: 12,262 m, and only 23 cm wide.
The centre of the Earth: 6,371 km down.

Real depths, holes shown side by side. Sources: Guinness World Records, Kola SG-3 records, USGS.

#shorts #earth #science #kolasuperdeepborehole #geology #space #slowlight

**Instagram / Facebook caption:**
12,262 metres. The deepest hole humans have ever made. 🕳️
It barely scratches the planet: 0.2% of the way to the centre.
#earth #science #geology #kolaborehole #scale #slowlight #reels

**Pinned comment:** Guess how hot it was at the bottom of Kola 👇 (about 180 °C near the bottom)

**Upload checklist:** AI/synthetic label on (rendered 3D); no music credits needed; loops, so no end screen.
