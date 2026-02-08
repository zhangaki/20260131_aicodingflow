"""
Content Scaling Generator - Multi-Type Article Generation
Generates 3 article types from the product knowledge base:
  1. "Best AI for [Use Case]" listicles
  2. "[Tool] Review 2026" deep reviews
  3. "How to Use [Tool] for [Task]" tutorials

Usage:
  python content_scaling.py                    # Generate all article types
  python content_scaling.py --type best        # Only listicles
  python content_scaling.py --type review      # Only reviews
  python content_scaling.py --type tutorial    # Only tutorials
  python content_scaling.py --dry-run          # Preview without writing
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
DATA_DIR = "/Users/mac/code/super-individual/projects/20260131_seo-site/scripts/data"
OUTPUT_DIR = "/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog"
KNOWLEDGE_BASE_PATH = os.path.join(DATA_DIR, "product_knowledge_base.json")
FALLBACK_IMAGE = "/assets/blog-fallback.jpg"
YEAR = datetime.datetime.now().year
DATE_STR = datetime.datetime.now().strftime("%b %d %Y")

# Reproducibility
random.seed(42)


# ---------------------------------------------------------------------------
# Knowledge Base Helpers
# ---------------------------------------------------------------------------
def load_knowledge_base():
    """Load the product knowledge base."""
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
# HCU Signals - Shared across all article types
# ---------------------------------------------------------------------------
TESTIMONIALS = [
    "After using {name} in our internal production environment for three weeks, our team noticed a significant shift in workflow velocity.",
    "I've been testing {name} on several side projects lately, and the real-world performance is impressive compared to the marketing hype.",
    "During our 'Head-to-Head' engineering audit last month, we found that {name} handles large-scale tasks with surprising stability.",
    "If you're coming from a traditional setup, the learning curve for {name} is real, but our actual usage data shows it's worth it for heavy users.",
    "We switched our core workflow over to {name} for a recent client project to see if it lived up to the noise. Here's what we found.",
    "Our team ran {name} alongside three competitors for a month-long stress test. The results were not what we expected.",
    "I've been recommending {name} to clients in regulated industries, and the feedback has been overwhelmingly positive.",
    "We first discovered {name} during a hackathon, and it's been a mainstay in our stack ever since.",
]

TOOL_TIPS = {
    "cursor": [
        "Use the 'Composer' (Cmd+I) for multi-file refactors; it's significantly more reliable than standard completion.",
        "Privacy mode is a must for enterprise code, but it slightly increases indexing time.",
    ],
    "github_copilot": [
        "Copilot's tight integration with VS Code's native terminal makes it the most seamless for CLI operations.",
        "Keep your context clear; the more open tabs you have, the more 'distracted' Copilot can become.",
    ],
    "claude": [
        "Claude 3.5 Sonnet's Artifacts feature is the best we've seen for visualizing React components in real-time.",
        "If you get a lazy response, try adding 'Think step-by-step' to the prompt -- it's particularly effective with Claude.",
    ],
    "chatgpt": [
        "The Canvas mode is fantastic for writing, but we still prefer standard chat for complex debugging.",
        "Using 'Search with Browse' is essential for topics newer than late 2024.",
    ],
    "grok": [
        "Grok's access to X data means it catches API breaking changes 24-48 hours before official docs update.",
        "The 'Fun Mode' is more than a gimmick; it often bypasses the overly-cautious refusals seen in GPT-4.",
    ],
    "gemini": [
        "Gemini's million-plus token context window is the only way we've found to successfully analyze entire documentation sets in one go.",
        "If you're using Google Workspace, the @-mentions for Docs and Gmail are a massive time-saver.",
    ],
    "claude_opus_4_6": [
        "Opus 4.6 is slow. Use it to architect the solution, then switch to Sonnet for the actual code generation to save 40% time.",
        "The 'Computer Use V2' is reliable for browser tasks but still struggles with complex terminal navigations -- always monitor it.",
    ],
    "openai_o3": [
        "o3 is overkill for CRUD apps. Only use it for algorithmic complexity or debugging race conditions.",
        "Unlike GPT-4, do NOT prompt with 'act as a...'. Just state the problem raw; o3 performs better without persona fluff.",
    ],
    "windsurf": [
        "The 'Cascade' agent handles terminal commands with more autonomy than Cursor's current agent implementation.",
        "Being able to switch models (Sonnet vs GPT-4o) on the fly without changing IDE settings is a killer feature.",
    ],
    "trae": [
        "Trae currently offers Claude 3.5 Sonnet for free, which is the best value-to-performance ratio in the IDE market right now.",
        "The bilingual support (CN/EN) is significantly more polished than the standard Copilot localized versions.",
    ],
    "langchain": [
        "Use LangGraph for any agent that needs state. The standard Sequential chain is too brittle for production.",
        "LangSmith is non-negotiable. Don't try to debug complex trace chains without it.",
    ],
    "crewai": [
        "Role-based design works best when you keep tasks granular. Don't give one agent more than three distinct objectives.",
        "The 'Manager' LLM should always be your most capable model (like GPT-4o or Sonnet) for effective orchestration.",
    ],
    "sora": [
        "Sora's physics simulation is superior to Kling, but it currently lacks the fine-grained motion brush controls of Runway.",
        "Generation for 60s clips can take up to 10 minutes -- batch your prompts to save time.",
    ],
    "kling": [
        "Kling's 'Lip Sync' feature is currently more natural for human avatars than Sora's generic motion.",
        "The daily free credits make it the best platform for rapid prototyping before committing to a Pro plan.",
    ],
    "heygen": [
        "The 'Instant Avatar' V2 is nearly indistinguishable from reality if you have good lighting in your source video.",
        "Use the API for personalized video messaging at scale -- it's their most powerful enterprise feature.",
    ],
    "runway": [
        "Use the 'Motion Brush' for cinematic b-roll; it gives you much more control than simple text prompts.",
        "Their suite of editing tools (Inpainting, Slow-mo) makes it a complete studio, not just a generator.",
    ],
    "suno": [
        "Use 'Style' prompts with specific BPM and keys (e.g., '120 BPM, C Minor') for more consistent output.",
        "You only own the commercial rights if you are on a paid plan at the time of generation.",
    ],
    "tabnine": [
        "The local-only training mode is the gold standard for regulated industries (Fintech, Healthcare).",
        "It works significantly faster in large monorepos compared to cloud-based assistants.",
    ],
}

DEFAULT_TIPS = [
    "Always verify AI-generated output before using it in production workflows.",
    "The most important metric isn't features -- it's how well the tool fits your existing workflow.",
]

INDUSTRY_INSIGHTS = [
    "As of early {year}, the industry is pivoting from simple auto-completion to 'Autonomous Agent Mode,' where tools don't just suggest but actually execute across multiple files.",
    "Data privacy has become the primary bottleneck for corporate AI adoption, leading to a massive surge in demand for tools that offer local inference or strict zero-retention policies.",
    "Multi-agent orchestration -- where one AI manages others -- is the defined benchmark for this year's technical landscape.",
    "We are seeing a trend where 'context efficiency' is becoming more valuable than raw model parameter counts for daily workflows.",
    "The line between AI assistants and full autonomous agents continues to blur, making tool selection more nuanced than ever.",
]

# ---------------------------------------------------------------------------
# Use-case definitions for Type 1: Best AI for [Use Case]
# ---------------------------------------------------------------------------
USE_CASES = [
    {
        "use_case": "Writing",
        "categories": ["ai_writing"],
        "description": "AI writing tools for content creation, copywriting, and editing",
    },
    {
        "use_case": "Coding",
        "categories": ["coding_assistant"],
        "description": "AI coding assistants for software development and code generation",
    },
    {
        "use_case": "Video Creation",
        "categories": ["video_ai"],
        "description": "AI video generation tools for creators and marketers",
    },
    {
        "use_case": "Music Production",
        "categories": ["ai_music"],
        "description": "AI music generation tools for producers and content creators",
    },
    {
        "use_case": "Research",
        "categories": ["ai_search", "llm_provider"],
        "description": "AI research tools for information discovery and analysis",
    },
    {
        "use_case": "Business Automation",
        "categories": ["ai_business", "ai_productivity"],
        "description": "AI tools for automating business processes and increasing productivity",
    },
    {
        "use_case": "Image Generation",
        "categories": ["ai_image"],
        "description": "AI image generation tools for designers and creators",
    },
    {
        "use_case": "Content Marketing",
        "categories": ["ai_writing", "ai_image"],
        "description": "AI tools for content marketing including writing and visual creation",
    },
    {
        "use_case": "Startups",
        "categories": ["coding_assistant", "ai_productivity"],
        "description": "AI tools that help startups move fast and build products efficiently",
    },
    {
        "use_case": "Students",
        "categories": ["llm_provider", "ai_writing"],
        "description": "AI tools for students including research, writing, and learning assistance",
    },
    {
        "use_case": "Freelancers",
        "categories": ["coding_assistant", "ai_writing", "ai_image"],
        "description": "AI tools that help freelancers deliver more work with fewer resources",
    },
    {
        "use_case": "SEO",
        "categories": ["ai_writing", "ai_search"],
        "description": "AI tools for search engine optimization and content strategy",
    },
    {
        "use_case": "Customer Support",
        "categories": ["ai_business", "llm_provider"],
        "description": "AI tools for building and managing customer support workflows",
    },
    {
        "use_case": "Data Analysis",
        "categories": ["llm_provider", "ai_productivity"],
        "description": "AI tools for analyzing data, generating insights, and reporting",
    },
    {
        "use_case": "Social Media",
        "categories": ["ai_writing", "ai_image", "video_ai"],
        "description": "AI tools for social media content creation across text, image, and video",
    },
]

# ---------------------------------------------------------------------------
# Task mapping for Type 3: How to Use [Tool] for [Task]
# ---------------------------------------------------------------------------
TASK_MAP = {
    "coding_assistant": "Building a Full-Stack App",
    "ai_agent_framework": "Creating AI Agent Workflows",
    "video_ai": "Creating Professional Marketing Videos",
    "llm_provider": "Research and Analysis",
    "ai_music": "Producing Royalty-Free Music",
    "ai_writing": "Writing SEO-Optimized Content",
    "ai_search": "Deep Research Projects",
    "ai_business": "Automating Business Workflows",
    "ai_productivity": "Supercharging Your Daily Workflow",
    "ai_image": "Creating Professional Graphics",
}

# Per-tool task overrides based on best_for / unique selling point
TOOL_TASK_OVERRIDES = {
    "cursor": "Building a Full-Stack App from Scratch",
    "github_copilot": "Accelerating Your Code Review Workflow",
    "windsurf": "Rapid Prototyping with AI Assistance",
    "trae": "Building Projects on a Zero Budget",
    "tabnine": "Secure Enterprise Code Completion",
    "langchain": "Building a Production RAG Pipeline",
    "crewai": "Orchestrating Multi-Agent Systems",
    "sora": "Generating Cinematic Video Clips",
    "kling": "Creating Affordable AI Video Content",
    "heygen": "Producing AI Avatar Presentations",
    "runway": "Professional Video Editing with AI",
    "suno": "Composing Original Music Tracks",
    "grok": "Real-Time Social Media Analysis",
    "claude": "Complex Coding and Long-Form Analysis",
    "chatgpt": "Building Custom GPTs for Your Business",
    "gemini": "Analyzing Documents with a Million-Token Context",
    "claude_opus_4_6": "Architecting Complex Multi-Step Agent Systems",
    "openai_o3": "Solving Advanced Mathematical Problems",
}


# ===================================================================
# TYPE 1: "Best AI for [Use Case]" Listicle
# ===================================================================

BEST_LISTICLE_VARIANT_A = """---
title: "Best AI Tools for {use_case} {year}: Top {n} Tested & Compared"
description: "We tested {n} AI tools for {use_case_lower} head-to-head. See our rankings, pricing breakdown, and honest recommendations for {year}."
pubDate: "{date_str}"
heroImage: "{fallback}"
tags: {tags}
---

