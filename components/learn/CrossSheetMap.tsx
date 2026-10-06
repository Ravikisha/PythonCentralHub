import {
  crossSheetOverlap,
  getSheet,
  problemUrl,
  problems,
  sheets,
} from "@/src/data/dsa";
import ProblemTable, { type Row } from "@/src/components/dsa/ProblemTable";

/**
 * CrossSheetMap — how much the public study sheets actually overlap.
 *
 * The point of the component is the duplication figure: the sheets look like
 * separate curricula and are largely the same problems, so the ones they agree
 * on are the highest-value problems on the site.
 *
 * Server component.
 */
export interface CrossSheetMapProps {
  /** A problem must appear in at least this many sheets to count as consensus. */
  minSheets?: number;
}

export function CrossSheetMap({ minSheets = 3 }: CrossSheetMapProps) {
  const overlap = crossSheetOverlap(minSheets);
  const sheetName = (key: string): string => getSheet(key)?.name ?? key;

  // Only sheets with a section breakdown carry per-title membership.
  const titleSheets = sheets.filter((s) => s.sections);

  const pairs: { a: string; b: string; shared: number; aTotal: number }[] = [];
  for (let i = 0; i < titleSheets.length; i++) {
    for (let j = i + 1; j < titleSheets.length; j++) {
      const a = titleSheets[i];
      const b = titleSheets[j];
      const shared = problems.filter(
        (p) => p.sheets?.[a.key] && p.sheets?.[b.key],
      ).length;
      pairs.push({
        a: a.name,
        b: b.name,
        shared,
        aTotal: Math.min(a.count, b.count),
      });
    }
  }

  const rows: Row[] = overlap.map(({ problem, sheets: keys }) => ({
    lc: problem.lc,
    slug: problem.slug,
    title: problem.title,
    difficulty: problem.difficulty,
    premium: problem.premium,
    url: problemUrl(problem),
    sheets: keys.map(sheetName),
    companies: problem.companies,
    freq: problem.freq,
    note: `in ${keys.length} sheets`,
  }));

  const union = problems.filter((p) =>
    titleSheets.some((s) => p.sheets?.[s.key]),
  ).length;
  const sumOfCounts = titleSheets.reduce((n, s) => n + s.count, 0);

  return (
    <>
      <div className="pch-xsheet">
        <div className="pch-xsheet__stat">
          <b>{sumOfCounts}</b>
          <span>problems listed across {titleSheets.length} sheets</span>
        </div>
        <div className="pch-xsheet__stat">
          <b>{union}</b>
          <span>distinct problems once duplicates are removed</span>
        </div>
        <div className="pch-xsheet__stat">
          <b>{Math.round((1 - union / sumOfCounts) * 100)}%</b>
          <span>of the combined list is duplication</span>
        </div>
        <div className="pch-xsheet__stat">
          <b>{overlap.length}</b>
          <span>problems appear in {minSheets} or more sheets</span>
        </div>
      </div>

      <p>
        Read the last figure first. Those {overlap.length} problems are what the
        sheet authors independently agree on, which makes them the highest-value
        problems on this site — and the ones to do before anything else,
        whichever sheet you eventually commit to.
      </p>

      <h3>How much any two sheets share</h3>

      <table>
        <thead>
          <tr>
            <th>Sheet A</th>
            <th>Sheet B</th>
            <th>Shared</th>
            <th>Share of the smaller sheet</th>
          </tr>
        </thead>
        <tbody>
          {pairs
            .sort((x, y) => y.shared - x.shared)
            .map((p, i) => (
              <tr key={i}>
                <td>{p.a}</td>
                <td>{p.b}</td>
                <td>{p.shared}</td>
                <td>{Math.round((p.shared / p.aTotal) * 100)}%</td>
              </tr>
            ))}
        </tbody>
      </table>

      <h3>The consensus problems</h3>

      <ProblemTable
        groups={[{ rows }]}
        caption={`Every problem below appears in at least ${minSheets} of the sheets. Finish these and you have covered the core of all of them simultaneously.`}
      />
    </>
  );
}

export default CrossSheetMap;
