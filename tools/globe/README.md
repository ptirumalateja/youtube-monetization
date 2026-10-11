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
