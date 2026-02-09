"""
Generate 5 high-quality pillar articles (3000+ words each)
using Gemini 2.0 Flash for deep, genuinely useful content.
"""
import json
import os
import re
import sys
import time
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

ARTICLES = [
    {
        "slug": "best-local-ai-assistants-offline-2026",
        "title": "7 Best Local AI Assistants That Work Completely Offline in 2026",
        "description": "We tested every major local AI assistant for speed, privacy, and real-world usefulness. Here are the 7 that actually work offline without compromising quality.",
        "category": "AI Tools",
        "tags": ["local-ai", "privacy", "offline", "llm"],
        "pubDate": "Jan 15 2026",
        "prompt": """Write a comprehensive, genuinely useful guide about the best local AI assistants that work offline in 2026. This should be 3000+ words.

CRITICAL QUALITY RULES:
- Write like a senior engineer who has actually tested all these tools, not a marketing blog
- Include SPECIFIC technical details: model sizes, RAM requirements, inference speeds, quantization formats
- Include real command-line examples for setup (ollama, llama.cpp, LM Studio)
- Compare HONESTLY - mention real limitations and dealbreakers
- Include a decision matrix table with actual specs
- NO fluffy intros like "In today's rapidly evolving..." - start with value immediately
- Include a "Quick Start" section with actual terminal commands
- Discuss GGUF vs GPTQ quantization trade-offs
- Mention specific models: Llama 3.3, Mistral, Phi-3, Qwen 2.5, DeepSeek
- Include RAM/VRAM requirements for each recommendation
- Add a "Who Should NOT Go Local" section (honesty builds trust)

STRUCTURE:
1. TL;DR comparison table (name, RAM needed, best for, setup difficulty)
2. Why go local in 2026? (3 concrete reasons with data)
3. Each tool deep-dive (500+ words each): Ollama, LM Studio, Jan, GPT4All, LocalAI, llama.cpp, Kobold.cpp
4. Head-to-head benchmark results
5. Step-by-step setup guide (Mac, Windows, Linux)
6. FAQ (5 genuine questions)
7. Final verdict"""
    },
    {
        "slug": "multi-agent-ai-orchestration-guide-2026",
        "title": "Multi-Agent AI Orchestration in 2026: From Concept to Production",
        "description": "A practical engineering guide to building multi-agent AI systems. Covers frameworks (CrewAI, LangGraph, AutoGen), architecture patterns, and production pitfalls.",
        "category": "AI Engineering",
        "tags": ["multi-agent", "orchestration", "langchain", "crewai"],
        "pubDate": "Jan 22 2026",
        "prompt": """Write a practical engineering guide about multi-agent AI orchestration in 2026. This should be 3000+ words.

CRITICAL QUALITY RULES:
- Write from the perspective of an engineer who has shipped multi-agent systems to production
- Include REAL code snippets (Python) for each framework
- Compare frameworks honestly: CrewAI vs LangGraph vs AutoGen vs custom
- Include architecture diagrams described in text/ASCII
- Discuss REAL production challenges: token costs, latency, error cascading, debugging
- Include cost calculations (e.g., "a 5-agent pipeline processing 1000 requests/day costs ~$X/month")
- NO theoretical fluff - every section should have actionable takeaways
- Include a "What I Wish I Knew Before Building Multi-Agent Systems" section

STRUCTURE:
1. What multi-agent orchestration actually means (skip the hype)
2. When you need it vs when a single prompt is enough (decision framework)
3. Framework comparison table (CrewAI, LangGraph, AutoGen, Semantic Kernel)
4. Architecture patterns: Sequential, Hierarchical, Debate, Swarm
5. Code walkthrough: Build a content pipeline with CrewAI (real code)
6. Production reality check: Costs, latency, failure modes
7. Monitoring and debugging multi-agent systems
8. FAQ (5 questions)
9. Resources and next steps"""
    },
    {
        "slug": "claude-code-vs-cursor-vs-windsurf-2026",
        "title": "Claude Code vs Cursor vs Windsurf: We Used All Three for 30 Days",
        "description": "After using Claude Code, Cursor, and Windsurf daily for a month, here is our honest comparison on code quality, speed, pricing, and which one we actually kept.",
        "category": "AI Coding",
        "tags": ["claude-code", "cursor", "windsurf", "ai-coding", "ide"],
        "pubDate": "Feb 03 2026",
        "prompt": """Write an honest, experience-based comparison of Claude Code, Cursor, and Windsurf in 2026. This should be 3000+ words.

CRITICAL QUALITY RULES:
- Write as if you used all three for 30 days on real projects
- Include SPECIFIC scenarios: "When refactoring a 500-line React component, Cursor took X approach while Claude Code did Y"
- Include pricing breakdown with REAL numbers and tiers
- Be brutally honest about each tool's weaknesses
- Include screenshots descriptions (mention what would be shown)
- Compare on: code quality, context window, multi-file editing, terminal integration, pricing, learning curve
- Include a "switching costs" section - what you lose migrating between tools
- Mention Claude Code's terminal-native approach vs Cursor's IDE approach
- Discuss Windsurf's (Codeium) unique agent features

STRUCTURE:
1. 30-second verdict (table with scores 1-10 on 6 dimensions)
2. Setup and first impressions
3. Daily workflow comparison (how each handles common tasks)
4. Code quality shootout (same 5 tasks, compare outputs)
5. Pricing deep-dive (what you actually pay, not just list price)
6. Context and memory handling
7. Where each tool fails (honest weaknesses)
8. Who should use what (developer profiles)
9. FAQ (5 questions)
10. Our final pick and why"""
    },
    {
        "slug": "build-private-ai-knowledge-base-2026",
        "title": "How to Build a Private AI Knowledge Base (No Cloud, No API Calls)",
        "description": "Step-by-step guide to building a fully private RAG system with local LLMs. Search your documents, code, and notes with AI - everything stays on your machine.",
        "category": "AI Engineering",
        "tags": ["rag", "local-ai", "knowledge-base", "privacy", "embeddings"],
        "pubDate": "Jan 28 2026",
        "prompt": """Write a complete hands-on tutorial for building a private AI knowledge base with RAG in 2026. This should be 3000+ words.

CRITICAL QUALITY RULES:
- This should be a REAL tutorial someone can follow start to finish
- Include ALL code needed (Python, complete working scripts)
- Use specific versions: Ollama + nomic-embed-text + Llama 3.3 + ChromaDB
- Include the exact pip install commands and versions
- Show real terminal output examples
- Discuss embedding model choices with benchmarks (nomic vs bge vs e5)
- Include chunking strategy comparison (fixed vs semantic vs recursive)
- Show how to handle PDFs, Markdown, code files, and emails
- Include performance numbers (ingestion speed, query latency)
- Add a "Common Mistakes" section based on real experience

STRUCTURE:
1. What we're building (architecture overview)
2. Prerequisites and installation (exact commands)
3. Step 1: Document ingestion pipeline (code)
4. Step 2: Embedding and vector store setup (code)
5. Step 3: Retrieval and re-ranking (code)
6. Step 4: LLM integration for answers (code)
7. Step 5: Building a CLI/web interface (code)
8. Advanced: Hybrid search, metadata filtering, incremental updates
9. Benchmarks: Query speed and accuracy on real documents
10. FAQ and troubleshooting"""
    },
    {
        "slug": "ai-memory-context-window-explained-2026",
        "title": "AI Memory and Context Windows Explained: What Every Developer Needs to Know in 2026",
        "description": "From 4K to 10M tokens: how AI context windows actually work, why bigger isn't always better, and practical strategies for managing memory in AI applications.",
        "category": "AI Engineering",
        "tags": ["context-window", "ai-memory", "llm", "rag", "engineering"],
        "pubDate": "Feb 01 2026",
        "prompt": """Write a comprehensive technical explainer about AI memory, context windows, and persistence in 2026. This should be 3000+ words.

CRITICAL QUALITY RULES:
- Write for developers who build AI applications, not casual readers
- Include actual token counts and costs per model (GPT-4o, Claude 3.5, Gemini 1.5, Llama 3.3)
- Explain KV-cache, attention mechanisms, and why context degrades at the edges
- Include the "Lost in the Middle" research findings with practical implications
- Compare strategies: RAG vs long context vs fine-tuning vs external memory
- Include cost calculations: "Stuffing 100K tokens into Claude costs $X per request"
- Show code examples for implementing memory patterns
- Discuss Claude's 200K, Gemini's 2M, and what "effective" context actually means
- Include real benchmark data on recall accuracy vs context position

STRUCTURE:
1. The context window landscape in 2026 (comparison table with costs)
2. How context windows actually work (KV-cache, attention, ROPE)
3. The "Lost in the Middle" problem (with data)
4. When to use long context vs RAG (decision framework)
5. Practical memory patterns for AI apps (code examples)
6. Cost optimization strategies (with real $ numbers)
7. Persistent memory: conversation history, user preferences, long-term learning
8. Building memory-efficient AI applications (architecture patterns)
9. What's coming next: infinite context, memory compression, neural databases
10. FAQ (5 questions)"""
    }
]


