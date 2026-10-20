# Slow Light: audio attribution (per file, ready to paste)

Source for every file: Freesound unless stated. "Changes were made" applies to all of them: the sounds were trimmed, layered, pitch/time-processed and mixed with other sounds.
Rule: CC0 needs no credit; CC BY needs a credit line plus the change notice; CC BY-NC is never used. Check this file whenever a sound is added or swapped.

## 1. Files that REQUIRE a credit (CC BY)

Paste the exact line into the description of any reel that uses the file.

| File | Used in | Paste-ready credit line |
|---|---|---|
| 849772 Electric Sparks | Night Sky, Scale Ladder | "Electric Sparks" by mikiko850, https://freesound.org/people/mikiko850/sounds/849772/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) |
| 19487 JacobsLadderSingle2.flac | Night Sky only | "JacobsLadderSingle2.flac" by Halleck, https://freesound.org/people/Halleck/sounds/19487/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) |
| 175183 5 Everyday Whooshes | Night Sky only | "5 Everyday Whooshes" by Tomlija, https://freesound.org/people/Tomlija/sounds/175183/ , CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/) |
| 115555 synth_jet.wav | Night Sky, Scale Ladder | "synth_jet.wav" by vartioh, https://freesound.org/people/vartioh/sounds/115555/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) |
| 722633 Cinematic Sound Braaam Sample (Chakongaudio, Brass, Trailer) | Scale Ladder only | "Cinematic Sound Braaam Sample (Chakongaudio, Brass, Trailer)" by chakong, https://freesound.org/people/chakong/sounds/722633/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/) |

### Description block: Night Sky
> Sound credits (from Freesound). Changes were made: the sounds below were trimmed, layered, pitch/time-processed and mixed with other sounds. All other sounds used are CC0.
> - "Electric Sparks" by mikiko850, https://freesound.org/people/mikiko850/sounds/849772/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
> - "JacobsLadderSingle2.flac" by Halleck, https://freesound.org/people/Halleck/sounds/19487/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
> - "5 Everyday Whooshes" by Tomlija, https://freesound.org/people/Tomlija/sounds/175183/ , CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/)
> - "synth_jet.wav" by vartioh, https://freesound.org/people/vartioh/sounds/115555/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

### Description block: Scale Ladder
> Sound credits (from Freesound). Changes were made: the sounds below were trimmed, layered, pitch/time-processed and mixed with other sounds. All other sounds used are CC0.
> - "Electric Sparks" by mikiko850, https://freesound.org/people/mikiko850/sounds/849772/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
> - "synth_jet.wav" by vartioh, https://freesound.org/people/vartioh/sounds/115555/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)
> - "Cinematic Sound Braaam Sample (Chakongaudio, Brass, Trailer)" by chakong, https://freesound.org/people/chakong/sounds/722633/ , CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/)

### Short form (Instagram / Facebook caption)
- Night Sky: "Sound: mikiko850, Halleck, Tomlija and vartioh via Freesound (CC BY 4.0 / 3.0), changes made (trimmed, layered, processed), plus CC0 sounds. Full credits on YouTube."
- Scale Ladder: "Sound: mikiko850, vartioh and chakong via Freesound (CC BY 4.0), changes made (trimmed, layered, processed), plus CC0 sounds. Full credits on YouTube."

## 2. CC0 files (no credit required; optional courtesy line)

| File | Author | Used in |
|---|---|---|
| 814046 Explosion From Another Dimension | qubodup | Night Sky, Scale Ladder |
| 814047 Fantasy Implosion | qubodup | Night Sky, Scale Ladder |
| 869757 Dark Suspense Accent | mikiko850 | Night Sky, Scale Ladder |
| 850262 Orbiting Plasma Burst and Trail FX | CVLTIV8R | Night Sky, Scale Ladder |
| 822420 Riser Hit sfx 120 | AudioPapkin | Night Sky, Scale Ladder |
| 22331 wind.ogg | sleepCircle | Night Sky, Scale Ladder |
| 276871 Sword In Air | lucabia | Night Sky only |
| 768664 portal gate opening | berkup | Night Sky only |
| 735062 Fast Warp In | GammaGool | Night Sky only |
| 752034 Sci-Fi Gateway | Bachsambora | Night Sky only |
| 649445 Cinematic Woosh SFX-015 | AudioPapkin | Night Sky only |
| 238375 CP_Subby_Whoosh | stewdio2003 | Night Sky only |

Optional courtesy line: "CC0 sounds by qubodup, mikiko850, CVLTIV8R, AudioPapkin, sleepCircle, lucabia, berkup, GammaGool, Bachsambora and stewdio2003 via Freesound." (Trim to the authors of the reel you are posting.)

## 3. Non-Freesound files: verify before a monetised upload

| File | Origin | Used in | Status |
|---|---|---|---|
| Uppbeat braam bass drop / long impact / screaming echo (Tomas Herudek / The Foundation / Epic Stock Media) | Uppbeat free SFX | Scale Ladder | Credit not required for SFX per the Uppbeat help centre, but terms change: re-check the current Uppbeat licence before uploading. |
| Circuits-hum and explosion files shared later in chat | Unknown source/licence | Experiments only | Not in the final cuts. Confirm origin and licence before using. |

Everything else in both mixes is synthesised in numpy (sub hits, braaam layers, choir pad, pings, risers, whooshes, ticks) and needs no credit.

## 4. Not used in the final cuts

- hykenfreak Transformers SFX: not in either final mix; no credit needed unless it is added later (check its licence first).
- No CC BY-NC file is used anywhere.

## 5. Checklist when sound changes

1. Open the reel's `mix_*.py` and grep for the files actually placed.
2. Update the tables above (add or remove the credit lines).
3. Update the matching `*-publish-copy.md` credit block and its licence table.
4. Keep "Changes were made" in the block.

## 6. The Ball That Never Falls

No third-party audio. Every sound (heartbeat, drone, creaks, hits, riser, loop tone) is synthesised in `tools/ball-never-falls/mix.py`, so no credit line or licence entry is needed.

## 7. The Shadow That Stops Copying

No third-party audio. Every sound is synthesised in `tools/shadow-stickman/mix.py`; no credit line or licence entry is needed.
