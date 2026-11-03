# The Sun's Shield (the heliosphere, from the galaxy down to Earth)

| | |
|---|---|
| Status | **FROZEN: v15 final (3 Nov 2026), approved by Teja.** Not posted yet: post only on his go-ahead. |
| Upload file | `slowlight_heliosphere_FINAL_v15.mp4` (project files; also sent in the chat) |
| Length | 26.13 s, 1080x1920, 30 fps, H.264 + AAC |
| Voice | None (captions + sound design) |
| Loudness | -17.1 LUFS integrated, true peak -1.0 dBFS (measured on the AAC file) |
| Build | `tools/heliosphere/` (README has the scene map and render commands) |

## Version notes
- v1-v7: heliosphere + planets + black hole backdrop; judged "still-image slow" and the planet/Sun motion was wrong.
- v8: rebuilt movement from the reference reel (Sun leads, planets follow in long helices, side-on camera, world-fixed galaxy).
- v9: orbits about 1.9x faster, 1.3x speed-up (34 s -> 26 s).
- v10-v11: synthetic pad (too strong) then softer; v12-v13: hook rebuilt to open on the whole galaxy with the Sun system scaled up, then a zoom into the heliosphere.
- v14-v15: Teja's own Freesound files; dance bass limited to the first 3 s. **v15 is final.**

## Publish copy

### YouTube Shorts
**Title (pick one, under 70 characters)**
1. The Sun built a shield around us. It's called the heliosphere (recommended: matches the hook)
2. Our Sun has an invisible bubble. Where does it end?
3. Does every star have a bubble like this?

**Description**
> The Sun is surrounded by an invisible bubble called the heliosphere. It is made by the solar wind, a stream of charged particles, carrying the Sun's magnetic field billions of kilometres out. It blocks or deflects part of the cosmic radiation coming from outside, and everything in our solar system lives inside it.
>
> Voyager 1 crossed the termination shock at about 94 AU in 2004 and left the bubble at the heliopause, about 121 AU out, in 2012.
>
> The bubble moves too: the Sun flies around the Milky Way at about 230 km/s, orbiting Sagittarius A*, one lap every 230 million years. Earth has its own, much smaller shield inside it: the magnetosphere.
>
> And the question at the end is real: stars with winds blow bubbles of their own ("astrospheres"), and astronomers have detected them around other stars.
>
> Distances compressed, sizes enlarged. Not to scale. Computer-generated visualisation. Sound from Freesound (credits below).
>
> Slow Light: stories worth slowing down for.
> #space #heliosphere #sun

**Hashtags (YouTube shows the first 3 above the title):** #space #heliosphere #sun
Also fine in the body: #astronomy #solarwind #voyager1 #milkyway #shorts

**Tags (under 500 characters)**
heliosphere, what is the heliosphere, sun's magnetic field, solar wind, heliopause, termination shock, voyager 1, does every star have a bubble, astrosphere, sun moving through the galaxy, how fast is the sun moving, sagittarius a*, cosmic rays, earth's magnetic field, magnetosphere, space facts, astronomy shorts, science shorts, slow light

**Pinned comment**
> Does every star have a bubble like this? Mostly yes: any star with a wind blows one, and astronomers have detected these "astrospheres" around other stars. Voyager 1 crossed ours in 2012, at about 121 AU. Which part surprised you most: the size of the bubble, or that it flies through the galaxy at 230 km/s? 🌌

**Upload settings:** Shorts, Science & Technology, not made for kids. **Altered or synthetic content = Yes.** Cover: the frame at about 0.3 s (galaxy + glowing bubble) or the Earth shield frame at about 20 s.

### Instagram Reels
**Caption**
> The Sun built a shield around us. 🌌☀️
>
> It's called the heliosphere: a bubble made by the solar wind that carries the Sun's magnetic field billions of km out. It blocks or deflects part of the cosmic radiation from outside. Voyager 1 left it in 2012, about 121 AU away.
>
> And the whole bubble flies through the Milky Way at about 230 km/s, once around every 230 million years.
>
> So... does every star have a bubble like this? 👇 Tell me what you think.
>
> (Distances compressed, sizes enlarged. Not to scale.)

**Hashtags (10-12):** #space #heliosphere #sun #astronomy #solarwind #voyager1 #milkyway #sciencefacts #universe #cosmos #astrophysics #spacefacts

