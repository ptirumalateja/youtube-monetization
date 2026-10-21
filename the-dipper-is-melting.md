# The Dipper Is Melting (reel 11)

Slow Light take on the reference reel "The Universe Is Moving. Your Sky Just Hides It." We kept only the topic. Everything else is ours: the scene, the data, the text and the sound.

- **Final file:** `final-reels/the-dipper-is-melting.mp4` in the project files. It is 20.0 s, 1080x1920 (rendered natively), 30 fps, H.264 at 10 Mb/s two-pass + AAC 192k, 25.6 MB, and it loops. Loudness after AAC: -15.4 LUFS integrated, -3.9 dBFS peak. A CRF 18 master (225 MB, mostly film grain) is not kept; re-encode from frames if you need it.
- **Source:** `tools/dipper-melting/`. The scene is `index.html` with `window.renderAt(t)`, `stars.py` builds the star data, the timeline is `timeline.json`, `overlay.py` draws the info layer and `mix_dipper.py` makes the sound. `render.js`, `shot.js` and `proj.js` are the Playwright drivers.
- **Format:** wordless, no voiceover, a few words of on-screen text, one monotonic counter, one paradox beat, a loop (playbook section 1).

## Concept

The Big Dipper looks permanent, but its seven stars are moving in different directions. We run the sky forward 100,000 years using each star's real measured motion, and the familiar ladle slides out of shape. Five of the seven stars stay together because they are one family, the Ursa Major Moving Group. Dubhe and Alkaid are not in that family, and they wander off. The twist is that the stars only look fixed: a human life is far too short to see this motion.

Why it differs from earlier reels: there is no tunnel, no rings and no galaxy plate (Night Sky), and no log-zoom ladder (Scale Ladder). The look is a star chart with long-exposure trails over faint integrated-flux cirrus. The camera grammar is a third type, a **time-lapse hold**: the camera stays on one patch of sky and time is what moves.

## Shot plan (video seconds)

| Time | Shot | Text | Sound |
|---|---|---|---|
| 0.0-2.0 | The Dipper as it is today, hanging bowl-up, already drifting. The stars flare on frame 0. | Hook typed fast: "THE BIG DIPPER / IS **MELTING.**" (red chip) | Hit on frame 0. The seven-star chord blooms (one pure voice per star). |
| 2.0 | Snap: a small push-in kick and a 10% flash. Time starts. | Counter "THE SKY IN / 0 YEARS" appears | Reverse suck, a vacuum, then the snap hit and a whoosh |
| 2.0-9.0 | Time-lapse speeds up from 0 to 60,000 years. Every star draws a trail from where it is today. Fast nearby stars streak across the field. The lines of the Dipper stretch. | Counter climbs. Small tag "REAL STAR MOTIONS · HIPPARCOS DATA" | A time whirr whose pitch follows the speed of time, plus star-dust grains. The chord starts to bend. |
| 9.3-12.6 | The family beat. Five trails turn teal and get teal rings. At 11.0 Dubhe and Alkaid get red rings and name labels; their trails stay gold. | "5 OF THESE 7 STARS" (red chip) / "TRAVEL TOGETHER", then "DUBHE AND ALKAID DON'T" | A unison ping for the five, then two sour pings for the loners |
| 12.6-13.17 | Held breath (time keeps creeping, 95,000 to 100,000) | | Near silence |
| 13.2 | Reveal. The counter lands on 100,000 YEARS with a pulse and a 14% flash. Today's shape appears as a dashed ghost. | "SAME 7 STARS." with a "TODAY" label at the ghost | The biggest hit (CC0 explosion layer, sub wall). The melted chord swells. |
| 14.4-17.6 | The camera pulls back into a wide sky full of trails. | Twist typed: "THE STARS ONLY / LOOK **FIXED.**" (red chip) | Wide whoosh, wind bed |
| 17.8-19.55 | Rewind: the stars slide back to today and the trails retract. The counter is hidden, so it never runs backwards. | none | Reverse whoosh, tape-rewind chirps, chord pitch rises and bends back to pure |
| 19.55-20.0 | Today's Dipper again, the same as frame 0 | none | Loop-link tone, then a short vacuum into the frame-0 hit |