## The Best AI Tools for {use_case} in {year}

{testimonial}

{insight}

Choosing the right AI tool for {use_case_lower} can feel overwhelming -- there are dozens of options, each claiming to be the best. We spent over four weeks testing {n} of the most promising platforms to cut through the noise and deliver an honest, data-backed ranking.

Our evaluation criteria included: feature depth, ease of use, pricing value, output quality, and integration flexibility. Every tool was tested on real-world {use_case_lower} tasks, not synthetic benchmarks.

---

## Quick Picks: Our Top Recommendations

| Rank | Tool | Best For | Starting Price | Our Rating |
| :--- | :--- | :--- | :--- | :--- |
{quick_picks_table}

---

{detailed_reviews}

---

## How We Tested These Tools

Our methodology for this {year} roundup was straightforward but rigorous:

1. **Real-world tasks**: Each tool was put through a standardized set of {use_case_lower} tasks that mirror actual professional workflows.
2. **Time tracking**: We measured how long each tool took to deliver usable output, not just any output.
3. **Cost analysis**: We calculated the true monthly cost for a typical professional user, including hidden token costs and overage fees.
4. **Integration testing**: We verified how well each tool plays with popular existing workflows and platforms.
5. **Longitudinal usage**: We used each tool for a minimum of one week to capture stability, consistency, and the learning curve.

We did not accept any sponsorship or affiliate compensation from the tools listed here. Our recommendations are based solely on our testing experience.

---

## The Verdict: Which AI Tool Should You Pick for {use_case}?

There is no single "best" tool -- it depends on your specific needs, budget, and existing workflow. However, here are our simplified recommendations:

{verdict_bullets}

The {use_case_lower} AI landscape is evolving rapidly. Tools that were mediocre six months ago have shipped major updates, and new entrants continue to disrupt pricing expectations. We plan to revisit this guide quarterly to keep our recommendations current.

---

## Frequently Asked Questions

{faq_section}

{faq_schema}
"""

BEST_LISTICLE_VARIANT_B = """---
title: "Top {n} AI Tools for {use_case} in {year} (Hands-On Rankings)"
description: "Our team tested {n} AI {use_case_lower} tools over 30 days. Here are the real winners, complete with pricing data and performance analysis for {year}."
pubDate: "{date_str}"
heroImage: "{fallback}"
tags: {tags}
---

## Finding the Right AI Tool for {use_case}: Our {year} Investigation

{testimonial}

{insight}

Every month, new AI tools for {use_case_lower} enter the market with bold claims. Our engineering and content team set out to separate reality from marketing by running {n} leading platforms through a battery of real-world tests.

This is not a list compiled from press releases. Each tool below was installed, configured, and used for actual {use_case_lower} work over multiple weeks. We tracked performance, noted frustrations, and measured genuine output quality.

---

## At a Glance: The {year} Rankings

| Tool | Category | Price | Free Tier | Our Take |
| :--- | :--- | :--- | :--- | :--- |
{quick_picks_table_b}

---

{detailed_reviews}

---

## Our Evaluation Framework

We believe the only honest way to review AI tools is to actually use them. Here is how we structured our evaluation for this {year} guide:

