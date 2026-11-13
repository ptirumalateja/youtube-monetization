const {chromium}=require('playwright');
(async()=>{const [,,page,out]=process.argv;const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader','--allow-file-access-from-files']});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));p.on('console',m=>{if(!m.text().includes('GL Driver'))console.log(m.text())});
await p.goto('http://localhost:8765/'+page);await p.waitForFunction('window.DONE',null,{timeout:600000});
await (await p.$('#c')).screenshot({path:out,type:'jpeg',quality:92});await b.close();})();
