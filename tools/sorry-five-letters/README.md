# Sorry Is 5 Letters

Slow Light stickman reel in the Silence Is Distance v8 look (same palette, figures, glossy ledge, dust, fonts), 13.6 s.
Two people stand back to back after a fight; SORRY hangs over them as five gold blocks that get heavier each day (DAY 1 -> 30),
until he types it and the giant letters shrink into one small message. Frame 0 = DAY 30 crush, slam at 0.25 s, rewind at 1.35 s.

    export NODE_PATH=$(npm root -g)
    OUT=out TIMES=0,2.4,9 node render.cjs stills
    OUT=out node render.cjs events && python3 mix.py out/events.json out/mix.wav
    for w in 0 1 2 3; do OUT=out node render.cjs frames $w 4 & done; wait   # ~15 s
    ffmpeg -framerate 30 -i out/frames/f%05d.jpg -i out/mix.wav -c:v libx264 -crf 19 -pix_fmt yuv420p -c:a aac -af loudnorm=I=-14:TP=-1.5 -shortest -movflags +faststart out/sorry.mp4

Foley: ElevenLabs (sfx/gen_new.sh for slam/thud/crack/creak/rewind/release; others from tools/silence-distance/sfx).
