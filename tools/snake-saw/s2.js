
function fitFont(g, txt, size, family, maxW) { g.font = `${size}px "${family}"`; const w = g.measureText(txt).width; if (w > maxW) { size *= maxW / w; g.font = `${size}px "${family}"`; } return size; }
function words(g, parts, x, y, size, maxW, fam = 'Patrick Hand SC') { const full = parts.map(p => p[0]).join(''); fitFont(g, full, size, fam, maxW); let w = g.measureText(full).width, cx = x - w / 2;
  g.textAlign = 'left'; for (const [s, c] of parts) { g.fillStyle = c; g.fillText(s, cx, y); cx += g.measureText(s).width; } }
function heart(g, x, y, r, a, col = RED) { if (a <= 0) return; g.save(); g.globalAlpha = a; g.fillStyle = col; g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.moveTo(x, y + r); g.bezierCurveTo(x - r * 1.6, y - r * 0.2, x - r * 0.8, y - r * 1.4, x, y - r * 0.5); g.bezierCurveTo(x + r * 0.8, y - r * 1.4, x + r * 1.6, y - r * 0.2, x, y + r); g.fill(); g.stroke(); g.restore(); }

// ======================= timeline (vo/vo.json, atempo 1.08) =======================
const DUR = 57.27;
const K = {
  wipe1: 2.62, start: 2.75, cut: 3.63, sting: 4.78, decided: 5.54, attacking: 6.34, struck: 8.63, bit: 10.09, cutMouth: 10.83,
  furious: 11.88, wrapped: 12.4, crush: 13.8, tighter: 14.5, deeper: 15.52, teeth: 15.98, until: 16.87, gone: 17.35,
  wipe2: 18.05, sawOne: 18.39, his: 19.61, reaction: 19.82, rest: 20.5, name: 21.35, horseFx: 22.39, bat: 23.61, bites: 24.11, nothing: 25.21,
  but: 26.43, panics: 26.71, runs: 27.33, collapses: 28.55, wipe3: 30.32, small: 30.6, big: 31.46, hurts: 32.88, wipe4: 34.05, everyday: 34.27,
  rude: 36.56, fire: 37.74, replay: 38.36, argument: 39.96, turn: 41.16, war: 41.74, time: 42.37, sleep: 42.95, peace: 43.73, gone2: 44.59,
  something: 45.47, two: 46.62, wipe5: 47.55, next: 47.77, cuts: 48.47, remember: 49.01, letGo: 50.41, rule: 52.4, worth: 53.16, cta: 54.6,
};
const win = (t, a, b) => t >= a && t < b;

// ======================= the snake's story =======================
function storyCuts(t) {
  const c = [];
  if (t >= K.cut) c.push({ i: 4, k: ss(K.cut, K.cut + 0.12, t) });
  return c;
}
function coilCuts(P, n, t) { const c = []; if (!P.depth) return c; const n0 = P.nNeck; const front = [];
  for (let j = 0; j < P.depth.length; j++) if (P.depth[j] > 0.15) front.push(n0 + j);
  const order = front.map(i => [hash(i * 1.37), i]).sort((a, b) => a[0] - b[0]).map(x => x[1]);
  for (let k = 0; k < Math.min(n, order.length); k++) c.push({ i: order[k], k: 1, drip: ((t * 1.3 + hash(k)) % 1) });
  return c; }
function cutCount(t) { // the counter: CUTS
  if (t < K.wipe1) return Math.round(lerp(28, 41, ss(0, 2.4, t)));
  if (t < K.cut) return 0; if (t < K.bit) return 1; if (t < K.cutMouth) return 2; if (t < K.tighter) return 3 + Math.round(4 * ss(K.wrapped, K.tighter, t));
  return 7 + Math.round(34 * ss(K.tighter, K.until, t));
}
function coilState(t, R, shiver) { return coilSpine(t, R, { shiver, head: [252, 708] }); }
function storyState(t) { // {P, o, coil}
  const o = { mood: 'calm', mouth: 0, tongue: 0, cuts: [] };
  if (t < K.wipe1) { // hook: squeezing hard, near the end
    const P = coilState(t, 49 + 1.5 * Math.sin(t * 9), 1); o.mood = 'angry'; o.mouth = 0.55 + 0.35 * Math.abs(Math.sin(t * 5)); o.headA = 0.42 + 0.06 * Math.sin(t * 11); o.cuts = coilCuts(P, 20, t); return { P, o, coil: true };
  }
  if (t < K.wrapped) {
    let hx, lift = 22, rear = 0, ha = null;
    if (t < K.cut) { const k = (t - K.start) / (K.cut - K.start); hx = lerp(-90, 286, eout(clamp(k))); lift = lerp(22, 46, ss(0.6, 1, k)); o.tongue = (Math.sin(t * 7) > 0.3) ? 1 : 0; }
    else if (t < K.sting) { hx = lerp(286, 300, ss(K.cut, K.sting, t)); lift = 46 - 8 * ss(K.cut, K.cut + 0.3, t); o.mood = 'alert'; }
    else {
      // recoil + rear up facing the blade tip
      const r = ss(K.sting, K.sting + 0.35, t); hx = lerp(300, 205, eout(r)); rear = r; ha = -0.12; o.mood = t > K.decided ? 'angry' : 'alert';
      o.mouth = t > K.attacking ? 0.75 + 0.15 * Math.sin(t * 20) : t > K.sting && t < K.sting + 0.5 ? 0.6 : 0; o.tongue = t < K.attacking ? 1 : 0;
      // strike 1: lunge at the tip
      if (t >= K.struck - 0.1 && t < K.bit - 0.2) { const c = t - (K.struck - 0.1); const k = c < 0.22 ? eout(c / 0.22) : 1 - eio(clamp((c - 0.5) / 0.5)); hx = lerp(205, 262, k); rear = lerp(1, 0.55, k); o.mouth = lerp(1, 0.9, k); ha = lerp(-0.12, 0.35, k); }
      // bite: grabs the blade and holds
      if (t >= K.bit - 0.2 && t < K.furious) { const k = eout(ss(K.bit - 0.2, K.bit + 0.05, t)); hx = lerp(205, 262, k); rear = lerp(1, 0.55, k); ha = lerp(-0.12, 0.35, k) + 0.05 * Math.sin(t * 30) * (t > K.bit ? 1 : 0); o.mouth = t > K.bit ? 0.32 : 1; }
      if (t >= K.furious) { const k = ss(K.furious, K.furious + 0.3, t); hx = lerp(262, 215, k); rear = lerp(0.55, 1, k); ha = -0.12 + 0.12 * Math.sin(t * 26); o.mouth = 0.9; o.mood = 'angry'; }
    }
    const P = groundSpine(hx, t, { lift, rear, amp: 9 });
    if (ha != null) o.headA = ha;
    o.cuts = storyCuts(t);
    return { P, o, coil: false };
  }
  // wrap: morph the slither into the coil, then squeeze, then die
  const R = t < K.tighter ? 60 : lerp(60, 49, ss(K.tighter, K.until, t));
  const dead = ss(K.until, K.gone + 0.1, t);
  const C = coilSpine(t, lerp(R, 55, dead), { shiver: t > K.tighter && t < K.until ? 1 : 0, head: [lerp(252, 280, dead), lerp(708, 846, eio(dead))] });
  const G = groundSpine(215, t, { lift: 26, rear: 1, amp: 9 });
  const m = eio(ss(K.wrapped, K.wrapped + 1.4, t));
  const P = m < 1 ? lerpSpine(G, C, m) : C;
  o.mood = t > K.gone - 0.05 ? 'dead' : 'angry'; o.mouth = dead > 0.5 ? 0.25 : 0.55 + 0.35 * Math.abs(Math.sin(t * 6)); o.headA = lerp(lerp(-0.12, 0.42, m), 0.15, dead);
  const n = Math.round(lerp(3, 7, ss(K.wrapped + 0.6, K.tighter, t)) + 14 * ss(K.tighter, K.until, t));
  o.cuts = coilCuts(P, n, t); if (dead > 0.5) for (const c of o.cuts) c.drip = 0.4;
  if (dead > 0) o.fill = mixCol(SNAKE, '#d9d2bf', dead);
  return { P, o, coil: true };
}
function mixCol(a, b, k) { const pa = a.match(/\w\w/g).map(h => parseInt(h, 16)), pb = b.match(/\w\w/g).map(h => parseInt(h, 16)); return `rgb(${pa.map((v, i) => Math.round(lerp(v, pb[i], k))).join(',')})`; }
function bloodPool(g, k, x = 410) { if (k <= 0) return; g.save(); g.fillStyle = RED; g.globalAlpha = 0.9; g.beginPath(); g.ellipse(x, FLOOR + 4, 20 + 90 * k, 5 + 9 * k, 0, 0, 7); g.fill(); g.restore(); }
function drips(g, t, k) { if (k <= 0) return; g.save(); g.fillStyle = RED; for (let i = 0; i < 6; i++) { const x = 330 + hash(i * 4.1) * 170, ph = (t * 1.1 + hash(i * 2.3)) % 1, y0 = sawBot(x) + 30; const y = lerp(y0, FLOOR, ph * ph); if (hash(i * 7) > k) continue; g.beginPath(); g.ellipse(x, y, 3.4, 5.5, 0, 0, 7); g.fill(); } g.restore(); }
function mouthBlood(g, t, k) { if (k <= 0) return; g.save(); g.fillStyle = RED; for (let i = 0; i < 3; i++) { const ph = (t * 1.4 + i / 3) % 1; g.beginPath(); g.ellipse(292 + i * 7, lerp(806, FLOOR, ph * ph), 3.2, 5, 0, 0, 7); g.fill(); } g.restore(); bloodPool(g, 0.25 * k, 300); }
function anger(g, x, y, k, s = 1) { if (k <= 0) return; g.save(); g.globalAlpha = k; g.strokeStyle = RED; g.lineWidth = 4 * s; g.lineCap = 'round'; for (let i = 0; i < 4; i++) { const a = i * Math.PI / 2 + 0.6; g.beginPath(); g.moveTo(x + Math.cos(a) * 5 * s, y + Math.sin(a) * 5 * s); g.quadraticCurveTo(x + Math.cos(a + 0.5) * 12 * s, y + Math.sin(a + 0.5) * 12 * s, x + Math.cos(a) * 16 * s, y + Math.sin(a) * 16 * s); g.stroke(); } g.restore(); }
function spark(g, x, y, k, r = 34) { if (k <= 0 || k >= 1) return; g.save(); g.globalAlpha = 1 - k; g.strokeStyle = RED; g.lineWidth = 4; g.lineCap = 'round'; for (let i = 0; i < 8; i++) { const a = i / 8 * Math.PI * 2 + 0.3, r0 = 8 + r * k, r1 = r0 + 16; g.beginPath(); g.moveTo(x + Math.cos(a) * r0, y + Math.sin(a) * r0); g.lineTo(x + Math.cos(a) * r1, y + Math.sin(a) * r1); g.stroke(); } g.restore(); }
function thought(g, x, y, w, h, k, tailTo) { if (k <= 0) return; g.save(); g.globalAlpha = Math.min(1, k * 1.4); const sc = 0.7 + 0.3 * eout(clamp(k));
  if (tailTo) for (const [f, r] of [[0.25, 7], [0.5, 11]]) blob(g, lerp(tailTo[0], x, f), lerp(tailTo[1], y + h * 0.45, f), r, r, FILL, 3);
  g.translate(x, y); g.scale(sc, sc); g.fillStyle = FILL; g.beginPath(); g.ellipse(0, 0, w / 2, h / 2, 0, 0, 7); g.fill();
  inkLine(g, Array.from({ length: 49 }, (_, i) => { const a = i / 48 * Math.PI * 2; return [Math.cos(a) * (w / 2 + 5 * Math.sin(a * 11)), Math.sin(a) * (h / 2 + 5 * Math.sin(a * 11))]; }), 3); g.restore(); }
