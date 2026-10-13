# Slow Light "What If" #2: Is the night sky showing us the past? (18 s, no voiceover)

Format: 9:16, 18 s, loops. Pure visuals plus sound design, a few words of on-screen text, a counter. No narration.
Feel: visual wonder, travelling through portals (orbiting-spark rings), anime impact frames on the hits.
Palette (playbook): charcoal and near-black, warm cream for text and line work, one red accent, occasional muted teal. Warm orange-white sparks on the portals.
Retention rules: frame 0 is already in motion with a hit; the pattern interrupt lands at ~1.8 s; something changes every 1-1.5 s in the first 6 s.

## Fact guardrails (every number on screen)
| On screen | Fact | Note |
|---|---|---|
| 1.3 SECONDS - MOON | Moonlight takes about 1.28 s | safe |
| 8 MIN 20 S - SUN | about 499 s average | matches the Sun reel |
| 4.2 YEARS - PROXIMA | 4.24 light-years | nearest star |
| ~600 YEARS - BETELGEUSE | estimates run ~550-700 ly | keep the "~" |
| 2.5 MILLION YEARS - ANDROMEDA | 2.5 million ly | most distant naked-eye object |
- Final line: "YOU'RE LOOKING AT THE PAST." True for every star and galaxy: we see each as it was when the light left it. Do NOT say the stars are "gone" or "dead"; most still exist.
- Label the reel "Thought experiment / not to scale" (distances are compressed).

## Timeline
| Time | Visual | On-screen text | Sound |
|---|---|---|---|
| 0.00 | Frame 0 already moving: small stargazer silhouette under a dense night sky, one star pulsing | none | HIT at 0.0: `869757 dark-suspense-accent` + synth sub boom. Wind bed `22331 wind` underneath. |
| 0.2-1.7 | The star pulses 3 times, faster each time, light flickering down onto the silhouette (charge-up) | `THIS LIGHT IS OLD.` (typed fast, 0.2-0.7 s) | Charge-flicker: `19487 jacobs-ladder` + `849772 electric-sparks` in 6-8 stuttering bursts, 80 ms gaps of near-silence between them |
| 1.7-2.1 | SNAP-ZOOM into the star. Anime impact frames (2 frames white, 1 black), speed lines radiate | text clears | Vacuum 100 ms before; `814047 fantasy-implosion` + `276871 sword-in-air` swish + sub hit. This is the pattern interrupt. |
| 2.1-3.0 | A glowing spark ring (portal 1) opens ahead; camera accelerates into the tunnel of streaking stars | `YEARS AGO` counter appears, 0 | `768664 portal-gate-opening` at ring open, `735062 fast-warp-in` as we enter |
| 3.0 | Pass through portal 1 | `1.3 SECONDS - THE MOON` | Whoosh from `175183 everyday-whooshes` (pass-by 1), tick on label |
| 4.8 | Pass through portal 2 | `8 MIN 20 S - THE SUN` | Whoosh pass-by 2 + `850262 orbiting-plasma-burst` swell |
| 6.6 | Pass through portal 3 | `4.2 YEARS - PROXIMA` | Whoosh pass-by 3 + `752034 sci-fi-gateway` |
| 8.4 | Pass through portal 4 | `~600 YEARS - BETELGEUSE` | Whoosh pass-by 4 + `238375 subby-whoosh` for weight |
| 8.4-11.5 | Hyper-acceleration; counter blurs upward toward 2,500,000; tunnel colours shift teal to red | counter climbing | `822420 riser-hit` riser (pre-roll), `115555 synth-jet` pitching up, `649445 cinematic-woosh` layered, rising sparks |
| 11.3-11.5 | Everything cuts to near-silence for ~150 ms (held breath) | | Vacuum |
| 11.5-14.0 | Final portal opens onto the Andromeda galaxy, huge, with a bloom flare | `2.5 MILLION YEARS` | Hero blast: `814046 explosion-from-another-dimension` + synth sub-bloom wall (tonal body ~200-250 Hz, top end rolling off, dark tail, Crimson-Moon style) |
| 14.0-16.0 | Hold on Andromeda, slow push, particles drifting | `THIS LIGHT LEFT BEFORE HUMANS EXISTED.` (see check below) | Sub wall decays, `850262` plasma trail fades |
| 16.0-16.3 | Hard snap back to the stargazer; silence | | Full silence 0.3 s |
| 16.3-18.0 | Stargazer, calm | `YOU'RE LOOKING AT THE PAST.` | `22331 wind` returns, re-ignition crackle (`849772`) on the last word, hard stop; loops to frame 0 |

