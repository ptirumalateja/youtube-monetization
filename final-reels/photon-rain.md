# Photon Rain (200 MP vs 24 MP)

- **Video:** `final-reels/photon-rain.mp4` in the project files (not in git). 22.0 s, 1080x1920 rendered natively, 30 fps, loops, no voiceover.
- **Status:** delivered 21 Oct 2026, reel #1 of the reference remakes (`ref-remakes-plan.md`). Not posted yet.
- **QA:** -14.7 LUFS integrated, true peak -2.3 dBFS measured after AAC; 26 MB; counters asserted monotonic in the overlay; last frame flows into frame 0 (the next wave of photons is already falling). Contact sheet: `final-reels/photon-rain_contact_2fps.jpg` in the project files.
- **Build:** `tools/photon-rain/` (see its README). Sound is fully synthesised, so no credits are needed.
- **Reference:** the 88 s voiced "200 megapixels… and still beaten by a 24 MP camera" explainer (flat navy line art). We took only the topic. Our version is one continuous 3D camera move with true sensor areas, real Poisson photon counts and a photo that develops on the sensors. It has no voiceover and no line-art layout.

## Concept
Megapixels count buckets, and light is what fills them. A 200 MP phone sensor and a 24 MP full-frame sensor sit side by side at their true relative area (12×). The same rain of photons falls on both at the same light level and the same shutter time. When we dive to the seam between them, one camera pixel is as wide as 10 phone pixels, so it covers the area of 100 of them. Each pixel is a glass bucket that fills with gold light. The phone buckets end up ragged, about ±10% from bucket to bucket, while the camera buckets fill flat, about ±1%. When we pull out, the same night photo has developed on both sensors: the phone's version is grainy and the camera's is clean.

## Shot plan (frozen before the build)
| Time | Shot | Text |
|---|---|---|
| 0-2.3 | Nearly top-down view of both sensors at true area. A burst of gold photon streaks is already falling on frame 0 (shutter hit). | Hook typed by 1.6 s: "200 MEGAPIXELS" / red chip "LOSES TO 24." Labels "PHONE 200 MP" and "CAMERA · 24 MP". |
| 2.3-6.6 | Steady, even rain. A night photo (moon, hills, a boat in the moon path) slowly develops on both sensors. | "SAME LIGHT. SAME SHUTTER." then "THE CAMERA SENSOR HAS / 12× THE AREA / SO IT CATCHES 12× THE LIGHT". |
| 6.6-9.2 | Log-distance dive to the seam (about ×1,200). The photo blurs, the 6 µm grid appears first, then the 0.6 µm grid. | Monotonic "ZOOM ×N" counter. "1 CAMERA PIXEL = 100 PHONE PIXELS". |
| 9.2-14.55 | Bucket field: phone buckets above the seam, camera buckets below, each a glass well. Rain fills them with gold light, and the height of the light is the real photon count. | "PHOTONS CAUGHT": PHONE PIXEL 0→~100, CAMERA PIXEL 0→~10,000 (both monotonic), with red squares on the two pixels being counted. "EVERY PIXEL IS A BUCKET OF LIGHT." "SMALL BUCKETS: ±10% NOISE" / red chip "BIG BUCKETS: ±1%". |
| 14.55-15.3 | Held breath: the rain stops and the sound goes nearly silent. | none |
| 15.3-17.7 | Fast pull-out back to the overview. The biggest hit (a big shutter with a body boom) lands at 17.4. | "200 MP GRAINY", "24 MP · CLEAN" |
| 17.9-21.2 | Both photos are held side by side. | End line typed: "MEGAPIXELS COUNT BUCKETS." / red chip "LIGHT FILLS THEM." |
| 21.2-22.0 | The photos fade to dark sensors. The next loop's first wave of photons is already falling, so the last frame flows into frame 0. | Tag stays on: "THOUGHT EXPERIMENT · SENSOR AREAS TO SCALE". |

