// node dbg.js <w> <h> <out.jpg> <id> <t> "<js to run before render>"
const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const [W,H,out,id,t,js]=[+process.argv[2],+process.argv[3],process.argv[4],+process.argv[5],+process.argv[6],process.argv[7]||''];
const b=await chromium.launch({args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
await p.goto(`http://localhost:${process.env.PORT||8771}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
const d=await p.evaluate(([id,t,js])=>{ window.HOOK=js?new Function(js):null; return window.renderLook(id,t,1);},[id,t,js]); fs.writeFileSync(out,Buffer.from(d.split(',')[1],'base64')); await b.close();})();
