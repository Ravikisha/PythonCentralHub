import {
  problemsForPatterns,
  problemUrl,
  getSheet,
  type Difficulty,
} from "@/src/data/dsa";
import ProblemTable, { type Row } from "@/src/components/dsa/ProblemTable";

/**
 * ProblemLadder — the generated Practice section for a topic page.
 *
 * Replaces the hand-written LeetCode tables that used to live in each page.
 * Those were the site's biggest source of drift: 502 links across 89 files,
 * each with its own copy of a title and difficulty, none aware of sheet
 * membership. This reads src/data/dsa instead, so a problem's metadata is
 * stated once.
 *
 * Server component. It selects and shapes the rows here and hands them to
 * `ProblemTable`, which was already React and is already a client component --
 * so the port is a change of wrapper, not of behaviour.
 */
export interface ProblemLadderProps {
  /** Pattern slug, or several. Matched against each problem's `patterns`. */
  pattern: string | string[];
  /** Drop anything harder than this. Useful on early-phase pages. */
  max?: Difficulty;
  /** Group by difficulty instead of presenting one flat ladder. */
  grouped?: boolean;
  /** LeetCode number -> a one-line "the twist" note for this page's context. */
  notes?: Record<number, string>;
  caption?: string;
}

const RANK: Record<Difficulty, number> = { easy: 0, medium: 1, hard: 2 };

const DEFAULT_CAPTION =
  "Work down the ladder. Tick each problem off as you go — progress is saved " +
  "in this browser, and the Export button in the filter bar writes it to a " +
  "file you can keep.";

export function ProblemLadder({
  pattern,
  max,
  grouped = false,
  notes = {},
  caption,
}: ProblemLadderProps) {
  const found = problemsForPatterns(pattern).filter(
    (p) => max === undefined || RANK[p.difficulty as Difficulty] <= RANK[max],
  );

  /** Sheet display names, so a badge reads "NeetCode 150" and not "neetcode150". */
  const sheetName = (key: string): string => getSheet(key)?.name ?? key;

  const toRow = (p: (typeof found)[number]): Row => ({
    lc: p.lc,
    slug: p.slug,
    title: p.title,
    difficulty: p.difficulty,
    premium: p.premium,
    url: problemUrl(p),
    sheets: Object.keys(p.sheets ?? {}).map(sheetName),
    companies: p.companies,
    freq: p.freq,
    note: p.lc !== null ? notes[p.lc] : undefined,
  });

  const patternList = Array.isArray(pattern) ? pattern : [pattern];

  if (found.length === 0) {
    // Author-facing, deliberately: an empty ladder means a slug typo or an
    // untagged problem, and saying so beats rendering nothing.
    return (
      <aside className="pch-pl__missing">
        <strong>No problems tagged</strong> for{" "}
        <code>{patternList.join(", ")}</code>. Add the pattern to problems in{" "}
        <code>src/data/dsa/problems.yaml</code>, or fix the slug in this
        page&apos;s frontmatter.
      </aside>
    );
  }

  const groups = grouped
    ? (["easy", "medium", "hard"] as Difficulty[])
        .map((d) => ({
          title: d[0].toUpperCase() + d.slice(1),
          rows: found.filter((p) => p.difficulty === d).map(toRow),
        }))
        .filter((g) => g.rows.length > 0)
    : [{ rows: found.map(toRow) }];

  return (
    <ProblemTable
      groups={groups}
      caption={caption ?? DEFAULT_CAPTION}
      filters={found.length > 6}
    />
  );
}

export default ProblemLadder;
