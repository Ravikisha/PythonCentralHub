import Mock from "@/src/components/dsa/MockInterview";
import { problems, problemsForPatterns } from "@/src/data/dsa";

/**
 * MockInterview — a timed, randomised problem set.
 *
 * Server component that builds the pool and hands it to the existing React
 * component, which owns the timer and was already a client island.
 */
export interface MockInterviewProps {
  minutes?: number;
  patterns?: string[];
}

export function MockInterview({ minutes = 45, patterns }: MockInterviewProps) {
  const source = patterns?.length ? problemsForPatterns(patterns) : problems;

  // Premium problems cannot be opened by everyone, so they are no use in a
  // timed run the reader is meant to actually attempt.
  const pool = source
    .filter((p) => !p.premium && p.slug)
    .map((p) => ({
      lc: p.lc ?? null,
      slug: p.slug,
      title: p.title,
      difficulty: p.difficulty,
      patterns: p.patterns ?? [],
    }));

  if (pool.length === 0) {
    return (
      <p>
        <em>No problems matched that filter.</em>
      </p>
    );
  }

  return <Mock problems={pool} minutes={minutes} />;
}

export default MockInterview;
