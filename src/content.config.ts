import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const blog = defineCollection({
	// Load Markdown and MDX files in the `src/content/blog/` directory.
	loader: glob({
		base: './src/content/blog',
		pattern: ['**/*.{md,mdx}', '!archive/**', '!**/archive/**'],
	}),
	// Type-check frontmatter using a schema
	schema: ({ image }) =>
		z.object({
			// Some legacy/generated files may miss frontmatter fields.
			// Keep build fail-safe by providing schema-level fallbacks.
			title: z.string().catch('Untitled'),
			description: z.string().catch(''),
			// Transform string to Date object and fallback on invalid/missing values.
			pubDate: z.coerce.date().catch(new Date('2026-01-01T00:00:00Z')),
			updatedDate: z.coerce.date().optional(),
			heroImage: z.string().optional(),
			tags: z.array(z.string()).default(['Uncategorized']),
			noindex: z.boolean().default(false),
		}),
});

export const collections = { blog };
