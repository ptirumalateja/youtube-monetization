// FROM=0 TO=690 OUT=dir node render.cjs  -> dir/f0000.jpg ... (30 fps, 23 s = 690 frames); skips frames already on disk
const { chromium } = require("playwright"); const http = require("http"), fs = require("fs"), path = require("path");
const root = __dirname, out = path.resolve(process.env.OUT || "frames"), from = +(process.env.FROM || 0), to = +(process.env.TO || 690);
fs.mkdirSync(out, { recursive: true });
const types = { ".html": "text/html", ".js": "text/javascript", ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2" };
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split("?")[0]); const f = path.join(root, u === "/" ? "index.html" : u);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { "Content-Type": types[path.extname(f)] || "application/octet-stream" }); r.end(d); }); });
srv.listen(0, "127.0.0.1", async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on("pageerror", (e) => console.log("ERR", e.message));
  await p.goto(`http://127.0.0.1:${srv.address().port}/index.html`);
  for (let i = 0; i < 600; i++) { if (await p.evaluate(() => window.ready === true)) break; await p.waitForTimeout(250); }
  await p.evaluate(() => document.fonts.ready); const t0 = Date.now();
  for (let f = from; f < to; f++) { const file = path.join(out, `f${String(f).padStart(4, "0")}.jpg`); if (fs.existsSync(file)) continue;
    await p.evaluate((t) => window.renderAt(t), f / 30); await p.screenshot({ path: file, type: "jpeg", quality: 93 });
    if (f % 30 === 0) console.log(`frame ${f} ${((Date.now() - t0) / 1000).toFixed(0)}s`); }
  console.log("done", from, to); await b.close(); srv.close();
});
