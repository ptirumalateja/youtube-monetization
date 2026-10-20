# The Shadow That Stops Copying (16 s, no voiceover): spec

Reel #2 in the psychological series, after `ball-never-falls-reel.md`. Source idea: the inner critic / being watched by yourself. Built in three.js (`tools/shadow-stickman/`), sound synthesised in numpy (no samples, no credits). First episode of a recurring **stickman** character so later reels (bystander, conformity, marshmallow) reuse the rig.

## Idea
A stickman stands in front of a wall under one lamp. His shadow copies every move. Then it is a beat late. Then it does something he didn't. At the reveal it stops being a shadow: it turns to look at the camera while he doesn't. In the last seconds it snaps back into sync and the loop restarts. Closing line: WHO IS FOLLOWING WHO?

## Why this one
Light and shadow are the channel's brand; one character, one lamp, no props; works on mute; the late-shadow moment is a perception hook (viewers rewind to check), and the final line invites comments.

## Look
Charcoal/navy void, one warm key lamp low and in front (a visible bulb at the edge of frame), a pale cream wall with soft falloff, the stickman drawn as thick cream-white round-capped tubes (head ring, torso, 4 limbs) so he reads at phone size, the shadow a soft-edged black silhouette on the wall that is about 1.6x his size (lamp close). Teal rim light only on the floor edge; red only on the label chip. Heartbeat pulse drives vignette and lamp flicker exactly as in the ball reel.

## How the shadow works (honest mechanics)
The shadow is not a shadow-map. It is the same skeleton, projected onto the wall plane from the lamp position with a planar projection matrix and drawn as flat black, soft-blurred in post. Its pose comes from its own clock: `poseShadow(t) = pose(t - lag(t))` plus an override channel for the scripted disobedience (turns head, sits, walks off). While `lag = 0` and no override it is a true cast shadow, so the first seconds are physically correct and the deviation reads as a violation, not a glitch.

## Timeline (16 s, v2: restructured after review)
| Time | Beat | Shadow |
|---|---|---|
| 0.0 | Hit on frame 0; man already walking in; hook types: YOUR SHADOW ALWAYS COPIES YOU. | exact copy |
| 2.0-4.4 | He stops, raises an arm (3.4-4.3), tilts his head | exact copy |
| 4.5-6.6 | **First disobedience:** he lowers his arm, the shadow keeps its raised arm for 2 s (dissonant sting), then lowers it | holds the pose |
| 6.2-9.0 | It leans slowly toward the viewer and its head turns from profile (nose bump shrinks away); lamp stutters 8.0-9.0, held-breath silence 8.2-9.0 | own |
| 9.0-9.12 | Reveal hit, lamp out for 3 frames; he startles and freezes, trembling, arms up | calm, upright |
| 9.12-12 | Two eyes light on the shadow's head; camera pushes toward the eyes with a small shake; ambience stays cut until 10.4, heartbeat returns fast; caption IT IS LOOKING AT YOU. | own |
| 12.0-12.9 | The shadow takes one deliberate step toward the lamp/viewer (its own depth grows, so it grows), thud | own |
| 13.0-15.8 | It keeps approaching and looms over the frame, eyes in the upper part; WHO'S FOLLOWING WHO? types at 12.9; heartbeat 118 -> 128 bpm, rising sub swell | own |
| 15.8 | Lamp blackout and sound cut = the loop point; frame 0 hits lit again | - |

There is no stopwatch or chip any more (it read as a tech demo). Only the small SLOW LIGHT tag, hook, one reveal caption and the end line remain.

Animation: foot angles (toe-up on swing), elbow flex tied to arm swing, small torso-lean oscillation per step, hip bob from foot grounding.

## Sound (procedural, same family as the ball reel)
Heartbeat from the scene's bpm curve; low drone; footsteps on the walk-in; dissonant sting at the first disobedience (4.5 s); held-breath silence 8.2-9.0; one big reveal hit at 9.0 and the ambience cut until 10.4; the shadow's step thud at 12.3; rising sub swell 13.0-15.8; hard cut to silence at the 15.8 blackout. Target -15 LUFS, true peak under -1 dBFS after AAC.

## Overlay
Tag: SLOW LIGHT (top). Hook 0.1-1.5 s; caption IT IS LOOKING AT YOU. 9.6-12.2 s; end line WHO'S FOLLOWING WHO? 12.9-15.7 s; all text clear by 15.75. No counter, no chip.

## Playbook compliance
Hit and motion on frame 0; hook by 1.9 s; held-breath silence before the one biggest hit; wordless; one monotonic counter; palette per playbook; loop frame matches; one idea. No AI imagery.

## Risks and how we handle them
- Stickman must read at phone size: thick tubes, high contrast against the cream wall; QA by contact sheet at 1/4 size.
- The late shadow must be visible but deniable: lag is eased in; check at 2 fps and 30 fps.
- Planar projection with a close lamp distorts limbs; clamp lamp distance so the shadow stays legible.

## As built (tools/shadow-stickman/)
- Profile-view stickman (cylinders + joint spheres, FK rig with grounding and foot angles), walk cycle tied to distance. Shadow = the same skeleton projected from the lamp onto the first plane the ray hits (wall or floor), rendered to a mask, gaussian-blurred for the penumbra, composited under the man. Its own depth `ZS(t)` grows at 12-15.8 s, which makes it loom (projection scale = lamp distance / (lamp distance - depth)).
- Eyes: two glowing discs on the projected head from 9.12 s. Head turn: a nose bump on both heads, the shadow's shrinks to nothing as it turns to face the viewer.
- Loop: lamp blackout at 15.8 s and hard cut to the lit frame 0 (the end state is not the start pose, by design).
- Rebuild: `node render.js 720 1280 $FRAMES $o 480 4` x4 workers, then `FRAMES=$FRAMES OUT=shadow_stickman.mp4 ./build.sh` (about 15 min on 4 CPUs).
