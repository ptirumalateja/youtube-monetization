const {chromium}=require('playwright');const http=require('http');const fs=require('fs');const path=require('path');
const root=__dirname;
const srv=http.createServer((q,r)=>{let p=path.join(root,decodeURIComponent(q.url.split('?')[0]));if(!fs.existsSync(p)){r.writeHead(404);r.end();return;}
 const ext=path.extname(p);r.writeHead(200,{'Content-Type':ext=='.js'?'text/javascript':ext=='.html'?'text/html':'application/octet-stream'});fs.createReadStream(p).pipe(r);}).listen(8137);
(async()=>{
 const [,,out,times]=process.argv; fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const pg=await b.newPage({viewport:{width:1080,height:1920}});
 pg.on('console',m=>console.log('C:',m.text()));pg.on('pageerror',e=>console.log('E:',e.message));
 await pg.goto('http://localhost:8137/scene.html');await pg.waitForFunction('window.ready===true',null,{timeout:60000});
 await pg.evaluate(()=>document.fonts.load('800 78px "Inter Display"'));
 let ts;
 if(times.startsWith('all:')){const [a,b2,fps]=times.slice(4).split(',').map(Number);ts=[];for(let f=Math.round(a*fps);f<Math.round(b2*fps);f++)ts.push([f,f/fps]);}
 else ts=times.split(',').map((x,i)=>[i,+x]);
 for(const [f,t] of ts){await pg.evaluate(t=>window.renderAt(t),t);
   await pg.screenshot({path:`${out}/f${String(f).padStart(4,'0')}.png`,clip:{x:0,y:0,width:1080,height:1920}});
   if(f%30==0)console.log('frame',f);}
 await b.close();srv.close();})();
