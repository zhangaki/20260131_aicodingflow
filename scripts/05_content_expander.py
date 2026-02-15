#!/usr/bin/env python3
"""
content_expander.py

Unified tool for expanding and improving existing blog content.
Merges functionality from:
- expand_pseo_articles.py (Thin "VS" articles)
- expand_thin_originals.py (Thin original editorials)
- expand_top_articles.py (High-performing GSC articles)

Usage:
    python scripts/content_expander.py --mode pseo
    python scripts/content_expander.py --mode thin
    python scripts/content_expander.py --mode top
    python scripts/content_expander.py --slug my-article-slug
"""

import os
import re
import sys
import time
import argparse
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = PROJECT_ROOT / "src" / "content" / "blog"
load_dotenv(PROJECT_ROOT / ".env")

GEMINI_API_KEY = os.getenv("Gemini_api_key") or os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("ERROR: No Gemini API key found")
    sys.exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ---------------------------------------------------------------------------
# DATA & LISTS
# ---------------------------------------------------------------------------

# Articles to expand (original editorials)
THIN_ORIGINALS_SLUGS = [
    "generative-ai-pharma-2026", "legal-ai-bias-auditing-2026", "private-ai-hardware-2026",
    "local-llm-knowledge-base-2026", "ai-code-reviewer-bias-2026", "ai-model-fingerprinting-2026",
    "ai-verification-markers-2026", "clawdbot-evolution-2026", "dna-data-storage-for-ai-models",
    "hitl-agency-2026", "inside-moltbook-2026", "mobile-os-ai-2026", "on-device-quantization-2026",
    "prompt-injection-prevention-2026", "rag-latency-optimization-2026", "rare-disease-ai-diagnosis-2026",
    "red-teaming-llm-2026", "stochastic-ai-testing-2026", "token-cost-reduction-2026"
]

# Top performing articles with custom prompts
TOP_ARTICLES_CONFIG = [
    {
        "slug": "offline-ai-remote-work-2026",
        "prompt": "Rewrite and expanded this verified guide on local offline AI. Focus on privacy, Ollama setup, and specific RAM requirements. Write like a senior engineer."
    },
    {
        "slug": "multi-agent-orchestration-2026",
        "prompt": "Rewrite and expand deep dive into multi-agent orchestration. Compare CrewAI, LangGraph, AutoGen. usage patterns. Include real code examples."
    },
    {
        "slug": "ai-memory-context-persistence-2026",
        "prompt": "Rewrite and expand analysis of AI memory systems. Cover vector stores, summary memory, and specific implementation details with LangChain."
    },
    {
        "slug": "synthetic-data-ml-2026",
        "prompt": "Rewrite and expand guide on synthetic data (CTGAN, Gretel). Focus on privacy preservation and practical ML training use cases."
    },
    {
        "slug": "multimodal-ai-fusion-2026",
        "prompt": "Rewrite and expand technical overview of multimodal AI fusion (Text+Vision+Audio). Cover architecture, benchmarks, and real-world pipelines."
    }
]

# ---------------------------------------------------------------------------
# SHARED LOGIC
# ---------------------------------------------------------------------------

def extract_frontmatter(content):
    match = re.search(r'^(---\n.*?\n---)\n', content, re.DOTALL)
    if match:
        return match.group(1), content[match.end():]
    return None, None

def generate_expanded_content(prompt, old_body):
    full_prompt = f"""{prompt}
    
EXISTING CONTENT (Rewrite and significantly expand):
{old_body[:4000]}

OUTPUT FORMAT:
- Output ONLY the article body in Markdown.
- NO frontmatter. NO H1 title.
- Start with H2 headers.
- Use specific details, code blocks, and tables where relevant.
- Target 1500-2500 words.
"""
    try:
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"  API Error: {e}")
        return None

