"use client";

import { useEffect, useState } from "react";
import {
  CircleCheckIcon,
  InfoIcon,
  Loader2Icon,
  OctagonXIcon,
  TriangleAlertIcon,
} from "lucide-react";
import { Toaster as Sonner, toast, type ToasterProps } from "sonner";

/**
 * The site's one toast surface.
 *
 * Two changes from the stock shadcn wrapper:
 *
 *  1. The theme comes from `data-theme` on <html>, which is what this site has
 *     always keyed off, instead of from next-themes (a dependency this project
 *     does not have and does not need for one attribute).
 *  2. It publishes `window.toast`, because the Python playground and the other
 *     plain scripts under public/ are not React and cannot import anything.
 *     They called the old toast.js with exactly this shape, so they keep
 *     working and there is still only one toast system on the page.
 */
type Variant = "success" | "error" | "warning" | "info";

function useThemeAttribute(): ToasterProps["theme"] {
  const [theme, setTheme] = useState<ToasterProps["theme"]>("system");

  useEffect(() => {
    const read = () =>
      setTheme(
        (document.documentElement.dataset.theme as ToasterProps["theme"]) ??
          "system",
      );

    read();
    const observer = new MutationObserver(read);
    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
    return () => observer.disconnect();
  }, []);

  return theme;
}

export function Toaster(props: ToasterProps) {
  const theme = useThemeAttribute();

  useEffect(() => {
    window.toast = {
      show({ title, description, variant }) {
        const say =
          variant && variant in toast ? (variant as Variant) : "message";
        const fn = say === "message" ? toast : toast[say];
        fn(title, { description });
      },
    };
  }, []);

  return (
    <Sonner
      theme={theme}
      position="bottom-right"
      className="toaster group"
      icons={{
        success: <CircleCheckIcon className="size-4" />,
        info: <InfoIcon className="size-4" />,
        warning: <TriangleAlertIcon className="size-4" />,
        error: <OctagonXIcon className="size-4" />,
        loading: <Loader2Icon className="size-4 animate-spin" />,
      }}
      style={
        {
          "--normal-bg": "var(--popover)",
          "--normal-text": "var(--foreground)",
          "--normal-border": "var(--line)",
          "--border-radius": "var(--radius)",
        } as React.CSSProperties
      }
      {...props}
    />
  );
}

export { toast };
