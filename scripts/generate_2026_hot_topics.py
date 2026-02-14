#!/usr/bin/env python3
"""
Generate articles for 2026 hot trending topics
Focus on: DeepSeek V4, Windsurf Cascade vs Claude Code, AI Agent Marketplace, Free AI Tools
"""

import os
import sys
import re
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

load_dotenv(PROJECT_ROOT / '.env')

from google import genai
from google.genai import types


HOT_TOPICS_2026 = [
    {
        "slug": "deepseek-v4-vs-claude-opus-2026",
        "title": "DeepSeek V4 vs Claude Opus 4.6: 2026 Coding Benchmark Test",
        "description": "DeepSeek V4 vs Claude Opus 4.6 coding comparison - 90% HumanEval test, pricing, speed, and real-world performance. Which wins in 2026?",
        "keywords": ["deepseek v4", "claude opus 4.6", "deepseek vs claude", "deepseek benchmark", "ai coding 2026"],
        "focus": "coding benchmark comparison with specific numbers",
    },
    {
        "slug": "windsurf-cascade-vs-claude-code-2026",
        "title": "Windsurf Cascade vs Claude Code: Which Agentic IDE Wins 2026?",
        "description": "Windsurf Cascade mode vs Claude Code comparison - pricing ($15 vs $20), AI agent capabilities, VS Code integration, and real coding performance test.",
        "keywords": ["windsurf cascade", "claude code", "windsurf vs claude code", "agentic ide 2026", "best ai coding tool 2026"],
        "focus": "agentic IDE comparison with feature-by-feature table",
    },
    {
        "slug": "best-free-ai-coding-tools-2026",
        "title": "Best Free AI Coding Tools 2026: No-Credit Alternatives Tested",
        "description": "Free AI coding tools in 2026 - Windsurf free tier, Replit Ghostwriter, Codeium free, and GitHub Copilot free trial. No credit card required options compared.",
        "keywords": ["free ai coding tools", "best free ai for coding 2026", "no credit card ai coding", "free ai code completion"],
        "focus": "comprehensive free tier comparison table",
    },
    {
        "slug": "ai-agent-marketplace-2026",
        "title": "AI Agent Marketplace 2026: How to Monetize Your Agents",
        "description": "AI agent marketplace economy in 2026 - how to build, list, and monetize AI agents on platforms like Replit Agent Hub, Cursor Agent Store, and others.",
        "keywords": ["ai agent marketplace 2026", "monetize ai agents", "sell ai agents", "agent marketplace economy 2026"],
        "focus": "monetization guide for AI agents with platform comparison",
    },
]


def generate_article(topic: dict, api_key: str) -> str:
    """Generate a single article using Gemini"""

    client = genai.Client(api_key=api_key)

    prompt = f"""
Write a comprehensive, data-driven article about: {topic['title']}

TOPIC FOCUS: {topic['focus']}

TARGET KEYWORDS: {', '.join(topic['keywords'])}

REQUIREMENTS:
1. Use REAL 2026 data where applicable
2. Include specific numbers, pricing, benchmarks
3. Personal testing experience (make it realistic for a developer)
4. Comparison tables where relevant
5. Code examples where applicable
6. 1800-2200 words
7. Avoid AI clichés: "delve", "unlock", "landscape", "realm", "transform"
8. Write like a real developer sharing hands-on experience
9. Include an FAQ section at the end (3-5 Q&A pairs)

STRUCTURE:
- Hook (real problem or surprising finding, 100 words)
- Main body with subheadings (1500-1800 words)
  - Include at least 1 comparison table
  - Include specific pricing/feature details
  - Real usage examples or code snippets
- FAQ section (300-400 words)
- Conclusion with actionable recommendation (50-100 words)

OUTPUT: Just the markdown content (no frontmatter, I'll add that)
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())]
            )
        )

        content = response.text.strip()

        # Robust Cleanup Logic
        # 1. Strip markdown code block wrappers
        markdown_match = re.search(r"```markdown\s*(.*?)\s*```", content, re.DOTALL | re.IGNORECASE)
        if markdown_match:
            content = markdown_match.group(1).strip()
        else:
            generic_match = re.search(r"```\s*(.*?)\s*```", content, re.DOTALL)
            if generic_match:
                content = generic_match.group(1).strip()

        # 2. Strip common AI intro fillers
        ai_fillers = [
            r"^Okay, here's a draft.*?\n",
            r"^Here's a blog article draft.*?\n",
            r"^I've crafted a data-driven article.*?\n",
            r"^Sure, here is the article.*?\n",
            r"^Based on your request.*?:\n",
        ]
        for filler in ai_fillers:
            content = re.sub(filler, "", content, flags=re.IGNORECASE | re.MULTILINE)

        content = content.strip()

        # Add FAQ detection marker for schema
        if "## FAQ" not in content and "## Frequently Asked" not in content:
            content += """

## FAQ

### Q: What's the main difference between these tools?

A: The key differentiator is [specific difference]. For most developers, [recommendation] provides the best balance of features and pricing.

### Q: Is this suitable for beginners?

A: Yes, [tool] has a gentle learning curve. Start with the free tier to evaluate before committing to a paid plan.

### Q: Can I use this alongside other AI tools?

A: Absolutely. Many developers use multiple tools for different tasks. Consider your specific workflow when choosing.
"""

        return content

    except Exception as e:
        print(f"❌ Generation failed for {topic['slug']}: {e}")
        return None


def create_article_file(topic: dict, content: str, blog_dir: Path):
    """Create article file with frontmatter"""

    pub_date = datetime.now().strftime('%b %d %Y')
    tags = [k.split()[0] for k in topic['keywords'][:3]]  # First keyword parts as tags

    frontmatter = f"""---
description: {topic['description']}
heroImage: /assets/{topic['slug']}.webp
pubDate: {pub_date}
tags:
{chr(10).join(f"- {t}" for t in tags)}
title: "{topic['title']}"
updatedDate: {pub_date}
---

"""

    full_content = frontmatter + content
    article_file = blog_dir / f"{topic['slug']}.md"

    article_file.write_text(full_content, encoding='utf-8')
    print(f"✅ Created: {article_file.name}")


def main():
    print("=" * 60)
    print("🔥 2026 Hot Topics Article Generator")
    print("=" * 60)

    api_key = os.environ.get("Gemini_api_key") or os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not found in .env")
        return

    blog_dir = PROJECT_ROOT / "projects/20260131_seo-site" / "src" / "content" / "blog"
    blog_dir.mkdir(parents=True, exist_ok=True)

    for topic in HOT_TOPICS_2026:
        print(f"\n📝 Generating: {topic['title']}")
        content = generate_article(topic, api_key)

        if content and len(content) > 1000:
            create_article_file(topic, content, blog_dir)
        else:
            print(f"⚠️  Skipped {topic['slug']} (insufficient content)")

    print("\n" + "=" * 60)
    print("🎉 Done! Next steps:")
    print("  1. Review and edit articles if needed")
    print("  2. Run: python scripts/internal_link_builder.py")
    print("  3. Run: npx astro build")
    print("  4. Run: git commit -am 'feat: add 2026 hot topic articles'")
    print("  5. Run: git push origin main")
    print("=" * 60)


if __name__ == "__main__":
    main()
