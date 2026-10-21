# The Jam Is Made of Phones (reel 6 of the ref remakes)

**Slug:** `jam-made-of-phones` · **Length:** 22.0 s, 1080x1920, 30 fps, loops · **Format:** wordless Slow Light reel (no voiceover), on-screen text + sound design
**Source code:** `tools/phone-jam/` (three.js scene `index.html`, `render.js`, `shot.js`, `proj.js`, `overlay.py`, `mix.py`)
**Built from:** the reel #6 brief in `ref-remakes-plan.md` (reference: a 159 s voiced, low-poly daytime explainer about how Google Maps knows about traffic). We took the topic only: no footage, layout, text or assets from the reference.

## 1. Concept

Google Maps doesn't see cars. It sees phones. When a lot of phones on one street slow to a crawl, the street turns red, and Maps sends everyone else another way.

The twist is a real event. In February 2020, the Berlin artist Simon Weckert pulled 99 second-hand phones through empty streets in a hand-cart. Google Maps showed a traffic jam ("Google Maps Hacks"). So the jam you see on the map is made of phones, and sometimes that's all it is.

What makes it different from the reference: it's set at night instead of a low-poly day city, and light trails show speed (long trail = fast, short = slow). One counter goes only up (phones reporting on this street, 0 to 99), and you can hear it too, because every phone that starts reporting gets its own ping. There's a real-world payoff (the wagon), and the reel loops.

## 2. Shot plan (as built)

| Time (s) | Shot | On screen | Sound |
|---|---|---|---|
| 0.0-1.9 | High aerial over a night city. Every street carries gold phone dots with light trails over a thin teal data layer. Frame-0 pulse. | Hook typed: "MAPS DOESN'T / SEE CARS." | Frame-0 hit (crack, pitch-drop body, small sub), typing ticks, city wash |
| 1.9-2.6 | Snap: the camera dives into one avenue (5-sub-frame motion blur) | | Reverse swell into a down-whoosh and a low thump |
| 2.5-6.0 | Drone shot down the avenue canyon. Phones start reporting one by one (ping ring). Long gold trails. The avenue line under the stream is teal. | Counter "PHONES ON THIS STREET" 0 to ~40; "AVG SPEED 48 KM/H" (teal dot); "IT SEES PHONES." / "EACH DOT IS ONE PHONE" | One data ping per phone, pitch rising; fast passing whooshes |
| 6.0-10.0 | The front of the stream slows first and the rear piles in (a real compression wave). Trails shrink. The avenue line goes teal to gold to red under the slow part. The camera sinks and slows with the jam. | Counter to 99; speed 48 to 4 km/h (dot teal, then gold, then red); "PHONES SLOW DOWN." / "THE ROAD TURNS RED." | Tape-stop drone sinking, two low warning pulses |
| 9.6-10.7 | The whole block paints red. The dots knot into one tight cluster. Held breath. | Red chip "TRAFFIC JAM" on the knot | Near-silence, then a reversed suck and a 70 ms vacuum |
| 10.7-11.4 | Dive into the knot | | **Biggest hit** at 10.72 s |
| 11.4-14.3 | Street level: no cars. One charcoal hand-cart holding 99 glowing phones (each screen shows a map with a red line), pulled by one walker on an empty red-lit street. | Red chip "BERLIN, 2020"; "NO CARS." / "ONE WAGON." / "99 PHONES." + credit "artist Simon Weckert, 'Google Maps Hacks'" | Footsteps in time with the walker's stride, wagon rattle, a soft chord shimmer from the phones |
| 14.3-15.2 | Rise straight up to a top-down map view | | Rising whoosh |
| 15.2-18.7 | Map view. The red block. A teal YOU dot to the south and a destination to the north. The old straight route (dashed cream) goes through the red. A search wave ripples out across the street graph. The old route fades and the new teal route draws around the block. YOU starts moving along it. | "MAPS BELIEVES IT" / "AND STEERS YOU AROUND."; "YOU" label tracks the dot | Sonar sweep with echoes, pluck arpeggio as the route draws, two-note confirmation |
| 18.6-22.0 | The camera swings back to the frame-0 aerial. The red and the knot fade, and the avenue's normal traffic returns. | End line typed once: "THE JAM IS / MADE OF PHONES." Gone by 21.95 s. | Warm pad, then a rising tone and a swell into frame 0 (loop) |

Loop: the camera at 22.0 s equals the camera at 0.0 s (`segE = segA(t-22)`). Ambient traffic runs exactly 880 m per 22 s on every street, so the dots are where they started.

## 3. Facts and sources

