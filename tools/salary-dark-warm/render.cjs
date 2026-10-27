// node render.cjs still OUT.jpg [v=after|before] [cam=JSON]   env W,H,SUB   -> one 3D still (no text)
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => { const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } }); });
(async () => {
  const [, out, v = 'after', cam] = process.argv.slice(2); await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try { const W = +process.env.W || 1080, H = +process.env.H || 1920, SUB = +process.env.SUB || 3;
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; }); page.on('console', m => { if (m.type() === 'error') console.error('[console]', m.text()); });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}&v=${v}${cam ? '&cam=' + encodeURIComponent(cam) : ''}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
    const b64 = await page.evaluate(k => window.renderAt(5, k), SUB); fs.writeFileSync(out, Buffer.from(b64.split(',')[1], 'base64')); console.log('ok', out);
  } finally { await browser.close(); server.close(); } })().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
