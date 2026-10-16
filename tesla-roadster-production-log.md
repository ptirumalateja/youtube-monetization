# Tesla Roadster — complete production log

Date: 16 October 2026 (IST).
Channel: Slow Light — “Stories worth slowing down for.”
Final delivered export: **Tesla_27s_Final.mp4**, 27 seconds, 1080×1920, 30 fps, H.264/AAC.
Status: delivered for owner review. No social publishing or scheduling was performed by the assistant; owner posting status is unconfirmed.

Related platform copy: [tesla-roadster-publish-copy.md](tesla-roadster-publish-copy.md).

## 1. Purpose and creative direction

A timely engineering explainer built around the Roadster demonstration: show the real stunt, explain the distinct roles of suction and thrust, then complete the second stunt at the end.

This extends Slow Light’s narrated explainer approach to current science/technology news. It is not a commitment to a daily general-news roundup. Earlier discussion proposed a small pilot series of individually explained science, engineering, space or technology stories.

The owner reported approximately 40% swiping away at 2–3 seconds, another drop in the middle, and about 30% reaching the end on previous videos. These are owner-reported figures, not retrieved analytics. Stayed-to-watch and audience-retention metrics must not be combined without seeing their actual definitions and charts.

Design response:
- Start close to the remarkable action, not the approach.
- Put a specific visual promise on screen immediately.
- Make the explanation introduce a second discovery: ramp contact and airborne control involve different mechanisms.
- Give the ending a payoff: complete the second stunt teased in the opening.
- Preserve the full landscape composition, since the ramp and flight path matter.
- Keep text well away from mobile app header, footer and right-side controls.

## 2. Reference reviewed

The repository’s latest branch at the start of review was feature/fervent-wright-la6ixo, commit 865c8192fd30f7c513f472b6806aff9d33a1f1ee (15 October 2026). Main was older.

Read: claude.md, slow-light-design-playbook.md, Tickle frozen spec and older style bible, Night Sky spec, Scale Ladder spec, Dreams publishing notes, and representative scene/render/audio code.

The owner supplied whyDreamsFeelReal_master.mp4 (30 seconds, 1080×1920). Sampled frames showed the heading very high and captions low; the owner reported both were obscured by mobile interface overlays. The Tesla edit uses inward text placement.

Important scope distinction:
- Format A: wordless cinematic light/scale reels.
- Format B: narrated visual explainers; final Tickle contour-line direction supersedes its earlier red photoreal and flat-vector experiments.
- Abhimanyu remains a separate narrated cinematic story.
- Frozen approved reels are not to be redesigned as part of this work.

## 3. Supplied footage and filename correction

| File | Actual duration | Resolution | Content |
|---|---:|---|---|
| Roadster Event (1).mov | 21.418467 s | 1920×1080 | Curved ramp, inverted section, release, descent |
| Roadster Event.mov | 6.623133 s | 1920×1080 | Second stunt over parked vehicles, airborne rotation and landing |

The owner initially described the filenames the other way around. Measured durations and contact sheets established the correct mapping.

The initial proposed n−10 to n−3 trim of the longer clip would have ended before the landing. The cut was moved to approximately source 16 seconds to place the car upside down immediately and show release within the opening.

Earlier Instagram reference: a 23-second 720×1280 repost with a small landscape picture and large empty areas. It was used for discussion, not as the final source.

## 4. Final locked sequence: 27 seconds

| Timeline | Material | Source interval / purpose |
|---|---|---|
| 0–5.4 s | Roadster Event (1).mov | 16.0–21.4 s: inverted car, release and descent |
| 5.4–7 s | Roadster Event.mov | 1.0–2.6 s: tease of the second stunt |
| 7–14.8 s | Authored schematic | Suction near the ramp; captions follow Fraser |
| 14.8–23 s | Authored schematic | Cold-gas thrust, opposite reaction force, rotation/descent |
| 23–27 s | Roadster Event.mov | 2.6–6.6 s: resume the second stunt through its landing |

