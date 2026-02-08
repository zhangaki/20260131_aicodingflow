#!/usr/bin/env python3
"""
internal_link_builder.py

Automatically adds internal "Related Reading" links to all blog articles
based on tool relationships, article type hierarchy, and tag overlap.

Usage:
    python scripts/internal_link_builder.py                  # Apply changes
    python scripts/internal_link_builder.py --dry-run        # Preview only
    python scripts/internal_link_builder.py --max-links 3    # Override max links per article
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from typing import Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BLOG_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "src", "content", "blog",
)
BLOG_DIR = os.path.normpath(BLOG_DIR)

KNOWLEDGE_BASE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "data", "product_knowledge_base.json",
)

DEFAULT_MAX_LINKS = 5

# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Matches YAML inline arrays like ["tag1", "tag2", "tag3"]
_YAML_INLINE_LIST_RE = re.compile(r'\[([^\]]*)\]')

# Matches YAML block list items like:
# - tag1
# - tag2
_YAML_BLOCK_ITEM_RE = re.compile(r'^\s*-\s+(.+)$', re.MULTILINE)


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from markdown content using regex.

    Returns a dict with keys: title, description, tags, etc.
    """
    m = _FRONTMATTER_RE.match(content)
    if not m:
        return {}

    raw = m.group(1)
    result = {}

    for line in raw.split("\n"):
        # Skip continuation lines (indented or list items handled separately)
        if line.startswith("  ") or line.startswith("\t"):
            continue
        if ":" not in line:
            continue

        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()

        # Strip surrounding quotes
        if value and value[0] in ('"', "'") and value[-1] == value[0]:
            value = value[1:-1]

        result[key] = value

    # Parse tags specially -- handle both inline and block formats
    tags_raw = _extract_tags_block(raw)
    result["tags"] = tags_raw

    return result


def _extract_tags_block(frontmatter_raw: str) -> list[str]:
    """Extract tags from frontmatter, handling both inline and block list YAML."""
    tags = []

    # Find the tags line
    lines = frontmatter_raw.split("\n")
    tags_start = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("tags:"):
            tags_start = i
            break

    if tags_start == -1:
        return []

    tags_line = lines[tags_start]
    after_colon = tags_line.partition(":")[2].strip()

    # Case 1: Inline list -- tags: ["tag1", "tag2"]
    inline_match = _YAML_INLINE_LIST_RE.search(after_colon)
    if inline_match:
        items_str = inline_match.group(1)
        for item in items_str.split(","):
            item = item.strip().strip('"').strip("'")
            if item:
                tags.append(item.lower())
        return tags

    # Case 2: Block list
    # tags:
    # - tag1
    # - tag2
    for j in range(tags_start + 1, len(lines)):
        line = lines[j]
        block_match = re.match(r'^\s*-\s+(.+)$', line)
        if block_match:
            tag = block_match.group(1).strip().strip('"').strip("'")
            tags.append(tag.lower())
        else:
            # Hit a non-list-item line -- stop
            if line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                break
            elif line.strip() == "":
                continue

    return tags


# ---------------------------------------------------------------------------
# Article data model
# ---------------------------------------------------------------------------

class Article:
    """Lightweight representation of a blog article."""

    def __init__(self, filename: str, content: str, meta: dict):
        self.filename = filename
        self.slug = filename.replace(".md", "")
        self.content = content
        self.title = meta.get("title", "")
        self.tags = meta.get("tags", [])
        self.article_type = self._detect_type()
        self.tools_mentioned: list[str] = []  # tool keys from knowledge base

    def _detect_type(self) -> str:
        slug = self.slug.lower()
        if slug.startswith("best-ai-"):
            return "best"
        if "-vs-" in slug:
            return "comparison"
        if slug.startswith("how-to-use-"):
            return "tutorial"
        if slug.endswith("-review-2026"):
            return "review"
        return "editorial"

    @property
    def url(self) -> str:
        return f"/blog/{self.slug}/"

    def __repr__(self):
        return f"Article({self.slug}, type={self.article_type})"


