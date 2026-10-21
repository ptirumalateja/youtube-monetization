# The Ship Never Moves (warp drive), 22 s, no voiceover

Reel #14 from `ref-remakes-plan.md` ("What If Space Itself Became the Engine"). We take the topic only: our own craft, our own grid, our own sound, no fighter jet, no red/blue HUD.

- File: `the-ship-never-moves.mp4`, 1080x1920 (rendered natively), 30 fps, 22.0 s, H.264 + AAC, loops (frame 660 matches frame 0).
- Source: `tools/warp-drive/` (three.js scene `index.html`, `render.js`, `proj.js`, `overlay.py`, `mix_warp.py`, `build.sh`).
- Sound: fully synthesised in numpy (`mix_warp.py`). No samples, so there is nothing to credit.

## Concept
Everyone pictures a warp drive as a very fast engine. Alcubierre's warp bubble is the opposite: the ship's engine is off, and it sits at rest in a pocket of flat space. Space squeezes in front of the bubble and stretches out behind it, and the pocket is carried along. Inside, nothing pushes, there is no g-force, and the ship's clock ticks at the normal rate. The bubble as a whole can still outrun a light beam, because no local speed limit applies to how space itself moves. The catch: it needs negative energy, and nobody knows whether enough can exist.

One idea, one monotonic counter (distance crossed, 0.00 to 4.20 light-years: about the distance to the nearest star), one paradox (speed 0, yet it outruns light), one twist, and a loop.

## Shot plan (as built)
Travel is always "up the screen", so the viewer never has to re-orient.

| Time (s) | Picture | Text |
|---|---|---|
| 0.0-1.9 | Our craft (ivory lathe hull, gold halo ring, dark engine) at rest over a flat teal space grid; slow push-in. Hit on frame 0. | Hook typed: "THIS SHIP NEVER MOVES." then red chip "YET IT OUTRUNS LIGHT." |
| 1.95-3.3 | Ignition: the bubble wall sweeps on with a small flash (no white-out); the camera pulls back and up behind the bubble. | Hook fades. |
| 3.3-8.2 | Hero shot from behind and above. Far space (grid and stars) flows past. Grid lines bunch up and glow gold ahead of the bubble, and spread apart and glow teal behind it. | "SPACE SQUEEZES AHEAD" (gold), "SPACE STRETCHES BEHIND" (teal). Odometer "DISTANCE CROSSED x.xx LIGHT-YEARS" starts; red chip "SHIP'S OWN SPEED: 0". |
| 8.2-11.2 | The camera passes through the wall into the bubble: a still, square lattice (flat space) around the ship, stars streaming outside. | "INSIDE: FLAT, STILL SPACE" / "NO PUSH. NO G-FORCE." / "SHIP CLOCK 0:xx.x TICKS NORMALLY". |
| 11.2-15.3 | Fast pull-out to a high wide shot. At 12.3 s a light beam fires forward beside the ship; the bubble pulls away from it and the beam's head slides down the frame. | Red ring + "LIGHT" chip on the beam's head; "A LIGHT BEAM, / LEFT BEHIND." Odometer lands on 4.20. |
| 15.3-16.2 | Held breath: the flow slows, text clears, only the ship's clock is still ticking. | none |
| 16.2-19.3 | Biggest hit. The bubble wall flickers, then collapses; the grid relaxes back to flat. | Red chip "IT NEEDS NEGATIVE ENERGY." / "NOBODY KNOWS IF ENOUGH / CAN EVER EXIST." |
| 19.3-22.0 | The camera glides back to the frame-0 pose over a flat, still grid. | "SPACE MOVED." / "THE SHIP NEVER DID." (gold), fades before the loop. |

"THOUGHT EXPERIMENT · NOT TO SCALE" stays on throughout.

### How the picture maps to the physics
- The scene is drawn in the ship's frame: the ship stays at the origin for the whole reel, and the engine nozzle is dark.
- Each grid vertex is a fixed piece of space. Far away it flows past at the bubble's speed. Near the bubble a displacement field moves with the bubble, so the spacing shrinks ahead (gold, squeeze) and grows behind (teal, stretch). This illustrates Alcubierre's contraction ahead and expansion behind. It is a picture of the idea, not a plot of the metric, which is one reason the reel is labelled a thought experiment.
- The bubble's cruise speed in the scene is 1.6 times the beam's speed, so the light beam falls behind at a steady rate.
- The total flow over the reel (180 units) is a whole number of grid cells and exactly one star-field period, so the last frame matches frame 0.