The owner explicitly requested restoring this final four-second segment after the shorter 25-second version: the opening had interrupted the second stunt, and the ending makes it whole.

Final ending:
- Top heading: THE ROADSTER / DEMONSTRATION.
- Small line: NOW WATCH THE ROTATION AND LANDING.
- Bottom caption: DEMONSTRATED: OCTOBER 2026 / PRODUCTION TARGET: 2028.
- Full 16:9 footage remains centered and uncropped.
- Original event audio returns quietly beneath the last spoken words and rises into the landing.
- No regenerated narration was required.

## 5. Approved narration — exact text

> Two tricks.
> On the ramp, fans remove air beneath the car. Lower pressure lets outside air push it against the surface.
> Once airborne, cold-gas thrusters take over.
> Gas shoots one way. The car is pushed the other—controlling its rotation and slowing its fall.

Do not regenerate or rewrite without owner instruction.

Voice:
- Provider route: ElevenLabs through Higgsfield.
- Preset: Fraser, explicitly selected by the owner to match the previous reel.
- Voice ID: 6705e465-7b52-5915-a1d8-b1222885e01d; voice_type preset.
- Model: text2speech_v2, variant elevenlabs.
- One generation submitted after script approval.
- Preflight quote: 0.9 credits.
- Job ID: 879c75be-84bb-43de-bbe6-bad1f192a95d.
- Raw file: Fraser_Tesla_Original.mp3.
- Raw duration: 16.509388 seconds.
- Starts at reel second 7. No pitch or speed adjustment.

Measured raw-take pauses informed caption timing. Phrase boundaries are approximate manual alignment from the known script and silence detection, not a word-level transcription.

## 6. Audio decisions

- Opening stunt keeps original event sound, including its natural spectacle; no additional opening SFX.
- Explanation uses Fraser plus quiet locally synthesised mechanical tones and restrained transition accents.
- SFX created locally with numpy; no Higgsfield SFX, stock music or new Freesound samples.
- Final stunt uses its original event audio, ducked under the remaining narration.
- Final 27-second encoded export measured approximately **−15.8 LUFS integrated, −1.9 dBTP**.
- Only one paid voice generation; no paid image or video generations.

Retaining event audio also retains any rights issues in that audio. Original event music is not automatically cleared by adding narration or credits.

## 7. Layout and graphics

- Deliverable canvas: 1080×1920, 9:16.
- Source footage: full 1920×1080 composition scaled to 1080×approximately 608, centered vertically.
- Design/render base: 720×1280, upscaled to 1080×1920 with Lanczos.
- Approximate final video bounds: y 656–1264.
- Heading below top app controls; narration captions around y 1356–1460; footer kept clear of essential text.
- Conservative text placement is a working layout, not a guarantee across every device/app; check in the actual mobile player.
- Near-black/navy background, cream lettering, teal schematic marks, red reaction-force arrows.
- Car is a purpose-built schematic side profile, not an AI-generated photograph or representation of Tesla’s precise hardware.
- Principle diagrams labelled SIMPLIFIED PRINCIPLE · NOT TESLA INTERNAL LAYOUT.
- Fans lower pressure near a surface; outside pressure pushes the car toward that surface.
- Thrust arrows illustrate gas momentum and the opposite reaction. No exact nozzle arrangement, pressure values or proprietary control logic is claimed.

## 8. Iteration record and delivered files

1. Slow_Light_Tesla_First_Cut.mp4 — 30-second visual preview; original audio and local effects, no voiceover.
2. Tesla_Storyboard.jpg — corresponding six-frame preview.
3. Slow_Light_Tesla_25s_Fraser.mp4 — initial voiced 25-second assembly.
4. Tesla_25s_Final.mp4 — 25-second voiced delivery; measured approximately −15.4 LUFS / −2.0 dBTP.
5. Tesla_25s_Storyboard.jpg — voiced version frame sheet.
6. **Tesla_27s_Final.mp4 — current final delivery**, including second-stunt completion at 23–27 seconds.
7. Tesla_Edit_Source.zip — delivered source scripts, original Fraser take and README; updated with ending27.py.

