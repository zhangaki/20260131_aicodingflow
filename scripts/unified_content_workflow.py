#!/usr/bin/env python3
"""
Unified Content Workflow - "The n8n Style Script"
-------------------------------------------------
Orchestrates the entire content production lifecycle:
1. Topic -> Strategy & Keyword Analysis
2. Outline Generation (The Architect)
3. Drafting (The Writer)
4. Critique (The Editor)
5. Refinement (The Polisher)
6. Image Generation (The Artist)
7. Formatting & SEO Audit (The QA)
8. Final Publish

Usage:
    python scripts/unified_content_workflow.py --topic "DeepSeek vs GPT-4"
    python scripts/unified_content_workflow.py --topic "Future of AI Agents" --auto
"""

import os
import sys
import re
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from google.genai import types
from PIL import Image

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BLOG_DIR = PROJECT_ROOT / "src" / "content" / "blog"
ASSETS_DIR = PROJECT_ROOT / "public" / "assets"


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
MODEL_IMAGE = "imagen-4.0-fast-generate-001"  
import random

STYLES = [
    # Tech / Future (Brand Aligned)
    "Futuristic, high-tech, abstract, 3D render, minimalist, dark mode aesthetic, neon accents (orange/blue)",
    "Swiss Design style, bold typography elements, grid layout, clean negative space, geometric abstraction, dark theme",
    "Technical blueprint schematics, white lines on deep blue background, detailed engineering diagram, glowing nodes",
    "Cyberpunk city architecture, neon lights, rain-slicked streets, high contrast, futuristic atmosphere",
    "Glassmorphism, translucent frosted glass shapes, soft lighting, vibrant gradient background, modern UI aesthetic",
    
    # Artistic / Abstract (For Variety)
    "Risograph print style, grainy texture, misaligned layers, limited color palette (neon pink and blue), dark background",
    "Abstract data visualization, flowing particles, network nodes, big data representation, ethereal lighting",
    "Synthwave retro-futuristic landscape, grid lines, sun on horizon, magenta and cyan color palette",
    "Isometric 3D illustration, digital assets, stylized floating elements, clean rendering, soft shadows",
    "Matisse-inspired paper cutouts, organic shapes, bold flat colors, but adapted for dark mode contrast"
]

