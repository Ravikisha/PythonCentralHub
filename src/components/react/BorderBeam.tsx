import { cn } from "@/lib/utils";

/**
 * MagicUI-style border beam. A light travels around the parent's border.
 * Drop inside a position:relative container (e.g. the REPL terminal).
 * Implemented with an offset-path rectangle so the beam hugs the corners;
 * keyframe pch-border-beam + reduced-motion handling live in landing.css.
 */
export default function BorderBeam({
  duration = 8,
  delay = 0,
  className,
}: {
  duration?: number;
  delay?: number;
  className?: string;
}) {
  return (
    <div
      className={cn("pch-border-beam", className)}
      aria-hidden="true"
      style={
        {
          "--beam-duration": `${duration}s`,
          "--beam-delay": `${delay}s`,
        } as React.CSSProperties
      }
    />
  );
}
