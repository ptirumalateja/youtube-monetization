#!/usr/bin/env python3
"""Queue LTX-2.3 (22B distilled fp8) image-to-video jobs on the Slow Light ComfyUI pod.

Usage: ltx_i2v.py JOBS.json   (list of {"name", "image", "prompt", "seed", "frames"?, "width"?, "height"?, "strength"?})
"image" is a file in ComfyUI's input folder. Defaults: 704x1280, 97 frames (8k+1) at 24 fps, first-frame guide strength 1.0.
Built from ComfyUI's LTX-2.3 FLF2V template: distilled 8-step manual sigmas, Euler ancestral, cfg 1.
The model also generates an audio track; it is saved with the clip and ignored in the edit.
"""
import json, os, subprocess, sys

B = os.environ.get("COMFY_URL", "https://zrqv12r68xf2aa-8188.proxy.runpod.net")
CKPT = "LTX-2.3/ltx-2.3-22b-distilled-fp8.safetensors"
NEG = ("blurry, out of focus, overexposed, underexposed, low contrast, washed out colors, excessive noise, flickering, "
       "distorted proportions, morphing, warping, text, subtitles, watermark, logo, cartoon, CGI, sudden cuts")
FPS = 24


def graph(prompt, seed, image, prefix, frames=97, w=704, h=1280, strength=1.0):
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CKPT}},
        "2": {"class_type": "LTXVAudioVAELoader", "inputs": {"ckpt_name": CKPT}},
        "3": {"class_type": "LTXAVTextEncoderLoader", "inputs": {"text_encoder": "gemma_3_12B_it_fp4_mixed.safetensors", "ckpt_name": CKPT, "device": "default"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": prompt}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": NEG}},
        "6": {"class_type": "LTXVConditioning", "inputs": {"positive": ["4", 0], "negative": ["5", 0], "frame_rate": float(FPS)}},
        "7": {"class_type": "LoadImage", "inputs": {"image": image}},
        "8": {"class_type": "ImageScale", "inputs": {"image": ["7", 0], "upscale_method": "lanczos", "width": w, "height": h, "crop": "center"}},
        "9": {"class_type": "LTXVPreprocess", "inputs": {"image": ["8", 0], "img_compression": 25}},
        "10": {"class_type": "EmptyLTXVLatentVideo", "inputs": {"width": w, "height": h, "length": frames, "batch_size": 1}},
        "11": {"class_type": "LTXVAddGuide", "inputs": {"positive": ["6", 0], "negative": ["6", 1], "vae": ["1", 2], "latent": ["10", 0],
                "image": ["9", 0], "frame_idx": 0, "strength": strength}},
        "12": {"class_type": "LTXVEmptyLatentAudio", "inputs": {"frames_number": frames, "frame_rate": FPS, "batch_size": 1, "audio_vae": ["2", 0]}},
        "13": {"class_type": "LTXVConcatAVLatent", "inputs": {"video_latent": ["11", 2], "audio_latent": ["12", 0]}},
        "14": {"class_type": "CFGGuider", "inputs": {"model": ["1", 0], "positive": ["11", 0], "negative": ["11", 1], "cfg": 1.0}},
        "15": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "16": {"class_type": "SamplerEulerAncestral", "inputs": {"eta": 0.0, "s_noise": 1.0}},
        "17": {"class_type": "ManualSigmas", "inputs": {"sigmas": "1., 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"}},
        "18": {"class_type": "SamplerCustomAdvanced", "inputs": {"noise": ["15", 0], "guider": ["14", 0], "sampler": ["16", 0], "sigmas": ["17", 0], "latent_image": ["13", 0]}},
        "19": {"class_type": "LTXVSeparateAVLatent", "inputs": {"av_latent": ["18", 1]}},
        "20": {"class_type": "LTXVCropGuides", "inputs": {"positive": ["11", 0], "negative": ["11", 1], "latent": ["19", 0]}},
        "21": {"class_type": "VAEDecodeTiled", "inputs": {"samples": ["20", 2], "vae": ["1", 2], "tile_size": 768, "overlap": 64, "temporal_size": 4096, "temporal_overlap": 64}},
        "22": {"class_type": "LTXVAudioVAEDecode", "inputs": {"samples": ["19", 1], "audio_vae": ["2", 0]}},
        "23": {"class_type": "CreateVideo", "inputs": {"images": ["21", 0], "audio": ["22", 0], "fps": float(FPS)}},
        "24": {"class_type": "SaveVideo", "inputs": {"video": ["23", 0], "filename_prefix": prefix, "format": "auto", "codec": "auto"}},
    }


for job in json.load(open(sys.argv[1])):
    g = graph(job["prompt"], job["seed"], job["image"], f"slowlight/ltx/{job['name']}_s{job['seed']}",
              job.get("frames", 97), job.get("width", 704), job.get("height", 1280), job.get("strength", 1.0))
    out = subprocess.run(["curl", "-sS", "-m", "60", "-H", "Content-Type: application/json", "-d", "@-", B + "/prompt"],
                         input=json.dumps({"prompt": g}), capture_output=True, text=True).stdout
    print(job["name"], job["seed"], out.strip()[:400])
