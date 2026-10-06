"use client";

import { useMemo } from "react";
import { cn } from "@/lib/utils";

/**
 * MagicUI-style meteor shower. `number` streaks fall diagonally across the
 * hero on staggered delays. Decorative + aria-hidden. Keyframe pch-meteor
 * and reduced-motion handling live in landing.css.
 *
 * Delays/positions are derived deterministically from the index (no
 * Math.random) so SSR and client markup match — no hydration mismatch.
 */
export default function Meteors({
  number = 18,
  className,
}: {
  number?: number;
  className?: string;
}) {
  const meteors = useMemo(
    () =>
      Array.from({ length: number }, (_, i) => ({
        left: `${Math.round((i / number) * 100)}%`,
        delay: `${(i % 7) * 0.6 + (i % 3) * 0.2}s`,
        duration: `${4 + (i % 5)}s`,
      })),
    [number],
  );

  return (
    <div className={cn("pch-meteors", className)} aria-hidden="true">
      {meteors.map((m, i) => (
        <span
          key={i}
          className="pch-meteor"
          style={{ left: m.left, animationDelay: m.delay, animationDuration: m.duration }}
        />
      ))}
    </div>
  );
}