// the saw as the snake imagines it: eyes + a toothy grin
function evilSaw(g, x, y, s, k, red) { g.save(); g.translate(x, y); g.scale(s, s); g.translate(-450, -770); drawSaw(g);
  g.fillStyle = '#fff'; g.strokeStyle = INK; g.lineWidth = 3; for (const ex of [330, 390]) { g.beginPath(); g.arc(ex, 768, 13, 0, 7); g.fill(); g.stroke(); g.fillStyle = red ? RED : INK; g.beginPath(); g.arc(ex + 3, 770, 5, 0, 7); g.fill(); g.fillStyle = '#fff'; }
  g.lineWidth = 5; g.lineCap = 'round'; g.beginPath(); g.moveTo(312, 745 - 4 * k); g.lineTo(346, 756); g.moveTo(406, 745 - 4 * k); g.lineTo(374, 756); g.stroke();
  if (red) { g.globalAlpha = 0.25; g.fillStyle = RED; g.fillRect(240, 700, 480, 140); } g.restore(); }

function workshopScene(g, t) {
  workshop(g); stump(g);
  const st = storyState(t);
  const sawShake = 0; // the saw never moves
  // blood on the floor
  if (st.coil) { const k = t < K.wipe1 ? 0.85 : ss(K.tighter, K.gone + 0.6, t); bloodPool(g, k); }
  if (t >= K.cutMouth && t < K.wrapped + 0.6) mouthBlood(g, t, ss(K.cutMouth, K.cutMouth + 0.3, t));
  // shadow
  g.save(); g.fillStyle = 'rgba(30,25,22,0.16)'; g.beginPath(); g.ellipse(st.coil ? 410 : st.P[20][0], FLOOR + 3, 200, 9, 0, 0, 7); g.fill(); g.restore();
  if (st.coil) { coilDraw(g, st.P, st.o, () => { drawSaw(g); sawBlood(g, t < K.wipe1 ? 1 : ss(K.wrapped, K.until, t)); }); drips(g, t, t < K.wipe1 ? 1 : ss(K.tighter, K.until, t) * (1 - ss(K.gone, K.gone + 1.2, t))); }
  else {
    drawSaw(g); if (t >= K.bit) sawBlood(g, 0.25);
    // body passes in front of the blade
    snakeChunk(g, st.P, 0, SN - 1, st.o); snakeHead(g, st.P, st.o);
  }
  // sting spark at the nick + the "!"
  if (t >= K.cut && t < K.cut + 0.5) spark(g, 290, 806, (t - K.cut) / 0.5, 26);
  if (win(t, K.sting, K.sting + 0.8)) { const k = ss(K.sting, K.sting + 0.12, t) * (1 - ss(K.sting + 0.6, K.sting + 0.8, t)); g.save(); g.globalAlpha = k; g.font = '80px "Permanent Marker"'; g.fillStyle = RED; g.textAlign = 'center'; g.fillText('!', 180, 690); g.restore(); }
  if (t >= K.struck && t < K.struck + 0.6) spark(g, 300, 784, (t - K.struck - 0.12) / 0.45, 40);
  if (t >= K.bit && t < K.bit + 0.5) spark(g, 300, 790, (t - K.bit) / 0.5, 40);
  // anger marks
  if (!st.coil && t > K.decided) anger(g, st.P[0][0] - 20, st.P[0][1] - 56, 1, 1.4);
  if (st.coil && st.o.mood === 'angry') anger(g, st.P[0][0] - 30, st.P[0][1] - 52, 1, 1.4);
  // what he thinks: the saw is attacking him
  if (t >= K.decided - 0.1 && t < K.struck) { const k = ss(K.decided - 0.1, K.decided + 0.25, t) * (1 - ss(K.struck - 0.25, K.struck, t));
    thought(g, 300, 520, 340, 210, k, [215, 720]); if (k > 0.3) { g.save(); g.globalAlpha = clamp(k * 1.5 - 0.4); const red = t > K.attacking; const lun = red ? Math.sin(t * 16) * 6 : 0; evilSaw(g, 300 + lun, 528, 0.62, red ? 1 : 0, red); g.restore(); } }
}

// ======================= scoreboard: one cut vs the rest =======================
function scoreScene(g, t) {
  paper(g);
  const pts = []; for (let y = -40; y <= DH + 40; y += 26) pts.push([360 + (hash(y) - 0.5) * 10, y]);
  // left: the saw alone
  g.save(); g.translate(180, 760); g.scale(0.62, 0.62); g.translate(-470, -790); drawSaw(g); sawBlood(g, 0.3); g.restore();
  // right: the saw with the snake (dead)
  g.save(); g.translate(540, 760); g.scale(0.62, 0.62); g.translate(-470, -800); const P = coilSpine(17.5, 55, { head: [280, 846] }); const cut = coilCuts(P, 18, 17.5); for (const c of cut) c.drip = 0.4; bloodPool(g, 1);
  coilDraw(g, P, { mood: 'dead', mouth: 0.25, headA: 0.15, cuts: cut, fill: '#d9d2bf' }, () => { drawSaw(g); sawBlood(g, 1); }); g.restore();
  inkLine(g, pts, 5);
  g.textAlign = 'center';
  const k1 = ss(K.sawOne, K.sawOne + 0.2, t), k2 = ss(K.his, K.his + 0.2, t);
  g.save(); g.globalAlpha = k1; g.font = '40px "Patrick Hand SC"'; g.fillStyle = INK; g.fillText('THE SAW', 180, 420); g.font = '150px "Permanent Marker"'; const p1 = 1 + 0.25 * Math.exp(-(t - K.sawOne - 0.43) * 9) * (t > K.sawOne + 0.43 ? 1 : 0); g.translate(180, 560); g.scale(p1, p1); g.fillText('1', 0, 0); g.restore();
  g.save(); g.globalAlpha = k1; g.font = '30px "Patrick Hand SC"'; g.fillStyle = INK; g.fillText('CUT', 180, 610); g.restore();
  const n = Math.round(lerp(1, 40, eout(ss(K.reaction, K.rest + 0.2, t))));
  g.save(); g.globalAlpha = k2; g.font = '40px "Patrick Hand SC"'; g.fillStyle = INK; g.fillText('HIS REACTION', 540, 420); g.font = '150px "Permanent Marker"'; g.fillStyle = RED; const p2 = 1 + 0.12 * Math.abs(Math.sin(t * 14)) * (t < K.rest + 0.2 ? 1 : 0); g.translate(540, 560); g.scale(p2, p2); g.fillText(String(n), 0, 0); g.restore();
  g.save(); g.globalAlpha = k2; g.font = '30px "Patrick Hand SC"'; g.fillStyle = INK; g.fillText('CUTS', 540, 610); g.restore();
}

