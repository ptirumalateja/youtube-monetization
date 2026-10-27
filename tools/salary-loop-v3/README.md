# Salary Loop V3 (19.3 s, 27 Oct 2026)
Story rebuild approved by Teja; the frozen plan is `STORY.md`. One hero (`HERO` in figure.js), three sets (bedroom, street, desk), the phone faces him, every expense is a phone buzz, a tear-off calendar is the only counter. All times live in `timeline.json`.
Rig fixes (sld.js / figure.js): elbow and shoulder limits, a fixed anatomical IK pole, pole blending, mitten hands, bigger face, worry brows instead of the angry V.
Needs `../slow-light-dark-common` (from branch `claude/project-thread-mwvuhi`). `npm i` first.
Stills: `W=1080 H=1920 SUB=2 OUT=output/final TIMES=0,1.5,... node render.cjs stills`, then `python3 overlay_v3.py still IN.jpg T OUT.jpg`.
Frames: `OUT=DIR node render.cjs frames W 4 19.3 30` (four workers W=0..3). Sound mix and compose are not written yet.
