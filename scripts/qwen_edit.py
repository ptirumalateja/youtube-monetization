#!/usr/bin/env python3
"""Queue Qwen-Image-Edit 2511 jobs on the Slow Light ComfyUI pod.

Usage: qwen_edit.py JOBS.json   (list of {"name", "prompt", "seed", "image"?})
Submits via curl (Cloudflare blocks Python's default user agent).
"""
import json, subprocess, sys

B = "https://ryj8fblndy68xx-8188.proxy.runpod.net"
W, H = 928, 1664  # 9:16


def graph(prompt, seed, image, prefix):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_edit_2511_fp8mixed.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors", "strength_model": 1.0}},
        "3": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["2", 0], "shift": 3.1}},
        "4": {"class_type": "CFGNorm", "inputs": {"model": ["3", 0], "strength": 1.0}},
        "5": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image", "device": "default"}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "7": {"class_type": "LoadImage", "inputs": {"image": image}},
        "8": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["5", 0], "vae": ["6", 0], "image1": ["7", 0], "prompt": prompt}},
        "9": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["5", 0], "vae": ["6", 0], "image1": ["7", 0], "prompt": ""}},
        "10": {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["8", 0], "reference_latents_method": "index_timestep_zero"}},
        "11": {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["9", 0], "reference_latents_method": "index_timestep_zero"}},
        "12": {"class_type": "EmptySD3LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "13": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["10", 0], "negative": ["11", 0], "latent_image": ["12", 0],
                "seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "14": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["6", 0]}},
        "15": {"class_type": "SaveImage", "inputs": {"images": ["14", 0], "filename_prefix": prefix}},
    }


for job in json.load(open(sys.argv[1])):
    g = graph(job["prompt"], job["seed"], job.get("image", "slowlight/abhimanyu_ref.png"), f"slowlight/{job['name']}_s{job['seed']}")
    out = subprocess.run(["curl", "-sS", "-m", "60", "-H", "Content-Type: application/json", "-d", "@-", B + "/prompt"],
                         input=json.dumps({"prompt": g}), capture_output=True, text=True).stdout
    print(job["name"], job["seed"], out.strip()[:300])
