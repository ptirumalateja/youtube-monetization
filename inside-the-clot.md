# Inside the Clot (24 s, no voiceover)

Reel #5 of the reference remakes (`ref-remakes-plan.md`). Topic taken from the ref "Every 40 seconds, someone in the US has a heart attack" (145 s voiced explainer); nothing else taken from it: no footage, assets, text or layout.
File: `final-reels/inside-the-clot.mp4` (project files), 1080x1920, 30 fps, 24.0 s, loops (last frame dips to the opening heart, frame 0 is the same camera on the same heart).
Source: `tools/inside-the-clot/` (`index.html` scene with `window.renderAt(t)`, `render.js`, `shot.js`, `proj.js`, `overlay.py`, `mix.py`).

## Concept
One continuous story about a single heart: the viewer dives into a coronary artery, watches a plaque build for decades, sees its cap crack, watches a clot seal the artery in minutes, then comes back outside to watch the muscle downstream go dark.
The twist is the real mechanism most people miss: the plaque only narrowed the artery; **the clot is what closed it**. The end line is the public-health message: time is muscle, call emergency services.

- **Hook (frame 0):** a beating heart, the culprit spot on the front artery already ringed in red, "A HEART ATTACK / STARTS WITH A CRACK." typed by 1.9 s on a big heartbeat hit.
- **Monotonic counters:** `AGE 25 -> 55` while the plaque grows; `0 -> 90 MIN` "minutes without blood" while the muscle dies. Both asserted frame by frame in `overlay.py`.
- **Paradox beat:** "THE PLAQUE DIDN'T BLOCK IT. THE CLOT DID."
- **Held breath:** 8.6-9.3 s, heartbeat and flow drop out, a thin high tone, then the crack is the biggest hit.
- **Tag:** "ILLUSTRATION · NOT TO SCALE · TIME COMPRESSED" (blood cells are huge compared with the artery, decades and minutes are compressed).
- **No gore:** the heart is a glowing fibre-line model, blood cells are amber discs, the dying muscle turns cold slate with a red wavefront marker.

## Look
- New designs for this channel (no reuse of Night Sky, Scale Ladder or other reels): a heart built from ~95k points laid along the real helical muscle-fibre directions (two counter-wound layers in the left ventricle), right ventricle, atria, aortic arch and pulmonary trunk; gold coronary arteries (LAD, diagonal, circumflex) with travelling flow pulses.
- Artery interior: a curved tube with an endothelium of flow-aligned cobblestone cells (teal), pulsing with the heartbeat; 170 instanced biconcave red cells tumbling downstream; a plaque that grows eccentrically to about 45 % diameter narrowing, its fatty core glowing through a thinning cap.
- Rupture: a jagged red seam opens along the cap crest, core debris puffs into the stream.
- Clot: 9,500 platelet granules stream in and stack outward from the crack, a fibrin mesh grows through them, red cells get trapped, the lumen is shut at 13.0 s; downstream the wall goes cold and dark.
- Outside again: the LAD below the clot turns grey, a red marker sits on the blocked spot, and the front wall below it goes dark as a wavefront spreading from the blockage toward the apex; that region stops contracting while the rest of the heart keeps beating.
- Palette per the playbook: navy-black, cream text, gold/teal, red only for the crack, wavefront, markers and chips. Grade: teal shadows, warm highlights, vignette, fine grain. Bloom after a soft clamp (no white-outs).

## v3 (21 Oct): crowd opening + voiceover, 24.9 s
Teja asked for an opening on a crowd, a zoom onto one person pressing his chest, then the heartbeat and clot story, with a voiceover from the first frame, under 25 s.
- **0-3.2 s:** x-ray crowd (rim-lit silhouettes) walking across a wet night plaza with city bokeh. One man (warm rim) stops, presses his left chest; his heart glows red-gold through it, beating; red ring marker. Camera flies from high-wide down to his chest and dives in (flash) onto the beating heart.
- **Hook text from frame 0:** "EVERY 40 SECONDS" / "SOMEONE IN THE US" / red chip "HAS A HEART ATTACK."
- **3.2-24.9 s:** the v2 heart / artery / crack / clot / dying-muscle film, time-warped (monotone cubic) so each beat lands on its voice line: snap 4.4, crack 10.75 (on "cracks"), clot shut ~14.2, muscle 14.4-19.0, twist 19.0-21.6, end line 21.6-24.9.
- **Voiceover (stand-in):** ElevenLabs refused (rate limited), so the take is Kokoro TTS (open model, voice `am_michael`), generated line by line with `tools/inside-the-clot/vo.py`. Swap for an ElevenLabs or recorded take by replacing the nine line files; starts are in `mix3.py`.
  > Every forty seconds, someone in the US has a heart attack. It starts inside an artery, decades earlier. Fatty plaque builds in the wall. Then its cap cracks. A clot seals the crack... and the artery. Within twenty to forty minutes, the heart muscle starts to die. The plaque didn't block it. The clot did. Time is muscle. Call emergency services.
