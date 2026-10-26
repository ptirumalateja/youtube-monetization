// env TL=timeline-26s.json renders the 26 s FB cut from the same scene
// node render.cjs stills            review stills (TIMES=0.5,2.9 to pick) -> $OUT/still-*.jpg
// node render.cjs meta              per-frame overlay/sound data + monotonic AGE / friend-count check -> $OUT/meta.json
// node render.cjs frames WORKER N   render every Nth frame starting at WORKER -> $OUT/frames/f00000.jpg
// env: W, H (render size, default 1080x1920), SUB (motion-blur sub-frames, default 3), OUT (default ./output)
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, out = process.env.OUT || path.join(root, 'output'); fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
const TLF = process.env.TL || 'timeline.json';
const spec = JSON.parse(fs.readFileSync(path.join(root, TLF), 'utf8'));
const total = Math.round(spec.duration * spec.fps);
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } });
});
(async () => {
  const [mode, a1, a2] = process.argv.slice(2);
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try {
    const W = Number(process.env.W || 1080), H = Number(process.env.H || 1920), SUB = Number(process.env.SUB || 3);
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('[console]', m.text()); });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}&tl=${TLF}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
    const shot = async (t, file) => { const b64 = await page.evaluate(([t, k]) => window.renderAt(t, k), [t, SUB]); fs.writeFileSync(file, Buffer.from(b64.split(',')[1], 'base64')); };
    if (mode === 'stills') {
      const times = process.env.TIMES ? process.env.TIMES.split(',').map(Number) : spec.reviewTimes;
      for (const t of times) { const t0 = Date.now(); await shot(t, path.join(out, `still-${t.toFixed(2).padStart(5, '0')}.jpg`)); console.log('still', t, Date.now() - t0, 'ms'); }
    } else if (mode === 'meta') {
      const meta = await page.evaluate(({ total, fps }) => { const m = []; for (let f = 0; f < total; f++) m.push(window.metaAt(f / fps)); return { frames: m, events: window.events }; }, { total, fps: spec.fps });
      let age = 0; meta.frames.forEach((m, f) => { if (m.age < age) throw Error(`AGE goes backwards at frame ${f}`); age = m.age; });
      console.log('age monotonic: ok;', meta.frames[0].age, '->', age);
      fs.writeFileSync(path.join(out, 'meta.json'), JSON.stringify(meta));
    } else if (mode === 'frames') {
      const wk = Number(a1 || 0), n = Number(a2 || 1); const t0 = Date.now();
      for (let f = wk; f < total; f += n) {
        const file = path.join(out, 'frames', `f${String(f).padStart(5, '0')}.jpg`); if (fs.existsSync(file) && !process.env.FORCE) continue;
        await shot(f / spec.fps, file + '.tmp'); fs.renameSync(file + '.tmp', file);
        if ((f - wk) % (n * 10) === 0) console.log(`w${wk} frame ${f}/${total} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      }
    }
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
