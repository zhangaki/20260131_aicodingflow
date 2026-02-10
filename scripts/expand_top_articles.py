"""
Expand the top 5 GSC-performing articles from ~900 words to 2000+ words.
Uses Gemini 2.0 Flash to generate high-quality expanded content while
preserving existing frontmatter.
"""
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

# Top 5 articles by GSC impressions, with expansion prompts
ARTICLES_TO_EXPAND = [
    {
        "slug": "offline-ai-remote-work-2026",
        "prompt": """Rewrite and significantly expand this article about local offline AI assistants for personal files and documents in 2026. Target 2500+ words.

MUST COVER:
- Why go offline: privacy regulations (GDPR, CCPA), corporate data policies, internet reliability
- Top 7 local offline AI assistants: Ollama + Open WebUI, LM Studio, Jan.ai, GPT4All, LocalAI, Khoj, AnythingLLM
- For each tool: what it does, setup steps, file access capabilities, RAM requirements, pros/cons
- How to search personal files with local AI: document ingestion, embedding, RAG pipeline
- Comparison table: tool name, file search support, OS support, RAM needed, ease of setup
- Step-by-step: Setting up Ollama + AnythingLLM for searching your documents folder
- Performance benchmarks: query latency on 10GB of documents
- Security considerations: local model vs cloud API data exposure risks
- FAQ: 5 real questions about local offline AI assistants

TONE: Write like a senior developer who actually uses these tools daily. Be specific with versions, commands, and real numbers. No marketing fluff."""
    },
    {
        "slug": "multi-agent-orchestration-2026",
        "prompt": """Rewrite and significantly expand this article about multi-agent AI orchestration in 2026. Target 2500+ words.

MUST COVER:
- What multi-agent orchestration actually means (with a clear diagram in text/ASCII)
- When you need multi-agent vs single prompt (decision framework)
- Framework comparison: CrewAI, LangGraph, AutoGen, Semantic Kernel, custom solutions
- Architecture patterns: Sequential pipeline, Hierarchical delegation, Debate/consensus, Swarm
- Real Python code example: Build a research agent pipeline with CrewAI (complete working code)
- Production challenges: token costs ($X/1000 requests), latency budgets, error cascading, debugging
- Monitoring: How to trace multi-agent conversations (LangSmith, Phoenix, custom logging)
- Comparison table: framework, learning curve, production readiness, cost efficiency, community
- Research findings: latest papers on agent coordination (2025-2026)
- FAQ: 5 practical questions about building multi-agent systems

TONE: Write as an engineer who has shipped multi-agent systems to production. Include real costs, real latency numbers, real code. No theoretical fluff."""
    },
    {
        "slug": "ai-memory-context-persistence-2026",
        "prompt": """Rewrite and significantly expand this article about AI chatbots with persistent memory across sessions in 2026. Target 2500+ words.

MUST COVER:
- The persistence problem: why standard chatbots forget everything between sessions
- Context window sizes in 2026: Claude 200K, Gemini 2M, GPT-4o 128K, Llama 3.3 128K
- Memory architectures: conversation buffer, summary memory, entity memory, vector store memory
- How persistent memory actually works: embedding conversations, storing in vector DB, retrieval
- Comparison of chatbots with built-in memory: ChatGPT memory, Claude projects, Gemini context caching, Custom GPTs
- Building your own persistent memory system (Python code with LangChain + ChromaDB)
- The "Lost in the Middle" problem and how it affects memory retrieval
- Cost analysis: storing and retrieving memories at scale (tokens, API costs, storage)
- Privacy implications: who owns your conversation memories?
- Comparison table: chatbot, memory type, persistence duration, privacy level, cost
- FAQ: 5 questions about AI chatbot memory across sessions

TONE: Technical but accessible. Include actual code, real token counts, real dollar costs. Address both users who want to use existing tools and developers building memory systems."""
    },
    {
        "slug": "synthetic-data-ml-2026",
        "prompt": """Rewrite and significantly expand this article about synthetic data generation for AI/ML training in 2026. Target 2500+ words.

MUST COVER:
- Why synthetic data matters: real data scarcity, labeling costs ($0.10-$5 per label), privacy regulations
- Types of synthetic data: tabular (CTGAN, TVAE), image (diffusion models, GANs), text (LLM-generated), audio
- Top synthetic data tools in 2026: Gretel.ai, Mostly AI, Tonic.ai, NVIDIA Omniverse, Synthesis AI
- Quality metrics: FID score, utility metrics, privacy metrics (membership inference, attribute inference)
- When synthetic data beats real data: class imbalance, rare events, privacy-sensitive domains
- When synthetic data fails: distribution shift, mode collapse, validation gaps
- Python code example: Generate synthetic tabular data with CTGAN (complete working code)
- Case studies: healthcare (HIPAA-compliant training data), autonomous driving, financial fraud detection
- Cost comparison: synthetic data generation vs real data collection
- Comparison table: tool, data types, privacy guarantees, pricing, ease of use
- FAQ: 5 practical questions about synthetic data for ML

TONE: Write for ML engineers and data scientists. Include specific metrics, real benchmarks, actual code. Be honest about limitations."""
    },
    {
        "slug": "multimodal-ai-fusion-2026",
        "prompt": """Rewrite and significantly expand this article about multimodal AI fusion in 2026. Target 2500+ words.

MUST COVER:
- What multimodal AI fusion means: combining vision, language, audio, and structured data in one model
- The state of multimodal AI in 2026: GPT-4o, Gemini 2.0, Claude 3.5 Sonnet vision, Llama 3.2 Vision, Qwen-VL
- Architecture deep-dive: how vision transformers connect to language models (cross-attention, projection layers)
- Use cases with code examples: document understanding, video analysis, audio transcription + summarization
- Open-source multimodal models: LLaVA, CogVLM, InternVL, Fuyu
- Benchmarks: MMMU, MathVista, DocVQA scores across models
- Building a multimodal pipeline: image + text input, structured output (Python code)
- Comparison table: model, modalities supported, context length, latency, cost per 1K tokens
- Limitations: hallucination in visual grounding, spatial reasoning gaps, audio quality sensitivity
- Future directions: real-time multimodal streaming, embodied AI, video understanding
- FAQ: 5 questions about multimodal AI implementation

TONE: Technical but practical. Include real benchmark numbers, actual API costs, working code snippets. No hype, just facts."""
    }
]