// ======================= the wild horse effect =======================
function plain(g, scroll) {
  paper(g); const GY = 900;
  // far hills (slow), near grass (fast)
  const h = []; for (let x = -60; x <= 780; x += 30) { const u = x + scroll * 0.15; h.push([x, 640 - 40 * Math.sin(u * 0.008) - 20 * Math.sin(u * 0.021 + 1)]); } inkLine(g, h, 2.2, 'rgba(30,25,22,0.45)');
  const h2 = []; for (let x = -60; x <= 780; x += 30) { const u = x + scroll * 0.4; h2.push([x, 760 - 26 * Math.sin(u * 0.012 + 2) - 12 * Math.sin(u * 0.03)]); } inkLine(g, h2, 2.4, 'rgba(30,25,22,0.6)');
  inkLine(g, [[-60, GY + 1], [780, GY - 1]], 3.5);
  for (let i = 0; i < 22; i++) { const x = ((i * 67 - scroll) % 840 + 840) % 840 - 60, y = GY + 20 + hash(i) * 180; inkLine(g, [[x - 8, y], [x - 4, y - 14]], 2, 'rgba(30,25,22,0.5)'); inkLine(g, [[x, y], [x + 2, y - 18]], 2, 'rgba(30,25,22,0.5)'); inkLine(g, [[x + 8, y], [x + 6, y - 13]], 2, 'rgba(30,25,22,0.5)'); }
  for (let i = 0; i < 6; i++) { const x = ((i * 151 - scroll) % 840 + 840) % 840 - 60; inkLine(g, [[x - 6, GY], [x - 3, GY - 12]], 2); inkLine(g, [[x + 2, GY], [x + 4, GY - 15]], 2); }
}
function horseX(t) { return 380; }
function horseScroll(t) { // distance travelled (px) - accelerates on "runs", stops on collapse
  if (t < K.runs - 0.2) return 0; const a = t - (K.runs - 0.2), stop = K.collapses + 0.5; const v = 1400;
  if (t < stop) return v * a * a / (a + 0.4); const a2 = stop - (K.runs - 0.2); const d0 = v * a2 * a2 / (a2 + 0.4); const dt = t - stop; return d0 + v * 0.35 * (1 - Math.exp(-dt * 3)); }
function horseScene(g, t) {
  const sc = horseScroll(t); plain(g, sc);
  const GY = 900; const run = ss(K.runs - 0.3, K.runs + 0.1, t) * (1 - ss(K.collapses, K.collapses + 0.3, t));
  let mode = 'stand', rear = 0, down = 0; if (t >= K.panics - 0.1 && t < K.runs - 0.2) { mode = 'rear'; rear = Math.sin(clamp((t - K.panics + 0.1) / (K.runs - K.panics)) * Math.PI); }
  if (run > 0) mode = 'run'; if (t >= K.collapses) { mode = 'down'; down = eout(ss(K.collapses, K.collapses + 0.5, t)); }
  const panic = ss(K.panics - 0.1, K.panics + 0.1, t);
  const hx = horseX(t);
  g.save(); g.fillStyle = 'rgba(30,25,22,0.16)'; g.beginPath(); g.ellipse(hx, GY + 3, 170, 9, 0, 0, 7); g.fill(); g.restore();
  // speed lines + dust while running
  if (run > 0.2) { g.save(); g.globalAlpha = run; for (let i = 0; i < 8; i++) { const y = 560 + hash(i) * 330, x = ((hash(i * 3) * 900 - t * 2600) % 900 + 900) % 900 - 90; inkLine(g, [[x, y], [x + 90 + 60 * hash(i * 5), y]], 2.2, 'rgba(30,25,22,0.5)'); } g.restore(); }
  for (let i = 0; i < 5; i++) { const ph = ((t * 2.2) + i / 5) % 1; if (run < 0.2 && !(t >= K.collapses && t < K.collapses + 1.2)) break; const big = t >= K.collapses ? 1.8 : 1; blob(g, hx - 150 - ph * 160, GY - 14 - ph * 24, (10 + 20 * ph) * big, (8 + 14 * ph) * big, `rgba(237,230,214,${1 - ph})`, 2 * (1 - ph)); }
  drawHorse(g, { x: hx, y: GY, s: 1.45, ph: t * 2.6, run, mode, rear, down, panic });
  // the bite dot on the near front leg
  const legP = [hx + (72 + 20) * 1.45 - 60 * 1.45 * 0, GY - 58];
  if (t >= K.bites && t < K.collapses) { g.save(); g.fillStyle = RED; g.beginPath(); g.arc(hx + 92, GY - 64 + (mode === 'run' ? -20 * Math.abs(Math.sin(t * 2.6 * Math.PI * 2)) : 0), 3.4, 0, 7); g.fill(); g.restore(); }
  // bat: flies in, bites, flies off
  if (t >= K.bat - 0.1 && t < K.but) { let bx, by; const a = clamp((t - K.bat + 0.1) / 0.6), b = clamp((t - K.bites - 0.3) / 0.9);
    bx = lerp(780, hx + 108, eout(a)); by = lerp(420, GY - 80, eout(a)); if (b > 0) { bx = lerp(hx + 108, 820, eio(b)); by = lerp(GY - 80, 300, eio(b)); }
    drawBat(g, bx, by, 1.3, t * 7); }
  if (t >= K.bites && t < K.bites + 0.5) spark(g, hx + 92, GY - 64, (t - K.bites) / 0.5, 18);
  // "the bite is nothing": a tiny label
  if (win(t, K.nothing - 0.2, K.but)) { const k = ss(K.nothing - 0.2, K.nothing, t); g.save(); g.globalAlpha = k; inkLine(g, [[hx + 50, GY - 170], [hx + 84, GY - 74]], 3, RED); inkLine(g, [[hx + 72, GY - 90], [hx + 84, GY - 74], [hx + 90, GY - 94]], 3, RED); g.font = '34px "Patrick Hand SC"'; g.fillStyle = RED; g.textAlign = 'center'; g.fillText('TINY BITE', hx + 40, GY - 180); g.restore(); }
  if (t >= K.panics - 0.05 && t < K.runs) { const k = ss(K.panics - 0.05, K.panics + 0.1, t); g.save(); g.globalAlpha = k; g.font = '80px "Permanent Marker"'; g.fillStyle = RED; g.textAlign = 'center'; g.fillText('!!', hx + 150, 540); g.restore(); }
  // title
  const tk = ss(K.horseFx - 0.1, K.horseFx + 0.2, t) * (1 - ss(K.bat + 0.2, K.bat + 0.5, t));
  if (tk > 0) { g.save(); g.globalAlpha = tk; const p = 1 + 0.15 * Math.exp(-(t - K.horseFx) * 8); g.translate(360, 380); g.scale(p, p); g.translate(-360, -380); g.textAlign = 'center';
    fitFont(g, 'THE WILD HORSE', 76, 'Permanent Marker', 600); g.fillStyle = INK; g.fillText('THE WILD HORSE', 360, 360); g.font = '76px "Permanent Marker"'; g.fillStyle = RED; g.fillText('EFFECT', 360, 446);
    const ul = ss(K.horseFx + 0.2, K.horseFx + 0.7, t); inkLine(g, [[200, 470], [lerp(200, 520, ul), 466]], 6, RED); g.restore(); }
}

// ======================= small wound + big reaction = real damage =======================
function bandage(g, x, y, s) { g.save(); g.translate(x, y); g.rotate(-0.4); g.scale(s, s); inkShape(g, [[-44, -14], [44, -14], [44, 14], [-44, 14]], '#f0d6b4', 3); inkShape(g, [[-14, -14], [14, -14], [14, 14], [-14, 14]], '#e7c49c', 2); g.strokeStyle = RED; g.lineWidth = 3; g.beginPath(); g.moveTo(-6, 0); g.lineTo(6, 0); g.stroke(); g.restore(); }
function burst(g, x, y, r, spin = 0, label = null) { g.save(); g.fillStyle = RED; g.strokeStyle = INK; g.lineWidth = 3.5; g.beginPath();
  for (let i = 0; i <= 24; i++) { const a = i / 24 * Math.PI * 2 + spin, rr = r * (i % 2 ? 0.55 : 1) * (0.9 + 0.2 * hash(i + Math.floor(T * 8))); g.lineTo(x + Math.cos(a) * rr, y + Math.sin(a) * rr); } g.closePath(); g.fill(); g.stroke();
  if (label) { g.fillStyle = FILL; g.textAlign = 'center'; g.font = `${r * 0.42}px "Permanent Marker"`; g.fillText(label, x, y + r * 0.15); } g.restore(); }
