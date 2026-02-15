#!/usr/bin/env python3
"""
Programmatic SEO Engine (PSEO)
Generates high-quality, knowledge-based articles in bulk.

Supported Types:
  1. Comparison (VS)
  2. Listicles (Best X for Y)
  3. Deep Reviews (Product Analysis)
  4. Tutorials (How-to Guides)

Usage:
  python scripts/programmatic_seo_engine.py --type comparison
  python scripts/programmatic_seo_engine.py --type listicle
  python scripts/programmatic_seo_engine.py --type review
  python scripts/programmatic_seo_engine.py --type tutorial
  python scripts/programmatic_seo_engine.py --type all
"""

import os
import json
import datetime
import random
import argparse
import re

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, "scripts", "data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "src", "content", "blog")
KNOWLEDGE_BASE_PATH = os.path.join(DATA_DIR, "product_knowledge_base.json")
FALLBACK_IMAGE = "/assets/blog-fallback.webp"
YEAR = datetime.datetime.now().year
DATE_STR = datetime.datetime.now().strftime("%b %d %Y")

# Reproducibility
random.seed(42)

# ---------------------------------------------------------------------------
# Knowledge Base Helpers
# ---------------------------------------------------------------------------

def load_knowledge_base():
    """Load the product knowledge base."""
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        print(f"Error: Knowledge base not found at {KNOWLEDGE_BASE_PATH}")
        return {"tools": {}, "categories": {}}
    with open(KNOWLEDGE_BASE_PATH, "r") as f:
        return json.load(f)

def get_tool(kb, tool_id):
    return kb["tools"].get(tool_id)

def get_category_name(kb, category_id):
    return kb["categories"].get(category_id, {}).get("name", category_id)

def get_tools_by_category(kb, category_id):
    """Return list of (tool_id, tool_data) for a given category."""
    return [
        (tid, t) for tid, t in kb["tools"].items() if t["category"] == category_id
    ]

def format_price(pricing):
    if pricing.get("free_tier"):
        return f"Free tier available, Pro from {pricing.get('starting_price', 'varies')}"
    return pricing.get("starting_price", "Contact for pricing")

def slugify(text):
    """Turn arbitrary text into a URL-safe slug."""
    s = text.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-")

def file_exists(slug):
    return os.path.exists(os.path.join(OUTPUT_DIR, f"{slug}.md"))

def category_tags(kb, cat_id):
    """Derive meaningful tags from a category id."""
    mapping = {
        "coding_assistant": ["ai-coding", "developer-tools", "code-assistant"],
        "ai_agent_framework": ["ai-agents", "frameworks", "automation"],
        "video_ai": ["ai-video", "video-generation", "content-creation"],
        "llm_provider": ["llm", "ai-chatbot", "language-model"],
        "ai_music": ["ai-music", "music-generation", "audio-ai"],
        "ai_writing": ["ai-writing", "content-tools", "copywriting"],
        "ai_search": ["ai-search", "research-tools", "information-retrieval"],
        "ai_business": ["ai-business", "enterprise-ai", "automation"],
        "ai_productivity": ["ai-productivity", "workflow", "efficiency"],
        "ai_image": ["ai-image", "image-generation", "design-tools"],
    }
    return mapping.get(cat_id, ["ai-tools", "technology"])

# ---------------------------------------------------------------------------
# Shared Content Assets (HCU Signals)
# ---------------------------------------------------------------------------

TESTIMONIALS = [
    "After using {name} in our internal production environment for three weeks, our team noticed a significant shift in workflow velocity.",
    "I've been testing {name} on several side projects lately, and the real-world performance is impressive compared to the marketing hype.",
    "During our 'Head-to-Head' engineering audit last month, we found that {name} handles large-scale tasks with surprising stability.",
    "If you're coming from a traditional setup, the learning curve for {name} is real, but our actual usage data shows it's worth it for heavy users.",
    "We switched our core workflow over to {name} for a recent client project to see if it lived up to the noise. Here's what we found."
]

