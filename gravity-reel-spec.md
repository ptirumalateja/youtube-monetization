# Slow Light "What if gravity switched off?" (about 16 s, wordless, ends on a question)

Status: PROPOSED, waiting for the owner's answers (see "Open questions"). Nothing is built yet.

Owner direction (18 Oct 2026):
- Design style: bright, soft, clay-like low-poly 3D city seen from above in a tall street canyon, pastel stick figures, pale cars, glassy water drops, clean thin sans type, tiny tracked captions running up the left edge (reference stills `images/17.webp`, `images/18.webp`: "TIME WITHOUT GRAVITY 5.0 s SHOWN IN SLOW MOTION", "YOUR HEIGHT 66 m ABOVE THE STREET", centre line "People. Cars. Water. You.").
- Use the real time it takes for things to float, not a round 5 or 10 s. Start with gravity on for 1-2 s while a pretty title explains the question, then a counter runs on the left side for 2-3 s of screen time, then objects and people float at the right moment.
- Reference video (Flow): "What if gravity switched off for 10 seconds?", a 3D New York street, narrated-style text.
- Build in code (three.js, flat-shaded low-poly) so the physics and the counter are exact; same pipeline as the Speed Ladder (render, overlay, mix, spec).

## The real time to float (the fact this reel is built on)
If gravity switched off, an object at rest on the ground keeps moving in a straight line (inertia) at the ground's speed, but the ground is on a rotating, curved planet and curves away beneath it. The ground's centripetal acceleration along the local vertical is a = w^2 R cos^2(lat), with w = 7.292e-5 rad/s and R = 6,378 km. Height above the ground after time t: h = a t^2 / 2.

| Height above the ground | Equator (a = 0.0339 m/s2) | New York, 40.7 deg N (a = 0.0195 m/s2) |
|---|---|---|
| 0.1 m | 2.4 s | 3.2 s |
| 0.5 m | 5.4 s | 7.2 s |
| 1 m | 7.7 s | 10.1 s |
| 3 m | 13.3 s | 17.5 s |
| 10 m | 24.3 s | 32 s |
| 66 m (reference frame) | 62 s | 82 s |

So the honest answer to "how long until you float?": about 10 seconds to be a metre off the ground in New York, and you are only drifting at about 0.2 m/s at that point. The "everything floats up" picture is a time-lapse of that slow, accelerating drift (height grows with the square of time), not an instant effect. This idealisation ignores air, water and elastic effects (below).

Caveats to state or avoid (TO CHECK before any number is on screen):
- Air and water: with gravity gone, the pressure gradient that normally holds the atmosphere down is suddenly unbalanced, so a real atmosphere would start expanding upward at once and fluids would not behave as in the idealisation. The reel should say "ignoring air and water" or stay at "solid objects". Source needed before any claim about air.
- Buildings and anything fixed to the ground stay put; only unattached objects (people, cars, loose things) drift.
- Do not say "you fly off into space"; the drift in the first minute is metres.

## Shot plan (about 16 s, 9:16, 1080x1920, 30 fps)
Grammar: tall street canyon, camera looking down from above the street (as in the stills), a very slow push-in. Light palette (sky blue, warm grey, cream), pastel accents. Type: a clean thin sans (open licence, e.g. Inter or Manrope, to be installed), dark on light, one short centre line, small tracked captions on the left edge.

| Time | Beat | Visual | Text | Sound |
|---|---|---|---|---|
| 0-1.8 | **Gravity on** | The street, people walking, cars, a fountain of water, everything normal. A small ball is dropped and falls (proof gravity is on) | Pretty title, soft fade-in: "WHAT IF GRAVITY SWITCHED OFF?" with the subline "HOW LONG UNTIL YOU ACTUALLY FLOAT?" | Quiet city bed, one soft low tone |
| 1.8-2.2 | **The switch** | The ball stops mid-fall and hangs; one soft hit; the title slides out | Left caption appears: "GRAVITY: OFF" | One clean low hit, then near silence |
| 2.2-5.2 | **The counter (time-lapse)** | A tall counter runs up the left edge, 0.0 s to 10.1 s over 3 s of screen time (about x3.4 speed), with "TIME-LAPSE x3.4". The scene barely changes at first: people and cars hold, the ball drifts | "TIME WITHOUT GRAVITY 0.0 s" rolling; "HEIGHT 0.00 m" | Slow rising tension, tick-free (no beeps) |
| 5.2-6.0 | **The first metre** | Counter reaches 10.1 s: things are now 1 m off the ground; the first people, cars and loose objects visibly lift together | Caption: "10.1 s: ONE METRE OFF THE GROUND" | A soft whoosh, a held breath before |
| 6.0-12.0 | **The float** | The time-lapse continues: counter 10 s to 32 s, height 1 m to 10 m, accelerating (h = a t^2 / 2). People, cars, water drops, trash, loose objects rise together; buildings stay | Left captions: time and height climb. Centre line near the end: "People. Cars. Water. You." | The sound opens up: low pad swell, soft airy texture |
| 12.0-14.2 | **Slow motion and wide** | Pull back to the tall canyon view of the reference stills (everything floating, soft haze), at the moment the counter shows ~32 s and about 10 m | "ABOUT 10 m AFTER 32 s" | Hollow, calm |
| 14.2-16.0 | **The question** | The scene dims slightly | "WOULD YOU RATHER FLOAT FOR 10 SECONDS OR FALL FOR 3?" (or the final question the owner picks) | Soft tail, no loop |

Counter rules: one monotonic time counter and one height counter; both computed from the same formula so they always agree; show "TIME-LAPSE x3.4" so the speed-up is honest; never show a number the formula does not give.

## Fact guardrails
| On screen | Fact | Status |
|---|---|---|
| a = w^2 R cos^2(lat) ; h = a t^2 / 2 | Standard kinematics on a rotating sphere (Earth's rotation rate 7.292e-5 rad/s, equatorial radius 6,378 km) | V (arithmetic; textbook physics, source to be linked before posting) |
| 10.1 s to 1 m; 17.5 s to 3 m; 32 s to 10 m (New York, 40.7 deg N) | Computed from the formula above | V (arithmetic) |
| Speed at 1 m about 0.2 m/s | v = a t = 0.0195 x 10.1 | V (arithmetic) |
| "Ignoring air and water" | Needed: the atmosphere's pressure gradient would no longer be balanced | TO CHECK (physics source) |
| Buildings stay | Anything attached to the ground stays on the ground | V |

## Sound plan
Not the Speed Ladder family. Calm and spacious: a soft city bed, one clean low hit at the switch, a slow rising swell during the counter, airy textures while things float, a hollow tail. CC0 or CC BY only (never NC); the owner may supply files, otherwise synthesised. Target about -15 LUFS, true peak after AAC.

## Build plan
`tools/gravity/`: three.js scene (flat-shaded low-poly street canyon, instanced buildings, people, cars, drops; real physics for the float; camera moves), headless render as before, PIL/HTML overlay for the left captions and the centre line, `mix` for the sound, compose, thumbnails, publish copy. Contact-sheet QA at 2 fps.

## Open questions for the owner
1. Where is it set? New York (matches the reference video; 10.1 s to the first metre) or the equator (7.7 s)? I recommend New York.
2. Air: say "ignoring air and water" on screen (recommended), or leave the air out silently?
3. Final question: "Would you rather float for 10 seconds or fall for 3?" or one of your own?
4. Title wording: "WHAT IF GRAVITY SWITCHED OFF?" with "HOW LONG UNTIL YOU ACTUALLY FLOAT?" underneath, or something else?
