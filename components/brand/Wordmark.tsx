import { SITE_NAME } from "@/lib/site";

/**
 * The Python Central Hub mark: a hub.
 *
 * A core node with six satellites around it, joined by spokes and a faint
 * orbit -- one place every course connects to. Drawn in the two colours people
 * read as Python, blue and yellow, without borrowing the Python Software Foundation's
 * (trademarked) snake logo. The spokes and core are blue; the satellites
 * alternate blue and yellow, and the core has a yellow centre, so it reads at
 * 16px as a single bright node rather than a cluster of dots.
 *
 * Inline, so it costs nothing and follows the theme's colour tokens.
 * public/favicon.svg and the app icons are the same drawing with fixed colours
 * (scripts/brand-icons.mjs).
 */
const R = 11;
const SATELLITES = [-90, -30, 30, 90, 150, 210].map((deg, i) => {
  const a = (deg * Math.PI) / 180;
  return { x: 16 + R * Math.cos(a), y: 16 + R * Math.sin(a), yellow: i % 2 === 1 };
});

export function Mark({ className, size = 28 }: { className?: string; size?: number }) {
  return (
    <svg
      className={className}
      viewBox="0 0 32 32"
      width={size}
      height={size}
      aria-hidden="true"
    >
      <circle
        cx="16"
        cy="16"
        r={R}
        fill="none"
        stroke="var(--color-python-blue)"
        strokeOpacity="0.4"
        strokeWidth="1.2"
      />
      <g stroke="var(--color-python-blue)" strokeWidth="2" strokeLinecap="round">
        {SATELLITES.map((s, i) => (
          <line key={i} x1="16" y1="16" x2={s.x.toFixed(2)} y2={s.y.toFixed(2)} />
        ))}
      </g>
      {SATELLITES.map((s, i) => (
        <circle
          key={i}
          cx={s.x.toFixed(2)}
          cy={s.y.toFixed(2)}
          r="2.7"
          fill={s.yellow ? "var(--color-python-amber)" : "var(--color-python-blue)"}
          stroke="var(--background)"
          strokeWidth="0.9"
        />
      ))}
      <circle cx="16" cy="16" r="5.2" fill="var(--color-python-blue)" stroke="var(--background)" strokeWidth="1" />
      <circle cx="16" cy="16" r="2.1" fill="var(--color-python-amber)" />
    </svg>
  );
}

/**
 * Mark plus name. "Python" is set in the brand blue and "Central Hub" in the
 * text colour, so the name carries the same two-part rhythm as the mark.
 */
export function Wordmark() {
  const [first, ...rest] = SITE_NAME.split(" ");
  return (
    <>
      <Mark className="brand__mark" />
      <span className="brand__name">
        <span className="brand__name-lead">{first}</span>
        {rest.length ? ` ${rest.join(" ")}` : null}
      </span>
    </>
  );
}
