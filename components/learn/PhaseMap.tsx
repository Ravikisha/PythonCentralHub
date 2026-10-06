import { phases, problemsForPatterns } from "@/src/data/dsa";

/**
 * PhaseMap — the shape of the DSA course at a glance.
 *
 * Separates the phases that form a teaching sequence from the reference
 * surfaces, because reading the latter in order is a waste of time and the
 * grid alone does not say so.
 *
 * Server component.
 */
export function PhaseMap() {
  const rows = phases.map((p) => ({
    ...p,
    problems:
      p.patterns.length > 0 ? problemsForPatterns(p.patterns).length : 0,
  }));

  const sequence = rows.filter((r) => r.inSyllabus);
  const reference = rows.filter((r) => !r.inSyllabus);

  const totalPages = rows.reduce((a, r) => a + r.pages, 0);
  const seqProblems = new Set(
    sequence.flatMap((r) => problemsForPatterns(r.patterns).map((p) => p.slug)),
  ).size;

  return (
    <div className="pch-pm">
      <p className="pch-pm__summary">
        <strong>{totalPages} pages</strong> across {rows.length} phases. The{" "}
        {sequence.length}-phase teaching sequence reaches{" "}
        <strong>{seqProblems} distinct problems</strong>; the rest are reference
        surfaces you dip into rather than work through.
      </p>

      <h4 className="pch-pm__head">The teaching sequence</h4>
      <p className="pch-pm__note">
        In order — later phases assume earlier ones. Phases 01 and 02 carry no
        problem ladders because they teach language and analysis rather than
        patterns.
      </p>
      <div className="pch-pm__grid">
        {sequence.map((r) => (
          <a
            className="pch-pm__card"
            href={r.firstPage?.url ?? "#"}
            key={r.number}
          >
            <span className="pch-pm__num">{r.number}</span>
            <span className="pch-pm__label">{r.label}</span>
            <span className="pch-pm__stats">
              {r.pages} {r.pages === 1 ? "page" : "pages"}
              {r.problems > 0 ? <> · {r.problems} problems</> : null}
            </span>
          </a>
        ))}
      </div>

      <h4 className="pch-pm__head">Reference and practice</h4>
      <p className="pch-pm__note">
        Not a sequence. Use these throughout — the cheatsheets the night before,
        the problem sets for mixed recognition practice, the company guides when
        a specific loop is imminent.
      </p>
      <div className="pch-pm__grid">
        {reference.map((r) => (
          <a
            className="pch-pm__card pch-pm__card--ref"
            href={r.firstPage?.url ?? "#"}
            key={r.number}
          >
            <span className="pch-pm__num">{r.number}</span>
            <span className="pch-pm__label">{r.label}</span>
            <span className="pch-pm__stats">
              {r.pages} {r.pages === 1 ? "page" : "pages"}
            </span>
          </a>
        ))}
      </div>
    </div>
  );
}

export default PhaseMap;
