# Sit Still System reel ("How Valued Members Of Society Are Made")

Remake of a ref conveyor loop: seated bone figures step along a belt; a mallet arm smashes each lit bulb, a second arm lowers a graduation cap.
- `npm i three@0.170.0` next to scene.html, then `node render.js full "all:0,12.6,30"` (frames, ~20 min swiftshader)
- `python3 synth.py` -> sfx.wav (procedural glass smash, clank, belt, servo, hum; ElevenLabs was unavailable)
- Cycle: T=2.1 s, stop 1.65 s, hit at 1.10 s; 6 cycles = seamless 12.6 s loop.
