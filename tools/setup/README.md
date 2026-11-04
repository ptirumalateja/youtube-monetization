# Toolkit setup

Cloud sessions start fresh, so run `bash tools/setup/install.sh` at the start of a session that needs these tools (about 2 minutes).

| asked for | installed | what works in the cloud |
|---|---|---|
| hyperframes | heygen-com/hyperframes (npm `hyperframes`) | renders fine; run `hf-gsap.sh <project>` first because jsdelivr is blocked |
| yt-alb | yt-dlp | installs, but youtube.com is blocked here; works on the Mac |
| wishper | Whisper via faster-whisper, base.en model from a GitHub mirror | `transcribe.py audio.mp3 --json words.json` gives word timings |
| openverse | WordPress/openverse API, `openverse.py` (stdlib) | API blocked here; works on the Mac |
| realsfx | vibe-motion/sound (Freesound search/download skill) | freesound.org blocked here; works on the Mac |
| earshot | Leonxlnx/earshot (agent ears: describe, measure, SFX bank, kits) | offline commands (`measure`, `sfx`, `kit`, `forge`) only; CLAP models need HF |