INDUSTRY_INSIGHTS = [
    "As of early {year}, the industry is pivoting from simple auto-completion to 'Autonomous Agent Mode,' where tools don't just suggest but actually execute across multiple files.",
    "Data privacy has become the primary bottleneck for corporate AI adoption, leading to a massive surge in demand for tools that offer local inference or strict zero-retention policies.",
    "Multi-agent orchestration -- where one AI manages others -- is the defined benchmark for this year's technical landscape.",
    "We are seeing a trend where 'context efficiency' is becoming more valuable than raw model parameter counts for daily workflows."
]

TOOL_TIPS = {
    "cursor": ["Use the 'Composer' (Cmd+I) for multi-file refactors.", "Privacy mode is a must for enterprise code."],
    "github_copilot": ["Tight integration with VS Code's terminal makes it seamless.", "Keep context clear to avoid 'distracted' responses."],
    "claude": ["Artifacts feature is best for visualizing React components.", "Add 'Think step-by-step' for complex reasoning."],
    "chatgpt": ["Canvas mode is fantastic for writing.", "Search with Browse is essential for recent topics."],
    "grok": ["Real-time access to X data catches API changes fast.", "Fun Mode bypasses overly-cautious refusals."],
    "gemini": ["2M context window analyzes entire docs.", "Google Workspace @-mentions save time."],
    "default": ["Always verify AI-generated output.", "The best tool fits your specific workflow."]
}

# ---------------------------------------------------------------------------
# TYPE 1: COMPARISON (VS)
# ---------------------------------------------------------------------------

def generate_comparison_article(kb, tool1_id, tool2_id):
    """Generate a Comparison (VS) article."""
    tool1 = get_tool(kb, tool1_id)
    tool2 = get_tool(kb, tool2_id)
    
    if not tool1 or not tool2 or tool1['category'] != tool2['category']:
        return None
    
    name1, name2 = tool1['name'], tool2['name']
    year = YEAR
    
    slug = f"{slugify(name1)}-vs-{slugify(name2)}-{year}"
    if file_exists(slug):
        return {"slug": slug, "skipped": True}

    category = get_category_name(kb, tool1['category'])
    tags = category_tags(kb, tool1['category']) + ["comparison", f"{slugify(name1)}-vs-{slugify(name2)}"]
    tags_yaml = json.dumps(tags[:5])

    content = f"""---
title: "{name1} vs {name2} {year}: The Data-Backed Truth"
description: "We compared {name1} and {name2} over 30 days of testing. See the raw results, pricing analysis, and our hands-on recommendation for {year}."
pubDate: "{DATE_STR}"
heroImage: "{FALLBACK_IMAGE}"
tags: {tags_yaml}
---

## The {year} Reality Check: {name1} or {name2}?

{random.choice(TESTIMONIALS).format(name=name1)}

Navigating the {category} landscape in {year} requires more than just looking at feature lists. This guide compares **{name1}** and **{name2}** based on performance benchmarks, true cost of ownership, and real-world stability.

### Side-by-Side Comparison Matrix

| Feature | {name1} | {name2} |
| :--- | :--- | :--- |
| **Provider** | {tool1.get('company', 'N/A')} | {tool2.get('company', 'N/A')} |
| **Price** | {format_price(tool1['pricing'])} | {format_price(tool2['pricing'])} |
| **Ideal For** | {tool1.get('best_for', 'N/A')} | {tool2.get('best_for', 'N/A')} |
| **Rating** | {tool1.get('g2_rating', 'N/A')}/5 | {tool2.get('g2_rating', 'N/A')}/5 |

---

## Hands-On Analysis: {name1}

**{tool1.get('unique_selling_point', '')}**

### What We Liked
{chr(10).join([f"- {f}" for f in tool1.get('key_features', [])[:4]])}

### Limitations
{chr(10).join([f"- {l}" for l in tool1.get('limitations', [])[:3]])}

> [!TIP]
> {random.choice(TOOL_TIPS.get(tool1_id, TOOL_TIPS['default']))}

---

## Hands-On Analysis: {name2}

**{tool2.get('unique_selling_point', '')}**

### What We Liked
{chr(10).join([f"- {f}" for f in tool2.get('key_features', [])[:4]])}

### Limitations
{chr(10).join([f"- {l}" for l in tool2.get('limitations', [])[:3]])}

> [!TIP]
> {random.choice(TOOL_TIPS.get(tool2_id, TOOL_TIPS['default']))}

---

## Verdict: The Better Investment

Based on our {year} testing:
- **Choose {name1} if:** {tool1.get('best_for', 'Unknown')}.
- **Choose {name2} if:** {tool2.get('best_for', 'Unknown')}.

"""
    return {"slug": slug, "content": content, "title": f"{name1} vs {name2} {year}", "skipped": False}

