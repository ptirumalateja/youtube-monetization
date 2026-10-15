// usage: node render2.js <outdir> <fps> <t0> <t1> [worker workers]   (needs python3 -m http.server 8792 in tools/tickle)
const {chromium}=require('/opt/node-tools/node_modules/playwright-core');
const fs=require('fs');
(async()=>{
  const [out,fps,t0,t1,wi,wn]=[process.argv[2],+process.argv[3],+process.argv[4],+process.argv[5],+(process.argv[6]||0),+(process.argv[7]||1)];
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
  const p=await b.newPage({viewport:{width:+(process.env.W||1080),height:+(process.env.H||1920)}});
  p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
  p.on('console',m=>{if(m.type()==='error')console.log('[console]',m.text().slice(0,300))});
  await p.goto('http://localhost:8792/three/index11.html?w='+(process.env.W||1080)+'&h='+(process.env.H||1920)+'');
  await p.waitForFunction('window.ready===true',{timeout:120000});
  const f0=Math.round(t0*fps),f1=Math.round(t1*fps),tt=Date.now();
  for(let f=f0+wi;f<=f1;f+=wn){await p.evaluate(t=>window.renderAt(t),f/fps);await p.screenshot({path:`${out}/f${String(f).padStart(5,'0')}.jpg`,type:'jpeg',quality:93});console.log('frame',f,((Date.now()-tt)/1000).toFixed(1)+'s');}
  await b.close();
})();
