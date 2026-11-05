"""fetch Commons files by title (images as 1600px thumbs, videos original) + record licence/credit"""
import json, sys, subprocess, urllib.parse, os, time, re
sys.path.insert(0, os.path.dirname(__file__)); from commons import get, UA
out = sys.argv[1]; titles = sys.argv[2:]; os.makedirs(out, exist_ok=True)
cred = json.load(open(f"{out}/credits.json")) if os.path.exists(f"{out}/credits.json") else {}
for i in range(0, len(titles), 20):
    d = get({"action":"query","format":"json","titles":"|".join(titles[i:i+20]),"prop":"imageinfo","iiurlwidth":1920,
             "iiprop":"url|mime|extmetadata","iiextmetadatafilter":"LicenseShortName|Artist"})
    for pg in d["query"]["pages"].values():
        if "imageinfo" not in pg: print("MISSING", pg.get("title")); continue
        ii = pg["imageinfo"][0]; vid = ii["mime"].startswith(("video","application/ogg"))
        url = ii["url"] if vid else ii.get("thumburl", ii["url"])
        url = url.split("?")[0].replace("://thumb.wikimedia.org/", "://upload.wikimedia.org/")
        name = re.sub(r"[^A-Za-z0-9._-]+","_", pg["title"][5:])[:80]
        if not vid: name = os.path.splitext(name)[0] + ".jpg"
        p = f"{out}/{name}"
        if not os.path.exists(p):
            for k in range(8):
                r = subprocess.run(["curl","-sS","-f","-A",UA,"-o",p,url],capture_output=True)
                if r.returncode==0: break
                time.sleep(5*(k+1))
            else: print("FAIL", name); continue
        m = ii.get("extmetadata",{})
        artist = re.sub("<[^>]+>","", m.get("Artist",{}).get("value","")).strip()
        cred[name] = {"title":pg["title"],"license":m.get("LicenseShortName",{}).get("value"),"artist":artist,"page":ii.get("descriptionurl")}
        print("ok", name, cred[name]["license"]); time.sleep(2)
json.dump(cred, open(f"{out}/credits.json","w"), indent=1)