function brokenHeart(g, x, y, r, k) { heart(g, x - 6 * k, y, r, 1); g.save(); g.strokeStyle = PAPER; g.lineWidth = 8; g.beginPath(); g.moveTo(x - 2, y - r * 0.5); g.lineTo(x + 8, y - r * 0.1); g.lineTo(x - 6, y + r * 0.25); g.lineTo(x + 4, y + r * 0.7); g.stroke(); g.strokeStyle = INK; g.lineWidth = 3; g.stroke(); g.restore(); }
function equationScene(g, t) {
  paper(g);
  const rows = [[K.small, 360], [K.big, 600], [K.hurts, 840]];
  const k1 = ss(K.small, K.small + 0.2, t), k2 = ss(K.big, K.big + 0.2, t), k3 = ss(K.hurts, K.hurts + 0.2, t);
  g.textAlign = 'left';
  // row 1
  if (k1 > 0) { g.save(); g.globalAlpha = k1; bandage(g, 150, 330, 0.8 + 0.2 * eout(k1)); g.font = '58px "Permanent Marker"'; g.fillStyle = INK; g.fillText('SMALL WOUND', 250, 352); g.restore(); }
  if (k2 > 0) { g.save(); g.globalAlpha = k2; g.font = '70px "Permanent Marker"'; g.fillStyle = INK; g.textAlign = 'center'; g.fillText('+', 360, 470); const r = 66 * (0.6 + 0.4 * eout(k2)) * (1 + 0.06 * Math.sin(t * 22)); burst(g, 150, 580, r, t * 0.5); g.textAlign = 'left'; g.font = '58px "Permanent Marker"'; g.fillStyle = RED; g.fillText('BIG REACTION', 250, 602); g.restore(); }
  if (k3 > 0) { g.save(); g.globalAlpha = k3; g.font = '70px "Permanent Marker"'; g.fillStyle = INK; g.textAlign = 'center'; g.fillText('=', 360, 718); brokenHeart(g, 150, 818, 44 * (0.7 + 0.3 * eout(k3)), ss(K.hurts + 0.2, K.hurts + 0.5, t)); g.textAlign = 'left'; g.font = '58px "Permanent Marker"'; g.fillStyle = INK; g.fillText('REAL DAMAGE', 250, 842); inkLine(g, [[250, 862], [lerp(250, 640, ss(K.hurts + 0.2, K.hurts + 0.7, t)), 858]], 6, RED); g.restore(); }
}

// ======================= people (ink, round heads) =======================
function prim(g, q, o, w, col) {
  const s = o.s, d = o.dir, X = p => o.x + p[0] * d * s, Y = p => o.y + p[1] * s;
  g.strokeStyle = col; g.fillStyle = col; g.lineCap = 'round'; g.lineJoin = 'round';
  if (q.t === 'l') { g.lineWidth = (q.w + w) * s; g.beginPath(); const p0 = jit(X(q.p[0]), Y(q.p[0]), 0.6); g.moveTo(p0[0], p0[1]); for (let i = 1; i < q.p.length; i++) { const p = jit(X(q.p[i]), Y(q.p[i]), 0.6); g.lineTo(p[0], p[1]); } g.stroke(); }
  else if (q.t === 'e') { const c = jit(X(q.c), Y(q.c), 0.5); g.beginPath(); g.ellipse(c[0], c[1], (q.rx + w / 2) * s, (q.ry + w / 2) * s, 0, 0, 7); g.fill(); }
}
function person(g, o) {
  const s = o.s, d = o.dir; const X = v => o.x + v * d * s, Y = v => o.y + v * s; const ph = o.walk || 0, wa = o.walk != null ? 1 : 0;
  const head = [0, -200];
  const legs = [[[-8, -80], [-8 + 14 * Math.sin(ph) * wa, -40], [-10 + 22 * Math.sin(ph) * wa, 0]], [[8, -80], [8 - 14 * Math.sin(ph) * wa, -40], [10 - 22 * Math.sin(ph) * wa, 0]]];
  let arms;
  if (o.arms === 'phone') arms = [[[-14, -150], [-22, -110], [14, -112]], [[14, -150], [26, -112], [20, -112]]];
  else if (o.arms === 'type') { const a = Math.sin(T * 40) * 4; arms = [[[-14, -150], [-22, -110], [10, -116 + a]], [[14, -150], [26, -112], [22, -114 - a]]]; }
  else if (o.arms === 'fists') arms = [[[-14, -150], [-4, -122], [26, -136]], [[14, -150], [34, -126], [46, -146]]];
  else if (o.arms === 'point') arms = [[[-14, -150], [-22, -112], [-20, -76]], [[14, -150], [50, -150], [80, -160]]];
  else arms = [[[-14, -150], [-22 - 6 * Math.sin(ph) * wa, -112], [-20 - 14 * Math.sin(ph) * wa, -76]], [[14, -150], [22 + 6 * Math.sin(ph) * wa, -112], [20 + 14 * Math.sin(ph) * wa, -76]]];
  const L = (pts, w) => ({ t: 'l', p: pts, w });
  const body = [L(legs[0], 15), L(legs[1], 15), L([[0, -150], [0, -90]], 50), L(arms[0], 13), L(arms[1], 13), { t: 'e', c: head, rx: 36, ry: 36 }];
  const oo = { x: o.x, y: o.y, s, dir: d };
  g.save(); g.globalAlpha = o.alpha ?? 1;
  for (const q of body) prim(g, q, oo, 6.5, INK); for (const q of body) prim(g, q, oo, 0, o.fill || FILL);
  for (const a of arms) { const h = a[2]; g.fillStyle = FILL; g.strokeStyle = INK; g.lineWidth = 3 * s; g.beginPath(); g.arc(X(h[0]), Y(h[1]), (o.arms === 'fists' ? 10 : 8) * s, 0, 7); g.fill(); g.stroke(); }
  if (o.arms === 'phone' || o.arms === 'type') { g.save(); g.translate(X(16), Y(-128)); g.rotate(-0.15 * d); g.fillStyle = INK; g.beginPath(); g.roundRect(-11 * s, -20 * s, 22 * s, 36 * s, 4 * s); g.fill(); g.fillStyle = o.screen || '#cfe0e6'; g.fillRect(-8 * s, -16 * s, 16 * s, 26 * s); g.restore(); }
  const hx = X(head[0]) + 6 * d * s, hy = Y(head[1]); g.strokeStyle = INK; g.fillStyle = INK; g.lineCap = 'round'; g.lineWidth = 3.2 * s; const f = o.face || 'calm';
  for (const e of [-12, 12]) { const x = hx + e * s, y = hy - 4 * s;
    if (f === 'smile') { g.beginPath(); g.arc(x, y + 2 * s, 5 * s, Math.PI * 1.1, Math.PI * 1.9); g.stroke(); }
    else if (f === 'wide') { g.fillStyle = '#fff'; g.beginPath(); g.arc(x, y, 7 * s, 0, 7); g.fill(); g.stroke(); g.fillStyle = INK; g.beginPath(); g.arc(x, y, 2.6 * s, 0, 7); g.fill(); }
    else { g.beginPath(); g.arc(x, y, 3.4 * s, 0, 7); g.fill(); }
    if (f === 'angry' || f === 'shout' || f === 'frown') { const tilt = f === 'frown' ? 0.4 : 1; g.beginPath(); g.moveTo(x - 7 * s * Math.sign(e), y - 16 * s * tilt); g.lineTo(x + 7 * s * Math.sign(e), y - 9 * s + 3 * s * tilt); g.stroke(); } }
  g.beginPath();
  if (f === 'smile') { g.arc(hx, hy + 8 * s, 10 * s, 0.15 * Math.PI, 0.85 * Math.PI); g.stroke(); }
  else if (f === 'frown' || f === 'angry') { g.arc(hx, hy + 22 * s, 9 * s, 1.2 * Math.PI, 1.8 * Math.PI); g.stroke(); }
  else if (f === 'shout') { g.fillStyle = RED; g.ellipse(hx, hy + 14 * s, 9 * s, 7 * s, 0, 0, 7); g.fill(); g.stroke(); }
  else if (f === 'wide') { g.moveTo(hx - 5 * s, hy + 15 * s); g.lineTo(hx + 5 * s, hy + 15 * s); g.stroke(); }
  else { g.moveTo(hx - 7 * s, hy + 13 * s); g.lineTo(hx + 7 * s, hy + 13 * s); g.stroke(); }
  if (o.mad) anger(g, X(head[0]) - 26 * d * s, Y(head[1]) - 40 * s, 1, s);
  g.restore();
}
function bubble(g, x, y, w, h, txt, k, tailDir = -1, col = FILL, txtCol = INK, size = 28) {
  if (k <= 0) return; g.save(); g.globalAlpha = Math.min(1, k * 1.5); g.translate(x, y); const sc = 0.7 + 0.3 * eout(clamp(k)); g.scale(sc, sc);
  g.fillStyle = col; g.strokeStyle = INK; g.lineWidth = 3; g.beginPath(); g.roundRect(-w / 2, -h / 2, w, h, 16); g.fill(); g.stroke();
  g.beginPath(); g.moveTo(tailDir * w * 0.25 - 10, h / 2 - 1.5); g.lineTo(tailDir * w * 0.25 + tailDir * 6, h / 2 + 18); g.lineTo(tailDir * w * 0.25 + 12, h / 2 - 1.5); g.fill(); g.stroke();
  g.fillStyle = col; g.fillRect(tailDir * w * 0.25 - 9, h / 2 - 5, 20, 6);
  g.fillStyle = txtCol; g.textAlign = 'center'; g.textBaseline = 'middle'; fitFont(g, txt, size + 6, 'Patrick Hand SC', w - 26); g.fillText(txt, 0, 2); g.textBaseline = 'alphabetic'; g.restore();
}
function impactBig(g, x, y, k, label) { g.save(); g.globalAlpha = 1 - k * 0.4; const r = 50 + 80 * eout(k); burst(g, x, y, r, 0, label); g.restore(); }
function room(g, night) {
  paper(g); for (let i = 0; i < 12; i++) { const x = -40 + i * 74; inkLine(g, [[x, -60], [x + 2, FLOOR - 4]], 1, 'rgba(30,25,22,0.12)'); }
  inkLine(g, [[-60, FLOOR + 1], [780, FLOOR - 1]], 3.5); for (let i = 1, d = 30; i < 7; i++, d *= 1.45) inkLine(g, [[-60, FLOOR + d], [780, FLOOR + d]], 1.1, 'rgba(30,25,22,0.16)');
}
function phoneBig(g, x, y, s, k, lines) { if (k <= 0) return; g.save(); g.globalAlpha = Math.min(1, k * 1.5); g.translate(x, y); g.scale(s * (0.85 + 0.15 * eout(k)), s * (0.85 + 0.15 * eout(k)));
  g.fillStyle = INK; g.beginPath(); g.roundRect(-150, -250, 300, 500, 36); g.fill(); g.fillStyle = FILL; g.beginPath(); g.roundRect(-136, -224, 272, 450, 22); g.fill();
  g.fillStyle = INK; g.beginPath(); g.roundRect(-30, -240, 60, 10, 5); g.fill();
  for (const ln of lines) ln(g); g.restore(); }
