# Not a Vortex (Slow Light, 29 s, wordless, loops)

Open on the viral "solar system is a vortex" picture and call it wrong. Fly past all eight planets (true sizes, true axial tilts, true relative spin rates, seven moons), pull up to the whole system tilted 60° to the galaxy, then let the Sun move at its real 230 km/s in the galaxy's frame: the paths become long stretched coils that recede behind the Sun, and the planets take turns ahead of it. Pull out to the whole Milky Way, dive to the centre where real S-star orbits whip around Sagittarius A*, and plunge home into the frame-0 vortex. Notes, facts and publish copy: `final-reels/not-a-vortex.md` in the project files.

```sh
npm ci
python3 gen_planets.py                     # assets/*: our own planet maps and Saturn's ring profile (~10 min, numpy)
node sound.mjs                             # output/sound.wav, fully synthesised (no samples, no credits)
node render.cjs --stills                   # review stills + fact checks (TIMES=1,2 to pick times)
RENDER_W=1080 FROM=0 TO=870 node render.cjs   # JPEG frames into output/frames (run several ranges in parallel)
./build.sh                                 # frames + sound -> output/not-a-vortex.mp4 (master) and _share.mp4
```

- `timeline.json`: duration, facts, J2000 planet elements with tilts and day lengths, shot list, review times.
- `scene.js`: three scenes at three scales in galactic axes. Solar (AU, Sun at origin; the planets live in an ecliptic group rotated by the J2000 ecliptic-to-galactic matrix), galaxy (light years, Sun at origin, centre at 26,700 ly), core (AU around Sgr A*). Planets follow Kepler orbits, staged in longitude so the flyby meets them in order. True paths are screen-space ribbons evaluated in the vertex shader: `P(y) = V_sun*(y - now) + orbit(y)`, with the Sun's galactic velocity (11.1, 245, 7.3) km/s, which is 60.6° out of the ecliptic. S-star orbits use Gillessen et al. 2017 elements at 8.28 kpc.
- `render.cjs` refuses to render if the distance counter goes backwards, if the ecliptic is not 60.2° from the galactic plane, or if Earth is not ahead of the Sun about half of each orbit.
- On a Mac set `CHROME_PATH` to Chrome and pass `--gpu`; the default is the container's Playwright Chromium with SwiftShader.
