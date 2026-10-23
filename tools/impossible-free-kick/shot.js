// node shot.js page.html W H outdir t1 t2 ...   -> outdir/t<t>.png  (single stills)
// node shot.js page.html W H outdir --range a b [step]  -> outdir/f0000.jpg frames (FPS 30)
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const [page,W,H,out,...rest]=process.argv.slice(2); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:+W,height:+H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
await p.goto(`http://localhost:${process.env.PORT||8771}/${page}?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
const save=async(t,name)=>{const r=await p.evaluate((t)=>window.renderAt(t),t); const d=typeof r==='string'?r:r.img; fs.writeFileSync(name,Buffer.from(d.split(',')[1],'base64')); return r;};
if(rest[0]==='--range'){const a=+rest[1],z=+rest[2],st=+(rest[3]||1); const meta={};
  for(let f=a;f<z;f+=st){const name=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(name)&&!process.env.FORCE){continue;} const r=await save(f/30,name); if(r.meta) meta[f]=r.meta; if(f%30===0)console.log('frame',f);}
  fs.writeFileSync(`${out}/meta_${a}_${z}.json`,JSON.stringify(meta));}
else for(const t of rest){const t0=Date.now(); await save(+t,`${out}/t${t}.jpg`); console.log(t,((Date.now()-t0)/1000).toFixed(1)+'s');}
await b.close();})();
