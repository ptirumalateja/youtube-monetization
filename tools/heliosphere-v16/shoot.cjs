// node shoot.cjs out_dir 0,1.2,2.4   -> out_dir/t0.00.png ... (full page: WebGL + captions)
const { chromium } = require("playwright"); const http = require("http"), fs = require("fs"), path = require("path");
const root = __dirname, out = path.resolve(process.argv[2] || "stills"), times = (process.argv[3] || "0").split(",").map(Number);
fs.mkdirSync(out, { recursive: true });
const types = { ".html": "text/html", ".js": "text/javascript", ".jpg": "image/jpeg", ".png": "image/png", ".woff2": "font/woff2" };
const srv = http.createServer((q, r) => { const u = decodeURIComponent(q.url.split("?")[0]); const f = path.join(root, u === "/" ? "index.html" : u);
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; } r.writeHead(200, { "Content-Type": types[path.extname(f)] || "application/octet-stream" }); r.end(d); }); });
srv.listen(0, "127.0.0.1", async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  p.on("pageerror", (e) => console.log("ERR", e.message)); p.on("console", (m) => { if (m.type() === "error") console.log("CONSOLE", m.text().slice(0, 300)); });
  await p.goto(`http://127.0.0.1:${srv.address().port}/index.html`);
  for (let i = 0; i < 600; i++) { if (await p.evaluate(() => window.ready === true)) break; await p.waitForTimeout(250); }
  await p.evaluate(() => document.fonts.ready);
  for (const t of times) { const t0 = Date.now(); await p.evaluate((t) => window.renderAt(t), t); await p.screenshot({ path: path.join(out, `t${t.toFixed(2)}.png`) }); console.log("shot", t, Date.now() - t0, "ms"); }
  await b.close(); srv.close();
});
