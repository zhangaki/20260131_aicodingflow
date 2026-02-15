import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel';
import { defineConfig } from 'astro/config';
import react from '@astrojs/react';

import expressiveCode from 'astro-expressive-code';

// https://astro.build/config
export default defineConfig({
	site: 'https://ai-coding-flow.com',
	output: 'server',
	adapter: vercel(),
	integrations: [
		expressiveCode({
			themes: ['github-dark'],
		}),
		mdx(),
		sitemap({
			customPages: ['https://ai-coding-flow.com/tools/aeo-audit']
		}),
		react()
	],
});