# ---------------------------------------------------------------------------
# Knowledge base loading
# ---------------------------------------------------------------------------

def load_knowledge_base() -> dict:
    """Load the product knowledge base and return tools dict."""
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        print(f"Warning: Knowledge base not found at {KNOWLEDGE_BASE_PATH}")
        return {}
    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("tools", {})


def build_tool_name_variants(kb_tools: dict) -> dict[str, str]:
    """Build a mapping of lowercase name variants -> tool_key.

    This maps display names and slug-style names to the canonical tool key,
    so we can detect which tools an article is about from its filename.
    """
    variants: dict[str, str] = {}
    for key, info in kb_tools.items():
        name = info.get("name", "")

        # Canonical key itself (e.g. "cursor", "github_copilot")
        variants[key.lower()] = key

        # Display name lowered (e.g. "cursor", "github copilot")
        variants[name.lower()] = key

        # Slug-style: replace spaces/dots with hyphens, lowercase
        slug_name = re.sub(r'[\s\.]+', '-', name.lower())
        variants[slug_name] = key

        # Handle special slug transformations
        # "GitHub Copilot" -> "github-copilot"
        # "DALL-E 3" -> "dall-e-3"
        # "Otter.ai" -> "otterai"
        # "Fireflies.ai" -> "firefliesai"
        # "bolt.new" -> "boltnew"
        # "v0 by Vercel" -> "v0-by-vercel"
        # "Kling AI" -> "kling-ai"
        # "Claude 4.6 Opus" -> "claude-46-opus"
        # "OpenAI o3" -> "openai-o3"
        no_dot = slug_name.replace(".", "")
        variants[no_dot] = key

    # Add known manual slug mappings that don't derive cleanly
    manual_mappings = {
        "dall-e-3": "dalle3",
        "otterai": "otter_ai",
        "firefliesai": "fireflies_ai",
        "boltnew": "bolt_new",
        "v0-by-vercel": "v0_dev",
        "kling-ai": "kling",
        "claude-46-opus": "claude_opus_4_6",
        "openai-o3": "openai_o3",
        "jasper-ai": "jasper",
        "grammarly-ai": "grammarly_ai",
        "replit-ai": "replit_ai",
        "hubspot-ai": "hubspot_ai",
        "zendesk-ai": "zendesk_ai",
        "salesforce-einstein": "salesforce_einstein",
        "leonardo-ai": "leonardo_ai",
        "notion-ai": "notion_ai",
        "claude-code": "claude_code",
        "github-copilot": "github_copilot",
        "stable-diffusion": "stable_diffusion",
        "youcom": "you_com",
        "copilot": "github_copilot",
    }
    for slug_variant, tool_key in manual_mappings.items():
        if tool_key in kb_tools:
            variants[slug_variant] = tool_key

    return variants


def detect_tools_from_slug(slug: str, name_variants: dict[str, str]) -> list[str]:
    """Detect which tools an article is about based on its filename slug.

    For comparison articles (a-vs-b), extracts both tools.
    For reviews (tool-review-2026), extracts the tool.
    For tutorials (how-to-use-tool-for-...), extracts the tool.
    For best articles, extracts tools mentioned in the slug.
    """
    tools_found = []
    slug_lower = slug.lower()

    # Comparison: tool-a-vs-tool-b-2026
    if "-vs-" in slug_lower:
        # Remove trailing year
        core = re.sub(r'-\d{4}$', '', slug_lower)
        parts = core.split("-vs-")
        for part in parts:
            part = part.strip()
            if part in name_variants:
                tools_found.append(name_variants[part])

    # Review: tool-review-2026
    elif slug_lower.endswith("-review-2026"):
        tool_part = slug_lower.replace("-review-2026", "")
        if tool_part in name_variants:
            tools_found.append(name_variants[tool_part])

    # Tutorial: how-to-use-tool-for-...-2026
    elif slug_lower.startswith("how-to-use-"):
        # Extract tool name between "how-to-use-" and "-for-"
        remainder = slug_lower[len("how-to-use-"):]
        for_idx = remainder.find("-for-")
        if for_idx != -1:
            tool_part = remainder[:for_idx]
        else:
            tool_part = re.sub(r'-\d{4}$', '', remainder)
        if tool_part in name_variants:
            tools_found.append(name_variants[tool_part])

    # Best articles: try to find tool mentions in slug
    elif slug_lower.startswith("best-ai-"):
        # These are category pages, not specific tool pages
        pass

    # Fallback: scan slug segments against known tool names
    if not tools_found:
        # Try progressively longer segments of the slug
        core = re.sub(r'-\d{4}$', '', slug_lower)
        segments = core.split("-")
        # Try multi-word combinations (longest first)
        for length in range(min(4, len(segments)), 0, -1):
            for start in range(len(segments) - length + 1):
                candidate = "-".join(segments[start:start + length])
                if candidate in name_variants:
                    key = name_variants[candidate]
                    if key not in tools_found:
                        tools_found.append(key)

    return tools_found


