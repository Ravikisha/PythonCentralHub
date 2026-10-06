/**
 * Asides — the `:::note` / `:::tip` / `:::caution` / `:::danger` blocks.
 *
 * 666 content files carry 2186 of these, so they are not a decorative extra:
 * they are how the writing marks the difference between "here is a fact" and
 * "here is the thing that will bite you". The Astro build got them from
 * Starlight; here they come from remark-directive plus Fumadocs' admonition
 * transform, which emits the three components below.
 *
 * Styling follows the site's existing device rather than inventing another:
 * a coloured rail on the inline-start edge, the same one the quiz explanations
 * and the profile status line use. Four kinds, four colours, no icons — the
 * label already says which it is.
 */
export type AsideKind = "info" | "tip" | "warn" | "error";

const LABEL: Record<AsideKind, string> = {
  info: "Note",
  tip: "Tip",
  warn: "Careful",
  error: "Danger",
};

export function Callout({
  type = "info",
  children,
}: {
  type?: AsideKind | string;
  children?: React.ReactNode;
}) {
  const kind = (["info", "tip", "warn", "error"] as const).includes(
    type as AsideKind,
  )
    ? (type as AsideKind)
    : "info";

  return (
    <aside className="pch-aside" data-kind={kind} role="note">
      {children}
    </aside>
  );
}

/**
 * The directive's label, e.g. `:::caution[A return inside finally…]`.
 *
 * When an author gives no label the transform still emits this element empty,
 * so it falls back to the kind's own name rather than rendering a blank line.
 */
export function CalloutTitle({
  children,
  type,
}: {
  children?: React.ReactNode;
  type?: AsideKind | string;
}) {
  const empty =
    children === undefined ||
    children === null ||
    (typeof children === "string" && children.trim() === "");

  return (
    <p className="pch-aside__title">
      {empty ? (LABEL[(type as AsideKind) ?? "info"] ?? "Note") : children}
    </p>
  );
}

export function CalloutBody({ children }: { children?: React.ReactNode }) {
  return <div className="pch-aside__body">{children}</div>;
}
