# Mosquito reel: Google Flow clip list and prompts (A-F)

Decisions (18 Oct 2026): photoreal Flow plates plus a designed data layer. No ChatGPT three.js (it cannot run our render/overlay/mix chain; designed beats are built locally). Six Flow generations (A-F), 2 variants each, 9:16, maximum length. Timeline 31 s x 30 fps = 930 frames; Flow is 24 fps and is conformed to 30 fps. Use Flow "Frames to Video" so clip E starts on clip B's last frame. Never use a clip with baked text; a leftover sparkle is removed with `delogo=x=852:y=1692:w=96:h=96`. Spec: `mosquito-reel-spec.md`.

## Timeline and transitions (final)
| Time | Beat | Source | Transition out |
|---|---|---|---|
| 0-1.2 | Swarm toward camera, NIGHT 1 | Flow A | in-clip: bass hit, whole swarm bursts to dust |
| 1.2-2.0 | Vanish, silence | Flow A | smash cut on silence (pattern interrupt at 2.0 s) |
| 2.0-3.5 | Earth + one pulse (my overlay) | Flow B 0-1.5 s | continuous push-in, no cut |
| 3.5-7.5 | WEEK 1: plunge through cloud to calm tundra, herd grazing | Flow B 1.5-5.5 s | camera drops to ground level, grass rack-focuses to the orchid |
| 7.5-10.5 | MONTH 1: orchid, mosquito dissolves, flower left alone | Flow C | cut on light match (same dusk teal) |
| 10.5-12.5 | Cacao pod, midge on flower, "SAFE" chip | Flow D | hard cut to black |
| 12.5-13.3 | Held breath (near silence) | black | Earth fades up from black |
| 13.3-19.5 | YEAR 1: photoreal Earth (B frame, Africa-centred) dissolves in 6 frames into my designed lattice data globe; red markers wink out; 610,000 number, hero hit | designed (mine) | pull away from Africa, plunge back through cloud (same motion as B) |
| 19.5-26 | YEAR 10: same tundra, new small insects in the air | Flow E (start frame = B's last frame) | rack focus from the air insects to one mosquito |
| 26-29.5 | End line; single mosquito hovers, wings start to buzz | Flow F | mosquito bursts to dust |
| 29.5-31 | Dust re-forms into the swarm = frame 0 (loop) | Flow A played in reverse | hard cut to frame 0 |

## Flow prompts (paste each; generate 2 variants)
Prefix for every prompt: "Photorealistic cinematic footage, 35 mm lens, natural muted colour, deep navy and teal night tones with faint warm highlights, subtle film grain, vertical 9:16. No text, no captions, no subtitles, no logos, no watermark, no UI, no graphics, no overlays, no glowing lines or wireframes, no music, no speech."

**A. Hook swarm + vanish (8 s):** "A dense swarm of hundreds of Aedes mosquitoes flies straight toward the camera through warm humid dusk air, backlit by a faint teal glow, extreme shallow depth of field, fine legs and beating wings visible, slight handheld shake. At about 1.5 seconds every mosquito disintegrates at the same instant into fine glowing dust that scatters outward in one burst, leaving completely empty dark air with a few drifting motes. Locked camera, one continuous shot." Fallback A2: swarm only, no vanish (I do the burst in post).

**B. Earth to tundra (8-10 s):** "Earth from space, centred on Africa and Europe, thin atmosphere glow, black star field, slow smooth push-in. The camera dives through layers of white cloud, descends over the Arctic and settles low over a calm summer tundra at dusk with shallow pools and cotton grass, about thirty caribou grazing peacefully across the plain. The air is clear and still; no insects anywhere. One continuous smooth shot." Save B's final frame as E's start frame.

**C. Orchid (5 s):** "Extreme macro of a small wild bog orchid, blunt-leaf orchid Platanthera obtusata: a slender spike of tiny pale green-white flowers with one blunt basal leaf, in a damp northern bog at dusk, soft navy-teal background. A single mosquito hovers in front of the flowers, then dissolves into fine pale dust that drifts away, leaving the orchid alone and still. Shallow depth of field, locked camera."

**D. Cacao (4 s):** "Macro of a cacao tree trunk with a cluster of tiny pink-white cacao flowers growing directly from the bark and one ripe yellow-orange cacao pod beside them. A tiny dark midge, not a mosquito, lands on a flower. Soft warm light against a dark green-navy background, shallow depth of field, slow push-in."

**E. Year 10 tundra (8 s, Frames to Video, start frame = B's last frame):** "The same tundra plain ten years later at dusk, caribou still grazing, and the air now holds a thin drifting haze of tiny non-biting flies and midges rising from the pools. Camera drifts slowly forward. No mosquitoes, no text, no overlays."

**F. Hovering mosquito (6 s):** "A single mosquito hovers facing the camera against a dark navy background, wings beating in a blur, fine legs hanging, slight breathing push-in of the camera, shallow depth of field. Photorealistic, no text." (needs 2.5+ s clean.)
