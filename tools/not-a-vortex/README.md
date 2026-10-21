# Not a Vortex (Slow Light, 26 s, loops)

Open on the viral "solar system is a vortex" picture and call it wrong. Then one continuous move, in the style of the reference: the real solar system (today's planet positions, all eight planets orbiting and spinning, seven moons, both belts) in front of the Milky Way; the Sun sets off at its real 230 km/s and the orbits turn into long stretched waves, with the planets ahead of the Sun half the time; the camera pulls back until the whole spiral and Sagittarius A* at its centre fill the frame, and the Sun runs one full lap (230 million years) before the camera drops back onto it and the loop restarts. Notes, facts and publish copy: `final-reels/not-a-vortex.md` in the project files.

```sh
npm ci
python3 gen_planets.py                     # assets/*: our own planet maps and Saturn's ring profile (~10 min, numpy)
python3 gen_galaxy.py                      # assets/galaxy_plate.jpg: our own face-on Milky Way plate (~1 min)
node sound.mjs                             # output/sound.wav, fully synthesised (no samples, no credits)
node render.cjs --stills                   # review stills + fact checks (TIMES=1,2 to pick times)
RENDER_W=1080 FROM=0 TO=780 node render.cjs   # JPEG frames into output/frames (run several ranges in parallel)
./build.sh                                 # frames + sound -> output/not-a-vortex_master.mp4 and not-a-vortex.mp4
```

- `timeline.json`: duration, facts, J2000 planet elements (with mean longitudes, tilts and day lengths), shot list, review times.
- `scene.js`: two scenes drawn into one frame, both in galactic axes. The galaxy scene is in light years (Sun starts at the origin, centre at 26,700 ly): the plate, star points sampled from it, Sgr A* (EHT-style ring, hugely enlarged), the Sun's orbit. The solar scene is an enlarged inset at the Sun on a compressed map (radius 2.2 sqrt(a), sizes R^0.5); its camera is the galaxy camera's offset from the Sun times K = dS/dG, so the two always line up. Planets follow Kepler orbits; axes come from the IAU pole coordinates. True paths are screen-space ribbons evaluated in the vertex shader, `P(y) = V_sun (y - now) + k orbit(y)`, with the Sun's galactic velocity (11.1, 245, 7.3) km/s, 60.6° out of the ecliptic, at a map speed that keeps Earth's true stretch (48.5 orbit radii per year). During the lap the disc turns with the Sun (the Sun sits near the spiral pattern's corotation radius).
- `render.cjs` refuses to render if the lap counter goes backwards, if the ecliptic is not 60.2° from the galactic plane, or if Earth is not ahead of the Sun about half of each orbit.
- On a Mac set `CHROME_PATH` to Chrome and pass `--gpu`; the default is the container's Playwright Chromium with SwiftShader.