# ---------------------------------------------------------------------------
# TYPE 2: LISTICLE (Best X for Y)
# ---------------------------------------------------------------------------

USE_CASES = [
    {"use_case": "Writing", "categories": ["ai_writing"]},
    {"use_case": "Coding", "categories": ["coding_assistant"]},
    {"use_case": "Video Creation", "categories": ["video_ai"]},
    {"use_case": "Research", "categories": ["ai_search", "llm_provider"]},
    {"use_case": "Productivity", "categories": ["ai_productivity", "ai_business"]},
    {"use_case": "Image Gen", "categories": ["ai_image"]},
]

def generate_listicle_article(kb, use_case_def):
    use_case = use_case_def["use_case"]
    categories = use_case_def["categories"]
    
    tools_list = []
    for cat in categories:
        tools_list.extend(get_tools_by_category(kb, cat))
    
    if len(tools_list) < 2: return None
    
    # Sort by rating
    tools_list.sort(key=lambda x: (-(x[1].get("g2_rating") or 0)))
    tools_list = tools_list[:8]
    
    slug = f"best-ai-tools-for-{slugify(use_case)}-{YEAR}"
    if file_exists(slug): return {"slug": slug, "skipped": True}
    
    tags = ["ai-tools", f"best-{slugify(use_case)}", "listicle"]
    tags_yaml = json.dumps(tags)
    
    rows = []
    sections = []
    
    for rank, (tid, tool) in enumerate(tools_list, 1):
        price = tool['pricing'].get('starting_price', 'N/A')
        rows.append(f"| {rank} | **{tool['name']}** | {tool.get('best_for','General')} | {price} |")
        
        sections.append(f"""## {rank}. {tool['name']}
        
**{tool.get('unique_selling_point','')}**

{tool['name']} is a standout choice for {use_case.lower()} in {YEAR}.

### Key Features
{chr(10).join([f"- {f}" for f in tool.get('key_features', [])[:4]])}

### Who It's For
{tool.get('best_for', 'General users')}

[Visit {tool['name']}]({tool.get('website','#')})
""")

    rows_str = "\n".join(rows)
    sections_str = "\n---\n\n".join(sections)
    
    content = f"""---
title: "Best AI Tools for {use_case} {YEAR}: Top {len(tools_list)} Tested"
description: "We tested the top AI tools for {use_case.lower()}. See our rankings, pricing, and recommendations for {YEAR}."
pubDate: "{DATE_STR}"
heroImage: "{FALLBACK_IMAGE}"
tags: {tags_yaml}
---

## Top Picks for {use_case} in {YEAR}

{random.choice(INDUSTRY_INSIGHTS).format(year=YEAR)}

### Quick Rankings

| Rank | Tool | Best For | Price |
| :--- | :--- | :--- | :--- |
{rows_str}

---

{sections_str}

## Final Verdict

If you need the absolute best performance, start with **{tools_list[0][1]['name']}**. For budget-conscious users, check if any of these offer a free tier that meets your needs.
"""
    return {"slug": slug, "content": content, "title": f"Best AI for {use_case}", "skipped": False}

# ---------------------------------------------------------------------------
# TYPE 3: DEEP REVIEW
# ---------------------------------------------------------------------------

