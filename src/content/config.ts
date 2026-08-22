import { defineCollection, z } from 'astro:content';
import { docsSchema, i18nSchema } from '@astrojs/starlight/schema';

/**
 * DSA interview metadata.
 *
 * Carried in the frontmatter of pages under `DSA with Python/` so that the
 * problem database, the generated practice ladders and the coverage audit all
 * read one source of truth instead of re-deriving it from prose.
 *
 * Every field is optional: the other ~700 pages on the site set none of them,
 * and a required field here would fail their builds.
 */
const dsaMeta = z.object({
	/**
	 * Pattern slugs this page teaches, e.g. `sliding-window`, `monotonic-stack`.
	 * `<ProblemLadder pattern="...">` matches problems against these.
	 */
	patterns: z.array(z.string()).optional(),

	/** Rough interview tier of the page's material. */
	difficulty: z.enum(['easy', 'medium', 'hard', 'mixed']).optional(),

	/** Pattern slugs a reader should have covered first. */
	prereqs: z.array(z.string()).optional(),

	/**
	 * Where this topic sits in the public study sheets. Each value is that
	 * sheet's own section/step label, or `true` for sheets without sections.
	 */
	sheets: z.record(z.union([z.string(), z.boolean()])).optional(),

	/** Company slugs that ask this pattern often, e.g. `google`, `meta`. */
	companies: z.array(z.string()).optional(),
});

export const collections = {
	docs: defineCollection({ schema: docsSchema({ extend: dsaMeta }) }),
	i18n: defineCollection({ type: 'data', schema: i18nSchema() }),
};
