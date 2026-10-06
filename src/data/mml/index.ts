/**
 * src/data/mml/index.ts — the read path into the Mathematics for Machine
 * Learning flashcard deck.
 *
 * The deck is generated from the pages themselves (scripts/gen-mml-recall.mjs),
 * so a prompt cannot drift from the page it came from. Vite inlines the YAML at
 * build time via `?raw`; there is no runtime fetch and no client-side copy of
 * the whole deck — `MathDrillDeck.astro` resolves its filter here and hands the
 * island only the prompts it will show.
 *
 * The shape mirrors `src/data/dsa/index.ts` closely enough that the DSA
 * `DrillDeck` island renders this deck unchanged. The one deliberate difference
 * is naming: a card's group is a **chapter** here, not a phase. `DeckItem`
 * therefore carries `chapter` for this module's own use *and* `phase` as an
 * alias, because the island filters on `phase`. Renaming the island's prop
 * would touch the DSA deck for no gain.
 */
import yaml from "js-yaml";
import { readFileSync } from "node:fs";
import { join } from "node:path";

/**
 * Read from disk rather than importing.
 *
 * Vite's `?raw` suffix inlined this for Astro; Turbopack has no equivalent and
 * fails with "Unknown module type". Evaluated once on the server, at build
 * time for the statically generated pages that use it.
 */
const recallRaw = readFileSync(join(process.cwd(), "src", "data", "mml", "recall.yaml"), "utf8");

/** One prompt: `label` is the face shown, `text` is what the reader recalls. */
export interface RecallPrompt {
  /**
   * `aspect` — the label is a short cue, the text is the content.
   * `cloze`  — the label is the sentence with the claim blanked out.
   * `fact`   — the label is the page title; there was no cue to extract.
   */
  kind: "aspect" | "cloze" | "fact";
  label: string;
  text: string;
}

export interface RecallCard {
  /** Slug of the page the card came from. */
  id: string;
  /** The page's frontmatter title. */
  title: string;
  /** Chapter directory name, e.g. `Chapter 07 - Continuous Optimization`. */
  chapter: string;
  /** Absolute site URL of the source page, trailing slash included. */
  url: string;
  prompts: RecallPrompt[];
}

/**
 * Every Recall card in the module.
 *
 * `cards:` with no entries parses to `null`, not `[]` — which is the state the
 * file is in until the first chapter is rewritten — so the fallback is load
 * bearing rather than defensive noise.
 */
export const recallCards: readonly RecallCard[] = Object.freeze(
  ((yaml.load(recallRaw) as { cards?: RecallCard[] } | null)?.cards ?? []).map((c) =>
    Object.freeze(c),
  ),
);

export interface DeckItem extends RecallPrompt {
  /** Stable identity for scheduling: `<page slug>#<prompt index>`. */
  key: string;
  cardId: string;
  cardTitle: string;
  /** Chapter directory name. */
  chapter: string;
  /** Same value as `chapter`. The DrillDeck island filters on this name. */
  phase: string;
  url: string;
}

/** Flatten the deck to prompts, optionally scoped to a set of chapters. */
export function buildDeck(opts: { chapters?: string[] } = {}): DeckItem[] {
  const want = opts.chapters?.length ? new Set(opts.chapters) : null;
  const items: DeckItem[] = [];
  for (const c of recallCards) {
    if (want && !want.has(c.chapter)) continue;
    c.prompts.forEach((p, i) => {
      items.push({
        ...p,
        key: `${c.id}#${i}`,
        cardId: c.id,
        cardTitle: c.title,
        chapter: c.chapter,
        phase: c.chapter,
        url: c.url,
      });
    });
  }
  return items;
}

/**
 * Every chapter contributing at least one card, in reading order.
 *
 * Plain lexicographic sort is correct because the directories are named
 * `Chapter NN - Title` with a zero-padded number, so string order and chapter
 * order agree. That is why the padding is a convention and not cosmetic.
 */
export const recallChapters: readonly string[] = Object.freeze(
  [...new Set(recallCards.map((c) => c.chapter))].sort(),
);

/** Human label for a chapter directory: `Chapter 07 - Convex...` -> `07 · Convex...`. */
export function chapterLabel(dir: string): string {
  return dir.replace(/^Chapter\s+(\d+)\s+-\s+/, "$1 · ");
}
