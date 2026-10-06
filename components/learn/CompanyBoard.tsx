import {
  getCompany,
  problemsForCompany,
  problemsForPatterns,
  problemUrl,
  getSheet,
} from "@/src/data/dsa";
import ProblemTable, { type Row } from "@/src/components/dsa/ProblemTable";

/**
 * CompanyBoard — an interview profile for one company.
 *
 * Server component. The honesty caveat below is part of the component, not
 * decoration: no company publishes its question bank, so every "asked at X"
 * list is aggregated candidate reports and is presented as an ordering hint
 * rather than a syllabus.
 */
export interface CompanyBoardProps {
  /** Company slug, as keyed in src/data/dsa/companies.yaml. */
  company: string;
}

export function CompanyBoard({ company: slug }: CompanyBoardProps) {
  const company = getCompany(slug);

  if (!company) {
    return (
      <aside className="pch-pl__missing">
        <strong>Unknown company</strong> <code>{slug}</code>. Profiles are
        defined in <code>src/data/dsa/companies.yaml</code>.
      </aside>
    );
  }

  const tagged = problemsForCompany(slug);
  const derived = problemsForPatterns(company.patterns);
  // Thin per-problem tagging is worse than honest pattern derivation, so fall
  // back once the tagged set is too small to be representative.
  const usingDerived = tagged.length < 12;
  const shown = usingDerived ? derived : tagged;

  const sheetName = (key: string): string => getSheet(key)?.name ?? key;

  const rows: Row[] = shown.map((p) => ({
    lc: p.lc,
    slug: p.slug,
    title: p.title,
    difficulty: p.difficulty,
    premium: p.premium,
    url: problemUrl(p),
    sheets: Object.keys(p.sheets ?? {}).map(sheetName),
    freq: p.freq,
  }));

  return (
    <div className="pch-co">
      <p className="pch-co__blurb">{company.blurb}</p>

      <h3>The loop</h3>
      <div className="pch-co__rounds">
        {company.rounds.map((r, i) => (
          <div className="pch-co__round" key={i}>
            <span className="pch-co__roundname">{r.name}</span>
            <span className="pch-co__roundmeta">
              {r.count}× · {r.minutes} min
            </span>
            <span className="pch-co__roundfocus">{r.focus}</span>
          </div>
        ))}
      </div>

      <h3>The bar</h3>
      <p className="pch-co__bar">{company.bar}</p>

      <h3>What they lean on</h3>
      <p className="pch-co__patternnote">
        This is the durable part. Which <em>pattern families</em> a company
        favours is far more stable than which individual problems it uses, so
        prepare in this order:
      </p>
      <ol className="pch-co__patterns">
        {company.patterns.map((p) => (
          <li key={p}>
            <code>{p}</code>
          </li>
        ))}
      </ol>

      <h3>Quirks worth knowing</h3>
      <ul className="pch-co__quirks">
        {company.quirks.map((q, i) => (
          <li key={i}>{q}</li>
        ))}
      </ul>

      <h3>Reported problems</h3>
      <aside className="pch-co__caveat">
        <strong>Read this before you trust the list.</strong> No company
        publishes its question bank. Every &ldquo;asked at {company.name}&rdquo;
        list in circulation — including this one — is aggregated from candidate
        reports, is months to years out of date, and over-represents whoever
        bothered to post. Use it to choose an <em>order</em> to practise in. Do
        not use it as a question bank, and do not assume a problem missing from
        it is safe to skip.
        {usingDerived ? (
          <>
            {" "}
            The list below is currently derived from {company.name}&apos;s
            pattern families rather than from per-problem tags, which is the
            more honest basis while the tag data is thin.
          </>
        ) : null}
      </aside>

      <ProblemTable groups={[{ rows }]} />
    </div>
  );
}

export default CompanyBoard;
