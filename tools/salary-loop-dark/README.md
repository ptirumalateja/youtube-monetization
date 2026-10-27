# Salary Loop V2, dark-warm visuals (27 Oct 2026)
The original Salary Loop V2 (bed, bell, rent, bank, market, pump, bills, food, office, back to bed) with only the visuals changed: charcoal/navy rooms (never #000), warm practical lamps, night street and office (no morning light), wide cameras (`WIDE=2.5`) so he is small in the room, office keeps its full 5 s so the calendar flips slower.
Render: `npm i`, then four workers `XF=0 WIDE=2.5 EDIT=edit.json OUT=DIR node render.cjs frames W 4 20 30` (W=0..3, about 35 min on 4 CPUs), `python3 mix.py DIR/mix.wav`, `python3 compose_v2.py DIR DIR/deliver`.
Needs `../slow-light-dark-common` and `../salary-loop` (from branch `claude/project-thread-mwvuhi`).