- **Sound:** `mix3.py` adds crowd murmur and footsteps, a heartbeat that rises as the camera closes on him, a dive hit; all v2 events are placed through the same warp; effects are ducked under the voice. Still no samples.
- Built natively at 1080x1920 (no upscale).

## Shot plan v2 (frozen, video seconds; v3 maps these through the warp)
| Time | Shot | On screen |
|---|---|---|
| 0.0-2.25 | Exterior heart, beating (66 bpm), slow push toward the culprit spot on the LAD; glow + red ring on it | hook typed 0.25-1.9 |
| 2.25 | Snap: dive into the artery at the spot (flash 14 %) | |
| 2.25-8.6 | Flight down the artery with the blood cells; plaque grows on the floor; camera slows and settles above it | "INSIDE A HEART ARTERY" (2.6-4.6); "PLAQUE BUILDS FOR DECADES" / AGE 25->55 / PLAQUE chip / "FAT + CHOLESTEROL INSIDE THE WALL" (4.6-8.6) |
| 8.6-9.3 | Held breath: flow slows, heartbeat drops out | |
| 9.3 | Cap cracks, red seam, debris puff, small camera shake, red flash 10 % | "THE CAP CRACKS" / "THE BODY TREATS IT AS A WOUND" (9.3-11.2) |
| 9.7-13.0 | Platelets + fibrin build the clot outward from the crack; cells trapped; flow stops; downstream wall goes dark | "A CLOT SEALS IT" / "PLATELETS + FIBRIN. BLOOD STOPS." (11.2-13.45) |
| 13.0-13.55 | Camera pulls back up the artery, flash to outside | |
| 13.55-18.7 | Same heart; LAD below the clot greyed; dark wavefront spreads down the front wall | "MINUTES WITHOUT BLOOD" / 0->90 MIN; from 20 MIN: "MUSCLE STARTS TO DIE" / "FROM ~20-40 MIN, THEN IT SPREADS" |
| 18.8-21.0 | Slow orbit on the heart | "THE PLAQUE / DIDN'T BLOCK IT. / THE CLOT DID." |
| 21.1-24.0 | Camera eases back to the opening framing; dip to black over the last 0.28 s into frame 0 | "TIME IS MUSCLE." + "CHEST PAIN? CALL EMERGENCY SERVICES." |

## Sound ("pulse and pressure" family, new for this reel)
Every sound is synthesized in `mix.py` (numpy): no samples, so nothing to credit and no licence to check.
- Heartbeat (lub-dub, 66 bpm) with weight in the 90-300 Hz band so phones reproduce it; muffled through the vessel wall while inside; uneven and weaker after the blockage; clean again on the end line.
- Pulsatile flow bed inside the artery; a turbulence hiss (a "bruit") rises as the plaque narrows the lumen; flow sound closes down as the clot shuts it.
- Year ticks with rising pitch for the AGE counter; clock ticks every 5 minutes for the MINUTES counter; dark two-note drone under the dying muscle.
- Hit hierarchy: crack at 9.3 s is the biggest (reverse swell, short vacuum, brittle micro-fracture cascade, pitch-drop body, sub, debris hiss, bell); frame-0 heartbeat hit; seal thud at 13.0 s; low gong on the twist; soft bell on the end line; a rising tone into frame 0 for the loop.
- Mastered with two-pass loudnorm: -15.1 LUFS integrated, true peak -0.5 dBTP measured after AAC. Video: 9 Mb/s two-pass H.264, 27.8 MB.