# ---------------------------------------------------------------------------
# Category mapping: which "best" articles cover which tools
# ---------------------------------------------------------------------------

CATEGORY_TO_BEST_ARTICLE = {
    "coding_assistant": "best-ai-tools-for-coding-2026",
    "ai_agent_framework": None,  # No best article
    "video_ai": "best-ai-tools-for-video-creation-2026",
    "llm_provider": None,  # Covered by best-ai-chatgpt-vs-gemini-vs-copilot-2026
    "ai_music": "best-ai-tools-for-music-production-2026",
    "ai_writing": "best-ai-tools-for-writing-2026",
    "ai_image": "best-ai-tools-for-image-generation-2026",
    "ai_productivity": None,
    "ai_search": "best-ai-tools-for-research-2026",
    "ai_development": None,
    "ai_business": "best-ai-tools-for-business-automation-2026",
}

# Map best article slugs to which tool categories they cover
BEST_ARTICLE_CATEGORIES = {
    "best-ai-tools-for-coding-2026": "coding_assistant",
    "best-ai-tools-for-video-creation-2026": "video_ai",
    "best-ai-tools-for-music-production-2026": "ai_music",
    "best-ai-tools-for-writing-2026": "ai_writing",
    "best-ai-tools-for-image-generation-2026": "ai_image",
    "best-ai-tools-for-research-2026": "ai_search",
    "best-ai-tools-for-business-automation-2026": "ai_business",
    "best-ai-tools-for-content-marketing-2026": "ai_writing",
    "best-ai-tools-for-seo-2026": "ai_writing",
    "best-ai-tools-for-social-media-2026": "ai_writing",
    "best-ai-tools-for-data-analysis-2026": "llm_provider",
    "best-ai-tools-for-freelancers-2026": None,  # Cross-category
    "best-ai-tools-for-students-2026": None,  # Cross-category
    "best-ai-tools-for-startups-2026": None,  # Cross-category
    "best-ai-tools-for-customer-support-2026": "ai_business",
    "best-ai-chatgpt-vs-gemini-vs-copilot-2026": "llm_provider",
}


# ---------------------------------------------------------------------------
# Link scoring and ranking
# ---------------------------------------------------------------------------

def _get_category_tools(category: str, kb_tools: dict) -> list[str]:
    """Get all tool keys belonging to a KB category."""
    return [key for key, info in kb_tools.items() if info.get("category") == category]