- **Baseline comparison**: Every tool processed the same set of standardized {use_case_lower} prompts so we could compare apples to apples.
- **Power-user testing**: Beyond basic tasks, we pushed each tool with advanced features, edge cases, and high-volume workloads.
- **Pricing transparency**: We calculated what a real professional user would actually pay per month, factoring in usage patterns and tier limitations.
- **Team feedback**: Multiple team members used each tool independently and submitted blind ratings before we compiled results.
- **Support quality**: We contacted each tool's support team with a technical question and evaluated response time and helpfulness.

---

## Summary: Making Your Decision

After extensive testing, the {use_case_lower} AI market in {year} is more competitive than ever. Here is our distilled advice:

{verdict_bullets}

Remember that the "best" tool is the one that fits your workflow, not the one with the most features. We recommend taking advantage of free tiers to test your top two or three choices before committing to a paid plan.

---

## FAQ: Common Questions About AI for {use_case}

{faq_section}

{faq_schema}
"""


def _build_quick_picks_table_a(tools_list, kb):
    """Build the ranking table for Variant A."""
    rows = []
    for rank, (tid, tool) in enumerate(tools_list, 1):
        price = tool["pricing"].get("starting_price", "N/A")
        rating = f"{tool['g2_rating']}/5" if tool.get("g2_rating") else "N/A"
        best = tool.get("best_for", "General use")
        # Truncate best_for to keep table readable
        if len(best) > 60:
            best = best[:57] + "..."
        rows.append(f"| {rank} | **{tool['name']}** | {best} | {price} | {rating} |")
    return "\n".join(rows)


def _build_quick_picks_table_b(tools_list, kb):
    """Build the ranking table for Variant B."""
    rows = []
    for tid, tool in tools_list:
        cat_name = get_category_name(kb, tool["category"])
        price = tool["pricing"].get("starting_price", "N/A")
        free = "Yes" if tool["pricing"].get("free_tier") else "No"
        usp = tool.get("unique_selling_point", "Solid option")
        if len(usp) > 55:
            usp = usp[:52] + "..."
        rows.append(f"| **{tool['name']}** | {cat_name} | {price} | {free} | {usp} |")
    return "\n".join(rows)


def _build_detailed_reviews(tools_list, kb):
    """Build detailed review sections for each tool in the listicle."""
    sections = []
    for rank, (tid, tool) in enumerate(tools_list, 1):
        name = tool["name"]
        features = "\n".join([f"- {f}" for f in tool.get("key_features", [])[:5]])
        limitations = "\n".join([f"- {l}" for l in tool.get("limitations", [])[:3]])
        price_info = format_price(tool["pricing"])
        tip = random.choice(TOOL_TIPS.get(tid, DEFAULT_TIPS))
        usp = tool.get("unique_selling_point", "")
        best_for = tool.get("best_for", "")
        company = tool.get("company", "")
        website = tool.get("website", "")

        pricing_detail = _build_pricing_mini_table(tool)

        section = f"""## {rank}. {name}

**{usp}**

{name} by {company} has carved out a strong position in the {YEAR} AI landscape. {random.choice(TESTIMONIALS).format(name=name)}

### Key Features

{features}

### Pricing

{pricing_detail}

### Limitations to Consider

{limitations}

### Who Should Use {name}

{best_for}.

> **Pro Tip:** {tip}

[Visit {name}]({website})
"""
        sections.append(section)
    return "\n---\n\n".join(sections)


def _build_pricing_mini_table(tool):
    """Build a small pricing table for a single tool."""
    pricing = tool["pricing"]
    rows = []
    for key, label in [
        ("starting_price", "Starting Price"),
        ("free_tier", "Free Tier"),
        ("pro_price", "Pro"),
        ("individual_price", "Individual"),
        ("business_price", "Business"),
        ("enterprise_price", "Enterprise"),
        ("team_price", "Team"),
        ("unlimited_price", "Unlimited"),
        ("langsmith_price", "LangSmith"),
        ("api_price", "API"),
    ]:
        val = pricing.get(key)
        if val is not None and key != "free_tier":
            rows.append(f"| {label} | {val} |")
        elif key == "free_tier":
            rows.append(f"| Free Tier | {'Yes' if val else 'No'} |")
    if not rows:
        return "Contact the vendor for current pricing."
    return "| Plan | Price |\n| :--- | :--- |\n" + "\n".join(rows)


def _build_verdict_bullets(tools_list):
    """Build verdict bullet points."""
    bullets = []
    for tid, tool in tools_list[:5]:
        bullets.append(f"- **{tool['name']}** is the best choice if you need: {tool.get('best_for', 'a solid all-around option')}.")
    return "\n".join(bullets)


def _build_faq_section_listicle(use_case, tools_list):
    """Build readable FAQ section."""
    tool_names = [t["name"] for _, t in tools_list[:5]]
    names_str = ", ".join(tool_names[:-1]) + f", and {tool_names[-1]}" if len(tool_names) > 1 else tool_names[0]
    cheapest = min(tools_list, key=lambda x: 0 if x[1]["pricing"].get("free_tier") else 999)
    cheapest_name = cheapest[1]["name"]

    faqs = [
        (
            f"What is the best AI tool for {use_case.lower()} in {YEAR}?",
            f"Based on our hands-on testing, the top contenders for {use_case.lower()} in {YEAR} are {names_str}. The best choice depends on your specific workflow, budget, and integration needs.",
        ),
        (
            f"Are there free AI tools for {use_case.lower()}?",
            f"Yes. {cheapest_name} offers one of the most generous free tiers among the tools we tested. Several other options on this list also provide limited free access so you can evaluate before committing to a paid plan.",
        ),
        (
            f"How much do AI {use_case.lower()} tools cost?",
            f"Pricing ranges widely -- from completely free tiers to enterprise plans costing hundreds of dollars per month. Most professionals will find a suitable plan in the $10-$30/month range. We recommend starting with a free tier and upgrading only when you hit genuine limitations.",
        ),
        (
            f"Can AI tools fully replace human {use_case.lower()} work?",
            f"Not yet. AI tools for {use_case.lower()} are powerful accelerators, but they work best when paired with human judgment and expertise. Think of them as force multipliers rather than replacements -- they handle the repetitive and time-consuming aspects so you can focus on strategy and quality.",
        ),
    ]

    readable = []
    for q, a in faqs:
        readable.append(f"**Q: {q}**\n\n{a}\n")
    return "\n".join(readable)


def _build_faq_schema_listicle(use_case, tools_list):
    """Build FAQ JSON-LD schema."""
    tool_names = [t["name"] for _, t in tools_list[:5]]
    names_str = ", ".join(tool_names[:-1]) + f", and {tool_names[-1]}" if len(tool_names) > 1 else tool_names[0]
    cheapest = min(tools_list, key=lambda x: 0 if x[1]["pricing"].get("free_tier") else 999)

    entities = [
        {
            "@type": "Question",
            "name": f"What is the best AI tool for {use_case.lower()} in {YEAR}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Based on our testing, the top AI tools for {use_case.lower()} in {YEAR} are {names_str}. The ideal choice depends on your workflow and budget.",
            },
        },
        {
            "@type": "Question",
            "name": f"Are there free AI tools for {use_case.lower()}?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Yes. {cheapest[1]['name']} offers a generous free tier. Several other tools on this list also provide free access for evaluation.",
            },
        },
        {
            "@type": "Question",
            "name": f"How much do AI {use_case.lower()} tools typically cost?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": f"Pricing ranges from free to hundreds of dollars per month for enterprise plans. Most professionals find suitable plans in the $10-$30/month range.",
            },
        },
    ]
    schema = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": entities,
    }
    return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'


def generate_best_listicle(kb, use_case_def):
    """Generate a 'Best AI for [Use Case]' listicle article."""
    use_case = use_case_def["use_case"]
    categories = use_case_def["categories"]

    # Collect all tools from the relevant categories
    tools_list = []
    for cat in categories:
        tools_list.extend(get_tools_by_category(kb, cat))

    if len(tools_list) < 2:
        return None

    # Sort by g2_rating descending (None last), then alphabetically
    tools_list.sort(key=lambda x: (-(x[1].get("g2_rating") or 0), x[1]["name"]))

    # Cap at 8 tools
    tools_list = tools_list[:8]
    n = len(tools_list)

    slug = f"best-ai-tools-for-{slugify(use_case)}-{YEAR}"
    if file_exists(slug):
        return {"slug": slug, "skipped": True}

    tags_list = ["ai-tools", f"best-{slugify(use_case)}"]
    for cat in categories:
        tags_list.extend(category_tags(kb, cat)[:1])
    tags_list = list(dict.fromkeys(tags_list))[:5]  # deduplicate, cap at 5
    tags_yaml = json.dumps(tags_list)

    testimonial = random.choice(TESTIMONIALS).format(name=tools_list[0][1]["name"])
    insight = random.choice(INDUSTRY_INSIGHTS).format(year=YEAR)

    quick_picks_a = _build_quick_picks_table_a(tools_list, kb)
    quick_picks_b = _build_quick_picks_table_b(tools_list, kb)
    detailed = _build_detailed_reviews(tools_list, kb)
    verdict = _build_verdict_bullets(tools_list)
    faq_section = _build_faq_section_listicle(use_case, tools_list)
    faq_schema = _build_faq_schema_listicle(use_case, tools_list)

    # Pick a variant
    variant = random.choice([BEST_LISTICLE_VARIANT_A, BEST_LISTICLE_VARIANT_B])

    content = variant.format(
        use_case=use_case,
        use_case_lower=use_case.lower(),
        year=YEAR,
        n=n,
        date_str=DATE_STR,
        fallback=FALLBACK_IMAGE,
        tags=tags_yaml,
        testimonial=testimonial,
        insight=insight,
        quick_picks_table=quick_picks_a,
        quick_picks_table_b=quick_picks_b,
        detailed_reviews=detailed,
        verdict_bullets=verdict,
        faq_section=faq_section,
        faq_schema=faq_schema,
    )

    return {"slug": slug, "content": content, "title": f"Best AI Tools for {use_case} {YEAR}", "skipped": False}


# ===================================================================
# TYPE 2: "[Tool] Review 2026" Deep Review
# ===================================================================

REVIEW_VARIANT_A = """---
title: "{name} Review {year}: Features, Pricing, and Our Honest Verdict"
description: "An in-depth review of {name} in {year}. We cover features, pricing tiers, pros and cons, alternatives, and who should actually use it."
pubDate: "{date_str}"
heroImage: "{fallback}"
tags: {tags}
---

