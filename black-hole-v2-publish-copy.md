# Black hole v2 (10 s, in the style of the nebula.galaxies refs)

Two 5 s shots joined by a hard cut, like both refs. 1080x1920, 30 fps. The cut also makes it loop. Source: `tools/black-hole-v2/` (bh2.c, post2.py, sound2.py, assemble2.py) on branch `claude/project-thread-r728nz`.

## Files
- `black-hole-v2_text.mp4`: hook "NOTHING ESCAPES THIS." typed in by 0.8 s and gone by 3.2 s, with sound
- `black-hole-v2_notext.mp4`: no text, with sound
- `black-hole-v2_silent.mp4`: text version with no audio
- `black-hole-v2_contact_2fps.jpg`

## Shots
1. 0-5 s: near edge-on. The disk is a diagonal blade, and the lensed halo (the far side of the disk bent over and under the hole) frames the shadow. Slow push-in.
2. 5-10 s, hard cut: a tilted ring view with the hole in the upper third and hair-fine strands filling the lower frame. Slow push-in and drift.

## What changed from v1
The disk is now a razor-thin surface with hair-fine concentric strands, not soft volumetric gas. The sky is near black with grey smoky wisps. The palette is cream-white with amber threads. The hole is bigger in frame, the clip is shorter, and it cuts between shots instead of making one long move. Light bending is still physically traced (Schwarzschild).

## Known gaps vs the refs
- The refs are AI-painted (Midjourney-style still plus image-to-video), so they have painterly smoke, debris chunks and dust clouds that this procedural render doesn't. A RunPod Qwen/Wan pass over these frames is the way to close that gap.
- In shot 1 the hole sits a little high, leaving the lower half darker than the ref.

## Sound
Synthesised (`sound2.py`), nothing to credit. Drone, wind and glass, with a sub swell on frame 0 and on the cut. -15.9 LUFS, -2.4 dBTP after AAC.

## Publish copy
- **Title:** Is this what a black hole really looks like?
- **Caption:** Every ray of light here is bent by the black hole's gravity: the glowing ring over the top is the far side of the disk, pulled around the hole toward you. Nothing escapes this.
- **Tags:** #blackhole #space #universe #astrophysics #interstellar #science #shorts
- Label as AI/synthetic content (computer-generated visualisation).
