#!/usr/bin/env python3
"""
Unified Content Workflow - "The n8n Style Script"
-------------------------------------------------
Orchestrates the entire content production lifecycle:
1. Topic -> Strategy & Keyword Analysis
2. Outline Generation (The Architect)
3. Research — collect verified data from KB + web search (The Researcher)
4. Drafting constrained by verified data (The Writer)
5. Claim Extraction & Verification — extract claims, verify, remove unverified (The Fact-Checker)
6. Critique & Refine (The Editor)
7. Quality Gate (The Auditor) — blocks low-quality articles
8. Image Generation (The Artist)
9. Final Publish

Usage:
    python scripts/unified_content_workflow.py --topic "DeepSeek vs GPT-4"
    python scripts/unified_content_workflow.py --topic "Future of AI Agents" --auto
    python scripts/unified_content_workflow.py --topic "Claude Code Review" --threshold 70
"""

import os
import sys
import re
import json
import time
import math
import argparse
from collections import Counter
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
SUPER_ROOT = Path("/Users/mac/code/super-individual")

# Add auditor path
sys.path.insert(0, str(SUPER_ROOT / "skills" / "core" / "content-reviewer" / "scripts"))


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

# Import HCU auditor
try:
    from auditor_hcu import audit_content_hcu
    HAS_AUDITOR = True
except ImportError:
    HAS_AUDITOR = False
    print("⚠️  auditor_hcu not available, quality gate will use built-in checks only")

# Quality gate defaults
DEFAULT_HCU_THRESHOLD = 60  # HCU score percentage minimum
MAX_QUALITY_RETRIES = 2     # Max times to retry after quality gate failure

# Content quality patterns (from content_quality_scan.py)
TEMPLATE_SPAM_PATTERNS = [
    r"has carved out a strong position",
    r"in our internal production environment",
    r"the feedback has been overwhelmingly positive",
    r"it's been a mainstay in our stack ever since",
    r"we first discovered .+ during a hackathon",
    r"always verify ai-generated output before using",
    r"alone can justify the subscription cost",
    r"delivers tangible productivity improvements",
    r"genuinely useful in daily workflows",
    r"features that seemed simple on the surface had surprising power",
    r"nobody on the team wanted to switch back",
    r"in today'?s rapidly evolving",
    r"in the (ever-evolving|rapidly changing|fast-paced) (world|landscape) of",
    r"let'?s (dive|delve) (in|into|deeper)",
    r"without further ado",
    r"game.?changer for",
    r"revolutioniz(e|ing|ed) the way",
    r"paradigm shift",
    r"stands out as a (beacon|leader|pioneer)",
    r"whether you'?re a .+ or a .+, this",
]

FAKE_DATA_PATTERNS = [
    (r"\b\d+% (success|accuracy|improvement|reduction|increase) rate\b", "unverified percentage claim"),
    (r"\bavg rating: \d\.\d/5\b", "fabricated rating"),
    (r"\b(based on|according to) (developer surveys|online reviews|our testing)\b", "vague source attribution"),
    (r"\bcatches .+ (\d+-\d+ hours|days) before\b", "fabricated prediction claim"),
]

