# Frozen Lightning (reel #7 from `ref-remakes-plan.md`)

20 s, 1080x1920, 30 fps, wordless (no voiceover), loops. Final file: `final-reels/frozen-lightning.mp4` in the project files (not in git). Source: `tools/frozen-lightning/`.

## Concept
The reference reel (28 s pixel art) says lightning turns sand into clear glass in a split second. We keep the topic and fix the claim: a real strike makes a **fulgurite**, a rough, sand-crusted, **hollow** glass tube that traces the path of the current through the sand. It is not a clear pane.

One idea, one monotonic counter (temperature, only goes up), one paradox beat (the freeze: same atoms, no order), one big reveal (the cut-away fulgurite), a loop back to the strike.

## Shot plan (as built)
| Time (s) | Shot | On-screen text |
|---|---|---|
| 0.0-1.9 | Night desert, storm clouds; the bolt strikes on frame 0 with return-stroke flickers; slow push-in; the impact point glows orange | Hook typed: "LIGHTNING CAN / **MAKE GLASS.**" |
| 1.9-2.75 | Restrike; the camera dives down the channel into the glowing impact point; zoom-dissolve into the sand | |
| 2.75-4.6 | Macro: translucent quartz grains, violet arcs crawl over them, heat glow grows on one grain; the camera pushes in | Counter "TEMPERATURE 20 °C" climbing; chip QUARTZ SAND |
| 4.3-7.3 | Dissolve into the grain: a silica crystal lattice (gold Si, teal O) seen down its channels, perfect rows; atoms start to shiver | chip QUARTZ CRYSTAL, "ATOMS LOCKED IN NEAT ROWS"; counter to 1,700 °C |
| 7.3-10.45 | Lattice glows orange, shakes, bonds snap, rows dissolve; camera shake | chip THE SAND MELTS, then INSIDE THE BOLT, "50,000 °F · 5× THE SUN'S SURFACE"; counter to 27,700 °C (PEAK) |
| 10.45-11.0 | Held breath (near silence) | |
| 11.0-12.6 | A cold front sweeps across: motion stops, colours cool; a frozen disordered network | chip FROZEN IN A FLASH, "SAME ATOMS. NO ORDER. GLASS." |
| 12.6-14.6 | Pull back out of the glass, ending on the reveal (biggest hit at 13.6) | |
| 13.6-17.2 | Cut-away of the sand: the branching fulgurite under the strike point. Top part shows the rough sandy crust; the lower part is sliced open to show the hollow, glassy channel. A faint ghost of the bolt re-flashes above it | chip FULGURITE, "WHAT LIGHTNING LEAVES IN SAND"; pointers ROUGH, SANDY CRUST / HOLLOW, GLASSY INSIDE; caption "NOT CLEAR GLASS: / A ROUGH, HOLLOW TUBE / SHAPED LIKE THE BOLT." |
| 17.2-19.5 | The camera rises out of the trench back to the storm view; distant cloud flickers | End line typed: "LIGHTNING, / **FROZEN.**" |
| 19.45-20.0 | Stepped leader descends; frame 0 is the strike (loop) | |

"THOUGHT EXPERIMENT · NOT TO SCALE" is on screen throughout (the atom zoom and the tube thickness are exaggerated).

Design notes: new hero objects (no Sun, galaxy or ring motif from earlier reels); camera-facing ribbon lightning; red only for chips and pointer markers; no white-outs (overlay flash capped at 8%).

## Facts and sources
| Claim on screen | Source |
|---|---|
| Lightning heats the air it passes through to about 50,000 °F (about 27,700 °C), roughly 5× the surface of the Sun | NOAA National Weather Service, "How hot is lightning?" https://www.weather.gov/safety/lightning-temperature |
| Peak channel temperatures exceed 30,000 K | Wikipedia, "Fulgurite" https://en.wikipedia.org/wiki/Fulgurite |
| Sand (quartz / silica) melts at around 1,700 °C (cristobalite melts at 1,713 °C; fulgurites form above about 1,800 °C) | Institute of Making materials library, "Fulgurite" https://www.instituteofmaking.org.uk/materials-library/library/fulgurite (above 1800 °C); cristobalite melting point, standard reference value |
| Fulgurites are generally hollow, branching glass tubes; inside smooth or lined with bubbles, outside rough and crusted with sand | Wikipedia, "Fulgurite"; Utah Geological Survey, https://geology.utah.gov/fulgurites-when-lightning-strikes-sand-magic-is-formed ; Institute of Making |
| The glass is lechatelierite, amorphous silica (no crystal order) | Wikipedia, "Lechatelierite" https://en.wikipedia.org/wiki/Lechatelierite |
| Not clear glass: most natural fulgurites range from white to black, iron can tint them brown-green | Wikipedia, "Fulgurite" |

