import { cn } from "@/lib/utils";

/**
 * MagicUI-style marquee. Duplicates its children and scrolls them in an
 * infinite loop; pauses on hover. Keyframe pch-marquee + reduced-motion
 * (renders a static, wrapping row) live in landing.css.
 */
export default function Marquee({
  children,
  reverse = false,
  pauseOnHover = true,
  duration = 40,
  className,
}: {
  children: React.ReactNode;
  reverse?: boolean;
  pauseOnHover?: boolean;
  duration?: number;
  className?: string;
}) {
  return (
    <div
      className={cn("pch-marquee", pauseOnHover && "pch-marquee--hoverable", className)}
      style={{ "--marquee-duration": `${duration}s` } as React.CSSProperties}
    >
      {[0, 1].map((dup) => (
        <div
          key={dup}
          className={cn("pch-marquee__track", reverse && "pch-marquee__track--reverse")}
          aria-hidden={dup === 1 ? "true" : undefined}
        >
          {children}
        </div>
      ))}
    </div>
  );
}
