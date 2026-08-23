import { defineCollection } from 'astro:content';
import { z } from 'astro/zod';
import { docsLoader, i18nLoader } from '@astrojs/starlight/loaders';
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
	// Zod 4 (Astro 6+) requires an explicit key schema for `z.record`.
	sheets: z.record(z.string(), z.union([z.string(), z.boolean()])).optional(),

	/** Company slugs that ask this pattern often, e.g. `google`, `meta`. */
	companies: z.array(z.string()).optional(),
});

/**
 * UI strings owned by this site rather than by Starlight.
 *
 * Starlight ships its own chrome translated for 36 locales, but it knows
 * nothing about the copy in `src/components/*` (Share, Print, the feedback
 * form, the quiz and exercise panels, the algorithm cards). Declaring the keys
 * here makes `Astro.locals.t('pch.share')` type-checked, so a typo or a key
 * dropped from one language's JSON is a build error instead of a blank label
 * on a live page.
 *
 * `.partial()` because only `src/content/i18n/en.json` has to be complete --
 * any key missing from another language falls back to English.
 */
const pchUiStrings = z
	.object({
		'pch.share': z.string(),
		'pch.print': z.string(),
		'pch.shareCopied': z.string(),
		'pch.shareCopiedTitle': z.string(),
		'pch.shareCopiedDesc': z.string(),
		'pch.shareDone': z.string(),
		'pch.shareError': z.string(),

		'pch.sidebarSearchPlaceholder': z.string(),
		'pch.sidebarSearchLabel': z.string(),
		'pch.sidebarCollapseAll': z.string(),
		'pch.sidebarExpandAll': z.string(),
		'pch.sidebarNoResults': z.string(),

		'pch.feedbackHeading': z.string(),
		'pch.feedbackSubheading': z.string(),
		'pch.feedbackEmail': z.string(),
		'pch.feedbackEmailPlaceholder': z.string(),
		'pch.feedbackComment': z.string(),
		'pch.feedbackCommentPlaceholder': z.string(),
		'pch.feedbackSubmit': z.string(),
		'pch.feedbackNoscript': z.string(),
		'pch.ratingVeryDissatisfied': z.string(),
		'pch.ratingDissatisfied': z.string(),
		'pch.ratingNeutral': z.string(),
		'pch.ratingSatisfied': z.string(),
		'pch.ratingVerySatisfied': z.string(),

		'pch.coffeeTagline': z.string(),
		'pch.coffeeCta': z.string(),

		'pch.quizTag': z.string(),
		'pch.quizDefaultTitle': z.string(),
		'pch.quizShowAnswer': z.string(),

		'pch.exerciseTag': z.string(),
		'pch.exerciseTitle': z.string(),
		'pch.openFullscreen': z.string(),

		'pch.viewSource': z.string(),
		'pch.viewOnGithub': z.string(),

		'pch.contactEmail': z.string(),
		'pch.contactEmailPlaceholder': z.string(),
		'pch.contactName': z.string(),
		'pch.contactNamePlaceholder': z.string(),
		'pch.contactMessage': z.string(),
		'pch.contactMessagePlaceholder': z.string(),
		'pch.contactSubmit': z.string(),
		'pch.contactIntro': z.string(),
		'pch.contactNoscript': z.string(),

		'pch.algoTag': z.string(),
		'pch.algoApi': z.string(),
		'pch.algoAssumes': z.string(),
		'pch.algoCost': z.string(),
		'pch.algoTrain': z.string(),
		'pch.algoPredict': z.string(),
		'pch.algoMemory': z.string(),
		'pch.algoHyperparams': z.string(),
		'pch.algoReachFor': z.string(),
		'pch.algoLookElsewhere': z.string(),
	})
	.partial();

export const collections = {
	docs: defineCollection({ loader: docsLoader(), schema: docsSchema({ extend: dsaMeta }) }),
	i18n: defineCollection({ loader: i18nLoader(), schema: i18nSchema({ extend: pchUiStrings }) }),
};
