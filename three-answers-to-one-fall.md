# Three Answers to One Fall (reel #9 of the reference remakes)

**Final file:** `three-answers-to-one-fall.mp4` (22.0 s, 1080x1920, 30 fps, H.264 9.8 Mbps two-pass + AAC 192k, 28 MB), saved in the project files under `final-reels/`. Not in git (rendered outputs stay out of git per `claude.md`).
**Source:** `tools/three-answers/` (`index.html` scene with `window.renderAt(t)`, `render.js`, `shot.js`, `overlay.py`, `mix.py`, `build.sh`).
**Reference it replaces:** "Newton vs Einstein vs Quantum Gravity" (24 s, 720x1280): a teal rubber-sheet wireframe well with an orange sun and small planets, tiny cluttered UI text. We kept the topic only; no footage, layout, text or assets.

## Concept
One golden apple, one fall, seen through three lenses. A year odometer climbs 1687 → 1915 → 2026 and a left ladder (NEWTON / EINSTEIN / ???) shows which answer we are on.

1. **Newton (1687):** a gold force arrow pulls the apple toward Earth's centre; a field of teal arrows (lengths fall off as 1/r²) all aim at the centre; strobe ghosts at equal time steps show the gaps growing as it speeds up.
2. **Einstein (1915):** the arrow is gone. Seven clock rings stack along the fall; each ring's bead and tick pulse run slower the lower the ring sits (heavily exaggerated, tagged). The apple falls through their centres. Then a light ray passes and bends toward Earth against a dashed straight reference line: light falls too. No rubber sheet.
3. **Quantum gravity (2026: today):** the camera dives into the empty space under the apple. A smooth lattice of space boils and breaks into foam bubbles. Stamp: UNKNOWN.

Twist: held breath, then the biggest hit and a pull-back to the whole small planet: **"NOBODY HAS THE THIRD ANSWER YET."** The camera returns to the apple on its branch and the last frame matches frame 0, so the reel loops into the next release.

What makes it better than the reference: one readable idea per beat instead of a static wireframe, the correct relativity picture (time runs slower below, not a ball on a trampoline), a real third answer beat that is honest about being unknown, true 3D with parallax and motion blur at native 1080x1920, and a designed sound track where the physics is audible (the clocks literally tick slower lower down).

## Shot plan (video seconds)
| Time | Shot | Text |
|---|---|---|
| 0.0-0.55 | Frame 0: the apple snaps off the branch (hit), falls | |
| 0.55-2.2 | Time freezes with the apple mid-air; slow push-in | WHY DOES IT **FALL?** (typed by ~1.3 s) |
| 2.2-3.0 | Gold force arrow grows under the apple; field arrows fade in; camera pulls back | ANSWER 1 OF 3 · 1687 · **NEWTON** · A FORCE PULLS IT DOWN. |
| 3.0-5.5 | Apple falls along the arrow; strobe ghosts every 0.3 s | EQUAL TIMES, GROWING GAPS: IT SPEEDS UP |
| 5.5-6.9 | Landing (thud), small bounce | |
| 6.9-7.9 | Rewind: apple lifts back to the branch, arrows dissolve | |
| 7.9-8.9 | Clock rings light up top to bottom; camera rises and orbits so the rings open | ANSWER 2 OF 3 · 1915 · **EINSTEIN** · NO FORCE. TIME RUNS SLOWER BELOW. |
| 8.9-11.5 | Apple falls through the ring centres, gold trail | 1 METRE LOWER: 1 SECOND LOST EVERY ~290 MILLION YEARS |
| 10.9-12.9 | Light ray crosses and bends toward Earth vs dashed straight line | THE APPLE FOLLOWS BENT SPACETIME. / SO DOES LIGHT (MEASURED IN 1919) |
| 12.7-13.7 | Rewind to the branch, rings fade | |
| 13.9-16.7 | Dive into a smooth lattice under the apple; it boils, bubbles appear | ANSWER 3 OF 3 · 2026: TODAY · **QUANTUM GRAVITY** · SPACETIME ITSELF MAY TURN TO FOAM / AT 10⁻³⁵ METRES: THE PLANCK LENGTH |
| 15.6-17.2 | Foam fully grainy | UNKNOWN (stamp, red outline) |
| 17.2-17.8 | Held breath: foam freezes and dims, near silence | |
| 17.8-20.3 | Biggest hit; foam bursts outward; pull-back to the whole planet | NOBODY HAS / THE THIRD / ANSWER **YET.** |
| 20.3-22.0 | Camera returns to the opening framing; apple on the branch | loops to frame 0 |

Tag throughout: THOUGHT EXPERIMENT · NOT TO SCALE (plus · CLOCKS EXAGGERATED during Einstein).