## Facts and sources
| On screen / in copy | Fact | Source |
|---|---|---|
| Copy: "Every 40 seconds, someone in the US has a heart attack" | "In the United States, someone has a heart attack every 40 seconds." About 805,000 per year (605,000 first, 200,000 repeat). | CDC, Heart Disease Facts: https://www.cdc.gov/heart-disease/data-research/facts-stats/ (checked 21 Oct 2026) |
| PLAQUE BUILDS FOR DECADES / FAT + CHOLESTEROL INSIDE THE WALL | Atherosclerotic plaque (lipid-rich core under a fibrous cap, inside the artery wall) develops silently over decades, starting as early as young adulthood. | AHA, "Atherosclerosis" patient pages; standard pathology. The AGE 25->55 counter is illustrative, not a statistic. |
| THE CAP CRACKS / THE BODY TREATS IT AS A WOUND / A CLOT SEALS IT | Most heart attacks (type 1 MI) happen when a plaque's fibrous cap ruptures (or its surface erodes); the exposed core triggers platelets and the clotting cascade (fibrin), and the thrombus blocks the artery. | Falk E, Shah PK, Fuster V. "Coronary plaque disruption." Circulation 1995;92:657-671. Fourth Universal Definition of MI (Thygesen et al., Circulation 2018) for "type 1 MI". |
| THE PLAQUE DIDN'T BLOCK IT. THE CLOT DID. | The plaques that rupture are often not severely narrowing beforehand: in pooled angiography studies most culprit lesions had been under 50-70 % stenosis; the sudden occlusion is the thrombus. The reel shows the plaque at about 45 % narrowing and the clot closing the rest. | Falk, Shah, Fuster 1995 (pooled data from Ambrose 1988, Little 1988 and others). Copy says "often", never "always". |
| MUSCLE STARTS TO DIE / FROM ~20-40 MIN, THEN IT SPREADS | Irreversible injury of heart muscle begins after roughly 20-40 minutes of complete blockage and spreads as a wavefront from the inner wall outward and along the territory over the next hours. | Reimer KA, Jennings RB et al. "The wavefront phenomenon of ischemic cell death." Circulation 1977;56:786-794 (and the 1979 follow-up, Lab Invest). The reel simplifies the inner-to-outer wavefront to a spread along the front wall. |
| TIME IS MUSCLE. / CALL EMERGENCY SERVICES. | Call 911 (or local emergency number) at the first signs; don't drive yourself. Guidelines measure first-medical-contact-to-device time, target 90 minutes or less for primary PCI. | AHA, 2013 ACCF/AHA STEMI guideline "Top things to know": https://professional.heart.org/en/science-news/2013-guideline-for-the-management-of-st-elevation-myocardial-infarction/top-things-to-know ; O'Gara PT et al., Circulation 2013;127:e362-e425. |

Verification notes: the CDC and AHA pages were read on 21 Oct 2026. The journal papers (Falk 1995, Reimer 1977, O'Gara 2013) are cited from the published record; their PubMed/PMC pages were behind a browser check from the build machine, so the page numbers above should be spot-checked before quoting them anywhere outside this file. The on-screen wording is deliberately conservative ("~20-40 MIN", "STARTS TO DIE", no claim about how often).

Rules for any recut: never say a blocked artery "always" comes from a crack (erosion exists, and type 2 MI has other causes); never give medical advice beyond "call emergency services"; keep "illustration, not to scale, time compressed"; this is education, not diagnosis.

## Publish copy

### YouTube Shorts
**Title (pick one):**
1. A heart attack starts with a crack.
2. The plaque didn't block the artery. The clot did.
3. What actually happens inside a heart attack

Recommended: option 1 (matches the hook).

**Description:**
> Every 40 seconds, someone in the US has a heart attack (CDC). This is what happens inside the artery.
>
> Plaque (fat and cholesterol) builds inside the artery wall for decades, often without narrowing it enough to cause symptoms.
> Then its cap cracks. The body treats the crack like a wound: platelets and fibrin build a clot on it, and within minutes the clot can close the artery completely.
> The heart muscle downstream gets no blood. After roughly 20-40 minutes it starts to die, and the damage keeps spreading for hours.
>
> That's why doctors say "time is muscle." Chest pain, pressure, or discomfort that spreads to the arm, jaw or back, shortness of breath, a cold sweat or nausea: call emergency services (911 in the US) right away. Don't drive yourself.
>
> Illustration: not to scale, time compressed. Educational, not medical advice. Visuals are 3D-rendered; all sound is synthesized.
> Sources: CDC Heart Disease Facts; American Heart Association; Falk, Shah & Fuster, Circulation 1995; Reimer & Jennings, Circulation 1977.
>
> Slow Light: stories worth slowing down for.
> #heart #health #science

**Hashtags (first 3 show above the title):** #heart #health #science

**Tags (under 500 characters):**
heart attack, what happens during a heart attack, how a heart attack happens, plaque rupture, blood clot heart, coronary artery, atherosclerosis, myocardial infarction, time is muscle, heart attack symptoms, heart health, cardiology, human body, medical animation, science shorts, health shorts, slow light

**Pinned comment:** Most people think the plaque slowly clogs the artery shut. Usually it's the clot that does it, in minutes. Did you know that? 🫀

### Instagram / Facebook
> A heart attack starts with a crack. 🫀
> Plaque builds in the artery wall for decades. When its cap cracks, a clot seals it, and the artery with it. The muscle downstream starts dying within about 20-40 minutes.
> Time is muscle: chest pain or pressure? Call emergency services right away.
> Illustration, not to scale. Educational, not medical advice. Sources: CDC, American Heart Association.
> #heart #hearthealth #science #humanbody #health #slowlight

### Upload checklist
- Turn on the platform's "altered or synthetic content" label (3D-rendered medical illustration).
- No sound credits needed (all audio synthesized in `mix.py`).
- YouTube may add a health information panel; keep the description sources as written.