function comment(g, y, name, txt, col, a = 1) { g.save(); g.globalAlpha *= a; blob(g, -100, y, 20, 20, '#d8cbb5', 2.5); g.textAlign = 'left'; g.font = '22px "Patrick Hand SC"'; g.fillStyle = 'rgba(30,25,22,0.6)'; g.fillText(name, -70, y - 6); g.font = '30px "Patrick Hand SC"'; g.fillStyle = col; fitFont(g, txt, 30, 'Patrick Hand SC', 190); g.fillText(txt, -70, y + 22); g.restore(); }
function battery(g, x, y, w, h, lvl, label, k) { g.save(); g.globalAlpha = k;
  inkShape(g, [[x, y], [x + w, y], [x + w, y + h], [x, y + h]], FILL, 4); inkShape(g, [[x + w, y + h * 0.3], [x + w + 14, y + h * 0.3], [x + w + 14, y + h * 0.7], [x + w, y + h * 0.7]], INK, 3);
  const col = lvl > 0.35 ? '#8fae6e' : RED; const segs = 5; for (let i = 0; i < segs; i++) { const on = lvl * segs > i + 0.05; if (!on) continue; g.fillStyle = col; g.fillRect(x + 8 + i * (w - 16) / segs + 2, y + 8, (w - 16) / segs - 6, h - 16); }
  g.font = '40px "Permanent Marker"'; g.textAlign = 'right'; g.fillStyle = INK; g.fillText(label, x - 18, y + h * 0.68);
  g.font = '30px "Patrick Hand SC"'; g.textAlign = 'center'; g.fillStyle = lvl < 0.05 ? RED : INK; g.fillText(Math.round(lvl * 100) + '%', x + w / 2, y + h + 34); g.restore(); }
function stopwatch(g, x, y, r, sec, k) { if (k <= 0) return; g.save(); g.globalAlpha = k; g.translate(x, y); const sc = 0.8 + 0.2 * eout(k); g.scale(sc, sc);
  inkShape(g, [[-14, -r - 26], [14, -r - 26], [14, -r - 4], [-14, -r - 4]], WOOD, 3); blob(g, 0, 0, r, r, FILL, 5);
  for (let i = 0; i < 12; i++) { const a = i / 12 * Math.PI * 2; inkLine(g, [[Math.sin(a) * r * 0.82, -Math.cos(a) * r * 0.82], [Math.sin(a) * r * 0.92, -Math.cos(a) * r * 0.92]], 3); }
  const a = sec / 60 * Math.PI * 2 * 5; g.fillStyle = 'rgba(200,40,42,0.25)'; g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, r * 0.78, -Math.PI / 2, -Math.PI / 2 + a); g.closePath(); g.fill();
  inkLine(g, [[0, 0], [Math.sin(a) * r * 0.75, -Math.cos(a) * r * 0.75]], 6, RED); blob(g, 0, 0, 8, 8, INK, 0);
  g.font = '64px "Permanent Marker"'; g.textAlign = 'center'; g.fillStyle = INK; g.fillText('0:0' + Math.min(2, Math.floor(sec)), 0, r * 0.55); g.restore(); }
function nightWash(g, k) { if (k <= 0) return; g.save(); g.globalCompositeOperation = 'multiply'; g.fillStyle = `rgba(200,210,230,${0.45 * k})`; g.fillRect(-400, -400, DW + 800, DH + 800); g.restore(); }
function lifeScene(g, t) {
  const Y0 = FLOOR + 60;
  if (t < K.rude) { // we do it every day: walking, calendar flipping
    room(g); const day = Math.floor(clamp((t - K.everyday) / 0.45, 0, 6)); const days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
    g.save(); g.translate(360, 360); inkShape(g, [[-90, -70], [90, -70], [90, 90], [-90, 90]], FILL, 4); g.fillStyle = RED; g.fillRect(-88, -68, 176, 44); g.font = '30px "Permanent Marker"'; g.textAlign = 'center'; g.fillStyle = FILL; g.fillText('EVERY DAY', 0, -36); g.fillStyle = INK; g.font = '76px "Permanent Marker"'; g.fillText(days[day], 0, 60); g.restore();
    person(g, { x: 360, y: Y0, s: 1.7, dir: 1, face: 'frown', arms: 'phone', walk: t * 9 });
    return;
  }
  if (t < K.fire) { // one rude comment
    room(g); const k = ss(K.rude, K.rude + 0.2, t);
    phoneBig(g, 360, 600, 1.1, 1, [g2 => { comment(g2, -150, '@you', 'new post!', INK); g2.save(); const kk = ss(K.rude + 0.15, K.rude + 0.35, t); g2.globalAlpha = kk; g2.fillStyle = 'rgba(200,40,42,0.12)'; g2.fillRect(-132, -40, 264, 90); comment(g2, 0, '@someone', 'nobody asked.', RED); g2.restore(); }]);
    return;
  }
  if (t < K.replay) { // you fire back
    room(g); person(g, { x: 230, y: Y0, s: 1.8, dir: 1, face: 'angry', arms: 'type', mad: true });
    const msgs = ['EXCUSE ME??', 'WHO ASKED YOU?', 'SAY THAT AGAIN', '!!!']; for (let i = 0; i < 4; i++) { const t0 = K.fire + i * 0.13; const k = ss(t0, t0 + 0.12, t); bubble(g, 470 + (i % 2) * 40, 680 - i * 110, 250, 64, msgs[i], k, -1, FILL, RED, 30); }
    return;
  }
  if (t < K.argument) { // replay it all night
    room(g); nightWash(g, 1);
    g.save(); g.translate(560, 300); blob(g, 0, 0, 44, 44, '#f7f1e2', 3); g.restore();
    g.save(); g.font = '46px "Permanent Marker"'; g.textAlign = 'center'; g.fillStyle = INK; const mins = 2 * 60 + 12 + Math.floor((t - K.replay) * 40); g.fillText(`${Math.floor(mins / 60) + 1}:${String(mins % 60).padStart(2, '0')} AM`, 200, 310); g.restore();
    person(g, { x: 360, y: Y0, s: 2.1, dir: 1, face: 'wide', arms: 'phone' });
    const loop = ((t - K.replay) * 2.2) % 1; bubble(g, 360, 600, 300, 76, '"nobody asked."', 0.4 + 0.6 * eout(loop), -1, FILL, RED, 36);
    g.save(); g.translate(560, 600); g.rotate(-t * 8); g.strokeStyle = RED; g.lineWidth = 5; g.beginPath(); g.arc(0, 0, 26, 0.3, 5.6); g.stroke(); g.fillStyle = RED; g.beginPath(); g.moveTo(26 * Math.cos(0.3) - 9, 26 * Math.sin(0.3) - 2); g.lineTo(26 * Math.cos(0.3) + 9, 26 * Math.sin(0.3) - 2); g.lineTo(26 * Math.cos(0.3), 26 * Math.sin(0.3) + 12); g.fill(); g.restore();
    return;
  }
  if (t < K.time) { // a small argument becomes a war
    room(g); const warK = ss(K.turn, K.war, t);
    person(g, { x: 190, y: Y0, s: 1.6, dir: 1, face: warK > 0.3 ? 'shout' : 'frown', arms: warK > 0.3 ? 'fists' : 'down', mad: warK > 0.3 });
    person(g, { x: 530, y: Y0, s: 1.6, dir: -1, face: warK > 0.5 ? 'shout' : 'calm', arms: warK > 0.5 ? 'fists' : 'down', fill: '#f4eadb', mad: warK > 0.5 });
    bubble(g, 230, 520, 250, 62, 'you forgot. again.', ss(K.argument + 0.1, K.argument + 0.3, t), -1);
    if (t > K.turn) { const n = Math.floor((t - K.turn) / 0.09); const ws = ['ALWAYS!', 'NEVER!', 'YOU!', 'ME?!', 'WHY?!', 'ENOUGH!']; for (let i = 0; i < Math.min(n, 6); i++) bubble(g, 120 + hash(i * 3) * 480, 380 + hash(i * 7) * 300, 150, 54, ws[i], 1, i % 2 ? 1 : -1, FILL, RED, 30); }
    if (t > K.war - 0.05) impactBig(g, 360, 650, clamp((t - K.war + 0.05) / 0.6), 'WAR!');
    return;
  }
  if (t < K.wipe5) { // batteries drain, then: 2 seconds
    room(g);
    const lv = tt => 1 - eio(ss(tt, tt + 0.55, t));
    const out = ss(K.something - 0.1, K.something + 0.3, t);
    g.save(); g.translate(0, -120 * out); g.globalAlpha = 1 - out;
    battery(g, 300, 330, 260, 96, lv(K.time + 0.05), 'TIME', ss(K.time - 0.1, K.time + 0.1, t));
    battery(g, 300, 500, 260, 96, lv(K.sleep + 0.05), 'SLEEP', ss(K.sleep - 0.1, K.sleep + 0.1, t));
    battery(g, 300, 670, 260, 96, lv(K.peace + 0.05), 'PEACE', ss(K.peace - 0.1, K.peace + 0.1, t));
    g.restore();
    if (t >= K.gone2 && t < K.something) { const k = (0.5 + 0.5 * Math.sin(t * 20)) * (1 - out); g.save(); g.globalAlpha = k; g.strokeStyle = RED; g.lineWidth = 6; for (const y of [330, 500, 670]) { g.beginPath(); g.roundRect(292, y - 8, 276, 112, 10); g.stroke(); } g.restore(); }
    stopwatch(g, 360, 560, 190, clamp((t - K.something - 0.3) / (K.two + 0.15 - K.something - 0.3)) * 2, out);
    return;
  }
}

