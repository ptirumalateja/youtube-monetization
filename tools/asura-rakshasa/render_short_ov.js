// node render_short_ov.js OUT.mov CUES.json DURATION [--stills t1,t2]
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');const fs=require('fs');
(async()=>{const [out,cj,dur]=process.argv.slice(2);const cues=JSON.parse(fs.readFileSync(cj));
const si=process.argv.indexOf('--stills');
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto('file://'+path.join(__dirname,'short.html'));await p.evaluate(()=>window.ready);await p.evaluate(c=>setCues(c),cues);
const el=await p.$('#c');
if(si>0){for(const t of process.argv[si+1].split(',')){await p.evaluate(t=>draw(t),+t);await el.screenshot({path:`${out}_${t}.png`,omitBackground:true})}await b.close();return}
const N=Math.round(+dur*30);const ff=spawn('ffmpeg',['-y','-loglevel','error','-f','image2pipe','-framerate','30','-i','-','-c:v','qtrle',out],{stdio:['pipe','ignore','inherit']});
for(let i=0;i<N;i++){await p.evaluate(t=>draw(t),i/30);const buf=await el.screenshot({type:'png',omitBackground:true});if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
ff.stdin.end();await new Promise(r=>ff.on('close',r));await b.close();console.log('ov',N)})();
