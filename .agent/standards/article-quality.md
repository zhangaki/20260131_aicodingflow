# Article Review & Quality Standards

This document defines the quality and technical standards for all articles on ai-coding-flow.com. All content (generated or manual) must pass these criteria.

## 1. Technical Formatting Standards
- **Markdown Hygiene**: Must not contain markdown code block wrappers (e.g., ` ```markdown `) around the entire content.
- **Frontmatter**:
  - `title`: Must be compelling and include the target year (e.g., "2026").
  - `description`: Must be a concise summary for SEO (150-160 characters).
  - `heroImage`: Must point to a valid WebP image in `/assets/`.
  - `pubDate`: Must follow `MMM DD YYYY` format.
- **No Conversational Filler**: Content must NOT start with AI conversational intros like "Okay, here's a draft..." or "I have crafted...".

## 2. Content Quality (HCU / E-E-A-T)
- **First-Person Perspective**: Use "I", "me", "my" to demonstrate personal experience/testing (e.g., "I spent the last two weeks diving deep into...").
- **Specific Data/Benchmarks**: Include specific numbers (pricing, token speed, benchmark scores) rather than generic adjectives.
- **Structure**:
  - `H1` (Title): Unique and SEO-optimized.
  - `H2/H3`: Logical flow, using keywords naturally.
  - **FAQ Section**: Articles should ideally end with an FAQ section to trigger rich snippets.
- **Tone**: Professional, helpful, developer-centric, and data-driven.

## 3. SEO & Internal Linking
- **Internal Links**: Every article should have 3-5 relevant internal links (handled by `internal_link_builder.py`).
- **Keyword Density**: Natural use of primary and secondary keywords.
- **No "AI Footprints"**: Remove repetitive phrases typical of LLMs (e.g., "In the rapidly evolving landscape...").

## 4. Resource Optimization
- **Images**: All images must be optimized WebP format (max width 1280px).
- **Alt Text**: Image tags should have descriptive alt text (if implemented in the layout).

## 5. Automated Audit Process
The standards above are enforced by:
1.  **Generation Cleanup**: Logic inside `generate_2026_hot_topics.py` and `generate_gsc_targeted_articles.py`.
2.  **Formatting Audit**: `python scripts/audit_article_formatting.py --fix`.
3.  **Master Pipeline**: `python scripts/pipeline.py`.
