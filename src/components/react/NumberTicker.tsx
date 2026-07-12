import { useEffect, useRef } from "react";
import { useInView, useMotionValue, useSpring } from "framer-motion";

/**
 * MagicUI-style number ticker. Counts from 0 → value the first time it
 * scrolls into view, then parks. Respects prefers-reduced-motion by
 * rendering the final value immediately. Used for the hero stat strip
 * (130+ tutorials, 200+ projects, …) — the count-up reinforces "loading".
 */
export default function NumberTicker({
  value,
  suffix = "",
  className,
}: {
  value: number;
  suffix?: string;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);
  const motionValue = useMotionValue(0);
  const spring = useSpring(motionValue, { damping: 40, stiffness: 120 });
  const inView = useInView(ref, { once: true, margin: "0px 0px -40px 0px" });

  const reduce =
    typeof window !== "undefined" &&
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  useEffect(() => {
    if (inView) motionValue.set(value);
  }, [inView, value, motionValue]);

  useEffect(() => {
    if (reduce) {
      if (ref.current) ref.current.textContent = `${value}${suffix}`;
      return;
    }
    return spring.on("change", (latest) => {
      if (ref.current) {
        ref.current.textContent = `${Math.round(latest)}${suffix}`;
      }
    });
  }, [spring, suffix, value, reduce]);

  return (
    <span ref={ref} className={className}>
      {reduce ? `${value}${suffix}` : `0${suffix}`}
    </span>
  );
}