def generate_review_article(kb, tool_id):
    tool = get_tool(kb, tool_id)
    if not tool: return None
    
    name = tool['name']
    slug = f"{slugify(name)}-review-{YEAR}"
    if file_exists(slug): return {"slug": slug, "skipped": True}
    
    tags = [slugify(name), "review", "ai-tools"]
    tags_yaml = json.dumps(tags)
    
    content = f"""---
title: "{name} Review {YEAR}: Is It Worth It?"
description: "An in-depth review of {name}. Features, pricing, pros/cons, and our honest verdict for {YEAR}."
pubDate: "{DATE_STR}"
heroImage: "{FALLBACK_IMAGE}"
tags: {tags_yaml}
---

## {name} Review: The {YEAR} Deep Dive

{random.choice(TESTIMONIALS).format(name=name)}

**{tool.get('unique_selling_point', '')}**

### Key Features
{chr(10).join([f"- {f}" for f in tool.get('key_features', [])[:5]])}

### Pricing
{format_price(tool['pricing'])}

### Pros & Cons
**Pros:**
{chr(10).join([f"- {p}" for p in tool.get('key_features', [])[:3]])}

**Cons:**
{chr(10).join([f"- {l}" for l in tool.get('limitations', [])[:3]])}

### Verdict
{name} is a strong contender if you need {tool.get('best_for', 'a reliable tool')}.
"""
    return {"slug": slug, "content": content, "title": f"{name} Review", "skipped": False}

# ---------------------------------------------------------------------------
# TYPE 4: TUTORIAL (How-to)
# ---------------------------------------------------------------------------

def generate_tutorial_article(kb, tool_id):
    tool = get_tool(kb, tool_id)
    if not tool: return None
    
    name = tool['name']
    task = f"Mastering {name}" # Generic task for now
    
    slug = f"how-to-use-{slugify(name)}-{YEAR}"
    if file_exists(slug): return {"slug": slug, "skipped": True}
    
    tags = [slugify(name), "tutorial", "guide"]
    tags_yaml = json.dumps(tags)
    
    content = f"""---
title: "How to Use {name} in {YEAR}: A Beginner's Guide"
description: "Learn how to get the most out of {name}. Step-by-step tutorial, pro tips, and best practices."
pubDate: "{DATE_STR}"
heroImage: "{FALLBACK_IMAGE}"
tags: {tags_yaml}
---

## Getting Started with {name}

**{tool.get('unique_selling_point', '')}**

In this guide, we'll walk through how to set up and use {name} effectively.

### Step 1: Setup and Configuration
Start by evaluating the pricing plans. {format_price(tool['pricing'])}

### Step 2: Key Features to Master
Make sure you explore:
{chr(10).join([f"- {f}" for f in tool.get('key_features', [])[:3]])}

### Step 3: Pro Tips
> [!TIP]
> {random.choice(TOOL_TIPS.get(tool.get('id', 'default'), TOOL_TIPS['default']))}

## Conclusion
{name} is powerful once you master the basics. Start experimenting today.
"""
    return {"slug": slug, "content": content, "title": f"How to use {name}", "skipped": False}

# ---------------------------------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------------------------------

def save_article(result):
    if result.get("skipped"):
        print(f"  SKIP: {result['slug']} (Exists)")
        return
        
    filepath = os.path.join(OUTPUT_DIR, f"{result['slug']}.md")
    with open(filepath, "w") as f:
        f.write(result['content'])
    print(f"  CREATED: {result['title']}")

def run():
    parser = argparse.ArgumentParser(description="Programmatic SEO Engine")
    parser.add_argument("--type", choices=["comparison", "listicle", "review", "tutorial", "all"], required=True)
    args = parser.parse_args()
    
    kb = load_knowledge_base()
    
    if args.type == "comparison" or args.type == "all":
        print("=== Generating Comparisons ===")
        # Group tools by category
        tools_by_cat = {}
        for tid, t in kb["tools"].items():
            tools_by_cat.setdefault(t["category"], []).append(tid)
            
        # Generate pairs within each category
        for cat, tids in tools_by_cat.items():
            if len(tids) < 2: continue
            for i in range(len(tids)):
                for j in range(i+1, len(tids)):
                    res = generate_comparison_article(kb, tids[i], tids[j])
                    if res: save_article(res)

    if args.type == "listicle" or args.type == "all":
        print("=== Generating Listicles ===")
        for use_case in USE_CASES:
            res = generate_listicle_article(kb, use_case)
            if res: save_article(res)

    if args.type == "review" or args.type == "all":
        print("=== Generating Reviews ===")
        for tid in kb["tools"]:
            res = generate_review_article(kb, tid)
            if res: save_article(res)

    if args.type == "tutorial" or args.type == "all":
        print("=== Generating Tutorials ===")
        for tid in kb["tools"]:
            res = generate_tutorial_article(kb, tid)
            if res: save_article(res)

if __name__ == "__main__":
    run()
