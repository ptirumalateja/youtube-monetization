"""Fixed job list for the mosquito Reel: Wan 2.2 TI2V 5B clips via local ComfyUI.
Runs on the GPU box (ComfyUI on 127.0.0.1:8188). Outputs: /root/out/<name>.mp4 (24 fps, 704x1280)."""
import json, os, subprocess, sys, time, urllib.request, uuid

API = "http://127.0.0.1:8188"
OUT = "/root/out"
COMFY_OUT = "/root/ComfyUI/output"
COMFY_IN = "/root/ComfyUI/input"
PREFIX = ("Photorealistic cinematic footage, 35 mm lens, natural muted colour, deep navy and teal night tones "
          "with faint warm highlights, subtle film grain, vertical 9:16. ")
NEG = ("text, captions, subtitles, logos, watermark, UI, graphics, overlays, glowing lines, wireframe, "
       "cartoon, 3d render, blurry, deformed, low quality")
FRAMES = 121  # ~5 s at 24 fps

JOBS = [  # name, prompt, start_image_from (job name or None)
    ("A", "Extreme macro of an Aedes mosquito about to bite glistening skin, then the camera pulls back fast to reveal "
          "hundreds of mosquitoes in warm humid dusk air, backlit by a faint teal glow, fine legs and beating wings "
          "visible. One continuous shot.", None),
    ("F", "A single mosquito hovers facing the camera against a dark background, wings beating in a blur, then slowly "
          "descends and lands on glistening skin, legs touching down, about to bite. Shallow depth of field, slight push-in.", None),
    ("C", "Extreme macro of a small wild bog orchid, blunt-leaf orchid Platanthera obtusata: a slender spike of tiny pale "
          "green-white flowers with one blunt basal leaf, in a damp northern bog at dusk, soft navy-teal background. "
          "Shallow depth of field, locked camera.", None),
    ("G", "A wading bird in a wetland at dusk, wings half open, snapping its beak at empty air over still water; clear "
          "air, no insects; soft teal-navy light, shallow depth of field.", None),
    ("I", "Earth from space with a slow pull-back as the sun rises over the horizon, thin atmosphere glow, black star "
          "field, city lights on the night side. Smooth, no overlays.", None),
    ("B", "Earth from space centred on Africa and Europe, thin atmosphere glow, black star field, slow smooth push-in. "
          "The camera dives through white cloud, descends over the Arctic and settles low over a calm summer tundra at "
          "dusk with shallow pools and cotton grass, about thirty caribou grazing peacefully. The air is clear and still, "
          "no insects. One continuous smooth shot.", None),
    ("E", "The same tundra plain ten years later at dusk, caribou still grazing, and the air now holds a thin drifting "
          "haze of tiny non-biting flies and midges rising from the pools. Camera drifts slowly forward. No mosquitoes.", "B"),
]


def workflow(prompt, seed, prefix, start_image=None):
    w = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "wan2.2_ti2v_5B_fp16.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "umt5_xxl_fp8_e4m3fn_scaled.safetensors", "type": "wan", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "wan2.2_vae.safetensors"}},
        "4": {"class_type": "ModelSamplingSD3", "inputs": {"model": ["1", 0], "shift": 8.0}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": PREFIX + prompt}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 0], "text": NEG}},
        "7": {"class_type": "Wan22ImageToVideoLatent",
              "inputs": {"vae": ["3", 0], "width": 704, "height": 1280, "length": FRAMES, "batch_size": 1}},
        "8": {"class_type": "KSampler",
              "inputs": {"model": ["4", 0], "positive": ["5", 0], "negative": ["6", 0], "latent_image": ["7", 0],
                         "seed": seed, "steps": 25, "cfg": 5.0, "sampler_name": "uni_pc", "scheduler": "simple", "denoise": 1.0}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}},
    }
    if start_image:
        w["11"] = {"class_type": "LoadImage", "inputs": {"image": start_image}}
        w["7"]["inputs"]["start_image"] = ["11", 0]
    return w


def post(path, data):
    r = urllib.request.Request(API + path, json.dumps(data).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(r))


def run(name, prompt, start, variant):
    prefix = f"{name}_v{variant}"
    start_img = None
    if start:
        src = f"{OUT}/{start}_v{variant}.mp4"
        if not os.path.exists(src):
            src = f"{OUT}/{start}_v0.mp4"
        start_img = f"{name}_start.png"
        subprocess.run(["ffmpeg", "-y", "-sseof", "-0.1", "-i", src, "-frames:v", "1", f"{COMFY_IN}/{start_img}"], check=True)
    pid = post("/prompt", {"prompt": workflow(prompt, 1000 + variant, prefix, start_img), "client_id": str(uuid.uuid4())})["prompt_id"]
    while True:
        h = json.load(urllib.request.urlopen(f"{API}/history/{pid}"))
        if pid in h:
            st = h[pid]["status"]
            if st.get("status_str") == "error":
                print("FAILED", prefix, json.dumps(st)[:2000], flush=True)
                return False
            break
        time.sleep(10)
    subprocess.run(f"ffmpeg -y -framerate 24 -i {COMFY_OUT}/{prefix}_%05d_.png -c:v libx264 -crf 14 -pix_fmt yuv420p {OUT}/{prefix}.mp4",
                   shell=True, check=True)
    print("DONE", prefix, time.strftime("%H:%M:%S"), flush=True)
    return True


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for _ in range(60):  # wait for ComfyUI
        try:
            urllib.request.urlopen(API + "/system_stats"); break
        except Exception:
            time.sleep(10)
    variants = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    for v in range(variants):
        for name, prompt, start in JOBS:
            if not os.path.exists(f"{OUT}/{name}_v{v}.mp4"):
                run(name, prompt, start, v)
    print("ALL_JOBS_DONE", flush=True)
