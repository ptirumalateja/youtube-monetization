# Slow Light: "16 Sunrises a Day" (ISS free-fall reel), frozen plan v1

Wordless space reel, 22.5 s, 1080x1920, 30 fps, loops. Built in `tools/iss-sunrises/` (three.js scene + in-page overlay, rendered with headless Chrome; sound synthesised in Node). Follows `slow-light-design-playbook.md`.

## Idea
Hook: astronauts on the ISS see 16 sunrises a day. Twist: the station is not floating, it is falling the whole time and keeps missing Earth (Newton's cannonball). Thesis line: "THEY NEVER STOP FALLING."

## Facts (checked)
| Fact | Value used on screen | Basis |
|---|---|---|
| ISS altitude | 400 KM UP | operates about 400-420 km |
| Orbital period | about 92.7 min (scene constant) | ~92-93 min |
| Sunrises per day | 16 | 24 h / 92.7 min = 15.5 orbits; starting on a sunrise, 16 sunrises fall inside 24 h (NASA: "16 sunrises and 16 sunsets") |
| Orbital speed | 7.7 KM/S (about 28,000 km/h) | ~7.66 km/s |
| Gravity at 400 km | about 90% of the surface value | (6371/6771)^2 = 0.885 |
| Earth's rotation during the day | one turn in 24 h, orbit plane fixed, 51.6 deg inclination | real geometry |
Newton's cannon is a thought experiment: the tower is 400 km tall and drawn not to scale. Arcs are integrated with real inverse-square gravity from that height (2, 4, 6, 7.7 km/s).

## Shot plan (camera grammar C: "orbit riding")
| Time (s) | Shot | Text |
|---|---|---|
| 0.0-2.2 | POV behind the ISS silhouette, dark Earth limb below; the Sun breaks over the limb on frame 0 (hit) and the station's arrays catch it | hook "THEY SEE 16 SUNRISES A DAY." typed by ~1.6 s; red chip "ISS · 400 KM UP"; counter SUNRISE 1, clock 00:00 |
| 2.2-3.4 | Snap: fast log pull-back from the station to a wide orbit view (Earth fills ~70% width, teal orbit ring, gold station dot with trail) | |
| 3.4-11.4 | Time-lapse: the dot laps Earth, accelerating; Earth turns once; every exit from the shadow is a gold sunrise flash at the terminator and a counter tick 2 -> 16; slow camera orbit for parallax | clock 00:00 -> 24:00, counter monotonic |
| 11.4-12.6 | Camera swings to face the orbit plane; the dot stops at the top of Earth; a 400 km tower rises under it | "IT ISN'T FLOATING." ; tag "THOUGHT EXPERIMENT · NOT TO SCALE" |
| 12.6-15.2 | Cannon arcs 2, 4, 6 km/s: each falls farther around the curve; red impact marks | speed readout (monotonic) |
| 15.2-15.7 | Held breath (near silence) | |
| 15.7-17.4 | 7.7 km/s arc wraps all the way round and closes on itself = the ISS orbit; biggest hit at closure, ring flares | "IT'S FALLING. IT JUST KEEPS MISSING EARTH." |
| 17.4-19.0 | Dot runs on again; fact line | "GRAVITY UP THERE: ~90%." |
| 19.0-20.6 | Plunge back down to the station POV on the night side | |
| 20.6-22.5 | Night limb, faint dawn glow grows; end line; last frame leads into frame 0 (sunrise) | "THEY NEVER STOP FALLING." |

## Visual identity (new to the channel)
Procedural Earth (fbm continents, clouds, gold city lights on the night side, teal atmosphere rim, warm terminator band); procedural ISS silhouette (truss, 8 array wings, modules); orbit ring teal; station gold; red only for chips and impact markers. No Sun disc design from earlier reels: here the Sun is a starburst over the limb.

## Sound family (new): "orbit glass"
Fully synthesised (no samples, no licences needed): frame-0 dawn swell + hit, one rising pentatonic glass chime per sunrise (16 notes climbing, monotonic like the counter), a low engine-room drone with slow pulse, snap whoosh, cannon thumps, held-breath silence, closure hit (biggest), plunge whoosh, loop riser into frame 0. Sub only on the hit bus, others high-passed at 90 Hz, about -15 LUFS, true peak checked after AAC.