def build_link_candidates(
    article: Article,
    all_articles: dict[str, Article],
    kb_tools: dict,
    tool_to_articles: dict[str, list[str]],
    category_to_articles: dict[str, list[str]],
    tag_to_articles: dict[str, list[str]],
) -> list[tuple[float, str]]:
    """Build scored link candidates for an article.

    Returns list of (score, slug) tuples, higher score = better match.
    Scoring priorities:
        - Same tool links: base score 100
        - Same KB category links: base score 50
        - Same tag links: base score 10
    With bonuses for article type hierarchy.
    """
    candidates: dict[str, float] = {}
    my_slug = article.slug

    def add_candidate(slug: str, score: float) -> None:
        if slug == my_slug:
            return
        candidates[slug] = candidates.get(slug, 0) + score

    # --- Special handling for "best" articles ---
    # "Best" articles are category pages. We associate them with all tools
    # in their mapped category so they can link to reviews/comparisons.
    effective_tools = list(article.tools_mentioned)
    if article.article_type == "best" and not effective_tools:
        best_category = BEST_ARTICLE_CATEGORIES.get(my_slug)
        if best_category:
            effective_tools = _get_category_tools(best_category, kb_tools)

    # --- Priority 1: Same-tool links ---
    for tool_key in effective_tools:
        tool_info = kb_tools.get(tool_key, {})
        tool_category = tool_info.get("category", "")

        for related_slug in tool_to_articles.get(tool_key, []):
            if related_slug == my_slug:
                continue

            related = all_articles.get(related_slug)
            if not related:
                continue

            base = 100.0

            # Article type hierarchy bonuses
            if article.article_type == "best":
                # Best articles should link to reviews and comparisons
                if related.article_type == "review":
                    base += 30
                elif related.article_type == "comparison":
                    base += 20
                elif related.article_type == "tutorial":
                    base += 10

            elif article.article_type == "review":
                # Reviews should link to comparisons, best lists, and tutorials
                if related.article_type == "comparison":
                    base += 25
                elif related.article_type == "best":
                    base += 20
                elif related.article_type == "tutorial":
                    base += 15

            elif article.article_type == "comparison":
                # Comparisons should link to both tool reviews
                if related.article_type == "review":
                    base += 30
                elif related.article_type == "best":
                    base += 15
                elif related.article_type == "tutorial":
                    base += 10

            elif article.article_type == "tutorial":
                # Tutorials should link to the tool's review first
                if related.article_type == "review":
                    base += 35
                elif related.article_type == "comparison":
                    base += 15
                elif related.article_type == "best":
                    base += 10

            add_candidate(related_slug, base)

        # Also link to the "best" article for this tool's category
        best_slug = CATEGORY_TO_BEST_ARTICLE.get(tool_category)
        if best_slug and best_slug != my_slug:
            add_candidate(best_slug, 80.0)

    # --- Priority 2: Same KB-category links ---
    for tool_key in effective_tools:
        tool_info = kb_tools.get(tool_key, {})
        tool_category = tool_info.get("category", "")

        for cat_slug in category_to_articles.get(tool_category, []):
            if cat_slug == my_slug:
                continue
            # Don't double-count articles already scored by same-tool
            if cat_slug not in candidates:
                add_candidate(cat_slug, 50.0)
            else:
                add_candidate(cat_slug, 10.0)  # Small bonus

    # --- Priority 3: Same-tag links ---
    for tag in article.tags:
        for tag_slug in tag_to_articles.get(tag, []):
            if tag_slug == my_slug:
                continue
            if tag_slug not in candidates:
                add_candidate(tag_slug, 10.0)
            else:
                add_candidate(tag_slug, 2.0)  # Small bonus

    # --- Bonus: "best" articles linking to other relevant "best" articles ---
    if article.article_type == "best":
        for best_slug in BEST_ARTICLE_CATEGORIES:
            if best_slug != my_slug and best_slug not in candidates:
                add_candidate(best_slug, 5.0)

    # Sort by score descending
    scored = [(score, slug) for slug, score in candidates.items()]
    scored.sort(key=lambda x: (-x[0], x[1]))

    return scored


# ---------------------------------------------------------------------------
# Existing link detection
# ---------------------------------------------------------------------------

def find_existing_links(content: str) -> set[str]:
    """Find all internal blog links already present in the content."""
    # Match both /blog/slug/ and /blog/slug patterns
    pattern = r'/blog/([\w-]+)/?'
    return {m.group(1) for m in re.finditer(pattern, content)}


