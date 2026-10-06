import { buildStudyPlan, getCompany, syllabus } from "@/src/data/dsa";

/**
 * StudyPlanner — a week-by-week schedule for the time the reader actually has.
 *
 * The component is as much about what it cannot fit as what it can: a short
 * plan is a slice of the syllabus chosen in teaching order, and everything it
 * drops is listed rather than quietly omitted.
 *
 * Server component.
 */
export interface StudyPlannerProps {
  weeks?: number;
  hoursPerWeek?: number;
  /** Narrow the syllabus to one company's pattern families. */
  company?: string;
  problemsPerHour?: number;
}

export function StudyPlanner({
  weeks = 8,
  hoursPerWeek = 10,
  company,
  problemsPerHour = 1,
}: StudyPlannerProps) {
  const co = company ? getCompany(company) : undefined;

  if (company && !co) {
    return (
      <aside className="pch-pl__missing">
        <strong>Unknown company</strong> <code>{company}</code>. Profiles live
        in <code>src/data/dsa/companies.yaml</code>.
      </aside>
    );
  }

  const plan = buildStudyPlan({
    weeks,
    hoursPerWeek,
    company,
    problemsPerHour,
  });

  // What the whole syllabus would cost at this pace, so the caveat can be
  // specific rather than vague about the gap.
  const fullPlan = buildStudyPlan({
    weeks: 52 * 3,
    hoursPerWeek,
    problemsPerHour,
  });
  const fullWeeks = fullPlan.weeks.length;

  const scheduledPages = plan.weeks.reduce((a, w) => a + w.pages.length, 0);
  const consideredPages = scheduledPages + plan.deferred.length;
  const pct =
    consideredPages > 0
      ? Math.round((scheduledPages / consideredPages) * 100)
      : 0;

  return (
    <div className="pch-sp">
      <p className="pch-sp__summary">
        <strong>{plan.weeks.length} weeks</strong> at{" "}
        {plan.options.hoursPerWeek} h/week
        {" — "}a budget of about <strong>{plan.problemBudget} problems</strong>{" "}
        per week.
        {co ? (
          <>
            {" "}
            Filtered to <strong>{co.name}</strong>&apos;s pattern families.
          </>
        ) : null}{" "}
        This schedules{" "}
        <strong>
          {scheduledPages} of {consideredPages}
        </strong>{" "}
        pattern pages ({pct}%) and <strong>{plan.totalProblems}</strong>{" "}
        problems.
      </p>

      <aside className="pch-sp__caveat">
        <strong>What this plan leaves out.</strong> The full syllabus is{" "}
        {syllabus.length} pattern pages, which at {plan.options.hoursPerWeek}{" "}
        h/week would take about <strong>{fullWeeks} weeks</strong>. A short plan
        is a <em>slice</em>, chosen in teaching order so the prerequisites hold
        — not a complete course. Everything it cannot fit is listed at the
        bottom rather than quietly dropped. The per-week counts are{" "}
        <strong>new</strong> problems: each problem is assigned to the first
        page that claims its pattern, so a later page can show 0 new ones and
        still need studying.
      </aside>

      <table className="pch-sp__table">
        <thead>
          <tr>
            <th>Week</th>
            <th>Focus</th>
            <th>New problems</th>
            <th>Mix</th>
          </tr>
        </thead>
        <tbody>
          {plan.weeks.map((w) => (
            <tr key={w.week}>
              <td className="pch-sp__wk">{w.week}</td>
              <td>
                <ul className="pch-sp__pages">
                  {w.pages.map((p) => (
                    <li key={p.url}>
                      <a href={p.url}>{p.title}</a>{" "}
                      <span className="pch-sp__phase">{p.phaseLabel}</span>
                    </li>
                  ))}
                </ul>
              </td>
              <td className="pch-sp__num">{w.problems.length}</td>
              <td className="pch-sp__mix">
                <span className="pch-sp__easy">{w.breakdown.easy}e</span>{" "}
                <span className="pch-sp__med">{w.breakdown.medium}m</span>{" "}
                <span className="pch-sp__hard">{w.breakdown.hard}h</span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {plan.deferred.length > 0 ? (
        <details className="pch-sp__deferred">
          <summary>
            Not scheduled: {plan.deferred.length} pattern{" "}
            {plan.deferred.length === 1 ? "page" : "pages"} beyond week{" "}
            {plan.weeks.length}
          </summary>
          <p>
            These come next, in the same teaching order. Raise the weeks or the
            hours to pull them in — or leave them, and know exactly what you
            have not covered.
          </p>
          <ul className="pch-sp__deflist">
            {plan.deferred.map((p) => (
              <li key={p.url}>
                <a href={p.url}>{p.title}</a>{" "}
                <span className="pch-sp__phase">{p.phaseLabel}</span>
              </li>
            ))}
          </ul>
        </details>
      ) : (
        <p className="pch-sp__complete">
          Everything in scope fits inside {plan.weeks.length} weeks — nothing
          deferred.
        </p>
      )}
    </div>
  );
}

export default StudyPlanner;
