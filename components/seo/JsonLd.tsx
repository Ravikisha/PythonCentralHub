/**
 * A schema.org block for search engines.
 *
 * `<` is escaped so a title containing "</script>" cannot end the block
 * early -- the data here comes from content files, which is to say from
 * anyone who can open a pull request.
 */
export function JsonLd({ data }: { data: Record<string, unknown> }) {
  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(data).replace(/</g, "\\u003c"),
      }}
    />
  );
}
