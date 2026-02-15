#!/usr/bin/env python3
"""
Topic Researcher - "The Editor-in-Chief"
----------------------------------------
Automates the discovery of high-potential content topics by:
1. Searching for recent trends and news in a specific niche.
2. Cross-referencing against existing blog posts to avoid duplicates.
3. Generating specific, actionable article ideas with associated workflows.

Usage:
    python scripts/topic_researcher.py --niche "AI Coding Assistants"
    python scripts/topic_researcher.py --count 10
"""

import os
import sys
import json
import argparse
import glob
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = PROJECT_ROOT / "src" / "content" / "blog"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Load Environment
# Try project root first, then super-individual root
env_paths = [
    PROJECT_ROOT / ".env",
    Path("/Users/mac/code/super-individual/.env")
]

for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

GEMINI_API_KEY = os.getenv("Gemini_api_key") or os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in .env")
    sys.exit(1)

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_TEXT = "gemini-2.0-flash"


class TopicResearcher:
    def __init__(self, niche="Artificial Intelligence, LLMs, Coding Tools", count=5):
        self.niche = niche
        self.count = count
        self.existing_slugs = self._get_existing_slugs()

    def _get_existing_slugs(self):
        """Get a set of all existing blog post slugs."""
        slugs = set()
        if not BLOG_DIR.exists():
            return slugs
            
        for file in BLOG_DIR.glob("*.md"):
            slugs.add(file.stem)
        return slugs

    def run(self):
        print(f"\n🔍 Researching topics for niche: '{self.niche}'...")
        print(f"   (Ignoring {len(self.existing_slugs)} existing articles)")

        # 1. Search for trends
        search_prompt = f"""
        Find the latest breaking news, trending releases, and hot debates in the world of {self.niche} from the last 7 days.
        Focus on:
        - New model releases (e.g. OpenAI, Anthropic, Google)
        - New developer tools or updates (e.g. Cursor, VS Code, Vercel)
        - Viral discussions on X/Twitter or Hacker News
        
        Return a summary of the top 10 trends.
        """
        
        try:
            response = client.models.generate_content(
                model=MODEL_TEXT,
                contents=search_prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                )
            )
            trends_summary = response.text
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return

        # 2. Generate Topics
        print("💡 Brainstorming content ideas...")
        
        existing_list = "\n".join(list(self.existing_slugs)[:50]) # Limit context window usage
        
        ideation_prompt = f"""
        Act as an Editor-in-Chief for a high-traffic tech blog.
        
        Based on these current trends:
        {trends_summary}

        And considering we ALREADY have these articles (DO NOT SUGGEST DUPLICATES):
        {existing_list}

        Generate {self.count} high-potential article ideas.
        
        For each idea, assign a "Mode" for our workflow script:
        - "news": For breaking news, release coverage.
        - "guide": For tutorials, how-to, or implementation guides.
        - "general": For deep dives, comparisons, or analysis.

        Output JSON format:
        [
            {{
                "title": "Article Title",
                "topic_query": "Short topic string for the CLI",
                "mode": "news|guide|general",
                "reasoning": "Why this is a hot topic now"
            }}
        ]
        """

        try:
            ideation_resp = client.models.generate_content(
                model=MODEL_TEXT,
                contents=ideation_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            # Extract JSON from potential markdown blocks
            text = ideation_resp.text
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            ideas = json.loads(text.strip())
            
            self._display_results(ideas)
            
        except Exception as e:
            print(f"❌ Ideation failed: {e}")

    def _display_results(self, ideas):
        print("\n" + "="*60)
        print(f" 🚀 TOP {len(ideas)} CONTENT OPPORTUNITIES")
        print("="*60 + "\n")

        for i, idea in enumerate(ideas, 1):
            print(f"{i}. {idea['title']}")
            print(f"   Reasoning: {idea['reasoning']}")
            print(f"   Command:")
            print(f"   👉 python scripts/02_unified_content_workflow.py --topic \"{idea['topic_query']}\" --mode {idea['mode']}")
            print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description="AI Topic Researcher")
    parser.add_argument("--niche", default="Artificial Intelligence, LLMs, Coding Tools, AI Agents", help="Niche to research")
    parser.add_argument("--count", type=int, default=5, help="Number of ideas to generate")
    
    args = parser.parse_args()
    
    researcher = TopicResearcher(args.niche, args.count)
    researcher.run()

if __name__ == "__main__":
    main()
