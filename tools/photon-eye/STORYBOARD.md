# The Photon That Made Your Eye: storyboard v1

Slow Light reel. 12.0 s loop, 1080x1920 (9:16), 30 fps, no voiceover. Footer on every shot: `THOUGHT EXPERIMENT · NOT TO SCALE`.

Status: **storyboard only, waiting for Teja's approval.** Nothing has been built or rendered yet apart from the concept stills.

Concept stills (code-rendered with numpy, so they show the look and the framing, not final quality): `still_01_birth.png` to `still_07_alt_hook.png` and `contact.jpg` in this folder. Script: `tools/photon-eye/stills.py` on branch `claude/project-thread-hvny5h`.

## How it gets built (after approval)

- Same engine as Not a Vortex: three.js `renderAt(t)` in headless Chromium, rendered natively at 1080x1920. The Sun's interior is a raymarched noise volume (gold fog, with darker cells and brighter scattering sparks). The photon is a white-hot point with additive glow, and its random-walk path is drawn as a fading light trail, like the vortex coils but packed into a small space.
- The stargazer is the upright modern silhouette rig from What Andromeda Sees (`tools/alien-perspective`), ported over and rim-lit gold by the sunset.
- The eye is drawn procedurally (iris fibres, sclera, lids, lashes, wet catchlight). No footage, no stock.
- Sound is synthesised in code (the `sound.mjs` pattern from Not a Vortex), optionally with CC0 hits that are already in `tools/sfxlib` and credited. Nothing else.

## Beats (Teja's version, kept as the default, with fact fixes)

| # | Time | Picture and camera | On-screen text | Sound |
|---|---|---|---|---|
| 1 | 0.0-2.0 | **The birth.** Pure black. On frame 0 a white-hot dot ignites at centre with a horizontal lens streak and a gold halo that breathes. Locked camera, very slow push in. (still 01) | Huge, centre: `THIS LIGHT STARTED OUT` then gold, bigger: `~100,000 YEARS AGO` | Sub thump and a glassy "tink" at ignition on frame 0, then a deep low hum swells |
| 2 | 2.0-5.5 | **The trap (hero shot).** Fast pull back from the dot: we are inside the Sun. Thick gold plasma fills the frame edge to edge, with a vignette pressing in. The photon zig-zags at insane speed; every scatter is a kink with a tiny flash, and the trail fades behind it into a tangled glowing knot. The camera drifts and slowly rotates to feel claustrophobic. Sub-beats so something new lands every ~1 s: trail density builds (2.0), camera rolls 15° (3.2), trail colour shifts gold to white-hot (4.3). (still 02) | Small top: `INSIDE THE SUN`. Count-up counter, lower third, mono: `YEAR 1 → 10,000 → 61,240 → 87,432 → ~100,000`. It only ever goes up and lands on ~100,000 exactly as the photon breaks out | Muffled pressure rumble, dense crackle where each scatter is a tick, pitch rising under a low-pass that slowly opens |
| 3 | 5.5-6.5 | **The escape.** The photon finds the surface and bursts through in slow-mo: a flash ring on the photosphere, then hard contrast from gold fog to black space. Camera is low on the Sun's limb looking up. (still 03) | `THEN IT ESCAPED.` | Big whoosh, then **hard silence** for about 0.4 s (the biggest contrast in the reel) |
| 4 | 6.5-8.0 | **The fall.** One straight beam from the Sun (glow below frame) to Earth. Stars streak outward like warp speed. Earth grows from a dot to a marble as the photon closes in. Camera rides just behind the photon. (still 04) | `8 MIN 20 S TO EARTH` and small `299,792 KM/S` | Air-tearing high whistle with a Doppler rise; star streaks whip past |
| 5 | 8.0-9.5 | **The meeting.** Earth fills the screen, then a hard cut to an extreme close-up of a human eye. The photon flies straight into the pupil. The pupil snaps smaller, and the Sun's catchlight glints on the cornea. Hold about 1 s on the eye. (still 05) | `AND LANDED IN YOUR EYE.` (Teja's `TO MAKE YOUR EYE SEE` also works; see the fact notes) | Soft impact plus a tight "click" as the pupil constricts; the hum returns, quietly |
| 6 | 9.5-12.0 | **The punch, loop point.** Pull back out of the eye to the upright stargazer silhouette on a ridge at sunset, the Sun low on the horizon, gold rim light. At 11.6 s the Sun shrinks to a point and the frame drops to black, so the last frame is the dot from frame 0. (still 06) | Biggest text in the reel: `THE LIGHT YOU SEE WITH` / `IS OLDER THAN CIVILIZATION.` Bottom small: `THOUGHT EXPERIMENT` | **Biggest hit:** a warm, wide chord swell and a boom at 9.5. Its tail decays into the low hum that frame 0 starts on, so the loop is seamless |