| Claim (on screen or implied) | Status | Source |
|---|---|---|
| Google Maps traffic comes from aggregated, anonymised location data from phones (speed of phones along road segments) | Verified | Google, "Google Maps 101: How AI helps predict traffic and determine routes", Johann Lau, 3 Sep 2020: "aggregate location data can be used to understand traffic conditions on roads all over the world" (https://blog.google/products/maps/google-maps-101-how-ai-helps-predict-traffic-and-determine-routes/). Google blog, Dave Barth, "The bright side of sitting in traffic: Crowdsourcing road congestion data", 25 Aug 2009 (anonymous speed and location data, trip start and end points deleted). Summary: https://en.wikipedia.org/wiki/Google_Traffic |
| "MAPS DOESN'T SEE CARS." | Simplification, defensible | Maps estimates traffic from phone data plus historical patterns and driver incident reports (same Google post). It doesn't count cars directly. In some regions it has also used road-sensor feeds, so we don't claim "only phones". |
| Berlin, 2020: one artist, one hand-cart, 99 phones, and Google Maps showed a jam | Verified | CNN (99 phones with location services on, in a small red cart; virtual jams including one outside Google's Berlin office). Artnet News, 4 Feb 2020 (99 second-hand phones in a little red wagon; streets turned from green to red). Work title "Google Maps Hacks" (Simon Weckert, 2020; ZKM listing https://extinction.zkm.de/artworks/google-maps-hacks). Google's response: "Whether via car or cart or camel, we love seeing creative uses of Google Maps..." |
| "AND STEERS YOU AROUND." | Verified as general behaviour | Maps routing takes live traffic into account and offers faster routes around congestion (Google post above). Weckert described the stunt as turning green streets red "by navigating cars on another route". We don't claim to know how many drivers were rerouted that day. |
| Walking pace about 4 km/h; free flow 48 km/h | Illustrative | Speed readout maps the stream's speed to a plausible urban free-flow (48 km/h) and walking pace (4 km/h). |
| Scene sizes and stream length | Not to scale | Tagged "ILLUSTRATION · NOT TO SCALE". The stream of 99 dots compressing into one cart is a data visualisation of what Maps sees, not a literal path. |

Design changes from reality, made on purpose: Weckert's cart was red. Ours is charcoal because red is reserved for markers (the jam). The walker is a faceless figure, not a likeness of the artist.

## 4. Sound

Everything is synthesised in `tools/phone-jam/mix.py` (numpy/scipy). It uses no samples, so **no audio credits are needed** and there's nothing to add to `audio-attribution.md`. It's a new sound family ("night signal") that doesn't reuse the Night Sky or Scale Ladder palettes: city wash and hum, one data ping per phone (an audible counter), a tape-stop slowdown, sonar route search, a pluck arpeggio and a warm pad. Hits only land on frame 0, the snap (small) and the reveal (biggest). Under 90 Hz is kept on the hit bus only. Final master after AAC: -16.1 LUFS integrated, true peak -1.7 dBFS (loudnorm I=-15 TP=-2, then a limiter at 0.8).

## 5. Publish copy

**YouTube title:** Google Maps doesn't see cars. It sees phones. 📱🚦
**Alt title (A/B):** 99 phones in a wagon made a fake traffic jam

**YouTube description:**
> Google Maps doesn't count cars. It watches phones. When lots of phones on one street slow down, the road turns red and Maps steers everyone else around it.
> In 2020, Berlin artist Simon Weckert pulled 99 phones through empty streets in a hand-cart ("Google Maps Hacks"). Google Maps showed a traffic jam.
> The jam is made of phones.
>
> Illustration, not to scale. Sources: Google Maps blog "Google Maps 101: How AI helps predict traffic and determine routes" (2020); Google blog "The bright side of sitting in traffic" (2009); Simon Weckert, "Google Maps Hacks" (2020).
> Sound: original, made for this video.
>
> #GoogleMaps #Traffic #Shorts #Science #Tech #DidYouKnow #SlowLight

**Instagram / Facebook caption:**
> That red line on your map? It isn't cars. It's phones moving slowly. 📱🚦
> In 2020 an artist pulled 99 phones in a wagon down an empty Berlin street, and Google Maps showed a traffic jam.
> Follow @slowlight for stories worth slowing down for.
> #googlemaps #traffic #tech #science #didyouknow #reels

**Pinned comment:** Would you have taken the detour? 🚗↪️

**Upload checklist:** turn the AI or synthetic label on (the visuals are computer-generated). Cover frame: the red block with the "TRAFFIC JAM" chip (about 10.3 s).

## 6. How to rebuild

```
cd tools/phone-jam && npm i three@0.170.0 playwright-core && pip install scipy pillow numpy
python3 -m http.server 8771 &
node shot.js 540 960 /tmp/stills 0 5 10.3 12.5 17.5          # test stills
for w in 0 1 2 3; do node render.js 1080 1920 /tmp/fr $w 660 4 & done; wait   # 660 frames, native 1080x1920
node proj.js /tmp/proj.json                                   # counter + screen positions for the overlay
python3 overlay.py /tmp/fr /tmp/proj.json /tmp/pic.mp4        # info layer (asserts the counter is monotonic)
python3 mix.py /tmp/mix.wav
ffmpeg -i /tmp/pic.mp4 -i /tmp/mix.wav -af "loudnorm=I=-15:TP=-2:LRA=11,alimiter=limit=0.8:level=false" -c:v libx264 -crf 22 -maxrate 12M -bufsize 24M -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart jam-made-of-phones.mp4
```

Rendering is headless Chromium with SwiftShader (CPU). Motion blur averages 2 sub-frames normally and 5 during the snap, dive, rise and return moves.

## 7. Delivery

- Final: `/mnt/project-files/final-reels/jam-made-of-phones.mp4` (22.0 s, 1080x1920, H.264 + AAC).
- 27.9 MB. Contact sheet at 2 fps: `/mnt/project-files/final-reels/jam-made-of-phones-contact.jpg`.
- QA: the counter is monotonic (asserted in overlay.py). No white frames (an 8-9 s white-out from stacked trails was fixed and re-rendered). Text stays out of the bottom 18%, except the small YOU label, which tracks the dot at about 82% height. The last frame matches frame 0. The end line clears before the hook is typed again.
