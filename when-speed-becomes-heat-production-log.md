# When Speed Becomes Heat — production record

Recorded: 16 October 2026. Channel: Slow Light.
Companion copy: [when-speed-becomes-heat-publish-copy.md](when-speed-becomes-heat-publish-copy.md).

## Current delivery and status

Latest export: `When-Speed-Becomes-Heat-35s-Voice-and-SFX.mp4`.
35.00 seconds; vertical 1080×1920; 30 fps; 1,050 frames; H.264 video and AAC stereo audio at 48 kHz. Procedural picture was rendered at 720×1280 and upscaled for delivery.

The 35-second edit, original effects and approved Fraser narration have been assembled. The owner approved the narration script and its generation cost. This records delivery, not final approval of the narrated export or a claim that the aircraft-realism concern is solved. Publishing copy is prepared; nothing has been posted or scheduled.

## Concept and scientific progression

Core idea: speed creates a thermal engineering problem.
The film moves from Concorde at about Mach 2, to the SR-71 at Mach 3, to the X-15 and the X-15A-2 Mach 6.7 record configuration. It explains skin expansion, material choice and thermal protection rather than merely ranking aircraft speeds.

The initial 45-second target was shortened to 35 seconds at the owner's request. The earlier 45-second exports remain as history, not the current publishing master.

## Design decisions and iteration history

1. Motion first: the owner wanted an aircraft coming toward the viewer, with visible air displacement and a fast reveal. An early front-to-side camera shift felt like separate images and broke continuity. It was replaced with a continuous frontal approach, multi-depth world-space particles and stronger attached teal/gold flow cues.
2. Speed: successive faster previews established the accepted rough opening. The approved rough approach was approximately 3.37 seconds; the final 35-second opening occupies 2.9 seconds.
3. Slow Light treatment: dense contour/wire lines made the distant aircraft resemble a bird and looked ribbed at close range. Solid shaded surfaces, sparse engraving, a smooth nose and cockpit, and selective teal accents replaced the dense cage.
4. Colour: the owner preferred the original cream/gold treatment over the graphite experiment. The warm aircraft against dark navy became the retained direction.
5. Expansion diagram: the first raised rectangular sample intersected the wing/airflow. An isolated-sample revision and a recessed cutaway/panel-lift version were tried.
6. Final expansion choice: retain intact aircraft skin, show a faint fixed outline of original dimensions, then let the highlighted heated region extend beyond it. No skin removal, explosion, scattered parts or literal thermal bulge in the retained version.
7. Pacing: the owner liked aircraft appearing side by side, but the Mach 2-to-Mach 3 transition stalled. The Blackbird was made to advance relative to Concorde and the transition was tightened. The Concorde explanation was shortened before adding X-15 and the full ending.
8. 35-second revision: closer/lower hero framing, stronger warm shadows and finer curved geometry sought a larger, more intimidating aircraft presence. These changes improved presentation but retained simplified models.
9. Premium realism references: the owner supplied cinematic rear/three-quarter, frontal and skin-detail imagery. These establish a future target for material texture, panel detail, atmosphere and aircraft mass. They are not part of the current rendered master.
10. Priority change: the owner deferred further visual work and asked to finish SFX and voiceover on the existing 35-second version first. That audio finish is the current delivery.

## Retained visual language

Deep navy backgrounds, warm cream/gold solid aircraft, sparse teal contours/flow and restrained typography. Red is limited to markers. Aircraft and camera movement must carry depth and continuity; scene changes must be readable. Airflow accents suggest speed without claiming literal tears in air.

The skin highlight follows the surface curvature. Its boundary grows beyond a fixed dashed footprint. Growth is exaggerated for understanding; the earlier illustrative region used 10% width and 17% length growth, not measured Concorde strain.

## Final picture timeline

| Seconds | Picture / explanation |
|---|---|
| 0–2.9 | Fast frontal Concorde opening |
| 2.9–7.6 | Concorde heating and intact-skin expansion |
| 7.6–15.4 | Blackbird transition, titanium and simplified sliding-attachment explanation |
| 15.4–19.6 | X-15 transition and hero reveal |
| 19.6–21.9 | Inconel X material explanation |
| 21.9–24.9 | Ablative coating and white sealant |
| 24.9–28.1 | Protected X-15A-2 record configuration |
| 28.1–30.9 | Three-aircraft comparison |
| 30.9–33 | Heat-engineering thesis |
| 33–35 | Return toward opening composition |

## Approved narration — verbatim

Speed has a hidden enemy. Heat.

At Mach two, Concorde's skin heats up and expands.

At Mach three, the Blackbird used titanium, with attachments that allowed its skin to expand.

The X fifteen pushed further, using heat-resistant Inconel X.

Its record-setting version added an ablative coating and white sealant.