def has_related_reading_section(content: str) -> bool:
    """Check if the article already has a Related Reading section."""
    return bool(re.search(r'^##\s+Related Reading', content, re.MULTILINE))


# ---------------------------------------------------------------------------
# Content injection
# ---------------------------------------------------------------------------

def build_related_section(links: list[tuple[str, str]]) -> str:
    """Build the Related Reading markdown section.

    Args:
        links: List of (title, slug) tuples.
    """
    lines = [
        "",
        "---",
        "",
        "## Related Reading",
        "",
    ]
    for title, slug in links:
        lines.append(f"- [{title}](/blog/{slug}/)")
    lines.append("")
    return "\n".join(lines)


def inject_related_section(content: str, section: str) -> str:
    """Inject the Related Reading section before any FAQ or JSON-LD schema at the end.

    Insertion strategy:
    1. Before "## Frequently Asked Questions" heading if it exists
    2. Before <script type="application/ld+json"> if it exists (without FAQ heading)
    3. At the end of the file
    """
    insert_pos: Optional[int] = None

    # Strategy 1: Before FAQ section
    faq_match = re.search(r'\n(##\s+Frequently Asked Questions)', content)
    if faq_match:
        insert_pos = faq_match.start()

    # Strategy 2: Before JSON-LD script tag
    if insert_pos is None:
        script_match = re.search(r'\n(<script\s+type="application/ld\+json">)', content)
        if script_match:
            insert_pos = script_match.start()

    if insert_pos is not None:
        before = content[:insert_pos]
        after = content[insert_pos:]

        # Check if 'before' already ends with a horizontal rule (---).
        # If so, replace that trailing --- with the section (which starts
        # with its own ---) to avoid a double rule.
        stripped = before.rstrip()
        if stripped.endswith("---"):
            stripped = stripped[:-3].rstrip()
            return stripped + "\n" + section + "\n" + after
        else:
            return before + section + "\n" + after

    # Strategy 3: Append to end, stripping trailing whitespace first
    content = content.rstrip()
    if content.endswith("---"):
        content = content[:-3].rstrip()
    content += "\n"
    return content + section


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def load_articles() -> dict[str, Article]:
    """Load all .md files from the blog directory."""
    articles: dict[str, Article] = {}

    if not os.path.isdir(BLOG_DIR):
        print(f"Error: Blog directory not found: {BLOG_DIR}")
        sys.exit(1)

    for filename in sorted(os.listdir(BLOG_DIR)):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(BLOG_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        meta = parse_frontmatter(content)
        article = Article(filename, content, meta)
        articles[article.slug] = article

    return articles


def build_indexes(
    articles: dict[str, Article],
    kb_tools: dict,
    name_variants: dict[str, str],
) -> tuple[dict[str, list[str]], dict[str, list[str]], dict[str, list[str]]]:
    """Build tool, category, and tag indexes.

    Returns:
        tool_to_articles: tool_key -> list of article slugs
        category_to_articles: category_key -> list of article slugs
        tag_to_articles: tag -> list of article slugs
    """
    tool_to_articles: dict[str, list[str]] = defaultdict(list)
    category_to_articles: dict[str, list[str]] = defaultdict(list)
    tag_to_articles: dict[str, list[str]] = defaultdict(list)

    for slug, article in articles.items():
        # Detect tools from filename
        tools = detect_tools_from_slug(slug, name_variants)
        article.tools_mentioned = tools

        for tool_key in tools:
            tool_to_articles[tool_key].append(slug)

            # Map to category
            tool_info = kb_tools.get(tool_key, {})
            category = tool_info.get("category", "")
            if category:
                category_to_articles[category].append(slug)

        # Tag index
        for tag in article.tags:
            tag_to_articles[tag].append(slug)

    return dict(tool_to_articles), dict(category_to_articles), dict(tag_to_articles)


def run(dry_run: bool = False, max_links: int = DEFAULT_MAX_LINKS) -> None:
    """Main entry point."""
    print(f"Internal Link Builder")
    print(f"  Blog directory: {BLOG_DIR}")
    print(f"  Max links per article: {max_links}")
    print(f"  Dry run: {dry_run}")
    print()

    # Load data
    kb_tools = load_knowledge_base()
    name_variants = build_tool_name_variants(kb_tools)
    articles = load_articles()

    print(f"Loaded {len(articles)} articles and {len(kb_tools)} tools from knowledge base")

    # Build indexes
    tool_to_articles, category_to_articles, tag_to_articles = build_indexes(
        articles, kb_tools, name_variants,
    )

    # Process each article
    updated_count = 0
    total_links_added = 0
    skipped_existing = 0

    for slug in sorted(articles.keys()):
        article = articles[slug]

        # Skip if already has Related Reading section
        if has_related_reading_section(article.content):
            skipped_existing += 1
            continue

        # Find existing links in the article
        existing_links = find_existing_links(article.content)

        # Build and score candidates
        candidates = build_link_candidates(
            article, articles, kb_tools,
            tool_to_articles, category_to_articles, tag_to_articles,
        )

        # Diversity-aware selection: ensure a mix of article types
        # Limit any single article type to at most 3 of the N slots, unless
        # fewer distinct types are available.
        MAX_SAME_TYPE = 2

        # First, filter out ineligible candidates
        eligible: list[tuple[float, str]] = []
        for score, candidate_slug in candidates:
            if candidate_slug in existing_links:
                continue
            candidate = articles.get(candidate_slug)
            if not candidate:
                continue
            eligible.append((score, candidate_slug))

        # Select with diversity: pick the highest-scored from each type
        # in round-robin fashion, then fill remaining slots by score.
        type_counts: dict[str, int] = defaultdict(int)
        selected_slugs: set[str] = set()
        final_links: list[tuple[str, str]] = []

        for score, candidate_slug in eligible:
            if len(final_links) >= max_links:
                break

            candidate = articles[candidate_slug]
            ctype = candidate.article_type

            # Enforce per-type cap to ensure diversity
            if type_counts[ctype] >= MAX_SAME_TYPE:
                continue

            title = candidate.title
            if not title:
                title = candidate_slug.replace("-", " ").title()

            final_links.append((title, candidate_slug))
            selected_slugs.add(candidate_slug)
            type_counts[ctype] += 1

        # If we still have room (due to type caps), fill with remaining
        # highest-scored candidates regardless of type
        if len(final_links) < max_links:
            for score, candidate_slug in eligible:
                if len(final_links) >= max_links:
                    break
                if candidate_slug in selected_slugs:
                    continue
                candidate = articles[candidate_slug]
                title = candidate.title
                if not title:
                    title = candidate_slug.replace("-", " ").title()
                final_links.append((title, candidate_slug))
                selected_slugs.add(candidate_slug)

        if not final_links:
            continue

        # Build the section and inject it
        section = build_related_section(final_links)
        new_content = inject_related_section(article.content, section)

        if dry_run:
            print(f"  [DRY RUN] {slug} (+{len(final_links)} links)")
            for title, link_slug in final_links:
                print(f"    -> /blog/{link_slug}/")
        else:
            filepath = os.path.join(BLOG_DIR, article.filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(new_content)

        updated_count += 1
        total_links_added += len(final_links)

    # Summary
    print()
    print("=" * 60)
    print(f"Summary:")
    print(f"  Total articles scanned: {len(articles)}")
    print(f"  Articles updated: {updated_count}")
    print(f"  Total links added: {total_links_added}")
    print(f"  Articles skipped (already have Related Reading): {skipped_existing}")
    if dry_run:
        print(f"  Mode: DRY RUN (no files were modified)")
    print("=" * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Add internal links (Related Reading) to blog articles.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing to files.",
    )
    parser.add_argument(
        "--max-links",
        type=int,
        default=DEFAULT_MAX_LINKS,
        help=f"Maximum internal links per article (default: {DEFAULT_MAX_LINKS}).",
    )
    args = parser.parse_args()

    run(dry_run=args.dry_run, max_links=args.max_links)


if __name__ == "__main__":
    main()
