# The Thing In Your Room: three.js nightmare scene (v2)

A 20 s, 1080x1920, wordless and silent vertical take for **SLOW LIGHT: THE THING IN YOUR ROOM**. Typography and sound are added later in the edit. It is a separate build from the earlier five-second opening test in `../src` and leaves that code untouched.

## Run

From `tools/sleep-paralysis` (it reuses that folder's `node_modules`: three 0.170, playwright-core), with Chrome and ffmpeg installed:

```sh
npm ci
cd nightmare
node shot.mjs /tmp/stills 1080 1920 0.3 5.4 9.4 13.6 16.9           # stills
node shot.mjs /tmp/dbg 540 960 5 --q "solo&nofog&cam=0.6,1.7,0.2&look=-1.8,1.6,-2&fov=62"   # debug views
node render.mjs /tmp/frames 60                                       # 1200 JPEG frames at 60 fps
ffmpeg -framerate 60 -i /tmp/frames/f%05d.jpg -vf "tmix=frames=2,fps=30,format=yuv420p" \
  -c:v libx264 -crf 18 -preset slow -movflags +faststart thing_in_your_room_v2.mp4
```

Rendering at 60 fps and blending pairs down to 30 fps gives a 1/60 s shutter (motion blur without ghosting). On the 2019 MacBook Pro (Metal) a full pass takes about 4 minutes.

## Shot plan (one continuous take, `timeline.js`)

| Time | Shot |
|---|---|
| 0-0.5 | Ink recedes from the frame edges (loop seam). Low angle from the pillow: the sleeper's face lower left, the wraith bowed over the bed upper right, barred moonlit window. |
| 0.55-0.85 | The sleeper's eye snaps open. |
| 0.2-5 | Crown branches grow across the ceiling; the head tilts 7 degrees toward the sleeper. |
| 3.6-9.4 | Deliberate acceleration back and up into the wide room (bed, window, light shaft, the figure beside the bed). |
| 9.4-13.6 | Slow creep back in along the bed. The arm reaches, the fingers unfold, the covered arm tries to lift and fails, and a cloud dims the moon. |
| 13.6-16.9 | Push under the descending hand; crimson pulses strengthen. |
| 16.9-20 | The hand curls into a claw over the face; ink closes in from the edges and the take returns to the frame-0 camera (loop). |

## Build

- `wraith.js`: a rigged figure (pelvis, spine, neck, head, shoulders, elbows, wrists, five three-joint fingers per hand, hips, knees). Every joint is a unit-scale Group, and limbs are bundles of twisted ligament strands around a dark core, with thorny twigs, torn cloth strips and root tendrils on the floor. Crimson filaments carry travelling shader pulses. Branch growth (`aGrow`) and drift (`aSway`) run in the vertex shader, and a matching depth material keeps the shadows in sync.
- `room.js`: real geometry at real depths. Walls with a barred window and an ajar door, a lit corridor, a bed with a faceted blanket over a body (it breathes, and a covered arm tries to lift), a pillow, a nightstand, a lamp, a dresser, a chair, curtains, a dead tree outside, and a sky with the moon. Surfaces use an engraving patch: world-anchored hatching, grain and stipple, so nothing swims on screen.
- `fx.js`: a ray-marched moonlight shaft cut by the window bars, ink flecks, rare tumbling crimson petals, and dust that shows only inside the shaft.
- `post.js`: ink outlines from the luminance gradient, a graphite-to-ivory monochrome grade that keeps crimson, static paper tooth, a vignette, and the fbm ink-bleed used for the loop seam.
- The sleeper's head is the project's own engraved asset `../assets/generated/sleeper-head-hand-atlas-v1.png` (made in an earlier session). It is registered on the pillow with a limited yaw toward the camera, and a canvas-drawn open eye sits on the closed lid. No other image or video generation was used.
