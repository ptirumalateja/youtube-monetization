// node render.js W H outdir port worker nworkers  -> frames f0000.jpg.. (interleaved across workers), motion-blurred
const {chromium}=require('playwright-core');const fs=require('fs');
(async()=>{const [W,H,out,port,wi,nw]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});const FPS=30;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:+W,height:+H}});p.on('pageerror',e=>console.log('[err]',e.message));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`);await p.waitForFunction('window.ready===true',{timeout:120000});
const DUR=await p.evaluate(()=>window.DUR);const NF=Math.round(DUR*FPS);
for(let f=+wi;f<NF;f+=+nw){const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`;if(fs.existsSync(fn))continue;const t=f/FPS;
  // more sub-frames where things move fast (time-lapse strikes, the rush in, the break, the crane, the rewind dive)
  const n=(t>3.6&&t<15.7)||(t>16.55&&t<21.7)||(t>23.5)?5:3;
  const d=await p.evaluate(([t,n])=>window.renderAt(t,n),[t,n]);fs.writeFileSync(fn,Buffer.from(d.split(',')[1],'base64'));if(f%60<+nw)console.log('frame',f);}
await b.close();})();
