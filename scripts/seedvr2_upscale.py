#!/usr/bin/env python3
"""Upscale/restore video clips with SeedVR2 (3B int8 by default) on the Slow Light ComfyUI pod.

Usage: seedvr2_upscale.py JOBS.json   (list of {"name", "video", "scale"?, "model"?, "seed"?})
"video" is a file in ComfyUI's input folder (upload the mp4 first). Default scale 1.5 (704x1280 -> 1056x1920).
One-step restoration; temporal chunking is automatic so long clips fit in VRAM. Colour is matched back (lab).
Built from ComfyUI's "SeedVR2 3B Int8: Upscale Video" template.
"""
import json, os, subprocess, sys

B = os.environ.get("COMFY_URL", "https://zrqv12r68xf2aa-8188.proxy.runpod.net")


def graph(video, prefix, scale=1.5, model="seedvr2_3b_int8_convrot.safetensors", seed=42, overlap=4):
    return {
        "1": {"class_type": "LoadVideo", "inputs": {"file": video}},
        "2": {"class_type": "GetVideoComponents", "inputs": {"video": ["1", 0]}},
        "3": {"class_type": "ImageScaleBy", "inputs": {"image": ["2", 0], "upscale_method": "lanczos", "scale_by": scale}},
        "4": {"class_type": "SeedVR2Preprocess", "inputs": {"resized_images": ["3", 0]}},
        "5": {"class_type": "VAELoader", "inputs": {"vae_name": "seedvr2_ema_vae_fp16.safetensors"}},
        "6": {"class_type": "UNETLoader", "inputs": {"unet_name": model, "weight_dtype": "default"}},
        "7": {"class_type": "VAEEncodeTiled", "inputs": {"pixels": ["4", 0], "vae": ["5", 0], "tile_size": 512, "overlap": 128, "temporal_size": 64, "temporal_overlap": 8}},
        "8": {"class_type": "SeedVR2TemporalChunk", "inputs": {"latent": ["7", 0], "temporal_overlap": overlap, "chunking_mode": "auto"}},
        "9": {"class_type": "SeedVR2Conditioning", "inputs": {"model": ["6", 0], "vae_conditioning": ["8", 0]}},
        "10": {"class_type": "KSampler", "inputs": {"model": ["6", 0], "positive": ["9", 0], "negative": ["9", 1], "latent_image": ["8", 0],
                "seed": seed, "steps": 1, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "11": {"class_type": "SeedVR2TemporalMerge", "inputs": {"latents": ["10", 0], "temporal_overlap": ["8", 1]}},
        "12": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["11", 0], "vae": ["5", 0], "tile_size": 512, "overlap": 128, "temporal_size": 64, "temporal_overlap": 8}},
        "13": {"class_type": "SeedVR2PostProcessing", "inputs": {"images": ["12", 0], "original_resized_images": ["3", 0], "color_correction_method": "lab"}},
        "14": {"class_type": "CreateVideo", "inputs": {"images": ["13", 0], "fps": ["2", 2]}},
        "15": {"class_type": "SaveVideo", "inputs": {"video": ["14", 0], "filename_prefix": prefix, "format": "auto", "codec": "auto"}},
    }


for job in json.load(open(sys.argv[1])):
    g = graph(job["video"], f"slowlight/up/{job['name']}", job.get("scale", 1.5),
              job.get("model", "seedvr2_3b_int8_convrot.safetensors"), job.get("seed", 42))
    out = subprocess.run(["curl", "-sS", "-m", "60", "-H", "Content-Type: application/json", "-d", "@-", B + "/prompt"],
                         input=json.dumps({"prompt": g}), capture_output=True, text=True).stdout
    print(job["name"], out.strip()[:400])
