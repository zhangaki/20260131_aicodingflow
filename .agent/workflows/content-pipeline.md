---
description: How to run the automated SEO content pipeline
---

# SEO Content Generation & Cleanup Pipeline

Use this workflow to generate new AI content and automatically perform technical SEO cleanup (formatting, linking, optimization).

// turbo
1. Run the master pipeline script:
   ```bash
   python3 scripts/pipeline.py
   ```

## What this workflow does:
- **Generates Content**: Automatically creates articles for hot topics and GSC targets.
- **Audits Formatting**: Strips AI conversational filler and fixes markdown code block wrappers.
- **Builds Links**: Analyzes the codebase to insert relevant internal links.
- **Optimizes Assets**: Converts new hero images to WebP and updates Markdown frontmatter.

## When to use this:
- After identifying new trending topics in `generate_2026_hot_topics.py`.
- After identifying high-impression zero-click keywords in GSC.
- To perform a global technical health check on all blog posts.
