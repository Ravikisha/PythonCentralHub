// Regenerate the brand images from the logo.
//
//   node scripts/brand-icons.mjs
//
// The mark is drawn in components/brand/Wordmark.tsx with theme colours. Here
// it is the same geometry with fixed colours, on a navy tile so it reads on
// light and dark browser tabs and home screens alike. Writes:
//
//   public/favicon.svg                         vector favicon
//   public/favicon.ico                         16, 32 and 48 px (PNG-in-ICO)
//   public/images/icons/icon-<n>x<n>.png       PWA icons listed in manifest.json
//   public/icon512_rounded.png                 "any" purpose icon
//   public/icon512_maskable.png                full-bleed, mark inside the safe zone
//   public/og.png                              default 1200x630 share image
import { mkdirSync, writeFileSync } from "node:fs";
import sharp from "sharp";

const NAVY = "#0f1f33";
const BLUE = "#4b8bbe";
const BLUE_BRIGHT = "#6ba9dd";
const YELLOW = "#ffd343";

/**
 * The hub, in a 32x32 box: a core, six satellites on spokes, and a faint
 * orbit through the satellites. Same geometry as components/brand/Wordmark.tsx.
 */
function hub({ spoke = BLUE_BRIGHT, outline = NAVY } = {}) {
  const R = 11;
  const pts = [-90, -30, 30, 90, 150, 210].map((deg, i) => {
    const a = (deg * Math.PI) / 180;
    return [16 + R * Math.cos(a), 16 + R * Math.sin(a), i % 2 === 1];
  });
  const f = (n) => n.toFixed(2);
  return [
    `<circle cx="16" cy="16" r="${R}" fill="none" stroke="${spoke}" stroke-opacity="0.4" stroke-width="1.2"/>`,
    `<g stroke="${spoke}" stroke-width="2" stroke-linecap="round">`,
    ...pts.map(([x, y]) => `<line x1="16" y1="16" x2="${f(x)}" y2="${f(y)}"/>`),
    `</g>`,
    ...pts.map(
      ([x, y, yellow]) =>
        `<circle cx="${f(x)}" cy="${f(y)}" r="2.7" fill="${yellow ? YELLOW : spoke}" stroke="${outline}" stroke-width="0.9"/>`,
    ),
    `<circle cx="16" cy="16" r="5.2" fill="${spoke}" stroke="${outline}" stroke-width="1"/>`,
    `<circle cx="16" cy="16" r="2.1" fill="${YELLOW}"/>`,
  ].join("");
}

/** The mark on a rounded navy tile. `pad` is the share of the tile left around it. */
function tile({ size = 512, radius = 0.22, pad = 0.14 } = {}) {
  const inner = size * (1 - pad * 2);
  const scale = inner / 32;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <rect width="${size}" height="${size}" rx="${size * radius}" fill="${NAVY}"/>
  <g transform="translate(${size * pad} ${size * pad}) scale(${scale})">${hub()}</g>
</svg>`;
}

const png = (svg, size) => sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();

/** An ICO file holding PNG images (supported by every current browser). */
function ico(images) {
  const header = Buffer.alloc(6);
  header.writeUInt16LE(0, 0);
  header.writeUInt16LE(1, 2);
  header.writeUInt16LE(images.length, 4);
  const entries = [];
  let offset = 6 + 16 * images.length;
  for (const { size, data } of images) {
    const e = Buffer.alloc(16);
    e.writeUInt8(size >= 256 ? 0 : size, 0);
    e.writeUInt8(size >= 256 ? 0 : size, 1);
    e.writeUInt8(0, 2);
    e.writeUInt8(0, 3);
    e.writeUInt16LE(1, 4);
    e.writeUInt16LE(32, 6);
    e.writeUInt32LE(data.length, 8);
    e.writeUInt32LE(offset, 12);
    offset += data.length;
    entries.push(e);
  }
  return Buffer.concat([header, ...entries, ...images.map((i) => i.data)]);
}

mkdirSync("public/images/icons", { recursive: true });

// Favicon: a small tile with less padding, so the hub is as large as it can be.
const favicon = tile({ size: 64, radius: 0.24, pad: 0.06 });
writeFileSync("public/favicon.svg", favicon);
writeFileSync(
  "public/favicon.ico",
  ico(await Promise.all([16, 32, 48].map(async (size) => ({ size, data: await png(favicon, size) })))),
);

for (const size of [72, 96, 128, 152, 192, 384, 512]) {
  writeFileSync(`public/images/icons/icon-${size}x${size}.png`, await png(tile({ size: 512 }), size));
}
writeFileSync("public/icon512_rounded.png", await png(tile({ size: 512 }), 512));
// Maskable: square, full bleed; launchers crop to a circle of 80%, so the mark
// sits well inside that.
writeFileSync("public/icon512_maskable.png", await png(tile({ size: 512, radius: 0, pad: 0.24 }), 512));

// Default share image.
const og = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <radialGradient id="glow" cx="78%" cy="40%" r="60%">
      <stop offset="0" stop-color="${BLUE}" stop-opacity="0.35"/>
      <stop offset="1" stop-color="${NAVY}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="630" fill="${NAVY}"/>
  <rect width="1200" height="630" fill="url(#glow)"/>
  <g transform="translate(760 95) scale(13.5)">${hub()}</g>
  <text x="88" y="250" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="78" font-weight="800" fill="${BLUE_BRIGHT}">Python</text>
  <text x="88" y="340" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="78" font-weight="800" fill="#ffffff">Central Hub</text>
  <text x="90" y="420" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="30" fill="#b9c4d0">Free courses in Python, data and machine learning,</text>
  <text x="90" y="462" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="30" fill="#b9c4d0">with code you run in the page.</text>
  <rect x="90" y="520" width="140" height="8" rx="4" fill="${YELLOW}"/>
</svg>`;
writeFileSync("public/og.png", await sharp(Buffer.from(og)).png().toBuffer());

console.log("brand images written: favicon.svg, favicon.ico, 7 PWA icons, 2 launcher icons, og.png");
