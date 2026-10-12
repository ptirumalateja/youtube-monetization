# Globe pipeline: India's real plate motion in Blender

This renders the India Episode 1 globe shots from real plate-reconstruction data. No AI is involved, so the continent shapes and positions come straight from the model.

## Sources

- **Plate model:** Müller et al. (2019), downloaded with `gplately` (`DataServer("Muller2019")`).
  - **Credit line:** *"Plate reconstruction: Müller et al. (2019), EarthByte / GPlates."*
- **Surface imagery:** NASA Blue Marble Next Generation, July 2004 (`world.topo.bathy.200407.3x21600x10800.jpg`), public domain. Downscale it to `bm_8k.png` (8192×4096).

## Pipeline (runs on the A40 pod)

1. **`gen_seq.py <width> <t_start_Ma> <t_end_Ma> <frames> <outdir>`** writes one equirectangular texture per frame:
   - `color_XXXX.jpg`: the surface texture.
   - `mask_XXXX.png`: R = land, G = India (plate 501).
   - `meta.json`: India's centroid for each frame.

   It uses `paleotex.py`, which works like this for every pixel at time *t*:
   - Find the plate under the pixel (reconstructed static polygons).
   - Rotate the pixel back to its present-day position.
   - Sample its colour from Blue Marble.
   - Fill ocean with a flat colour, and remove modern Himalayan snow from the Indian plate.

   It runs in the venv `/workspace/tools/geo` and needs `MPLBACKEND=Agg`.
2. **`blender -b -P globe_scene.py -- <seqdir> <outdir> [samples] [frame_end]`** builds the scene and renders PNG frames, using Cycles on the GPU with OptiX:
   - globe, procedural clouds, atmosphere rim and stars
   - a camera that follows India's centroid

   Blender 4.2 LTS is installed at `/workspace/tools/blender`.
3. **`ffmpeg -framerate 24 -i f_%04d.png …`** encodes the clean clip. **`overlay.py`** adds a preview title and year counter. The final text should go on in the editor.

## Hook shot (Episode 1, shot 1): racing version (current)

```
gen_seq.py 8192 80 52 72 seq_race
trail.py seq_race 0.86
CAM=fixed CAM_POS=-18,59.5,2.75 CAM_TGT=1,62 blender -b -P globe_scene.py -- seq_race render_race 64
overlay.py race_clean.mp4 race_preview.mp4 80 52      # preview text + year counter
```

How it's set up:
- **Fixed camera** with a slow 6% push-in, so India visibly travels up the frame toward Asia.
- **`trail.py`** writes a fading wake into the mask's B channel, and the shader shows it as a faint warm glow on the ocean.
- **`FRAMES=1,36,72`** renders only those frames, for quick look checks.

## Hook shot: first version (camera follows India)

```
gen_seq.py 8192 74 58 72 seq_hook
blender -b -P globe_scene.py -- seq_hook render_hook 64
```

72 frames: about 6 min for textures and about 15 min to render on the A40.

**Pod note:** Blender's system libraries (`libxrender1 libxi6 libxkbcommon0 libsm6 libgl1 libxxf86vm1 libxfixes3 libegl1`) are installed on the pod's temporary container disk. Reinstall them with apt after a pod restart.

## Shots 4, 7 and 10

```
# Shot 4: India breaks from Madagascar (92 → 72 Ma, 4 s)
gen_seq.py 8192 92 72 96 seq_s4 && trail.py seq_s4 0.95
CAM=fixed CAM_POS=-55,40,2.7 CAM_TGT=-30,46 blender -b -P globe_scene.py -- seq_s4 r4 48

# Shot 7: collision, with a glow on India's leading edge (50 → 35 Ma, 4 s)
gen_seq.py 8192 50 35 96 seq_s7 && edge.py seq_s7 14
CAM=fixed CAM_POS=-14,70,2.2 CAM_TGT=17,73 GLOW=0.9 blender -b -P globe_scene.py -- seq_s7 r7 48

# Shot 10: today, a slow orbit with a pulsing pressure line (1 → 0 Ma, 3 s)
gen_seq.py 8192 1 0 72 seq_s10 && edge.py seq_s10 14
CAM=fixed CAM_POS=-6,68,2.45 CAM_POS_END=-4,80,2.3 CAM_TGT=22,76 CAM_TGT_END=24,80 GLOW=0.9 PULSE=1 \
  blender -b -P globe_scene.py -- seq_s10 r10 48
```

### Options

**Mask B channel:** either `trail.py` (a motion wake) or `edge.py` (a glow along India's northernmost edge in each column, i.e. the leading edge or suture).

**`globe_scene.py` environment variables:**
- `CAM=fixed` with `CAM_POS`, `CAM_TGT`: fixed camera.
- `CAM_POS_END`, `CAM_TGT_END`: a smoothstep camera move from the start values to these.
- `GLOW`: strength of the B-channel glow.
- `PULSE=1`: makes the glow pulse.
- `FRAMES=a,b,c`: renders only those frames.

**`paleotex.py` and ice:** before 34 Ma it turns present-day ice (Antarctica, Greenland) into tundra, because the ice sheets hadn't formed yet.
