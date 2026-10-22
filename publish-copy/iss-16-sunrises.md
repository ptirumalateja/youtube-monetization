# 16 Sunrises a Day (ISS free fall)

| | |
|---|---|
| Status | Delivered, awaiting Teja's review |
| Upload file | `iss_16_sunrises_v1.mp4` (project files root) / `final-reels/iss-16-sunrises.mp4` on the Mac |
| Length | 22.5 s |
| Voice | None (wordless) |
| Copy taken from | `iss-sunrises-publish-copy.md` on branch `claude/project-thread-g6qq1m` |

## Publish copy

### YouTube Shorts
**Title (pick one):**
1. Astronauts see 16 sunrises a day (recommended)
2. The ISS isn't floating. It's falling.
3. Why the space station never hits the ground

**Description:**
> Astronauts on the International Space Station see about 16 sunrises every day.
>
> The station circles Earth every 92 minutes at about 7.7 km per second, 400 km up. And it isn't floating: gravity up there is still about 90% as strong as on the ground. The ISS is falling the whole time. It just moves sideways so fast that Earth's surface curves away beneath it, so it keeps missing. That's an orbit.
>
> The cannon on a giant tower is Newton's thought experiment, not to scale. Visuals are 3D-rendered.
>
> Sound: original, synthesised for this video.
>
> Slow Light: stories worth slowing down for.
> #space #ISS #science

**Hashtags:** #space #ISS #science

**Tags (under 500 characters):**
ISS, international space station, 16 sunrises a day, sunrise from space, how does the ISS stay in orbit, why astronauts float, free fall, orbit explained, Newton's cannonball, orbital speed, space facts, astronomy, physics, space shorts, science shorts, slow light

**Pinned comment:** Did you know the ISS is falling right now, at 7.7 km per second? 🌍

**Upload settings:** Shorts, Science & Technology, not made for kids. **Altered or synthetic content = Yes** (realistic-looking rendered space visuals). Thumbnail: about 1.6 s (station silhouette, sunrise and the full hook) or about 17.6 s (the closed orbit with "IT'S FALLING.").

### Instagram Reel (AI label ON, max 5 hashtags)
> Astronauts on the ISS see 16 sunrises a day.
>
> One lap of Earth takes about 92 minutes at 7.7 km per second. And the station isn't floating: it's falling the whole time, just sideways fast enough to keep missing Earth.
>
> Newton's cannonball, not to scale. Original sound.
>
> Follow Slow Light for more stories worth slowing down for.
>
> #space #ISS #science #physics #astronomy

### Facebook Reel
> They see 16 sunrises a day, and they never stop falling. 🌍 The International Space Station circles Earth every 92 minutes at 7.7 km/s. Gravity up there is still about 90%, but the station moves sideways so fast that it keeps missing the ground. (Newton's cannonball, not to scale. Original sound.)

### Audio
Fully synthesised in `tools/iss-sunrises/synth.mjs` (glass FM bells, filtered-noise whooshes, synthesised impacts, drone). No samples, so no credit lines are needed.

## Facts and sources

| On screen | Fact |
|---|---|
| ISS · 400 KM UP | The station orbits about 400-420 km above Earth |
| 16 sunrises a day | One orbit takes about 92-93 minutes, about 15.5 orbits a day, so the crew sees about 16 sunrises and 16 sunsets every 24 hours |
| 7.7 KM/S | Orbital speed about 7.66 km/s (about 28,000 km/h) |
| Gravity up there still ~90% | (6,371 / 6,771)^2 = 0.885 of surface gravity at 400 km |
| "It's falling. It just keeps missing Earth." | An orbit is free fall: the station falls toward Earth all the time but moves sideways fast enough that the surface curves away beneath it (Newton's cannonball) |
- The cannon on a 400 km tower is Newton's thought experiment, drawn not to scale. The 2, 4 and 6 km/s arcs are computed with real inverse-square gravity from that height; 7.7 km/s closes into a circle.
- The weightlessness on board comes from falling together with the station, not from a lack of gravity. Don't say "zero gravity".
- Visuals are procedurally 3D-rendered (Earth, station and orbit drawn in code; no NASA imagery). The station model is simplified.
