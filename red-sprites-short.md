# Caught on Record #1 — Red Sprites (Slow Light Short)

Format: 9:16, ~26 s + 1.5 s end card. Answer lands by ~15 s. Ends on a line that loops into the hook.
Look reference: `ShortA_He_Opened_The_Door_v2.mp4` (dark, low-key, one red accent, macro close-ups, one escalating idea).

---

## 1. Voiceover (master timeline — pauses beat visuals)

| Time | Line |
|---|---|
| 0–4 | For decades, pilots said they saw red lightning above the storm. |
| 4–6 | Nobody could prove it. |
| 6–9 | Many scientists blamed tired eyes. |
| 9–13 | Then, in 1989, a team in Minnesota was testing a camera… and pointed it at a storm. |
| 13–17 | It caught one. By accident. Red, tens of kilometres above the clouds, gone in milliseconds. |
| 17–22 | We call them sprites. Astronauts have filmed them from orbit. |
| 22–26 | The pilots were right. |

Loop: "The pilots were right." hard-cuts to frame 0 ("…pilots said they saw red lightning").

### Fact guardrails (verify before locking)
- First sprite on video: University of Minnesota, July 1989 (6 July in most sources), found while testing a low-light camera for a rocket launch. Source: NASA Earthdata.
- Sprites sit roughly 40–90 km up, above thunderstorms, and last milliseconds. Never say "shoot into space".
- Earliest known visual report: 1886. Say "pilots" only for the hook; "many scientists doubted" is a fair summary but I have not pinned a primary source — check or soften to "few believed it".
- "Astronauts have filmed them" is supported (NASA Expedition 31, 2012; ESA Mogensen, 2023). Do not say "regularly".

---

## 2. Visual system (one look, escalating)

