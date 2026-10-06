import Deck from "@/src/components/dsa/DrillDeck";
import { buildDeck, recallPhases } from "@/src/data/dsa";

/**
 * DrillDeck — spaced-recall prompts built from the pages themselves.
 *
 * Server component that selects the cards and hands them to the existing
 * React deck, which was already a client island.
 */
export interface DrillDeckProps {
  phases?: string[];
  patterns?: string[];
}

export function DrillDeck({ phases, patterns }: DrillDeckProps) {
  const items = buildDeck({ phases, patterns }).map((i) => ({
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
          No recall prompts matched. Re-run <code>npm run dsa:recall</code>{" "}
          after editing a page.
        </em>
      </p>
    );
  }

  // Only offer a phase in the filter if the current selection actually has
  // cards from it — otherwise the reader picks a phase and gets an empty deck.
  const present = [...new Set(items.map((i) => i.phase))].sort();
  const options = phases?.length
    ? present
    : recallPhases.filter((p) => present.includes(p));

  return <Deck items={items} phases={options} />;
}

export default DrillDeck;
