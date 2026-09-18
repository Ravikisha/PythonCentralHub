// Rasterise two SVGs at the same width and compare them pixel by pixel.
// This is the only check that actually proves an optimisation is visually
// lossless; coordinate diffs cannot, because svgo restructures paths.
import sharp from "sharp";
import { readFileSync } from "node:fs";

const WIDTH = Number(process.env.W || 1400);

const HEIGHT = Number(process.env.H || 0);
async function render(p) {
  const r = sharp(readFileSync(p), { density: 300 });
  const opts = HEIGHT ? { width: WIDTH, height: HEIGHT, fit: "fill" }
                      : { width: WIDTH };
  return r.resize(opts)
    .flatten({ background: "#ffffff" })
    .raw()
    .toBuffer({ resolveWithObject: true });
}

const pairs = process.argv.slice(2);
let worstAll = 0;
for (let i = 0; i < pairs.length; i += 3) {
  const [a, b, name] = [pairs[i], pairs[i + 1], pairs[i + 2] ?? pairs[i]];
  const A = await render(a);
  const B = await render(b);
  if (A.info.width !== B.info.width || A.info.height !== B.info.height) {
    console.log(`--- ${name}\n    RENDERED SIZE DIFFERS: ` +
      `${A.info.width}x${A.info.height} vs ${B.info.width}x${B.info.height}`);
    worstAll = 255;
    continue;
  }
  const n = A.data.length;
  let diffPx = 0, maxCh = 0, sum = 0;
  const ch = A.info.channels;
  for (let p = 0; p < n; p += ch) {
    let d = 0;
    for (let c = 0; c < Math.min(ch, 3); c++) {
      const v = Math.abs(A.data[p + c] - B.data[p + c]);
      if (v > d) d = v;
    }
    if (d > 0) { diffPx++; sum += d; }
    if (d > maxCh) maxCh = d;
  }
  const total = n / ch;
  console.log(`--- ${name}`);
  console.log(`    rendered         : ${A.info.width}x${A.info.height} px`);
  console.log(`    pixels differing : ${diffPx} of ${total} ` +
    `(${(100 * diffPx / total).toFixed(4)}%)`);
  console.log(`    worst channel    : ${maxCh} of 255`);
  console.log(`    mean |delta| over differing px: ` +
    `${diffPx ? (sum / diffPx).toFixed(2) : "0"}`);
  if (maxCh > worstAll) worstAll = maxCh;
}
console.log(`\nWORST channel difference across all pairs: ${worstAll} / 255`);
