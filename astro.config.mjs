import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';
import vercel from '@astrojs/vercel';
import { defineConfig } from 'astro/config';

import expressiveCode from 'astro-expressive-code';

// https://astro.build/config
export default defineConfig({
	site: 'https://ai-coding-flow.com',
	output: 'server',
	adapter: vercel(),
	integrations: [
		expressiveCode(),
		mdx(),
		sitemap({
			customPages: ['https://ai-coding-flow.com/tools/aeo-audit']
		})
	],
});
