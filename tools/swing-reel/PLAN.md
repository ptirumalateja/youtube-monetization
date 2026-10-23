# Swing reel ("The ball that breaks physics") — paused plan

Status: paused 2026-10-23 before any render (Teja: one reel at a time, stumps reel first).

## Verified physics
- Conventional swing: seam angled ~20-30 deg toward slip; seam side trips the boundary layer to turbulent, which separates later; the shiny side stays laminar and separates earlier. Wake is deflected, ball is pushed toward the side the seam points. Best around 70 mph (~112 km/h, ~31 m/s). (Leeds Beckett; COMSOL blog citing Mehta; BUET ICME07-FL-17)
- Reverse swing: above ~85 mph (~137-140 km/h) or with an old ball, both sides turbulent, ball moves the other way (toward shiny side). (Leeds Beckett; ScienceABC)
- Side force coefficient for new-ball conventional swing about 0.3-0.4 (Cambridge thesis, repository.cam.ac.uk/handle/1810/349081). Plan uses CF 0.2 (conservative).
- Key reveal: a constant sideways push gives sideways drift ~ t^2, so only ~25% of the swing has happened at halfway and ~75% comes in the second half. The ball never "turns"; it curves all the way. Exact share to be taken from the simulation (drag lowers it slightly).

## Shot plan (~23 s, 1080x1920, 30 fps)
- 0-2.2 macro red ball, seam upright, crimson rim light, dark stadium bokeh; hook "WHY DID THIS BALL TURN IN MID-AIR?"
- 2.2-4.6 behind-bowler end-on, silhouette delivery, slow-mo first half of flight
- 4.6-7.6 freeze at halfway, straight dashed line to stumps, monotonic meter "SIDEWAYS SO FAR: ~8 CM"
- 7.6-12.5 second half, meter climbs to ~35 cm, right-hander silhouette beaten outside off
- 12.5-16.5 top-down luminous path vs straight line, quarter markers, "75% OF THE SWING IN THE LAST HALF"
- 16.5-21 top-view airflow: shiny side lets go early, seam side clings, sideways push arrow
- 21-23 "IT NEVER TURNED. IT CURVED ALL THE WAY." loop to macro ball
- Outswinger to a right-hander: off side = screen right in the end-on view.

## Build
three.js r0.170 headless (playwright-core + /opt/pw-browsers chromium), numpy physics sim -> trajectory JSON, PIL overlay, numpy synth sound. Silhouettes from three.js example rigged models (assets/Xbot.glb etc., posed per bone) for correct anatomy.