class ContentWorkflow:
    def __init__(self, topic, mode="general", auto_mode=False):
        self.topic = topic
        self.mode = mode
        self.auto_mode = auto_mode
        self.state = {
            "topic": topic,
            "slug": "",
            "title": "",
            "angle": "",
            "outline": "",
            "draft": "",
            "critique": "",
            "clean_content": "",
            "image_path": "",
            "image_prompt": ""
        }
        self.console = ConsoleUI()

    def run(self):
        self.console.header(f"🚀 Starting Workflow for: {self.topic}")

        # Step 1: Strategy
        self.step_strategy()

        # Step 2: Outline
        self.step_outline()

        # Step 3: Drafting
        self.step_drafting()

        # Step 4: Critique & Refine
        self.step_critique_refine()

        # Step 5: Image Generation
        self.step_image_gen()

        # Step 6: Final Polish & Save
        self.step_publish()

        self.console.success("✨ Workflow Complete!")
        print(f"\n📄 Article saved to: {BLOG_DIR}/{self.state['slug']}.md")

    def step_strategy(self):
        self.console.step("1. Developing Strategy (Keywords, Slug, Angle)...")
        
        if self.mode == "news":
            prompt = f"""
            Analyze the breaking news topic: "{self.topic}"
            
            Return a JSON object with:
            - "slug": URL-safe slug (e.g., "deepseek-r1-release-news")
            - "title": Urgent, news-style H1 title
            - "angle": The "scoop" or main impact angle
            - "keywords": List of 5 trending keywords
            - "description": Meta description (punchy, 150 chars)
            """
        elif self.mode == "guide":
             prompt = f"""
            Analyze the tutorial topic: "{self.topic}"
            
            Return a JSON object with:
            - "slug": URL-safe slug (e.g., "how-to-deploy-deepseek-r1")
            - "title": SEO-optimized "How-To" Title
            - "angle": The specific problem being solved
            - "keywords": List of 5 long-tail keywords
            - "description": Meta description (benefit-focused)
            """
        else:
            prompt = f"""
            Analyze the topic: "{self.topic}"
            
            Return a JSON object with:
            - "slug": URL-safe slug (e.g., "deepseek-vs-gpt4-2026")
            - "title": SEO-optimized title (H1)
            - "angle": The unique angle or "hook" for a developer audience (e.g., "Focus on API costs and latency")
            - "keywords": List of 5 target keywords
            - "description": Meta description (150-160 chars)
            """
        
        response = client.models.generate_content(
            model=MODEL_TEXT,
            contents=prompt,
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        data = json.loads(response.text)
        self.state.update(data)
        
        self.console.info(f"Title: {self.state['title']}")
        self.console.info(f"Slug: {self.state['slug']}")
        self.console.info(f"Angle: {self.state['angle']}")

    def step_outline(self):
        self.console.step(f"2. Generating Outline ({self.mode.title()} Mode)...")
        
        if self.mode == "news":
            prompt = f"""
            Create a fast-paced "News Brief" outline for: "{self.state['title']}".
            Angle: {self.state['angle']}
            
            Structure:
            1. The What (3 bullet points on the core news)
            2. The So What (Why it matters to devs/business)
            3. The Now What (Immediate actions/predictions)
            """
        elif self.mode == "guide":
            prompt = f"""
            Create a detailed "Ultimate Guide" outline for: "{self.state['title']}".
            Angle: {self.state['angle']}
            Target Audience: Developers building in production.
            
            Structure:
            - Prerequisites & Environment Setup
            - Core Concepts (Brief)
            - Step-by-Step Implementation (The meat of the guide)
            - Advanced Configuration / Edge Cases
            - FAQ (5 common questions)
            """
        else:
            prompt = f"""
            Create a detailed outline for an article titled "{self.state['title']}".
            Angle: {self.state['angle']}
            Target Audience: Senior Developers & CTOs.
            
            Requirements:
            - Deep technical depth (no fluff)
            - Include "Comparison Table" section if relevant
            - Include "Code Examples" section if relevant
            - Structure with H2 and H3 headings
            - Add bullet points under each heading describing what to cover
            """
        
        response = client.models.generate_content(
            model=MODEL_TEXT,
            contents=prompt
        )
        
        self.state['outline'] = response.text
        
        if not self.auto_mode:
            print("\n--- Proposed Outline ---")
            print(self.state['outline'])
            print("------------------------")
            input("Press Enter to approve (or Ctrl+C to abort)...")

    def step_drafting(self):
        self.console.step(f"3. Writing First Draft ({self.mode.title()} Mode)...")
        
        if self.mode == "news":
            prompt = f"""
            Write a breaking news analysis article based on this outline.
            
            Title: {self.state['title']}
            Outline:
            {self.state['outline']}
            
            Style Rules:
            - Format: "News Brief" style - punchy, direct, urgent.
            - Structure: 
              1. The "What" (Analysis of the trend)
              2. The "So What" (Impact on businesses/devs)
              3. The "Now What" (Actionable steps)
            - Tone: Investigative journalist mixed with Senior Engineer.
            - Length: 800-1200 words (Keep it tight).
            - NO passive voice.
            - Output ONLY the markdown body.
            """
        elif self.mode == "guide":
            prompt = f"""
            Write a comprehensive, hands-on guide based on this outline.
            
            Title: {self.state['title']}
            Outline:
            {self.state['outline']}
            
            Style Rules:
            - Format: "Ultimate Guide" / Tutorial style.
            - Structure: 
              1. Prerequisites (Tools/Env setup)
              2. Step-by-Step Implementation (with code blocks)
              3. Common Pitfalls & Debugging
              4. FAQ Section (Auto-generate 5 relevant Q&A)
            - Tone: Instructive, clear, patient but technical.
            - Length: 2500+ words (Go deep).
            - Use specific commands, config examples, and best practices.
            - Output ONLY the markdown body.
            """
        else:
            prompt = f"""
            Write a comprehensive technical article based on this outline.
            
            Title: {self.state['title']}
            Outline:
            {self.state['outline']}
            
            Style Rules:
            - Tone: Authoritative, experienced, "Senior Engineer to Senior Engineer"
            - No AI fillers ("In this digital landscape", "Let's delve in", "Unlocking")
            - Use specific numbers, benchmarks, and costs where possible
            - Code blocks must be realistic
            - Output ONLY the markdown body (no frontmatter yet)
            - Length: 2000+ words
            """
        
        response = client.models.generate_content(
            model=MODEL_TEXT,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8192
            )
        )
        
        self.state['draft'] = response.text
        self.console.info(f"Draft generated: {len(self.state['draft'].split())} words")

    def step_critique_refine(self):
        self.console.step("4. Review & Refine (The Editor)...")
        
        # Critique
        critique_prompt = f"""
        Act as a strict Senior Editor. Review this draft for:
        1. AI Cliches (delve, landscape, game-changer)
        2. Fluff / Repetitive sentences
        3. Lack of specific data/examples
        
        Draft:
        {self.state['draft'][:10000]} (truncated)
        
        Provide a list of specific improvements.
        """
        
        critique_resp = client.models.generate_content(model=MODEL_TEXT, contents=critique_prompt)
        self.state['critique'] = critique_resp.text
        self.console.info("Editor Feedback Received.")
        
        # Refine
        self.console.step("5. Polishing Content...")
        refine_prompt = f"""
        Rewrite the draft to address the specific editorial feedback below.
        Keep the technical depth but make the prose sharper and more human.
        
        Original Draft:
        {self.state['draft']}
        
        Editor Feedback:
        {self.state['critique']}
        
        Output the FINAL polished markdown.
        """
        
        refine_resp = client.models.generate_content(
            model=MODEL_TEXT,
            contents=refine_prompt,
            config=types.GenerateContentConfig(max_output_tokens=8192)
        )
        
        # Clean up any residual markdown blocks
        clean_text = refine_resp.text
        clean_text = re.sub(r"^```markdown\s*", "", clean_text)
        clean_text = re.sub(r"\s*```$", "", clean_text)
        self.state['clean_content'] = clean_text

    def step_image_gen(self):
        self.console.step("6. Generating Hero Image (The Artist)...")
        
        # Select Random Style
        style = random.choice(STYLES)
        self.console.info(f"Selected Style: {style[:50]}...")

        # 1. Design Prompt
        design_prompt = f"""
        Create a prompt for an AI image generator (Imagen 3) for this article: "{self.state['title']}".
        Style: "{style}".
        No text in the image.
        Output ONLY the prompt string.
        """
        prompt_resp = client.models.generate_content(model=MODEL_TEXT, contents=design_prompt)
        image_prompt = prompt_resp.text.strip()

        self.state['image_prompt'] = image_prompt
        self.console.info(f"Prompt: {image_prompt}")
        
        # 2. Generate Image
        try:
            image_resp = client.models.generate_images(
                model=MODEL_IMAGE,
                prompt=image_prompt,
                config=genai.types.GenerateImagesConfig(number_of_images=1, aspect_ratio="16:9")
            )
            
            if image_resp.generated_images:
                # Save raw
                raw_filename = f"{self.state['slug']}.png"
                raw_path = ASSETS_DIR / raw_filename
                
                with open(raw_path, "wb") as f:
                    f.write(image_resp.generated_images[0].image.image_bytes)
                
                self.console.info(f"Image saved to {raw_path}")
                
                # Optimize to WebP
                self._optimize_image(raw_path)
                
                # Set final path for frontmatter
                self.state['image_path'] = f"/assets/{self.state['slug']}.webp"
                
            else:
                self.console.warn("No image generated. Using fallback.")
                self.state['image_path'] = "/assets/blog-fallback.jpg"
                
        except Exception as e:
            self.console.error(f"Image gen failed: {e}")
            self.state['image_path'] = "/assets/blog-fallback.jpg"

    def _optimize_image(self, img_path):
        try:
            with Image.open(img_path) as img:
                # Resize
                if img.width > 1200:
                    ratio = 1200 / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
                
                # Save as WebP
                webp_path = img_path.with_suffix(".webp")
                img.save(webp_path, "WEBP", quality=85)
                
                # Delete original
                if img_path != webp_path:
                    os.remove(img_path)
                    
            self.console.info("Image optimized to WebP")
            
        except Exception as e:
            self.console.error(f"Optimization failed: {e}")

    def step_publish(self):
        self.console.step("7. Final Assembly & Publish...")
        
        today = datetime.now().strftime("%b %d %Y")
        tags = [t.strip() for t in self.state.get("keywords", [])]
        tags_yaml = "\n".join([f"- {t}" for t in tags])
        
        frontmatter = f"""---
title: "{self.state['title']}"
description: "{self.state['description']}"
pubDate: "{today}"
heroImage: "{self.state['image_path']}"
tags:
{tags_yaml}
---

"""
        full_content = frontmatter + self.state['clean_content']
        
        # Post-process for common AI artifacts
        full_content = self._final_cleanup(full_content)
        
        outfile = BLOG_DIR / f"{self.state['slug']}.md"
        with open(outfile, "w") as f:
            f.write(full_content)

    def _final_cleanup(self, content):
        # Remove "Here is the article" variants
        patterns = [
            r"^Here represents a draft.*",
            r"^Sure, here is.*",
            r"^I have crafted.*"
        ]
        context_body = content.split("---")[-1]
        for p in patterns:
            context_body = re.sub(p, "", context_body, flags=re.MULTILINE|re.IGNORECASE)
        
        # Re-assemble
        parts = content.split("---")
        if len(parts) >= 3:
            parts[-1] = context_body
            return "---".join(parts)
        return content


class ConsoleUI:
    def header(self, msg):
        print("\n" + "="*60)
        print(f" {msg}")
        print("="*60 + "\n")

    def step(self, msg):
        print(f"\n👉 {msg}")

    def info(self, msg):
        print(f"   ℹ️  {msg}")

    def success(self, msg):
        print(f"\n✅ {msg}")

    def warn(self, msg):
        print(f"   ⚠️  {msg}")

    def error(self, msg):
        print(f"   ❌ {msg}")


def main():
    parser = argparse.ArgumentParser(description="Unified Content Workflow")
    parser.add_argument("--topic", required=True, help="Topic for the article")
    parser.add_argument("--mode", choices=["general", "news", "guide"], default="general", help="Content mode: 'general' (deep dive), 'news' (trend update), or 'guide' (comprehensive tutorial)")
    parser.add_argument("--auto", action="store_true", help="Run without manual approvals")
    
    args = parser.parse_args()
    
    workflow = ContentWorkflow(args.topic, args.mode, args.auto)
    workflow.run()

if __name__ == "__main__":
    main()
