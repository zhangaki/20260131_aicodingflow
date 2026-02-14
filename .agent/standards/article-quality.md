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
### Word Count Standards
- **Hard Minimum**: **1,000+ words** for indexable content.
- **Thin Content Penalty**: Any article **<500 words** must be marked with `noindex: true` (managed by `noindex_thin.py`).
- **Optimal SEO Range**: **1,500 - 2,500 words** is the target for standard reviews and tutorials.
- **Pillar Content**: **3,000+ words** for high-authority "Pillar" or "Deep Dive" articles.

### Quality Signals
- **Expertise Signals (Required)**: Every article must include "First-hand experience" phrases (e.g., "I tested this for 30 days...", "Our engineering team found...").
- **Specific Data/Benchmarks**: Include specific numbers (pricing, token speed, benchmark scores) rather than generic adjectives.
- **Data Density**: Every deep-dive post must have a validated table (**Metric | Target | Standard**) to show data density.
- **AEO/GEO markers**: Include explicit mentions of `llms.txt`, `JSON-LD`, and `crawlers` to attract AI-native traffic.
- **Native-Level English**: Avoid "Chinglish" and AI-isms. The flow must be natural and professional.

## 3. SEO & Internal Linking
- **Internal Links**: Every article should have 3-5 relevant internal links (handled by `internal_link_builder.py`).
- **Keyword Density**: Natural use of primary and secondary keywords. Avoid "AI News" keywords; stick to technical architecture terminology.
- **Pro Tips**: Include tool-specific "Pro Tips" (e.g., Cursor's Composer mode vs standard completion).

## 4. Resource Optimization
- **Images**: All images must be optimized WebP format (max width 1280px).
- **Alt Text**: Image tags should have descriptive alt text.

## 5. Automated Audit Process
The standards above are enforced by:
1.  **Generation Cleanup**: Logic inside `generate_2026_hot_topics.py` and `generate_gsc_targeted_articles.py`.
2.  **Formatting Audit**: `python scripts/audit_article_formatting.py --fix`.
3.  **Master Pipeline**: `python scripts/pipeline.py`.
