import json,os,urllib.request,concurrent.futures as cf
S={
"freeze_hit":("massive cinematic impact boom then everything freezes, glassy time-stop shimmer tail, tyre screech cut off abruptly",2.0),
"whip":("very fast cinematic whip pan whoosh",0.5),
"brain_zap":("bright electric neural zap crackle rising quickly, glowing energy",1.0),
"foot_scrape":("sneaker scraping quickly backwards on wet asphalt",0.8),
"heart_slam":("three very fast heavy deep heartbeats, punchy, body thump",1.5),
"iris_open":("quick camera aperture iris opening with soft whoosh",0.8),
"sugar_rush":("rushing glowing liquid energy surge, sparkly whoosh building",1.6),
"tunnel":("fast flying through a tunnel whoosh, rushing liquid",1.0),
"bullet_time":("deep slow-motion bullet time whoosh, suspended rain, ethereal reverb",2.2),
"glitch_snap":("sharp record scratch snap and reality glitch",0.8),
"memory_frames":("rapid camera shutter clicks and film frames flicking, soft shimmer",2.6),
"car_pass":("car speeding past very close at high speed, loud whoosh, horn blast doppler",2.0),
"rain_start":("time resumes, heavy rain suddenly pours on a city street",2.0),
"rain_amb":("calm night city rain ambience, distant traffic hum",10.0),
"drone":("dark tense cinematic low drone, suspense, subtle",10.0),
"soft_end":("soft warm cinematic ending swell, single gentle chime",2.0),
}
def go(k):
    if os.path.exists(k+'.mp3'): return k,'skip'
    t,d=S[k]
    body=json.dumps({"text":t,"duration_seconds":d,"prompt_influence":0.5}).encode()
    r=urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation",data=body,headers={"xi-api-key":os.environ["ELEVENLABS_API_KEY"],"Content-Type":"application/json"})
    try: open(k+'.mp3','wb').write(urllib.request.urlopen(r).read());return k,'ok'
    except Exception as e: return k,str(e)
with cf.ThreadPoolExecutor(4) as ex:
    for k,s in ex.map(go,S): print(k,s)
