import type { Metadata } from "next";
import Link from "next/link";
import { Header } from "@/components/docs/Header";
import { Footer } from "@/components/docs/Footer";
import { ShortcutKey } from "@/components/docs/ShortcutKey";
import "@/components/docs/docs.css";
import "@/components/docs/chrome.css";

export const metadata: Metadata = {
  title: "Page not found",
};

/**
 * 404.
 *
 * An empty screen is an invitation to act, so this offers the two things
 * someone who mistyped a URL actually wants: the search, and the way back into
 * the course. It does not apologise and it does not explain HTTP.
 *
 * It carries the site header, because the shortcut it tells you to press
 * belongs to the search in that header -- without it the key did nothing.
 */
export default function NotFound() {
  return (
    <>
      <Header />
      <main className="mx-auto w-full max-w-2xl px-4 py-24">
        <p
          className="font-mono text-sm"
          style={{ color: "var(--color-python-blue-bright)" }}
        >
          &gt;&gt;&gt; 404
        </p>

        <h1 className="mt-4 text-4xl font-bold leading-tight">
          There is no page here
        </h1>

        <p className="mt-4 text-lg" style={{ color: "var(--muted)" }}>
          The address may have a typo, or the page may have moved. Press{" "}
          <ShortcutKey className="rounded border px-1.5 py-0.5 font-mono text-sm" />{" "}
          to search the course, or start from the top.
        </p>

        <p className="mt-8">
          <Link
            href="/"
            className="underline underline-offset-4"
            style={{ color: "var(--link)" }}
          >
            All modules
          </Link>
        </p>
      </main>
      <Footer />
    </>
  );
}
