// PAGE=index.html|scenes.html SS=1.25 node render.js W H outdir startFrame endFrame step
// Renders only frames the page wants (window.want(t)); writes f####.jpg and proj_<start>.json (screen positions for the overlay).
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],b2=+process.argv[6],step=+process.argv[7]||1,FPS=30; fs.mkdirSync(out,{recursive:true});
const page=process.env.PAGE||'index.html';
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:8778/${page}?w=${W}&h=${H}&ss=${process.env.SS||1}`); await p.waitForFunction('window.ready===true',{timeout:180000});
const PJ={};
for(let f=a;f<b2;f+=step){ const t=f/FPS; if(!(await p.evaluate(t=>window.want(t),t))) continue;
  const d=await p.evaluate(t=>window.renderAt(t,1,3),t); PJ[f]=await p.evaluate(()=>window.lastProj||null);
  fs.writeFileSync(`${out}/f${String(f).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); if(f%30<step) console.log('frame',f); }
fs.writeFileSync(`${out}/proj_${page}_${a}.json`,JSON.stringify(PJ)); await b.close();})();
