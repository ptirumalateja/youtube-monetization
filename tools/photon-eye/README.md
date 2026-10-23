# The Photon That Made Your Eye

Slow Light reel: 12.0 s, 1080x1920, 30 fps, no voiceover, loops. Approved storyboard: `STORYBOARD.md` (v2).

## How it's built

All of it is continuous code-generated motion. No still images, and no transitions other than light.

- `gl/shots.glsl`: four GPU fragment shaders, animated by `uT` (local time).
  - Trap: a raymarched tunnel of gold plasma smoke that flows toward camera and is lit by the photon wherever it is.
  - Escape: a boiling photosphere, corona smoke streaming off the limb, a growing plasma jet, and a rim of light racing along the limb.
  - Eye: a golden iris with micro-moving fibres, a pupil that constricts on impact, and a slowly turning Earth reflected in the pupil.
  - Sky: a sunset with drifting cloud layers while the sun sinks.
- `gl/render.mjs`: renders the shader plates in one headless Chromium page (SwiftShader). The trap renders at 720x1280 and is upscaled, because the fog is soft.
- `anim.py`: the timeline and compositor.
  - The photon's random walk is drawn as it happens, with trails, scatter flashes, drifting dust, the year counter and type.
  - The light match-cuts: the dot swells into the Sun, the photon bursts into the escape, the beam flares into the eye, the pupil swallows the frame, the sunset rises out of the black, and the sun sets back into the frame-0 dot.
- `sound.py`: synth layers plus CC0 Freesound files from `tools/sfxlib`. A tick lands on every scatter (cue times come from `events.json`), then the explosion, 0.4 s of hard silence, the jet roar, the pupil click, and the biggest hit at 10.0 s.
- `build.sh OUTDIR`: runs everything and encodes. It is resumable: existing plates and frames are skipped.
- `hero.py`, `compose.py`, `stills.py`: storyboard stills only (v2 hero frames, v1 sketches).

## Timeline

| Time (s) | Shot | Text |
|---|---|---|
| 0.0-1.5 | The dot breathes in black; at 1.2 s it swells into a gold flash | `THIS LIGHT WAS MADE` / `100,000 YEARS AGO` |
| 1.5-6.0 | The camera rushes back out of the dot into the plasma tunnel. The photon's arcs draw themselves; at 4.3 s the camera rolls 15° | `YEAR 1 → 100,000` (counts up only) |
| 6.0-8.0 | The photon breaks out in slow motion: the jet erupts, the rim races and ejecta fly | `THEN IT ESCAPED.` |
| 8.0-10.0 | The beam lands in the pupil, the pupil tightens, Earth turns in the reflection; at 9.55 s the pupil swallows the frame | `AND ENDED IN YOUR EYE.` |
| 10.0-12.0 | The sunset rises out of the black: stargazer, moving clouds, swaying grass. At 11.45 s it sets back into the frame-0 dot | `THE LIGHT YOU SEE WITH` / `IS OLDER THAN CIVILIZATION.` |

Music drop for the silent copy: **10.0 s**. Secondary accents: 1.5 s and 6.0 s.

Text is kept inside a 900 px safe width, at least 90 px from each edge.
