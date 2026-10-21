# Proton Laps Earth (v1, with the light-wins ending)

- **Video:** `final-reels/proton-laps-earth.mp4` (local only, not in git). 22.5 s, 1080x1920, 30 fps, loops, no voiceover.
- **Status:** delivered 21 Oct 2026. Teja then asked for a new cut: a realistic Earth, and one full minute of laps (448) compressed into about 20 s. That cut is `proton-laps-one-minute.md`.
- **Build:** `tools/proton-laps/` (see its README); publish copy `proton-laps-publish-copy.md`.

## Concept
Protons in CERN's Large Hadron Collider move at 99.999999% of light speed: fast enough to circle Earth 7.48 times in one second. Twist: light still wins, by 2.85 m after 299,792 km. Nothing with mass catches light.

## Shot plan
| Time | Shot |
|---|---|
| 0-2.4 | Dark globe with a gold equator (tick per 1,000 km); a real-speed blur of light whips around it. Hook: "THIS PROTON / CIRCLES EARTH 7.5× / IN ONE SECOND." |
| 2.4-12.4 | One second slowed 10x: the proton laps the equator, each lap leaving a glowing ring (a coil). TIME / LAPS / KM counters climb to 1.000 s, 7.48, 299,792. |
| 12.4-14.4 | "7.5 LAPS IN 1 SECOND." chip "REAL PROTONS · CERN LHC", "its 27 km ring: 11,245 laps a second". |
| 14.4-16.6 | "AND LIGHT STILL WINS." Log plunge from Earth scale to metres along the beam. |
| 16.6-21.0 | Finish line: two lanes with metre ticks, light ahead of the proton, a 1.75 m person for scale, red bracket "2.85 M". "BY 2.85 METRES. AFTER 299,792 KM." then "NOTHING WITH MASS CATCHES LIGHT." |
| 21.0-22.5 | Pull back to Earth, blur ring returns (loop). |

## Facts and sources
- Speed of light 299,792.458 km/s (exact, SI definition). Earth's equatorial circumference 40,075 km (WGS 84). 299,792.458 / 40,075 = 7.48 laps per second.
- LHC Run 3 beam energy 6.8 TeV per proton (CERN). Proton mass 0.938 GeV -> gamma about 7,247, 1 - v/c = 1/(2 gamma^2) = 9.5e-9 -> v = 99.99999905% of c, about 2.85 m/s slower than light.
- LHC circumference 26.659 km; protons lap it about 11,245 times a second (CERN LHC facts).
- On screen: "THOUGHT EXPERIMENT · NOT TO SCALE" (real protons circle the 27 km ring, not Earth).

## Sound
Fully synthesised (`sound.mjs`, no credits): speed whine, doppler pass-by each time the proton crosses the front of Earth, climbing lap ticks, counter chatter, falling plunge whoosh, bright "zing" for light. -16.4 LUFS, true peak -2.9 dBFS after AAC.

## Publish copy (summary)
- YouTube title: "This Proton Circles Earth 7.5 Times in One Second #shorts"
- Pinned comment: "2.85 metres after 300,000 km. Is that close, or impossibly far?"
- Full copy: `proton-laps-publish-copy.md`.
