import json, sys, subprocess, urllib.parse, time
UA="SlowLightReel/1.0 (https://github.com/ptirumalateja/youtube-monetization)"
def get(p):
    u="https://commons.wikimedia.org/w/api.php?"+urllib.parse.urlencode(p)
    for i in range(10):
        r=subprocess.run(["curl","-sS","-A",UA,u],capture_output=True,text=True)
        try: return json.loads(r.stdout)
        except Exception: time.sleep(15*(i+1))
    raise SystemExit(r.stdout[:300])
def q(s, n=15):
    d=get({"action":"query","format":"json","generator":"search","gsrsearch":s,"gsrnamespace":6,"gsrlimit":n,
         "prop":"imageinfo","iiprop":"url|size|mime|extmetadata","iiextmetadatafilter":"LicenseShortName|Artist"})
    out=[]
    for pg in d.get("query",{}).get("pages",{}).values():
        ii=pg["imageinfo"][0]; m=ii.get("extmetadata",{})
        out.append((pg["title"], ii["mime"], ii.get("width"), ii.get("height"), ii.get("duration"), m.get("LicenseShortName",{}).get("value"), ii["url"]))
    return out
if __name__=="__main__":
    for s in sys.argv[1:]:
        time.sleep(1.5); print("###", s)
        for t in q(s): print(" ", t[1], t[2], "x", t[3], round(t[4] or 0,1), t[5], "|", t[0][:90])
