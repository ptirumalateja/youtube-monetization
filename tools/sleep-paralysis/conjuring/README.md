# Sleep Paralysis reel v4: Conjuring cut

This is a 20.6 s, 1080x1920, 30 fps vertical horror reel. It reuses the three.js bedroom, the rigged branch wraith and the sleeper asset from `../nightmare/`. It relights and regrades them: a candle, a 3:00 clock, sick teal moonlight, red eyes, film grain and a red heartbeat throb. The take is cut into ten shots keyed to the ElevenLabs voiceover, and the figure is closer on every cut. The title and the word-synced captions are drawn over the graded frame.

- `timeline.js`: the cut list, the figure's position per cut, candle, eye and heartbeat curves. All times are derived from `audio/vo_v4_timestamps.json` (the voiceover sits at +0.2 s).
- `main.js`: scene dressing, lights, props and the per-frame update.
- `grade.js`: the colour grade, grain and vignette.
- `overlay.js`: the title, captions and the final eyes in the dark.
- `sfx.py`: the locally synthesised sound bed.
- `fonts/`: Cinzel 900 and Oswald 700 from Fontsource, under the SIL Open Font License.

## Rebuild (from `tools/sleep-paralysis`, after `npm ci`)
On macOS with Chrome, the defaults work. On Linux, the cloud, or headless setups without a GPU, set:
```sh
export CHROME_PATH=/path/to/chrome GL_ARGS="--use-angle=swiftshader --enable-unsafe-swiftshader"
```
Then:
```sh
cd conjuring
node shot.mjs /tmp/stills 540 960 1.2 7.6 10.6 14 17.2 19.3        # stills
node render.mjs /tmp/frames 30 0 310 & node render.mjs /tmp/frames 30 310 618   # 618 frames, two processes
python3 sfx.py .                                                      # -> audio/sfx_bed.wav
ffmpeg -i audio/vo_v4.mp3 -i audio/sfx_bed.wav -filter_complex "[0:a]aresample=48000,adelay=200|200,apad=whole_dur=20.6,highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,volume=2.2,asplit=2[vo][sc];[1:a]volume=0.6,highpass=f=30[bed];[bed][sc]sidechaincompress=threshold=0.05:ratio=4:attack=20:release=250[duck];[vo][duck]amix=inputs=2:duration=longest:normalize=0,atrim=0:20.6,loudnorm=I=-14:TP=-1.5:LRA=11" -ar 48000 -ac 2 mix.wav
ffmpeg -framerate 30 -i /tmp/frames/f%05d.jpg -i mix.wav -c:v libx264 -crf 19 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -t 20.6 -movflags +faststart sleep-paralysis.mp4
```
With SwiftShader on 4 CPU cores, a full-resolution frame takes about 6 to 10 s.