## Facts and sources
- **Phone sensor:** Samsung ISOCELL HP2, 200 MP, 1/1.3-inch type, 0.6 µm pixels; it is the main camera of the Galaxy S23 Ultra. Its active array of 16,320 × 12,240 px × 0.6 µm is 9.79 × 7.34 mm, about 71.9 mm². Sources: [New Atlas, ISOCELL HP2](https://newatlas.com/mobile-technology/samsung-isocell-hp2/); [KED Global, "Samsung unveils 200-megapixel image sensor for Galaxy S23 Ultra"](https://amp.kedglobal.com/newsView/ked202301170018); [PhoneArena](https://www.phonearena.com/news/samsung-unveils-200mp-sensor-for-s23-ultra_id144895).
- **Full-frame 24 MP:** 36 × 24 mm = 864 mm²; 6,000 × 4,000 px gives a 6.0 µm pitch (for example, the 24 MP Sony a7 III's pitch is about 5.9 µm). For comparison, see [apotelyt sensor specs](https://apotelyt.com/camera-specs/sony-a7-iv-sensor-pixels).
- **Area ratio:** 864 / 71.9 = 12.0×, so the "12× THE AREA" label holds. **Pixel area:** (6.0 / 0.6)² = 100×, so "1 CAMERA PIXEL = 100 PHONE PIXELS" holds.
- **Same light per area:** at the same f-number and shutter speed, each mm² receives the same photon flux. A whole sensor therefore catches light in proportion to its area (12×), and each pixel in proportion to its own area (100×).
- **Shot noise:** photon arrivals are Poisson, so the noise is √N. With 100 photons the noise is 10 (±10%); with 10,000 it is 100 (±1%). This is physics, not a flaw of the sensor. In the scene, each bucket's count comes from a seeded Poisson simulation. The measured spread at the end is 10.0% for the phone and 1.0% for the camera.
- **The photo:** both sensors capture the same picture at the same output size. Per output pixel, the phone collects about 10.7× fewer photons, and the noise is simulated with Poisson statistics per colour channel.
- **Honest caveats** (for the copy, not on screen): real phones fight back by stacking many frames and denoising. The comparison is per single exposure at the same settings. Read noise, lens quality and processing also matter. The photon streaks are illustrative; the counters, not the streaks, carry the real numbers.

## Sound (synthesised, `mix_photon.py`)
New family, "glass rain + filling bottle + shutter":
- Every photon landing is a tiny glass tick, and the tick rate follows the visible rain. A hiss bed sits under the ticks.
- While the buckets fill, a resonance rises in pitch like a bottle being filled, with a fluttering voice an octave higher for the phone field.
- A small shutter hit lands on frame 0 (at 25 ms, because a click on sample 0 made the AAC encoder overshoot by +5 dB). The big hit at 17.4 s is a double click, a pitch-dropping body, gong partials and a small sub.
- A whoosh carries the dive, and a reversed swell with a 40 ms vacuum leads into the reveal. The held breath sits at 14.6-15.3 s, and a rising tone links back to frame 0.
- Everything except the hit bus is high-passed at 90 Hz.

## Publish copy
**YouTube title:** 200 Megapixels Loses to 24. Here's Why. #shorts

**Description:**
> A 200 MP phone sensor and a 24 MP camera sensor, drawn at their true sizes, in the same rain of light.
> The camera sensor has 12× the area, so in one shot it catches 12× the light. Each of its pixels is as big as 100 phone pixels.
> Light arrives as photons, and photons arrive randomly. A pixel that catches 100 photons is about ±10% noisy. One that catches 10,000 is about ±1%.
> Megapixels count buckets. Light fills them.
> (Phones fight back by stacking many frames and denoising. This shows a single exposure at the same settings.)
> Sensors: Samsung ISOCELL HP2 (200 MP, 0.6 µm, 1/1.3") vs a 36 × 24 mm 24 MP full frame (6 µm). Thought experiment; sensor areas to scale.
> Sound: all sounds synthesised for this video.
> #camera #photography #smartphone #megapixels #science #physics #shorts

**Pinned comment:** Would you rather have more megapixels or bigger pixels? (Phones cheat by stacking frames. Ask me how.)

**Instagram / Facebook caption:** 200 megapixels, still beaten by 24. Megapixels count buckets, and light fills them. 📷 Sensor areas to scale. #photography #camera #science

**Hashtags:** #shorts #photography #camera #megapixels #smartphone #physics #science

**Upload notes:** turn on the AI/synthetic-content label. No third-party audio is used.