## Facts and sources (keep identical everywhere)
| On screen / in copy | Fact | Source |
|---|---|---|
| Space squeezes ahead, stretches behind | Alcubierre's metric produces "a purely local expansion of spacetime behind the spaceship and an opposite contraction in front of it." | M. Alcubierre, "The warp drive: hyper-fast travel within general relativity", Class. Quantum Grav. 11, L73-L77 (1994), [arXiv:gr-qc/0009013](https://arxiv.org/abs/gr-qc/0009013) |
| Ship's own speed 0; inside is flat, still space | The ship sits in a flat region inside the bubble and is carried along with it; it moves on a geodesic (free fall). | Alcubierre 1994 |
| No push, no g-force | "The proper acceleration along the spaceship's path will always be zero." Tidal forces near the ship are very small (they can be very large in the wall). | Alcubierre 1994 |
| Its clock ticks normally | The ship's "proper time is equal to coordinate time": no time dilation for the passengers during the trip. | Alcubierre 1994 |
| Outruns a light beam | The bubble's speed is not limited by light speed. Locally, nothing inside ever moves faster than light. | Alcubierre 1994 |
| It needs negative energy | The energy density the metric needs is negative everywhere, which violates the weak, dominant and strong energy conditions ("exotic matter"). | Alcubierre 1994 |
| Nobody knows if enough can exist | Small amounts of negative energy are allowed in quantum field theory (for example the Casimir effect), but quantum inequalities limit how much and for how long. Pfenning and Ford found that the walls would be only a few hundred Planck lengths thick, and that the total energy needed "is physically unattainable". | M. J. Pfenning and L. H. Ford, "The unphysical nature of 'Warp Drive'", Class. Quantum Grav. 14, 1743 (1997), [arXiv:gr-qc/9702026](https://arxiv.org/abs/gr-qc/9702026) |
| 4.20 light-years | Proxima Centauri, the nearest star after the Sun, is about 4.24 light-years away. The odometer is an illustration of a trip, not a claimed travel time. | standard value |

Nuance for comments (do not put on screen): later papers reduce the energy (Van Den Broeck 1999) or look for warp shells made of positive energy that travel slower than light (for example Fuchs et al. 2024, "Constant Velocity Physical Warp Drive Solution", [arXiv:2405.02709](https://arxiv.org/abs/2405.02709)). No known solution travels faster than light without negative energy. Say "may not exist" or "nobody knows if enough can exist", never "impossible".

## Sound design (new family: "clockwork and stretched space")
All synthesised in `mix_warp.py`, so there is no licence to credit.
- **Ship's clock:** one soft mechanical tick per second for the whole reel. It never speeds up or slows down, which is the sound version of "its clock ticks normally". In the held breath it is the only sound left.
- **Hits** (sized): frame 0 (medium), ignition at 1.95 s (large, with a reversed swell), twist at 16.2 s (biggest: crack, pitch-drop body, gong partials, sub), and a small thump when the bubble collapses at 19.3 s.
- **Bubble membrane:** a detuned shimmer cluster with tremolo that follows the bubble's strength, and stutters with the flicker during the twist.
- **Stretched-space drone:** two detuned low voices whose beating speeds up with the bubble's speed, muffled while the camera is inside the bubble.
- **Flowing-space rush:** filtered noise that follows the speed, plus a soft flutter at the rate grid lines pass under the ship.
- **Light beam:** a bright ping at 12.3 s that falls in pitch as the bubble pulls away.
- **End:** a warm pad and a rising tone into frame 0, so the loop is audible.
- Sub energy lives on the hit bus only; every other bus is high-passed at 90 Hz for phone speakers. Master is loudness-normalised to about -15 LUFS with true peak measured after AAC encoding.

## Publish copy

### YouTube Shorts
**Title (pick one):**
1. This ship never moves. It still outruns light.
2. How a warp drive actually works (the ship doesn't move)
3. The warp drive that breaks no speed limit

Recommended: option 1 (it matches the hook).

**Description:**
> This ship never moves. It still outruns light.
>
> In 1994 physicist Miguel Alcubierre found a way to "warp" in Einstein's general relativity: squeeze space in front of a ship and stretch it out behind. The ship sits in a bubble of flat space and is carried along. Its engine is off, it feels no push, and its clock ticks normally. The bubble can still outrun a light beam, because the speed of light limits things moving through space, not space itself.
>
> The catch: the bubble needs negative energy. Tiny amounts appear in quantum physics, but nobody knows if enough could ever exist.
>
> A thought experiment: the visuals are an illustration, not to scale. Visuals are 3D-rendered.
>
> Source: M. Alcubierre, "The warp drive: hyper-fast travel within general relativity", Classical and Quantum Gravity 11, L73 (1994).
>
> Slow Light: stories worth slowing down for.
> #space #physics #science

**Hashtags (YouTube shows the first 3 above the title):** #space #physics #science

**Tags (under 500 characters):**
warp drive, alcubierre drive, alcubierre warp drive, faster than light, ftl travel, how does a warp drive work, warp bubble, negative energy, exotic matter, general relativity, spacetime, einstein, space travel, interstellar travel, physics explained, space shorts, science shorts, slow light

**Pinned comment:** If space can move faster than light, but nothing in space can, does the ship ever break the speed limit? 🚀

**Upload settings:** Shorts, Science & Technology, not made for kids. Altered or synthetic content: these are clearly stylised 3D renders, so a label is not strictly required; turn it on if unsure. Thumbnail: a frame from about 6.5 s (the bubble with gold squeezed grid ahead and teal stretched grid behind, "SPACE SQUEEZES AHEAD").

### Instagram Reel (max 5 hashtags)
> This ship never moves. It still outruns light.
>
> A warp drive doesn't push the ship. It squeezes space in front and stretches it behind, and the ship rides along in a bubble of flat space: engine off, no g-force, its clock ticking normally.
>
> The catch? It needs negative energy, and nobody knows if enough can exist.
>
> Follow Slow Light for more stories worth slowing down for.
>
> #warpdrive #space #physics #science #slowlight

### Facebook Reel
> This ship never moves. It still outruns light. Here is how Alcubierre's warp drive works, and the one thing it needs that may not exist. 🚀

## QA (playbook section 7)
- Frame 0: hit plus premise; hook done by about 1.9 s.
- Contact sheet at 2 fps checked: one subject at a time, no white or beige frames, labels legible at phone size.
- Counters are asserted monotonic in `overlay.py` (distance and ship clock); typed text never uses a negative slice.
- Loop: frame 659 to frame 0 is continuous in camera, grid, stars and sound (tick at 0 s and 22 s).
- Audio: loudness and true peak measured on the final AAC file (values in the build log).
