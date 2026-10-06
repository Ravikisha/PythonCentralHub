/**
 * Replacements for the two Starlight primitives the content still uses.
 *
 * `404.mdx` and the four locale index pages import `CardGrid` and `LinkCard`
 * from `@astrojs/starlight/components`. That is a bare package import, so the
 * import codemod's `.astro` pattern never matched it, and the first production
 * build failed on `/404` trying to type-strip Starlight's own TypeScript.
 *
 * These reproduce the markup and class names Starlight emits, so the existing
 * `.card`/`.sl-link-card` rules in src/styles keep applying. Phase 2 replaces
 * them with the new design system's own cards.
 */
export interface CardGridProps {
  children?: React.ReactNode;
  /** Starlight's staggered layout, which offsets alternate cards. */
  stagger?: boolean;
}

export function CardGrid({ children, stagger = false }: CardGridProps) {
  return (
    <div className={`card-grid${stagger ? " stagger" : ""}`} data-card-grid="">
      {children}
    </div>
  );
}

export interface LinkCardProps {
  title: string;
  href: string;
  description?: string;
}

export function LinkCard({ title, href, description }: LinkCardProps) {
  return (
    <div className="sl-link-card">
      <span className="sl-flex stack">
        <a href={href}>
          <span className="title">{title}</span>
        </a>
        {description ? (
          <span className="description">{description}</span>
        ) : null}
      </span>
      <span aria-hidden="true" className="icon rtl:flip">
        →
      </span>
    </div>
  );
}