def generate_article(article_config):
    """Generate a single high-quality article using Gemini"""
    slug = article_config["slug"]
    output_path = BLOG_DIR / f"{slug}.md"

    if output_path.exists():
        print(f"  SKIP (exists): {slug}")
        return False

    prompt = f"""{article_config['prompt']}

OUTPUT FORMAT RULES:
- Output ONLY the article body in Markdown (no frontmatter, no title H1)
- Start directly with the first H2 section
- Use ## for main sections, ### for subsections
- Use proper markdown tables where specified
- Use ```python or ```bash for code blocks
- Use **bold** for key terms on first mention
- Write in a confident, direct tone - no hedging or filler
- Target 3000-3500 words
- End with a clear conclusion, not a cliffhanger
- Do NOT include phrases like "In conclusion" or "To sum up"
"""

    print(f"  Generating: {slug}...")
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=8192,
                temperature=0.7,
            )
        )
        body = response.text.strip()
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    # Build frontmatter
    tags_str = json.dumps(article_config["tags"])
    frontmatter = f"""---
title: "{article_config['title']}"
description: "{article_config['description']}"
pubDate: "{article_config['pubDate']}"
heroImage: "/assets/blog-fallback.jpg"
category: "{article_config['category']}"
tags: {tags_str}
---

# {article_config['title']}

"""

    full_content = frontmatter + body
    word_count = len(full_content.split())

    with open(output_path, "w") as f:
        f.write(full_content)

    print(f"  OK: {slug} ({word_count} words)")
    return True


def main():
    print("=== Generating 5 Pillar Articles ===\n")

    success = 0
    for i, article in enumerate(ARTICLES, 1):
        print(f"\n[{i}/5] {article['title']}")
        if generate_article(article):
            success += 1
            time.sleep(2)  # Rate limit

    print(f"\n=== Done: {success}/5 articles generated ===")


if __name__ == "__main__":
    main()
