import { getSheet, problemsForSheet, problemUrl } from "@/src/data/dsa";
import ProblemTable, { type Row } from "@/src/components/dsa/ProblemTable";

/**
 * SheetTracker — one of the public study sheets, section by section.
 *
 * Server component. It also tells the reader how faithful the mapping is,
 * because some sheets publish steps rather than a LeetCode list and the
 * equivalents shown are close rather than identical.
 */
export interface SheetTrackerProps {
  /** Sheet key, as defined in src/data/dsa/sheets.yaml. */
  sheet: string;
  collapsed?: boolean;
}

export function SheetTracker({
  sheet: key,
  collapsed = true,
}: SheetTrackerProps) {
  const sheet = getSheet(key);

  if (!sheet) {
    return (
      <aside className="pch-pl__missing">
        <strong>Unknown sheet</strong> <code>{key}</code>. Known keys are
        defined in <code>src/data/dsa/sheets.yaml</code>.
      </aside>
    );
  }

  const groups = problemsForSheet(key)
    .map((s) => ({
      title: `${s.section} · ${s.problems.length}`,
      rows: s.problems.map((p): Row => ({
        lc: p.lc,
        slug: p.slug,
        title: p.title,
        difficulty: p.difficulty,
        premium: p.premium,
        url: problemUrl(p),
        // Sheet badges are noise inside a sheet's own page; company chips are not.
        companies: p.companies,
        freq: p.freq,
      })),
    }))
    .filter((g) => g.rows.length > 0);

  const resolved = groups.reduce((n, g) => n + g.rows.length, 0);
  const isStepMapped = sheet.by === "step";

  return (
    <div className="pch-sheet">
      <header className="pch-sheet__head">
        <div>
          <h3 className="pch-sheet__name">{sheet.name}</h3>
          <p className="pch-sheet__by">
            by {sheet.author} ·{" "}
            <a href={sheet.url} target="_blank" rel="noopener noreferrer">
              original sheet
            </a>
          </p>
        </div>
        <span className="pch-sheet__count">{sheet.count} problems</span>
      </header>

      <p className="pch-sheet__blurb">{sheet.blurb}</p>

      {isStepMapped ? (
        <aside className="pch-sheet__note">
          <strong>How this one is mapped.</strong> {sheet.name} publishes{" "}
          <em>steps</em> rather than a LeetCode-only problem list, and a good
          number of its problems live on GeeksforGeeks or Coding Ninjas rather
          than LeetCode. So each step below is matched to the pages on this site
          that teach it, and the problems shown are this site&apos;s LeetCode
          equivalents for that step — close to the original, not identical to
          it. Follow the link above for the canonical list.
        </aside>
      ) : resolved < sheet.count ? (
        <aside className="pch-sheet__note">
          <strong>
            {resolved} of {sheet.count} resolved.
          </strong>{" "}
          The remaining {sheet.count - resolved} could not be matched to a row
          in the problem database — usually a renamed problem. Worth reporting.
        </aside>
      ) : null}

      <ProblemTable groups={groups} collapsible={collapsed} />
    </div>
  );
}

export default SheetTracker;
