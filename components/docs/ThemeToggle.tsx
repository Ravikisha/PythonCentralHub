"use client";

import { useEffect, useState } from "react";
import { MoonStar, Sun } from "lucide-react";
import { Button } from "@/components/ui/button";

type Theme = "light" | "dark";

/**
 * Light / dark switch.
 *
 * The choice is written to `data-theme` on <html> and remembered in
 * localStorage, matching what every stylesheet here keys off. `app/layout.tsx`
 * applies the stored value before first paint, so this never causes the flash
 * of the wrong theme.
 *
 * Both icons are always mounted and cross-faded: swapping one element for the
 * other makes the button jump by a pixel as the glyphs differ in width, and
 * the rotation is what tells you the switch did something.
 */
export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme | null>(null);

  useEffect(() => {
    const current = document.documentElement.dataset.theme as Theme | undefined;
    setTheme(
      current ??
        (window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light"),
    );
  }, []);

  function toggle() {
    const next: Theme = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("pch-theme", next);
    } catch {
      /* private mode: the choice lasts for this page only */
    }
  }

  return (
    <Button
      type="button"
      variant="ghost"
      size="icon"
      onClick={toggle}
      className="relative"
      // Until the effect has run we do not know the theme, and announcing the
      // wrong one is worse than announcing it generically.
      aria-label={
        theme
          ? `Switch to ${theme === "dark" ? "light" : "dark"} theme`
          : "Switch theme"
      }
    >
      <Sun
        className="size-[18px] rotate-0 scale-100 transition-all duration-300 dark:-rotate-90 dark:scale-0"
        aria-hidden="true"
      />
      <MoonStar
        className="absolute size-[18px] rotate-90 scale-0 transition-all duration-300 dark:rotate-0 dark:scale-100"
        aria-hidden="true"
      />
    </Button>
  );
}

export default ThemeToggle;
