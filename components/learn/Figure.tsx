/**
 * Figure — a committed, theme-aware static plot.
 *
 * p5 sketches carry intuition and mermaid carries structure, but neither can
 * show a real matplotlib result (an ROC curve on actual data, a learning
 * curve, a dendrogram). Those are generated at author time by
 * `npm run figures` and committed as an SVG pair under
 * `public/images/ml/<slug>/`, then embedded here.
 *
 * Pass `src` without the `-dark.svg` / `-light.svg` suffix and both variants
 * are wired up; CSS swaps them with the site theme. Pass `single` for a figure
 * that reads correctly on either background.
 *
 * Server component: nothing here is interactive, so it costs no client JS on
 * the 292 pages that use it.
 */
export interface FigureProps {
  /**
   * Path under `public/`, WITHOUT extension and without the theme suffix —
   * e.g. `/images/ml/phase-03-regression/learning-curves`.
   * With `single`, pass the full path including extension.
   */
  src: string;
  /** Accessible description of what the plot shows. Required — these are data. */
  alt: string;
  /** Shown in the panel header bar. */
  title?: string;
  /** Shown under the plot: what the reader should take away. */
  caption?: string;
  /** Set when one image works on both themes (pass a full path with extension). */
  single?: boolean;
  /** Intrinsic size, used to reserve layout space and avoid layout shift. */
  width?: number;
  height?: number;
}

import { existsSync } from "node:fs";
import { join } from "node:path";

/**
 * The file to serve for a figure path: the `.webp` when the SVG was
 * rasterised (scripts/rasterize-figures.mjs does that to plots whose SVG is
 * over 256 KB), otherwise the SVG. Checked on the server at build time, so
 * pages keep naming figures the same way whichever format is on disk.
 */
function served(svgPath: string): string {
  if (!svgPath.endsWith(".svg")) return svgPath;
  const webp = svgPath.replace(/\.svg$/, ".webp");
  return existsSync(join(process.cwd(), "public", webp)) ? webp : svgPath;
}

export function Figure({
  src,
  alt,
  title,
  caption,
  single = false,
  width = 900,
  height = 540,
}: FigureProps) {
  const darkSrc = served(single ? src : `${src}-dark.svg`);
  const lightSrc = served(single ? src : `${src}-light.svg`);

  return (
    <figure className="pch-figure">
      <div className="pch-viz__bar">
        <span className="pch-viz__tag">figure</span>
        <span className="pch-viz__title">{title ?? alt}</span>
        <span className="pch-figure__lib">matplotlib</span>
      </div>

      <div className="pch-figure__stage">
        {/* Plain <img>, not next/image: these are committed files served from
            public/ as they are. The optimiser has nothing to do for an SVG,
            the large plots are already WebP, and on the free plan its quota
            is better spent nowhere. Only the visible variant is fetched: the
            other is display:none and lazy, so the browser never requests it. */}
        <img
          className="pch-figure__img pch-figure__img--dark"
          src={darkSrc}
          alt={alt}
          width={width}
          height={height}
          loading="lazy"
          decoding="async"
        />
        {!single && (
          <img
            className="pch-figure__img pch-figure__img--light"
            src={lightSrc}
            alt={alt}
            width={width}
            height={height}
            loading="lazy"
            decoding="async"
          />
        )}
      </div>

      {caption ? (
        <figcaption className="pch-figure__caption">{caption}</figcaption>
      ) : null}
    </figure>
  );
}

export default Figure;