## How the motion is computed (real data)

- **Catalogue:** HYG Database v4.1 (astronexus, CC BY-SA 4.0), which takes positions, parallaxes and proper motions from the Hipparcos new reduction (van Leeuwen 2007) and radial velocities from compiled catalogues. Download: `https://raw.githubusercontent.com/astronexus/HYG-Database/main/hyg/CURRENT/hygdata_v41.csv` (not committed, 34 MB). `stars.json` is derived from it.
- **Method:** each star is moved in 3D (`xyz + v·t` in parsecs, including radial velocity), then projected onto a gnomonic sky plane centred at RA 12h21m, Dec +55.5°, every 1,000 years from 0 to 100,000. This includes perspective effects that a flat proper-motion shift would miss. We use 1,756 stars down to magnitude 6.8 within 52° of the centre. Stars that leave the field where the projection still works are dropped (for example Arcturus and Groombridge 1830); the seven Dipper stars are always kept.
- **The seven stars (HYG v4.1):**

| Star | Distance | Proper motion (mas/yr, RA·cosδ / Dec) | Radial velocity | Moves in 100,000 years | Ursa Major Moving Group |
|---|---|---|---|---|---|
| Dubhe (α UMa) | 123 ly | -136.5 / -35.3 | -9 km/s | 4.2° | **no** |
| Merak (β UMa) | 80 ly | +81.7 / +33.7 | -12 km/s | 2.7° | yes |
| Phecda (γ UMa) | 83 ly | +107.8 / +11.2 | -13 km/s | 3.2° | yes |
| Megrez (δ UMa) | 81 ly | +103.6 / +7.8 | -13.4 km/s | 3.1° | yes |
| Alioth (ε UMa) | 83 ly | +111.7 / -9.0 | -9 km/s | 3.3° | yes |
| Mizar (ζ UMa) | 86 ly | +121.2 / -22.0 | -5.6 km/s | 3.6° | yes |
| Alkaid (η UMa) | 104 ly | -121.2 / -15.6 | -11 km/s | 3.7° | **no** |

For scale, the full Moon is about 0.5° wide. Over 100,000 years Dubhe moves about eight Moon-widths.

## Facts and sources (checked for the brief)

1. **"5 of these 7 stars travel together."** Merak, Phecda, Megrez, Alioth and Mizar belong to the Ursa Major Moving Group. Dubhe and Alkaid are not members and move in different directions. Sources: King, J. R. et al. 2003, *AJ* 125, 1980, "Stellar Kinematic Groups II: A Reexamination of the Membership, Activity, and Age of the Ursa Major Group" (doi:10.1086/368241); the Wikipedia summary at https://en.wikipedia.org/wiki/Ursa_Major_moving_group.
2. **The group's core is about 80 light-years away** (same sources). This matches the HYG distances of 80-86 ly for the five members. Dubhe (123 ly) and Alkaid (104 ly) are farther away.
3. **The shape after 100,000 years** is computed from the catalogue values above, not drawn by hand. In it the bowl stretches as Dubhe heads one way and Merak the other, and the handle bends where Alkaid breaks away from Mizar. This agrees with the familiar textbook "Big Dipper 100,000 years from now" diagrams.
4. **"The stars only look fixed."** Proper motions are tiny on human timescales. Even Dubhe, the fastest of the seven, moves about 0.14 arcseconds a year, which would take roughly 13,000 years to shift the width of a full Moon.
5. **Visual liberties (said in the tag and the copy):** the star sizes, glows, trails and lines are artistic, and the sky is rotated so the Dipper hangs vertically for a 9:16 frame. The positions and motions are real. No "not to scale" tag is needed because no distances or sizes are compressed; the tag says "REAL STAR MOTIONS · HIPPARCOS DATA" instead.

