"""
Intent-Based Content Generator
Matches user search intent to optimal title templates and content structures.
"""

import os
import json
import datetime
import random
import re

# Configuration
DATA_DIR = "/Users/mac/code/super-individual/projects/20260131_seo-site/scripts/data"
OUTPUT_DIR = "/Users/mac/code/super-individual/projects/20260131_seo-site/src/content/blog"
FALLBACK_IMAGE = "/assets/blog-fallback.jpg"

# Intent Keywords Database
INTENT_TRIGGERS = {
    "informational": ["what is", "how does", "explain", "research", "guide", "tutorial", "why", "meaning", "definition"],
    "listicle": ["best", "top", "alternatives", "options", "list", "ranked", "compared", "picks", "tools for"],
    "comparison": ["vs", "versus", "or", "compare", "difference", "between"],
    "navigational": ["review", "pricing", "login", "download", "free", "demo", "trial", "features"]
}

# Title Templates by Intent
TITLE_TEMPLATES = {
    "informational": [
        "What is {keyword}? A 2026 Technical Deep Dive",
        "{keyword} Explained: The Only Guide You Need in 2026",
        "How {keyword} Works: A Technical Breakdown [2026]",
        "{keyword} in 2026: Key Research & Insights Explained"
    ],
    "listicle": [
        "{keyword} in 2026: Top 5 Picks Tested",
        "{keyword}: 7 Alternatives Worth Trying in 2026",
        "Top {keyword} Ranked by Real Users (Feb 2026)",
        "{keyword} in 2026: Which One Should You Choose? [5 Tested]"
    ],
    "comparison": [
        "{keyword}: 3 Hidden Differences That Matter in 2026",
        "{keyword}: The Wrong Choice Could Cost You Hours",
        "{keyword} in 2026 - We Tested Both for 30 Days",
        "Don't Buy Until You See This {keyword} [2026 Review]"
    ],
    "navigational": [
        "{keyword}: Is It Worth the Hype? (2026 Review)",
        "{keyword}: Features, Pricing & What They Don't Tell You",
        "{keyword} in 2026: A Hands-On Technical Deep Dive",
        "{keyword} Review: Everything You Need to Know [2026]"
    ]
}


# Description Templates by Intent
DESCRIPTION_TEMPLATES = {
    "informational": [
        "Stop guessing. Our 2026 technical breakdown of {keyword} reveals what most guides miss.",
        "Everything you need to know about {keyword} in 2026. Research-backed insights for developers."
    ],
    "listicle": [
        "We tested 10+ options to find the best {keyword} in 2026. Here are our top picks with real data.",
        "Looking for the best {keyword}? Our 2026 rankings are based on hands-on testing, not affiliate deals."
    ],
    "comparison": [
        "Stop! Before you choose, read our 2026 {keyword} breakdown. We uncovered 3 critical differences.",
        "Thinking about {keyword}? Learn which one actually delivers ROI in 2026 and which is just hype."
    ],
    "navigational": [
        "Is {keyword} worth it in 2026? Our hands-on review covers pricing, features, and hidden costs.",
        "The definitive 2026 guide to {keyword}. Pricing, privacy, and the 'hidden' features most reviews miss."
    ]
}

def normalize_keyword(keyword, intent):
    """Clean keyword for use in templates, avoiding duplication."""
    kw = keyword.strip()
    if intent == "listicle":
        # Remove leading 'best' to avoid 'Best Best...'
        if kw.lower().startswith("best "):
            kw = kw[5:]
    return kw

def classify_intent(keyword):

    """Classify a keyword into an intent type."""
    keyword_lower = keyword.lower()
    
    for intent, triggers in INTENT_TRIGGERS.items():
        for trigger in triggers:
            if trigger in keyword_lower:
                return intent
    
    # Default to informational if no match
    return "informational"

def generate_title(keyword, intent):
    """Generate a title based on keyword and intent."""
    templates = TITLE_TEMPLATES.get(intent, TITLE_TEMPLATES["informational"])
    template = random.choice(templates)
    normalized = normalize_keyword(keyword, intent)
    return template.format(keyword=normalized.title())


def generate_description(keyword, intent):
    """Generate a meta description based on keyword and intent."""
    templates = DESCRIPTION_TEMPLATES.get(intent, DESCRIPTION_TEMPLATES["informational"])
    template = random.choice(templates)
    normalized = normalize_keyword(keyword, intent)
    return template.format(keyword=normalized)