def update_file(filepath, new_body, frontmatter):
    # Ensure updatedDate is present
    if 'updatedDate:' not in frontmatter:
        frontmatter = frontmatter.replace('\n---', '\nupdatedDate: Feb 15 2026\n---')
    else:
        frontmatter = re.sub(r'updatedDate:.*', 'updatedDate: Feb 15 2026', frontmatter)
        
    # Extract title from frontmatter for H1
    title_match = re.search(r'title:\s*["\']?(.*?)["\']?\s*$', frontmatter, re.MULTILINE)
    title = title_match.group(1) if title_match else filepath.stem.replace('-', ' ').title()
    
    full_content = f"{frontmatter}\n\n# {title}\n\n{new_body}\n"
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    return True

# ---------------------------------------------------------------------------
# MODES
# ---------------------------------------------------------------------------

def run_pseo(max_threshold=800):
    print("=== Expanding Thin PSEO Articles ===")
    files = sorted(BLOG_DIR.glob("*-vs-*-2026.md"))
    count = 0
    for f in files:
        with open(f, 'r') as fh:
             content = fh.read()
             
        wc = len(content.split())
        if wc >= max_threshold:
            continue
            
        print(f"Expanding {f.name} ({wc} words)...")
        fm, body = extract_frontmatter(content)
        if not fm: continue
        
        prompt = "Rewrite and expand this comparison article. Add a comparison table, pricing details, and specific feature analysis. Be opinionated and technical."
        new_body = generate_expanded_content(prompt, body)
        
        if new_body and len(new_body.split()) > wc:
            update_file(f, new_body, fm)
            print(f"  -> Expanded to {len(new_body.split())} words")
            count += 1
            time.sleep(2)
    print(f"Expanded {count} PSEO articles.")

def run_thin():
    print("=== Expanding Thin Original Articles ===")
    count = 0
    for slug in THIN_ORIGINALS_SLUGS:
        f = BLOG_DIR / f"{slug}.md"
        if not f.exists(): continue
        
        with open(f, 'r') as fh:
             content = fh.read()
        
        wc = len(content.split())
        if wc > 1500: 
            print(f"Skipping {slug} (already {wc} words)")
            continue
            
        print(f"Expanding {slug} ({wc} words)...")
        fm, body = extract_frontmatter(content)
        if not fm: continue
        
        prompt = "Significantly expand this article. Add practical examples, real data, and actionable steps. Write for experts."
        new_body = generate_expanded_content(prompt, body)
        
        if new_body:
            update_file(f, new_body, fm)
            print(f"  -> Expanded to {len(new_body.split())} words")
            count += 1
            time.sleep(2)
    print(f"Expanded {count} original articles.")

def run_top():
    print("=== Expanding Top Performing Articles ===")
    count = 0
    for config in TOP_ARTICLES_CONFIG:
        slug = config['slug']
        f = BLOG_DIR / f"{slug}.md"
        if not f.exists(): continue
        
        print(f"Expanding {slug}...")
        with open(f, 'r') as fh:
             content = fh.read()
        
        fm, body = extract_frontmatter(content)
        if not fm: continue
        
        new_body = generate_expanded_content(config['prompt'], body)
        
        if new_body:
            update_file(f, new_body, fm)
            print(f"  -> Updated {slug}")
            count += 1
            time.sleep(2)
    print(f"Expanded {count} top articles.")

def run_single(slug):
    print(f"=== Expanding Single Article: {slug} ===")
    f = BLOG_DIR / f"{slug}.md"
    if not f.exists():
        print("File not found.")
        return
        
    with open(f, 'r') as fh:
            content = fh.read()
    
    fm, body = extract_frontmatter(content)
    if not fm:
        print("No frontmatter found.")
        return
        
    prompt = "Rewrite and significantly expand this article. Add depth, examples, and technical details."
    new_body = generate_expanded_content(prompt, body)
    
    if new_body:
        update_file(f, new_body, fm)
        print(f"Expanded {slug} to {len(new_body.split())} words.")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Content Expansion Tool")
    parser.add_argument("--mode", choices=["pseo", "thin", "top"], help="Expansion mode")
    parser.add_argument("--slug", help="Expand a specific article slug")
    args = parser.parse_args()
    
    if args.slug:
        run_single(args.slug)
    elif args.mode == "pseo":
        run_pseo()
    elif args.mode == "thin":
        run_thin()
    elif args.mode == "top":
        run_top()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
