# 🛠️ SEO & Content Automation Scripts

This directory contains the **Core Engine** for the `seo-site` project. These scripts are numbered to indicate their order in the content workflow.

> **🤖 FOR AI AGENTS:**
> When asked to "generate content", "fix the blog", or "optimize images", **ALWAYS** check this directory first.
> Do NOT write new one-off scripts. Use the existing engines below.

---

## 🚀 1. Strategy & Planning

### `01_topic_researcher.py` (The Editor-in-Chief)
**Purpose:** Automates the "What should I write about?" phase. Searches for trends, checks for duplicates, and simple high-potential topics.
**Capabilities:** Google Trends Search -> Deduplication -> Ideation -> Command Generation.
**Usage:**
```bash
# Find 5 trending topics in the default niche (AI/Coding)
python scripts/01_topic_researcher.py

# Find topics for a specific niche
python scripts/01_topic_researcher.py --niche "Python Web Frameworks" --count 3
```

---

## ✍️ 2. core Content Generation

### `02_unified_content_workflow.py` (The Flagship)
**Purpose:** The main entry point for generating high-quality, single blog posts.
**Capabilities:** Keyword research -> Outline -> Drafting -> Critique -> Image Gen -> SEO Audit -> Formatting.
**Usage:**
```bash
# General Technical Article
python scripts/02_unified_content_workflow.py --topic "Future of AI Agents" --mode general

# News Brief (Short, punchy, trend-focused)
python scripts/02_unified_content_workflow.py --topic "OpenAI o3 Release" --mode news

# Detailed Guide (Step-by-step, tutorial style)
python scripts/02_unified_content_workflow.py --topic "How to fine-tune Llama 3" --mode guide
```

### `03_programmatic_seo_engine.py` (The Bulk Generator)
**Purpose:** Generating volume content based on structured data (Comparison, Listicle, Review, Tutorial).
**Data Source:** Uses `scripts/data/` (e.g. `ai_tools.json`) as the source of truth.
**Usage:**
```bash
# Generate comparison articles (e.g., Tool A vs Tool B)
python scripts/03_programmatic_seo_engine.py --type comparison

# Generate listicle articles (e.g., Top 10 Tools)
python scripts/03_programmatic_seo_engine.py --type listicle
```

### `04_batch_generate_deep_dives.sh` (The Batch Runner)
**Purpose:** Shell script to execute multiple `02_unified_content_workflow.py` commands in sequence.
**Usage:**
```bash
# Run the batch generation
./scripts/04_batch_generate_deep_dives.sh
```

---

## 📈 3. Optimization & Growth

### `05_content_expander.py` (The Scaler)
**Purpose:** "Old Content -> New Content". Expands short/thin articles into full-length SEO masterpieces.
**Usage:**
```bash
# Expand all "thin" articles (<800 words)
python scripts/05_content_expander.py --mode thin

# Expand specific article by slug
python scripts/05_content_expander.py --slug "my-short-post"
```

### `06_link_builder.py` (The Connector)
**Purpose:** Internal linking and graph structure.
**Usage:**
```bash
# Build internal links based on semantic relevance
python scripts/06_link_builder.py --build

# Audit for broken internal links
python scripts/06_link_builder.py --audit
```

---

## 🎨 4. Assets & Maintenance

### `07_image_manager.py` (The Visual Engine)
**Purpose:** All-in-one image handler. Generates, optimizes, and audits images.
**Usage:**
```bash
# 1. Generate an image from a prompt (Uses Gemini Imagen 3)
python scripts/07_image_manager.py --action generate --prompt "A futuristic cyberpunk city, neon lights, 8k" --output "assets/cyber-city.png"

# 2. Optimize ALL assets (Convert to WebP, Resize >1200px)
python scripts/07_image_manager.py --action optimize

# 3. Audit for missing images or unused "zombie" files
python scripts/07_image_manager.py --action audit
```

### `08_blog_maintenance.py` (The Janitor)
**Purpose:** Keeps the codebase clean, consistent, and error-free.
**Usage:**
```bash
# Fix Markdown structuring (Tables, Code Fences, Trapped Text)
python scripts/08_blog_maintenance.py --action format

# Audit for structural issues (Read-only check)
python scripts/08_blog_maintenance.py --action audit

# Standardize Frontmatter (Dates, Tags, Descriptions)
python scripts/08_blog_maintenance.py --action clean

# Add 'noindex' to thin content
python scripts/08_blog_maintenance.py --action noindex --min-words 500
```

---

## 🧠 5. Utilities

### `09_generate_llm_bundle.js`
**Purpose:** Dumps ALL blog content into a single text file (`public/llms-full.txt`).
**Why:** Use this file to feed a generic LLM (like ChatGPT or Claude) with your *entire* content history for context-aware Q&A.
**Usage:**
```bash
node scripts/09_generate_llm_bundle.js
```

---

## ⚠️ Workflow Rules
1. **Always Optimize Images:** Run `scripts/07_image_manager.py --action optimize` after adding any new image.
2. **Check Structure:** Run `scripts/08_blog_maintenance.py --action audit` before pushing.
3. **Safe Deploy:** Use `./deploy.sh` in the root (which builds first) instead of raw `git push`.
