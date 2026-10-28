# You Were Blind for 20 Minutes Today (28 Oct 2026)
19 s wordless reel. **V2 (current, `scene_dark.js`)**: Slow Light Dark look (void, one lamp beam with dust, mirror floor, cream capsule stickman from `sld.js` with two eye dots), each moment of his day staged in the same pool of light, wide cameras; then an eye macro and a neural field. Teja asked for this full-dark tone for this reel only. V1 (`scene.js`, dark-warm flat with the clothed figure) is kept but no longer loaded by `index.html`.
The eye macro (12.0–13.8 s) is `eye.js` (`buildEye`), rebuilt when Teja asked for a highly accurate eye. It has a 2048² iris texture (limbal ring, radial fibres, collarette, crypts, furrows, gold flecks, pupil ruff), sclera vessels and corner shade, a clear cornea cap with an env-map catchlight, and one skin height field. Lid margins are placed by true distance to two polylines, so there are no seams. Lids roll onto the globe and drape over the cornea, so a shut lid fully hides it. It also has a crease, instanced curved lashes and brow hairs, a caruncle, a tear meniscus and an upper-lid contact shadow. Re-render just that shot with `EDIT=output/eye_edit.json FORCE=1` (segments [[360,414]]).

Every blink is a pair of screen-space eyelids in the grade pass (`uLid` in `sld.js` / `stage.js`); his eye dots close with them, except in the mirror shot.

Render: `npm i`, then two workers `OUT=DIR SUB=3 node render.cjs frames W 2 19 30` (W=0,1; about 35 min on 4 CPUs; more workers are slower because SwiftShader already uses every core).
Text: `python3 overlay.py check` (counter monotonic), `python3 overlay.py frames DIR/frames DIR/comp`.
Sound: `python3 mix.py DIR/mix.wav`; mux with `sld_sound.master_to_mp4` (-15 LUFS).
