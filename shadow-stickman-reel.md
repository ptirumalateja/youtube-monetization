# The Shadow That Stops Copying (14.4 s, v3, no voiceover): spec

Reel #2 in the psychological series, after `ball-never-falls-reel.md`. Source idea: the inner critic / being watched by yourself. Built in three.js (`tools/shadow-stickman/`), sound synthesised in numpy (no samples, no credits). First episode of a recurring **stickman** character so later reels (bystander, conformity, marshmallow) reuse the rig.

## Idea
A stickman stands in front of a wall under one lamp. His shadow copies every move. Then it is a beat late. Then it does something he didn't. At the reveal it stops being a shadow: it turns to look at the camera while he doesn't. In the last seconds it snaps back into sync and the loop restarts. Closing line: WHO IS FOLLOWING WHO?

## Why this one
Light and shadow are the channel's brand; one character, one lamp, no props; works on mute; the late-shadow moment is a perception hook (viewers rewind to check), and the final line invites comments.

## Look
Charcoal/navy void, one warm key lamp low and in front (a visible bulb at the edge of frame), a pale cream wall with soft falloff, the stickman drawn as thick cream-white round-capped tubes (head ring, torso, 4 limbs) so he reads at phone size, the shadow a soft-edged black silhouette on the wall that is about 1.6x his size (lamp close). Teal rim light only on the floor edge; red only on the label chip. Heartbeat pulse drives vignette and lamp flicker exactly as in the ball reel.

## How the shadow works (honest mechanics)
The shadow is not a shadow-map. It is the same skeleton, projected onto the wall plane from the lamp position with a planar projection matrix and drawn as flat black, soft-blurred in post. Its pose comes from its own clock: `poseShadow(t) = pose(t - lag(t))` plus an override channel for the scripted disobedience (turns head, sits, walks off). While `lag = 0` and no override it is a true cast shadow, so the first seconds are physically correct and the deviation reads as a violation, not a glitch.

## Timeline (14.4 s, v3: tightened after the second review)
V2's character, lamp, wall and palette are frozen. This pass is timing and direction only.

| Time | Beat | Shadow |
|---|---|---|
| 0.0-0.8 | Hit on frame 0; man already walking in; hook fully typed by 0.8 s: YOUR SHADOW ALWAYS COPIES YOU. | exact copy |
| 1.8-3.3 | He stops and raises an arm | copy |
| 3.3-4.6 | He lowers his arm; **the shadow keeps its arm up for over a second** (dissonant sting at 3.5 s); he slowly looks toward it | holds the pose |
| 3.9-5.5 | He is frozen; it is not: slow breathing, a lean, a restless far arm, a head drift; arm lowers slowly 4.6-5.4; no camera drift | subtle motion |
| 5.5-5.9 | **Without warning the shadow turns its head** (nose bump disappears). No camera move, near-silent | impossible |
| 5.9-6.5 | Held breath: lamp stutters, silence | - |
| 6.5-6.62 | Reveal hit; lamp out 3 frames; he startles, freezes, trembles | calm, upright |
| 6.62-8.4 | Eyes light; push-in toward the eyes with a small shake; ambience cut until 7.9; caption IT IS LOOKING AT YOU. at the bottom | own |
| 8.4-10.6 | Shadow takes one deliberate step toward the lamp/viewer (thud 8.8) and creeps closer; its depth is capped so head and both eyes stay in frame | own |
| 10.6-14.1 | **It stops and stares** at the viewer, perfectly still, eyes slowly pulsing; WHO'S FOLLOWING WHO? types 10.9-12.0 at the bottom; heartbeat 118 -> 128 bpm, rising swell | still |
| 14.1 | Lamp blackout and sound cut = the loop point; cut back to the lit walking shot at frame 0 | - |

No stopwatch or chip. Captions sit at the bottom (y 1450) so they never cover the eyes; the hook stays at the top.

## Sound (procedural, same family as the ball reel)
Heartbeat from the scene's bpm curve; low drone; footsteps on the walk-in; dissonant sting at the first disobedience (3.5 s); a barely audible creak for the head turn (5.5 s, no loud sound); held-breath silence 5.9-6.5; one big reveal hit at 6.5 and the ambience cut until 7.9; the shadow's step thud at 8.8; rising sub swell 9.3-14.1; hard cut to silence at the 14.1 blackout. Target -15 LUFS, true peak under -1 dBFS after AAC.

## Overlay
Tag: SLOW LIGHT (top). Hook 0.0-0.8 s; caption IT IS LOOKING AT YOU. 7.0-9.8 s; end line WHO'S FOLLOWING WHO? 10.9-14.0 s; all text clear by 14.1. No counter, no chip.

## Playbook compliance
Hit and motion on frame 0; hook by 1.9 s; held-breath silence before the one biggest hit; wordless; one monotonic counter; palette per playbook; loop frame matches; one idea. No AI imagery.

## Risks and how we handle them
- Stickman must read at phone size: thick tubes, high contrast against the cream wall; QA by contact sheet at 1/4 size.
- The late shadow must be visible but deniable: lag is eased in; check at 2 fps and 30 fps.
- Planar projection with a close lamp distorts limbs; clamp lamp distance so the shadow stays legible.

## As built (tools/shadow-stickman/)
- Profile-view stickman (cylinders + joint spheres, FK rig with grounding and foot angles), walk cycle tied to distance. Shadow = the same skeleton projected from the lamp onto the first plane the ray hits (wall or floor), rendered to a mask, gaussian-blurred, composited under the man. Its own depth `ZS(t)` grows 8.4-10.6 s (capped at +0.65 m so the head stays in frame), which makes it loom.
- Eyes: two glowing discs on the projected head from 6.62 s, a slow pulse once it has stopped.
- Loop: lamp blackout at 14.1 s and a hard cut to the lit frame 0 (the end state is not the start pose, by design).
- Result: 14.4 s, -15.3 LUFS, true peak -0.9 dBFS after AAC, 6.3 MB.
- Rebuild: `node render.js 720 1280 $FRAMES $o 432 4` x4 workers, then `FRAMES=$FRAMES OUT=shadow_stickman.mp4 ./build.sh` (about 13 min on 4 CPUs; restart `python3 -m http.server 8778` first if it has died).