## Facts and sources
| Claim on screen | Check | Source |
|---|---|---|
| Newton, 1687 | *Philosophiæ Naturalis Principia Mathematica* published 5 July 1687 (law of universal gravitation). | Newton, *Principia* (1687) |
| Einstein, 1915 | Field equations of general relativity presented to the Prussian Academy, 25 Nov 1915. | Einstein, Sitzungsber. Preuss. Akad. Wiss. (1915) 844 |
| "No force. Time runs slower below." | In GR an apple in free fall feels no force; for slow motion in weak gravity the fall comes almost entirely from the gradient of clock rates (the time-time part of the metric). We avoid the rubber-sheet picture on purpose. | Standard weak-field (Newtonian) limit of GR, e.g. Carroll, *Spacetime and Geometry*, ch. 4 |
| 1 metre lower: 1 second lost every ~290 million years | Fractional rate difference ≈ g·h/c² = 9.81 × 1 / (2.998e8)² = 1.09e-16. 1 / 1.09e-16 s = 9.2e15 s ≈ 290 million years. Measured directly at 33 cm height difference with aluminium-ion optical clocks. | Chou, Hume, Rosenband & Wineland, *Science* 329, 1630 (2010); [NIST release](https://www.nist.gov/node/406661) |
| Light bends (measured in 1919) | Starlight deflection near the Sun measured during the 29 May 1919 eclipse (Dyson, Eddington & Davidson, *Phil. Trans. R. Soc. A* 220, 1920). Bending shown near Earth is exaggerated (thought experiment tag). | Dyson, Eddington & Davidson (1920) |
| Spacetime may turn to foam at 10⁻³⁵ m (Planck length) | Planck length = 1.616e-35 m (CODATA 2018). "Spacetime foam" is Wheeler's 1955 proposal; it is a hypothesis, so the line says "may". | CODATA 2018; Wheeler, *Phys. Rev.* 97, 511 (1955); [Ng, gr-qc/0001100](https://arxiv.org/pdf/gr-qc/0001100) |
| Nobody has the third answer yet | No theory of quantum gravity (string theory, loop quantum gravity, others) has been confirmed by experiment. | Review consensus (e.g. Kiefer, *Quantum Gravity*, 3rd ed., 2012) |

Odometer is monotonic (1600 → 1687 → 1915 → 2026); `overlay.py` asserts it frame by frame.

## Sound (fully synthesised, licence-clean)
New family, "clockwork and grain", made in numpy by `mix.py` (no samples, so no credits needed):
- Frame 0: stem snap + medium pitch-drop hit, fall whoosh, tape-stop into the freeze, glassy suspended chord.
- Newton: filtered brass swell under the arrow, a pluck per strobe ghost, a whistle whose pitch rises faster and faster as the apple accelerates, landing thud, reversed whoosh on the rewind.
- Einstein: polyrhythm of clock ticks, one voice per ring, synced to the bead crossings in the scene; lower rings tick slower and lower in pitch. Glass sweep for the light ray.
- Quantum: detuned low drone, high fizz, granular crackle whose density follows the foam.
- Held breath (17.2-17.8 s, about -40 dB) with a quiet reversed suck and a 60 ms vacuum, then the one big hit (crack + 330→55 Hz body + gong partials + sub).
- Tail: dark pad, a lone pendulum tick each second ("still waiting"), rising link tone into frame 0.
- Master: subs only on the hit bus, other buses high-passed at 90 Hz, reverb per bus, ducking under hits, loudnorm + soft-clip + limiter; measured after AAC: -16.2 LUFS integrated, -1.0 dBTP.

## Build
```
cd tools/three-answers
ln -s <dir with node_modules: three@0.170.0, playwright-core> node_modules   # not committed
./build.sh /path/to/workdir     # renders 660 frames (4 workers, 3 sub-frames each), overlay, mix, final encode
```
`shot.js` renders stills for checks (`python3 -m http.server 8777` in this folder first).

## Publish copy
**Title (YouTube Shorts):** Why does an apple fall? Physics has 3 answers
**Alt titles:** Newton vs Einstein vs quantum gravity in 22 seconds / Nobody has the third answer yet

**Description:**
Same apple. Same fall. Three answers.
1687: Newton says a force pulls it down.
1915: Einstein says there is no force. Clocks run slower closer to Earth, and the apple simply follows bent spacetime. So does light.
Today: at the Planck length (10⁻³⁵ m) spacetime itself may turn to foam. Nobody knows. That's quantum gravity, and nobody has the third answer yet.

Fact check: one metre lower, a clock loses about 1 second every 290 million years (NIST measured this with optical clocks just 33 cm apart, 2010).
Thought experiment, not to scale; clock rates heavily exaggerated.

#physics #gravity #einstein #newton #quantumgravity #relativity #science #shorts

**Pinned comment:** Which answer did you learn in school? 1, 2, or "we don't know yet"?

**Instagram / Facebook caption:** Same apple, same fall, three answers. Newton: a force. Einstein: no force, just bent time. Quantum gravity: ...nobody knows yet. 🍏 #physics #einstein #science

**Upload notes:** turn on the AI / synthetic content label. Audio is original (synthesised), no third-party credits needed.
