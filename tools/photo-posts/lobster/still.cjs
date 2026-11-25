// node still.cjs OUT.png [W H]   render the scene once (headless Chromium, SwiftShader) to a PNG
const { chromium } = require('playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, out = process.argv[2] || path.join(root, 'still.png');
const W = +(process.argv[3] || 2160), H = +(process.argv[4] || 2700);
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } });
});
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try {
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}&${process.env.QS || ''}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
    const b64 = await page.evaluate(() => window.render());
    fs.writeFileSync(out, Buffer.from(b64.split(',')[1], 'base64')); console.log('wrote', out);
  } finally { await browser.close(); server.close(); }
})();
