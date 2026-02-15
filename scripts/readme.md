# 🛠️ SEO & Content Automation Scripts

This directory contains the **Core Engine** for the `seo-site` project. These scripts automate content generation, optimization, and maintenance.

> **🤖 FOR AI AGENTS:**
> When asked to "generate content", "fix the blog", or "optimize images", **ALWAYS** check this directory first.
> Do NOT write new one-off scripts. Use the existing engines below.

---

## 🚀 1. Core Content Generation

### `unified_content_workflow.py` (The Flagship)
**Purpose:** The main entry point for generating high-quality, single blog posts.
**Capabilities:** Keyword research -> Outline -> Drafting -> Critique -> Image Gen -> SEO Audit -> Formatting.
**Usage:**
```bash
# General Technical Article
python scripts/unified_content_workflow.py --topic "Future of AI Agents" --mode general

# News Brief (Short, punchy, trend-focused)
python scripts/unified_content_workflow.py --topic "OpenAI o3 Release" --mode news

# Detailed Guide (Step-by-step, tutorial style)
python scripts/unified_content_workflow.py --topic "How to fine-tune Llama 3" --mode guide
```

### `programmatic_seo_engine.py` (The Bulk Generator)
**Purpose:** Generating volume content based on structured data (Comparison, Listicle, Review, Tutorial).
**Data Source:** Uses `scripts/data/` (e.g. `ai_tools.json`) as the source of truth.
**Usage:**
```bash
# Generate comparison articles (e.g., Tool A vs Tool B)
python scripts/programmatic_seo_engine.py --type comparison

# Generate listicle articles (e.g., Top 10 Tools)
python scripts/programmatic_seo_engine.py --type listicle
```

### `content_expander.py` (The Scaler)
**Purpose:** "Old Content -> New Content". Expands short/thin articles into full-length SEO masterpieces.
**Usage:**
```bash
# Expand all "thin" articles (<800 words)
python scripts/content_expander.py --mode thin

# Expand specific article by slug
python scripts/content_expander.py --slug "my-short-post"
```

---

## 🎨 2. Assets & Media

### `image_manager.py` (The Visual Engine)
**Purpose:** All-in-one image handler. Generates, optimizes, and audits images.
**Usage:**
```bash
# 1. Generate an image from a prompt (Uses Gemini Imagen 3)
python scripts/image_manager.py --action generate --prompt "A futuristic cyberpunk city, neon lights, 8k" --output "assets/cyber-city.png"

# 2. Optimize ALL assets (Convert to WebP, Resize >1200px)
python scripts/image_manager.py --action optimize

# 3. Apply generated images to Markdown frontmatter
python scripts/image_manager.py --action apply

# 4. Audit for missing images or unused "zombie" files
python scripts/image_manager.py --action audit
```

---

## 🧹 3. Maintenance & SEO

### `blog_maintenance.py` (The Janitor)
**Purpose:** Keeps the codebase clean, consistent, and error-free.
**Usage:**
```bash
# Fix Markdown structuring (Tables, Code Fences, Trapped Text)
python scripts/blog_maintenance.py --action format

# Audit for structural issues (Read-only check)
python scripts/blog_maintenance.py --action audit

# Standardize Frontmatter (Dates, Tags, Descriptions)
python scripts/blog_maintenance.py --action clean

# Add 'noindex' to thin content
python scripts/blog_maintenance.py --action noindex --min-words 500
```

### `link_builder.py` (The Connector)
**Purpose:** Internal linking and graph structure.
**Usage:**
```bash
# Build internal links based on semantic relevance
python scripts/link_builder.py --build

# Audit for broken internal links
python scripts/link_builder.py --audit
```

---

## 🧠 4. Utilities

### `generate_llm_bundle.js`
**Purpose:** Dumps ALL blog content into a single text file (`public/llms-full.txt`).
**Why:** Use this file to feed a generic LLM (like ChatGPT or Claude) with your *entire* content history for context-aware Q&A.
**Usage:**
```bash
node scripts/generate_llm_bundle.js
```

---

## ⚠️ Workflow Rules
1. **Always Optimize Images:** Run `image_manager.py --action optimize` after adding any new image.
2. **Check Structure:** Run `blog_maintenance.py --action audit` before pushing.
3. **Safe Deploy:** Use `./deploy.sh` in the root (which builds first) instead of raw `git push`.
