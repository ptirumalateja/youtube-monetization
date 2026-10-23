# Black hole reel v3 (Google Flow clips)

11.2 s, 1080x1920, 24 fps. Made from Teja's Veo 3 clips (Google Flow) and the prompts in `black-hole-flow-prompts.md`. There are four 2.8 s beats with hard cuts, and the last beat cuts straight back to the first, so it loops. Edit script: `tools/black-hole-flow/cut.sh` + `sound3.py`.

## Files
- `black-hole-flow_text.mp4`: hook "NOTHING ESCAPES THIS." over the first 2.6 s, with sound
- `black-hole-flow_notext.mp4`: no text, with sound
- `black-hole-flow_silent.mp4`: text version with no audio, for a trending sound
- `black-hole-flow_master.mp4`: high-bitrate (CRF 14) text version, no audio
- `black-hole-flow_contact_2fps.jpg`

## Edit
| Time | Clip | Window used |
|---|---|---|
| 0.0-2.8 | Blade (`...133545`) | 0.4-3.2 s |
| 2.8-5.6 | Galaxy reveal (`...133956`) | 0.0-2.8 s |
| 5.6-8.4 | Saturn ring (`...133756`) | 0.0-2.8 s |
| 8.4-11.2 | Vortex with debris (`...133844`) | 4.2-7.0 s |

I left out the landscape clip (`...133458`). In the ring clip, everything after about 4 s turns into scribbly strands; in the galaxy clip the disk lines get messy after about 6 s.

Grade: slight contrast and saturation lift, gamma 0.97, fine temporal grain.

## Sound
Synthesised bed (`sound3.py`), nothing to credit. Drone, wind and glass, with a sub swell on frame 0 and on each cut. -16.7 LUFS, -3.1 dBTP after AAC.

## Notes
- The Veo/Gemini sparkle watermark is still in the bottom-right corner. I left it in on purpose: it marks the clip as AI-generated.
- Label as AI/synthetic content on upload.

## Publish copy
- **Title:** Nothing escapes this 🕳️
- **Caption:** Four views of a black hole: the blade, the galaxy, the ring and the fall. Which one would you want to see in real life?
- **Tags:** #blackhole #space #universe #cosmos #astrophysics #interstellar #shorts