## Sound: the seven-star chord (new family, playbook 4.2)

- Each Dipper star is one voice of a pure D add9 chord (D3 A3 D4 F♯4 A4 D5 E5). As the years run, the five family voices bend together by -35 cents, so they stay in tune with each other. Dubhe drifts +85 cents and Alkaid -120 cents, so the chord goes sour as the shape melts. The rewind bends it back to pure for the loop.
- The time-lapse has a whirr whose pitch is the speed of time, plus star-dust grains that get denser as time speeds up. There are only three hits: frame 0, the snap at 2.0 s and the reveal at 13.2 s (the biggest). A held breath sits before the reveal, there is a tape-rewind gesture and a loop-link tone.
- Everything is synthesized in `mix_dipper.py` except two **CC0** Freesound files: 22331 "wind.ogg" by sleepCircle and 814046 "Explosion From Another Dimension" by qubodup. **No credit is required.** Optional courtesy line: "CC0 sounds by sleepCircle and qubodup via Freesound."
- No ticks and no shepard tones, so the sound does not copy the Scale Ladder's character.

## Publish copy

**YouTube Shorts title (pick one)**
- A: The Big Dipper Is Melting 🌌 (100,000 years of real star motion)
- B: The Big Dipper won't last. Here's why.

**Description**
> Run the sky forward 100,000 years and the Big Dipper falls apart. Five of its seven stars (Merak, Phecda, Megrez, Alioth and Mizar) are one family, the Ursa Major Moving Group, about 80 light-years away and travelling together. Dubhe and Alkaid aren't in it, and they wander off on their own. Every star in this video moves by its real measured motion (Hipparcos data via the HYG database). The stars only look fixed because our lives are short.
>
> Star data: HYG Database v4.1 (astronexus, CC BY-SA 4.0), from the Hipparcos new reduction (van Leeuwen 2007). Star sizes, glows and trails are artistic; positions and motions are real.
> Sound: original synthesis plus CC0 sounds by sleepCircle and qubodup via Freesound.
>
> #space #astronomy #bigdipper #stars #ursamajor #science #shorts

**Pinned comment:** "Which constellation should we melt next? 👇 (Orion is wild.)"

**Instagram / Facebook caption**
> The Big Dipper is melting. 🌌 Run the sky forward 100,000 years using each star's real motion: 5 of the 7 stars travel together as one family, and 2 go their own way. The stars only look fixed.
> Star data: Hipparcos via the HYG database. Sound: original + CC0 (Freesound).
> #space #astronomy #bigdipper #stars #science #reels

**Upload checklist:** turn on the AI/synthetic content label. Loop playback is on by default for Shorts.

## Rebuild

```bash
cd tools/dipper-melting
npm i three@0.170.0 playwright-core@1.56.1
python3 stars.py /path/to/hygdata_v41.csv stars.json      # already committed as stars.json
python3 -m http.server 8771 &
node proj.js proj.json                                       # overlay anchors
for w in 0 1 2 3; do node render.js 1080 1920 frames $w 600 4 & done; wait
python3 overlay.py proj.json overlay.mov
python3 mix_dipper.py mix.wav
ffmpeg -framerate 30 -i frames/f%04d.jpg -i overlay.mov -i mix.wav \
  -filter_complex "[0:v][1:v]overlay=0:0,format=yuv420p[v];[2:a]volume=<gain>dB,asoftclip=type=tanh,alimiter=limit=0.89[a]" \
  -map "[v]" -map "[a]" -c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k -movflags +faststart master.mp4
# share size: two-pass 10 Mb/s (the grain makes CRF files huge)
ffmpeg -i master.mp4 -c:v libx264 -b:v 10M -preset slow -pass 1 -an -f null /dev/null
ffmpeg -i master.mp4 -c:v libx264 -b:v 10M -maxrate 14M -bufsize 20M -preset slow -pass 2 -c:a copy -movflags +faststart the-dipper-is-melting.mp4
```
The mix used `volume=-4.3dB` (raw mix is -10.7 LUFS).
