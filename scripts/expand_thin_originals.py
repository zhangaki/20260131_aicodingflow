"""
Expand thin original articles (600-1000 words) to 1800+ words.
Prioritizes articles with GSC impressions.
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

# Articles to expand (original articles between 600-1000 words)
TARGET_SLUGS = [
    "generative-ai-pharma-2026",
    "legal-ai-bias-auditing-2026",
    "private-ai-hardware-2026",
    "local-llm-knowledge-base-2026",
    "ai-code-reviewer-bias-2026",
    "ai-model-fingerprinting-2026",
    "ai-verification-markers-2026",
    "clawdbot-evolution-2026",
    "dna-data-storage-for-ai-models",
    "hitl-agency-2026",
    "inside-moltbook-2026",
    "mobile-os-ai-2026",
    "on-device-quantization-2026",
    "prompt-injection-prevention-2026",
    "rag-latency-optimization-2026",
    "rare-disease-ai-diagnosis-2026",
    "red-teaming-llm-2026",
    "stochastic-ai-testing-2026",
    "token-cost-reduction-2026",
]


def expand_article(slug):
    filepath = BLOG_DIR / f"{slug}.md"
    if not filepath.exists():
        return False, "not found"

    with open(filepath) as f:
        content = f.read()

    if 'noindex: true' in content:
        return False, "noindex"

    word_count = len(content.split())
    if word_count >= 1500:
        return False, f"already {word_count}w"

    fm_match = re.match(r'^(---\n.*?\n---)\n', content, re.DOTALL)
    if not fm_match:
        return False, "no frontmatter"

    frontmatter = fm_match.group(1)
    old_body = content[fm_match.end():]

    title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
    title = title_match.group(1) if title_match else slug

    prompt = f"""Significantly expand and improve this article. Current content is only {word_count} words. Target 2000-2500 words.

TITLE: {title}

EXISTING CONTENT (rewrite and expand, keeping the same topic but going much deeper):
{old_body[:3000]}

EXPANSION REQUIREMENTS:
- Keep the same topic and perspective but add MUCH more depth
- Add practical examples, code snippets where relevant, real data points
- Add a comparison table if the topic involves tools or approaches
- Add specific numbers: costs, performance metrics, timelines
- Add a "Getting Started" or "How to Implement" section with actionable steps
- Add a FAQ section with 3-5 questions and answers
- Write like an expert practitioner, not a content marketer
- Be specific and opinionated - take clear positions
- NO filler phrases like "In today's rapidly evolving" or "As we navigate"

OUTPUT FORMAT:
- Output ONLY the article body in Markdown (NO frontmatter, NO title H1)
- Start with the first H2 section
- Use ## for main sections, ### for subsections
- Use proper markdown tables
- Use ```python or ```bash for code blocks
"""

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=6144,
                temperature=0.7,
            )
        )
        new_body = response.text.strip()
    except Exception as e:
        return False, f"api_error: {e}"

    new_wc = len(new_body.split())
    if new_wc < word_count:
        return False, f"shorter ({new_wc} < {word_count})"

    if 'updatedDate:' not in frontmatter:
        frontmatter = frontmatter.replace('\n---', '\nupdatedDate: Feb 10 2026\n---')

    full_content = f"{frontmatter}\n\n# {title}\n\n{new_body}\n"

    with open(filepath, "w") as f:
        f.write(full_content)

    return True, f"{word_count} -> {len(full_content.split())} words"


def main():
    print(f"=== Expanding {len(TARGET_SLUGS)} Thin Original Articles ===\n")
    success = 0
    for i, slug in enumerate(TARGET_SLUGS, 1):
        print(f"[{i}/{len(TARGET_SLUGS)}] {slug}...", end=" ", flush=True)
        ok, msg = expand_article(slug)
        if ok:
            print(f"OK ({msg})")
            success += 1
            time.sleep(1.5)
        else:
            print(f"SKIP ({msg})")

    print(f"\n=== Done: {success}/{len(TARGET_SLUGS)} articles expanded ===")


if __name__ == "__main__":
    main()
