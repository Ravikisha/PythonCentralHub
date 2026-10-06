import Link from "next/link";

export interface PagerPage {
  url: string;
  title: string;
  /** The module or phase the page sits in, shown as the smaller line. */
  where?: string;
}

/**
 * Previous and next, in course order.
 *
 * Named "Previous"/"Next" with the page's own title underneath, because on a
 * course the useful question is what comes next, not which direction the arrow
 * points. The arrows are separate icons rather than glyphs appended to the
 * words, so a screen reader reads a title and not "Next arrow".
 */
export function Pager({
  previous,
  next,
}: {
  previous?: PagerPage;
  next?: PagerPage;
}) {
  if (!previous && !next) return null;

  return (
    <nav className="pager" aria-label="Course navigation">
      {previous ? (
        <Link className="pager__link" href={previous.url}>
          <Arrow direction="left" />
          <span>
            <span className="pager__meta">Previous</span>
            <span className="pager__title">{previous.title}</span>
          </span>
        </Link>
      ) : (
        <span />
      )}

      {next ? (
        <Link className="pager__link pager__link--next" href={next.url}>
          <Arrow direction="right" />
          <span>
            <span className="pager__meta">Next</span>
            <span className="pager__title">{next.title}</span>
          </span>
        </Link>
      ) : null}
    </nav>
  );
}

function Arrow({ direction }: { direction: "left" | "right" }) {
  return (
    <svg
      className="pager__arrow"
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
    >
      <path
        d={direction === "left" ? "M15 5l-7 7 7 7" : "M9 5l7 7-7 7"}
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export default Pager;
