"use client";

import { useEffect, useState } from "react";

/**
 * The search shortcut, spelled the way this reader's keyboard spells it.
 *
 * The listener accepts both ⌘K and Ctrl-K; only the label differs. It renders
 * ⌘K on the server and swaps after mount, so the prerendered markup stays the
 * same for everyone and hydration never disagrees.
 */
export function ShortcutKey({ className }: { className?: string }) {
  const [mac, setMac] = useState(true);

  useEffect(() => {
    const platform =
      (navigator as Navigator & { userAgentData?: { platform?: string } })
        .userAgentData?.platform ?? navigator.platform;
    setMac(/mac|iphone|ipad/i.test(platform));
  }, []);

  return <kbd className={className}>{mac ? "⌘K" : "Ctrl K"}</kbd>;
}