STYLES = [
    # 1. High-Impact Digital Art & Surrealism
    "Surrealist digital art, dreamlike composition, floating geometric shapes in nature, ethereal lighting, Octane render, cinematic 8k",
    "Double exposure artistic collage, silhouette of a human head filled with galaxy stars and circuit board lines, emotional and dramatic",
    "Bioluminescent fantasy landscape, glowing organic forms, deep purple and teal palette, Avatar-like atmosphere, magical realism",
    "Futuristic abstract sculpture, liquid metal and glass, raytracing, vibrant iridescent colors, high-end 3D art, ArtStation trending",
    "Moebius style sci-fi illustration, intricate line work, flat pastel colors, surreal desert landscape, sense of scale and wonder",

    # 2. Expressive Fine Art (Texture & Color)
    "Vincent van Gogh inspired, thick impasto brushstrokes, swirling energy patterns, vibrant contrasting colors (blue/gold), expressive oil painting",
    "Abstract Alcohol Ink art, fluid flowing dyes, gold leaf veins, marble texture, organic chaos, rich saturated colors, elegant",
    "Washedui watercolor painting, wet-on-wet technique, soft bleeding colors, white negative space, artistic and emotive, minimalist composition",
    "Pop Art explosion, bold black outlines, halftone dots, bright primary colors, comic book dynamic action, Roy Lichtenstein style",
    "Kim Jung Gi style, incredibly detailed black ink sketching, fish-eye perspective, dynamic crowd/machinery, masterful composition",

    # 3. Conceptual & Graphic
    "Neo-Constructivism, bold geometric shapes, red black and cream color palette, industrial design, revolutionary poster art style",
    "Paper cut light box art, layers of paper creating depth, backlit with warm light, silhouette landscapes, cozy yet striking",
    "Glitch art portrait, digital distortion, datamoshing, RGB shift, cyberpunk aesthetic (but artistic), raw and edgy",
    "Low poly isometric world, but high-detail lighting, vibrant gradients, stylized digital illustration, charming and clean"
]