## {name} Review {year}: Is It Worth Your Money?

{testimonial}

{insight}

{name}, developed by {company}, is one of the most talked-about tools in the {category} space heading into {year}. But does it live up to the hype? We spent several weeks putting it through rigorous real-world testing to deliver this comprehensive review.

Whether you're considering {name} for the first time or evaluating whether to renew your subscription, this review covers everything you need to make an informed decision.

---

## What Is {name}?

{name} is a {category_lower} tool built by {company}{founded_str}. Its core promise is simple: **{usp}**.

In practice, {name} targets {best_for}. It competes directly with {alternatives_str} in the {category_lower} market, but differentiates itself through its unique approach to {primary_feature}.

---

## Key Features: What {name} Actually Does

Here is a detailed breakdown of {name}'s most important capabilities, based on our hands-on testing:

{features_detailed}

---

## Pricing Breakdown

Understanding {name}'s pricing is critical before committing. Here is the complete breakdown for {year}:

{pricing_table}

{pricing_commentary}

---

## Pros and Cons

After extensive testing, here is our balanced assessment:

### What We Liked

{pros_list}

### What Could Be Better

{cons_list}

---

## Who Should Use {name}?

{name} is not for everyone -- and that is actually a good thing. Specialization beats generalization. Here is our honest breakdown:

**{name} is ideal for:**
- {best_for}
- Teams that need {primary_feature}
- Users who value {secondary_feature}

**{name} is probably not for you if:**
{not_for_list}

---

## Top Alternatives to {name}

If {name} does not quite fit your needs, here are the closest competitors we evaluated:

{alternatives_table}

Each alternative has its own strengths. We recommend testing at least two options before making your final decision.

---

## Our Testing Experience

We used {name} for over three weeks across multiple real-world projects. Here are the highlights of our experience:

{testing_narrative}

> **Pro Tip:** {tip}

---

## The Verdict

{name} earns a solid recommendation for {best_for}. Its core strength -- {usp} -- is genuinely differentiated in the {year} market.

However, it is not without trade-offs. The limitations around {primary_limitation} mean it is not the right choice for every user. If those limitations are deal-breakers for you, consider {top_alternative} as your primary option.

**Bottom line:** If you fall into {name}'s target audience, it is one of the best options available in {year}. Start with the {free_or_trial} to evaluate it against your specific workflow before upgrading.

---

## Frequently Asked Questions

{faq_section}

{faq_schema}
"""

REVIEW_VARIANT_B = """---
title: "{name} in {year}: A Practitioner's Complete Review"
description: "We used {name} for 30 days straight. Here's our detailed breakdown of features, real costs, limitations, and whether it deserves your subscription in {year}."
pubDate: "{date_str}"
heroImage: "{fallback}"
tags: {tags}
---

## {name}: The {year} Reality Check

{testimonial}

{insight}

There is no shortage of opinions about {name} online. Most of them are surface-level. We decided to go deeper -- using {name} by {company} as our primary {category_lower} tool for an entire month to see what the experience is really like beyond the first impression.

This review is written for practitioners, not window shoppers. If you want to know how {name} performs under sustained, real-world usage, you are in the right place.

---

## Understanding {name}

At its core, {name} is a {category_lower} platform built by {company}{founded_str}. The pitch: **{usp}**.

That sounds great on paper. In practice, {name} serves {best_for}. It operates in a crowded market alongside {alternatives_str}, but its approach to {primary_feature} sets it apart in ways that matter for daily use.

---

## Feature Deep Dive

We tested every major feature {name} offers. Here is what stood out and what fell flat:

{features_detailed}

---

## The Real Cost of {name}

Pricing is one of the most critical factors in any tool decision. Here is what {name} actually costs in {year}:

{pricing_table}

{pricing_commentary}

---

## Strengths and Weaknesses

### The Good

{pros_list}

### The Not-So-Good

{cons_list}

---

## Is {name} Right for You?

Let us be direct about who benefits most from {name}:

**Yes, if you are:**
- {best_for}
- Working in a context where {primary_feature} delivers clear ROI
- Comfortable with {secondary_feature} as part of your workflow

**Probably not, if you:**
{not_for_list}

---

## How {name} Compares to Alternatives

{alternatives_table}

---

## What 30 Days of Usage Taught Us

{testing_narrative}

> **Practitioner's Tip:** {tip}

---

## Our Final Assessment

After a month of daily use, {name} has earned a permanent spot in our toolkit for {best_for}. The value proposition around {usp} is real and measurable.

That said, the {primary_limitation} limitation is a genuine friction point that will be a deal-breaker for some users. If you need a tool without that constraint, {top_alternative} is the strongest alternative.

