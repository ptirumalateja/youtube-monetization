# Jupiter bodyguard reel

14 s 9:16 hype reel: Saturn roasts Earth by text, Jupiter rises behind Earth ("I have him."), then yanks a fireball swarm aimed at Earth into itself.

- `kernel.py`: numba ray tracer (Earth day/night/clouds, oblate Jupiter, Saturn + rings with shadows, lensed Milky Way sky, procedural stars)
- `assets.py`: textures (8k Solar System Scope maps via media.githubusercontent.com, set `JB_TEX`), colourised sky, nebula
- `shots.py`: timeline, cameras, fireball simulation (Jupiter "grabs" rocks near Earth)
- `comp.py`: fireballs, impacts/scars, gravity pulse, bloom, grade, text-message bubbles (twemoji PNGs in `$JB_TEX/emoji`)
- `render.py OUT START END STEP SS`, `mix.py SFXDIR OUT.wav`, `package.sh FRAMES MIX OUTDIR NAME`

Full render: ~2.8 s/frame at 1080x1920 with 2x2 supersampling on 4 cores.
