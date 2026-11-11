# Silence Is Distance

Canvas-2D stickman remake of the "texts first / waits" split-screen reel (Slow Light look: warm gold top story, cool lonely bottom story, glossy ledges).

    export NODE_PATH=$(npm root -g)
    OUT=out node render.cjs stills                      # review stills
    OUT=out node render.cjs events                      # sound cues
    for w in 0 1 2 3; do OUT=out node render.cjs frames $w 4 & done; wait   # ~20 s
    python3 mix.py out/events.json out/mix.wav
    ffmpeg -framerate 30 -i out/frames/f%05d.jpg -i out/mix.wav -c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -af loudnorm=I=-14:TP=-1.5 -shortest -movflags +faststart out/silence-is-distance.mp4

Layout copies the reference's 720x1280 design space (figure heights, ledge positions, label/counter placement), scaled to 1080x1920.
Foley: ElevenLabs sound effects (`sfx/gen.sh`).
