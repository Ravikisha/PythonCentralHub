"use client";

/**
 * ProblemTable — the one interactive table behind every practice list on the site.
 *
 * `<ProblemLadder>`, `<SheetTracker>` and `<CompanyBoard>` are thin Astro
 * wrappers that query the problem database at build time and hand the resulting
 * rows here. Only the rows a page actually needs cross into the client bundle —
 * the 422-row database itself never does.
 *
 * What it adds over a static markdown table:
 *   * a status control per problem, persisted in localStorage (see useProgress)
 *   * a progress bar with easy/medium/hard breakdown
 *   * filters: difficulty, undone-only, and sheet membership
 *   * sheet badges and company chips generated from the database, so a problem's
 *     metadata can never drift out of sync between pages
 */
import { useMemo, useState } from "react";
import { useProgress, type Status } from "./useProgress";

/** The subset of a Problem that is worth shipping to the client. */
export interface Row {
  lc: number | null;
  slug: string;
  title: string;
  difficulty: "easy" | "medium" | "hard";
  premium?: boolean;
  url: string;
  /** Sheet display names this problem belongs to. */
  sheets?: string[];
  companies?: string[];
  freq?: number;
  /** One-line "the twist" note, when the page has something specific to say. */
  note?: string;
}

export interface Group {
  /** Section heading, e.g. a sheet category or a phase name. Empty for flat lists. */
  title?: string;
  rows: Row[];
}

export interface ProblemTableProps {
  groups: Group[];
  /** Shown above the table. */
  caption?: string;
  /** Start with sections collapsed — sensible for a 150-problem sheet. */
  collapsible?: boolean;
  /** Hide the filter bar for short ladders where it is just noise. */
  filters?: boolean;
}

const STATUS_LABEL: Record<Status, string> = {
  todo: "To do",
  attempted: "Attempted",
  solved: "Solved",
  review: "Redo",
};

const STATUS_GLYPH: Record<Status, string> = {
  todo: "○",
  attempted: "◐",
  solved: "●",
  review: "⟲",
};

type DiffFilter = "all" | "easy" | "medium" | "hard";