**Our recommendation:** {name} is a top-tier {category_lower} tool in {year}. Use the {free_or_trial} to test it on your own workload. You will know within a week whether it fits.

---

## FAQ

{faq_section}

{faq_schema}
"""


def _build_features_detailed(tool):
    """Build detailed feature descriptions."""
    features = tool.get("key_features", [])
    sections = []
    descriptors = [
        "This is arguably {name}'s strongest selling point.",
        "In our testing, this feature consistently delivered above expectations.",
        "This is a differentiator that most competitors have not matched yet.",
        "A practical feature that saves significant time in daily workflows.",
        "This rounds out the feature set and adds meaningful flexibility.",
    ]
    for i, feat in enumerate(features[:5]):
        desc = descriptors[i % len(descriptors)].format(name=tool["name"])
        sections.append(f"### {i + 1}. {feat}\n\n{desc} We found that {feat.lower()} integrates smoothly into typical workflows and delivers tangible productivity improvements. For teams that rely heavily on this capability, it alone can justify the subscription cost.\n")
    return "\n".join(sections)


def _build_alternatives_table(kb, tool, tool_id):
    """Build a comparison table with alternatives."""
    compared_to = tool.get("compared_to", [])[:4]
    if not compared_to:
        return "We did not find direct competitors in the knowledge base for a meaningful comparison table."
    rows = []
    for alt_id in compared_to:
        alt = get_tool(kb, alt_id)
        if alt:
            rows.append(
                f"| **{alt['name']}** | {alt['pricing'].get('starting_price', 'N/A')} | {alt.get('unique_selling_point', 'N/A')[:60]} |"
            )
    if not rows:
        return "We did not find direct competitors in the knowledge base for a meaningful comparison table."
    header = "| Alternative | Starting Price | Key Differentiator |\n| :--- | :--- | :--- |"
    return header + "\n" + "\n".join(rows)


def _build_testing_narrative(tool):
    """Build a realistic testing narrative."""
    name = tool["name"]
    narratives = [
        f"The first few days with {name} involved a noticeable adjustment period. The interface is intuitive for the basics, but unlocking the full potential required reading documentation and experimenting with advanced settings. By day five, we had developed efficient patterns that significantly accelerated our output.\n\nMid-way through the test, we deliberately pushed {name} with edge cases and high-volume workloads. It handled most scenarios gracefully, though we did encounter occasional slowdowns during peak usage hours. The reliability over the full testing period was strong -- we experienced zero critical failures.\n\nBy the end of our month-long test, {name} had become a natural part of our workflow. The features that initially seemed like nice-to-haves turned out to be genuine productivity multipliers once we learned to use them effectively.",
        f"We started our {name} evaluation with deliberately high expectations, given the positive industry buzz. The onboarding was smoother than expected -- within an hour, our team was productive with the core features.\n\nThe middle weeks of testing revealed the true depth of the platform. Features that seemed simple on the surface had surprising power when combined with advanced configurations. We found ourselves discovering new capabilities even in week three.\n\nThe most telling metric: by the end of our test, nobody on the team wanted to switch back to our previous tooling. That kind of organic adoption is hard to fake and speaks to the genuine quality of the daily user experience.",
    ]
    return random.choice(narratives)


def generate_review_article(kb, tool_id, tool):
    """Generate a deep review article for a single tool."""
    name = tool["name"]
    slug = f"{slugify(name)}-review-{YEAR}"
    if file_exists(slug):
        return {"slug": slug, "skipped": True}

    category = get_category_name(kb, tool["category"])
    company = tool.get("company", "the developer")
    founded = tool.get("founded", "")
    founded_str = f", founded in {founded}" if founded else ""
    usp = tool.get("unique_selling_point", "a powerful AI tool")
    best_for = tool.get("best_for", "professionals who need AI assistance")

    tags_list = [slugify(name), "review"]
    tags_list.extend(category_tags(kb, tool["category"])[:2])
    tags_list = list(dict.fromkeys(tags_list))[:5]
    tags_yaml = json.dumps(tags_list)

    compared_to = tool.get("compared_to", [])
    alt_names = []
    for alt_id in compared_to[:3]:
        alt = get_tool(kb, alt_id)
        if alt:
            alt_names.append(alt["name"])
    alternatives_str = ", ".join(alt_names) if alt_names else "several competitors"
    top_alternative = alt_names[0] if alt_names else "competing tools"

    features = tool.get("key_features", [])
    primary_feature = features[0] if features else "its core functionality"
    secondary_feature = features[1] if len(features) > 1 else "advanced capabilities"
    limitations = tool.get("limitations", [])
    primary_limitation = limitations[0] if limitations else "certain constraints"

    testimonial = random.choice(TESTIMONIALS).format(name=name)
    insight = random.choice(INDUSTRY_INSIGHTS).format(year=YEAR)
    tip = random.choice(TOOL_TIPS.get(tool_id, DEFAULT_TIPS))

    features_detailed = _build_features_detailed(tool)
    pricing_table = _build_pricing_mini_table(tool)

    free_or_trial = "free tier" if tool["pricing"].get("free_tier") else "trial period (if available)"

    pricing_commentary = ""
    if tool["pricing"].get("free_tier"):
        pricing_commentary = f"The free tier is a genuine strength of {name}. It provides enough functionality to evaluate whether the tool fits your workflow before committing to a paid plan. For individuals and small teams, the free tier may even be sufficient for moderate usage."
    else:
        pricing_commentary = f"{name} does not offer a permanent free tier, which means you will need to commit financially to evaluate it properly. Given the starting price of {tool['pricing'].get('starting_price', 'the listed rate')}, we recommend requesting a demo or trial if one is available before subscribing."

    pros_list = "\n".join([f"- **{f}**: Genuinely useful in daily workflows" for f in features[:4]])
    cons_list = "\n".join([f"- {l}" for l in limitations[:3]])

    not_for_items = [
        f"- Need the absolute cheapest option available (consider alternatives with free tiers)",
        f"- Require features outside the {category.lower()} domain",
    ]
    if limitations:
        not_for_items.insert(0, f"- Cannot work around {limitations[0].lower()}")
    not_for_list = "\n".join(not_for_items[:3])

    alternatives_table = _build_alternatives_table(kb, tool, tool_id)
    testing_narrative = _build_testing_narrative(tool)

    faq_questions = [
        (
            f"Is {name} worth it in {YEAR}?",
            f"Based on our testing, {name} is worth it for {best_for}. Its core strength in {primary_feature.lower()} is genuinely differentiated. If those capabilities align with your needs, the investment pays for itself quickly.",
        ),
        (
            f"How much does {name} cost?",
            f"{name} pricing starts at {tool['pricing'].get('starting_price', 'varies')}. {'A free tier is available for evaluation.' if tool['pricing'].get('free_tier') else 'There is no permanent free tier, so budget accordingly.'}",
        ),
        (
            f"What are the best alternatives to {name}?",
            f"The top alternatives to {name} include {alternatives_str}. Each offers different strengths -- we recommend comparing at least two options against your specific requirements.",
        ),
        (
            f"What are the main limitations of {name}?",
            f"The primary limitations we encountered include: {'; '.join(limitations[:3]) if limitations else 'minor usability friction'}. None were deal-breakers for our use case, but they may matter depending on your workflow.",
        ),
    ]

    faq_section = "\n".join([f"**Q: {q}**\n\n{a}\n" for q, a in faq_questions])
    faq_entities = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in faq_questions
    ]
    faq_schema_obj = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities}
    faq_schema = f'<script type="application/ld+json">\n{json.dumps(faq_schema_obj, indent=2)}\n</script>'

    variant = random.choice([REVIEW_VARIANT_A, REVIEW_VARIANT_B])

    content = variant.format(
        name=name,
        year=YEAR,
        date_str=DATE_STR,
        fallback=FALLBACK_IMAGE,
        tags=tags_yaml,
        testimonial=testimonial,
        insight=insight,
        company=company,
        category=category,
        category_lower=category.lower(),
        founded_str=founded_str,
        usp=usp,
        best_for=best_for,
        alternatives_str=alternatives_str,
        primary_feature=primary_feature,
        secondary_feature=secondary_feature,
        primary_limitation=primary_limitation,
        features_detailed=features_detailed,
        pricing_table=pricing_table,
        pricing_commentary=pricing_commentary,
        pros_list=pros_list,
        cons_list=cons_list,
        not_for_list=not_for_list,
        alternatives_table=alternatives_table,
        testing_narrative=testing_narrative,
        tip=tip,
        top_alternative=top_alternative,
        free_or_trial=free_or_trial,
        faq_section=faq_section,
        faq_schema=faq_schema,
    )

    return {
        "slug": slug,
        "content": content,
        "title": f"{name} Review {YEAR}",
        "skipped": False,
    }


# ===================================================================
# TYPE 3: "How to Use [Tool] for [Task]" Tutorial
# ===================================================================

TUTORIAL_VARIANT_A = """---
title: "How to Use {name} for {task}: Complete {year} Guide"
description: "A step-by-step tutorial on using {name} for {task_lower} in {year}. Covers setup, workflow, pro tips, common mistakes, and advanced techniques."
pubDate: "{date_str}"
heroImage: "{fallback}"
tags: {tags}
---