// ======================= ending: a new snake lets go =======================
function endScene(g, t) {
  workshop(g); stump(g); drawSaw(g); sawBlood(g, 0.15);
  const o = { mood: 'calm', mouth: 0, tongue: 0, cuts: [] };
  let hx, lift = 22;
  if (t < K.cuts) { hx = lerp(-90, 288, eout(clamp((t - K.wipe5) / (K.cuts - K.wipe5)))); lift = lerp(22, 46, ss(K.cuts - 0.4, K.cuts, t)); o.tongue = Math.sin(t * 7) > 0.3 ? 1 : 0; }
  else if (t < K.letGo) { hx = 288 + 4 * ss(K.cuts, K.cuts + 0.3, t); lift = 46 - 8 * ss(K.cuts, K.cuts + 0.3, t); o.mood = t < K.remember ? 'alert' : 'calm'; o.cuts = [{ i: 4, k: 1 }]; o.tongue = t > K.remember + 0.6 ? 1 : 0; }
  else { const k = clamp((t - K.letGo - 0.25) / 4.6); hx = lerp(292, 1180, k * (0.6 + 0.4 * k)); lift = lerp(38, 22, ss(K.letGo, K.letGo + 0.4, t)); o.cuts = [{ i: 4, k: 1 }]; o.tongue = Math.sin(t * 7) > 0.3 ? 1 : 0; }
  const P = groundSpine(hx, t, { lift, amp: 9 });
  g.save(); g.fillStyle = 'rgba(30,25,22,0.16)'; g.beginPath(); g.ellipse(P[20][0], FLOOR + 3, 200, 9, 0, 0, 7); g.fill(); g.restore();
  snakeChunk(g, P, 0, SN - 1, o); snakeHead(g, P, o);
  if (t >= K.cuts && t < K.cuts + 0.45) spark(g, 290, 806, (t - K.cuts) / 0.45, 22);
  // remember the snake: thought bubble with the first snake on the saw
  if (t >= K.remember - 0.1 && t < K.letGo + 0.3) { const k = ss(K.remember - 0.1, K.remember + 0.2, t) * (1 - ss(K.letGo, K.letGo + 0.3, t)); thought(g, 300, 540, 380, 250, k, [270, 760]);
    if (k > 0.3) { g.save(); g.globalAlpha = clamp(k * 1.5 - 0.4); g.beginPath(); g.ellipse(300, 540, 170, 105, 0, 0, 7); g.clip(); g.translate(300, 548); g.scale(0.44, 0.44); g.translate(-450, -790);
      const Pc = coilSpine(17.5, 55, { head: [280, 846] }); const cut = coilCuts(Pc, 18, 17.5); bloodPool(g, 1); coilDraw(g, Pc, { mood: 'dead', mouth: 0.25, headA: 0.15, cuts: cut, fill: '#d9d2bf' }, () => { drawSaw(g); sawBlood(g, 1); }); g.restore(); } }
}
function ctaScene(g, t) { endScene(g, t); }

// ======================= transitions =======================
function inkWipe(g, k) {
  if (k <= 0 || k >= 1) return; const e = k < 0.5 ? lerp(DW + 60, -60, eio(k * 2)) : -60, e2 = k < 0.5 ? DW + 60 : lerp(DW + 60, -60, eio((k - 0.5) * 2));
  g.save(); g.beginPath(); g.moveTo(e, -40); for (let y = -40; y <= DH + 40; y += 24) g.lineTo(e + (hash(y * 0.7 + 3) - 0.5) * 50, y); for (let y = DH + 40; y >= -40; y -= 30) g.lineTo(Math.min(e2, DW + 60) + (hash(y * 0.3) - 0.5) * 40, y); g.closePath();
  g.fillStyle = '#16120f'; g.fill(); g.restore();
}
const WIPES = [[K.wipe1 - 0.2, 0.42], [K.wipe2 - 0.22, 0.5], [K.wipe3 - 0.2, 0.45], [K.wipe4 - 0.2, 0.45], [K.wipe5 - 0.2, 0.45]];

