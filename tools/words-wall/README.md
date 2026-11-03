# Their Words Became His Wall (Slow Light Dark), V2 of They Threw Words

17.5 s, 1080x1920, 30 fps. This is the side-on wall version Teja asked for: the stairs V1 (`../words-to-stairs/`) was too close to One Step a Day. Copy: `publish-copy/their-words-became-his-wall.md`.
The pipeline is the same as `../words-to-stairs/README.md`: npm install, copy the two JetBrains Mono TTFs into `fonts/`, `render.cjs meta|frames|stills`, `mix.py OUT.wav`, `compose.py RENDER OUT`.

- `scene.js`: three slate men on the left and the wall (3 x 4 blocks, word faces toward camera) with him behind it on the right. He catches each block, turns it word-out and sets it in, bottom row first. The red block (held low by the third man from frame 0) smashes into the wall's left end, which shakes along with the camera, and bounces back to land at the men's feet. He rests his hands on top of the wall.
- `voices/`: the shouted insults and laughs, made with Kokoro TTS (free, `voices/make_voices.py`, model files from the kokoro-onnx GitHub release). `mix.py shout()` pitches them down, saturates them and adds a little room.
- `mix.py`: a jeer on each wind-up, a recorded whoosh per throw (Tomlija 175183, CC BY 3.0), catch slaps, stone placements with ember crackle, shuffle steps, mocking laughs, a held-breath duck, then the slam into the wall and the drop. No music.
