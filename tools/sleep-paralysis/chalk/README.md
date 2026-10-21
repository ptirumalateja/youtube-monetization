# Sleep Paralysis reel v3: chalk stickman horror

A 20 s, 1080x1920, 30 fps vertical reel in the chalk-on-black stickman style of the user's reference clip. It has a "SLEEP PARALYSIS" title from frame 0, an ElevenLabs voiceover (voice "Max - Deep and Crisp Voice", eleven_v4) and word-synced captions.

Palette: black, chalk white, cold moonlight blue (#9cc3e6), and blood red (#d3141c) for the figure, key words and the "1 IN 10" stamp.

## Beats (all timed from `audio/vo_timestamps.json`; the voiceover starts at +0.35 s)
1. "You wake up… but you can't move." The kid's eyes snap open, he jolts, and his hand twitches.
2. "And something is standing in your room." The camera pulls back to a tall branch-crowned figure with red ember eyes.
3. "This is sleep paralysis." A push into the terrified face (sweat, red veins).
4. "Your brain wakes up, but your body is still locked in dream sleep." A thought-bubble brain with sparks, then chains and a red padlock across the body.
5. "So the dream spills into your bedroom." Scribble smoke pours from a dream cloud into the figure, which glides to the bed and dims the moon.
6. "Some people even see a figure." It leans over the bed and reaches; the camera shakes.
7. "Nearly one in ten people will feel this at least once." A pull-back to ten bedrooms with the red-ringed one and a "1 IN 10" stamp.
8. A rush back into the bed, then a black blink that loops to frame 0.

Fact basis: a lifetime prevalence of about 7.6% in the general population (Sharpless and Barber 2011), so "nearly one in ten". Sensed or seen intruders are common in sleep paralysis but not universal ("some people").

## Rebuild (from this folder, with Chrome and ffmpeg)
```sh
node shot.mjs /tmp/stills 1080 1920 1 5 9.5 12.9 15.6 17.5       # stills
node render.mjs /tmp/frames 30                                    # 600 frames
python3 sfx.py .                                                  # original synthesised sound bed -> audio/sfx_bed.wav
# mix: see the ffmpeg line in the thread / below
ffmpeg -i audio/vo_sleep_paralysis.mp3 -i audio/sfx_bed.wav -filter_complex "[0:a]aresample=48000,adelay=350|350,apad=whole_dur=20,highpass=f=70,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,volume=2.2,asplit=2[vo][sc];[1:a]volume=0.55,highpass=f=40[bed];[bed][sc]sidechaincompress=threshold=0.04:ratio=5:attack=20:release=300[duck];[vo][duck]amix=inputs=2:duration=longest:normalize=0,atrim=0:20,afade=t=out:st=19.8:d=0.2,loudnorm=I=-15:TP=-1.5:LRA=11" -ar 48000 -ac 2 mix.wav
ffmpeg -framerate 30 -i /tmp/frames/f%05d.jpg -i mix.wav -c:v libx264 -crf 20 -preset slow -pix_fmt yuv420p -c:a aac -b:a 192k -t 20 -movflags +faststart out.mp4
```
Audio: the voiceover was generated with ElevenLabs. Every sound effect is synthesised locally in `sfx.py`, with no samples, so there are no licence credits. The mix measures -15 LUFS integrated with a -4.4 dBFS peak.