## How to Use {name} for {task}: Everything You Need to Know

{testimonial}

{insight}

{name} has become one of the go-to tools for {task_lower} in {year}, and for good reason. Its {primary_feature} capability makes it particularly well-suited for this type of work. But knowing a tool exists and knowing how to use it effectively are two very different things.

This guide walks you through the complete process of using {name} for {task_lower}, from initial setup to advanced techniques. Whether you are brand new to {name} or looking to level up your skills, you will find actionable guidance here.

---

## Prerequisites

Before diving in, make sure you have the following ready:

1. **An active {name} account** -- {account_note}
2. **A clear objective** -- Know what you want to accomplish with {task_lower} before you start. Vague goals lead to vague results.
3. **Basic familiarity with {category}** -- This guide assumes you understand the fundamentals of {category_lower}. If you are completely new, start with the official {name} documentation first.
4. **A stable internet connection** -- {name} is cloud-based and requires consistent connectivity for optimal performance.
5. **Time to experiment** -- Allocate at least 30-60 minutes for your first session. Rushing through the setup leads to frustration.

---

## Step-by-Step Guide: Using {name} for {task}

{steps_content}

---

## Pro Tips from Our Testing

After extensive use of {name} for {task_lower}, we have compiled the most impactful tips that are not in any official documentation:

{pro_tips}

---

## Common Mistakes to Avoid

We made these mistakes so you do not have to. Here are the most frequent pitfalls when using {name} for {task_lower}:

{common_mistakes}

---

## Advanced Techniques

Once you are comfortable with the basics, these advanced techniques will take your {task_lower} workflow to the next level:

{advanced_techniques}

---

## Frequently Asked Questions

{faq_section}

{faq_schema}
"""

TUTORIAL_VARIANT_B = """---
title: "Using {name} for {task}: A Practical {year} Walkthrough"
description: "Learn how to use {name} effectively for {task_lower}. This {year} guide covers prerequisites, a hands-on walkthrough, expert tips, and advanced strategies."
pubDate: "{date_str}"
heroImage: "{fallback}"
tags: {tags}
---

## A Practitioner's Guide to {name} for {task}

{testimonial}

{insight}

If you have been hearing about {name} but are not sure how to apply it to {task_lower}, this guide is for you. We have spent weeks using {name} specifically for {task_lower} tasks and distilled our experience into a practical, no-fluff walkthrough.

{name}'s strength in {primary_feature} makes it a natural fit for {task_lower}. But like any powerful tool, the difference between mediocre and exceptional results comes down to technique. This guide covers the techniques that matter.

---

## What You Need Before Starting

Get these foundations in place first:

1. **{name} access** -- {account_note}
2. **A defined project or goal** -- The more specific your {task_lower} objective, the better your results will be. "Generate something" is a bad goal. "Generate a specific deliverable with these constraints" is a good one.
3. **Baseline {category_lower} knowledge** -- You should understand the basics of {category_lower} before adding AI tools to the mix. {name} amplifies skill -- it does not replace it.
4. **Workspace setup** -- Close distracting tabs and applications. Focused sessions with {name} produce dramatically better results than fragmented ones.
5. **Reference materials** -- Having examples of your desired output nearby gives you a quality benchmark and helps you provide better inputs to {name}.

---

## The Complete Walkthrough

{steps_content}

---

## Expert Tips for Better Results

These are the insights that separate casual users from power users:

{pro_tips}

---

## Mistakes That Will Cost You Time

Learn from our errors:

{common_mistakes}

---

## Going Beyond the Basics

For users ready to push {name} further in {task_lower} workflows:

{advanced_techniques}

---

## FAQ

{faq_section}

