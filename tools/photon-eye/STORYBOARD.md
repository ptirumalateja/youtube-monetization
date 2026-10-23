# The Photon That Made Your Eye: storyboard v2

Slow Light reel. 12.0 s loop, 1080x1920 (9:16), 30 fps, no voiceover. One photon, one story. Footer on every shot: `THOUGHT EXPERIMENT · NOT TO SCALE`.

Status: **storyboard v2, waiting for Teja's approval.** Only stills exist so far; no video has been built.

Hero frames (full 1080x1920): `hero_1_birth.png` to `hero_5_punch.png`, overview in `contact_v2.jpg`. Teja's style reference is `reference_trap.png`. v1 (the diagram look Teja rejected) is in `v1/`.

## What changed from v1

- **New look.** The plates are now GPU fragment shaders (`tools/photon-eye/gl/shots.glsl`), rendered through headless Chromium. That is the same path the video will use, so the stills are what the motion will look like.
  - The Sun's interior is a raymarched tunnel of gold plasma smoke, lit by the photon.
  - The photon leaves smooth, curving light trails with bloom, plus gold bokeh dust.
  - The escape has a plasma jet, a rim light racing along the limb, and ejecta.
  - The eye is a golden starburst iris with Earth reflected in the pupil.
  - The ending is a cloud-lit sunset behind the upright stargazer.
- **4 story beats instead of 6.** The separate "8 minutes to Earth" shot is gone. The beam flies straight from the escape into the eye.
- **Text follows Teja's notes.** The counter is huge and centred, the small `INSIDE THE SUN` label is gone, the escape gets one line, and the eye line is small at the bottom.
- **The beats follow the reel-script structure from Teja's screenshots:** hook, lock-in, body, rehook, body, rehook or payoff, CTA. Each beat is listed with its edit layers (captions, zoom in and out, graphics, BGM and SFX).

## Beats

| Script slot | Time | Picture and camera | On-screen text | Edit layers (zoom / graphics / SFX) |
|---|---|---|---|---|
| **Hook** | 0.0-1.5 | Black. On frame 0 a white-hot dot ignites with a cross-shaped lens flare and drifting gold dust (hero 1). | `THIS LIGHT WAS MADE` / gold `100,000` + `YEARS AGO` | Punch zoom-in (105→100%) on the ignition frame. Sub thump plus a glassy "tink" on frame 0, then a low hum swells |
| **Lock-in** | 1.5-2.5 | The camera rushes back out of the dot and we're inside the Sun: the gold plasma tunnel opens around it (hero 2) | Counter appears, huge and centred: `YEAR 12,000` | Fast pull-back with motion blur. A deep whoosh lands on the reveal |
| **Body 1** | 2.5-6.0 | **Hero shot.** The photon races in long glowing arcs, scatters (a sharp kink with a tiny flash) and arcs off again. Its trail builds into a glowing knot of loops while the fog drifts and the camera slowly rolls. Gold dust floats across in depth | The counter rolls up: `12,000 → 34,000 → 61,240 → 87,000 → ~100,000` and only ever goes up | **Mini rehook at 4.3 s:** a 15° camera roll, a counter jump and a brighter trail. Every scatter is a crisp tick in the mix, with pitch rising under a low-pass that slowly opens |
| **Rehook 1** | 6.0-7.5 | **The escape.** The photon breaks the surface in slow motion. A plasma jet tears up behind it, a rim of light races along the Sun's edge, and sparks fly out into black space (hero 3) | `THEN IT ESCAPED.` | Zoom-out on the break, then a 1.15× slow push. A big whoosh, then **hard silence** for 0.4 s (the biggest contrast in the reel) |
| **Body 2** | 7.5-9.5 | The beam whips across space into an extreme close-up of a human eye. The golden iris fills the frame, and Earth is reflected in the pupil. The photon lands dead centre and the pupil tightens (hero 4) | Small, bottom: `AND ENDED IN YOUR EYE.` (optional chip during the 0.3 s whip: `8 MIN 20 S LATER`) | Whip transition. A soft impact plus a tight "click" as the pupil constricts, with the hum returning quietly |
| **Payoff (rehook 2)** | 9.5-11.4 | Pull back out of the eye to the upright stargazer on a ridge, sunset behind, with gold rim light on the silhouette (hero 5) | Biggest text in the reel: `THE LIGHT YOU SEE WITH` / gold `IS OLDER THAN CIVILIZATION.` | **Biggest hit:** a warm, wide chord swell and a boom at 9.5 s |
| **Loop / CTA** | 11.4-12.0 | The setting Sun shrinks to a single point and the frame goes black, leaving the dot from frame 0 | Nothing on screen; the CTA lives in the caption so the loop stays clean | The chord's tail decays into the frame-0 hum, so the loop is seamless |

