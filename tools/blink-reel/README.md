# You Were Blind for 20 Minutes Today (28 Oct 2026)
19 s wordless reel in the dark-warm look: one studio flat (reading chair, window, desk, bed, wall mirror), an eye macro and a neural field. Every blink is a pair of screen-space eyelids in the grade pass (`uLid` in `stage.js`); the hero blinks with them except in the mirror shot. Stage, figure, rig and set helpers are copied from `tools/salary-loop-dark` (branch `claude/project-thread-oa553s`); `sld_sound.py` from `tools/slow-light-dark-common`.

Render: `npm i`, then four workers `OUT=DIR SUB=3 node render.cjs frames W 4 19 30` (W=0..3, about 40-50 min on 4 CPUs).
Text: `python3 overlay.py check` (counter monotonic), `python3 overlay.py frames DIR/frames DIR/comp`.
Sound: `python3 mix.py DIR/mix.wav`; mux with `sld_sound.master_to_mp4` (-15 LUFS).
