"use client";

import { cn } from "@/lib/utils";

/**
 * MagicUI-style shiny text. A soft highlight sweeps across the text — used
 * on the hero eyebrow so the `>>>` import line reads as a live prompt.
 * Keyframe pch-shiny + reduced-motion handling live in landing.css.
 */
export default function AnimatedShinyText({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <span className={cn("pch-shiny", className)} aria-hidden="false">
      {children}
    </span>
  );
}
