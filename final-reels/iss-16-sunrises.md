# 16 Sunrises a Day (ISS free fall)

- **Video:** `final-reels/iss-16-sunrises.mp4` (local only, not in git). 22.5 s, 1080x1920, 30 fps, H.264 + AAC, 26 MB, loops, no voiceover.
- **Status:** delivered 21 Oct 2026, awaiting Teja's review.
- **Build:** `tools/iss-sunrises/` (see its README). Frozen plan `iss-sunrises-spec.md`, publish copy `iss-sunrises-publish-copy.md`.

## Concept
Hook: astronauts on the ISS see 16 sunrises a day. Twist: the station isn't floating. It falls the whole time and keeps missing Earth (Newton's cannonball). End line: "THEY NEVER STOP FALLING." The new camera language is "orbit riding": a POV behind the station at the limb, a wide orbit time-lapse, a face-on view of the orbit plane for the cannon, and a dive back to the station.

## Shot plan
| Time (s) | Shot |
|---|---|
| 0-2.2 | POV behind a procedural ISS silhouette. The Sun breaks over Earth's limb on frame 0 (hit). Hook typed "THEY SEE / 16 SUNRISES / A DAY."; red chip "ISS · 400 KM UP"; counter SUNRISE 1, mission clock 00:00, 16 pips. |
| 2.2-3.4 | Snap: log pull-back from the station to a wide orbit view (teal orbit ring, gold station dot with trail); short exposure dip over the day side. |
| 3.4-11.35 | Time-lapse: the dot laps Earth faster and faster and Earth turns; each exit from the shadow is a gold flash and a counter tick 2 -> 16 (monotonic). Clock runs to 24:00. |
| 11.35-12.6 | Camera swings face-on to the orbit plane and closes in on a 400 km tower under the station. "IT ISN'T FLOATING." plus "THOUGHT EXPERIMENT · NOT TO SCALE". |
| 12.65-15.15 | Cannon arcs at 2, 4 and 6 km/s land farther round the curve (red impact rings); speed readout climbs. |
| 15.2-15.7 | Held breath (near silence). |
| 15.7-17.4 | 7.7 km/s shot wraps all the way round and closes on itself (the ISS orbit). Biggest hit, ring flare. "IT'S FALLING. / IT JUST KEEPS MISSING EARTH." |
| 18.25-19.6 | "GRAVITY UP THERE / STILL ~90%". |
| 19.0-20.6 | Dive along the orbit back to the station on the night side. |
| 20.6-22.5 | Night limb with airglow, end line "THEY NEVER / STOP FALLING." typed then faded; the last frame leads into the frame-0 sunrise (loop checked). |

## Facts and sources
- ISS altitude about 400-420 km; orbital speed about 7.66 km/s (~28,000 km/h); period about 92-93 min (NASA ISS facts and figures).
- 24 h / 92.7 min = 15.5 orbits, so the crew sees about 16 sunrises and 16 sunsets a day (NASA's commonly quoted figure). Scene uses a 92.7 min period; starting on a sunrise, sunrise 16 falls at 23:10 of mission time.
- Gravity at 400 km: (6,371 / 6,771)^2 = 0.885 of surface gravity, shown as "~90%".
- Orbit as free fall: Newton's cannonball thought experiment (Principia, "A Treatise of the System of the World"). The arcs are integrated with inverse-square gravity from a 400 km tower at 2, 4, 6 km/s (they land 5.5, 12.4 and 25.8 degrees round the Earth) and at circular speed for the closed orbit.
- Not to scale: the tower, the station marker and the atmosphere thickness are exaggerated; Earth's turn is set to 16 orbits so the loop closes exactly. Visuals are procedural 3D (no NASA imagery); the ISS model is simplified.

## Sound
Fully synthesised in `tools/iss-sunrises/synth.mjs` (no samples, no credits): one glass FM bell per sunrise rising up a pentatonic scale (16 notes, monotonic like the counter), cabin-air bed and 110 Hz drone, snap whoosh, cannon thumps and impacts, rising "around the world" tone into the closure hit, pad swell, plunge whoosh, dawn riser into the loop. Sub only on the hit bus, others high-passed at 90 Hz. -14.8 LUFS, true peak -2.1 dBFS after AAC.

## Publish copy (summary)
- YouTube title: "Astronauts see 16 sunrises a day" (alternatives: "The ISS isn't floating. It's falling."; "Why the space station never hits the ground").
- Hashtags: #space #ISS #science. Pinned comment: "Did you know the ISS is falling right now, at 7.7 km per second? 🌍"
- Altered or synthetic content: Yes. Full copy for YouTube, Instagram and Facebook: `iss-sunrises-publish-copy.md`.

## Known limits
- The snap at about 2.5 s passes over the bright day side for about half a second (darkened, but the brightest moment in the reel).
- Not yet listed in `slow-light-design-playbook.md` (another thread had uncommitted edits there).
