# Heliosphere hook v17 (5 s)

Opening hook for the heliosphere reel, built on the Not a Vortex engine (tools/not-a-vortex on branch claude/project-thread-k71kjg):
galaxy plate + plate-sampled stars, white-gold Sun with corona, Kepler planets and true stretched paths, canvas bloom.
Added here: Earth's magnetosphere (shield + dipole field lines), the heliosphere (termination shock + heliopause on the same sqrt map), solar wind sparks,
and the hook captions in Playfair. The hook code is the HELIOSPHERE HOOK section at the end of scene.js.

```sh
ln -s ../heliosphere-v16/node_modules node_modules   # three 0.170
RENDER_W=1080 TIMES=0,1.2,3 node render.cjs --stills
RENDER_W=1080 FROM=0 TO=150 OUT_DIR=output/frames node render.cjs   # ~1.5 s/frame, split into 4 ranges
```
Assets (planet maps, galaxy plate) are copied from Not a Vortex and are our own generated textures.
