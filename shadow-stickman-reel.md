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

## Timeline (16 s, fast pacing)
| Time | Beat | Shadow |
|---|---|---|
| 0.0 | Hit on frame 0; stickman already moving (slow pace + arm swing); hook types: YOUR SHADOW ALWAYS COPIES YOU. | exact copy |
| 1.5-4.0 | He stops, raises an arm, tilts his head, steps; lamp creeps closer, cone narrows, heartbeat 54 -> 80 bpm | exact copy |
| 4.0-6.5 | First tell: lag grows 0 -> 0.12 s (almost invisible), creak/tick in the audio | late |
| 6.5-8.2 | He freezes mid-step; shadow still finishes the step | lag 0.5 s |
| 8.2-9.0 | Held breath: silence, lamp stutters | frozen |
| 9.0 | Reveal hit; lamp flickers off for 3 frames | on relight it has turned its head to the camera, he hasn't |
| 9.4-12.0 | He backs away; the shadow sits down; the camera pushes to the shadow | independent |
| 12.0-14.0 | Shadow stands, walks out of frame; he follows 0.4 s later (his pose now delayed) | leads |
| 14.0-15.6 | Both return into the first frame's pose; shadow snaps back into exact sync; end line: WHO IS FOLLOWING WHO? | copy again |
| 15.6-16 | All text clears; last frame = frame 0 pose (loop) | copy |

Single source of truth for timings: `tools/shadow-stickman/timeline.json`.

## Sound (procedural, same family as the ball reel)
Heartbeat from the scene's bpm curve; low drone; wall-scrape and footstep ticks tied to the shadow's late steps (sound follows the shadow, not the man, after 4 s: a tell); held-breath silence 8.2-9.0; one big reveal hit at 9.0; lamp-stutter electrical crackle; rising loop tone into frame 0. Target -15 LUFS, true peak under -1 dBFS after AAC.

## Overlay
Tag: SLOW LIGHT (top). Stopwatch with red chip label "WATCHING" -> "WATCHED" at the reveal, leaves at 11 s. Hook 0.1-1.4 s; end line 12.9-14.4 s; everything clear before the loop.

## Playbook compliance
Hit and motion on frame 0; hook by 1.9 s; held-breath silence before the one biggest hit; wordless; one monotonic counter; palette per playbook; loop frame matches; one idea. No AI imagery.

## Risks and how we handle them
- Stickman must read at phone size: thick tubes, high contrast against the cream wall; QA by contact sheet at 1/4 size.
- The late shadow must be visible but deniable: lag is eased in; check at 2 fps and 30 fps.
- Planar projection with a close lamp distorts limbs; clamp lamp distance so the shadow stays legible.

## As built (tools/shadow-stickman/)
- Profile-view stickman (cylinders + joint spheres, FK rig with grounding), walk cycle tied to distance so feet match the ground speed. Shadow = same skeleton projected from the lamp onto the first plane the ray hits (wall or floor), rendered to a mask, gaussian-blurred for the penumbra, composited under the man. At 9.12 s two glowing eyes appear on the shadow's head.
- Loop: the entry curve is extended backwards for the re-entry (14.5-16 s), so position, stride phase and velocity at 16 s equal frame 0; both man and shadow are off-screen while the scripted shadow hands back to the copy at 14.4-14.7.
- Extra caption added: IT IS LOOKING AT YOU. (9.5-12.4 s). Chip: WATCHING -> WATCHED at 9.0 s; stopwatch leaves at 10.6-11.0 s.
- Result: 16 s, -16.5 LUFS, true peak -1.6 dBFS after AAC, 6.8 MB.
- Rebuild: same as the ball reel (`node render.js 720 1280 $FRAMES $o 480 4` x4 workers, then `FRAMES=$FRAMES OUT=shadow_stickman.mp4 ./build.sh`), about 15 min on 4 CPUs.