// ======================= text =======================
const CAPS = [
  [K.start, K.sting - 0.05, [['ONE ', INK], ['TINY ', RED], ['CUT.', INK]]],
  [K.sting - 0.05, K.decided, [['HE FELT THE ', INK], ['STING.', RED]]],
  [K.decided, K.attacking, [['AND DECIDED...', INK]]],
  [K.attacking, K.struck - 0.1, [['THE SAW WAS ', INK], ['ATTACKING.', RED]]],
  [K.struck - 0.1, K.bit - 0.1, [['SO HE ', INK], ['STRUCK BACK.', RED]]],
  [K.bit - 0.1, K.cutMouth, [['HE BIT THE BLADE.', INK]]],
  [K.cutMouth, K.furious, [['AND CUT ', INK], ['HIS OWN MOUTH.', RED]]],
  [K.furious, K.wrapped, [['FURIOUS.', RED]]],
  [K.wrapped, K.crush, [['HE WRAPPED AROUND IT...', INK]]],
  [K.crush, K.tighter, [['TO ', INK], ['CRUSH IT.', RED]]],
  [K.tighter, K.deeper, [['TIGHTER...', INK]]],
  [K.deeper, K.until, [['DEEPER.', RED]]],
  [K.until, K.wipe2 - 0.3, [['UNTIL HE WAS ', INK], ['GONE.', RED]]],
  [K.name, K.horseFx - 0.1, [['THERE\'S A NAME FOR THIS.', INK]]],
  [K.bat, K.nothing - 0.15, [['A TINY BAT ', INK], ['BITES.', RED]]],
  [K.nothing - 0.15, K.but, [['THE BITE IS ', INK], ['NOTHING.', RED]]],
  [K.but, K.runs, [['BUT THE HORSE ', INK], ['PANICS.', RED]]],
  [K.runs, K.collapses, [['AND RUNS. AND RUNS.', INK]]],
  [K.collapses, K.wipe3 - 0.25, [['UNTIL IT ', INK], ['COLLAPSES.', RED]]],
  [K.hurts, K.wipe4 - 0.2, [['THAT\'S WHAT ', INK], ['HURTS YOU.', RED]]],
  [K.everyday, K.rude, [['WE DO IT ', INK], ['EVERY DAY.', RED]]],
  [K.rude, K.fire, [['ONE ', INK], ['RUDE COMMENT.', RED]]],
  [K.fire, K.replay, [['YOU ', INK], ['FIRE BACK.', RED]]],
  [K.replay, K.argument, [['REPLAY IT ', INK], ['ALL NIGHT.', RED]]],
  [K.argument, K.turn, [['ONE SMALL ARGUMENT...', INK]]],
  [K.turn, K.time, [['TURNED INTO A ', INK], ['WAR.', RED]]],
  [K.gone2, K.something, [['GONE.', RED]]],
  [K.something, K.wipe5 - 0.2, [['OVER A ', INK], ['2-SECOND ', RED], ['THING.', INK]]],
  [K.next, K.remember, [['NEXT TIME SOMETHING ', INK], ['CUTS YOU,', RED]]],
  [K.remember, K.letGo, [['REMEMBER ', INK], ['THE SNAKE.', RED]]],
  [K.letGo, K.rule - 0.05, [['LET GO ', RED], ['OF THE SAW.', INK]]],
];
function caption(g, t) {
  for (const [t0, t1, a] of CAPS) { if (t < t0 || t >= t1) continue; const k = ss(t0, t0 + 0.1, t), pop = 1 + 0.1 * Math.exp(-(t - t0) * 12);
    g.save(); g.globalAlpha = k * (1 - ss(t1 - 0.06, t1, t)); g.translate(360, 922); g.scale(pop, pop); g.translate(-360, -922);
    g.fillStyle = 'rgba(237,230,214,0.9)'; g.beginPath(); g.roundRect(60, 888, 600, 68, 14); g.fill();
    words(g, a, 360, 938, 54, 570); g.restore(); }
}
function counterBox(g, t) {
  let label = null, val = '', col = RED;
  if (t < K.wipe1 || (t >= K.cut && t < K.wipe2 - 0.2)) { label = 'CUTS'; val = String(cutCount(t)); }
  else if (t >= K.runs && t < K.wipe3) { label = 'KM RUN'; val = (horseScroll(t) / 260).toFixed(1); col = INK; }
  else if (t >= K.replay && t < K.argument) { label = 'REPLAYS'; val = String(1 + Math.floor((t - K.replay) * 2.2 * 6)); }
  if (!label) return;
  const flash = t >= K.cut && t < K.cut + 0.3 ? 1 : 0;
  g.save(); const x = 230, y = 208, w = 260, h = 58; g.translate(360, y + h / 2); const p = 1 + 0.12 * flash; g.scale(p, p); g.translate(-360, -(y + h / 2));
  g.fillStyle = 'rgba(251,247,238,0.95)'; g.beginPath(); g.roundRect(x, y, w, h, 12); g.fill();
  inkLine(g, [[x, y + 6], [x, y + h - 6], [x + 6, y + h], [x + w - 6, y + h], [x + w, y + h - 6], [x + w, y + 6], [x + w - 6, y], [x + 6, y], [x, y + 6]], 3);
  g.font = '26px "Patrick Hand SC"'; g.textAlign = 'left'; g.fillStyle = INK; g.fillText(label, x + 18, y + 38);
  g.font = '36px "Permanent Marker"'; g.textAlign = 'right'; g.fillStyle = col; g.fillText(val, x + w - 16, y + 44); g.restore();
}
function plate(g, y0, h) { g.fillStyle = 'rgba(237,230,214,0.9)'; g.beginPath(); g.roundRect(56, y0, 608, h, 16); g.fill(); }
function bigLines(g, t) {
  g.textBaseline = 'alphabetic';
  if (t < K.wipe1 - 0.02) { const p = 1 + 0.12 * Math.exp(-t * 8); g.save(); g.translate(360, 320); g.scale(p, p); g.translate(-360, -320);
    plate(g, 280, 128); words(g, [['HE KILLED ', INK], ['HIMSELF.', RED]], 360, 338, 66, 580);
    const k2 = ss(1.3, 1.45, t); if (k2 > 0) { g.globalAlpha = k2; words(g, [['THE SAW ', INK], ['NEVER MOVED.', RED]], 360, 394, 50, 540); } g.restore(); }
  if (t >= K.rule && t < K.cta) { const k1 = ss(K.rule, K.rule + 0.2, t), k2 = ss(K.worth - 0.2, K.worth, t);
    g.save(); plate(g, 440, 140); g.globalAlpha = k1; words(g, [['NOT EVERY BATTLE', INK]], 360, 502, 64, 580, 'Permanent Marker'); g.globalAlpha = k2; words(g, [['IS ', INK], ['WORTH FIGHTING.', RED]], 360, 562, 54, 580, 'Permanent Marker'); g.restore(); }
  if (t >= K.cta) { const k = ss(K.cta, K.cta + 0.25, t); g.save(); g.globalAlpha = k; plate(g, 440, 140);
    words(g, [['SEND THIS TO SOMEONE', INK]], 360, 502, 58, 580, 'Permanent Marker'); words(g, [['WHO ', INK], ['NEEDS IT.', RED]], 360, 562, 58, 580, 'Permanent Marker'); g.restore(); }
}

