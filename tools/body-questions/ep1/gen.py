import json,os,urllib.request,sys,concurrent.futures as cf
S={
"drop_hit":("single crisp water droplet plop with a deep cinematic sub boom impact, clean, close mic",1.5),
"punch":("fast short whoosh into a tight punchy impact, cinematic trailer swipe",0.8),
"cut_tick":("short crisp cinematic snap transition hit, glassy",0.6),
"nerve_zap":("soft electric shimmer zap rising, warm glowing energy sparkle, neural signal",1.2),
"heartbeat":("slow deep muffled heartbeat inside the body, two beats, warm low thump",2.5),
"squeeze":("low rubbery squeezing tightening sound, tendon tension creak, organic",1.5),
"skin_crinkle":("slow wet rubbery skin crinkling and folding, organic squelch texture, close up",3.5),
"proof_hit":("massive cinematic boom hit with a short reverb tail, dramatic reveal",2.0),
"whoosh":("smooth airy whoosh transition, soft",1.0),
"water_drain":("water trickling and draining through small channels, gentle running droplets, close",3.5),
"splash_soft":("soft hand lifting out of bath water, gentle splash and drips",2.0),
"pop":("cute soft bubble pop ui sound",0.5),
"bath_amb":("calm warm bathroom ambience, faint water lapping in a bathtub, quiet room tone",10.0),
}
def go(k):
    if os.path.exists(k+'.mp3'): return k,'skip'
    t,d=S[k]
    body=json.dumps({"text":t,"duration_seconds":d,"prompt_influence":0.5}).encode()
    r=urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation",data=body,headers={"xi-api-key":os.environ["ELEVENLABS_API_KEY"],"Content-Type":"application/json"})
    open(k+'.mp3','wb').write(urllib.request.urlopen(r).read());return k,'ok'
with cf.ThreadPoolExecutor(5) as ex:
    for k,s in ex.map(go,S): print(k,s)
