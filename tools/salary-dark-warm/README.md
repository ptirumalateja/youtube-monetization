# Salary Loop, dark-warm full reel (27 Oct 2026)
18.5 s, 1080x1920, 24 fps. One dark-warm room (charcoal/navy, one 3000 K lamp, 11 pm clock), wide shot with the wooden man small in frame, loops on the next-month salary notification.
Render: `npm i`, `node render.cjs frames W 4` for W in 0..3 (OUT=dir), `python3 mix.py OUT/mix.wav`, `python3 compose.py OUT OUT/deliver`. About 25 min on 4 CPUs.
Needs `../slow-light-dark-common` (sld_text/sld_sound) and `../salary-loop` (mix helpers) from branch `claude/project-thread-mwvuhi`.
Single stills: `TIMES=3.8 node render.cjs stills`, then `python3 overlay.py still IN.jpg T OUT.jpg`.
