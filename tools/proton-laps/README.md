# Proton Laps Earth (Slow Light, 22.5 s, wordless, loops)

An LHC proton (6.8 TeV, 99.999999% of light speed) could circle Earth's equator 7.48 times in one second. Shown slowed 10x as a coil of laps with TIME / LAPS / KM counters, then a log plunge from Earth scale to metres at the finish: light is still ahead, by 2.85 m. Same visual language as the Birthday Paradox reel (navy, gold ring ticks, teal trails, Menlo counters, red chips).

```sh
npm ci
node sound.mjs                    # output/sound.wav, fully synthesised (no samples, no credits)
node render.cjs --gpu --stills    # review stills + monotonic-counter check (TIMES=1,2 to pick times)
node render.cjs --gpu             # output/proton-laps-earth.mp4 (1080x1920, 30 fps)
```

- `timeline.json`: duration, shot list, slow-motion start and factor, and the fact table used by scene and sound.
- `scene.js`: two three.js scenes. Earth (radius 10 units): dark globe with dotted grid and fresnel rim, gold equator with a tick per 1,000 km, the proton coil (radius grows 0.3 units per lap so laps stay countable), a real-speed blur ring for the hook. Finish line (metres): two lanes with metre ticks, light and proton heads with streaks, 400 km beam lines to follow down, a 1.75 m person for scale, scale-free ground dots (1 m to 100 km). The plunge interpolates log-distance and crossfades the scenes between about 2,500 km and 450 km.
- Facts: c = 299,792.458 km/s; equator 40,075 km -> 7.48 laps/s. 6.8 TeV proton: gamma = 7,247, 1 - beta = 9.5e-9 -> 2.85 m behind light per second. LHC ring 26.659 km, 11,245 laps/s.
