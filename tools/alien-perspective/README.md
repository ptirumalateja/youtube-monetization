# What Andromeda Sees (Alien Perspective reel)

Slow Light reel, 12.0 s, 1080x1920, 30 fps, wordless, loops. Idea from Meta AI's creator assistant ("If an alien in Andromeda looked at Earth right now, they'd see mammoths"), rebuilt with the fact fixed and a payoff-first edit.

## Fact fix

Andromeda is about 2.5 million light-years away, so light reaching it today left Earth about 2.5 million years ago. Woolly mammoths only appeared about 700,000 to 400,000 years ago and modern humans about 300,000 years ago, so "they'd see mammoths" is wrong as written. At 2.5 million years ago Earth had early human ancestors (early Homo, Australopithecus, Paranthropus) in Africa and the first stone tools (Oldowan, about 2.6 million years). The reel shows an early ancestor holding a hand stone on an African savanna and says "NO MODERN HUMANS YET."

(Earlier mammoth species, such as the southern mammoth, did live in Europe 2.5 million years ago, but not woolly ones; we left mammoths out to keep the line clean.)

## Beats

| Time (s) | Picture | Text |
|---|---|---|
| 0.0-2.3 | Payoff first: early ancestor silhouette on a ridge under a huge Andromeda, frame-0 hit | ALIENS IN ANDROMEDA / SEE EARTH LIKE THIS. + RIGHT NOW chip |
| 2.3-4.6 | Alien eye (slit pupil), Earth reflected in the pupil, push in to the dot | THE LIGHT IN THEIR EYE / LEFT EARTH LONG AGO. |
| 4.6-7.75 | Ride the light beam out from Earth; era panes land one by one; odometer only goes up | THIS LIGHT LEFT EARTH / NOW (CITIES) -> 4,500 YEARS AGO (PYRAMIDS) -> 300,000 YEARS AGO (FIRST MODERN HUMANS) -> 2,500,000 YEARS AGO |
| 8.0-8.55 | Held breath: the last pane (the opening shot) approaches, near silence | |
| 8.6-10.0 | The pane fills the frame: same shot as frame 0, biggest hit | 2,500,000 YEARS AGO / NO MODERN / HUMANS YET. |
| 10.0-12.0 | The ancestor morphs into a modern stargazer (city glow on the horizon), then back to the ancestor = frame 0 | TODAY'S LIGHT GETS THERE / IN 2.5 MILLION YEARS. |

Music drop point for the silent copy: 8.6 s (the reveal hit). Secondary accents: 2.3 s (eye snap), 4.6 s (into the beam).

## Files

- `render.py`: numpy + PIL renderer (ink-wash night look, procedural Andromeda, parallax layers, morphing silhouette rig, procedural alien eye, light-beam flight with era panes, text overlay). `python3 render.py OUTDIR [frames...]`, 4 processes, about 5 min on 4 cores. Asserts the odometer is monotonic.
- `sound.py`: synth layers plus CC0 Freesound files from `tools/sfxlib` (qubodup explosion-from-another-dimension, lucabia sword-in-air, AudioPapkin cinematic woosh 015, stewdio2003 subby whoosh, sleepCircle wind). Circular buffer so the loop is seamless.

## Build

```
python3 render.py OUT/frames
python3 sound.py OUT/mix.wav
ffmpeg -framerate 30 -i OUT/frames/f%04d.png -i OUT/mix.wav -af "loudnorm=I=-15:TP=-2:LRA=11" -c:v libx264 -crf 18 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart what-andromeda-sees.mp4
```
