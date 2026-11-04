#!/usr/bin/env python3
"""Search/download free-licensed audio or images from Openverse (WordPress/openverse API, no key needed).
Usage: openverse.py audio "whoosh" [-n 10] [--license cc0,pdm] [--get DIR]
       openverse.py images "milky way" --license cc0
Note: api.openverse.org is blocked in the cloud container; run this on the Mac."""
import argparse, json, os, urllib.parse, urllib.request

ap = argparse.ArgumentParser()
ap.add_argument("kind", choices=["audio", "images"]); ap.add_argument("q")
ap.add_argument("-n", type=int, default=10); ap.add_argument("--license", default="cc0,pdm,by")
ap.add_argument("--get", metavar="DIR", help="download all results into DIR")
a = ap.parse_args()
url = f"https://api.openverse.org/v1/{a.kind}/?" + urllib.parse.urlencode(
    {"q": a.q, "license": a.license, "page_size": a.n})
req = urllib.request.Request(url, headers={"User-Agent": "slowlight-tools"})
res = json.load(urllib.request.urlopen(req, timeout=30))["results"]
for r in res:
    dur = f"{r.get('duration', 0) / 1000:.1f}s " if a.kind == "audio" and r.get("duration") else ""
    print(f"{r['id']}  {dur}{r['license']}  {r['title'][:60]}  by {r.get('creator')}\n    {r['url']}")
    if a.get:
        os.makedirs(a.get, exist_ok=True)
        ext = os.path.splitext(urllib.parse.urlparse(r["url"]).path)[1] or ".bin"
        urllib.request.urlretrieve(r["url"], os.path.join(a.get, r["id"] + ext))
        with open(os.path.join(a.get, "CREDITS.txt"), "a") as f:
            f.write(f"{r['id']}{ext}: \"{r['title']}\" by {r.get('creator')} ({r['license']}) {r.get('foreign_landing_url')}\n")
