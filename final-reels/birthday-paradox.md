# The Birthday Paradox

- **Video:** `final-reels/birthday-paradox.mp4` (local only, not in git). 21.5 s, 1080x1920, 30 fps, loops, no voiceover.
- **Status:** delivered 21 Oct 2026; Teja did not like it ("I dont like it"), so it is parked, not for posting.
- **Build:** `tools/birthday-paradox/` (see its README); publish copy `birthday-paradox-publish-copy.md`.

## Concept
23 people in a room give a 50.7% chance that two share a birthday; 70 people give 99.9%. The hook is the disbelief (most people guess around 183). The explanation is visual: count the pairs, not the people (23 people = 253 pairs).

## Shot plan
| Time | Shot |
|---|---|
| 0-2.2 | Empty 365-day ring (JAN at the top), gold pulse sweeps on frame 0. Hook typed: "23 PEOPLE. / 50% CHANCE TWO / SHARE A BIRTHDAY." |
| 2.2-11.0 | Camera tilts into 3D. People drop in as dots on their birthday slot; each new dot threads a teal arc to every earlier dot. Centre counter "CHANCE OF A SHARED BIRTHDAY" climbs 0% -> 47.6%; PEOPLE / PAIRS counters below; teal gauge creeps toward a red 50% tick. |
| 11.0-11.75 | Held breath; person 23 falls slowly. |
| 11.75-15.2 | Person 23 lands on 14 March next to person 8: red dots, red circle, chip "BOTH MAR 14", flash, biggest hit. Caption "23 PEOPLE / MEANS / 253 PAIRS / EVERY PAIR IS A CHANCE TO MATCH." Odds 50.7%. |
| 15.2-18.0 | Fast fill to 70 people, 2,415 threads, more red matches; 99.9%. |
| 18.0-20.2 | "COUNT THE PAIRS, / NOT THE PEOPLE." |
| 20.2-21.5 | Dots and threads implode into the centre; empty ring = frame 0 (loop). |

## Facts and sources
- P(n) = 1 - prod_{k=0}^{n-1} (365-k)/365: P(22) = 47.6%, P(23) = 50.7%, P(70) = 99.9%. Pairs n(n-1)/2: 253 at 23, 2,415 at 70. Standard result (e.g. any probability textbook; Wikipedia "Birthday problem").
- Assumes 365 equally likely days, ignores 29 February. The dots are one seeded simulated room; the first match is forced at person 23 so it lands where the odds pass 50%; everyone after is random. On screen: "THOUGHT EXPERIMENT · ONE SIMULATED ROOM".

## Sound
Fully synthesised (`sound.mjs`, no samples, no credits): music-box plucks where each month is a note (birthday twins ring in unison), tightening drone, accelerating heartbeat, thread sparkle, one big gong-partial hit on the match. -15 LUFS, true peak -1.6 dBFS after AAC.

## Publish copy (summary)
- YouTube title: "23 People. 50% Chance Two Share a Birthday. #shorts"
- Pinned comment: "What number did you guess before watching? Most people say around 183."
- Full copy: `birthday-paradox-publish-copy.md`.
