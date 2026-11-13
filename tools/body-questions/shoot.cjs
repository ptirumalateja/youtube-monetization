const {chromium}=require('playwright');
(async()=>{const [,,q,out]=process.argv;const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e));p.on('console',m=>console.log(m.text()));
await p.goto('file://'+__dirname+'/finger.html?'+q);await p.waitForFunction('window.DONE',null,{timeout:600000});
await (await p.$('#c')).screenshot({path:out});await b.close();})();
