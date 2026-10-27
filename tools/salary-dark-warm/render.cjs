// node render.cjs stills                 env TIMES=0,3.5,10 -> $OUT/still-*.jpg
// node render.cjs frames WORKER N        every Nth frame from WORKER -> $OUT/frames/f00000.jpg      (env W,H,SUB,OUT,FORCE)
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, out = process.env.OUT || path.join(root, 'output'); fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
const spec = JSON.parse(fs.readFileSync(path.join(root, 'timeline.json'), 'utf8')); const total = Math.round(spec.duration * spec.fps);
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => { const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } }); });
(async () => {
  const [mode, a1, a2] = process.argv.slice(2); await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try { const W = +process.env.W || 1080, H = +process.env.H || 1920, SUB = +process.env.SUB || 3;
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exit(1); }); page.on('console', m => { if (m.type() === 'error') console.error('[console]', m.text()); });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
    const shot = async (t, file) => { const b64 = await page.evaluate(([t, k]) => window.renderAt(t, k), [t, SUB]); fs.writeFileSync(file, Buffer.from(b64.split(',')[1], 'base64')); };
    if (mode === 'stills') { for (const t of (process.env.TIMES || '0').split(',').map(Number)) { const t0 = Date.now(); await shot(t, path.join(out, `still-${t.toFixed(2).padStart(5, '0')}.jpg`)); console.log('still', t, Date.now() - t0, 'ms'); } }
    else if (mode === 'frames') { const wk = +a1 || 0, n = +a2 || 1; const t0 = Date.now();
      for (let f = wk; f < total; f += n) { const file = path.join(out, 'frames', `f${String(f).padStart(5, '0')}.jpg`); if (fs.existsSync(file) && !process.env.FORCE) continue;
        await shot(f / spec.fps, file + '.tmp'); fs.renameSync(file + '.tmp', file); if ((f - wk) % (n * 10) === 0) console.log(`w${wk} frame ${f}/${total} ${((Date.now() - t0) / 1000).toFixed(0)}s`); } }
  } finally { await browser.close(); server.close(); } })().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
