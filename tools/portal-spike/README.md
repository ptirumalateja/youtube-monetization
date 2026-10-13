# Portal spike (three.js, CPU render)
`npm i three@0.170.0 playwright-core@1.49.1`, serve this folder (`python3 -m http.server 8765`), then
`node render.js <w> <h> <t0> <t1> <outdir>` renders JPEG frames with headless Chromium (SwiftShader).
Encode with `ffmpeg -framerate 30 -i frames/f%04d.jpg -c:v libx264 -crf 17 -pix_fmt yuv420p out.mp4`.
~19 s to render 6 s at 540x960.
`sfx-drive-ids.txt` lists the Drive IDs of the free sound files (download via `drive.google.com/uc?export=download&id=...` when the folder is link-shared).
