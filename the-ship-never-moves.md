# The Ship Never Moves (warp drive), v2, 24 s, no voiceover

Reel #14 from `ref-remakes-plan.md` ("What If Space Itself Became the Engine"). We take the topic only: our own craft, our own grid, our own sound, no fighter jet, no red/blue HUD.

- Files (project folder `final-reels/`): `the-ship-never-moves.mp4` (share size, under 30 MB) and `the-ship-never-moves_master.mp4` (high bitrate, use for uploads). Both are 1080x1920, rendered natively at 30 fps, 24.0 s long, H.264 + AAC, and loop (the last frame runs into frame 0).
- Source: `tools/warp-drive/` (three.js scene `index.html`, `render.js`, `proj.js`, `overlay.py`, `mix_warp.py`, `build.sh`).
- v1 (22 s) is in git history (commit `45e1d82`). Teja's notes on v1: "not engaging enough", sound "not working", visuals need improvement. v2 answers those with something new on screen every 1-2 s, four new beats (planet fly-by, exotic-energy ring, arrival at the star, the stop-blast), and real recorded cinematic sound instead of synthesised beeps.

## Concept
Everyone pictures a warp drive as a very fast engine. Alcubierre's warp bubble is the opposite: the ship's engine is off and it sits at rest in a pocket of flat space. Space squeezes in front of the bubble and stretches out behind it, and the pocket is carried along. Inside, nothing pushes, there is no g-force, and the ship's clock ticks normally. The bubble can still outrun a light beam, because no local speed limit applies to how space itself moves.

Two catches turn it from a promise into a paradox: it needs negative energy, which may not exist in the amounts needed, and when it stops, the matter it swept up on the way is released as a blast at whatever is ahead.

One idea, one monotonic counter (distance crossed, 0.00 to 4.20 light-years), one paradox (speed 0, yet it outruns light), two twists, and a loop.

## Shot plan (as built)
Travel is always "up the screen" or "into the screen", so the viewer never has to re-orient.

| Time (s) | Picture | Text |
|---|---|---|
| 0.0-1.6 | The camera whips around our craft (ivory hull, swept tail fins, rotating gold halo ring, dark engine) over a flat teal grid. Hit on frame 0. | "THIS SHIP NEVER MOVES." then red chip "YET IT OUTRUNS LIGHT." |
| 1.6-2.6 | Ignition: a ring of exotic-energy sparks lights around the ship, the bubble wall sweeps on, small flash, fast pull-back. | Hook fades. |
| 2.6-5.0 | Hero shot from behind and above: far space flows past, grid lines bunch up gold ahead and spread out teal behind. | "SPACE SQUEEZES AHEAD" (gold), "SPACE STRETCHES BEHIND" (teal). Odometer + red chip "SHIP'S OWN SPEED: 0" start. |
| 5.0-6.5 | A ringed gas giant roars past on the right (it is far space, so it flows by). | "THE SHIP ISN'T FLYING." / "SPACE IS." (gold) |
| 6.5-9.2 | Through the wall into the bubble (wide lens): still lattice, gold squeezed grid ahead, stars streaming. | "INSIDE: NO PUSH." / "NO G-FORCE." / "SHIP CLOCK 0:xx.x TICKS NORMALLY" |
| 9.2-11.8 | High wide shot: at 10.0 s a light beam fires forward beside the ship and falls behind. | Red ring + "LIGHT" chip; "A LIGHT BEAM, / LEFT BEHIND." |
| 11.8-14.0 | Low shot looking ahead: the nearest star (a small point dead ahead the whole trip) fills the frame as the bubble slows. | Odometer lands on 4.20. "4.2 LIGHT-YEARS LATER:" / "THE NEAREST STAR." |
| 14.0-14.7 | Held breath: text clears, only the ship's clock ticks. | none |
| 14.7-17.2 | Biggest hit. Side view: the exotic-energy ring around the bubble burns hot. | Red chip "IT NEEDS NEGATIVE ENERGY." / "NOBODY KNOWS IF ENOUGH / CAN EVER EXIST." + red marker "NEGATIVE ENERGY" on the ring. |
| 17.2-20.6 | Matter piled on the front wall all trip (gold specks); the bubble stops, the wall flickers, implodes, and the pile blasts forward toward the star with a shock ring. | "AND WHEN IT STOPS," / red chip "IT BLASTS WHATEVER IS AHEAD." |
| 20.6-24.0 | The star fades, the camera glides back to the frame-0 pose over a flat, still grid. | "SPACE MOVED." / "THE SHIP NEVER DID." (gold), fades before the loop. |

"THOUGHT EXPERIMENT · NOT TO SCALE" stays on throughout.

