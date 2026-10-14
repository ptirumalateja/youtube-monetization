// usage: node render.js <outdir> <fps> <t0> <t1> [workerIndex workers]
//  stills:  node render.js out/stills 1 1.2 1.2     (one frame at 1.2 s)  -> use fps with t0..t1 inclusive
//  frames:  node render.js out/frames 30 0 32 0 4   (worker 0 of 4; frames named f00000.jpg)
const {chromium}=require('/opt/node-tools/node_modules/playwright-core');
const fs=require('fs'),path=require('path');
(async()=>{
  const [out,fps,t0,t1,wi,wn]=[process.argv[2],+process.argv[3],+process.argv[4],+process.argv[5],+(process.argv[6]||0),+(process.argv[7]||1)];
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
  p.on('console',m=>{if(m.type()==='error')console.log('[console]',m.text().slice(0,200))});
  await p.goto('file://'+path.resolve(__dirname,'index.html'));
  await p.waitForFunction('window.ready===true');
  const f0=Math.round(t0*fps), f1=Math.round(t1*fps), tt=Date.now();
  for(let f=f0+wi;f<=f1;f+=wn){
    const t=f/fps;
    await p.evaluate(([t,f])=>window.renderAt(t,f),[t,f]);
    await p.screenshot({path:`${out}/f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:93});
    if((f-f0)%(wn*30)===wi)console.log('worker',wi,'frame',f,((Date.now()-tt)/1000).toFixed(0)+'s');
  }
  await b.close();
})();
