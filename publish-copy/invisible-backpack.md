# The Invisible Backpack (stickman, Part 1 of 2)

| | |
|---|---|
| Status | v1 delivered, awaiting Teja's review; Part 2 ("Check Your Friend's Bag") picks up on its last frame |
| Upload file | `final-reels/invisible-backpack_master.mp4` (share: `invisible-backpack_master_share.mp4`; silent: `invisible-backpack_music-ready.mp4`, payoff chord on 15.0 s) |
| Length | 18.0 s (end frame held 1.2 s) |
| Voice | None (wordless; on-screen text only) |
| Copy taken from | storyboard brief for Part 1; build notes in `tools/invisible-backpack/README.md` |

## Publish copy

**YouTube Shorts title:** The Backpack Nobody Could See #shorts

**YouTube description:**
> You were never slow. You were just carrying too much.
> What will they say. Failed in 2021. I'm behind. Not ready. Every one of them was a rock in a bag nobody else could see.
> He didn't throw them away. He stood on them.
> Your baggage is your foundation. One rock a day.
>
> Part 1 of 2. A Slow Light parable, made entirely in code (three.js, rendered frame by frame; sound synthesised, no samples).
>
> #stickman #motivation #mentalhealth #selfimprovement #overthinking #animation #parable #shorts

**Instagram / Facebook caption:**
> You were never slow. You were just carrying too much. 🎒
> He didn't throw the rocks away. He built with them.
> Part 2 tomorrow — what he did after reaching the top.
> #stickman #motivation #mentalhealth #overthinking #animation #reels

**Pinned comment:** What's the heaviest rock in your bag? Name it, then put it under your feet.

**Hashtags:** #shorts #stickman #motivation #mentalhealth #selfimprovement #parable #animation #slowlight

**Sound credit line:** none needed (all sound synthesised for this reel in `tools/invisible-backpack/sound.py`).

**Upload settings:** 9:16, AI/synthetic media label on (rendered scene), no music claimed. For the `_music-ready` cut, line the platform track's drop up with 15.0 s (the payoff text and the lamp).

## On-screen text

| Time (s) | Text |
|---|---|
| 0.0-2.0 | WHY DOES IT FEEL / SO HEAVY? |
| 2.15-4.0 | THE INVISIBLE / BACKPACK |
| 2.45-7.0 | Rock labels, blurred until each rock turns into focus: WHAT WILL THEY SAY / FAILED IN 2021 / I'M BEHIND / NOT READY / COMPARE / TOO LATE / NOT ENOUGH |
| 7.25-9.0 | YOU DON'T HAVE TO / THROW IT AWAY. |
| 9.6-14.9 | ROCK 1 → STEP 1 ... ROCK 7 → STEP 7 (monotonic counter, red STEP chip) |
| 12.35-14.9 | BUILD WITH IT. |
| 15.3-18.0 | YOUR BAGGAGE IS / YOUR FOUNDATION. · One rock a day. · slowlighttv |

## Facts and sources

The reel is a parable and makes no factual claim on screen. "FAILED IN 2021" is a stand-in year from the brief (kept as written). The rock labels are generic inner-critic phrases, not quotes from anyone. Nothing here claims a statistic or a real person.

## Playbook check

Motion and a heartbeat hit on frame 0; hook typed by 1.3 s; pattern interrupt (flash + x-ray cut) at 2.0 s with a 16% flash (no white frame); one idea; one monotonic counter (asserted in `render.cjs meta` and `overlay.py`); held breath 14.6-15.0 s before the payoff chord; red used only for the STEP chip; cream text with black stroke in Liberation Mono Bold; text kept out of the bottom 18%; wordless. Measured after AAC: -15.5 LUFS integrated, -2.2 dBFS peak.
Deviation from the usual loop rule: the brief asks for an end-frame hold and a hand-off to Part 2, so the last frame (hero on the stair) does not match frame 0 (walking under the bag).