### How the picture maps to the physics
- The scene is drawn in the ship's frame: the ship stays at the origin for the whole reel, and the engine nozzle is dark.
- Each grid vertex is a fixed piece of space. Far away it flows past at the bubble's speed. Near the bubble a displacement field moves with the bubble, so the spacing shrinks ahead (gold) and grows behind (teal). This illustrates Alcubierre's contraction ahead and expansion behind; it is a picture of the idea, not a plot of the metric.
- The exotic-energy ring sits on the bubble's equator, perpendicular to the motion, which is where the (negative) energy density of Alcubierre's metric is concentrated.
- The bubble's cruise speed is 1.6 times the beam's speed, so the light beam falls behind steadily.
- Swept-up matter: gold specks build up on the front wall in proportion to the distance travelled and are released forward when the bubble stops.
- The total flow over the reel (180 units) is a whole number of grid cells and exactly one star-field period, so the last frame matches frame 0. The planet and the star fade in while they are still far away and the star fades out at the end, so neither breaks the loop.

## Facts and sources (keep identical everywhere)
| On screen / in copy | Fact | Source |
|---|---|---|
| Space squeezes ahead, stretches behind | Alcubierre's metric produces "a purely local expansion of spacetime behind the spaceship and an opposite contraction in front of it." | M. Alcubierre, "The warp drive: hyper-fast travel within general relativity", Class. Quantum Grav. 11, L73-L77 (1994), [arXiv:gr-qc/0009013](https://arxiv.org/abs/gr-qc/0009013) |
| Ship's own speed 0; the ship isn't flying, space is | The ship sits in a flat region inside the bubble and is carried along; it moves on a geodesic (free fall). | Alcubierre 1994 |
| No push, no g-force | "The proper acceleration along the spaceship's path will always be zero." | Alcubierre 1994 |
| Its clock ticks normally | The ship's "proper time is equal to coordinate time". | Alcubierre 1994 |
| Outruns a light beam | The bubble's speed is not limited by light speed; locally nothing inside moves faster than light. | Alcubierre 1994 |
| It needs negative energy (ring) | The energy density the metric needs is negative, violating the weak, dominant and strong energy conditions; it is concentrated in a ring around the bubble, perpendicular to the motion. | Alcubierre 1994 |
| Nobody knows if enough can exist | Quantum field theory allows small amounts of negative energy (Casimir effect), but quantum inequalities limit it; Pfenning and Ford found the energy needed "is physically unattainable". | M. J. Pfenning and L. H. Ford, Class. Quantum Grav. 14, 1743 (1997), [arXiv:gr-qc/9702026](https://arxiv.org/abs/gr-qc/9702026) |
| When it stops, it blasts whatever is ahead | Particles met on the way are swept up into the bubble's front region; when the bubble decelerates they are released in an energetic burst forward. The authors say people at the destination "would be gamma ray and high energy particle blasted into oblivion"; the energy grows with the length of the trip. | B. McMonigal, G. F. Lewis and P. O'Byrne, "The Alcubierre warp drive: On the matter of matter", Phys. Rev. D 85, 064024 (2012), [arXiv:1202.5708](https://arxiv.org/abs/1202.5708); summary: [Universe Today](https://www.universetoday.com/articles/warp-drives-may-come-with-a-killer-downside) |
| 4.2 light-years, the nearest star | Proxima Centauri, the nearest star after the Sun, is about 4.24 light-years away. The odometer illustrates a trip, not a travel time. | standard value |

Nuance for comments (not on screen): later papers reduce the energy (Van Den Broeck 1999) or look for positive-energy warp shells that travel slower than light (Fuchs et al. 2024, [arXiv:2405.02709](https://arxiv.org/abs/2405.02709)). No known solution goes faster than light without negative energy. Say "may not exist" or "nobody knows if enough can exist", never "impossible".

## Sound design (v2)
- **Score:** a synthesised 120 BPM bass ostinato (A minor, saw bass opening up with the speed) and a low drum on beats 1 and 3 drive the flight; it goes half-time and darker for the twist, and stops at the blast.
- **Bed:** ElevenLabs "warp field hum" (generated for this reel), looped and muffled while the camera is inside the bubble, plus a filtered-noise rush that follows the speed.
- **Hits** (sized): frame 0 dark accent; ignition = fast warp-in + portal gate + plasma burst; twist = cinematic braaam; blast = implosion sucking in, then the explosion. Each has a synthesised transient layer for a hard front edge.
- **Movement:** jet doppler + cinematic woosh for the planet; gateway shimmer going into the bubble, subby whooshes coming out; an electric zap and a falling tone for the light beam; sparks under the unstable ring; a riser and a warm pad into the star reveal.
- **Ship's clock:** a soft tick every second all the way through, louder inside the bubble and alone in the held breath (14.0-14.7 s).
- **End:** wind and a glass bell, then a rising tone into frame 0 so the loop is audible.
- Master: about -15 LUFS integrated, true peak under -1 dBTP, both measured on the final AAC file.

### Sound credits (paste into the YouTube description)
> Sound credits (from Freesound). Changes were made: the sounds below were trimmed, layered, pitch/time-processed and mixed with other sounds. All other sounds used are CC0, generated with ElevenLabs, or synthesised.
> - "Cinematic Sound Braaam Sample (Chakongaudio, Brass, Trailer)" by chakong, https://freesound.org/people/chakong/sounds/722633/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
> - "synth_jet.wav" by vartioh, https://freesound.org/people/vartioh/sounds/115555/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
> - "JacobsLadderSingle2.flac" by Halleck, https://freesound.org/people/Halleck/sounds/19487/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
> - "Electric Sparks" by mikiko850, https://freesound.org/people/mikiko850/sounds/849772/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

CC0 files used (no credit needed): 869757 Dark Suspense Accent, 768664 portal gate opening, 735062 Fast Warp In, 850262 Orbiting Plasma Burst, 814047 Fantasy Implosion, 814046 Explosion From Another Dimension, 649445 Cinematic Woosh SFX-015, 238375 CP_Subby_Whoosh, 752034 Sci-Fi Gateway, 22331 wind.ogg. ElevenLabs file: `tools/sfxlib/elevenlabs_warp_field_hum.mp3`.

Short form (Instagram / Facebook): "Sound: chakong, vartioh, Halleck and mikiko850 via Freesound (CC BY 4.0), changes made, plus CC0, ElevenLabs and synthesised sounds. Full credits on YouTube."

## Publish copy

### YouTube Shorts
**Title (pick one):**
1. This ship never moves. It still outruns light.
2. How a warp drive actually works (and why stopping it is deadly)
3. The warp drive that breaks no speed limit

Recommended: option 1 (it matches the hook).

**Description:**
> This ship never moves. It still outruns light.
>
> In 1994 physicist Miguel Alcubierre found a "warp drive" inside Einstein's general relativity: squeeze space in front of a ship and stretch it out behind. The ship sits in a bubble of flat space and is carried along. Its engine is off, it feels no push, and its clock ticks normally. The bubble can still outrun a light beam, because the speed of light limits things moving through space, not space itself.
>
> Two catches. The bubble needs negative energy, and nobody knows if enough could ever exist. And in 2012, physicists found that the bubble sweeps up particles on the way and releases them as a blast when it stops, aimed at whatever is ahead.
>
> A thought experiment: the visuals are an illustration, not to scale. Visuals are 3D-rendered.
>
> Sources: M. Alcubierre, Classical and Quantum Gravity 11, L73 (1994). B. McMonigal, G. F. Lewis and P. O'Byrne, Physical Review D 85, 064024 (2012).
>
> (sound credits block from above)
>
> Slow Light: stories worth slowing down for.
> #space #physics #science

**Hashtags (YouTube shows the first 3 above the title):** #space #physics #science

**Tags (under 500 characters):**
warp drive, alcubierre drive, alcubierre warp drive, faster than light, ftl travel, how does a warp drive work, warp bubble, negative energy, exotic matter, general relativity, spacetime, einstein, space travel, interstellar travel, proxima centauri, physics explained, space shorts, science shorts, slow light

**Pinned comment:** Would you still take the trip if stopping meant blasting your destination? 🚀

**Upload settings:** Shorts, Science & Technology, not made for kids. Altered or synthetic content: stylised 3D render; turn the label on if unsure. Thumbnail: a frame from about 5.6 s (the bubble with the ringed planet roaring past) or 16 s (the glowing negative-energy ring with "IT NEEDS NEGATIVE ENERGY.").

### Instagram Reel (max 5 hashtags)
> This ship never moves. It still outruns light.
>
> A warp drive doesn't push the ship. It squeezes space in front and stretches it behind, and the ship rides along in a bubble of flat space: engine off, no g-force, its clock ticking normally.
>
> The catches? It needs negative energy that may not exist. And when it stops, everything it swept up on the way blasts out ahead.
>
> Follow Slow Light for more stories worth slowing down for.
>
> #warpdrive #space #physics #science #slowlight

### Facebook Reel
> This ship never moves. It still outruns light. Here is how Alcubierre's warp drive works, the energy it needs that may not exist, and why stopping it could blast your destination. 🚀

## QA (playbook section 7)
- Frame 0: hit plus premise; hook done by about 1.8 s; something new on screen every 1-2 s.
- Contact sheet at 2 fps checked: one subject at a time, labels legible at phone size.
- Counters are asserted monotonic in `overlay.py` (distance and ship clock); typed text never uses a negative slice.
- Flashes: ignition 10%, twist 5%, blast 13%, each about 0.1-0.2 s (inside the playbook's 12-16% limit).
- Loop: last frame to frame 0 is continuous in camera, grid, stars and sound (tick at 0 s and 24 s, rising tone into frame 0).
- Audio: loudness and true peak are measured on the final AAC files (see the build log).