Videos and source ZIP were delivered as downloadable files. They have not been committed as binary assets in this repository.

Local script names in the source bundle:
- build.py: shared artwork, layouts, footage decoding, original preview.
- build25.py: captions, 25-second assembly and mix.
- ending27.py: final stunt continuation and 27-second assembly.
- README_Tesla.txt: initial rebuild notes.
- Fraser_Tesla_Original.mp3: approved single take.

Rebuild order: place the two MOV files in an upload directory beside the working source directory; run build25.py, then reproduce the 25-second +2 dB audio finishing step documented below, then ending27.py. Requires Python Pillow/numpy, ffmpeg and the specified system DejaVu font paths.

The source bundle uses intermediate filenames from this session. It is a session reproducibility bundle, not yet a portable one-command project.

25-second finishing command:
```sh
ffmpeg -i Slow_Light_Tesla_25s_Fraser.mp4 -c:v copy -af volume=2dB -c:a aac -b:a 192k -movflags +faststart Tesla_25s_Final.mp4
```

Source code, readme and voice file are inside the delivered ZIP; only production documentation is committed here.

## 9. Publishing copy

Complete platform-specific captions, credits and alternative title are in tesla-roadster-publish-copy.md.

### YouTube
Title: **How Tesla’s Roadster Drives Upside Down—Then Flies**

Caption:
A car upside down on a ramp. Then airborne. How?

Two mechanisms do different jobs: fans reduce air pressure beneath the car near the ramp, while cold-gas thrusters help control its airborne rotation and descent.

The engineering explained in 27 seconds.

Demonstrated: October 2026. Production targeted for 2028.
Graphics are simplified illustrations.

Footage: Tesla Roadster event broadcast. Original explanation, graphics, editing and additional sound design: Slow Light. Independent commentary; not affiliated with Tesla or SpaceX.

Recommended focused hashtags:
#TeslaRoadster #Tesla #FlyingCar #SpaceX #EngineeringExplained #Shorts

Tags:
Tesla Roadster, Tesla Roadster explained, Tesla flying car, Tesla upside down car, cold gas thrusters, suction downforce, fan car, SpaceX thrusters, how thrusters work, engineering explained, physics explained, science shorts, Slow Light

### Instagram
Cover: **UPSIDE DOWN. THEN AIRBORNE.**

Caption:
Two tricks. One extraordinary demonstration.

Fans reduce air pressure beneath the Roadster near the ramp. Once airborne, cold-gas thrusters help control its rotation and descent.

Watch the ending again—now you know what to look for.

Demonstrated: October 2026. Production target: 2028.
Simplified illustrations.

Footage: Tesla Roadster event broadcast. Explanation, graphics, edit and additional sound design: Slow Light. Independent commentary; not affiliated with Tesla or SpaceX.

### Facebook
Title: **Tesla’s Roadster Went Upside Down. Here’s How.**

Caption:
How does a car stay upside down on a ramp—and then control its fall?

Fan-generated suction near the ramp. Cold-gas thrusters in the air. Two mechanisms, explained in 27 seconds.

Which surprised you more: staying upside down, or the landing?

Demonstrated: October 2026. Production targeted for 2028.
Simplified illustrations.

Footage: Tesla Roadster event broadcast. Explanation, graphics, edit and additional sound design: Slow Light. Independent commentary; not affiliated with Tesla or SpaceX.

Facebook topic keywords, if a field is offered:
Tesla Roadster, Engineering, Physics, Electric vehicles, SpaceX, Automotive technology, Science explained

Do not treat topic keywords as people/Page mentions or paste a keyword dump if no separate field exists.

