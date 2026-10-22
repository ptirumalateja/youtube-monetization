# Photon Rain (200 MP vs 24 MP)

| | |
|---|---|
| Status | v2 final; a v3 storyboard is waiting on Teja's hook pick |
| Upload file | `final-reels/photon-rain-v2.mp4` |
| Length | 32.0 s |
| Voice | None (wordless) |
| Copy taken from | `final-reels/photon-rain.md` |

## Version notes

- v1 (3D bucket field) is superseded by the v2 line-art cut. The copy applies to v2.

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

## Facts and sources

- **Phone sensor:** Samsung ISOCELL HP2, 200 MP, 1/1.3-inch type, 0.6 µm pixels; it is the main camera of the Galaxy S23 Ultra. Its active array of 16,320 × 12,240 px × 0.6 µm is 9.79 × 7.34 mm, about 71.9 mm². Sources: [New Atlas, ISOCELL HP2](https://newatlas.com/mobile-technology/samsung-isocell-hp2/); [KED Global, "Samsung unveils 200-megapixel image sensor for Galaxy S23 Ultra"](https://amp.kedglobal.com/newsView/ked202301170018); [PhoneArena](https://www.phonearena.com/news/samsung-unveils-200mp-sensor-for-s23-ultra_id144895).
- **Full-frame 24 MP:** 36 × 24 mm = 864 mm²; 6,000 × 4,000 px gives a 6.0 µm pitch (for example, the 24 MP Sony a7 III's pitch is about 5.9 µm). For comparison, see [apotelyt sensor specs](https://apotelyt.com/camera-specs/sony-a7-iv-sensor-pixels).
- **Area ratio:** 864 / 71.9 = 12.0×, so the "12× THE AREA" label holds. **Pixel area:** (6.0 / 0.6)² = 100×, so "1 CAMERA PIXEL = 100 PHONE PIXELS" holds.
- **Same light per area:** at the same f-number and shutter speed, each mm² receives the same photon flux. A whole sensor therefore catches light in proportion to its area (12×), and each pixel in proportion to its own area (100×).
- **Shot noise:** photon arrivals are Poisson, so the noise is √N. With 100 photons the noise is 10 (±10%); with 10,000 it is 100 (±1%). This is physics, not a flaw of the sensor. In the scene, each bucket's count comes from a seeded Poisson simulation. The measured spread at the end is 10.0% for the phone and 1.0% for the camera.
- **The photo:** both sensors capture the same picture at the same output size. Per output pixel, the phone collects about 10.7× fewer photons, and the noise is simulated with Poisson statistics per colour channel.
- **Honest caveats** (for the copy, not on screen): real phones fight back by stacking many frames and denoising. The comparison is per single exposure at the same settings. Read noise, lens quality and processing also matter. The photon streaks are illustrative; the counters, not the streaks, carry the real numbers.
