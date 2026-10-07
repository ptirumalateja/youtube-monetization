#!/usr/bin/env python3
"""Queue Qwen-Image-Edit 2511 jobs on the Slow Light ComfyUI pod.

Usage: qwen_edit.py JOBS.json   (list of {"name", "prompt", "seed", "image"?, "image2"?, "steps"?, "cfg"?, "lora"?, "neg"?})
Defaults are the fast 4-step Lightning draft; set lora=false, steps=40, cfg=4 for full quality.
Refine a draft: "init" (an input-folder image) + "denoise" (~0.5) keeps its composition.
Submits via curl (Cloudflare blocks Python's default user agent).
"""
import json, os, subprocess, sys

B = os.environ.get("COMFY_URL", "https://l1rnmkhcwsgzh6-8188.proxy.runpod.net")
W, H = 928, 1664  # 9:16


def graph(prompt, seed, image, prefix, steps=4, cfg=1.0, lora=True, neg="", init=None, denoise=1.0, image2=None):
    g = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_edit_2511_fp8mixed.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors", "strength_model": 1.0 if lora else 0.0}},
        "3": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["2", 0], "shift": 3.1}},
        "4": {"class_type": "CFGNorm", "inputs": {"model": ["3", 0], "strength": 1.0}},
        "5": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image", "device": "default"}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "7": {"class_type": "LoadImage", "inputs": {"image": image}},
        "8": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["5", 0], "vae": ["6", 0], "image1": ["7", 0], "prompt": prompt}},
        "9": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["5", 0], "vae": ["6", 0], "image1": ["7", 0], "prompt": neg}},
        "10": {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["8", 0], "reference_latents_method": "index_timestep_zero"}},
        "11": {"class_type": "FluxKontextMultiReferenceLatentMethod", "inputs": {"conditioning": ["9", 0], "reference_latents_method": "index_timestep_zero"}},
        "12": {"class_type": "EmptySD3LatentImage", "inputs": {"width": W, "height": H, "batch_size": 1}},
        "13": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["10", 0], "negative": ["11", 0], "latent_image": ["12", 0],
                "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "14": {"class_type": "VAEDecode", "inputs": {"samples": ["13", 0], "vae": ["6", 0]}},
        "15": {"class_type": "SaveImage", "inputs": {"images": ["14", 0], "filename_prefix": prefix}},
    }
    if image2:  # second reference picture (e.g. a character plus a prop)
        g["23"] = {"class_type": "LoadImage", "inputs": {"image": image2}}
        for n in ("8", "9"):
            g[n]["inputs"]["image2"] = ["23", 0]
    if init:  # refine an existing draft: start from its latent, keep the composition
        g["20"] = {"class_type": "LoadImage", "inputs": {"image": init}}
        g["21"] = {"class_type": "ImageScale", "inputs": {"image": ["20", 0], "upscale_method": "lanczos", "width": W, "height": H, "crop": "center"}}
        g["22"] = {"class_type": "VAEEncode", "inputs": {"pixels": ["21", 0], "vae": ["6", 0]}}
        g["13"]["inputs"]["latent_image"] = ["22", 0]
        g["13"]["inputs"]["denoise"] = denoise
    if image is None:  # text-to-image: no reference picture
        del g["7"]
        for n in ("8", "9"):
            del g[n]["inputs"]["image1"]
    return g


for job in json.load(open(sys.argv[1])):
    g = graph(job["prompt"], job["seed"], job.get("image"), f"slowlight/{job['name']}_s{job['seed']}",
              job.get("steps", 4), job.get("cfg", 1.0), job.get("lora", True), job.get("neg", ""),
              job.get("init"), job.get("denoise", 1.0), job.get("image2"))
    out = subprocess.run(["curl", "-sS", "-m", "60", "-H", "Content-Type: application/json", "-d", "@-", B + "/prompt"],
                         input=json.dumps({"prompt": g}), capture_output=True, text=True).stdout
    print(job["name"], job["seed"], out.strip()[:300])