export default function ProblemTable({
  groups,
  caption,
  collapsible = false,
  filters = true,
}: ProblemTableProps) {
  const { ready, statusOf, cycleStatus, solvedCount, exportJson, importJson, reset } = useProgress();
  const [diff, setDiff] = useState<DiffFilter>("all");
  const [undoneOnly, setUndoneOnly] = useState(false);
  const [open, setOpen] = useState<Record<string, boolean>>({});
  const [ioMessage, setIoMessage] = useState<string | null>(null);

  const allSlugs = useMemo(() => groups.flatMap((g) => g.rows.map((r) => r.slug)), [groups]);
  const total = allSlugs.length;
  const solved = solvedCount(allSlugs);

  const counts = useMemo(() => {
    const c = { easy: 0, medium: 0, hard: 0 };
    for (const g of groups) for (const r of g.rows) c[r.difficulty] += 1;
    return c;
  }, [groups]);

  const visible = useMemo(
    () =>
      groups
        .map((g) => ({
          ...g,
          rows: g.rows.filter(
            (r) =>
              (diff === "all" || r.difficulty === diff) &&
              (!undoneOnly || statusOf(r.slug) !== "solved"),
          ),
        }))
        .filter((g) => g.rows.length > 0),
    [groups, diff, undoneOnly, statusOf],
  );

  const onExport = () => {
    const blob = new Blob([exportJson()], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "pch-dsa-progress.json";
    a.click();
    URL.revokeObjectURL(a.href);
    setIoMessage("Downloaded pch-dsa-progress.json — keep it somewhere safe.");
  };

  const onImport = async (file: File | undefined) => {
    if (!file) return;
    const result = importJson(await file.text());
    setIoMessage(result.message);
  };

  const onReset = () => {
    // Destructive and unrecoverable, so it is gated behind an explicit confirm.
    if (!window.confirm("Clear all saved DSA progress on this device? This cannot be undone.")) return;
    reset();
    setIoMessage("Progress cleared.");
  };

  return (
    <div className="pch-pl">
      <div className="pch-pl__head">
        <div className="pch-pl__meter" role="group" aria-label="Progress">
          <div className="pch-pl__bar">
            <span
              className="pch-pl__fill"
              style={{ width: total ? `${(solved / total) * 100}%` : "0%" }}
            />
          </div>
          <span className="pch-pl__count">
            {ready ? (
              <>
                <b>{solved}</b> / {total} solved
              </>
            ) : (
              <>{total} problems</>
            )}
          </span>
        </div>
        <span className="pch-pl__mix">
          <i className="tone-easy">{counts.easy} easy</i>
          <i className="tone-medium">{counts.medium} medium</i>
          <i className="tone-hard">{counts.hard} hard</i>
        </span>
      </div>

      {caption ? <p className="pch-pl__caption">{caption}</p> : null}

      {filters ? (
        <div className="pch-pl__filters">
          <div className="pch-pl__seg" role="group" aria-label="Filter by difficulty">
            {(["all", "easy", "medium", "hard"] as DiffFilter[]).map((d) => (
              <button
                key={d}
                type="button"
                className={`pch-pl__segbtn${diff === d ? " is-on" : ""}`}
                onClick={() => setDiff(d)}
                aria-pressed={diff === d}
              >
                {d === "all" ? "All" : d[0].toUpperCase() + d.slice(1)}
              </button>
            ))}
          </div>
          <label className="pch-pl__check">
            <input
              type="checkbox"
              checked={undoneOnly}
              onChange={(e) => setUndoneOnly(e.target.checked)}
              disabled={!ready}
            />
            Unsolved only
          </label>
          <span className="pch-pl__io">
            <button type="button" className="pch-pl__linkbtn" onClick={onExport} disabled={!ready}>
              Export
            </button>
            <label className="pch-pl__linkbtn">
              Import
              <input
                type="file"
                accept="application/json"
                hidden
                onChange={(e) => onImport(e.target.files?.[0])}
              />
            </label>
            <button type="button" className="pch-pl__linkbtn is-danger" onClick={onReset} disabled={!ready}>
              Reset
            </button>
          </span>
        </div>
      ) : null}

      {ioMessage ? (
        <p className="pch-pl__io-msg" role="status">
          {ioMessage}
        </p>
      ) : null}

      {visible.length === 0 ? (
        <p className="pch-pl__empty">Nothing matches those filters.</p>
      ) : (
        visible.map((group, gi) => {
          const key = group.title ?? `g${gi}`;
          const isOpen = !collapsible || open[key] !== false;
          const groupSlugs = group.rows.map((r) => r.slug);
          const groupSolved = solvedCount(groupSlugs);
          return (
            <section key={key} className="pch-pl__group">
              {group.title ? (
                <h4 className="pch-pl__grouphead">
                  {collapsible ? (
                    <button
                      type="button"
                      className="pch-pl__toggle"
                      onClick={() => setOpen((o) => ({ ...o, [key]: !isOpen }))}
                      aria-expanded={isOpen}
                    >
                      <span className="pch-pl__chev" aria-hidden="true">
                        {isOpen ? "▾" : "▸"}
                      </span>
                      {group.title}
                    </button>
                  ) : (
                    group.title
                  )}
                  <span className="pch-pl__groupcount">
                    {ready ? `${groupSolved}/${group.rows.length}` : group.rows.length}
                  </span>
                </h4>
              ) : null}

              {isOpen ? (
                <ul className="pch-pl__list">
                  {group.rows.map((r) => {
                    const status = statusOf(r.slug);
                    return (
                      <li key={r.slug} className={`pch-pl__row is-${status}`}>
                        <button
                          type="button"
                          className={`pch-pl__status is-${status}`}
                          onClick={() => cycleStatus(r.slug)}
                          disabled={!ready}
                          title={`${STATUS_LABEL[status]} — click to change`}
                          aria-label={`${r.title}: ${STATUS_LABEL[status]}. Click to change.`}
                        >
                          <span aria-hidden="true">{STATUS_GLYPH[status]}</span>
                        </button>

                        <span className="pch-pl__lc">{r.lc ?? "—"}</span>

                        <a className="pch-pl__title" href={r.url} target="_blank" rel="noopener noreferrer">
                          {r.title}
                          {r.premium ? <em className="pch-pl__premium">premium</em> : null}
                        </a>

                        <span className={`pch-pl__diff tone-${r.difficulty}`}>{r.difficulty}</span>

                        {r.note ? <span className="pch-pl__note">{r.note}</span> : null}

                        <span className="pch-pl__tags">
                          {r.sheets?.map((s) => (
                            <em key={s} className="pch-pl__sheet" title={`In ${s}`}>
                              {s}
                            </em>
                          ))}
                          {r.companies?.map((c) => (
                            <em key={c} className="pch-pl__co" title={`Reported at ${c}`}>
                              {c}
                            </em>
                          ))}
                        </span>
                      </li>
                    );
                  })}
                </ul>
              ) : null}
            </section>
          );
        })
      )}
    </div>
  );
}
