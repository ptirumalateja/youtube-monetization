# ComfyUI on the Slow Light pod: what's available (checked 2026-10-07)

- ComfyUI 0.30.0, templates package 0.11.27, A40 (48 GB VRAM).
- 493 templates; 1,071 node types, of which 215 are API ("partner") nodes.

## Video
- **Local (runs on our GPU, no per-clip fee):**
  - Wan 2.2 14B: i2v, t2v, first-last frame, Fun Camera control. Installed.
  - LTX-2.3: i2v, t2v, first-last frame, image+audio to video. About 39–47 GB, fits the A40 tightly.
  - Hunyuan Video 1.5 720p: about 45 GB.
  - MiniMax H3 (open weights): about 57 GB, too big for the A40; needs an 80 GB+ GPU.
- **API (paid per clip with Comfy.org credits):**
  - Kling 3.0 / O3 / Omni Pro, Seedance 2.0, MiniMax Hailuo, Veo, Vidu, Luma, Runway, PixVerse, Grok.

## Utility (local, small)
- SeedVR2 3B/7B video and image upscaler (4–9 GB).
- RIFE/FILM frame interpolation.
- SAM3 segmentation, Depth Anything 3, BiRefNet background removal.

## Audio
- **Local:** ACE-Step 1.5 (music), Stable Audio 3 (music/SFX).
- **API:** ElevenLabs TTS and SFX (billed through Comfy credits, so no access to our cloned voices), Seed Audio, Sonilo.

## Installed on the volume
Qwen-Image-Edit 2511 (+ Lightning LoRA), Wan 2.2 I2V 14B high/low (+ Lightx2v LoRAs), UMT5, Qwen 2.5 VL, VAEs.
