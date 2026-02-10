"""
Batch expand thin PSEO comparison articles from ~540 words to 1200+ words.
Uses Gemini 2.0 Flash. Processes in batches with rate limiting.
"""
import os
import re
import sys
import time
import glob
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("Gemini_api_key") or os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: No Gemini API key found")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

BLOG_DIR = Path(__file__).parent.parent / "src" / "content" / "blog"
MAX_WORD_THRESHOLD = 800  # Only expand articles under this word count


def extract_tools_from_slug(slug):
    """Extract the two tool names from a vs slug like 'cursor-vs-github-copilot-2026'"""
    slug_clean = re.sub(r'-2026$', '', slug)
    parts = slug_clean.split('-vs-')
    if len(parts) == 2:
        tool_a = parts[0].replace('-', ' ').title()
        tool_b = parts[1].replace('-', ' ').title()
        return tool_a, tool_b
    return None, None


def expand_article(filepath):
    """Expand a single comparison article"""
    slug = filepath.stem

    with open(filepath) as f:
        content = f.read()

    word_count = len(content.split())
    if word_count >= MAX_WORD_THRESHOLD:
        return False, "skip_long"

    if 'noindex: true' in content:
        return False, "skip_noindex"

    # Extract frontmatter
    fm_match = re.match(r'^(---\n.*?\n---)\n', content, re.DOTALL)
    if not fm_match:
        return False, "no_frontmatter"

    frontmatter = fm_match.group(1)
    old_body = content[fm_match.end():]

    # Extract title from frontmatter
    title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
    title = title_match.group(1) if title_match else slug

    tool_a, tool_b = extract_tools_from_slug(slug)
    if not tool_a:
        return False, "bad_slug"

    prompt = f"""Rewrite and significantly expand this {tool_a} vs {tool_b} comparison article.
Current content is only {word_count} words. Target 1400-1800 words.

EXISTING CONTENT (keep the same comparison structure but go much deeper):
{old_body[:2000]}

EXPANSION REQUIREMENTS:
- Keep the numbered question format (5 questions) but add MUCH more detail to each answer
- Add a comparison table at the top with: Feature, {tool_a}, {tool_b} (at least 8 rows: pricing, key feature, best for, learning curve, context window/capability, IDE support, unique strength, weakness)
- Add real pricing data (monthly costs, free tier limits)
- Add specific technical details: version numbers, supported languages, integration methods
- Include a "Quick Verdict" section at the end with 3 bullet points: pick {tool_a} if..., pick {tool_b} if..., pick both if...
- Add a FAQ section with 3 questions and answers
- Write like a developer who has used both tools extensively
- Be specific and opinionated - don't just say "both are great"
- NO filler phrases like "In today's rapidly evolving" or "As we navigate"

OUTPUT FORMAT:
- Output ONLY the article body in Markdown (NO frontmatter, NO title H1)
- Start with the comparison table
- Use ## for main sections, ### for subsections
- End with Quick Verdict and FAQ
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=4096,
                temperature=0.7,
            )
        )
        new_body = response.text.strip()
    except Exception as e:
        return False, f"api_error: {e}"

    new_word_count = len(new_body.split())
    if new_word_count < word_count:
        return False, f"shorter ({new_word_count} < {word_count})"

    # Add updatedDate to frontmatter if not present
    if 'updatedDate:' not in frontmatter:
        frontmatter = frontmatter.replace('\n---', '\nupdatedDate: Feb 10 2026\n---')
    else:
        frontmatter = re.sub(r'updatedDate:.*', 'updatedDate: Feb 10 2026', frontmatter)

    full_content = f"{frontmatter}\n\n# {title}\n\n{new_body}\n"

    with open(filepath, "w") as f:
        f.write(full_content)

    return True, f"{word_count} -> {len(full_content.split())} words"


def main():
    # Find all vs comparison articles
    vs_files = sorted(BLOG_DIR.glob("*-vs-*-2026.md"))
    thin_files = []

    for f in vs_files:
        with open(f) as fh:
            wc = len(fh.read().split())
        if wc < MAX_WORD_THRESHOLD:
            thin_files.append(f)

    print(f"=== PSEO Article Expansion ===")
    print(f"Total vs articles: {len(vs_files)}")
    print(f"Under {MAX_WORD_THRESHOLD} words: {len(thin_files)}")
    print()

    success = 0
    errors = 0
    for i, filepath in enumerate(thin_files, 1):
        slug = filepath.stem
        print(f"[{i}/{len(thin_files)}] {slug}...", end=" ", flush=True)

        ok, msg = expand_article(filepath)
        if ok:
            print(f"OK ({msg})")
            success += 1
        else:
            print(f"SKIP ({msg})")
            if "api_error" in msg:
                errors += 1
                if errors >= 3:
                    print("\nToo many API errors, stopping.")
                    break

        # Rate limit: 1.5 seconds between requests
        if ok:
            time.sleep(1.5)

    print(f"\n=== Done: {success}/{len(thin_files)} articles expanded ===")


if __name__ == "__main__":
    main()
