// node shot.js outdir w h name:mode:age[:rot] ...   (needs `python3 -m http.server 8777` running in this folder)
const {chromium} = require('playwright-core'); const fs = require('fs');
(async () => {
  const [out, W, H, ...jobs] = process.argv.slice(2); fs.mkdirSync(out, {recursive: true});
  const b = await chromium.launch({executablePath: '/opt/pw-browsers/chromium', args: ['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist', '--use-gl=angle']});
  for (const j of jobs) {
    const [name, mode, age, rot] = j.split(':'); const t0 = Date.now();
    const p = await b.newPage({viewport: {width: +W, height: +H}});
    p.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.log('[page]', m.text().slice(0, 200)); });
    p.on('pageerror', e => console.log('[err]', e.message.slice(0, 300)));
    await p.goto(`http://localhost:8777/index.html?w=${W}&h=${H}&mode=${mode}&age=${age}&rot=${rot || 0}`);
    await p.waitForFunction('window.ready===true', {timeout: 120000});
    const d = await p.evaluate(() => window.renderStill());
    fs.writeFileSync(`${out}/${name}.jpg`, Buffer.from(d.split(',')[1], 'base64'));
    console.log(name, ((Date.now() - t0) / 1000).toFixed(1) + 's'); await p.close();
  }
  await b.close();
})();
