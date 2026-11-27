// node render_gfx.js OUTDIR [ID ...] [--stills]
const {chromium}=require('playwright');const {spawn}=require('child_process');const path=require('path');const fs=require('fs');
(async()=>{const out=process.argv[2];const stills=process.argv.includes('--stills');let ids=process.argv.slice(3).filter(a=>!a.startsWith('--'));
fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1920,height:1080}});
await p.goto('file://'+path.join(__dirname,'gfx.html'));await p.evaluate(()=>window.ready);
const scenes=await p.evaluate(()=>window.SCENES);if(!ids.length)ids=Object.keys(scenes);
const el=await p.$('#c');
for(const id of ids){const {d,alpha}=scenes[id];
 if(stills){for(const f of [.25,.6,.98]){await p.evaluate(([i,t])=>draw(i,t),[id,d*f]);await el.screenshot({path:`${out}/${id}_${Math.round(f*100)}.png`,omitBackground:alpha});}continue}
 const fps=30,N=Math.round(d*fps);
 const args=alpha?['-y','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','qtrle',`${out}/${id}.mov`]
   :['-y','-f','image2pipe','-framerate',''+fps,'-i','-','-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',`${out}/${id}.mp4`];
 const ff=spawn('ffmpeg',args,{stdio:['pipe','ignore','inherit']});
 for(let i=0;i<N;i++){await p.evaluate(([id,t])=>draw(id,t),[id,i/fps]);
   const buf=await el.screenshot({type:alpha?'png':'jpeg',quality:alpha?undefined:93,omitBackground:alpha});
   if(!ff.stdin.write(buf))await new Promise(r=>ff.stdin.once('drain',r));}
 ff.stdin.end();await new Promise(r=>ff.on('close',r));console.log(id,N);}
await b.close();})();
