const {chromium}=require('/opt/node-tools/node_modules/playwright-core');
(async()=>{const W=+(process.env.W||540),H=+(process.env.H||960),out=process.argv[2],ts=process.argv.slice(3).map(Number);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}});p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));p.on('console',m=>{if(m.type()==='error')console.log('[c]',m.text().slice(0,300))});
await p.goto('http://localhost:8792/three/index9.html?w='+W+'&h='+H);await p.waitForFunction('window.ready===true',{timeout:120000});
for(const t of ts){await p.evaluate(t=>window.renderAt(t),t);await p.screenshot({path:`${out}/p_${t.toFixed(2)}.jpg`,type:'jpeg',quality:85});}
await b.close();})();
