#!/usr/bin/env python3
"""ComfyUI client for the tickle reel plates (RunPod pod, models on the slowlight-100 volume).

  POD=<podid> python3 comfy.py qwen <seed.png> "<prompt>" <out.png> [seed] [WxH]
  POD=<podid> python3 comfy.py wan  <still.png> "<prompt>" <out.mp4> [frames] [seed] [WxH]

qwen: Qwen Image Edit 2511 (+Lightning 4-step) re-renders a storyboard panel as a 9:16 still.
wan : Wan 2.2 I2V 14B (high/low noise, lightx2v 4-step LoRAs) animates a still (16 fps).
Stop the pod when done (see claude.md rule 8).
"""
import json, os, sys, time, uuid
import requests

POD = os.environ["POD"]
BASE = f"https://{POD}-8188.proxy.runpod.net"
H = {"User-Agent": "curl/8.5.0"}


def upload(path):
    with open(path, "rb") as f:
        r = requests.post(f"{BASE}/upload/image", headers=H, files={"image": (os.path.basename(path), f)}, data={"overwrite": "true"}, timeout=120)
    r.raise_for_status()
    return r.json()["name"]


def run(graph, out_node, timeout=1500):
    cid = str(uuid.uuid4())
    r = requests.post(f"{BASE}/prompt", headers=H, json={"prompt": graph, "client_id": cid}, timeout=60)
    if r.status_code != 200:
        raise SystemExit("queue failed: " + r.text[:1500])
    pid = r.json()["prompt_id"]
    t0 = time.time()
    while time.time() - t0 < timeout:
        h = requests.get(f"{BASE}/history/{pid}", headers=H, timeout=60).json()
        if pid in h:
            st = h[pid]["status"]
            if st.get("status_str") == "error":
                raise SystemExit("run error: " + json.dumps(st)[:2000])
            if st.get("completed"):
                return h[pid]["outputs"][out_node], time.time() - t0
        time.sleep(3)
    raise SystemExit("timeout")


def fetch(item, dest):
    r = requests.get(f"{BASE}/view", headers=H, params={"filename": item["filename"], "subfolder": item.get("subfolder", ""), "type": item.get("type", "output")}, timeout=300)
    r.raise_for_status()
    open(dest, "wb").write(r.content)


def qwen_graph(img, prompt, seed, w, h):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_edit_2511_fp8mixed.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16.safetensors", "strength_model": 1.0}},
        "3": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["2", 0], "shift": 3.0}},
        "4": {"class_type": "CFGNorm", "inputs": {"model": ["3", 0], "strength": 1.0}},
        "5": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image", "device": "default"}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "7": {"class_type": "LoadImage", "inputs": {"image": img}},
        "8": {"class_type": "ImageScaleToTotalPixels", "inputs": {"image": ["7", 0], "upscale_method": "lanczos", "megapixels": 1.0, "resolution_steps": 1}},
        "9": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["5", 0], "prompt": prompt, "vae": ["6", 0], "image1": ["8", 0]}},
        "10": {"class_type": "TextEncodeQwenImageEditPlus", "inputs": {"clip": ["5", 0], "prompt": "", "vae": ["6", 0], "image1": ["8", 0]}},
        "11": {"class_type": "EmptySD3LatentImage", "inputs": {"width": w, "height": h, "batch_size": 1}},
        "12": {"class_type": "KSampler", "inputs": {"model": ["4", 0], "positive": ["9", 0], "negative": ["10", 0], "latent_image": ["11", 0], "seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "denoise": 1.0}},
        "13": {"class_type": "VAEDecode", "inputs": {"samples": ["12", 0], "vae": ["6", 0]}},
        "14": {"class_type": "SaveImage", "inputs": {"images": ["13", 0], "filename_prefix": "tickle/qwen"}},
    }


NEG = "blurry, low quality, text, watermark, subtitles, extra fingers, deformed hands, morphing, cartoon, bright daylight, overexposed"


def wan_graph(img, prompt, seed, w, h, frames):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "3": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["1", 0], "lora_name": "wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors", "strength_model": 1.0}},
        "4": {"class_type": "LoraLoaderModelOnly", "inputs": {"model": ["2", 0], "lora_name": "wan2.2_i2v_lightx2v_4steps_lora_v1_low_noise.safetensors", "strength_model": 1.0}},
        "5": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["3", 0], "shift": 5.0}},
        "6": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["4", 0], "shift": 5.0}},
        "7": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
        "8": {"class_type": "VAELoader", "inputs": {"vae_name": "wan_2.1_vae.safetensors"}},
        "9": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["7", 0], "text": prompt}},
        "10": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["7", 0], "text": NEG}},
        "11": {"class_type": "LoadImage", "inputs": {"image": img}},
        "12": {"class_type": "ImageScale", "inputs": {"image": ["11", 0], "upscale_method": "lanczos", "width": w, "height": h, "crop": "center"}},
        "13": {"class_type": "WanImageToVideo", "inputs": {"positive": ["9", 0], "negative": ["10", 0], "vae": ["8", 0], "width": w, "height": h, "length": frames, "batch_size": 1, "start_image": ["12", 0]}},
        "14": {"class_type": "KSamplerAdvanced", "inputs": {"model": ["5", 0], "add_noise": "enable", "noise_seed": seed, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["13", 0], "negative": ["13", 1], "latent_image": ["13", 2], "start_at_step": 0, "end_at_step": 2, "return_with_leftover_noise": "enable"}},
        "15": {"class_type": "KSamplerAdvanced", "inputs": {"model": ["6", 0], "add_noise": "disable", "noise_seed": 0, "steps": 4, "cfg": 1.0, "sampler_name": "euler", "scheduler": "simple", "positive": ["13", 0], "negative": ["13", 1], "latent_image": ["14", 0], "start_at_step": 2, "end_at_step": 10000, "return_with_leftover_noise": "disable"}},
        "16": {"class_type": "VAEDecode", "inputs": {"samples": ["15", 0], "vae": ["8", 0]}},
        "17": {"class_type": "CreateVideo", "inputs": {"images": ["16", 0], "fps": 16.0}},
        "18": {"class_type": "SaveVideo", "inputs": {"video": ["17", 0], "filename_prefix": "tickle/wan", "format": "mp4", "codec": "h264"}},
    }


def main():
    mode = sys.argv[1]
    if mode == "qwen":
        seedp, prompt, out = sys.argv[2:5]
        seed = int(sys.argv[5]) if len(sys.argv) > 5 else 7
        w, h = map(int, (sys.argv[6] if len(sys.argv) > 6 else "832x1472").split("x"))
        outs, dt = run(qwen_graph(upload(seedp), prompt, seed, w, h), "14")
        fetch(outs["images"][0], out)
    else:
        stillp, prompt, out = sys.argv[2:5]
        frames = int(sys.argv[5]) if len(sys.argv) > 5 else 81
        seed = int(sys.argv[6]) if len(sys.argv) > 6 else 7
        w, h = map(int, (sys.argv[7] if len(sys.argv) > 7 else "480x848").split("x"))
        outs, dt = run(wan_graph(upload(stillp), prompt, seed, w, h, frames), "18", timeout=2400)
        fetch(outs["images"][0], out)
    print(f"{mode} done in {dt:.0f}s -> {out}")


if __name__ == "__main__":
    main()
