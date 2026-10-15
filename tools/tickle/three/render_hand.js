// usage: node render_hand.js <outdir> ; renders isolated hand views for modelling checks
const {chromium}=require('/opt/node-tools/node_modules/playwright-core');
const fs=require('fs');
(async()=>{
  const out=process.argv[2]; fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
  const p=await b.newPage({viewport:{width:1080,height:1350}});
  p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
  await p.goto('http://localhost:8792/three/index2.html?w=1080&h=1350'); await p.waitForFunction('window.ready===true',{timeout:120000});
  const views=[['point',0,0.15],['point',0.6,0.35],['reach',0,0.2],['reach',0.5,0.55],['reach',0.15,1.2]];
  for(const [i,[pose,yaw,pitch]] of views.entries()){await p.evaluate(([a,y,q])=>window.renderHand(a,y,q,62),[pose,yaw,pitch]);await p.screenshot({path:`${out}/h${i}_${pose}.jpg`,type:'jpeg',quality:92});console.log('view',i);}
  await b.close();
})();
