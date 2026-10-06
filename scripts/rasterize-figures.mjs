// Turn oversized figure SVGs into WebP.
//
//   node scripts/rasterize-figures.mjs            convert and delete the SVG
//   node scripts/rasterize-figures.mjs --dry-run  report only
//
// Most figures are small, crisp vectors and stay SVG. A few are scatter plots
// and dense heatmaps whose SVG holds one element per point -- 16 of them were
// over 1 MB and the largest 4 MB, for an image that is 900 pixels wide on the
// page. Rendered at twice that width and saved as WebP they are a few percent
// of the size and look the same, text included.
//
// components/learn/Figure.tsx prefers `<name>.webp` when it exists, so no
// page has to change. `npm run figures` runs this after regenerating plots,
// so a plot that grows past the limit is converted the next time.
import { readdirSync, statSync, unlinkSync, existsSync } from "node:fs";
import { join } from "node:path";
import sharp from "sharp";

const ROOT = "public/images";
/** SVGs at or above this size are converted. */
const LIMIT = 256 * 1024;
/** Output width: 2x the 900px the figure panel shows, for sharp text on HiDPI. */
const WIDTH = 1800;
const QUALITY = 82;

const dryRun = process.argv.includes("--dry-run");

function walk(dir, out = []) {
  for (const entry of readdirSync(dir)) {
    const p = join(dir, entry);
    if (statSync(p).isDirectory()) walk(p, out);
    else if (entry.endsWith(".svg")) out.push(p);
  }
  return out;
}

let before = 0;
let after = 0;
let converted = 0;

for (const svg of walk(ROOT)) {
  const size = statSync(svg).size;
  if (size < LIMIT) continue;

  const webp = svg.replace(/\.svg$/, ".webp");
  if (dryRun) {
    console.log(`would convert ${(size / 1024 / 1024).toFixed(1)} MB  ${svg}`);
    before += size;
    continue;
  }

  // density scales the SVG's own size; resize then pins the output width, so
  // the result is WIDTH px wide whatever size the SVG declared.
  await sharp(svg, { density: 192, limitInputPixels: false })
    .resize({ width: WIDTH, withoutEnlargement: false })
    .webp({ quality: QUALITY, effort: 6 })
    .toFile(webp);

  const out = statSync(webp).size;
  if (!existsSync(webp) || out === 0) {
    console.error(`failed: ${svg}`);
    process.exitCode = 1;
    continue;
  }

  unlinkSync(svg);
  before += size;
  after += out;
  converted += 1;
  console.log(
    `${(size / 1024).toFixed(0).padStart(6)} KB -> ${(out / 1024).toFixed(0).padStart(4)} KB  ${webp}`,
  );
}

const mb = (n) => (n / 1024 / 1024).toFixed(1);
console.log(
  dryRun
    ? `\n${mb(before)} MB of SVG over ${LIMIT / 1024} KB would be converted.`
    : `\n${converted} figure(s): ${mb(before)} MB -> ${mb(after)} MB.`,
);
