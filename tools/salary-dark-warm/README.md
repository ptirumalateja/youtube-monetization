# Salary Loop, dark-warm reference frame (27 Oct 2026)
One still of The Salary Loop restyled to the "dark but not black" look: one 3000 K table lamp, charcoal/navy room (never #000), 11 pm clock, wooden man alone at the table, calendar day 24.
Reuses `../slow-light-dark-common` / `../parents-aging-v2/sld.js` (copied here with bg/fog/lift/vig options). Needs `npm i` (three) and the playwright chromium.
`node render.cjs still out/raw_after.jpg after '{"p":[-0.05,1.62,3.5],"l":[-0.02,1.38,-0.4]}'` then `python3 -I overlay.py out/raw_after.jpg out/final.jpg after` (use `before` for the payday frame).
Outputs are copied to `downloads/`.
