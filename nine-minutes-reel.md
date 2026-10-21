# Nine Minutes (CAR-T vs cancer): reel #15

Slow Light remake of the reference "What does it actually look like when a CAR-T cell attacks cancer" (29 s microscopy timelapse). Ours is an original 3D render, not the footage: 22 s, 1080x1920, 30 fps, wordless, loops.

- Final file: `final-reels/nine-minutes.mp4` in the project files (not in git, per `claude.md` rule 6).
- Source: `tools/nine-minutes/` (`index.html` scene with `window.renderAt(t)`, `render.js`, `shot.js`, `overlay.py`, `mix.py`, `build.sh`).

## 1. Concept

One idea: a living drug kills a cancer cell, and you watch the clock while it happens.

- Hook (fully on screen from frame 0, no typing): **WATCH THIS CANCER CELL / DIE IN 9 MINUTES.** over a slowly turning leukemia cell studded with red CD19 markers, labelled CANCER CELL (LEUKEMIA, A BLOOD CANCER). "Cancer" leads because more viewers know it than "leukemia" (owner's call).
- Pattern interrupt at 2.2 s: whip to a teal T cell. Gold Y-shaped receptors sprout all over it: this is the CAR.
- Target first (playbook 3.3): the camera chases the T cell from behind with the cancer cell already ahead and growing.
- Contact starts a **minutes timer that only goes up** (00:00 to 09:00, script-asserted monotonic).
- Held breath at 08:55, then the biggest hit: the cancer cell blebs (round membrane balloons), dims, shrinks and sheds apoptotic bodies.
- Thesis line: **A LIVING DRUG.** The camera flies to the next cancer cell, which is identical to frame 0, so the reel loops.

What makes it ours and not a copy: rendered 3D cells with depth and parallax in place of grey microscopy, a decodable story (receptor, marker, contact, synapse, granules, death), one monotonic counter, our palette, and our own sound family.

## 2. Shot plan (video seconds)

| Time | Shot | On screen |
|---|---|---|
| 0.0-2.2 | Close orbit on the leukemia cell (amber, translucent, red CD19 dots, dark nucleus). Hit on frame 0. | WATCH THIS CANCER CELL / **DIE IN 9 MINUTES.** chip "CANCER CELL" + "(LEUKEMIA, A BLOOD CANCER)", all on from frame 0 |
| 2.2-2.6 | Whip pan to the T cell | |
| 2.6-5.0 | T cell close-up; about 170 gold Y receptors grow in a wave (2.85-4.9) | THE PATIENT'S OWN T CELL / **CAR-T CELL** / "given a new receptor in a lab (the CAR)" |
| 5.0-8.7 | Chase from behind the T cell; it stretches as it crawls; the cancer cell grows ahead | IT HUNTS ONE MARKER / **CD19** / "red dots on the cancer cell" |
| 8.7 | Contact (hit). Timer appears at 00:00 | SINCE CONTACT 00:00 |
| 8.7-12.0 | T cell flattens against the target; glowing synapse disc forms (teal ring, gold core). Timer 00:00 to 03:00 | SYNAPSE FORMING |
| 12.0-13.5 | Synapse stable | LOCKED ON / "stable within ~3 min" |
| 13.5-16.3 | Gold lytic granules gather at the synapse and stream into the cancer cell. Timer to 08:45 | TOXIC GRANULES DELIVERED |
| 15.4-16.3 | Cancer cell shivers | |
| 16.3-17.3 | Held breath, near-silence; timer crawls to 09:00 | |
| 17.3 | Biggest hit, timer pulse at 09:00; blebs balloon out | **APOPTOSIS** / "the cancer cell self-destructs" |
| 18.4-21.0 | Cell shrinks and greys; five apoptotic bodies pinch off; T cell lets go and moves on | |
| 19.5-21.4 | Camera swings to the next cancer cell (already centred, small) and flies in | **A LIVING DRUG.** / "timings from one cell pair in a lab dish · Lee et al., eLife 2020" |
| 21.4-22.0 | Same framing and motion as frame 0: seamless loop | |

Persistent tag: ILLUSTRATION · NOT TO SCALE · TIME-LAPSE.

Scene constants: FOV 60, cancer cell radius 3.2, T cell 1.6 (roughly true ratio for K562 vs a T cell), second cancer cell offset (24,-12,-36) = exactly one period of every camera-wrapped dust lattice, so the background matches at the loop point.

## 3. Facts and sources

Primary source (the study the reference video comes from):
Lee M, Lee Y-H, Song J, Kim G, Jo YJ, Min HS, Kim CH, Park YK. "Deep-learning-based three-dimensional label-free tracking and analysis of immunological synapses of CAR-T cells." *eLife* 2020;9:e49023. https://elifesciences.org/articles/49023

| Claim on screen | What the paper says | Status |
|---|---|---|
| Dies in about 9 minutes | CAR-T cells "induced apoptotic blebbing on the target cells about 9 min after the initial contact" (Results) | Verified |
| Synapse "stable within ~3 min" | Synapse area reached half maximum within 40 s and "reached a steady-state within only 3 min" (K562-CD19, Fig. 8b) | Verified |
| CD19 is the marker | CART19: anti-CD19 scFv (FMC63), CD8a hinge/TM, 4-1BB, CD3ζ; targets were K562 cells transduced with human CD19; CD19-negative K562 did not form a stable synapse | Verified |
| "Leukemia cell" | K562 is a human chronic myelogenous leukemia cell line | Verified (cell line identity) |
| Toxic granules delivered at the synapse | The paper tracks lytic granules "coalescing into the IS" | Verified (wording kept general: no perforin/granzyme claim on screen) |
| "The patient's own T cell, given a new receptor in a lab" | Standard description of autologous CAR-T therapy; the study used T cells engineered with a lentiviral CAR construct | General knowledge; phrased generically |
| Apoptosis / self-destructs | Apoptotic blebbing is a hallmark of apoptosis (programmed cell death) | Verified |

Accuracy guardrails used:
- The 9 minutes is one observation in a lab dish (one effector-target pair, label-free holotomography). The end card says so. Do not claim every CAR-T kill takes 9 minutes, or that this happens in a patient on this clock.
- The video is an illustration: shapes, colours, receptor counts and granule counts are artistic. Tagged "ILLUSTRATION · NOT TO SCALE · TIME-LAPSE".
- No treatment claims, cure claims or survival statistics.

## 4. Sound

Own family, all synthesised in numpy (`tools/nine-minutes/mix.py`), so no credits are needed and the licence is clean:
wet pitch-drop hits with a gong tail on frame 0 / contact / death (death is the biggest), a muffled body "flow pulse" bed that speeds up with the tension and stops in the held breath, glassy plucks as the receptors grow, two sonar pings during the hunt, a tick every 15 timer-seconds (louder on each minute), sparkling granule fizz, bubbly up-sweeps for the blebs and pops for the apoptotic bodies, a soft A-minor-add9 resolve, an end-line bell and a rising loop-link into frame 0. Sub only on the hit bus, other buses high-passed at 90 Hz. Loudness target about -15 LUFS, checked after AAC.

## 5. Publish copy

**YouTube title:** What a CAR-T cell does to cancer in 9 minutes

**Alt titles:** "A living drug vs a leukemia cell" / "Watch a cancer cell self-destruct"

**Description:**
> A CAR-T cell is a patient's own T cell, given a new receptor in a lab so it can recognise a marker on cancer cells (here, CD19 on a leukemia cell). In a lab-dish study, one CAR-T cell locked on to its target within about 3 minutes, and the cancer cell began apoptotic blebbing (self-destructing) about 9 minutes after first contact.
>
> This is a 3D illustration, not microscopy footage. Shapes and colours are artistic and not to scale; timings are from one cell pair in a lab dish.
>
> Source: Lee M. et al., "Deep-learning-based three-dimensional label-free tracking and analysis of immunological synapses of CAR-T cells", eLife 2020;9:e49023. https://elifesciences.org/articles/49023
>
> Sound: original, synthesised for this video.
>
> #CART #Cancer #Immunotherapy #Leukemia #Biology #Science #Shorts

**Instagram / Facebook caption:**
> Nine minutes. That's how long it took one CAR-T cell to make a leukemia cell self-destruct in a lab dish. 🧬
> A CAR-T cell is your own T cell, rebuilt to hunt one marker (CD19).
> 3D illustration, not to scale. Timings: Lee et al., eLife 2020. Original sound.
> #CART #Immunotherapy #Cancer #Science

**Pinned comment idea:** "The 9 minutes is from one cell pair in a lab dish (eLife 2020). Real treatment involves millions of these cells, and each kill can look different."

Upload checklist: AI/synthetic content label ON (it is a rendered illustration); not medical advice; no claims about cure rates.

## 6. QA (playbook section 7)

- Frame 0: hit + premise; full hook already on screen at frame 0.
- Contact sheets at 2 fps checked: one target at a time, no white or beige frames, labels legible.
- Timer monotonic (asserted in `overlay.py`), ends at 09:00 exactly.
- Typed text (end line) starts at n >= 1.
- Loop: last frame and frame 0 share camera formula, cell, CD19 layout and dust lattice.
- Text kept out of the bottom 18% and the top strip.

## 7. Rebuild

```
cd tools/nine-minutes && npm i three@0.170.0 playwright-core@1.56
python3 -m http.server 8771 &          # serve index.html
./build.sh <scratch_dir>               # renders frames (3 workers), overlay, mix, composite
```