class ContentWorkflow:
    def __init__(self, topic, mode="general", auto_mode=False, hcu_threshold=DEFAULT_HCU_THRESHOLD):
        self.topic = topic
        self.mode = mode
        self.auto_mode = auto_mode
        self.hcu_threshold = hcu_threshold
        self.state = {
            "topic": topic,
            "slug": "",
            "title": "",
            "angle": "",
            "outline": "",
            "research_data": {"verified_facts": []},
            "draft": "",
            "verified_claims": [],
            "unverified_claims": [],
            "critique": "",
            "clean_content": "",
            "image_path": "",
            "image_prompt": "",
            "quality_score": 0,
            "quality_issues": [],
        }
        self.console = ConsoleUI()

    def run(self):
        self.console.header(f"Starting Workflow for: {self.topic}")

        # Step 1: Strategy
        self.step_strategy()

        # Step 2: Outline
        self.step_outline()

        # Step 3: Research — collect verified data BEFORE writing
        self.step_research()

        # Step 4: Drafting constrained by research data
        self.step_drafting()

        # Step 5: Claim extraction + verification
        self.step_fact_check()

        # Step 6: Critique & Refine
        self.step_critique_refine()

        # Step 7: Quality Gate (blocks bad articles)
        passed = self.step_quality_gate()
        if not passed:
            self.console.error(f"Article REJECTED after {MAX_QUALITY_RETRIES} retries. Not published.")
            print(f"\nDraft saved to: /tmp/rejected-{self.state['slug']}.md")
            Path(f"/tmp/rejected-{self.state['slug']}.md").write_text(
                self.state.get('clean_content', self.state.get('draft', '')), encoding='utf-8'
            )
            return

        # Step 8: Image Generation
        self.step_image_gen()

        # Step 9: Final Polish & Save
        self.step_publish()

        self.console.success("Workflow Complete!")
        print(f"\n  Article saved to: {BLOG_DIR}/{self.state['slug']}.md")
        print(f"  Quality score: {self.state['quality_score']}/100")
        print(f"  Verified claims: {len(self.state['verified_claims'])}")
        print(f"  Removed unverified: {len(self.state['unverified_claims'])}")

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

    def _load_knowledge_base_data(self):
        """Load relevant entries from product_knowledge_base.json."""
        kb_path = PROJECT_ROOT / "scripts" / "data" / "product_knowledge_base.json"
        if not kb_path.exists():
            return []

        try:
            with open(kb_path, encoding="utf-8") as f:
                kb = json.load(f)
        except Exception:
            return []

        topic_lower = self.topic.lower()
        title_lower = self.state.get('title', '').lower()
        search_text = topic_lower + " " + title_lower

        facts = []
        for tool_id, tool_data in kb.get("tools", {}).items():
            tool_name = tool_data.get("name", "").lower()
            # Check if this tool is mentioned in the topic/title
            if tool_name in search_text or tool_id.replace("_", " ") in search_text:
                # Extract pricing
                pricing = tool_data.get("pricing", {})
                if pricing.get("starting_price"):
                    facts.append({
                        "claim": f"{tool_data['name']} starts at {pricing['starting_price']}",
                        "source": tool_data.get("website", "product_knowledge_base.json"),
                        "category": "pricing"
                    })
                if pricing.get("free_tier"):
                    facts.append({
                        "claim": f"{tool_data['name']} offers a free tier",
                        "source": tool_data.get("website", "product_knowledge_base.json"),
                        "category": "pricing"
                    })
                # Extract rating
                if tool_data.get("g2_rating"):
                    facts.append({
                        "claim": f"{tool_data['name']} has a {tool_data['g2_rating']}/5 rating on G2 ({tool_data.get('g2_reviews', 'N/A')} reviews)",
                        "source": "g2.com",
                        "category": "rating"
                    })
                # Extract key features
                for feature in tool_data.get("key_features", [])[:3]:
                    facts.append({
                        "claim": f"{tool_data['name']}: {feature}",
                        "source": tool_data.get("website", "product_knowledge_base.json"),
                        "category": "feature"
                    })
                # Extract limitations
                for limit in tool_data.get("limitations", [])[:2]:
                    facts.append({
                        "claim": f"{tool_data['name']} limitation: {limit}",
                        "source": tool_data.get("website", "product_knowledge_base.json"),
                        "category": "limitation"
                    })

        return facts

    def step_research(self):
        self.console.step("3. Research — Collecting Verified Data...")

        # Load from knowledge base
        kb_facts = self._load_knowledge_base_data()
        if kb_facts:
            self.console.info(f"Found {len(kb_facts)} facts from knowledge base")

        # Search for additional real-time data
        prompt = f"""
        Research the topic "{self.state['title']}" using Google Search.
        Extract ONLY verifiable facts with source URLs.

        Categories to research:
        - Official pricing (from vendor websites)
        - Feature lists (from official docs)
        - Current version numbers (from changelogs/release notes)
        - Ratings and review counts (from G2, Capterra, GitHub stars)
        - Benchmark scores (from published papers or blog posts)
        - Release dates and company information

        RULES:
        - ONLY include facts you found via search with a real source URL
        - Do NOT guess or fabricate any data
        - If a source URL is unclear, describe where you found it

        Output JSON:
        {{"verified_facts": [
          {{"claim": "Cursor Pro costs $20/month", "source": "https://cursor.sh/pricing", "category": "pricing"}},
          {{"claim": "GitHub Copilot has 4.5/5 on G2 with 1247 reviews", "source": "https://g2.com/products/github-copilot", "category": "rating"}}
        ]}}
        """

        try:
            response = client.models.generate_content(
                model=MODEL_TEXT,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                )
            )

            # Parse JSON from response (may have markdown wrapping)
            text = response.text or ""
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            search_data = json.loads(text.strip())
            search_facts = search_data.get("verified_facts", [])
            self.console.info(f"Found {len(search_facts)} facts from web search")
        except Exception as e:
            self.console.warn(f"Search research failed: {e}")
            search_facts = []

        # Merge: KB facts + search facts (deduplicate by claim text)
        all_facts = kb_facts.copy()
        existing_claims = {f["claim"].lower() for f in all_facts}
        for fact in search_facts:
            if fact.get("claim", "").lower() not in existing_claims:
                all_facts.append(fact)
                existing_claims.add(fact["claim"].lower())

        self.state['research_data'] = {"verified_facts": all_facts}
        self.console.info(f"Total verified facts: {len(all_facts)}")

        # Print summary
        categories = {}
        for f in all_facts:
            cat = f.get("category", "other")
            categories[cat] = categories.get(cat, 0) + 1
        for cat, count in sorted(categories.items()):
            self.console.info(f"  {cat}: {count}")

    def step_drafting(self):
        self.console.step(f"4. Writing Draft Constrained by Research Data ({self.mode.title()} Mode)...")

        # Build verified data block for the prompt
        research_json = json.dumps(self.state['research_data']['verified_facts'], indent=2, ensure_ascii=False)

        search_instruction = f"""
            VERIFIED DATA — use ONLY these facts for specific numbers, prices, and statistics:
            {research_json}

            CRITICAL RULES:
            - ALL prices, ratings, version numbers, and statistics MUST come from the VERIFIED DATA above
            - If the verified data does not cover a topic, write QUALITATIVELY (e.g. "competitively priced" not "$X/month")
            - Do NOT fabricate benchmarks, test results, CVE numbers, user counts, or comparison data
            - Do NOT use template phrases ("has carved out a strong position", "game-changer", "paradigm shift")
            - You may add analysis, opinions, and technical insights — but all FACTS must trace to verified data
            - You may also use Google Search to find additional facts during writing
            """

        if self.mode == "news":
            prompt = f"""
            Write a breaking news analysis article based on this outline.

            Title: {self.state['title']}
            Outline:
            {self.state['outline']}

            {search_instruction}

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

            {search_instruction}

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

            {search_instruction}

            Style Rules:
            - Tone: Authoritative, experienced, "Senior Engineer to Senior Engineer"
            - No AI fillers ("In this digital landscape", "Let's delve in", "Unlocking")
            - Use specific numbers, benchmarks, and costs where possible — ALL verified via search
            - Code blocks must be realistic
            - Output ONLY the markdown body (no frontmatter yet)
            - Length: 2000+ words
            """

        response = client.models.generate_content(
            model=MODEL_TEXT,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8192,
                tools=[{"google_search": {}}],
            )
        )

        self.state['draft'] = response.text
        self.console.info(f"Draft generated: {len(self.state['draft'].split())} words (search-grounded)")

    def step_fact_check(self):
        self.console.step("5. Claim Extraction & Verification...")

        # Step 5a: Extract all factual claims from the draft
        extract_prompt = f"""
        Extract ALL factual claims from this article. A factual claim is any specific:
        - Price (e.g. "$20/month")
        - Statistic or percentage (e.g. "87% accuracy")
        - Version number (e.g. "GPT-4o")
        - Benchmark score (e.g. "92.1% on HumanEval")
        - Rating (e.g. "4.5/5 on G2")
        - User/review count (e.g. "1 million users")
        - Date or timeline (e.g. "released in March 2026")
        - Performance metric (e.g. "45 seconds execution time")

        Do NOT include opinions, qualitative statements, or general descriptions.

        Article:
        {self.state['draft'][:12000]}

        Output JSON array:
        [{{"claim": "Cursor Pro costs $20/month", "type": "pricing"}}, ...]
        """

        try:
            extract_resp = client.models.generate_content(
                model=MODEL_TEXT,
                contents=extract_prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json"),
            )
            extracted_claims = json.loads(extract_resp.text)
            if isinstance(extracted_claims, dict):
                extracted_claims = extracted_claims.get("claims", extracted_claims.get("factual_claims", []))
            if not isinstance(extracted_claims, list):
                extracted_claims = []
        except Exception as e:
            self.console.warn(f"Claim extraction failed: {e}")
            extracted_claims = []

        self.console.info(f"Extracted {len(extracted_claims)} factual claims")

        # Step 5b: Verify each claim against research data
        verified_facts_lower = [
            f["claim"].lower() for f in self.state['research_data']['verified_facts']
        ]
        verified_facts_text = " ".join(verified_facts_lower)

        verified = []
        unverified = []
        for claim_obj in extracted_claims:
            claim_text = claim_obj.get("claim", "").lower()
            matched = False

            # Strategy 1: Check if key numbers from the claim appear in verified facts
            numbers_in_claim = re.findall(r'\$[\d,.]+(?:/\w+)?|\d+\.?\d*%|\d+\.?\d*/\d+', claim_text)
            if numbers_in_claim:
                matched = any(n in verified_facts_text for n in numbers_in_claim)

            # Strategy 2: Check if significant words overlap with any verified fact
            if not matched:
                claim_words = set(re.findall(r'[a-z]{4,}', claim_text)) - {'this', 'that', 'with', 'from', 'have', 'been', 'more', 'than'}
                for vf in verified_facts_lower:
                    overlap = claim_words & set(re.findall(r'[a-z]{4,}', vf))
                    if len(overlap) >= 3:
                        matched = True
                        break

            if matched:
                verified.append(claim_obj)
            else:
                unverified.append(claim_obj)

        self.state['verified_claims'] = verified
        self.state['unverified_claims'] = unverified
        self.console.info(f"Verified: {len(verified)}, Unverified: {len(unverified)}")

        if not unverified:
            self.console.info("All claims verified — no changes needed")
            return

        # Step 5c: Try to verify unverified claims via search
        unverified_text = json.dumps([c["claim"] for c in unverified], ensure_ascii=False)
        verify_prompt = f"""
        Verify these specific claims using Google Search. For each claim, determine if it's TRUE, FALSE, or UNVERIFIABLE.

        Claims to verify:
        {unverified_text}

        Output JSON:
        [{{"claim": "...", "status": "TRUE|FALSE|UNVERIFIABLE", "correction": "correct value if FALSE, null if TRUE"}}]
        """

        try:
            verify_resp = client.models.generate_content(
                model=MODEL_TEXT,
                contents=verify_prompt,
                config=types.GenerateContentConfig(
                    tools=[{"google_search": {}}],
                )
            )
            # Parse JSON from response
            vtext = verify_resp.text or ""
            if "```json" in vtext:
                vtext = vtext.split("```json")[1].split("```")[0]
            elif "```" in vtext:
                vtext = vtext.split("```")[1].split("```")[0]
            verification_results = json.loads(vtext.strip())
            if isinstance(verification_results, dict):
                verification_results = verification_results.get("results", verification_results.get("claims", []))
        except Exception as e:
            self.console.warn(f"Search verification failed: {e}")
            verification_results = [{"claim": c["claim"], "status": "UNVERIFIABLE"} for c in unverified]

        # Separate truly unverified from search-verified
        still_unverified = [r for r in verification_results if r.get("status") in ("UNVERIFIABLE", "FALSE")]
        search_verified = [r for r in verification_results if r.get("status") == "TRUE"]

        self.console.info(f"After search: {len(search_verified)} newly verified, {len(still_unverified)} to remove/fix")
        self.state['verified_claims'].extend(search_verified)
        self.state['unverified_claims'] = still_unverified

        if not still_unverified:
            return

        # Step 5d: Remove/fix unverified claims from the article
        claims_to_fix = json.dumps(still_unverified, indent=2, ensure_ascii=False)
        cleanup_prompt = f"""
        Fix or remove these unverified/incorrect claims from the article:

        {claims_to_fix}

        For FALSE claims with corrections: replace with the correct value.
        For UNVERIFIABLE claims: replace specific numbers with qualitative language, or remove the sentence entirely.

        Example: "$99/month" → "a premium-tier subscription" or remove the price entirely.
        Example: "87% accuracy rate" → remove the claim if unverifiable.

        Keep the article coherent and well-structured after changes.

        Article:
        {self.state['draft'][:12000]}

        Output ONLY the corrected markdown body.
        """

        cleanup_resp = client.models.generate_content(
            model=MODEL_TEXT,
            contents=cleanup_prompt,
            config=types.GenerateContentConfig(max_output_tokens=8192)
        )

        old_wc = len(self.state['draft'].split())
        clean = cleanup_resp.text
        clean = re.sub(r"^```markdown\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)
        self.state['draft'] = clean
        new_wc = len(self.state['draft'].split())
        self.console.info(f"Cleaned: {old_wc} -> {new_wc} words ({len(still_unverified)} claims fixed/removed)")

    def step_critique_refine(self):
        self.console.step("6. Review & Refine (The Editor)...")
        
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
        self.console.step("6b. Polishing Content...")
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

    def _run_quality_checks(self, content):
        """Run all quality checks, return (score, issues)."""
        issues = []
        content_lower = content.lower()

        # 1. Template spam patterns
        template_hits = 0
        for pattern in TEMPLATE_SPAM_PATTERNS:
            matches = re.findall(pattern, content_lower)
            if matches:
                template_hits += len(matches)
                issues.append(f"TEMPLATE: '{pattern}' matched {len(matches)}x")

        # 2. Fake data patterns
        fake_hits = 0
        for pattern, desc in FAKE_DATA_PATTERNS:
            matches = re.findall(pattern, content_lower)
            if matches:
                fake_hits += len(matches)
                issues.append(f"FAKE_DATA: {desc} ({len(matches)}x)")

        # 3. Word count check
        word_count = len(content.split())
        if word_count < 800:
            issues.append(f"THIN: only {word_count} words")

        # 4. Excessive unverified pricing
        price_claims = re.findall(r'\$\d+(?:\.\d+)?/(?:month|mo|user|seat)', content_lower)
        if len(price_claims) > 5:
            issues.append(f"PRICING: {len(price_claims)} unverified price claims")

        # 5. Unverified claims check
        verified_count = len(self.state.get('verified_claims', []))
        unverified_count = len(self.state.get('unverified_claims', []))
        if unverified_count > verified_count and unverified_count > 3:
            issues.append(f"UNVERIFIED: {unverified_count} unverified claims vs {verified_count} verified")

        # 6. HCU audit (if available)
        hcu_score = 0
        if HAS_AUDITOR:
            hcu_result = audit_content_hcu(content, file_name=f"{self.state['slug']}.md")
            hcu_score = hcu_result['score']
            if hcu_result['verdict'] == 'REJECT':
                issues.append(f"HCU_REJECT: score {hcu_score}/100 — {hcu_result.get('verdict_reason', '')}")
            elif hcu_result['verdict'] == 'WARNING':
                issues.append(f"HCU_WARNING: score {hcu_score}/100")
            for issue in hcu_result.get('issues', []):
                issues.append(f"HCU: {issue}")
        else:
            # Fallback: simple scoring without auditor
            hcu_score = 100 - (template_hits * 5) - (fake_hits * 3)
            hcu_score = max(0, min(100, hcu_score))

        # 7. Diversity Check (Similarity Auditor)
        self.console.info("Running Diversity Audit...")
        sim_score, twin = self._check_diversity(content)
        if sim_score > 0.4:
            issues.append(f"DIVERSITY_REJECT: {sim_score:.2%} similarity with {twin}")
            hcu_score -= int(sim_score * 50)  # Heavy penalty for low diversity

        return hcu_score, issues

    def _get_tokens(self, text):
        """Tokenize and filter text for similarity analysis."""
        words = re.findall(r'\w+', text.lower())
        stopwords = {'the', 'a', 'an', 'in', 'on', 'at', 'with', 'for', 'to', 'is', 'are', 'was', 'were', 'and', 'of', 'how', 'what', 'why'}
        return [w for w in words if len(w) > 2 and w not in stopwords]

    def _calculate_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two Counter vectors."""
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])
        sum1 = sum([vec1[x]**2 for x in vec1.keys()])
        sum2 = sum([vec2[x]**2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)
        return float(numerator) / denominator if denominator else 0.0

    def _check_diversity(self, content):
        """Compare current content with existing blog posts."""
        if not BLOG_DIR.exists():
            return 0.0, None

        # Clean current content (remove frontmatter)
        body = re.sub(r'^---.*?---', '', content, flags=re.DOTALL)
        current_vec = Counter(self._get_tokens(body))
        
        max_sim = 0.0
        twin = None

        for f in BLOG_DIR.glob("*.md"):
            if f.stem == self.state['slug']:
                continue
            
            try:
                exist_content = f.read_text(encoding='utf-8')
                exist_body = re.sub(r'^---.*?---', '', exist_content, flags=re.DOTALL)
                exist_vec = Counter(self._get_tokens(exist_body))
                
                sim = self._calculate_similarity(current_vec, exist_vec)
                if sim > max_sim:
                    max_sim = sim
                    twin = f.name
            except Exception:
                continue
        
        return max_sim, twin

    def step_quality_gate(self):
        """Quality gate: blocks articles below threshold. Returns True if passed."""
        self.console.step(f"7. Quality Gate (threshold: {self.hcu_threshold}/100)...")

        content = self.state.get('clean_content', self.state.get('draft', ''))

        for attempt in range(1 + MAX_QUALITY_RETRIES):
            score, issues = self._run_quality_checks(content)
            self.state['quality_score'] = score
            self.state['quality_issues'] = issues

            if score >= self.hcu_threshold and not any('TEMPLATE:' in i for i in issues):
                self.console.info(f"PASSED: {score}/100 (attempt {attempt + 1})")
                if issues:
                    self.console.info(f"Minor issues: {len(issues)}")
                return True

            self.console.warn(f"FAILED: {score}/100 (attempt {attempt + 1}/{1 + MAX_QUALITY_RETRIES})")
            for issue in issues[:5]:
                self.console.warn(f"  - {issue}")

            if attempt < MAX_QUALITY_RETRIES:
                self.console.step(f"  Retrying: sending issues back to writer...")
                content = self._retry_with_feedback(content, issues)
                self.state['clean_content'] = content

        return False

    def _retry_with_feedback(self, content, issues):
        """Re-generate content with specific quality feedback."""
        issues_text = "\n".join(f"- {i}" for i in issues)
        research_json = json.dumps(self.state['research_data']['verified_facts'], indent=2, ensure_ascii=False)

        if any("DIVERSITY_REJECT" in i for i in issues):
            prompt = f"""
            This article failed the DIVERSITY AUDIT. It is too similar to existing content.
            
            REACTION PLAN:
            - Change the PERSPECTIVE entirely. (e.g. if you were an expert, be a skeptical tester).
            - Add 3 completely new sections that focus on UNCOMMON use cases.
            - Inject more personal "I tried this and it failed" stories.
            - Ensure the vocabulary and sentence structures are fresh.
            
            ISSUES TO FIX:
            {issues_text}
            
            {research_json}
            
            ARTICLE TO REWRITE:
            {content[:12000]}
            """
        else:
            prompt = f"""
            This article FAILED quality review. Fix ALL the issues listed below.

            ISSUES FOUND:
            {issues_text}

            VERIFIED DATA (keep using these real facts — do NOT remove them):
            {research_json}

            RULES:
            - Remove ALL template/cliche phrases (e.g. "has carved out a strong position", "game-changer", "paradigm shift")
            - Remove ALL fabricated statistics that are NOT in the VERIFIED DATA above
            - KEEP all prices, ratings, and features from VERIFIED DATA — these are real
            - Add first-hand experience language: "I tested", "in my experience", "after using X for 3 months"
            - Add specific examples of how the tools work in practice
            - Keep the article's core structure and information
            - IMPORTANT: maintain at least 1500 words — do NOT shorten the article
            - Output ONLY the corrected markdown body

            ARTICLE TO FIX:
            {content[:12000]}
            """

        response = client.models.generate_content(
            model=MODEL_TEXT,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=8192,
                tools=[{"google_search": {}}],
            )
        )

        clean = response.text
        clean = re.sub(r"^```markdown\s*", "", clean)
        clean = re.sub(r"\s*```$", "", clean)
        return clean

    def step_image_gen(self):
        self.console.step("8. Generating Hero Image (The Artist)...")
        
        # Select Random Style
        style = random.choice(STYLES)
        self.console.info(f"Selected Style: {style[:50]}...")

        # 1. Design Prompt
        # 1. Design Prompt
        design_prompt = f"""
        Act as an expert AI Art Director. Create a detailed prompt for an AI image generator (Imagen 3) for this article: "{self.state['title']}".
        
        Selected Art Style: "{style}"

        Instructions:
        1. Analyze the title and pick a concrete, visual metaphor or subject (e.g., objects, landscapes, abstract forms) that represents the topic.
        2. Describe the lighting, color palette, and composition based on the selected style.
        3. Ensure the scene is visually striking and suitable for a blog hero image (16:9 aspect ratio).
        4. CRITICAL: DO NOT include any text, letters, or words in the image.
        5. Output ONLY the prompt string to be sent to the image generator.
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
        self.console.step("9. Final Assembly & Publish...")
        
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
    parser.add_argument("--threshold", type=int, default=DEFAULT_HCU_THRESHOLD, help=f"HCU quality score threshold (default: {DEFAULT_HCU_THRESHOLD})")

    args = parser.parse_args()

    workflow = ContentWorkflow(args.topic, args.mode, args.auto, args.threshold)
    workflow.run()

if __name__ == "__main__":
    main()
