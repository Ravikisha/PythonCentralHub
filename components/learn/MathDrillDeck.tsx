import Deck from "@/src/components/dsa/DrillDeck";
import { buildDeck, recallChapters, chapterLabel } from "@/src/data/mml";

/**
 * MathDrillDeck — the DSA recall deck, pointed at the maths chapters.
 *
 * Reuses the same client deck component with different grouping nouns, so the
 * two modules cannot drift apart in behaviour.
 *
 * Server component.
 */
export interface MathDrillDeckProps {
  chapters?: string[];
}

export function MathDrillDeck({ chapters }: MathDrillDeckProps) {
  const items = buildDeck({ chapters }).map((i) => ({
    key: i.key,
    kind: i.kind,
    label: i.label,
    text: i.text,
    cardId: i.cardId,
    cardTitle: i.cardTitle,
    phase: i.phase,
    url: i.url,
  }));

  if (items.length === 0) {
    return (
      <p>
        <em>
          No recall prompts matched. Re-run <code>npm run mml:recall</code>{" "}
          after adding a <code>## Recall card</code> section to a page.
        </em>
      </p>
    );
  }

  // Only offer a chapter in the filter if the current selection actually has
  // cards from it — otherwise the reader picks a chapter and gets an empty deck.
  const present = [...new Set(items.map((i) => i.phase))].sort();
  const options = chapters?.length
    ? present
    : recallChapters.filter((c) => present.includes(c));

  const groupLabels = Object.fromEntries(
    options.map((c) => [c, chapterLabel(c)]),
  );

  return (
    <Deck
      items={items}
      phases={options}
      groupNoun="chapter"
      groupLabels={groupLabels}
    />
  );
}

export default MathDrillDeck;