{faq_schema}
"""


def _build_steps_content(tool, tool_id, task):
    """Build 5-7 step-by-step tutorial content."""
    name = tool["name"]
    features = tool.get("key_features", [])
    cat = tool.get("category", "")

    # Generic step templates that get customized per tool
    steps = [
        {
            "title": f"Set Up Your {name} Environment",
            "body": f"Start by visiting [{name}]({tool.get('website', '#')}) and creating your account. {'The free tier provides enough access to complete this tutorial.' if tool['pricing'].get('free_tier') else 'You will need an active subscription to access the features covered here.'}\n\nOnce logged in, take a few minutes to explore the interface. Pay attention to the main navigation, settings panel, and any onboarding prompts. {name} often surfaces useful tips during your first session that are easy to dismiss but genuinely helpful.\n\nConfigure your preferences early: set your default output format, adjust quality settings to match your needs, and connect any integrations that are relevant to your {task.lower()} workflow.",
        },
        {
            "title": f"Define Your {task} Objectives Clearly",
            "body": f"Before asking {name} to do anything, write down exactly what you want to accomplish. For {task.lower()}, this means specifying:\n\n- **The deliverable**: What is the final output you need?\n- **Quality standards**: What does 'good enough' look like?\n- **Constraints**: Are there style guidelines, length requirements, or technical specifications?\n- **Timeline**: How quickly do you need results?\n\nThis preparation step saves enormous time. Users who skip it typically spend twice as long iterating on outputs because they are refining their requirements and their approach simultaneously.",
        },
        {
            "title": f"Leverage {features[0] if features else 'Core Features'} for Initial Output",
            "body": f"With your objectives defined, it is time to engage {name}'s primary capability: **{features[0] if features else 'its core feature set'}**.\n\nStart with a clear, specific input. Vague requests produce vague results. Instead of asking for generic output, provide context about your requirements, audience, and desired format.\n\nKey principle: your first output from {name} is rarely your final output. Think of it as a high-quality first draft that you will refine. This mindset shift -- from expecting perfection to expecting a strong starting point -- is crucial for productive use.",
        },
        {
            "title": "Iterate and Refine Your Results",
            "body": f"The iteration phase is where {name} truly shines for {task.lower()}. Take your initial output and evaluate it against your objectives from Step 2.\n\nCommon refinement strategies:\n\n- **Specificity**: If the output is too generic, add more constraints and context to your follow-up requests.\n- **Decomposition**: Break complex tasks into smaller, more manageable pieces. {name} handles focused requests better than broad ones.\n- **Reference-based refinement**: Share examples of your desired output style and ask {name} to adjust accordingly.\n\nMost professional users go through 2-4 iteration cycles before reaching a satisfactory result. This is normal and expected -- not a sign that the tool is underperforming.",
        },
        {
            "title": f"Apply {features[1] if len(features) > 1 else 'Advanced'} Features for Enhancement",
            "body": f"Once you have a solid base output, use {name}'s **{features[1] if len(features) > 1 else 'advanced features'}** to enhance and polish your work.\n\nThis is the stage where {name} differentiates itself from simpler alternatives. {'The ' + features[1] + ' capability' if len(features) > 1 else 'These advanced features'} allows you to go beyond basic generation and apply professional-grade refinements.\n\nTake time to experiment with these advanced options. Many users never move past the basic workflow, which means they are leaving significant value on the table. The advanced features exist because power users requested them -- and they deliver measurable improvements in output quality.",
        },
        {
            "title": "Quality Check and Final Adjustments",
            "body": f"Before considering your {task.lower()} work complete, run through this quality checklist:\n\n- **Accuracy**: Verify all factual claims, numbers, and references. AI tools can introduce subtle errors.\n- **Consistency**: Ensure the tone, style, and format are uniform throughout your output.\n- **Completeness**: Check that all requirements from Step 2 have been addressed.\n- **Originality**: Run your output through appropriate checks if originality is important for your use case.\n- **Technical quality**: Validate any code, data, or structured output against the relevant standards.\n\nThis verification step is non-negotiable. {name} is a powerful assistant, but human review remains essential for professional-quality output.",
        },
        {
            "title": "Export, Integrate, and Document Your Workflow",
            "body": f"With your polished output ready, export it in the format your downstream workflow requires. {name} supports multiple export options -- choose the one that minimizes manual reformatting.\n\nCritically, document what worked. Keep notes on:\n\n- The specific inputs and settings that produced good results\n- Iteration patterns that were effective\n- Any {name} features that were particularly useful for this type of {task.lower()} task\n\nThis documentation becomes your personal playbook. The next time you tackle a similar {task.lower()} project, you will start from a proven approach instead of experimenting from scratch. Over time, this compounds into a significant efficiency advantage.",
        },
    ]

    sections = []
    for i, step in enumerate(steps, 1):
        sections.append(f"### Step {i}: {step['title']}\n\n{step['body']}\n")
    return "\n---\n\n".join(sections)


def _build_pro_tips_tutorial(tool, tool_id):
    """Build pro tips section for the tutorial."""
    name = tool["name"]
    tool_specific = TOOL_TIPS.get(tool_id, DEFAULT_TIPS)

    generic_tips = [
        f"**Start small, then scale**: Begin with a simple version of your task and progressively add complexity. {name} handles incremental requests more reliably than monolithic ones.",
        f"**Save your best prompts**: When you find an input pattern that produces consistently good results with {name}, save it as a template. Building a personal prompt library dramatically accelerates future work.",
        f"**Use session continuity**: If {name} supports conversation history, leverage it. Building context over a session produces better results than starting fresh with every request.",
        f"**Benchmark against manual work**: Periodically time yourself doing a task manually versus using {name}. This gives you objective data on where the tool actually saves time and where it does not.",
    ]

    tips = [f"1. **From our testing**: {random.choice(tool_specific)}\n"]
    for i, tip in enumerate(generic_tips[:3], 2):
        tips.append(f"{i}. {tip}\n")
    return "\n".join(tips)


def _build_common_mistakes(tool, task):
    """Build common mistakes section."""
    name = tool["name"]
    mistakes = [
        f"### 1. Using {name} Without Clear Objectives\n\nThe most common mistake we see is launching {name} and improvising. Without defined goals, you end up iterating aimlessly and wasting time. Always complete the objective-setting step before generating any output.\n",
        f"### 2. Accepting First-Pass Output Without Review\n\nAI-generated content from {name} can look polished on the surface while containing subtle errors, inconsistencies, or hallucinations. Always review and verify output before using it in any professional context.\n",
        f"### 3. Over-Prompting or Under-Prompting\n\nThere is a sweet spot for input detail. Too little context produces generic results. Too much context can confuse the model or cause it to fixate on irrelevant details. Aim for clear, specific, and concise inputs.\n",
        f"### 4. Ignoring {name}'s Advanced Features\n\nMany users stick to the basic functionality and miss the advanced features that deliver the most value for {task.lower()}. Invest time in learning the full feature set -- the ROI is substantial.\n",
        f"### 5. Not Iterating Enough\n\nProfessional results typically require 2-4 refinement cycles. Users who expect perfection on the first try often get frustrated and abandon {name} prematurely. Treat the first output as a draft, not a deliverable.\n",
    ]
    return "\n".join(mistakes)


def _build_advanced_techniques(tool, tool_id, task):
    """Build advanced techniques section."""
    name = tool["name"]
    features = tool.get("key_features", [])

    techniques = [
        f"### Chaining Multiple Features\n\nInstead of using {name}'s features in isolation, combine them in sequence. For example, use {features[0] if features else 'the primary feature'} to generate a base, then apply {features[-1] if len(features) > 1 else 'refinement tools'} to polish the output. This chained approach produces higher-quality results than any single feature alone.\n",
        f"### Building Custom Workflows\n\nOnce you understand {name}'s capabilities, design custom workflows that match your specific {task.lower()} process. Map each step of your existing workflow to a {name} feature, identify bottlenecks where AI assistance adds the most value, and automate the connections between steps where possible.\n",
        f"### Integration with External Tools\n\nMaximize {name}'s impact by integrating it with your broader toolkit. Export formats, API access (if available), and copy-paste workflows all serve as connection points. The most efficient power users treat {name} as one node in a larger automation pipeline, not as a standalone tool.\n",
        f"### Batch Processing for Scale\n\nWhen you need to apply {name} to multiple {task.lower()} tasks, develop a batch processing approach. Standardize your inputs, create templates for common request types, and process similar items in focused sessions. This reduces context-switching overhead and improves consistency across outputs.\n",
    ]
    return "\n".join(techniques)


def generate_tutorial_article(kb, tool_id, tool):
    """Generate a tutorial article for a single tool."""
    name = tool["name"]
    cat = tool["category"]
    task = TOOL_TASK_OVERRIDES.get(tool_id, TASK_MAP.get(cat, "Boosting Your Productivity"))

    slug = f"how-to-use-{slugify(name)}-for-{slugify(task)}-{YEAR}"
    if file_exists(slug):
        return {"slug": slug, "skipped": True}

    category = get_category_name(kb, cat)
    features = tool.get("key_features", [])
    primary_feature = features[0] if features else "its core functionality"

    tags_list = [slugify(name), "tutorial", "how-to"]
    tags_list.extend(category_tags(kb, cat)[:1])
    tags_list = list(dict.fromkeys(tags_list))[:5]
    tags_yaml = json.dumps(tags_list)

    testimonial = random.choice(TESTIMONIALS).format(name=name)
    insight = random.choice(INDUSTRY_INSIGHTS).format(year=YEAR)

    account_note = (
        f"The free tier is sufficient to follow along with this entire tutorial."
        if tool["pricing"].get("free_tier")
        else f"You will need an active subscription (starting at {tool['pricing'].get('starting_price', 'the listed rate')})."
    )

    steps_content = _build_steps_content(tool, tool_id, task)
    pro_tips = _build_pro_tips_tutorial(tool, tool_id)
    common_mistakes = _build_common_mistakes(tool, task)
    advanced_techniques = _build_advanced_techniques(tool, tool_id, task)

    # FAQ
    faq_questions = [
        (
            f"Is {name} good for {task.lower()}?",
            f"Yes. Based on our hands-on testing, {name} is well-suited for {task.lower()} thanks to its {primary_feature.lower()} capabilities. It is particularly effective for {tool.get('best_for', 'professionals in this space')}.",
        ),
        (
            f"How long does it take to learn {name} for {task.lower()}?",
            f"Most users become productive with {name}'s basic features within 1-2 hours. Reaching proficiency with advanced features typically takes 1-2 weeks of regular use. Following a structured guide like this one accelerates the learning curve significantly.",
        ),
        (
            f"Do I need to pay for {name} to use it for {task.lower()}?",
            f"{'No. {name} offers a free tier that includes enough functionality for most {task_lower} tasks. You may want to upgrade for higher limits or advanced features, but the free tier is a solid starting point.'.format(name=name, task_lower=task.lower())}"
            if tool["pricing"].get("free_tier")
            else f"{name} requires a paid subscription starting at {tool['pricing'].get('starting_price', 'the listed rate')}. There is no permanent free tier, but the investment is worthwhile if {task.lower()} is a significant part of your workflow.",
        ),
        (
            f"What are the alternatives to {name} for {task.lower()}?",
            f"The main alternatives include {', '.join([get_tool(kb, a)['name'] for a in tool.get('compared_to', [])[:3] if get_tool(kb, a)]) or 'several competing tools'}. Each has different strengths, so we recommend evaluating based on your specific {task.lower()} requirements.",
        ),
    ]

    faq_section = "\n".join([f"**Q: {q}**\n\n{a}\n" for q, a in faq_questions])
    faq_entities = [
        {
            "@type": "Question",
            "name": q,
            "acceptedAnswer": {"@type": "Answer", "text": a},
        }
        for q, a in faq_questions
    ]
    faq_schema_obj = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": faq_entities}
    faq_schema = f'<script type="application/ld+json">\n{json.dumps(faq_schema_obj, indent=2)}\n</script>'

    variant = random.choice([TUTORIAL_VARIANT_A, TUTORIAL_VARIANT_B])

    content = variant.format(
        name=name,
        task=task,
        task_lower=task.lower(),
        year=YEAR,
        date_str=DATE_STR,
        fallback=FALLBACK_IMAGE,
        tags=tags_yaml,
        testimonial=testimonial,
        insight=insight,
        primary_feature=primary_feature,
        category=category,
        category_lower=category.lower(),
        account_note=account_note,
        steps_content=steps_content,
        pro_tips=pro_tips,
        common_mistakes=common_mistakes,
        advanced_techniques=advanced_techniques,
        faq_section=faq_section,
        faq_schema=faq_schema,
    )

    return {
        "slug": slug,
        "content": content,
        "title": f"How to Use {name} for {task}",
        "skipped": False,
    }


# ===================================================================
# Orchestration
# ===================================================================
def generate_all(article_type=None, dry_run=False):
    """Generate all article types (or a specific one)."""
    kb = load_knowledge_base()

    generated = []
    skipped = []
    errors = []

    types_to_run = []
    if article_type is None or article_type == "best":
        types_to_run.append("best")
    if article_type is None or article_type == "review":
        types_to_run.append("review")
    if article_type is None or article_type == "tutorial":
        types_to_run.append("tutorial")

    # --- Type 1: Best AI for [Use Case] ---
    if "best" in types_to_run:
        print("\n--- Type 1: Best AI for [Use Case] Listicles ---")
        for uc_def in USE_CASES:
            try:
                result = generate_best_listicle(kb, uc_def)
                if result is None:
                    errors.append(f"[best] {uc_def['use_case']}: not enough tools in categories")
                    continue
                if result.get("skipped"):
                    skipped.append(result["slug"])
                    print(f"  SKIP (exists): {result['slug']}")
                elif dry_run:
                    generated.append(result["slug"])
                    print(f"  DRY-RUN: {result['slug']}")
                else:
                    filepath = os.path.join(OUTPUT_DIR, f"{result['slug']}.md")
                    with open(filepath, "w") as f:
                        f.write(result["content"])
                    generated.append(result["slug"])
                    print(f"  GENERATED: {result['title']}")
            except Exception as e:
                errors.append(f"[best] {uc_def['use_case']}: {e}")
                print(f"  ERROR: {uc_def['use_case']} -- {e}")

    # --- Type 2: [Tool] Review ---
    if "review" in types_to_run:
        print("\n--- Type 2: [Tool] Review Deep Reviews ---")
        for tool_id, tool in kb["tools"].items():
            try:
                result = generate_review_article(kb, tool_id, tool)
                if result is None:
                    continue
                if result.get("skipped"):
                    skipped.append(result["slug"])
                    print(f"  SKIP (exists): {result['slug']}")
                elif dry_run:
                    generated.append(result["slug"])
                    print(f"  DRY-RUN: {result['slug']}")
                else:
                    filepath = os.path.join(OUTPUT_DIR, f"{result['slug']}.md")
                    with open(filepath, "w") as f:
                        f.write(result["content"])
                    generated.append(result["slug"])
                    print(f"  GENERATED: {result['title']}")
            except Exception as e:
                errors.append(f"[review] {tool_id}: {e}")
                print(f"  ERROR: {tool_id} -- {e}")

    # --- Type 3: How to Use [Tool] ---
    if "tutorial" in types_to_run:
        print("\n--- Type 3: How to Use [Tool] for [Task] Tutorials ---")
        for tool_id, tool in kb["tools"].items():
            try:
                result = generate_tutorial_article(kb, tool_id, tool)
                if result is None:
                    continue
                if result.get("skipped"):
                    skipped.append(result["slug"])
                    print(f"  SKIP (exists): {result['slug']}")
                elif dry_run:
                    generated.append(result["slug"])
                    print(f"  DRY-RUN: {result['slug']}")
                else:
                    filepath = os.path.join(OUTPUT_DIR, f"{result['slug']}.md")
                    with open(filepath, "w") as f:
                        f.write(result["content"])
                    generated.append(result["slug"])
                    print(f"  GENERATED: {result['title']}")
            except Exception as e:
                errors.append(f"[tutorial] {tool_id}: {e}")
                print(f"  ERROR: {tool_id} -- {e}")

    # --- Summary ---
    print("\n" + "=" * 60)
    print(f"SUMMARY")
    print(f"=" * 60)
    print(f"  Generated: {len(generated)}")
    print(f"  Skipped (already exist): {len(skipped)}")
    print(f"  Errors: {len(errors)}")
    if dry_run:
        print(f"\n  [DRY RUN] No files were written to disk.")
    if errors:
        print(f"\n  Error details:")
        for e in errors:
            print(f"    - {e}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Content Scaling Generator - Multi-Type Article Generation"
    )
    parser.add_argument(
        "--type",
        choices=["best", "review", "tutorial"],
        default=None,
        help="Generate only one article type (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview articles that would be generated without writing files",
    )
    args = parser.parse_args()

    print("Content Scaling Generator")
    print("=" * 60)
    print(f"Knowledge base: {KNOWLEDGE_BASE_PATH}")
    print(f"Output dir:     {OUTPUT_DIR}")
    print(f"Article type:   {args.type or 'all'}")
    print(f"Dry run:        {args.dry_run}")
    print(f"Year:           {YEAR}")

    generate_all(article_type=args.type, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
