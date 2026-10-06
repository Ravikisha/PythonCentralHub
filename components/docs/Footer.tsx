import Link from "next/link";
import { t } from "@/lib/strings";
import { Wordmark } from "@/components/brand/Wordmark";
import { REPO_URL } from "@/lib/site";

/**
 * The site footer.
 *
 * Deliberately short: what a reader actually goes looking for at the bottom
 * of a page -- who runs the site and how to reach them, the policies, the
 * source, the feed and a way in to their own progress.
 */
const LINKS: { href: string; label: string; external?: boolean }[] = [
  {
    href: REPO_URL,
    label: "Source",
    external: true,
  },
  { href: "/courses/", label: "Courses" },
  { href: "/about/", label: "About" },
  { href: "/reference/contact/", label: "Contact" },
  { href: "/rss.xml", label: "RSS" },
  { href: "/policy/", label: "Privacy" },
  { href: "/terms/", label: "Terms" },
  { href: "/dashboard/", label: "Your progress" },
  { href: "/saved/", label: "Saved" },
];

export function Footer() {
  return (
    <footer className="foot">
      <p className="foot__mark">
        <Wordmark />
      </p>

      {/* The one ask on the page, and it is a link rather than a panel: the
          author pays for the hosting, and the reader pays nothing. */}
      <a
        className="foot__coffee"
        href="https://buymeacoffee.com/ravikisha"
        rel="noopener"
        target="_blank"
      >
        <svg
          width="15"
          height="15"
          viewBox="0 0 24 24"
          fill="none"
          aria-hidden="true"
        >
          <path
            d="M4 8h13v6a5 5 0 0 1-5 5H9a5 5 0 0 1-5-5V8Z"
            stroke="currentColor"
            strokeWidth="1.6"
          />
          <path
            d="M17 10h1.5a2.5 2.5 0 0 1 0 5H17"
            stroke="currentColor"
            strokeWidth="1.6"
          />
          <path
            d="M8 3v2M12 3v2"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
        {t("pch.coffeeCta")}
      </a>

      <nav className="foot__links" aria-label="Site">
        {LINKS.map((link) =>
          link.external ? (
            <a key={link.href} href={link.href} rel="noopener" target="_blank">
              {link.label}
            </a>
          ) : (
            <Link key={link.href} href={link.href}>
              {link.label}
            </Link>
          ),
        )}
      </nav>
    </footer>
  );
}

export default Footer;