Music drop for the silent `_music-ready` copy: **9.5 s** (the punch). Secondary accents: 5.5 s (escape), 8.0 s (eye).

Text-off test: shots 2 and 3 (the gold random walk and the escape flash into black) are the key moments. They have to look spectacular with every caption hidden, and the build will be judged on that first.

## The cold-open risk, and a stronger alternative

Black plus one small dot for the first 2 s is the weakest picture in the reel, and it sits exactly where people decide to keep watching. The hook text carries it, but in a muted autoplay feed the frame reads as nearly empty, which goes against the payoff-first rule from the Roberto Carlos feedback.

**Option B (payoff-first open):** open on the hero shot. Frame 0 is already inside the Sun with the trail glowing and the photon bouncing, under `THIS LIGHT IS / ~100,000 YEARS OLD.` and small `IT STILL HASN'T LEFT THE SUN` (still 07). Everything after it stays the same, except the birth beat becomes a 0.3 s ignition flash at frame 0 and the trap runs 0.0-5.5 s (5.5 s total, with the same sub-beats). For the loop, the punch shot pushes into the setting Sun until its disc fills the frame and becomes the plasma of frame 0, a match cut instead of a drop to black.

I wrote the storyboard with Teja's version (A) as the default. My recommendation is B, because it puts the most beautiful frame on frame 0.

## Fact notes (handled honestly)

1. **~100,000 years is an estimate, not a measurement.** How long energy takes to get from the core to the surface depends on the solar model; published figures run from about 10,000 to about 170,000 years, and ~100,000 is a common round number. That's why the text says `~100,000` with a tilde, and why the caption gives the range.
2. **"One photon" is a storytelling device.** In reality, light inside the Sun is absorbed and re-emitted countless times. The energy starts as gamma rays in the core and leaves as visible light from the surface, so the photon that reaches you is not the one that was born in the core. That's what `THOUGHT EXPERIMENT · NOT TO SCALE` covers, and it's why I suggest `THIS LIGHT STARTED OUT ~100,000 YEARS AGO` over `THIS LIGHT WAS MADE 100,000 YEARS AGO`. "Made" claims one particle was created and survived; "started out" stays true for the energy.
3. **8 min 20 s** is the average Sun-Earth light time (about 499 s). It varies from about 8 min 10 s to 8 min 27 s over the year. Teja's correction holds, so the screen says `8 MIN 20 S`, not `8 MINUTES`.
4. **The photon goes through the pupil, not the iris.** Light that you see passes through the pupil and lands on the retina. The iris is the coloured ring that blocks light. So the photon flies into the black centre, and the pupil constricting is the eye's real response to bright light.
5. **"Older than civilization" holds.** The first cities are about 6,000 years old and farming about 12,000, so ~100,000 years is well past both, and even the low 10,000-year estimate beats the first cities. `OLDER THAN THE FIRST CITIES` would be completely bulletproof if you want it tighter.
6. **The counter counts up, like the Andromeda odometer.** It is not a countdown and never pauses for a quiz, and it is asserted monotonic in code.
7. **Sun safety.** The stargazer looks at a low sunset Sun, and the eye shows a reflection. Nothing on screen suggests staring at the Sun, and the caption can carry a one-line reminder.
8. **Title wording.** "The Photon That Made Your Eye" can read as "the photon created your eye". It works as a working title. For the YouTube title, `The light in your eye is 100,000 years old` is clearer (options below).

## Publish copy (draft, built from Teja's)

**Title options**
- The light in your eye is 100,000 years old ☀️
- This sunlight took 100,000 years to leave the Sun
- The Photon That Made Your Eye (Teja's)

**Facebook Tags (Business Suite Tags box):** `Solar physics`, `Astrophysics`, `Sun`, `Photon`, `Science education`, `Optics`

**Caption**
```
The sunlight hitting your eye right now left the Sun 8 minutes and 20 seconds ago.

But its journey started about 100,000 years ago, deep inside the Sun.

All that time it was absorbed and re-emitted, over and over, wandering at random through the Sun's dense interior, trying to get out.

8 minutes to reach you. ~100,000 years to escape.

Thought experiment, not to scale. Scientists' estimates for the escape run from about 10,000 to 170,000 years, and the "photon" is really energy passed from atom to atom. (And please don't stare at the Sun.)

#PhotonStory #Sunlight #SlowLight #Astrophysics #Time
```

**Hashtags (end of description):** `#PhotonStory #Sunlight #SlowLight #Astrophysics #Time`

**Upload:** label as AI/synthetic (computer-generated visualisation), as with the other code-rendered reels.

## What I need from Teja

Approve, or edit, any line above. In particular: cold open A (as written) or B (payoff-first), and whether the wording changes (`STARTED OUT`, `~100,000`, `AND LANDED IN YOUR EYE.`) are OK. I won't build or render anything until the storyboard is approved.
