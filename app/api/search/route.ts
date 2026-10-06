import { readFile } from "node:fs/promises";
import { join } from "node:path";
import { allow, clientIp } from "@/lib/server/rate-limit";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

/**
 * GET /api/search/?q=words&course=slug
 *
 * Full-text search over lesson text, for the "In lesson text" part of the ⌘K
 * dialog. The browser's own index covers titles and headings; this finds the
 * page that explains something in the middle of a lesson.
 *
 * The text is .search/fulltext.json (scripts/gen-search-index.mjs), loaded
 * once per function instance and scanned per query. At ~1,200 lessons and
 * ~12 MB that is a few milliseconds, and simpler than an index to keep in
 * step with the content.
 */
interface Doc {
  u: string;
  t: string;
  m: string;
  x: string;
  /** Lower-cased `x`, computed once on load. */
  lx?: string;
}

let docs: Promise<Doc[]> | undefined;

function load(): Promise<Doc[]> {
  docs ??= readFile(join(process.cwd(), ".search", "fulltext.json"), "utf8")
    .then((raw) => {
      const list = JSON.parse(raw) as Doc[];
      for (const d of list) d.lx = d.x.toLowerCase();
      return list;
    })
    .catch((err) => {
      docs = undefined; // retry on the next request
      throw err;
    });
  return docs;
}

function count(hay: string, needle: string): number {
  let n = 0;
  for (let i = hay.indexOf(needle); i !== -1 && n < 50; i = hay.indexOf(needle, i + needle.length)) n++;
  return n;
}

/** ~160 characters around the first place the phrase, or else a word, occurs. */
function snippet(doc: Doc, phrase: string, words: string[]): string {
  const lx = doc.lx!;
  let at = lx.indexOf(phrase);
  if (at === -1) at = Math.max(0, ...words.map((w) => lx.indexOf(w)).filter((i) => i >= 0).slice(0, 1));
  const start = Math.max(0, at - 60);
  const end = Math.min(doc.x.length, at + 100);
  return `${start > 0 ? "…" : ""}${doc.x.slice(start, end).trim()}${end < doc.x.length ? "…" : ""}`;
}

export async function GET(req: Request): Promise<Response> {
  const params = new URL(req.url).searchParams;
  const phrase = (params.get("q") ?? "").trim().toLowerCase().slice(0, 100);
  const course = params.get("course") ?? "";
  const words = phrase.split(/\s+/).filter((w) => w.length >= 2).slice(0, 8);
  if (phrase.length < 3 || !words.length) return Response.json({ results: [] });

  // Each query scans every lesson. Repeat queries are served from the CDN
  // (see Cache-Control below); this bounds unique ones per client.
  if (!(await allow(`search:${clientIp(req)}`, 60, 60_000))) {
    return Response.json(
      { results: [], error: "Too many searches. Wait a moment." },
      { status: 429, headers: { "Retry-After": "60" } },
    );
  }

  let all: Doc[];
  try {
    all = await load();
  } catch {
    return Response.json({ results: [], error: "Search index is not available." }, { status: 503 });
  }

  const scored: { doc: Doc; score: number }[] = [];
  for (const doc of all) {
    if (course && !doc.u.startsWith(`/${course}/`)) continue;
    const lx = doc.lx!;
    let score = 0;
    let ok = true;
    for (const w of words) {
      const n = count(lx, w);
      if (!n) {
        ok = false;
        break;
      }
      score += Math.log2(1 + n);
    }
    if (!ok) continue;
    if (words.length > 1 && lx.includes(phrase)) score += 6;
    if (doc.t.toLowerCase().includes(phrase)) score += 4;
    scored.push({ doc, score });
  }

  scored.sort((a, b) => b.score - a.score);
  const results = scored.slice(0, 10).map(({ doc }) => ({
    u: doc.u,
    t: doc.t,
    m: doc.m,
    s: snippet(doc, phrase, words),
  }));

  return Response.json(
    { results },
    // Same answer for everyone until the next deploy.
    { headers: { "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=86400" } },
  );
}
