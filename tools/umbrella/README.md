# Rain or Shine (checkers vs chess umbrella reel, Slow Light Dark)

Remake of the neuronvisuals "Some people play checkers. Others play chess." reel (Teja, 11 Nov 2026): same composition,
figure sizes (hero 29% of frame height), beats and length (11.8 s), rebuilt in our look with the Slow Light stickman rig,
glossy wet floor, lit pool, red sun. Wordless; only the grey man's HA HA. No music: ElevenLabs foley (sfx/gen.sh).

    npm install
    OUT=out node render.cjs meta
    for w in 0 1 2 3; do OUT=out node render.cjs frames $w 4 & done; wait     # ~60 min on 4 CPUs (SUB=3)
    python3 mix.py out/mix.wav
    python3 compose.py out deliveries
    node calib.cjs "cx=..&ty=.." 0.6,6   # projected head/feet/bowl positions, to match the ref framing

Shared code copied from tools/climb and tools/slow-light-dark-common (branch claude/project-thread-xwz8zt).
