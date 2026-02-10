"""
Generate targeted articles for GSC queries that have impressions
but no dedicated page. These are proven demand signals.
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

# Articles targeting GSC queries with proven impressions
TARGETED_ARTICLES = [
    {
        "slug": "anthropic-ai-tools-complete-guide-2026",
        "title": "Anthropic AI Tools: Complete Guide to Claude, API, and Enterprise Features (2026)",
        "description": "Everything you need to know about Anthropic's AI tools in 2026. Covers Claude models, Claude Code CLI, API pricing, tool use, enterprise features, and how to get started.",
        "category": "AI Tools",
        "tags": ["anthropic", "claude", "ai-tools", "api", "enterprise"],
        "pubDate": "Feb 05 2026",
        "prompt": """Write a comprehensive guide about Anthropic's AI tools ecosystem in 2026. Target 2500+ words.

This article targets users searching "anthropic ai tools" - they want to understand the full picture.

MUST COVER:
- Overview of Anthropic and their mission (safety-focused AI)
- Claude model lineup: Claude 3.5 Haiku, Claude 3.5 Sonnet, Claude 4.5, Claude Opus 4.6 (sizes, pricing, use cases)
- Claude.ai: the consumer product (free tier, Pro plan $20/month, features)
- Claude Code: the CLI tool for developers (what it does, how to install, key features)
- Anthropic API: pricing per model, rate limits, tool use feature, system prompts, streaming
- Enterprise features: Claude for Business, Amazon Bedrock integration, Google Cloud Vertex AI
- Claude's unique features: 200K context window, vision capabilities, artifacts, projects
- Code example: Simple API call with Python SDK
- Comparison table: Claude vs GPT-4o vs Gemini (pricing, context, features)
- Who should use Anthropic tools: developers, enterprises, content creators, researchers
- Getting started guide: step by step
- FAQ: 5 questions

TONE: Authoritative, practical, specific pricing and version numbers. No hype."""
    },
    {
        "slug": "home-assistant-local-ai-integration-2026",
        "title": "Home Assistant + Local AI: Complete Offline Smart Home Setup (2026)",
        "description": "Step-by-step guide to integrating local AI with Home Assistant for a fully offline smart home. No cloud, no subscriptions, complete privacy with Ollama and local LLMs.",
        "category": "AI Tools",
        "tags": ["home-assistant", "local-ai", "smart-home", "offline", "privacy"],
        "pubDate": "Feb 04 2026",
        "prompt": """Write a complete hands-on guide about integrating local AI with Home Assistant in 2026. Target 2500+ words.

This article targets users searching "home assistant local ai integration offline 2026" and "home ai server local offline no cloud".

MUST COVER:
- Why local AI for smart homes: privacy, no subscriptions, no internet dependency, faster response
- Prerequisites: Home Assistant OS/Docker, hardware requirements (Raspberry Pi 5 vs mini PC)
- Setting up Ollama on your home server (install, model selection, resource tuning)
- Home Assistant integrations for local AI: Extended OpenAI Conversation, Local AI, Wyoming
- Voice assistant setup: local wake word (openWakeWord), local STT (Whisper), local TTS (Piper)
- Automations with AI: natural language commands, context-aware responses
- Step-by-step tutorial: From bare metal to "Hey Jarvis, what's the weather?"
- Hardware recommendations and costs: budget ($100), mid-range ($300), enthusiast ($800)
- Comparison table: Cloud-based (Alexa/Google) vs Local AI smart home
- Performance benchmarks: response latency, accuracy, resource usage
- FAQ: 5 questions

TONE: Write for tech-savvy homeowners who value privacy. Include exact commands, config YAML, and real hardware specs."""
    },
    {
        "slug": "llama-4-coder-local-coding-assistant-2026",
        "title": "Llama 4 Coder: How to Run Meta's Coding LLM Locally in 2026",
        "description": "Complete guide to running Llama 4 Coder as a local coding assistant. Setup with Ollama, VS Code integration, benchmarks vs GPT-4o and Claude, and optimization tips.",
        "category": "AI Coding",
        "tags": ["llama", "local-ai", "coding", "meta", "open-source"],
        "pubDate": "Feb 03 2026",
        "prompt": """Write a practical guide about running Llama 4 Coder as a local coding assistant in 2026. Target 2500+ words.

This article targets users searching "llama-4-coder model" - they want to know what it is and how to use it.

MUST COVER:
- What is Llama 4 Coder: Meta's open-source coding-focused LLM, model sizes (8B, 70B, 405B)
- How it compares to Llama 3 and previous coding models (CodeLlama)
- Performance benchmarks: HumanEval, MBPP, SWE-Bench scores vs GPT-4o, Claude, DeepSeek Coder
- System requirements: RAM and VRAM for each model size, quantization options (Q4, Q5, Q8)
- Step-by-step setup with Ollama (exact commands)
- VS Code integration: Continue.dev extension setup with local Llama 4 Coder
- Neovim integration: with Avante or Codecompanion
- Fine-tuning for your codebase: LoRA setup basics
- Optimal model configurations: context window, temperature, system prompt for coding
- Comparison table: Llama 4 Coder vs DeepSeek Coder V2 vs CodeQwen vs StarCoder2
- When to use local Llama vs cloud APIs (decision framework)
- FAQ: 5 questions

TONE: Write for developers who want to ditch cloud APIs. Include real terminal commands, config files, and benchmark numbers."""
    },
]


def generate_article(config):
    """Generate a single targeted article"""
    slug = config["slug"]
    output_path = BLOG_DIR / f"{slug}.md"

    if output_path.exists():
        print(f"  SKIP (exists): {slug}")
        return False

    prompt = f"""{config['prompt']}

OUTPUT FORMAT RULES:
- Output ONLY the article body in Markdown (no frontmatter, no title H1)
- Start directly with the first H2 section
- Use ## for main sections, ### for subsections
- Use proper markdown tables where specified
- Use ```python or ```bash for code blocks
- Write in a confident, direct tone - no hedging or filler
- Target 2500-3000 words
- End with a clear conclusion
- Do NOT use phrases like "In conclusion" or "In today's rapidly evolving"
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

    tags_str = json.dumps(config["tags"])
    frontmatter = f"""---
title: "{config['title']}"
description: "{config['description']}"
pubDate: "{config['pubDate']}"
heroImage: "/assets/blog-fallback.jpg"
category: "{config['category']}"
tags: {tags_str}
---

# {config['title']}

"""

    full_content = frontmatter + body
    word_count = len(full_content.split())

    with open(output_path, "w") as f:
        f.write(full_content)

    print(f"  OK: {slug} ({word_count} words)")
    return True


def main():
    print("=== Generating GSC-Targeted Articles ===\n")

    success = 0
    for i, article in enumerate(TARGETED_ARTICLES, 1):
        print(f"\n[{i}/{len(TARGETED_ARTICLES)}] {article['title']}")
        if generate_article(article):
            success += 1
            time.sleep(2)

    print(f"\n=== Done: {success}/{len(TARGETED_ARTICLES)} articles generated ===")


if __name__ == "__main__":
    main()
