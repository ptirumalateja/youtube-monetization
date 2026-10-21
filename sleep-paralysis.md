# Sleep Paralysis: "The Thing In Your Room" (v4, Conjuring cut)

**Final reel:** `final-reels/sleep-paralysis.mp4` in the project files. It runs 20.6 s at 1080x1920 and 30 fps, encoded as H.264 (11 Mb/s, about 28 MB) with AAC audio, mixed to -15.6 LUFS with a -3.8 dBFS peak. Videos are kept in the project folder and are not committed to git.
**Source:** `tools/sleep-paralysis/conjuring/` (v4, this cut). It reuses the 3D bedroom, the rigged branch wraith and the sleeper asset from `tools/sleep-paralysis/nightmare/` (v2). The rebuild steps are in the folder's README.
**Earlier versions:** v2 was a wordless engraved three.js take, and v3 (`tools/sleep-paralysis/chalk/`) was a chalk stickman explainer. The owner rejected v3 because it felt funny rather than frightening, and asked for a Conjuring-style look with a story that stays intimidating to the end.

## Concept
It's 3 A.M. You wake up and can't move or scream, and something is standing in the corner. The reel names it, sleep paralysis, then never lets the viewer off the hook. On every cut the figure is closer, and the line ends with "Don't... open your eyes" as it lunges into the lens. Then it hard cuts to black, and two eyes open in the dark.

**Look:** a dark 3D bedroom with stained 1970s wallpaper, varnished wood, and a dying candle beside a red 3:00 clock. Sickly green-teal moonlight comes through a barred window, and a branch-bodied wraith has red ember eyes. The grade uses a filmic curve with drained colour, keeping only reds and the candle's warmth, plus teal-lifted blacks, heavy moving film grain, lens fringing, a crushing vignette and a red throb on every heartbeat.

**Text:** "SLEEP PARALYSIS" (Cinzel, distressed, with a blood-red glow) is large from frame 0, then pinned to the top for the whole reel. Captions in Oswald are word-synced to the voiceover, with the key words in blood red.

## Cut list (voiceover starts at +0.2 s; cuts come from `audio/vo_v4_timestamps.json`)
| Time | Voiceover | Picture |
|---|---|---|
| 0.00–1.96 | "It's 3 A.M." | The title is centred. The clock beside the guttering candle flips from 2:59 to 3:00 on "3". |
| 1.96–4.52 | "You wake up... and you can't move." | A close-up of his face. The bloodshot eye snaps open on "wake". |
| 4.52–6.10 | "You can't scream." | Tighter, tilted and trembling. |
| 6.10–8.91 | "Something is standing in the corner of your room." | His point of view across the dark room. A slow zoom finds the far corner, and the red eyes ignite on "corner". The heartbeat starts. |
| 8.91–11.28 | "Doctors call it sleep paralysis." | A high wide shot. It has crossed half the room. |
| 11.28–14.57 | "Your mind wakes up... but your body stays asleep." | A wide shot past the bed. It is at the foot now, and his covered arm tries to lift and fails. The candle gutters. |
| 14.57–16.44 | "And every second you're trapped..." | Low beside the pillow, looking up past his face at it. Heartbeat push-ins. |
| 16.44–17.87 | "it comes closer." | From the pillow: it glides in and bends over the bed. |
| 17.87–18.61 | "Don't..." | The candle is snuffed. Only its eyes remain, right above him. |
| 18.61–19.75 | "open your eyes." | It lunges into the lens with an accelerating shake. Hard cut to black as the line ends. |
| 19.75–20.60 | (silence) | Black. Two red eyes open in the dark, then the reel loops to the title. |

## Facts
- Sleep paralysis is REM-sleep muscle atonia persisting into wakefulness while the mind is awake. That is the basis for "your mind wakes up, but your body stays asleep".
- Sensing or seeing an intruder is a common hallucination during episodes (Sharpless & Barber, 2011, *Sleep Medicine Reviews* 15(5):311–315; lifetime prevalence about 7.6% in the general population).

## Audio
- **Voiceover:** ElevenLabs, voice "Max - Deep and Crisp Voice" (eleven_v4), `tools/sleep-paralysis/conjuring/audio/vo_v4.mp3` (19.51 s). Word times are in `vo_v4_timestamps.json`, from ElevenLabs Scribe.
- **Sound effects:** all synthesised locally by `conjuring/sfx.py` (numpy, no samples), so no licence credits are needed. The bed has:
  - a sub drone with a minor-second cluster
  - clock ticks and a 3:00 beep
  - bowed-metal screeches on the eye opening and the ignition
  - impacts on every closer cut
  - an accelerating heartbeat
  - breathy whispers
  - a candle snuff and a drop to near silence
  - a rising scream into the lunge, cut dead on black
  - a sub thud when the eyes open in the dark
- **Mix:** the voice is compressed and the bed is side-chain ducked under it.

## Publish copy
**YouTube Shorts title:** It's 3 A.M. Don't Open Your Eyes 😨 #sleepparalysis
**Alternative title:** Something Is Standing In The Corner Of Your Room

**Description:**
It's 3 A.M. You wake up, but you can't move. You can't scream. And something is standing in the corner of your room.
Doctors call it sleep paralysis: your mind wakes up, but your body is still locked in REM sleep, and the dream spills into the room.
Has it happened to you? 👇
Source: Sharpless & Barber (2011), Sleep Medicine Reviews.
#sleepparalysis #horror #scary #creepy #3am #psychology #sleep #remsleep #slowlight #shorts

**Instagram / Facebook caption:**
It's 3 A.M. You can't move. You can't scream. Something is in the corner. 👁️👁️
This is sleep paralysis. Don't open your eyes.
Ever had it? 👇
#sleepparalysis #horror #creepy #3am #scarystories #psychologyfacts #slowlight

**Pinned comment:** Sleep paralysis isn't dangerous and usually passes within seconds to a couple of minutes. If it happens often or disturbs your sleep, talk to a doctor.

**Upload checks:**
- Turn on the platform's AI or synthetic content label, because the voice is AI-generated.
- Thumbnail: frame 0 (title over the 3:00 clock and candle) or the red eyes in the corner at 7.6 s.
- It loops from the black eyes back to the title.