- Palette: near-black blue-teal (#0B1016), cool steel, **one accent: sprite red (#E0201B)**. Warm amber only for cockpit instruments.
- Lens: 35 mm anamorphic feel, shallow depth of field, fine grain, slow push-ins. No whip pans.
- Escalation: cockpit → storm → doubt → 1989 lab → the flash → real NASA proof → back to cockpit.
- Reference-style overlays added in edit, never baked into clips: monospace label with red cursor block (e.g. `35,000 FT`, `ALTITUDE ~80 KM`), corner label `Dramatised reconstruction`, black end card with serif title + `FULL STORY ON SLOW LIGHT`.
- Hard rules: no faces of real people, no real insignia/liveries on aircraft, no text or captions inside generated clips, no AI dialogue.

### What a sprite must look like (the thing AI gets wrong)
Faint, thin, **vertical** branching tendrils like a jellyfish/carrot, red at the top, dim blue-violet filaments hanging below, sitting *above* a lit cloud top, lasting a blink. NOT a thick bolt, NOT glowing fantasy beams, NOT rising to space.

---

## 3. Reference images to make first (the "bible", ~8 stills, 9:16)

Generate #1 first; feed it as a style reference to all the others so the look locks.

| # | Still | Purpose |
|---|---|---|
| R1 | **Look frame:** cockpit over-shoulder, pilot as silhouette/back of helmet, lightning-lit storm beyond windscreen, faint red flicker far above the cloud | Master palette/lens; also frame 0 of the video |
| R2 | Gloved hand on throttle, rain streaks on glass, red reflection | Macro/detail language (matches the door-handle shots) |
| R3 | Airliner passenger window at night, distant storm, tiny red flicker above it | "Aeroplane" coverage, no faces |
| R4 | Generic fighter jet, night, above storm tops, canopy glint, **no insignia, no tail numbers** | "Fighter jet" coverage |
| R5 | Wide storm cell, anvil top lit from inside, stars above | Environment plate |
| R6 | 1989 lab: vintage low-light TV camera on tripod, CRT monitor glowing, VHS deck, hands only, desaturated + grain | Discovery scene |
| R7 | CRT close-up showing thin red tendrils on the screen | The reveal inside the world |
| R8 | **Sprite hero plate:** wide night, storm anvil lit, sprite blooming above it, built to the anatomy above | Hero moment (cross-check against the NASA clip) |

Real reference to study (not to publish): the NASA clip and its stills `ISS031-E-10711/12/13`.

---

## 4. Shot list + prompts

Image prompt → feed to image model with R1 as style ref. Motion prompt → image-to-video. Generate 2–4 takes of each; keep the best.

Shared suffix for every image prompt:
`9:16 vertical, cinematic, 35mm anamorphic, shallow depth of field, fine film grain, low-key lighting, near-black blue-teal shadows, single red accent, photorealistic, no text, no logos, no insignia, no faces`

| # | Time | VO | Image prompt | Motion prompt |
|---|---|---|---|---|
| 1 | 0–4 | hook | R1: over the shoulder of a pilot in a dark airliner cockpit, silhouette only, amber instrument glow, huge thunderstorm outside lit by flickering lightning, far above the cloud a faint thin red flicker | Very slow push toward the windscreen. Lightning pulses inside the cloud. Red flicker appears once, small. |
| 2 | 4–6 | nobody could prove | R2: extreme close-up of a gloved hand on a throttle, rain on the glass behind, faint red reflection on the glove | Slight rack focus from hand to the glass; red reflection blinks and dies. |
| 3 | 6–9 | tired eyes | R4: generic grey fighter jet silhouette banking above a night storm, canopy glint, no markings; cut with R3 airliner window view | Slow tracking, jet banks away into cloud; window shot: slow push on distant flash. |
| 4 | 9–11 | Minnesota, testing a camera | R6: vintage low-light TV camera on a tripod, CRT glowing, hands adjusting a dial, desaturated 1980s feel | Slow push-in on the camera lens, CRT flicker. |
| 5 | 11–13 | pointed at a storm | Camera aimed out of a dark window/field at a distant storm, tripod silhouette | Slow lateral drift; distant lightning. |
| 6 | 13–15 | It caught one | R7: CRT close-up, noisy picture, red tendrils flash on the screen | Static frame; one-frame flash, tendrils appear, hold 6 frames, fade. |
| 7 | 15–17 | red, tens of km above clouds | R8: sprite hero plate, wide, storm anvil lit, faint sprite blooming above | Slow push-in; blink-fast sprite, then dark. Sprite must be thin, vertical, branching. |
| 8 | 17–22 | astronauts filmed them | **Real NASA clip** (see §5), in a horizontal band; overlay `REAL · NASA ISS, 2012` | Use ~0:04–0:09 of the clip as-is. |
| 9 | 22–26 | pilots were right | R1 again | Same push as shot 1, pilot's head turns slightly toward the red flicker; hold; hard cut to frame 0 loop. |

End card (1.5 s): black, serif `CAUGHT ON RECORD` + monospace `FULL STORY ON SLOW LIGHT`.

Negative prompt (video): `thick lightning bolt, glowing beam into space, fantasy, cartoon, text, subtitles, logo, insignia, face, morphing, warping, extra limbs, flicker artifacts`

---

## 5. Real footage (shot 8)

- Clip: NASA SVS 11059 "Elusive Red Sprite" — https://svs.gsfc.nasa.gov/11059 (ISS Expedition 31, 30 Apr 2012; sprite ~0:06–0:08).
- Source is only 960×540. **Do not crop it to 9:16** — that leaves ~304 px width. Use it as a full-width horizontal band (~1080×608) in the vertical frame, upscale once, and show the credit label. The HD time-lapse is linked from the NASA Earth Observatory article (`myanmar_iss_20120430HD_web.mov`); try that first.
- Credit in description and on-screen: "ISS video and photos courtesy of the crew of Expedition 31 and Image Science & Analysis Laboratory, NASA Johnson Space Center."
- NASA states no explicit public-domain line on the page; check NASA's reproduction guidelines before publishing.

---

## 6. Quality gate (reject a take if any fail)

1. Sprite is thin, vertical, branching, above cloud, brief — not a bolt.
2. No faces, insignia, tail numbers, or readable text.
3. Aircraft geometry is sane (wings, canopy, no morphing).
4. Red is the only accent; no warm sunset colours.
5. Frame 0 reads as a hook on a phone with sound off.
6. Last shot matches frame 0 closely enough that the loop feels intentional.
7. Facts match §1 guardrails.