Check on the 14-16 s line: modern humans are ~300,000 years old; the Andromeda light is ~2.5 million years old, so "left before modern humans existed" is correct. Keep "modern humans", not "humans".

## Sound mix targets (from the references)
- Integrated -14 LUFS, true peak <= -1.0 dBTP.
- Hit on frame 0; a hit or tick on every visual change; near-silent gaps (-40 dB) before each big hit.
- Hero low end: synth sub boom + tonal body (200-250 Hz), top end rolled off on the tail. Near-mono centre.
- Gap in the library: no fire/flame roar or low tonal drone. I'll synthesize those, or ask for 1-2 more files.

## Library notes
- 17 files in the Drive folder, mapped above. Each is a Freesound file: **confirm every licence is CC0 (or CC-BY with credit added to the description). Avoid any CC-BY-NC.**
- The files could not be downloaded from Drive without sign-in. Share the folder as "Anyone with the link can view" or attach the files in chat.

## Build plan
1. 3D spike: tunnel and spark-ring portals in three.js (headless Chromium, CPU rendering), 5 s test.
2. If the spike looks good: render the full tunnel, composite stargazer/night-sky/Andromeda plates (Qwen/Wan), anime impact frames, text and counters in PIL/ffmpeg.
3. Sound: assemble the library files plus synth layers, then loudness-match to -14 LUFS and compare hit density with the references.
4. Fallback if the 3D look disappoints: 2D anime-style portals (ink rings, speed lines, motion on twos).

## Quality gate
1. The first frame is moving and the first hit lands at 0.0 s.
2. A pattern interrupt lands at ~1.8 s.
3. Every number on screen matches the fact table.
4. Text is inside the Shorts safe zone (bottom ~18% and top strip clear).
5. The loop point (stargazer to stargazer) feels intentional.
6. All sound files have a confirmed commercial-safe licence.

## Build status (v1 built)
- Built as `night_sky_past_v2_hq.mp4` (18 s, 1080x1920, 23 MB). Plates: Qwen+Wan+SeedVR2 (stargazer, Andromeda); tunnel: three.js (`tools/portal-spike/index2.html`); text/impact frames: `tools/night-sky/overlay.py`; sound: `tools/night-sky/mix.py` (library files + synth sub wall).
- Measured: -15.7 LUFS, -1.7 dBTP, 13 distinct hits, silent gaps at 1.6 s, 11.3 s, 16.0 s. Audio not yet auditioned by ear.
- Licences of the 18 Freesound files still need confirming (CC-BY needs credit in the description).

## Revision v3 (two hook variants)
- New opening: near-dark frame 0 with a flaring star, sky lights up, snap-pull at 0.5 s, portal ring forms 1.0-1.7 s, pulled into the tunnel at 2.1 s. Hook text starts at 0.35 s: **A** "YOU'RE SEEING THE PAST." vs **B** "THIS LIGHT IS OLD."
- Tunnel (`tools/portal-spike/index3.html`): four different portals (Moon: silver ring, Sun: gold double ring with flares, Proxima: red hexagon, Andromeda: large spiral ring), helix filaments for depth, streaks fade at the vanishing point.
- Counter holds on three milestones (Moon 1.3 s, Sun 8 min 20 s, Proxima 4.2 years) with a log ruler; display jumps to 2.5 million years for Andromeda.
- Andromeda: firmer push, outward particles, shockwave ring. Ending frame matches frame 0 (loop).
- Sound (`tools/night-sky/mix2.py`): per-portal sound identities, bass restricted to designed hits, accelerating pulse in the hyper phase, held-breath silence at 11.3 s, controlled-decay sub wall. Measured -15.0 LUFS, -1.2 dBTP; not yet auditioned by ear.
- Wording: "THIS LIGHT LEFT BEFORE HOMO SAPIENS EXISTED."
