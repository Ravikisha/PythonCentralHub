"use client";

import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import type { Root } from "fumadocs-core/page-tree";
import { Button } from "@/components/ui/button";
import { Search } from "./Search";
import { ThemeToggle } from "./ThemeToggle";
import { Sidebar } from "./Sidebar";
import { UserMenu } from "./UserMenu";
import { Notifications } from "./Notifications";
import { Wordmark } from "@/components/brand/Wordmark";
import { SITE_NAME } from "@/lib/site";

/**
 * Site header.
 *
 * The wordmark opens the catalogue, and the two links beside it are the two
 * places a learner goes between lessons: the courses, and their own progress.
 *
 * Below 64rem the sidebar becomes a drawer opened from here, because the same
 * tree is the only way to navigate a course of this size on a phone.
 *
 * The tree is optional: the signed-in pages (dashboard, profile, exams) use
 * the same header without it, and offering a "contents" button there would
 * open a drawer of course pages on a screen that is about the reader.
 */
export function Header({ tree }: { tree?: Root }) {
  const [drawer, setDrawer] = useState(false);
  const pathname = usePathname();
  const menuButton = useRef<HTMLButtonElement>(null);
  const panel = useRef<HTMLDivElement>(null);

  // Picking a lesson navigates without a reload, so the drawer has to close
  // itself -- it used to stay open over the page it had just opened.
  useEffect(() => {
    setDrawer(false);
  }, [pathname]);

  // Open: focus moves into the panel and Escape closes it. Closed: focus goes
  // back to the button that opened it.
  useEffect(() => {
    if (!drawer) return;
    const trigger = menuButton.current;
    panel.current
      ?.querySelector<HTMLElement>('[aria-current="page"], a, button')
      ?.focus({ preventScroll: true });

    // A modal dialog keeps focus inside it: Tab and Shift-Tab cycle through
    // the drawer's links and the button that closes it, and the page behind
    // is `inert`, so neither the keyboard nor a screen reader wanders into
    // content the drawer covers.
    const FOCUSABLE = 'a[href], button:not([disabled]), input, summary, [tabindex]:not([tabindex="-1"])';
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setDrawer(false);
        return;
      }
      if (e.key !== "Tab" || !panel.current) return;
      // Links inside a collapsed section are in the DOM and look visible to
      // offsetParent, but cannot take focus; skip them, keeping summaries.
      const stops = [
        ...(trigger ? [trigger] : []),
        ...panel.current.querySelectorAll<HTMLElement>(FOCUSABLE),
      ].filter(
        (el) =>
          el === trigger ||
          (el.offsetParent !== null &&
            (!el.closest("details:not([open])") || el.closest("summary") !== null)),
      );
      if (!stops.length) return;
      // Move through the stops ourselves, wrapping at both ends, so the
      // browser never gets to pick a target outside the drawer.
      e.preventDefault();
      const at = stops.indexOf(document.activeElement as HTMLElement);
      const next =
        at === -1
          ? e.shiftKey
            ? stops.length - 1
            : 0
          : (at + (e.shiftKey ? -1 : 1) + stops.length) % stops.length;
      stops[next].focus();
    };
    document.addEventListener("keydown", onKey);

    const behind = [...document.querySelectorAll<HTMLElement>("main, footer.foot")]
      .filter((el) => !el.contains(panel.current));
    behind.forEach((el) => el.setAttribute("inert", ""));

    return () => {
      document.removeEventListener("keydown", onKey);
      behind.forEach((el) => el.removeAttribute("inert"));
      trigger?.focus({ preventScroll: true });
    };
  }, [drawer]);

  return (
    <>
      <header className="hdr">
        {tree ? (
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="hdr__menu"
            ref={menuButton}
            onClick={() => setDrawer((v) => !v)}
            aria-expanded={drawer}
            aria-label={
              drawer ? "Close the course contents" : "Open the course contents"
            }
          >
            {drawer ? (
              <X className="size-[18px]" aria-hidden="true" />
            ) : (
              <Menu className="size-[18px]" aria-hidden="true" />
            )}
          </Button>
        ) : null}

        <Link className="hdr__brand" href="/" aria-label={`${SITE_NAME} home`}>
          <Wordmark />
        </Link>

        <nav className="hdr__nav" aria-label="Main">
          <Link href="/courses/">Courses</Link>
          <Link href="/dashboard/">My learning</Link>
        </nav>

        <span className="hdr__spacer" />

        <Search />
        <ThemeToggle />
        <Notifications />
        <UserMenu />
      </header>

      {drawer && tree ? (
        <>
          <div className="drawer__backdrop" onClick={() => setDrawer(false)} />
          <div
            className="drawer"
            ref={panel}
            role="dialog"
            aria-modal="true"
            aria-label="Course contents"
          >
            <Sidebar tree={tree} />
          </div>
        </>
      ) : null}
    </>
  );
}

export default Header;
