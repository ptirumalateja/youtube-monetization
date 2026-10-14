# sfxlib: sound library used by the mix scripts

Mix scripts in `tools/*/mix*.py` read `LIB="../sfxlib/"`, i.e. this folder (`tools/sfxlib/`).

## What is committed
The 17 Freesound files placed in the final mixes (CC0 or CC BY). Credits: see `/audio-attribution.md`.

## What is NOT committed (re-supply from the user's Google Drive / re-download)
- Uppbeat braams: `braam_bass_drop.mp3`, `braam_long_impact.mp3`, `braam_screaming_echo.mp3` (Scale Ladder v4 sound). Uppbeat terms may forbid redistribution, so they are not in git. Download them again from Uppbeat (free account) or ask the user.
- `gregorquendel_circuits_hum.mp3`, `soundreality_explosion_fx.mp3`: unknown licence, experiments only.
- `248182 hykenfreak transformers-type-sfx-2.wav`, `382249 alexprost moving-effect.wav`: tried, not in any final cut.

## Google Drive
`drive_ids.txt` lists `<Drive file id>  <file name>` for the Freesound files the user keeps in their Google Drive (open with `https://drive.google.com/file/d/<id>/view`, or use the Google Drive connector `download_file_content`). If a file is missing here, look there first.