### Facebook Reels
**Caption**
> The Sun has an invisible shield, and it is moving through the galaxy right now. 🌌
>
> The heliosphere is a bubble the solar wind blows around the whole solar system. Voyager 1 flew out through its edge in 2012, about 121 AU from the Sun. Earth has its own, much smaller shield inside it.
>
> Does every star have a bubble like this? Share this with someone who loves space.
>
> (Distances compressed and sizes enlarged. Not to scale.)

**Hashtags (3-5):** #space #heliosphere #sun #astronomy #milkyway

### Posting plan (suggested, nothing is scheduled)
- YouTube Short first, then IG and FB the same day around 19:30 IST (playbook slot), only at a time Teja agrees.
- After posting: record 2-second stayed-to-watch, average view duration, completion and shares, and compare with Not a Vortex and Scale Ladder.

### Upload checklist
- AI/synthetic label on; first comment pinned.
- Keep the footer "DISTANCES COMPRESSED · SIZES ENLARGED · NOT TO SCALE".
- **Sound licences are unverified from the sandbox (Freesound is blocked there).** Teja picked them under his CC0-only rule. Open each page once (list in `audio-attribution.md`, section "Heliosphere reel") and confirm CC0 before uploading. If any is CC BY, paste its credit line in the description (a placeholder block is in `audio-attribution.md`). Never CC BY-NC.

## Facts and sources

| On screen | Fact | Source |
|---|---|---|
| Heliosphere, solar wind carries the Sun's magnetic field out | The solar wind drags the Sun's magnetic field outward and inflates a bubble around the solar system | NASA Heliophysics, "Heliosphere" |
| Termination shock ~90 AU | Voyager 1 crossed it at about 94 AU on 16 Dec 2004 (Voyager 2 at about 84 AU in 2007); label says ~90 AU as the round figure | Stone et al., Science 309 (2005); same as `edge-of-the-wind.md` |
| Heliopause ~120 AU | Voyager 1 crossed it at about 121 AU on 25 Aug 2012 | NASA JPL, "Interstellar Voyager"; Gurnett et al., Science 341 (2013) |
| "Blocks or deflects part of the cosmic radiation" | The heliosphere reduces the flux of low- and mid-energy galactic cosmic rays reaching the inner solar system; the highest-energy ones get through. The reel never gives a percentage. | NASA Heliophysics; Voyager cosmic-ray results |
| Sun's speed 230 km/s, lap 230 million years, Sagittarius A* | About 230 km/s around the Galactic Centre, about 26,700 ly away, one lap about 230 million years; Sgr A* is about 4.3 million solar masses | same as `not-a-vortex.md` |
| "SUN TRAVELLED ... AU" counter | 230 km/s = 48.5 AU per year; the counter is that speed times the time-lapse years (e.g. 90 yr -> 4,365 AU) | arithmetic |
| Earth shield: ~10 R magnetopause, ~13 R bow shock, tilt ~11°, 23.93 h rotation | Typical sunward distances about 10 Earth radii (magnetopause) and about 13-15 (bow shock) vary with solar wind; dipole tilt about 11°; sidereal day 23.93 h | NASA / standard magnetosphere references |
| "Does every star have a bubble like this?" | Stars with winds blow astrospheres; hydrogen "walls" and astrospheres have been detected around other stars with Hubble Lyman-alpha absorption | Wood, Living Reviews in Solar Physics (2004) and later updates |

Accuracy notes (use in replies to comments):
- **Not to scale.** The Sun, planets and the bubble are enlarged (the bubble is about 0.002 ly across; the Milky Way about 100,000 ly), orbit speeds and time are sped up and distances compressed.
- The heliosphere's true shape is debated (comet-like, "croissant", or rounder). The reel draws a generic nose-and-tail bubble.
- **Consistency with "Not a Vortex":** the planet paths here are traces of where each planet has been in its orbit around the moving Sun, drawn as helices because the orbits are compressed and sped up. They are not a claim that the planets "trail behind in a vortex". If someone asks, point to Not a Vortex: in the real geometry the planets are ahead of the Sun about half the time, and the real paths are long stretched waves. Do not use the word "vortex" in this reel's copy.
- Say "Voyager 1 crossed the heliopause", not "left the solar system".
- The galaxy is a stylised procedural spiral, not a map of the real Milky Way.
