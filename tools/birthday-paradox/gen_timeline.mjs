// Builds timeline.json: the single timing source for scene, overlay, sound and renderer.
// One simulated room: 70 birthdays from a seeded RNG. The first 22 are distinct and
// person 23 shares person 8's birthday, so the first match lands exactly where the
// maths says the odds pass 50%. Everyone after 23 is drawn at random.
import fs from 'node:fs';
let s = 20261021;
const rnd = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 2 ** 32; };
const N = 70, MATCH_WITH = 8, MATCH_DAY = 72; // day index 72 = 14 March
const days = [];
while (days.length < 22) {
  const d = days.length === MATCH_WITH - 1 ? MATCH_DAY : Math.floor(rnd() * 365);
  if (!days.includes(d) && (d !== MATCH_DAY || days.length === MATCH_WITH - 1)) days.push(d);
}
days.push(MATCH_DAY);
while (days.length < N) days.push(Math.floor(rnd() * 365));

// Landing times (seconds). Accelerating arrivals, a held breath before 23, a fast fill to 70.
const land = [2.35];
for (let k = 2; k <= 22; k++) land.push(+(land.at(-1) + 0.58 * 0.9625 ** (k - 2)).toFixed(3));
land.push(11.75);
for (let k = 1; k <= N - 23; k++) land.push(+(15.2 + 2.8 * Math.sqrt(k / (N - 23))).toFixed(3));

const P = n => { let q = 1; for (let k = 0; k < n; k++) q *= (365 - k) / 365; return 1 - q; };
const people = days.map((day, i) => {
  const prior = days.slice(0, i).filter(d => d === day).length;
  // drop: seconds the dot falls before it lands (slow for the held breath on #23)
  const drop = i < 22 ? 0.34 : i === 22 ? 0.6 : 0.22;
  return { n: i + 1, day, t: land[i], drop, stack: prior, p: +P(i + 1).toFixed(5) };
});
// tRed: when this dot turns red (the moment its first birthday twin lands)
people.forEach(p => {
  const twins = people.filter(q => q !== p && q.day === p.day);
  p.tRed = twins.length ? Math.min(...twins.map(q => Math.max(p.t, q.t))) : null;
});
const firstMatch = people.find(p => p.stack > 0);
if (firstMatch.n !== 23) throw Error('first match must be person 23, got ' + firstMatch.n);
const spec = {
  duration: 21.5, fps: 30,
  shots: [[0, 2.2, 'hook'], [2.2, 11.0, 'build'], [11.0, 11.75, 'held breath'], [11.75, 15.2, 'reveal: 253 pairs'],
          [15.2, 18.0, 'fill to 70'], [18.0, 20.2, 'thesis'], [20.2, 21.5, 'implode and loop']],
  matchDay: MATCH_DAY, matchWith: MATCH_WITH,
  people,
  reviewTimes: [0.03, 0.6, 1.5, 2.3, 3.2, 5, 7.5, 10.5, 11.3, 11.8, 12.4, 13.6, 15.0, 16.0, 17.0, 18.1, 19.0, 20.0, 20.6, 21.1, 21.45]
};
fs.writeFileSync(new URL('./timeline.json', import.meta.url), JSON.stringify(spec, null, 1));
console.log('collisions:', people.filter(p => p.stack).map(p => `#${p.n}@${p.day}`).join(' '));
console.log('P(22,23,70)=', P(22), P(23), P(70), 'pairs(23,70)=', 23 * 22 / 2, 70 * 69 / 2, 't22', land[21]);
