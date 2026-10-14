// usage: node render.js <outdir> <shot: hook|brain> <fps> <t0> <t1> [worker workers]
const {chromium}=require('/opt/node-tools/node_modules/playwright-core');
const fs=require('fs'),path=require('path');
(async()=>{
  const [out,shot,fps,t0,t1,wi,wn]=[process.argv[2],process.argv[3],+process.argv[4],+process.argv[5],+process.argv[6],+(process.argv[7]||0),+(process.argv[8]||1)];
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
  await p.goto('file://'+path.resolve(__dirname,'index.html')+'?shot='+shot);
  await p.waitForFunction('window.ready===true');
  const f0=Math.round(t0*fps),f1=Math.round(t1*fps);
  for(let f=f0+wi;f<=f1;f+=wn){await p.evaluate(([t,f])=>window.renderAt(t,f),[f/fps,f]);await p.screenshot({path:`${out}/${shot}_f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:93});}
  await b.close();
})();