Three aircraft. Different solutions. Because flying faster means engineering for the heat.

## Voice generation and placement

Voice: Fraser preset, ID `6705e465-7b52-5915-a1d8-b1222885e01d`.
Engine: ElevenLabs through Higgsfield, `text2speech_v2`, variant `elevenlabs`.
Cost preflight: 1.35 exact credits, approved by owner before submission.
One take submitted; no paid retries.
Job: `06455113-4b68-452c-b07a-4cf3ea13fabd`.
Decoded take: 25.68 seconds. Speech speed and pitch were not changed.

Paragraph boundaries were selected inside measured natural pauses. This is paragraph alignment, not a word-level forced-alignment claim.

| Phrase | Raw take region (s) | Placement in film (s) |
|---|---|---|
| Hook | 0–2.55 | 0.25 |
| Concorde | 2.78–6.00 | 3.00 |
| Blackbird | 6.13–11.60 | 8.00 |
| X-15 material | 11.78–15.82 | 16.00 |
| Coating | 15.88–19.65 | 22.00 |
| Closing thesis | 20.05–25.68 | 28.30 |

## Sound finish and measured checks

Original locally synthesised effects were retained and ducked beneath speech, recovering between phrases. No Higgsfield SFX generation and no new music in this pass. Tiny fades protect paragraph joins.

The base was `When-Speed-Becomes-Heat-35s-Cinematic.mp4`; the narration export copies its video stream unchanged. The encoded final was decoded through all 1,050 frames and measured at 35.00 seconds. Encoded audio: -15.8 LUFS integrated, 2.7 LU loudness range and -1.8 dB true peak. These are automated measurements; they do not substitute for owner listening approval.

## Local working files and rebuild map

Workspace root:
`C:/Users/admin/.codex/.chatgpt-projects/g-p-6ad1bd6659c48191846879f4082364cd/heat-motion/`

- `prepare_heavy_modules.py`: prepares the closer-camera/material scene modules.
- `build_full_35s.py`: renders the 35-second picture.
- `finish_full_35s.py`: retimes and assembles the existing effects.
- `voiceover/narration-script.txt` and `voiceover/voice.lock`: approved script and persistent voice pair.
- `voiceover/Fraser-Approved-Raw.mp3`: untouched generated take.
- `voiceover/Existing-SFX-35s.wav`: extracted base effects.
- `voiceover/Fraser-Aligned-35s.wav`: placed speech.
- `voiceover/Voice-and-SFX-35s.wav`: finished audio.
- `voiceover/finish_audio.py`: paragraph placement, ducking, normalisation, mux and encoded checks.
- `voiceover/generation-ledger.json`, `normalization-log.txt`, `encoded-audio-check.txt`: audit records.
- `35-second-delivery-notes.md`, `45-second-delivery-notes.md`, `README.md`: earlier local production notes.

This Git entry preserves the production record. It does not upload these scripts, raw audio, images or rendered videos; those remain local. Synced `sources/` references were not modified.

## Scientific boundaries and references

The models, relative positions and size comparison are schematic. Flow colours are artistic explanation, not CFD or measured temperatures. The skin diagram exaggerates expansion and does not show buckling or skin failure. The attachment diagram is not an exact internal engineering drawing. Mach 6.7 denotes the X-15A-2 record, not routine cruise; protective coating and white sealant are included rather than attributing the record entirely to bare Inconel.

- NASA X-15 programme: https://www.nasa.gov/reference/x-15/
- NASA X-15 aircraft history: https://www.nasa.gov/aeronautics/x-15/
- NASA coating image: https://www.nasa.gov/image-article/x-15a-2-with-full-scale-ablative-coating/
- NASA Blackbird engineering history: https://ntrs.nasa.gov/api/citations/20090007797/downloads/20090007797.pdf
- NASA SR-71 material/Mach 3 context: https://www.nasa.gov/image-article/sr-71-takeoff-with-afterburner/

Instagram footage/audio and the owner's Meta stills are references only, not incorporated assets. Effects in this cut are original synthesis. Narration is generated with the licensed provider preset; no owner voice clone was used.

## Deferred work / next visual pass

The owner and external critiques identified the remaining weakness: smooth simplified aircraft lack the surface detail, scale and weight of real machines. Preserve the current structure and accepted motion while upgrading the opening, SR-71 hero and final comparison with more convincing geometry/materials or controlled footage.

The macro reference is useful for material richness; its dents/pitting must not be presented as ordinary thermal expansion. Multi-angle stills alone do not produce continuous 3D motion or accurate camera parallax.

A four-second premium image-to-video test was quoted at 28 credits but was not approved or submitted. No RunPod pod was started for that deferred test. Any new paid visual generation requires a fresh concrete cost approval under the project rules.
