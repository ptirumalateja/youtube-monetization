# 11 Indias Fit on the Moon (v1)

Teja's brief (27 Oct 2026): the "how many Indias fit on the Moon" idea already did 4.2M views on another channel, so the differentiator is the unit underneath: India's real outline, drawn true to scale, re-tiling every bigger body, with a states series as the follow-up. 21.6 s, 1080x1920, 30 fps, wordless, loops.

## Numbers (by surface area)

India 3.287M km² (official). Moon 37.93M km² → 11.54; Earth 510.1M → 155.2; Jupiter 61.42B (mean radius 69,911 km) → 18,686, shown as 18,700; Sun 6.082T → 1.85 million. The script's 62.1B km² for Jupiter is not the NASA figure, so the reel does not say 18,900.

## Beat map

| Time | Beat | Picture | Text |
|---|---|---|---|
| 0.0-1.6 | Hook | A flat glowing India (tricolour) floats down onto the Moon and wraps onto it at 1.0 s | 11 INDIAS / FIT ON THE MOON. |
| 1.6-5.2 | Tier 1 | The Moon turns; 10 more Indias stamp on, then a half India (north half filled, south half ghosted) | counter 1 → 11.5, INDIAS ON THE MOON |
| 5.2-8.8 | Tier 2 | The Moon drops onto Earth's upper-left limb (impact flash); a wave of Indias spreads over Earth from the contact point | 155 INDIAS ON EARTH |
| 8.8-12.4 | Tier 3 | Earth (with the Moon) drops onto Jupiter; Indias spread as a fine mesh | 18,700 INDIAS ON JUPITER |
| 12.4-16.0 | Tier 4 | Jupiter drops onto the Sun; a lace of sub-10 px Indias sweeps the Sun while the camera pulls out | 1.85 MILLION INDIAS ON THE SUN |
| 16.0-18.0 | Payoff | Pull back; a ring marks the Earth, a few pixels wide | INDIA IS / A PIXEL TOO. |
| 18.0-20.0 | Prompt | The push back in starts; the stack separates again, text over the starfield | WHICH STATE GOES / ON THE MOON NEXT? |
| 20.0-21.6 | Loop | Camera lands on the opening Moon shot; the flat India re-forms above the Moon | 11 INDIAS / FIT ON THE MOON. |

No handle card and no platform icons: handles go in the caption.

## How it is built

- `make_sdf.py`: India outline (Natural Earth 10m, India point-of-view edition: all of J&K incl. Aksai Chin) → signed distance field on the Lambert azimuthal equal-area plane, in Earth radii (`tex/india_sdf.f32`).
- Every copy is that plane scaled by Earth radius / body radius and projected back onto the body with inverse LAEA, so each India has its true area on every body.
- `pack_moon.py`: annealing over 11 centres + rotations so the 11.5 Moon copies overlap as little as possible (87% covered, 11% doubled). The hero stays facing the camera, north up.
- Earth, Jupiter, Sun: copies on equal-area latitude bands (cell area = India's area), painter order by distance from the contact point, so each new India lands on top as the wave passes.
- `gl/head.glsl + lib.glsl + main.glsl`: analytic spheres (no ray marching), surfaces reused from `tools/size-ladder` (Moon albedo + craters, Blue Marble Earth, procedural Jupiter, boiling Sun with corona). About 3 s per 1080x1920 plate alone, ~12 s with 4 in parallel.
- `cam.py`: timeline (drops, waves, Moon spin that makes exactly one turn so the loop matches, camera in log distance with the target following linearly in distance). `comp.py`: dust, bloom, grain, text, counter, Earth ring. `sound.py`: sound design. `run_plates.sh OUT 4` renders and composites.