// ======================= camera [zoom, cx, cy, shake] =======================
function cam(t) {
  const HEAD = [262, 712];
  if (t < K.wipe1) {
    if (t < 0.6) { const k = eio(clamp(t / 0.6)); return [lerp(2.7, 1.5, k), lerp(HEAD[0] + 20, 395, k), lerp(HEAD[1], 770, k), 4 * (1 - k)]; }
    if (t >= 1.5 && t < 2.32) { const k = clamp((t - 1.5) / 0.82); return [lerp(2.0, 2.15, k), 600, 790, 0]; } // the saw handle: perfectly still
    return [1.5 + 0.08 * ss(0.6, 2.6, t), 395, 770, 3 * Math.abs(Math.sin(t * 9))];
  }
  if (t < K.cut) { const hx = storyState(t).P[0][0]; return [1.75, clamp(hx - 40, 200, 470), 800, 0]; }
  if (t < K.sting) { const k = eout(clamp((t - K.cut) / 0.25)); return [lerp(1.75, 2.3, k), lerp(270, 285, k), lerp(780, 800, k), 0]; }
  if (t < K.decided) { const k = eout(clamp((t - K.sting) / 0.3)); return [lerp(2.3, 1.5, k), lerp(285, 300, k), lerp(800, 740, k), 6 * Math.exp(-(t - K.sting) * 6)]; }
  if (t < K.attacking) return [1.5 + 0.08 * ss(K.decided, K.attacking, t), 300, 660, 0];
  if (t < K.struck - 0.1) { const k = eout(clamp((t - K.attacking) / 0.25)); return [lerp(1.58, 1.8, k), 300, lerp(660, 580, k), 2 * Math.sin(t * 30) * k]; }
  if (t < K.bit - 0.2) { return [1.6, 300, 770, (t > K.struck + 0.1 && t < K.struck + 0.5) ? 7 : 0]; }
  if (t < K.cutMouth) { const k = eout(clamp((t - K.bit + 0.2) / 0.25)); return [lerp(1.6, 2.3, k), 290, 790, t > K.bit && t < K.bit + 0.4 ? 6 : 1.5]; }
  if (t < K.furious) return [2.6, 300, 820, 1]; // close: blood drips from the mouth
  if (t < K.wrapped) { const k = eout(clamp((t - K.furious) / 0.3)); return [lerp(2.6, 1.6, k), lerp(300, 250, k), lerp(820, 740, k), 4]; }
  if (t < K.tighter) { const k = eio(clamp((t - K.wrapped) / 1.0)); return [lerp(1.6, 1.4, k), lerp(250, 395, k), lerp(740, 770, k), 0]; }
  if (t < K.deeper) { const k = eout(clamp((t - K.tighter) / 0.3)); return [lerp(1.4, 1.75, k), lerp(395, 330, k), 740, 3]; }
  if (t < K.until) { const k = eout(clamp((t - K.deeper) / 0.25)); return [lerp(2.3, 2.5, k), 420, 820, 4]; }
  if (t < K.wipe2) { const k = eio(clamp((t - K.until) / 1.0)); return [lerp(1.8, 1.45, k), lerp(330, 395, k), lerp(780, 780, k), 0]; }
  if (t < K.name) { if (t < K.his) return [1.0 + 0.25 * ss(K.sawOne, K.sawOne + 0.4, t), 260, 600, 0]; if (t < K.rest) { const k = eout(clamp((t - K.his) / 0.25)); return [lerp(1.25, 1.35, k), lerp(260, 460, k), 600, 0]; } const k = eout(clamp((t - K.rest) / 0.4)); return [lerp(1.35, 1.0, k), lerp(460, 360, k), lerp(600, 640, k), 0]; }
  if (t < K.bat) return [1.0 + 0.06 * ss(K.name, K.bat, t), 360, 640, 0];
  if (t < K.bites) return [1.1, 420, 700, 0];
  if (t < K.nothing - 0.15) { const k = eout(clamp((t - K.bites) / 0.25)); return [lerp(1.1, 2.0, k), lerp(420, 470, k), lerp(700, 820, k), 0]; }
  if (t < K.but) return [2.4 + 0.2 * ss(K.nothing, K.but, t), 480, 830, 0];
  if (t < K.runs) { const k = eout(clamp((t - K.but) / 0.3)); return [lerp(2.4, 1.05, k), lerp(480, 380, k), lerp(830, 720, k), t > K.panics ? 5 : 0]; }
  if (t < K.collapses) return [1.05 + 0.08 * ss(K.runs, K.collapses, t), 360, 720, 3];
  if (t < K.wipe3) { const k = eout(clamp((t - K.collapses) / 0.4)); return [lerp(1.1, 1.25, k), lerp(360, 430, k), lerp(720, 800, k), 8 * Math.exp(-(t - K.collapses - 0.3) * 4) * (t > K.collapses + 0.3 ? 1 : 0)]; }
  if (t < K.wipe4) { if (t < K.big) return [1.1, 360, 400, 0]; if (t < K.hurts) { const k = eout(clamp((t - K.big) / 0.25)); return [1.1, 360, lerp(400, 600, k), 4 * Math.exp(-(t - K.big) * 4)]; } const k = eout(clamp((t - K.hurts) / 0.3)); return [lerp(1.1, 1.0, k), 360, lerp(600, 640, k), 0]; }
  if (t < K.rude) return [1.35 + 0.08 * ss(K.everyday, K.rude, t), 360, 640, 0];
  if (t < K.fire) { const k = eout(clamp((t - K.rude - 0.15) / 0.25)); return [lerp(1.0, 1.45, k), 360, lerp(600, 600, k), 0]; }
  if (t < K.replay) return [1.1, 360, 620, 4];
  if (t < K.argument) return [1.0 + 0.12 * ss(K.replay, K.argument, t), 360, 600, 0];
  if (t < K.time) { if (t < K.turn) return [1.15, 360, 680, 0]; return [1.05 + 0.15 * ss(K.turn, K.war, t), 360, 640, t > K.war ? 9 * Math.exp(-(t - K.war) * 3) : 3]; }
  if (t < K.wipe5) { if (t < K.something) return [1.12, 360, 560, t > K.gone2 && t < K.gone2 + 0.4 ? 6 : 0]; return [1.0 + 0.12 * ss(K.something, K.wipe5, t), 360, 600, 0]; }
  if (t < K.cuts) { const hx = endSnakeX(t); return [1.7, clamp(hx - 40, 200, 470), 800, 0]; }
  if (t < K.remember) { const k = eout(clamp((t - K.cuts) / 0.25)); return [lerp(1.7, 1.9, k), 290, 800, 0]; }
  if (t < K.letGo) { const k = eout(clamp((t - K.remember) / 0.35)); return [lerp(1.9, 1.3, k), lerp(290, 320, k), lerp(800, 680, k), 0]; }
  if (t < K.rule) { const k = eio(clamp((t - K.letGo) / 1.4)); return [lerp(1.3, 1.15, k), lerp(320, 420, k), lerp(680, 700, k), 0]; }
  return [1.15 + 0.08 * ss(K.rule, DUR, t), 440, 700, 0];
}
function endSnakeX(t) { return lerp(-90, 288, eout(clamp((t - K.wipe5) / (K.cuts - K.wipe5)))); }
function scene(g, t) {
  if (t < K.wipe2) return workshopScene(g, t);
  if (t < K.name) return scoreScene(g, t);
  if (t < K.wipe3) return horseScene(g, t);
  if (t < K.wipe4) return equationScene(g, t);
  if (t < K.wipe5) return lifeScene(g, t);
  return endScene(g, t);
}
function frame(g, t) {
  T = t;
  const [z, cx, cy, sh] = cam(t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0); g.translate(360, 640); g.scale(z, z); g.translate(-cx + Math.sin(t * 61) * sh, -cy + Math.cos(t * 47) * sh);
  scene(g, t);
  g.setTransform(W / DW, 0, 0, H / DH, 0, 0);
  const hostile = t < K.wipe1 || (t >= K.attacking && t < K.gone) || (t >= K.panics && t < K.collapses) || (t >= K.turn && t < K.time);
  if (hostile) { const p = 0.5 + 0.5 * Math.sin(t * 9); const gr = g.createRadialGradient(360, 640, 420, 360, 640, 900); gr.addColorStop(0, 'rgba(200,40,42,0)'); gr.addColorStop(1, `rgba(200,40,42,${0.1 + 0.1 * p})`); g.fillStyle = gr; g.fillRect(0, 0, DW, DH); }
  const gr = g.createRadialGradient(360, 640, 380, 360, 640, 900); gr.addColorStop(0, 'rgba(120,95,60,0)'); gr.addColorStop(1, 'rgba(120,95,60,0.12)'); g.fillStyle = gr; g.fillRect(0, 0, DW, DH);
  for (const tf of [K.name, K.rude, K.fire, K.replay, K.argument, K.time]) if (t >= tf && t < tf + 0.12) { g.fillStyle = `rgba(255,252,244,${0.7 * (1 - (t - tf) / 0.12)})`; g.fillRect(0, 0, DW, DH); }
  counterBox(g, t); caption(g, t); bigLines(g, t);
  for (const [w0, d] of WIPES) inkWipe(g, (t - w0) / d);
}
window.renderAt = (t, sub = 1) => {
  sub = Math.max(1, sub | 0);
  if (sub === 1) frame(out, t);
  else { out.setTransform(1, 0, 0, 1, 0, 0); out.fillStyle = '#000'; out.fillRect(0, 0, W, H);
    for (let i = 0; i < sub; i++) { A.setTransform(1, 0, 0, 1, 0, 0); frame(A, t + (i / sub - 0.5) * (1 / 30) * 0.5); out.setTransform(1, 0, 0, 1, 0, 0); out.globalCompositeOperation = 'lighter'; out.globalAlpha = 1 / sub; out.drawImage(acc, 0, 0); }
    out.globalCompositeOperation = 'source-over'; out.globalAlpha = 1; }
  return cv.toDataURL('image/jpeg', 0.92);
};
// ======================= sound cues (no SFX in the hook 0-3.5 s or the rule + CTA) =======================
window.events = (() => { const e = [];
  e.push({ t: K.wipe1 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  for (let i = 0; i < 3; i++) e.push({ t: K.start + 0.8 + i * 0.5, s: 'slither', g: 0.35, pan: -0.3 + i * 0.2 });
  e.push({ t: K.sting - 0.05, s: 'hiss', g: 0.7, pan: 0 });
  e.push({ t: K.attacking, s: 'hiss', g: 0.8, pan: 0, rate: 0.9 });
  e.push({ t: K.struck + 0.1, s: 'clang', g: 0.75, pan: 0.1 });
  e.push({ t: K.bit, s: 'clang', g: 0.7, pan: 0, rate: 0.9 }, { t: K.bit + 0.05, s: 'scrape', g: 0.5, pan: 0 });
  e.push({ t: K.cutMouth, s: 'drip', g: 0.45, pan: 0 });
  e.push({ t: K.wrapped, s: 'slither', g: 0.55, pan: 0.2, rate: 0.9 });
  e.push({ t: K.crush, s: 'creak', g: 0.55, pan: 0 });
  e.push({ t: K.tighter, s: 'scrape', g: 0.6, pan: 0 }, { t: K.deeper, s: 'scrape', g: 0.65, pan: 0.2, rate: 0.9 });
  e.push({ t: K.until + 0.2, s: 'heart', g: 0.5, pan: 0 });
  e.push({ t: K.gone, s: 'thud', g: 0.6, pan: 0 });
  e.push({ t: K.wipe2 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.sawOne + 0.43, s: 'marker', g: 0.45, pan: -0.3 }, { t: K.reaction, s: 'tick', g: 0.5, pan: 0.3 });
  e.push({ t: K.name - 0.05, s: 'swipe', g: 0.4, pan: 0, rate: 1.2 }, { t: K.name, s: 'wind', g: 0.35, pan: 0 });
  e.push({ t: K.horseFx, s: 'marker', g: 0.5, pan: 0 });
  e.push({ t: K.bat - 0.05, s: 'flap', g: 0.55, pan: 0.4 }, { t: K.bites, s: 'nip', g: 0.5, pan: 0.2 });
  e.push({ t: K.panics - 0.05, s: 'neigh', g: 0.7, pan: 0 });
  e.push({ t: K.runs - 0.1, s: 'gallop', g: 0.7, pan: 0 });
  e.push({ t: K.collapses + 0.3, s: 'thud', g: 0.8, pan: 0, rate: 0.8 });
  e.push({ t: K.wipe3 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.small, s: 'marker', g: 0.45, pan: -0.2 }, { t: K.big, s: 'boom', g: 0.6, pan: 0 }, { t: K.hurts, s: 'crack', g: 0.55, pan: 0 });
  e.push({ t: K.wipe4 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.rude + 0.15, s: 'ding', g: 0.55, pan: 0.2 }, { t: K.fire, s: 'typing', g: 0.6, pan: 0 });
  e.push({ t: K.replay, s: 'clock', g: 0.45, pan: -0.3 });
  e.push({ t: K.war - 0.05, s: 'boom', g: 0.75, pan: 0 });
  e.push({ t: K.time + 0.05, s: 'drain', g: 0.45, pan: -0.2 }, { t: K.sleep + 0.05, s: 'drain', g: 0.45, pan: 0, rate: 0.9 }, { t: K.peace + 0.05, s: 'drain', g: 0.45, pan: 0.2, rate: 0.8 });
  e.push({ t: K.something + 0.3, s: 'tick', g: 0.5, pan: 0 });
  e.push({ t: K.wipe5 - 0.15, s: 'swipe', g: 0.5, pan: 0 });
  e.push({ t: K.next + 0.2, s: 'slither', g: 0.3, pan: -0.3 });
  e.push({ t: K.letGo + 0.3, s: 'slither', g: 0.35, pan: 0.3 });
  return e.sort((a, b) => a.t - b.t); })();
window.TL = K; window.DUR = DUR;
document.fonts.load('40px "Patrick Hand SC"').then(() => document.fonts.load('40px "Permanent Marker"')).then(() => { window.ready = true; });