Music drop for the silent `_music-ready` copy: **9.5 s**. Secondary accents: 1.5 s (into the Sun) and 6.0 s (escape).

Text-off test: the trap and the escape (hero 2 and 3) carry the reel. Both have to look great with every word hidden.

### The cold open
Teja's black-plus-dot hook stays as the default and is now only 1.5 s. If the first-second hold rate is weak after posting, the cheap fix is to cut straight into the trap shot at frame 0 under the same hook line.

## Fact notes

1. **100,000 years is an estimate.** Published figures for how long energy takes to get from the Sun's core to its surface run from about 10,000 to about 170,000 years, depending on the solar model. 100,000 is a common round number. The caption gives the range.
2. **"One photon" is a storytelling device.** Light inside the Sun is absorbed and re-emitted countless times, so no single photon makes the whole trip. The curved trails are also stylised: between scatterings, a real photon travels in a straight line. The `THOUGHT EXPERIMENT · NOT TO SCALE` footer covers both points. `THIS LIGHT WAS MADE` is kept as Teja wants. `THIS LIGHT STARTED OUT` is the strictly accurate swap if Teja prefers it.
3. **8 min 20 s** is the average Sun-to-Earth light time (about 499 s).
4. **The photon enters through the pupil**, which is the real path to the retina. A bright source makes the pupil constrict, which is true.
5. **Earth in the pupil** is a poetic reflection, an echo of the Andromeda reel. Literally, an eye looking at the sunset would reflect the Sun.
6. **"Older than civilization"** holds: the first cities are about 6,000 years old and farming about 12,000.
7. **The counter only counts up** (no countdown) and lands on ~100,000 as the photon escapes.

## Sound
All synthesised in code (the `sound.mjs` pattern from Not a Vortex), plus CC0 hits that are already in `tools/sfxlib` and credited. A silent `_music-ready` copy is included so Teja can add platform music.

## Publish copy (draft)

**Title options:** `The light in your eye is 100,000 years old ☀️` / `This sunlight took 100,000 years to leave the Sun` / `The Photon That Made Your Eye`

**Facebook Tags:** `Solar physics`, `Astrophysics`, `Sun`, `Photon`, `Science education`, `Optics`

**Caption**
```
The sunlight hitting your eye right now is 8 minutes old in space.

But it started out about 100,000 years ago, deep inside the Sun.

It spent all that time bouncing randomly through the Sun's dense interior, absorbed and re-emitted over and over, trying to get out.

8 minutes to reach you. 100,000 years to be made for you.

What were humans doing 100,000 years ago? Best answer gets pinned 👇

Thought experiment. Not to scale. (Estimates for the escape run from about 10,000 to 170,000 years.)

#PhotonStory #Sunlight #SlowLight #Astrophysics #Time
```

**CTA:** the comment question in the caption, plus a pinned comment: "Fun fact: 100,000 years ago our species was already here, still living as hunter-gatherers." (Homo sapiens is about 300,000 years old.)

**Upload:** label as AI/synthetic (computer-generated visualisation).

## Build plan once approved
Animate the same shaders over time (the fog drifts, the trail grows, the camera rolls) in `tools/photon-eye/`, and render natively at 1080x1920, 30 fps. Deliverables: `_music-ready` silent copy, `_master`, contact sheet, `.md` notes and publish copy.
