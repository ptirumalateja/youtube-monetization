# Tickle reel: style bible (continuity lock)

Every plate, overlay and graphic in "Why can't you tickle yourself?" must look like one film. This replaces the flat-vector / gold / teal look of silent v1. Source of the look: the owner's storyboard image (24 panels, 25 s). Anything that breaks these rules is a defect, not a taste call.

## Palette (only these)
- Black / near-black `#050302`-`#0e0906`, warm cream `#e8e4d0` (text, highlights, ripple cores), **storyboard red `#d63e30`-`#ff5a44`** as the one signal colour (brain, command, prediction, ripples, radar, graph, chips). Warm amber only as the low-key light beam on stone/skin. **No teal, no gold, no blue.**
- The only exception is natural skin and stone tones inside the plates.

## Light and lens
- One narrow warm key beam from the upper left; red practical glow from the touch point; deep shadows, rim light on edges.
- Shallow depth of field, macro for fingertip/skin shots, fine film grain, slight vignette. Same grade over the whole timeline.

## Hero hand (identity lock)
- One adult right hand, medium-warm skin, short clean nails, dark charcoal cuff, no jewellery, no tattoos. The second ("other") hand: same skin family, different hand (left), same cuff colour, visibly different pose/size so it reads as someone else.
- Generated once; passed as a reference image into every hand plate.

## Environment
- Rough dark stone wall (hook/loop shots), pure black void (brain and macro shots), skin surface for ripples. No other environments.

## Overlay language (code-drawn, same red glow and line weight as plates)
- Radar: concentric rings with thin scan ticks and a lock-on reticle at the touch point. Signal lines: thin red lines with bright travelling pulses and soft bloom. Waveform: red line on black, cream peak marker. Particles: small red/cream embers.
- Typography: Liberation Sans Narrow Bold (placeholder) caps, cream with red keyword chip; brand mark top-left, clock top-right, no baked text in any plate.
- Graph in the bottom third: red line (tickle felt) plus a thin cream line (hand movement). Fixed positions, same as the silent v1 layout.

## Camera
- Slow push-ins and drifts only, one speed family. Whip/shake only on the single reveal.
- The touch point sits at a fixed screen position (lower-centre third) in every shot where it appears.
- **Match cuts:** the end pose of each shot equals the start pose of the next (fingertip screen position and direction).

## Generation rules (Qwen / Wan)
- One prompt prefix for every plate: "Cinematic vertical 9:16 frame, dark moody low-key lighting, warm film grain, red energy accents, photorealistic, shallow depth of field." plus "No text, no labels, no numbers, no boxes, no captions."
- Every hand plate passes the hero hand as a reference; every plate passes the approved look still.
- Wan: 480x848 base, 81 frames, one motion verb per clip, camera drift slow; discard any take with morphing fingers or a colour shift.

## Continuity QA (before delivery)
1. Contact sheet at 2 fps: palette, light direction, skin tone, grain look the same across shots.
2. Script check: per-shot mean colour and red-ratio within tolerance of the look still; fingertip position at every cut matches.
3. No text baked in plates; no teal/gold pixels from overlays.
