# Sleep Paralysis: "The Thing In Your Room"

**Final reel:** `final-reels/sleep-paralysis.mp4`. It runs 20.0 s at 1080x1920 and 30 fps, encoded as H.264 with AAC audio. It is about 13.8 MB and mixed to -15 LUFS integrated. Videos are kept locally and are not committed to git.
**Earlier visuals-only version, kept for reference:** `final-reels/sleep-paralysis-nightmare-visuals-v2.mp4`. This is the 20 s three.js engraved-nightmare take, which has no text and no audio. The owner replaced it with v3 because it felt too still and had no story.
**Source:** `tools/sleep-paralysis/chalk/` (v3, the final cut) and `tools/sleep-paralysis/nightmare/` (v2). Rebuild steps are in each folder's README.

## Concept
You wake up and can't move, and something is standing in your room. The reel explains it in 20 s. Your brain wakes up, but your body is still in REM sleep with the muscles switched off. The dream leaks into the room, some people see a figure, and nearly 1 in 10 people will have it at least once.

The style follows the owner's chalk stickman reference clip: chalk white on pitch black, with scribble-hatched blocks and a big-eyed stickman. The horror palette adds cold moonlight blue and blood red for the figure, the key words and the "1 IN 10" stamp.

## Shot plan (timed from the voiceover word timestamps; the voiceover starts at +0.35 s)
| Time | Voiceover | Picture |
|---|---|---|
| 0.0–3.0 | "You wake up… but you can't move." | Title slams in. The kid's eyes snap open, he jolts, and his fingers twitch on the blanket. |
| 3.5–5.8 | "And something is standing in your room." | The camera pulls back. A tall branch-crowned figure with red ember eyes stands by the door. The title shrinks to the top. |
| 6.3–8.1 | "This is sleep paralysis." | A push into his face, with sweat and red veins in his eyes. |
| 8.3–12.0 | "Your brain wakes up, but your body is still locked in dream sleep." | A thought-bubble brain sparks awake. Chains wrap the blanket and a red padlock snaps shut. |
| 12.0–14.3 | "So the dream spills into your bedroom." | Scribble smoke pours from a dream cloud into the figure, which glides to the bedside. The moon dims. |
| 14.5–16.3 | "Some people even see a figure." | It leans over him and reaches its claws toward his face. The camera shakes. |
| 16.3–19.4 | "Nearly one in ten people will feel this at least once." | A pull-back to ten bedrooms. His is ringed in red, and "1 IN 10" is stamped on screen. |
| 19.4–20.0 | (silence) | A rush back into his bed, then a black blink that loops to frame 0. |

## Facts and sources
- **Prevalence.** A systematic review of 35 studies (Sharpless & Barber, 2011, *Sleep Medicine Reviews* 15(5):311–315) found these lifetime rates:
  - about 7.6% in the general population
  - 28.3% in students
  - 31.9% in psychiatric patients

  The reel says "nearly one in ten", not "one in five".
- **Mechanism.** Sleep paralysis is REM-sleep atonia persisting into wakefulness, while REM dream imagery intrudes into a waking mind. This is the basis for "brain wakes up, body still locked in dream sleep".
- **Sensed or seen intruders** are a common hallucination type during episodes, but not universal. The reel says "some people even see a figure" for that reason.

## Audio
- **Voiceover:** ElevenLabs, voice "Max - Deep and Crisp Voice", model eleven_v4, generated in the project on 2026-10-21. Files are `tools/sleep-paralysis/chalk/audio/vo_sleep_paralysis.mp3` and `vo_timestamps.json`.
- **Sound effects:** title slam, eye tick, figure boom, accelerating heartbeat, padlock snap, swells and drone. All are synthesised locally by `tools/sleep-paralysis/chalk/sfx.py`, with no samples, so no licence credits are needed.
- **Mix:** the bed is side-chain ducked under the voice. It measures -15 LUFS integrated with a -4.4 dBFS peak.

## Publish copy
**YouTube Shorts title:** You Wake Up… But You Can't Move 😨 #sleepparalysis
**Alternative title:** The Thing Standing In Your Room (Sleep Paralysis Explained)

**Description:**
You wake up. You can't move. And something is standing in your room.
That's sleep paralysis: your brain wakes up, but your body is still locked in REM (dream) sleep, so the dream spills into your bedroom. Nearly 1 in 10 people will feel it at least once.
Has it happened to you? Tell us below. 👇
Source: Sharpless & Barber (2011), Sleep Medicine Reviews.
#sleepparalysis #sleep #psychology #science #horror #creepy #brain #remsleep #slowlight #shorts

**Instagram / Facebook caption:**
You wake up… but you can't move. 😶 Something is standing in your room.
This is sleep paralysis: your brain is awake, but your body is still locked in dream sleep. Nearly 1 in 10 people will feel it at least once.
Ever had it? 👇
#sleepparalysis #psychologyfacts #brainfacts #creepy #horrortok #sciencefacts #slowlight

**Pinned comment:** Sleep paralysis isn't dangerous, and it usually passes in seconds to a couple of minutes. If it happens often or disturbs your sleep, talk to a doctor.

**Upload checks:**
- Turn on the platform's AI or synthetic content label, because the voice is AI-generated.
- Keep the first frame as the thumbnail: the title with the sleeping kid.
- It loops cleanly through the black blink.