Simplifications, stated here so the copy stays honest:
- The lattice is drawn as an idealised silica network (cristobalite-like diamond net), not the exact alpha-quartz cell. Labelled not to scale.
- The counter is "temperature in the strike": the 1,700 °C stop is the sand, the 27,700 °C peak is the air in the bolt channel (that is why the label says INSIDE THE BOLT). Sand at the centre of the channel vaporises, which is why the tube is hollow.

## Sound
v2 (current): hero effects generated with ElevenLabs Sound Effects (`eleven_text_to_sound_v2`, files in `tools/frozen-lightning/sfx/`): a close lightning strike with thunder (frame 0, and its crack again on the 1.92 s restrike), a long thunder roll, high-voltage electric arcing (grains and bolt phase), a furnace blast (melt at 7.3 s), a glass freeze snap (11.0 s) and a deep cinematic boom (reveal at 13.6 s, the biggest hit). They sit on top of the numpy-synthesised beds from v1 (rain and wind, sand hiss, crystal ticks, heat roar, warm drone, glass bells, loop crackle) in `mix_frozen.py`. About -15 LUFS integrated, true peak -4.4 dBTP after AAC.
Licence: generated on Teja's ElevenLabs account; no third-party credit needed. Check that the account's plan covers commercial use before a monetised upload.

v2 visual changes: closer opening camera with a thicker, more branched channel, lit clouds, wet-sand sheen, a spray of molten sparks, a dust shockwave and rain; a visible stepped leader in the last half-second so the loop lands on the strike; arcs on the sand grains drawn as real lightning ribbons; a current pulse racing down the fulgurite on the reveal; moving light on the glass; a grainier sand face.

## Rebuild
```
cd tools/frozen-lightning
npm i three@0.170.0 playwright-core@1.56.0     # or symlink an existing node_modules
python3 -m http.server 8777 &
NODE_PATH=./node_modules node render.js 720 1280 <frames> 0 600 1 8777   # or 4 interleaved workers: start 0..3, step 4
python3 mix_frozen.py frozen_mix.wav
python3 overlay_frozen.py <frames> overlay.mov
ffmpeg -framerate 30 -i <frames>/f%04d.jpg -i overlay.mov -i frozen_mix.wav \
  -filter_complex "[0:v]scale=1080:1920:flags=lanczos,format=rgba[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p[v]" \
  -map "[v]" -map 2:a -c:v libx264 -preset slow -b:v 10M -c:a aac -b:a 192k -movflags +faststart frozen-lightning.mp4
```
`shot.js` renders test stills: `node shot.js 720 1280 <outdir> 8777 0 3.6 9.5 15.5`.

## Publish copy

**YouTube title options**
- Lightning Makes Glass, But Not the Kind You Think ⚡
- What Lightning Leaves Behind in Sand
- Lightning, Frozen in Glass

**YouTube description**
> A lightning bolt heats the air to about 50,000 °F, five times hotter than the surface of the Sun. Where it hits sand, the quartz melts in a fraction of a second and freezes before its atoms can line up again. That is glass, but not a clear pane: it is a fulgurite, a rough, hollow tube shaped like the path the lightning took through the ground.
>
> Thought experiment, not to scale: atoms and the tube are exaggerated so you can see them.
>
> Sources: NOAA National Weather Service (lightning temperature); Utah Geological Survey and the Institute of Making (fulgurites).
>
> Sound: original, synthesised for this video.
>
> #shorts #lightning #science #physics #geology #fulgurite #glass

**Instagram / Facebook caption**
> Lightning really can make glass ⚡ Sand melts around 1,700 °C, the bolt is about 27,700 °C, and the melt freezes so fast the atoms never line up again. The result is a fulgurite: a rough, hollow tube shaped like the bolt. Not clear glass. (Thought experiment, not to scale.)
> #lightning #science #geology #fulgurite #physics #reels

**Pinned comment**
> Fulgurites can be metres long. The longest reported pieces are around 5 m. Would you dig one up?

Upload checklist: AI/synthetic content label on; check true peak after encoding (done for the delivered file).
