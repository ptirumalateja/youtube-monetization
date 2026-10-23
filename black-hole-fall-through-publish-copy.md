# Black hole v4: one continuous fall (Google Flow clips)

12 s, 1080x1920, 24 fps, loops. There are no hard cuts: the camera dives into each black hole until the frame is black and comes out of the next one. Source: `tools/black-hole-flow/` (track.py, comp.py, sound4.py).

## Files
- `black-hole-fall-through_text.mp4`: hook "WHAT'S ON / THE OTHER SIDE?" typed in over the first 2.6 s, with sound
- `black-hole-fall-through_notext.mp4`: no text, with sound
- `black-hole-fall-through_silent.mp4`: text version with no audio
- `black-hole-fall-through_contact_4fps.jpg`

## Structure
| Time | World | Join |
|---|---|---|
| 0.0-2.9 | Blade (frame 0 is already coming out of the dark) | dive at 1.95 s |
| 2.9-5.9 | Galaxy reveal | out of the hole, dive at 5.0 s |
| 5.9-8.8 | Saturn ring | out of the hole, dive at 7.9 s |
| 8.8-12.0 | Vortex with debris | out of the hole, dive at 11.0 s, lands on frame 0 |

## How the continuity works
- **Tracking:** each clip's black hole centre and size is tracked frame by frame (`track.py`).
- **Dives and emerges:** each dive is an accelerating zoom that drifts the hole to frame centre, with radial motion blur sized to the zoom speed and a roll that builds to about 50°. Each emerge mirrors it, so the spin keeps one direction through the join.
- **Constant motion:** between dives there's a gentle constant push and slow roll, so the camera never stops.
- **Dust layer:** a 3D dust and ember field (1,400 particles) streams out of the current hole toward the camera for the whole reel. It has true perspective, three depth-of-field layers and light-speed streaks during dives. It's the same field across every join, which ties the worlds together and gives the parallax.

## Sound
Synthesised (`sound4.py`), nothing to credit. A drone and wind bed, with an accelerating whoosh and pitch riser into each hole that peaks on the black frame, then a sub boom and an airy release as the next world opens. The last dive lands on the frame-0 boom. -16.9 LUFS, -2.4 dBTP after AAC.

## Notes
- The Veo sparkle watermark shows in the bottom-right corner during the plain stretches; I left it in.
- Label as AI/synthetic content on upload.

## Publish copy
- **Title:** What's on the other side of a black hole?
- **Caption:** Fall in, and keep falling. Four black holes, one fall. Where do you think it ends?
- **Tags:** #blackhole #space #universe #wormhole #interstellar #cosmos #shorts
