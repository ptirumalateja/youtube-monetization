# Proton Laps: One Minute

- **Video:** `final-reels/proton-laps-one-minute.mp4` in the project files (not in git). 31 s, 1080x1920, 30 fps, loops, no voiceover.
- **Status:** v2 rendered 21 Oct 2026 in the cloud (v1, 30 s with a flat ring disc, was replaced the same night after Teja asked for spirals, pointing at a Van Allen belt proton reel as the style reference). This is the cut Teja asked for after v1 (`proton-laps-earth.md`): a realistic Earth, 7.5 laps a second, and one full minute of laps (448) inside about 20 s of clip.
- **Build:** `tools/proton-minute/` (see its README).

## Concept
An LHC proton (99.999999% of light speed) could lap Earth's equator 7.48 times a second. Keep it going for one minute: 448 laps, 17,987,547 km. That is 46 trips to the Moon, in sixty seconds.

## Shot plan
| Time | Shot |
|---|---|
| 0-3.0 | Real Earth (NASA Blue Marble day, city lights on the night side, clouds). A real-speed comet of light whips round the equator. Hook, readable from frame 1: "THIS PROTON / LAPS EARTH 7.5× / EVERY SECOND." |
| 3.0-5.8 | "HOW MANY LAPS / IN ONE MINUTE?" Big LAPS counter appears, TIME and KM beside it. |
| 3.0-23.0 | One real minute in 20 s. Playback ramps x1 -> x5 (shown live as "PLAYBACK ×N"). The proton's trail is a tight glowing coil; each lap's orbit tilts and turns a little, so the 448 laps of spirals build a solid orange belt round the globe (newest laps white-gold, older ones cooling to deep red). Zoom blur and camera shake grow with the speed. Red chips at 10 s · 74 laps, 20 s · 149, 30 s · 224, 40 s · 299, 50 s · 374. |
| 23.0-25.2 | Hard stop on 60.0 s: flash, jolt, "448 LAPS. / IN 60 SECONDS. / 17,987,547 KM". |
| 25.2-28.9 | Pull back to the Moon at its true distance ("384,400 KM · TO SCALE"). "THAT'S 46 TRIPS / TO THE MOON." A bright proton shuttles Earth to Moon and back, slowly at first then a blur, leaving one arc per trip; TRIPS counter lands on 46 with a hit. |
| 29.0-30.1 | "IN ONE MINUTE." chip "REAL PROTONS · CERN LHC", "99.999999% OF LIGHT SPEED". |
| 29.9-31.0 | Snap back to Earth, the belt unwinds, the hook returns (loop). |

## Facts and sources
- Speed of light 299,792.458 km/s (exact, SI). Earth's equatorial circumference 40,075.017 km (WGS 84). 299,792.458 / 40,075.017 = 7.4808 laps per second.
- One minute: 60 x 7.4808 = 448.85 laps, so 448 full laps; 60 x 299,792.458 = 17,987,547 km.
- Moon: mean Earth-Moon distance 384,400 km (NASA). 17,987,547 / 384,400 = 46.8, so 46 full trips (one way).
- LHC protons at 6.8 TeV run at 99.99999905% of c (rounded on screen to 99.999999%), which is within 3 m/s of light, so the light-speed figures above hold to better than a part in 100 million.
- Counters are exact at every frame: clip time u maps to real time s = u + 0.1 u² (60 s at u = 20).
- On screen: "THOUGHT EXPERIMENT" (real LHC protons circle a 27 km ring, not Earth). The coil drawn round each orbit (about 200 km across), the orbit tilt and the belt's growing radius are visual devices; each lap still stands for one 40,075 km lap. The Earth-Moon distance shot is to scale.

## Images
- Earth day: NASA Blue Marble (NASA Visible Earth), public domain. Night lights: NASA Black Marble, public domain. Downloaded from the three-globe example mirror on GitHub because NASA's own servers are blocked from the cloud build box; same images.
- Clouds and the Moon surface are generated in code (`make_clouds.py`, `scene.js`), so no third-party rights.

## Sound
Fully synthesised (`tools/proton-minute/sound.mjs`, no credits): a tick on each of the 448 laps (clicks that accelerate into a buzz), an engine whine whose flutter is the lap rate, a kick on every real second (60 to 300 BPM), milestone hits every 10 s, a big stop hit at 448, a pull-back whoosh, one plink per Moon trip, reverse rise into the loop.

## Publish copy
- **YouTube title:** This Proton Laps Earth 448 Times in One Minute #shorts
- **Alt title:** 1 Minute at 99.999999% Light Speed = 46 Trips to the Moon
- **Description:** Protons in CERN's Large Hadron Collider move at 99.999999% of the speed of light: 7.5 laps of Earth every second. Keep that up for one minute and it's 448 laps, nearly 18 million km. That's 46 trips to the Moon. In sixty seconds. Thought experiment: real LHC protons circle a 27 km ring, not Earth. #physics #cern #lhc #speedoflight #space #science #shorts
- **Tags:** proton speed, speed of light, LHC, CERN, large hadron collider, earth moon distance, particle physics, physics facts, slow light
- **Pinned comment:** "Guess before the end: how many laps in one minute? Then tell me if you got close to 448."
- **Instagram / Facebook:** "This proton laps Earth 7.5 times a SECOND. ⚡ Give it one minute: 448 laps. 46 trips to the Moon. #physics #cern #speedoflight #space #mindblown #slowlight"
- **Upload checklist:** AI/synthetic content label on. Loop on. No music credits needed.
