# Inside the Clot v3 plan (paused, resume here)
- Teja (21 Oct): open on a crowd walking, zoom onto one person pressing his chest, then into the heart + clot story; voiceover from frame 0; total under 25 s; hook text on screen from frame 0.
- ElevenLabs refused (429, one try). Stand-in VO: Kokoro TTS (kokoro-onnx, model + voices from the kokoro-onnx GitHub release), voice am_michael, speed 1.0, made per line by `vo.py` (lines: 3.76, 2.68, 1.70, 1.21, 2.49, 3.66, 1.24, 0.97, 3.02 s = 20.7 s). Swap for an ElevenLabs take if Teja sends an MP3.
  espeak data path fix: symlink the espeakng_loader data dir to /home/runner/work/espeakng-loader/espeakng-loader/espeak-ng/_dynamic/share/espeak-ng-data.
- VO starts (video s): 0.15, 4.3, 7.3, 9.9 ("cracks" ~10.75), 11.6, 14.9, 19.0, 20.45, 21.7; video length 24.9 s.
- Video -> scene time warp (monotone cubic): 3.2->0.4, 4.4->2.25 (snap), 9.75->8.6, 10.75->9.3 (crack), 14.4->13.55, 19.0->18.7, 21.6->21.0, 24.9->24.0.
- 0-3.2 s: new crowd world (point-cloud walking figures on a dark wet plaza, bokeh city lights); hero walks toward camera, stops ~1.1 s, right hand to left chest 1.3-1.8 s, gold/red heart glow pulsing through his chest, red ring marker; camera from high-wide to the chest, dive + flash at 3.2 s into the beating heart.
- Overlay: hook "EVERY 40 SECONDS" / "SOMEONE IN THE US" / chip "HAS A HEART ATTACK." from frame 0; other labels driven by scene time.
- Mix: sample masks driven by scene time per sample; events placed through the warp; crowd footsteps + murmur + rising heartbeat 0-3.2 s; duck beds under VO.
