#!/usr/bin/env python3
"""Generate all tickle plates (Qwen) with the hero hand + look still as references. Usage: POD=<id> python3 make_stills.py <scratch> [plate ...]"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sc = sys.argv[1]; only = sys.argv[2:]
spec = json.load(open(os.path.join(os.path.dirname(__file__), "plates_spec.json")))
here = os.path.dirname(os.path.abspath(__file__))
def job(item):
    name, p = item
    out = f"{sc}/plates2/{name}.png"
    cmd = ["python3", f"{here}/comfy.py", "qwen", "--ref", f"{sc}/refs/hero.png", "--ref", f"{sc}/refs/look.png",
           f"{sc}/seeds_clean/{p['seed_img']}.png", spec["prefix"] + p["prompt"], out, "41"]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(name, (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "no output", flush=True)
items = [(k, v) for k, v in spec["plates"].items() if not only or k in only]
with ThreadPoolExecutor(3) as ex: list(ex.map(job, items))
