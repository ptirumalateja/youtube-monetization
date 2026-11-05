"""Openverse helper (images download via the API's own thumb proxy; flickr/wikimedia hosts are blocked here).
python3 ov.py search NAME "query" [n]   -> bg/NAME/cands.json + contact sheet bg/NAME/sheet.jpg
python3 ov.py get NAME idx              -> bg/NAME.jpg (full size) + credits line in bg/credits.txt"""
import json, sys, os, time, subprocess, urllib.parse
from PIL import Image, ImageDraw
API = 'https://api.openverse.org/v1/images/'
def curl(url, out=None):
    for i in range(4):
        r = subprocess.run(['curl', '-s', '-m', '40', '-w', '%{http_code}', '-o', out or '/dev/stdout', url], capture_output=True)
        code = r.stdout[-3:].decode() if out else r.stdout[-3:].decode()
        if code == '200': return r.stdout[:-3]
        time.sleep(2 * (i + 1))
    raise SystemExit(f'fail {code} {url}')
cmd, name = sys.argv[1], sys.argv[2]; d = f'bg/{name}'; os.makedirs(d, exist_ok=True)
if cmd == 'search':
    n = int(sys.argv[4]) if len(sys.argv) > 4 else 12
    q = urllib.parse.urlencode({'q': sys.argv[3], 'page_size': 20, 'license_type': 'commercial', 'mature': 'false'})
    res = json.loads(curl(API + '?' + q))['results']
    res = [r for r in res if (r.get('height') or 0) >= 600][:n]
    json.dump(res, open(f'{d}/cands.json', 'w'), indent=1)
    tiles = []
    for i, r in enumerate(res):
        p = f'{d}/c{i}.jpg'
        try: curl(API + r['id'] + '/thumb/', p); im = Image.open(p).convert('RGB')
        except BaseException: im = Image.new('RGB', (300, 300))
        im.thumbnail((300, 300)); t = Image.new('RGB', (300, 300)); t.paste(im, ((300 - im.width) // 2, (300 - im.height) // 2))
        ImageDraw.Draw(t).text((6, 4), f'{i} {r["width"]}x{r["height"]} {r["license"]}', fill=(255, 255, 0)); tiles.append(t); time.sleep(0.4)
    cols = 4; sh = Image.new('RGB', (300 * cols, 300 * ((len(tiles) + cols - 1) // cols)))
    for i, t in enumerate(tiles): sh.paste(t, (300 * (i % cols), 300 * (i // cols)))
    sh.save(f'{d}/sheet.jpg'); print(len(tiles), 'cands')
else:
    r = json.load(open(f'{d}/cands.json'))[int(sys.argv[3])]
    curl(API + r['id'] + '/thumb/?full_size=true', f'bg/{name}.jpg'); print(Image.open(f'bg/{name}.jpg').size)
    lines = [l for l in open('bg/credits.txt').read().splitlines() if not l.startswith(name + ':')] if os.path.exists('bg/credits.txt') else []
    lines.append(f'{name}: "{r["title"]}" by {r.get("creator")} ({r["license"].upper()} {r.get("license_version","")}) {r["foreign_landing_url"]}')
    open('bg/credits.txt', 'w').write('\n'.join(lines) + '\n')
