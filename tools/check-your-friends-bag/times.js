// node times.js port out.json -> the timeline plus per-frame overlay data (label anchors, ROCK counter) for compose.py and mix.py
const fs=require('fs');const {open}=require('./browser.js');
(async()=>{const [port,out]=process.argv.slice(2);const {b,p}=await open(1080,1920,port);
const r=await p.evaluate(()=>{const FPS=30,NF=Math.round(window.DUR*FPS),frames=[];for(let f=0;f<NF;f++)frames.push(window.metaAt(f/FPS));return {...window.TL,dur:window.DUR,frames};});
let prev=0;r.frames.forEach((m,f)=>{if(m.counter<prev)throw Error('ROCK counter goes backwards at frame '+f);prev=m.counter;});
fs.writeFileSync(out,JSON.stringify(r));console.log('frames',r.frames.length,'counter monotonic, final',prev);await b.close();})();