### Expanded relevant hashtag pool
#TeslaRoadster #Tesla #SpaceX #FlyingCar #Roadster #TeslaNews #ElectricVehicles #EVTechnology #AutomotiveEngineering #EngineeringExplained #PhysicsExplained #ColdGasThrusters #FutureOfMobility #TechNews #SlowLight

Suggested Instagram/Facebook selection:
#TeslaRoadster #Tesla #SpaceX #FlyingCar #TeslaNews #EngineeringExplained #PhysicsExplained #SlowLight

Use a relevant subset within the current app’s allowed hashtag limit; avoid generic trending tags unrelated to the content. Hashtags are descriptive metadata, not a guaranteed reach mechanism.

Suggested first caption phrase if revising for search clarity:
“Tesla Roadster flying demonstration: two mechanisms explain the stunt.”

Pinned comment:
“Which surprised you more: staying upside down, or controlling the landing?”

## 10. Timing recommendation

At approximately 12:50 PM IST on 16 October, advice was to publish promptly on all three platforms rather than wait for evening, because the story was receiving fresh same-day coverage.

This was an editorial freshness judgment, not an analytics-derived optimal posting time. No universal best minute was claimed.
- YouTube: upload, allow processing/copyright checks, then publish when ready.
- Instagram and Facebook: post in the same session.
- Evening: optionally share the Reel to Stories and respond to comments.
- No automated schedule was created.
- Do not delete and repost solely because the first hour is slow.
- YouTube says upload time is not known to determine long-term video performance; account-specific audience activity can help early viewership.

## 11. Copyright, credits and unresolved rights

Existing video source credit: SOURCE FOOTAGE: TESLA ROADSTER EVENT.

Longer description attribution:
“Footage source: Tesla Roadster event broadcast. Underlying event footage and event audio belong to their respective rights holders. Original explanation, illustrative graphics, editing and additional sound design by Slow Light. Independent commentary; not affiliated with or endorsed by Tesla or SpaceX.”

No separate “no infringement intended” end card was added. Attribution does not grant permission or prevent Content ID/Meta claims. A short duration, education label, editing, or commentary does not automatically establish fair use/fair dealing.

Permission/licence for the event footage and original event audio has **not been established** in this session. Commercial-use entitlement for the generated voice was not independently verified. No claim-free or monetisation guarantee was given.

The owner should establish the applicable permission/licence or legal basis before publishing. A clean platform copyright check is not permission and does not prevent later claims.

## 12. Sources consulted

Reporting:
- https://www.reuters.com/business/autos-transportation/tesla-set-unveil-next-generation-roadster-sports-ev-after-years-delay-2026-10-15/
- https://www.theverge.com/transportation/1012552/tesla-roadster-next-gen-reveal-elon-musk
- https://indianexpress.com/article/technology/tesla-roadster-spacex-thrusters-video-10924129/

Manufacturer:
- https://www.tesla.com/roadster
The manufacturer page exposed limited text through the retrieval tool; full internal engineering details were not verified from that page. Detailed diagram geometry is intentionally illustrative.

Original event links found through published viewing guides (players could not be loaded directly during retrieval):
- https://www.youtube.com/watch?v=qt5p-_tE8d0
- https://x.com/i/broadcasts/1yKAPwNggRaxb

Official platform guidance:
- https://support.google.com/youtube/answer/9783148
- https://www.facebook.com/help/354736791367645/
- https://support.google.com/youtube/answer/16533387

## 13. Next checks

- Owner review on mobile: text visibility, car readability, ending satisfaction.
- Confirm source footage/audio reuse basis.
- Confirm current manufacturer targets before a later repost.
- Record actual publishing URLs/status when owner supplies them.
- Measure opening retention, explanation-transition drop, end retention and rewatches. Keep metrics distinct.
- Preserve the approved Fraser take; no extra generation or frozen-reel changes without instruction.