def generate_content(keyword, intent):
    """Generate full article content based on intent."""
    year = datetime.datetime.now().year
    normalized = normalize_keyword(keyword, intent)
    
    if intent == "listicle":
        content = f"""## Best {normalized.title()} in {year}

Looking for the best **{normalized}**? You're in the right place. We've tested and ranked the top options available in {year}.

### Our Top Picks

| Rank | Tool | Best For | Starting Price |
| :--- | :--- | :--- | :--- |
| #1 | Coming Soon | - | - |
| #2 | Coming Soon | - | - |
| #3 | Coming Soon | - | - |

### How We Tested

Our methodology focuses on:
- **Real-world performance** - Not just benchmarks
- **Cost-effectiveness** - Value for money analysis
- **User experience** - Ease of use and learning curve

### The Bottom Line

The best {normalized} for you depends on your specific needs. Bookmark this page - we update our rankings monthly based on new data.

---
*Generated by PSEO Engine V3 - Intent-Aligned Content*
"""
    elif intent == "informational":
        content = f"""## What is {normalized.title()}?

**{normalized.title()}** is a topic that's gaining significant attention in {year}. Let's break it down in simple terms.

### Key Concepts

Understanding {normalized} requires grasping these fundamentals:
- **Core Definition**: What it means in technical terms
- **Why It Matters**: The real-world implications
- **Current State**: Where we are in {year}

### How It Works

The underlying mechanism of {normalized} involves several components working together...

### Why This Matters in {year}

The landscape is evolving rapidly. Here's what you need to know for {year}:
1. Industry adoption is accelerating
2. New standards are emerging
3. Cost structures are changing

### Frequently Asked Questions

**Q: What is the main benefit of {normalized}?**
A: The primary advantage is improved efficiency and capability in relevant workflows.

**Q: Is {normalized} worth investing in during {year}?**
A: It depends on your specific use case. Evaluate the cost-benefit ratio for your situation.

---
*Generated by PSEO Engine V3 - Intent-Aligned Content*
"""
    elif intent == "navigational":
        content = f"""## {normalized.title()} Review {year}

Is **{normalized.title()}** worth your time and money in {year}? We put it to the test.

### Quick Verdict

After extensive testing, here's our take on {normalized}:

| Aspect | Rating | Notes |
| :--- | :--- | :--- |
| Features | ⭐⭐⭐⭐ | Solid feature set |
| Pricing | ⭐⭐⭐ | Fair but could be better |
| Ease of Use | ⭐⭐⭐⭐ | Intuitive interface |

### What We Liked
- Strong core functionality
- Regular updates and improvements
- Good community support

### What Could Be Better
- Pricing transparency
- Advanced feature availability
- Learning curve for new users

### Should You Buy It?

**For beginners**: Recommended with reservations
**For professionals**: Evaluate based on specific needs

---
*Generated by PSEO Engine V3 - Intent-Aligned Content*
"""
    else:  # comparison
        content = f"""## {normalized.title()}: A Complete Comparison

Deciding between options in **{normalized}**? This guide breaks down the key differences.

### Head-to-Head Comparison

| Factor | Option A | Option B |
| :--- | :--- | :--- |
| Price | Varies | Varies |
| Features | Strong | Strong |
| Best For | Specific use cases | Different use cases |

### The Hidden Differences

What most reviews don't tell you about {normalized}:
1. **Real-world performance varies** - Lab tests don't tell the full story
2. **Hidden costs exist** - Watch for upgrade fees and add-ons
3. **Support quality matters** - Check community feedback

### Our Recommendation

The best choice for {normalized} depends on your priorities in {year}.

---
*Generated by PSEO Engine V3 - Intent-Aligned Content*
"""
    return content

def generate_faq_schema(keyword, intent):
    """Generate FAQ JSON-LD schema."""
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": f"What is the best {keyword} in 2026?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"The best {keyword} depends on your specific needs. Our 2026 guide covers the top options with detailed comparisons."
                }
            },
            {
                "@type": "Question",
                "name": f"Is {keyword} worth it in 2026?",
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": f"Based on our testing, {keyword} can provide significant value for the right use cases. See our detailed analysis above."
                }
            }
        ]
    }
    return json.dumps(faq, indent=2)

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    return text

def generate_from_keyword(keyword):
    """Generate a complete article from a single keyword."""
    intent = classify_intent(keyword)
    title = generate_title(keyword, intent)
    description = generate_description(keyword, intent)
    content = generate_content(keyword, intent)
    faq = generate_faq_schema(keyword, intent)
    
    date_str = datetime.datetime.now().strftime("%b %d %Y")
    slug = slugify(keyword) + "-2026"
    
    full_content = f\"\"\"---
title: \"{title}\"
description: \"{description}\"
pubDate: \"{date_str}\"
heroImage: \"{FALLBACK_IMAGE}\"
---

{content}
\"\"\"

    
    filepath = os.path.join(OUTPUT_DIR, f"{slug}.md")
    with open(filepath, 'w') as f:
        f.write(full_content)
    
    print(f"Generated [{intent.upper()}]: {slug}.md -> {title[:50]}...")
    return slug

def run_batch(keywords):
    """Process a batch of keywords."""
    count = 0
    for kw in keywords:
        generate_from_keyword(kw)
        count += 1
    print(f"\nIntent-Based Generation Complete. Created {count} articles.")

# GSC Zero-Click Keywords (from user's screenshot)
GSC_PRIORITY_KEYWORDS = [
    "ai chatbots with persistent memory across sessions 2026",
    "llama-4-coder model",
    "multi-agent orchestration research 2026",
    "best local offline ai assistant for accessing personal files projects documents 2026",
    "multi-agent orchestration ai 2026",
    "aeo checker",
    "keyboard era cpu blog engineer"
]

if __name__ == "__main__":
    run_batch(GSC_PRIORITY_KEYWORDS)