def expand_article(config):
    """Expand a single article using Gemini"""
    slug = config["slug"]
    filepath = BLOG_DIR / f"{slug}.md"

    if not filepath.exists():
        print(f"  SKIP (not found): {slug}")
        return False

    with open(filepath) as f:
        content = f.read()

    # Extract frontmatter
    fm_match = re.match(r'^(---\n.*?\n---)\n', content, re.DOTALL)
    if not fm_match:
        print(f"  ERROR: No frontmatter found in {slug}")
        return False

    frontmatter = fm_match.group(1)
    old_body = content[fm_match.end():]
    old_word_count = len(old_body.split())

    print(f"  Current: {old_word_count} words")

    prompt = f"""{config['prompt']}

EXISTING CONTENT (for reference, rewrite and expand significantly):
{old_body[:3000]}

OUTPUT FORMAT RULES:
- Output ONLY the article body in Markdown (NO frontmatter, NO title H1)
- Start directly with the first H2 section
- Use ## for main sections, ### for subsections
- Use proper markdown tables where specified
- Use ```python or ```bash for code blocks
- Use **bold** for key terms on first mention
- Write in a confident, direct tone - no hedging or filler
- Target 2500-3000 words
- End with a clear conclusion, not a cliffhanger
- Do NOT include phrases like "In conclusion" or "To sum up" or "In today's rapidly evolving"
"""

    print(f"  Generating expanded content...")
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=8192,
                temperature=0.7,
            )
        )
        new_body = response.text.strip()
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

    # Extract title from frontmatter for H1
    title_match = re.search(r"title:\s*['\"]?(.*?)['\"]?\s*$", frontmatter, re.MULTILINE)
    title = title_match.group(1) if title_match else slug

    full_content = f"{frontmatter}\n\n# {title}\n\n{new_body}\n"
    new_word_count = len(full_content.split())

    if new_word_count < old_word_count:
        print(f"  WARN: New content ({new_word_count}) shorter than old ({old_word_count}), skipping")
        return False

    with open(filepath, "w") as f:
        f.write(full_content)

    print(f"  OK: {slug} ({old_word_count} -> {new_word_count} words)")
    return True


def main():
    print("=== Expanding Top 5 GSC-Performing Articles ===\n")

    success = 0
    for i, article in enumerate(ARTICLES_TO_EXPAND, 1):
        print(f"\n[{i}/5] {article['slug']}")
        if expand_article(article):
            success += 1
            time.sleep(2)  # Rate limit

    print(f"\n=== Done: {success}/5 articles expanded ===")


if __name__ == "__main__":
    main()
